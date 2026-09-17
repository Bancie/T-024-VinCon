# Nhật ký tuần 01 · 15/09 – 21/09/2026

**Đợt báo cáo:** đợt 1 (giữa tuần, T5 17/09) — task BBox.

**Lead tuần này:** Nguyễn Chí Bằng (2A202602248)
**Dữ liệu / task CVAT:** W1-BBOX-G3-T1 — [task 142](https://cvat.note.transformerlabs.ai/tasks/142) · guideline G01 BBox / Polygon / Polyline

## Thành viên và phân công

| Thành viên | Vị trí | Phân công đợt 1 (task BBox) |
|---|---|---|
| Nguyễn Chí Bằng (2A202602248) | Lead | Điều phối task BBox; không gán job BBox |
| Võ Thị Bảo Chi (2A202602200) | Annotator · Reviewer | Gán job 1418; review job 1420 (Nam) |
| Đặng Văn Nam (2A202602295) | Annotator · Reviewer | Gán job 1420; review job 1418 (Chi) |
| Nguyễn Việt Tiến (2A202602315) | Annotator · Reviewer | Gán job 1424; review job 1422 (Thành) |
| Trương Đức Thành (2A202602179) | Annotator · Reviewer | Gán job 1422; review job 1424 (Tiến) |

Review chéo: Chi ↔ Nam, Tiến ↔ Thành.

Chi là lead task Semantic Segmentation (không gán job seg). Bằng gán 1 job seg. Cả hai ghi ở đợt 2, không thuộc đợt 1.

## Công việc

| # | Nội dung công việc | Annotator | Reviewer | Hoàn thành | Ghi chú |
|---|---|---|---|---|---|
| 1 | Job 1418 — 25 frame (0–24), G01 BBox / Polygon / Polyline | Võ Thị Bảo Chi (2A202602200) | Đặng Văn Nam (2A202602295) | ✅ 100% | Gán xong 21h 16/09; review xong ~22h30 16/09 |
| 2 | Job 1420 — 25 frame (25–49), cùng task | Đặng Văn Nam (2A202602295) | Võ Thị Bảo Chi (2A202602200) | 🟡 đang sửa | Gán xong 21h 16/09. Chi mở **106 issue**; review xong 9h 17/09. Nam đang sửa |
| 3 | Job 1422 — 25 frame (50–74), cùng task | Trương Đức Thành (2A202602179) | Nguyễn Việt Tiến (2A202602315) | ✅ 100% | Gán xong 21h 16/09; review xong ~22h30 16/09 |
| 4 | Job 1424 — 25 frame (75–99), cùng task | Nguyễn Việt Tiến (2A202602315) | Trương Đức Thành (2A202602179) | ✅ 100% | Gán xong 21h 16/09; review xong ~22h30 16/09 |

Mức hoàn thành: ✅ xong **và đã qua review** · 🟡 đang làm (ghi %) · ⛔ bị chặn (ghi lý do) · ⬜ chưa bắt đầu

## Tổng kết

- Đã gán: 100 / 100 frame (4 job × 25), xong 21h 16/09
- Qua review lần đầu: 3/4 job (1418, 1422, 1424) xong ~22h30 16/09; job 1420 Chi mở 106 issue, Nam đang sửa (review xong 9h 17/09)
- Edge case mới / đã chốt: [P-004](../problem-backlog.md#p-004) … [P-008](../problem-backlog.md#p-008) — 🔴 Mở (P-001–P-003 là template, không phải backlog đội)

## Vướng mắc

- [P-004](../problem-backlog.md#p-004): cùng guideline G01, annotator chọn khác loại shape (bbox / polygon / polyline) — chưa chốt QĐ.
- [P-005](../problem-backlog.md#p-005)–[P-008](../problem-backlog.md#p-008): ca khó tin nhắn đội (tối/xa, class xe, đường phía trong, crosswalk) — 🔴 Mở.
- Job 1420: 106 issue sau review; Nam đang sửa. Đây là lý do review chéo Chi–Nam kéo đến 9h 17/09.

### Ca khó (tin nhắn đội, kèm link CVAT)

**[P-005](../problem-backlog.md#p-005)** — frame tối / xe xa

- Nam job 1420: [frame 30](https://cvat.note.transformerlabs.ai/tasks/142/jobs/1420?frame=30); [frame 34](https://cvat.note.transformerlabs.ai/tasks/142/jobs/1420?frame=34) quá tối; [frame 49](https://cvat.note.transformerlabs.ai/tasks/142/jobs/1420?frame=49) nhiều xe, tối
- Thành job 1422: [frame 70](https://cvat.note.transformerlabs.ai/tasks/142/jobs/1422?frame=70) — xe xa vẫn gán `car`

**[P-006](../problem-backlog.md#p-006)** — class xe

- Chi job 1418: [frame 9](https://cvat.note.transformerlabs.ai/tasks/142/jobs/1418?frame=9) — xe chở 2 xe con, không chắc `truck`
- Chi job 1418 — van vs `car` vs `truck` (ảnh taxi vàng + xe van trắng; tin nhắn chưa ghi số frame)

**[P-007](../problem-backlog.md#p-007)** — đường phía trong

- Chi job 1418: [frame 24](https://cvat.note.transformerlabs.ai/tasks/142/jobs/1418?frame=24)

**[P-008](../problem-backlog.md#p-008)** — vẽ crosswalk

- Chi job 1418: [frame 0](https://cvat.note.transformerlabs.ai/tasks/142/jobs/1418?frame=0) / [frame 13](https://cvat.note.transformerlabs.ai/tasks/142/jobs/1418?frame=13)

## Kế hoạch đợt 2 tuần 1

- Fix issue BBox đợt 1 (job 1420 / 106 issue).
- Bắt đầu và hoàn thành task Semantic Segmentation (Chi lead, Chi không gán; Bằng gán 1 job seg).
