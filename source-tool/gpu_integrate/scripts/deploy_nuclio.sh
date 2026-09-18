#!/usr/bin/env bash
# Deploy SAM 3 Nuclio proxies into the local CVAT Nuclio project.
# Does not replace pth-facebookresearch-sam-vit-h.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ROOT}/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing ${ENV_FILE}. Copy .env.example to .env and fill Modal URLs + proxy token." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${SAM3_MODAL_VISUAL_URL:?Set SAM3_MODAL_VISUAL_URL in .env}"
: "${SAM3_MODAL_TEXT_URL:?Set SAM3_MODAL_TEXT_URL in .env}"
: "${MODAL_PROXY_KEY:?Set MODAL_PROXY_KEY in .env}"
: "${MODAL_PROXY_SECRET:?Set MODAL_PROXY_SECRET in .env}"

if ! command -v nuctl >/dev/null 2>&1; then
  echo "nuctl not found. Install the Nuclio CLI matching your CVAT Nuclio version (often 1.13.0)." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found." >&2
  exit 1
fi

detect_cvat_network() {
  local name cid
  name="$(docker network ls --format '{{.Name}}' | grep -E 'cvat' | head -n 1 || true)"
  if [[ -n "$name" ]]; then
    echo "$name"
    return 0
  fi
  cid="$(docker ps --format '{{.ID}} {{.Names}}' | awk 'BEGIN{IGNORECASE=1} /nuclio|cvat/ {print $1; exit}')"
  if [[ -n "$cid" ]]; then
    docker inspect -f '{{range $k, $_ := .NetworkSettings.Networks}}{{println $k}}{{end}}' "$cid" \
      | awk 'NF{print; exit}'
    return 0
  fi
  return 1
}

NETWORK="$(detect_cvat_network || true)"
if [[ -z "${NETWORK}" ]]; then
  echo "Could not find a Docker network for CVAT/Nuclio. Start CVAT with the serverless compose file, then retry." >&2
  echo "Hint: docker compose -f docker-compose.yml -f components/serverless/docker-compose.serverless.yml up -d" >&2
  exit 1
fi

echo "Using Docker network: ${NETWORK}"

nuctl create project cvat --platform local >/dev/null 2>&1 || true

deploy_fn() {
  local path="$1"
  echo "Deploying $(basename "$path") ..."
  nuctl deploy --project-name cvat --path "$path" \
    --file "${path}/function.yaml" --platform local \
    --env "SAM3_MODAL_VISUAL_URL=${SAM3_MODAL_VISUAL_URL}" \
    --env "SAM3_MODAL_TEXT_URL=${SAM3_MODAL_TEXT_URL}" \
    --env "MODAL_PROXY_KEY=${MODAL_PROXY_KEY}" \
    --env "MODAL_PROXY_SECRET=${MODAL_PROXY_SECRET}" \
    --env "SAM3_TIMEOUT_SEC=${SAM3_TIMEOUT_SEC:-170}" \
    --platform-config "{\"attributes\": {\"network\": \"${NETWORK}\"}}"
}

deploy_fn "${ROOT}/nuclio/sam3_interactor"
deploy_fn "${ROOT}/nuclio/sam3_detector"

echo
nuctl get function --platform local
echo
echo "Done. In CVAT: AI Tools → Interactors → SAM 3 (Modal)"
echo "              AI Tools → Detectors → SAM 3 Concept (Modal)"
echo "Existing Segment Anything (sam-vit-h) is unchanged."
