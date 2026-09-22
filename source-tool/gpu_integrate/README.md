# gpu_integrate — SAM 3 trên Modal GPU cho CVAT local

**Giải quyết:** SAM 3 nặng hơn máy local; CVAT Community không có native AI agent. Tool này chạy SAM 3 trên GPU Modal, CVAT local chỉ gọi Nuclio mỏng. Không đụng SAM vit-h đang có.

## Pain point

Local Docker (Mac, ~11 GB) không chạy thoải mái SAM 3. CVAT Community chỉ gắn model qua Nuclio, không qua `cvat-cli function create-native`.

## Tool làm gì

- Modal GPU (L4): SAM 3 ảnh — click/box (Sam3Tracker) và text/concept (Sam3Model)
- Nuclio CPU: `pth-modal-sam3-interactor` và `pth-modal-sam3-detector` → HTTP sang Modal
- SAM 1 `pth-facebookresearch-sam-vit-h` giữ nguyên

Không làm video.

## Cài đặt và chạy

### 0. Điều kiện

- Modal account + `modal token new`
- Hugging Face: [facebook/sam3](https://huggingface.co/facebook/sam3) **ACCEPTED**, rồi token Read
- CVAT + Nuclio đang chạy (serverless compose)
- `nuctl` khớp version Nuclio (CVAT thường 1.13.0)
- Docker RAM nên ≥ 16 GB (GPU vẫn bên Modal)

### 1. Secret Hugging Face trên Modal

```bash
modal secret create huggingface HF_TOKEN=hf_...
```

Nếu secret đã tồn tại, sửa trên [Modal Secrets](https://modal.com/secrets) hoặc tạo lại.

### 2. Deploy SAM 3 lên Modal

Từ root repo:

```bash
modal deploy source-tool/gpu_integrate/modal/sam3_app.py
```

CLI in URL. Copy vào `.env` (từ `.env.example`):

- `...-sam3-visual.modal.run`
- `...-sam3-text.modal.run`
- `...-sam3-health.modal.run` (tuỳ chọn)

Tạo proxy token: Dashboard → Settings → Proxy Auth Tokens, hoặc `modal workspace proxy-tokens`. Điền `MODAL_PROXY_KEY` / `MODAL_PROXY_SECRET`.

Lần đầu container tải checkpoint (~3.4 GB) vào volume `sam3-hf-cache` — startup có thể vài phút.

### 3. Test API

```bash
python3 -m pip install -r source-tool/gpu_integrate/scripts/requirements.txt
python3 source-tool/gpu_integrate/scripts/test_modal.py
```

Phải in `visual rle length` và `text objects` > 0 (ảnh mẫu là xe).

### 4. Gắn vào CVAT (Nuclio)

```bash
chmod +x source-tool/gpu_integrate/scripts/deploy_nuclio.sh
source-tool/gpu_integrate/scripts/deploy_nuclio.sh
```

Script tự tìm docker network `cvat*`. Nếu lỗi, bật CVAT serverless rồi chạy lại:

```bash
docker compose -f docker-compose.yml -f components/serverless/docker-compose.serverless.yml up -d
```

Trên Mac Apple Silicon, nếu build vẫn fail `msgpack`:

```bash
DOCKER_DEFAULT_PLATFORM=linux/amd64 source-tool/gpu_integrate/scripts/deploy_nuclio.sh
```

### 5. Dùng trong editor

- **AI Tools → Interactors → SAM 3 (Modal)** — click dương/âm hoặc box
- **AI Tools → Detectors → SAM 3 Concept (Modal)** — text = **tên label** của task (không có ô gõ text trên Community)

Sửa [`nuclio/sam3_detector/labels.yaml`](nuclio/sam3_detector/labels.yaml) và `spec` trong [`nuclio/sam3_detector/function.yaml`](nuclio/sam3_detector/function.yaml) cho khớp class task, rồi deploy lại detector.

Đổi mask → bbox: `type: rectangle` trong yaml.

## Đầu vào / đầu ra

- Vào (interactor): ảnh + `pos_points` / `neg_points` / `obj_bbox` (protocol CVAT như IOG)
- Vào (detector): ảnh; prompt = label (`nguoi` → `person` nếu có map)
- Ra interactor: mask RLE CVAT (IOG-style)
- Ra detector: `mask` bitmap crop + bbox (và `points` polygon nếu convert mask→poly)

## Giữ ấm GPU / chi phí

Mặc định `min_containers=0`, `scaledown_window=300` (5 phút idle rồi tắt). Click đầu sau khi tắt = cold start.

Session gán dài: sửa `min_containers=1` trong [`modal/sam3_app.py`](modal/sam3_app.py) rồi `modal deploy` lại (tốn GPU idle).

## Giới hạn

- Chỉ ảnh, không video
- HTTP Modal tối đa ~150s/request (có redirect); Nuclio timeout 180s
- Detector không có text box trên UI Community
- Label detector phải trùng (hoặc map) với label task
- Chưa Accepted HF thì Modal không tải được `facebook/sam3`
- Nếu `nuctl` không thấy function: đúng version nuctl, CVAT/Nuclio đang chạy, docker network đúng

## Người viết

Đội T-024 — local CVAT + Modal GPU
