# Problem backlog

Những chỗ gặp trong lúc gán nhãn mà **guideline chưa trả lời được**, cộng các pain point về công cụ.

Ghi ngay khi gặp, kể cả lúc chưa biết xử lý thế nào. Một edge case không được ghi lại thì
mỗi người sẽ tự xử lý theo một kiểu — và đó là nguồn lớn nhất của nhãn không nhất quán.

> P-001–P-003 là **ví dụ** (tên và link CVAT giả). Từ P-004 trở đi là mục thật của đội. Mẫu trống để copy nằm cuối file.

## Danh sách

| Mã | Tóm tắt | Loại | Mục guideline | Trạng thái | Kết quả |
|---|---|---|---|---|---|
| [P-001](#p-001) | Người ngồi sau xe máy: box riêng hay gộp với người lái | Guideline mơ hồ | §3.2 | ✅ Đã chốt | [QĐ-001](so-quyet-dinh.md#qđ-001) |
| [P-002](#p-002) | Xe bị che khuất hơn một nửa | Guideline chưa nói tới | §3.4 | ↗️ Hỏi BTC | — |
| [P-003](#p-003) | Phải vẽ lại box y hệt qua nhiều frame liên tiếp | Pain point công cụ | — | 🗣️ Đang bàn | — |
| [P-004](#p-004) | Cùng guideline G01, 3 annotator chọn khác loại shape (bbox / polygon / polyline) | Guideline mơ hồ | G01 — phạm vi BBox / Polygon / Polyline | 🔴 Mở | — |
| [P-005](#p-005) | Frame tối / xe xa, thiếu bằng chứng class | Guideline mơ hồ | G01 §3 — không đoán; object nhỏ/mờ → review | 🔴 Mở | — |
| [P-006](#p-006) | Class xe: car-carrier vs `truck`; van vs `car` vs `truck` | Guideline mơ hồ | G01 §2 — taxonomy object instance | 🔴 Mở | — |
| [P-007](#p-007) | Đường phía trong (sau lan can) gán class/shape gì | Guideline mơ hồ | G01 §4.1 — `area/drivable` vs `area/alternative` | 🔴 Mở | — |
| [P-008](#p-008) | Quy ước vẽ `lane/crosswalk` (polyline) | Guideline mơ hồ | G01 §4.2 — polyline lane marking | 🔴 Mở | — |

**Loại**

| Loại | Nghĩa là |
|---|---|
| Guideline chưa nói tới | Tình huống không có trong guideline |
| Guideline mơ hồ | Đọc guideline ra được hai cách hiểu trở lên |
| Guideline mâu thuẫn | Hai mục trong guideline nói ngược nhau |
| Pain point công cụ | Guideline rõ, nhưng làm trên CVAT chậm hoặc dễ sai |

**Trạng thái:** 🔴 Mở · 🗣️ Đang bàn · ↗️ Hỏi BTC · ✅ Đã chốt (trỏ sang QĐ) · 🛠️ Làm tool (trỏ sang `source-tool/`) · ⚪ Bỏ (ghi lý do)

---

## P-001

**Người ngồi sau xe máy: box riêng hay gộp chung với người lái**

- **Loại:** Guideline mơ hồ
- **Mục guideline:** §3.2 — "mỗi người một bounding box"
- **Người phát hiện:** @thanh-vien-b · 16/09/2026
- **Link CVAT:**
  - https://cvat.example.com/tasks/12/jobs/101?frame=37 — hai người, gần như chồng khít
  - https://cvat.example.com/tasks/12/jobs/101?frame=112 — người ngồi sau chỉ lộ đầu
- **Mô tả:** §3.2 nói mỗi người một box, nhưng hình minh hoạ trong guideline lại vẽ một box
  cho cả xe máy lẫn người trên xe.
- **Các cách hiểu:**
  1. Theo câu chữ: người ngồi sau có box `nguoi` riêng.
  2. Theo hình minh hoạ: không vẽ box `nguoi` cho ai đang ngồi trên xe.
- **Xử lý tạm trong lúc chờ:** vẽ box riêng và gắn tag `can_xem_lai` để dễ lọc ra sửa.
- **Kết quả:** ✅ [QĐ-001](so-quyet-dinh.md#qđ-001)

## P-002

**Xe bị che khuất hơn một nửa**

- **Loại:** Guideline chưa nói tới
- **Mục guideline:** §3.4 — chỉ nói về vật thể bị cắt ở mép ảnh, không nói về bị che
- **Người phát hiện:** @thanh-vien-c · 17/09/2026
- **Link CVAT:**
  - https://cvat.example.com/tasks/12/jobs/103?frame=8 — ô tô sau xe buýt, lộ khoảng 30%
  - https://cvat.example.com/tasks/12/jobs/103?frame=64 — xe máy sau cột điện, lộ khoảng 50%
- **Mô tả:** Không rõ có gán nhãn vật thể bị che không, và nếu có thì box ôm phần nhìn thấy
  hay ôm cả phần ước lượng bị che.
- **Các cách hiểu:**
  1. Bỏ qua khi lộ dưới 50%.
  2. Luôn gán, box chỉ ôm phần nhìn thấy.
  3. Luôn gán, box ôm cả phần ước lượng.
- **Xử lý tạm trong lúc chờ:** dừng job 103, chuyển sang job khác ít ca che khuất.
- **Kết quả:** ↗️ Đã hỏi BTC ngày 18/09/2026, chờ trả lời.

## P-003

**Phải vẽ lại box y hệt qua nhiều frame liên tiếp**

- **Loại:** Pain point công cụ
- **Mục guideline:** —
- **Người phát hiện:** @thanh-vien-d · 18/09/2026
- **Link CVAT:** https://cvat.example.com/tasks/12/jobs/105?frame=200 — frame 200–260, xe đỗ không di chuyển
- **Mô tả:** Ảnh chụp liên tiếp từ camera cố định. Xe đỗ bên đường xuất hiện y nguyên ở hàng chục
  frame, annotator phải vẽ lại ở từng frame. Ước tính chiếm ~40% thời gian job 105.
- **Hướng đang cân nhắc:**
  1. Dùng chế độ *Track* sẵn có của CVAT — cần thử xem có hợp với dữ liệu dạng ảnh rời không.
  2. Viết script đọc file export của CVAT, nhân box sang các frame kế tiếp, rồi import lại.
- **Kết quả:** 🗣️ Đang bàn. Nếu chọn hướng 2 thì đổi trạng thái sang 🛠️ và làm trong
  [`source-tool/`](source-tool/).

## P-004

**Cùng đọc G01 nhưng 3 annotator vẽ khác loại shape**

- **Loại:** Guideline mơ hồ
- **Mục guideline:** G01 *Bounding Box, Polygon & Polyline* (bài thực hành, 4 trang).
  Trang 1, phạm vi: bounding box cho object instance; polygon cho drivable area;
  polyline cho lane marking. Nguyên tắc: không đoán; không tự tạo class; case không
  rõ phải đưa review. G01 là rule set thực hành cho bài tập; nếu batch/customer có
  guideline khác thì guideline đó được ưu tiên.
- **Người phát hiện:** Nguyễn Chí Bằng (2A202602248) · 16/09/2026
- **Link CVAT:**
  - https://cvat.note.transformerlabs.ai/tasks/142/jobs/1424 — Tiến. Bổ sung `?frame=`
    khi chốt được frame lệch loại shape.
  - https://cvat.note.transformerlabs.ai/tasks/142/jobs/1420?frame=25 — Nam. Building
    vẽ rectangle/bbox; `sky` vẽ polygon; mặt đường vẽ polygon (`ROAD 7 (MANUAL)`);
    khoảng 27 items trên frame.
  - Job của Chi — cần bổ sung URL job và `?frame=` (không đoán link).
- **Mô tả:** Ba annotator (Tiến, Nam, Chi) đều đọc G01 trước khi gán task 142
  (ảnh giao thông: object instance + drivable area + lane marking) nhưng chọn **khác
  tool/shape** cho cùng loại vật thể. G01 chỉ 4 trang nên nút thắt không phải “không
  tìm được đoạn”, mà là câu “bbox / polygon / polyline dùng khi nào” đọc ra nhiều
  cách. Cùng đọc, vẫn ra ba kiểu vẽ. Reviewer chưa có quyết định trong
  [`so-quyet-dinh.md`](so-quyet-dinh.md) để lấy làm chuẩn, nên mỗi người (kể cả lúc
  review) tiếp tục theo cách hiểu riêng. Hệ quả: nhãn lệch giữa các job; review, so
  ground truth, và pipeline huấn luyện/evaluation không dùng được một taxonomy shape
  thống nhất.
- **Các cách hiểu:**
  1. *Đúng câu chữ phạm vi G01* — object instance (xe, người, building, …) = bbox;
     drivable area = polygon; lane marking = polyline. Một class một loại shape. Không
     đổi tool vì object méo, vì ôm sát hơn, hay vì vẽ bbox nhanh hơn. Mở job tương ứng
     (Tiến 1424 / Nam 1420 / Chi khi có link) để đối chiếu ai đang làm theo cách này.
  2. *Ưu tiên ôm sát ranh giới* — object không phải hình chữ nhật (building méo, mặt
     đường cong, vạch lane) thì dùng polygon hoặc polyline dù G01 xếp chúng là instance
     hoặc lane marking. Ôm sát hơn nhưng phá taxonomy shape. Không gán sẵn cách này cho
     Tiến hay Chi khi chưa mở job đối chiếu.
  3. *Ưu tiên tốc độ / thói quen CVAT* — bbox cho gần như mọi thứ, hoặc lẫn
     rectangle / polygon / polyline trong cùng một class tùy frame. Nam, frame 25, là
     một mix cụ thể: bbox cho building, polygon cho road và sky. Job Tiến và Chi có thể
     mix khác; mở job là thấy, không suy từ frame của Nam.
- **Xử lý tạm trong lúc chờ:** không lấy một annotator làm chuẩn. Frame lệch loại
  shape gắn tag `can_xem_lai` để lọc ra sửa sau. Job đang làm: không chắc shape thì
  dừng, ghi tiếp vào backlog hoặc đưa review — đúng nguyên tắc G01, không đoán.
- **Hướng đang cân nhắc:** (tool — chỉ sau khi đã chốt cách vẽ)
  1. Cheat sheet 1 trang: mỗi class → đúng một shape, kèm 1 ảnh đúng / 1 ảnh sai và
     link quyết định.
  2. Họp đội, chọn một trong ba cách hiểu trên, ghi QĐ, ghim kênh, rà lại job 1420,
     job 1424, và job của Chi khi có link.
  3. Chatbot RAG chỉ sau khi đã có QĐ. Index G01 **và** [`so-quyet-dinh.md`](so-quyet-dinh.md).
     Câu trả lời phải kèm mục guideline hoặc mã QĐ; không có thì bảo ghi P. Không RAG
     chỉ trên G01 rồi để model tự phán shape — cùng đoạn mơ hồ sẽ ra thêm cách hiểu
     thứ tư.
- **Kết quả:** 🔴 Mở

## P-005

**Frame tối / xe xa, thiếu bằng chứng class**

- **Loại:** Guideline mơ hồ
- **Mục guideline:** G01 §3 — không đoán class; object quá nhỏ/mờ thì đưa review, không tự suy. Quick reference: class không chắc → Issue (`UNCERTAIN_CLASS`), có review.
- **Người phát hiện:** Đặng Văn Nam (2A202602295), Trương Đức Thành (2A202602179) · 17/09/2026
- **Link CVAT:**
  - https://cvat.note.transformerlabs.ai/tasks/142/jobs/1420?frame=30 — Nam. Frame được gắn cờ, không mô tả thêm trong tin.
  - https://cvat.note.transformerlabs.ai/tasks/142/jobs/1420?frame=34 — Nam. Quá tối.
  - https://cvat.note.transformerlabs.ai/tasks/142/jobs/1420?frame=49 — Nam. Nhiều xe, tối, khó xác định.
  - https://cvat.note.transformerlabs.ai/tasks/142/jobs/1422?frame=70 — Thành. File `w1/bbox_polygon/G03/G03_B070.jpg`. Xe ở xa, không đủ bằng chứng nhưng vẫn gán `car`.
- **Mô tả:** Cùng rule G01 “không đoán”, hai annotator làm khác nhau. Nam dừng ở chỗ tối/khó đọc (frame 34, 49). Thành ghi rõ không có định nghĩa chuẩn về khoảng cách và độ rõ, rồi vẫn gán các xe xa là `car`. Reviewer chưa có QĐ nên mỗi job tự chọn escalate hoặc gán cho xong. Hệ quả: recall/precision lệch giữa job tối và job xa.
- **Các cách hiểu:**
  1. *Đúng câu chữ G01* — không đủ bằng chứng thị giác thì không gán class; tạo Issue / đưa review (`UNCERTAIN_CLASS`). Nam đang nghiêng cách này.
  2. *Vẫn gán class gần đúng* — xe xa/tối vẫn box `car` (hoặc class đoán) để không miss object. Thành đã làm vậy trên frame 70.
  3. *Bỏ object* — không box, không Issue. Nhanh nhưng mất object rõ một phần và không để reviewer bắt được.
- **Xử lý tạm trong lúc chờ:** không lấy cách của Thành hay Nam làm chuẩn. Frame tối/xa gắn tag `can_xem_lai`. Không chắc class thì Issue, không đoán thêm class mới.
- **Kết quả:** 🔴 Mở

## P-006

**Class xe: car-carrier vs `truck`; van vs `car` vs `truck`**

- **Loại:** Guideline mơ hồ
- **Mục guideline:** G01 §2 — object instance BBox: `car`, `truck`, `bus`, … Không tự tạo class, không gộp class theo cảm tính. Class không chắc → Issue, không đoán.
- **Người phát hiện:** Võ Thị Bảo Chi (2A202602200) · 17/09/2026
- **Link CVAT:**
  - https://cvat.note.transformerlabs.ai/tasks/142/jobs/1418?frame=9 — Chi. Xe chở 2 xe con trên thùng; không chắc gán `truck` có đúng.
  - Job 1418 — van vs `car` vs `truck` (ảnh taxi vàng + xe van trắng trong tin 10:46). **Không ghi `?frame=`** — tin nhắn không có số frame.
- **Mô tả:** Taxonomy G01 có `car` / `truck` / `bus`, không có `van` hay `car-carrier`. Chi hỏi hai ca: (1) xe tải chở 2 ô tô con trên thùng — có phải `truck`; (2) van đứng cạnh taxi — lúc nào `car`, lúc nào `truck`. Cùng đọc bảng class vẫn ra hơn một cách gán.
- **Các cách hiểu:**
  1. *Theo hình dáng khung* — thùng chở xe / van hộp = `truck`; sedan/taxi = `car`. Frame 9 sẽ là `truck`.
  2. *Theo chức năng / kích thước gần `car`* — van khách và taxi cùng `car`; chỉ xe tải thùng lớn mới `truck`. Frame 9 có thể vẫn `truck`, van thì `car`.
  3. *Không đủ class trong G01* — không đoán `van`/`car-carrier`; tạo Issue `UNCERTAIN_CLASS`, chờ QĐ. Không tự thêm class.
- **Xử lý tạm trong lúc chờ:** không chốt `truck` cho frame 9 và không gán `van` thành class mới. Tag `can_xem_lai`. Bổ sung `?frame=` cho ca van khi mở đúng ảnh.
- **Kết quả:** 🔴 Mở

## P-007

**Đường phía trong (sau lan can) gán class/shape gì**

- **Loại:** Guideline mơ hồ
- **Mục guideline:** G01 §4.1 — drivable area dùng Polygon: `area/drivable`, `area/alternative`. Bám sát biên nhìn thấy; phân biệt hai class theo định nghĩa mentor/batch đã chốt; không tự đổi nhãn khi chưa chắc.
- **Người phát hiện:** Võ Thị Bảo Chi (2A202602200) · 17/09/2026
- **Link CVAT:**
  - https://cvat.note.transformerlabs.ai/tasks/142/jobs/1418?frame=24 — Chi. Đường phía trong (sau lan can, tách khỏi làn ego); hỏi “label sẽ là gì”.
- **Mô tả:** Frame 24 có làn ego (đã vẽ) và một dải đường phía trong, ngăn bởi lan can. G01 bắt polygon cho drivable area nhưng không nói nhánh đường song song / sau rào là `area/drivable`, `area/alternative`, hay không thuộc scope. Chi chưa có QĐ nên không biết gán class/shape.
- **Các cách hiểu:**
  1. *Cùng mặt đường xe chạy được* — polygon `area/drivable` nếu còn thấy mặt đường.
  2. *Làn phụ / không phải ego* — `area/alternative` (G01 để batch/mentor chốt cặp này).
  3. *Ngoài scope* — không polygon; đường sau lan can không gán drivable. Chỉ Issue nếu không chắc.
- **Xử lý tạm trong lúc chờ:** không tự chọn 1 trong 3. Frame 24 tag `can_xem_lai`. Không đổi polyline/bbox thay polygon cho drivable.
- **Kết quả:** 🔴 Mở

## P-008

**Quy ước vẽ `lane/crosswalk` (polyline)**

- **Loại:** Guideline mơ hồ
- **Mục guideline:** G01 §4.2 — lane marking dùng Polyline (`lane/crosswalk`, …). Đi theo tim/biên vạch, không nối tắt vùng không có vạch; không dùng Polygon thay lane chỉ vì vạch có bề rộng.
- **Người phát hiện:** Võ Thị Bảo Chi (2A202602200) · 17/09/2026
- **Link CVAT:**
  - https://cvat.note.transformerlabs.ai/tasks/142/jobs/1418?frame=0 — Chi. Hỏi quy ước vẽ crosswalk.
  - https://cvat.note.transformerlabs.ai/tasks/142/jobs/1418?frame=13 — Chi. Cùng câu (cách vẽ crosswalk).
- **Mô tả:** G01 xếp crosswalk vào polyline lane marking nhưng không vẽ mẫu: một polyline cắt ngang đường, một polyline mỗi vạch, hay bao quanh vùng vạch. Chi hỏi trên hai frame. Thiếu QĐ thì mỗi người vẽ một kiểu, evaluate lane không so được.
- **Các cách hiểu:**
  1. *Một polyline theo hướng người đi* — cắt ngang làn, bám mép/tim vùng vạch nhìn thấy; dừng khi hết evidence.
  2. *Mỗi vạch zebra một polyline* — đúng từng sọc, chậm hơn, không gộp thành một vùng.
  3. *Polygon ôm cả vùng crosswalk* — ôm sát bề rộng vạch nhưng trái §4.2 (lane không dùng polygon thay polyline).
- **Xử lý tạm trong lúc chờ:** không lấy polygon làm chuẩn. Frame 0 và 13 tag `can_xem_lai`. Không chắc hướng vẽ thì Issue, không bịa quy ước đội.
- **Kết quả:** 🔴 Mở

---

## Mẫu để copy

```markdown
## P-NNN

**Tóm tắt một dòng**

- **Loại:** Guideline chưa nói tới | Guideline mơ hồ | Guideline mâu thuẫn | Pain point công cụ
- **Mục guideline:** §
- **Người phát hiện:** @ · dd/mm/yyyy
- **Link CVAT:** (bỏ trống nếu không có)
  - https://…/tasks/<id>/jobs/<id>?frame=<n> — frame này có gì
- **Mô tả:**
- **Các cách hiểu:** (với pain point công cụ thì ghi **Hướng đang cân nhắc:**)
  1.
  2.
- **Xử lý tạm trong lúc chờ:**
- **Kết quả:** 🔴 Mở
```

Nhớ thêm một dòng vào bảng **Danh sách** ở đầu file.
