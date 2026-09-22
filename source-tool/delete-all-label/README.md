# delete-all-label

**Giải quyết:** [P-009](../../problem-backlog.md#p-009) — xoá hết shape/tag trên một frame CVAT local (không đụng track)

## Pain point

Trước khi có tool: SAM / auto-annotation hoặc gán nhầm đổ nhiều box lên một frame; phải click xoá từng object trên UI. Track nhiều frame thì không được đụng. Lặp lại mỗi lần chạy lại detector trên đúng frame đó.

## Tool làm gì

CLI gọi REST CVAT local: lấy annotation của job, lọc shape và tag đúng frame, rồi `PATCH .../annotations?action=delete`. Track giữ nguyên. Có `--dry-run` và hỏi xác nhận trừ khi `--yes`.

## Cài đặt và chạy

Từ folder tool:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # điền CVAT_USERNAME / CVAT_PASSWORD
```

CVAT local đang chạy (mặc định `http://localhost:8080`).

```bash
python3 delete_all_label.py --job 1420 --frame 25 --dry-run
python3 delete_all_label.py --job 1420 --frame 25
python3 delete_all_label.py --url 'http://localhost:8080/tasks/142/jobs/1420?frame=25'
python3 delete_all_label.py --job 1420 --frame 25 --yes
```

`--frame` = số trên URL `?frame=`. Nếu số đó không nằm trong `start_frame..stop_frame` của job, tool hiểu là index 0 = ảnh đầu job.

## Đầu vào / đầu ra

- Vào: job ID + frame (hoặc URL job), tài khoản CVAT local trong `.env`
- Ra: xoá shape/tag trên server; stdout in số lượng và id. Không ghi file export/import

## Đã thử trên

Chưa đo trên job thật. Chạy `--dry-run` trước trên job local rồi mới `--yes`.

## Giới hạn

- Không xoá, không cắt track (object kéo dài nhiều frame) dù track hiện trên frame đó
- Không xoá cả job (`DELETE /annotations/` bị cấm trong tool)
- Chỉ CVAT local qua REST; không thay UI live — reload job sau khi chạy

## Người viết

đội
