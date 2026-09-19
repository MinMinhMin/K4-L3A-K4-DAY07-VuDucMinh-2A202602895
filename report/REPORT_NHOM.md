# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** TwoMenSquad
**Thành viên:** Vũ Đức Minh, Nguyễn Ngọc Vĩnh, Nguyễn Công Vinh
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Học bổng và chính sách hỗ trợ sinh viên tại Trường Đại học Công nghệ (UET)

**Tại sao nhóm chọn chủ đề này?**
Nhóm chọn chủ đề này vì các thông báo học bổng chứa nhiều thông tin có cấu trúc rõ ràng như đối tượng, điều kiện, giá trị, chỉ tiêu, hồ sơ và thời hạn. Đây là bộ dữ liệu phù hợp để so sánh chunking vì câu trả lời thường nằm trong từng mục/section riêng biệt và có nhiều con số cần truy xuất chính xác. Các tài liệu đều là nguồn công khai từ website UET và được chuẩn hóa về metadata để phục vụ tìm kiếm, lọc và truy vết nguồn.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Học bổng Data Nest 2026–2027 | https://uet.edu.vn/hoc-bong-data-nest-nam-hoc-2026-2027/ | 2026-09-19 / not-stated | 2.708 | `student`, `student-affairs`, `scholarship`, `vi` |
| 2 | Điều chỉnh đối tượng học bổng Data Nest 2026–2027 | https://uet.edu.vn/dieu-chinh-doi-tuong-xet-hoc-bong-data-nest-nam-hoc-2026-2027/ | 2026-09-19 / not-stated | 1.645 | `student`, `student-affairs`, `scholarship-adjustment`, `vi` |
| 3 | Học bổng EVN 2025–2026 | https://uet.edu.vn/hoc-bong-evn-nam-hoc-2025-2026/ | 2026-09-19 / not-stated | 2.123 | `student`, `student-affairs`, `scholarship`, `vi` |
| 4 | Học bổng kỳ cuối cho sinh viên tốt nghiệp 06/2026 | https://uet.edu.vn/cap-hoc-bong-khuyen-khich-hoc-tap-ki-cuoi-cho-sinh-vien-tot-nghiep-dot-xet-thang-06-nam-2026/ | 2026-09-19 / not-stated | 1.773 | `student`, `student-affairs`, `scholarship-award`, `vi` |
| 5 | Chương trình học bổng Goertek 2027 | https://uet.edu.vn/chuong-trinh-hoc-bong-goertek-nam-2027/ | 2026-09-19 / not-stated | 1.828 | `student`, `student-affairs`, `scholarship`, `vi` |
| 6 | Học bổng The Best of MB Chasing 2026 | https://uet.edu.vn/hoc-bong-the-best-of-mb-chasing-2026/ | 2026-09-19 / not-stated | 1.055 | `student`, `student-affairs`, `scholarship`, `vi` |
| 7 | Quy định xét, cấp học bổng khuyến khích học tập UET | https://uet.edu.vn/quy-dinh-ve-viec-xet-cap-hoc-bong-khuyen-khich-hoc-tap-tai-truong-dai-hoc-cong-nghe/ | 2026-09-19 / not-stated | 1.981 | `all`, `student-affairs`, `scholarship-policy`, `vi` |
| 8 | Đề nghị xét học bổng Vallet 2026 | https://uet.edu.vn/de-nghi-xet-hb-vallet-nam-2026/ | 2026-09-19 / not-stated | 953 | `student`, `student-affairs`, `scholarship-recommendation`, `vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.
- [x] Có 8 tài liệu cùng chủ đề và `sources.csv` khớp một-một với các file `.md`.
- [x] `audience` có hai giá trị `student` và `all`, đủ để kiểm thử metadata filter.
- [x] Nội dung đã được làm sạch, chỉ giữ thông tin học bổng cần cho benchmark.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `uet-data-nest-2026-2027` | Định danh ổn định để nối chunk với tài liệu gốc và hỗ trợ `delete_document`. |
| `title` | string | `Học bổng Data Nest 2026–2027` | Giúp nhận diện tài liệu và truy vết nguồn trong kết quả. |
| `source_url` | string | URL website UET | Cho phép kiểm tra nguồn của câu trả lời. |
| `retrieved_at` | date | `2026-09-19` | Ghi nhận thời điểm thu thập dữ liệu. |
| `document_version` | string | `not-stated` | Phân biệt phiên bản/ngày hiệu lực; không tự suy đoán khi nguồn không nêu. |
| `audience` | enum | `student`, `all` | Cho phép lọc tài liệu theo đối tượng, đặc biệt với query dành cho sinh viên. |
| `department` | string | `student-affairs` | Lọc theo đơn vị phụ trách nội dung. |
| `category` | string | `scholarship-policy` | Phân biệt thông báo học bổng, quy định và điều chỉnh đối tượng. |
| `language` | string | `vi` | Hỗ trợ lọc theo ngôn ngữ của corpus. |
| `source_published_at` | date | `2026-08-26` | Hỗ trợ đánh giá độ mới của thông báo. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Quy ước chạy chung

Để kết quả công bằng, cả ba thành viên phải giữ nguyên các yếu tố sau:

- Corpus: `data/hoc-bong-uet/`.
- `chunk_size = 500`.
- Không đưa YAML front matter vào nội dung chunk.
- Mỗi chunk tạo thành một `Document` riêng với `Document.id = "<doc_id>#<index>"` và `metadata["doc_id"] = "<doc_id gốc>"`.
- Dùng cùng embedding backend trong một vòng so sánh. Nếu không cài được embedding thật, dùng `mock` nhưng phải ghi rõ vì mock không biểu diễn ngữ nghĩa.
- Mỗi người chỉ thay giá trị chiến lược trong `bench.py`, không thay query, corpus, `top_k` hoặc cách tính điểm.

Chạy tất cả lệnh từ thư mục gốc repo:

```bash
python bench.py --strategy baseline --data-dir data/hoc-bong-uet --chunk-size 500 \
  | tee ket_qua_baseline.txt
```

Sau đó mỗi thành viên chạy chiến lược riêng:

```bash
python bench.py --strategy heading --data-dir data/hoc-bong-uet --chunk-size 500 \
  --provider local \
  | tee ket_qua_benchmark_vuducminh.txt

python bench.py --strategy sentence --data-dir data/hoc-bong-uet --chunk-size 500 \
  --provider local \
  | tee ket_qua_benchmark_nguyenngocvinh.txt

python bench.py --strategy recursive --data-dir data/hoc-bong-uet --chunk-size 500 \
  --provider local \
  | tee ket_qua_benchmark_nguyencongvinh.txt
```

Mỗi file kết quả phải ghi được: số chunk đã nạp, `count`, `avg_length`, top-3 của cả 5 query, score, `doc_id`, và lần chạy có/không có `metadata_filter={"audience": "student"}` cho query cần lọc.

Nếu `bench.py` trong nhóm chưa có CLI như trên, dùng đúng một dòng chọn chiến lược trong file:

```python
STRATEGY = "heading"    # Vũ Đức Minh
# STRATEGY = "sentence"  # Thành viên 2
# STRATEGY = "recursive" # Thành viên 3
```

Sau mỗi lần chạy lưu output vào một file riêng, không ghi đè kết quả của thành viên khác.

### Phân tích đường cơ sở (Baseline Analysis)

R3 chạy `ChunkingStrategyComparator().compare()` trên ba tài liệu đại diện dưới đây. Kết quả baseline phải được dùng chung cho cả nhóm; không chạy mỗi người một tham số khác nhau.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `uet-data-nest-2026-2027.md` | FixedSizeChunker (`fixed_size`) | 6 | 437.50 | Có overlap, nhưng có thể cắt giữa ý/section. |
| `uet-data-nest-2026-2027.md` | SentenceChunker (`by_sentences`) | 8 | 295.38 | Giữ trọn câu, chunk ngắn hơn. |
| `uet-data-nest-2026-2027.md` | RecursiveChunker (`recursive`) | 7 | 337.71 | Cân bằng giữa cấu trúc và kích thước. |
| `uet-evn-2025-2026.md` | FixedSizeChunker (`fixed_size`) | 4 | 489.50 | Gần sát giới hạn, dễ cắt section. |
| `uet-evn-2025-2026.md` | SentenceChunker (`by_sentences`) | 7 | 256.57 | Mạch lạc nhưng nhiều chunk hơn. |
| `uet-evn-2025-2026.md` | RecursiveChunker (`recursive`) | 5 | 360.00 | Giữ paragraph tốt hơn fixed-size. |
| `uet-scholarship-regulation-2026.md` | FixedSizeChunker (`fixed_size`) | 4 | 423.25 | Đủ nhỏ nhưng không nhận biết mục nội dung. |
| `uet-scholarship-regulation-2026.md` | SentenceChunker (`by_sentences`) | 4 | 384.25 | Giữ câu, phù hợp văn bản ngắn. |
| `uet-scholarship-regulation-2026.md` | RecursiveChunker (`recursive`) | 5 | 307.20 | Tạo các mảnh nhỏ hơn theo separator. |

### Phân công và chỉ dẫn cho từng thành viên

#### Thành viên 1 — Vũ Đức Minh: chunk theo heading/section

- **Mục tiêu:** giữ mỗi mục như “Đối tượng”, “Giá trị”, “Hồ sơ”, “Thời hạn” thành một đơn vị ngữ nghĩa.
- **Chiến lược:** `heading`.
- **Quy tắc:** tách trước các dòng bắt đầu bằng `#`, `##`, `###`; nếu section dài hơn 500 ký tự thì dùng `RecursiveChunker(chunk_size=500)` và gắn lại heading vào từng chunk con.
- **Lệnh chạy:**

```bash
python bench.py --strategy heading --data-dir data/hoc-bong-uet --chunk-size 500 \
  --provider local \
  | tee ket_qua_benchmark_vuducminh.txt
```

- **Cần ghi lại:** tổng số chunk, độ dài trung bình, top-3 của 5 query, score của top-1, `doc_id`, section/heading của chunk và kết quả A/B có/không filter.

#### Thành viên 2 — Nguyễn Ngọc Vĩnh: SentenceChunker

- **Mục tiêu:** gom tối đa 3 câu liên tiếp trong mỗi chunk.
- **Chiến lược:** `sentence` / `SentenceChunker(max_sentences_per_chunk=3)`.
- **Lệnh chạy:**

```bash
python bench.py --strategy sentence --data-dir data/hoc-bong-uet --chunk-size 500 \
  --provider local \
  | tee ket_qua_benchmark_thanhvien2.txt
```

- **Cần ghi lại:** số chunk, độ dài trung bình, top-3 và nhận xét xem câu trả lời về điều kiện/số tiền/thời hạn có bị tách khỏi ngữ cảnh không.

#### Thành viên 3 — Nguyễn Công Vinh: RecursiveChunker

- **Mục tiêu:** ưu tiên giữ paragraph/section, sau đó hạ dần xuống dòng, câu và khoảng trắng khi đoạn quá dài.
- **Chiến lược:** `recursive` / `RecursiveChunker(chunk_size=500)`.
- **Lệnh chạy:**

```bash
python bench.py --strategy recursive --data-dir data/hoc-bong-uet --chunk-size 500 \
  --provider local \
  | tee ket_qua_benchmark_thanhvien3.txt
```

- **Cần ghi lại:** số chunk, độ dài trung bình, top-3, trường hợp recursive giữ được nhiều ngữ cảnh hơn hoặc tạo chunk quá dài/quá ngắn.

#### Quy trình thu thập kết quả bắt buộc

1. Cả nhóm chạy baseline trên cùng ba file và điền bảng baseline.
2. R2 cung cấp đúng 5 query và gold answer; không thành viên nào tự đổi câu hỏi.
3. Mỗi thành viên chạy chiến lược riêng trên cùng backend và cùng `top_k=3`.
4. Với query yêu cầu đối tượng sinh viên, chạy hai lần: không filter và `metadata_filter={"audience": "student"}`.
5. Đối chiếu nội dung chunk với gold answer, không chỉ kiểm tra `doc_id`.
6. Mỗi thành viên lưu output riêng, sau đó điền khối chiến lược của mình và bảng so sánh chung.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Vũ Đức Minh**
- **Loại chiến lược:** Custom heading/section chunking
- **Embedding backend:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Kết quả:** 42 chunks; top-3 chứa ít nhất một phần thông tin trả lời ở 2/5 query.
- **Mô tả & lý do chọn cho chủ đề này:** Các thông báo học bổng được tổ chức tự nhiên theo các mục như đối tượng, giá trị, hồ sơ và thời hạn nên chunk theo heading giúp giữ được ranh giới ngữ nghĩa. Tuy nhiên, với tài liệu Goertek, heading “Hai mô hình chương trình” bị tách khỏi hai subsection “Đào tạo tại Việt Nam” và “Đào tạo tại Trung Quốc”, làm query về hai mô hình không lấy được đầy đủ nội dung trong top-3.
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
# Đã triển khai trong bench.py: HeadingChunker(chunk_size=500)
```

**Thành viên 2 — Nguyễn Ngọc Vĩnh**
- **Loại chiến lược:** SentenceChunker(max_sentences_per_chunk=3)
- **Embedding backend:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Kết quả:** 32 chunks; top-3 chứa ít nhất một phần thông tin trả lời ở 4/5 query.
- **Mô tả & lý do chọn:** SentenceChunker gom tối đa ba câu liên tiếp nên giữ được ý trọn vẹn hơn khi câu hỏi yêu cầu điều kiện hoặc thời hạn. Chiến lược này đạt kết quả retrieval tốt nhất trong ba chiến lược, nhưng query về giá trị và chỉ tiêu học bổng EVN vẫn không đưa section chứa hai con số vào top-3.
- **Code snippet (nếu custom):** Không có; dùng implementation trong `src/chunking.py`.

**Thành viên 3 — Nguyễn Công Vinh**
- **Loại chiến lược:** RecursiveChunker(chunk_size=500)
- **Embedding backend:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Kết quả:** 33 chunks; top-3 chứa ít nhất một phần thông tin trả lời ở 2/5 query.
- **Mô tả & lý do chọn:** RecursiveChunker ưu tiên giữ paragraph và section, sau đó mới hạ xuống các separator nhỏ hơn khi cần. Chiến lược giữ được điều kiện Data Nest và thời hạn MB khá tốt, nhưng các section chứa bảng/số tiền của EVN, Goertek và học bổng kỳ cuối chưa được xếp vào top-3 tương ứng.
- **Code snippet (nếu custom):** Không có; dùng implementation trong `src/chunking.py`.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Vũ Đức Minh | Heading/section | Chưa đủ dữ liệu agent | 42 chunks; giữ section rõ ràng | Tách heading khỏi subsection; 2/5 query có chunk trả lời |
| Nguyễn Ngọc Vĩnh | SentenceChunker | Chưa đủ dữ liệu agent | 32 chunks; 4/5 query có chunk trả lời | Query EVN vẫn thiếu section giá trị/chỉ tiêu trong top-3 |
| Nguyễn Công Vinh | RecursiveChunker | Chưa đủ dữ liệu agent | 33 chunks; giữ paragraph và điều kiện | Một số section số liệu không lọt top-3; 2/5 query có chunk trả lời |

### Tổng hợp score top-1 từ ba file kết quả

Các score dưới đây được lấy trực tiếp từ `ket_qua_benchmark_*.txt`; cả ba lần chạy dùng cùng embedding backend local multilingual.

| Thành viên | Backend | Số chunk | Q1 | Q2 | Q3 | Q4 | Q5 | Score top-1 trung bình |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Vũ Đức Minh — heading | multilingual MiniLM | 42 | 0.772884 | 0.657033 | 0.479062 | 0.714526 | 0.867222 | 0.698145 |
| Nguyễn Ngọc Vĩnh — sentence | multilingual MiniLM | 32 | 0.755795 | 0.633325 | 0.594524 | 0.674286 | 0.836103 | 0.698807 |
| Nguyễn Công Vinh — recursive | multilingual MiniLM | 33 | 0.751200 | 0.652748 | 0.485539 | 0.688203 | 0.862580 | 0.688054 |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
Xét riêng coverage nội dung top-3, SentenceChunker tốt nhất với 4/5 query có ít nhất một phần thông tin trả lời; query Data Nest vẫn cần ghép thêm ngữ cảnh để có câu trả lời đầy đủ. Heading/section có ưu điểm về tính dễ đọc và giữ cấu trúc tài liệu, nhưng cần xử lý đặc biệt để gắn heading cha với các subsection con. RecursiveChunker giữ ngữ cảnh tương đối tốt nhưng vẫn có thể xếp các chunk chứa số liệu quan trọng xuống ngoài top-3. Kết luận này chỉ đánh giá retrieval; cần bổ sung output của agent để chấm đầy đủ 10 điểm chất lượng truy xuất.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Điều kiện để sinh viên được xét học bổng Data Nest là gì? | Sinh viên đại học chính quy năm thứ 3 thuộc Khoa Công nghệ thông tin hoặc Viện Trí tuệ nhân tạo; có nguyện vọng; có GPA từ 3.0 và rèn luyện từ Tốt trở lên **hoặc** có hoàn cảnh kinh tế khó khăn; chưa nhận/đang đề xuất học bổng khác trong năm học 2026–2027. | `uet-data-nest-adjustment-2026-2027.md`, mục **Đối tượng sau điều chỉnh** |
| 2 | Học bổng EVN có giá trị bao nhiêu và có bao nhiêu suất? | Giá trị **10.000.000 đồng/sinh viên/năm học**, có **15 suất**. | `uet-evn-2025-2026.md`, mục **Giá trị và chỉ tiêu** |
| 3 | Chương trình Goertek có những mô hình đào tạo nào? | Có hai mô hình: **đào tạo tại Việt Nam** và **đào tạo tại Trung Quốc**. | `uet-goertek-2027.md`, các mục **Đào tạo tại Việt Nam** và **Đào tạo tại Trung Quốc** |
| 4 | Sinh viên chương trình CLC CNTT loại Giỏi được nhận học bổng kỳ cuối bao nhiêu? | Mức học bổng là **4.000.000 đồng/sinh viên/tháng**. | `uet-final-term-scholarship-graduates-2026.md`, mục **Mức học bổng** |
| 5 | Hạn đăng ký học bổng The Best of MB Chasing 2026 là khi nào? | Hạn đăng ký là **12h00 ngày 10/08/2026**. | `uet-mb-best-of-chasing-2026.md`, mục **Thông tin chương trình** |

### Đối chiếu top-3 theo nội dung chunk

Các trạng thái dưới đây được xác định bằng cách kiểm tra nội dung chunk, không chỉ kiểm tra `doc_id`. “Một phần” nghĩa là top-3 có fragment liên quan nhưng chưa chắc đủ toàn bộ gold answer. Ba file kết quả chỉ ghi retrieval top-3, chưa ghi câu trả lời do `KnowledgeBaseAgent` sinh ra.

| Query | Heading — Vũ Đức Minh | Sentence — Nguyễn Ngọc Vĩnh | Recursive — Nguyễn Công Vinh | Nhận xét |
|---|---|---|---|---|
| 1 | Một phần: `uet-data-nest-2026-2027#1` | Một phần: `uet-data-nest-2026-2027#0` | Có: `uet-data-nest-adjustment-2026-2027#1` | Recursive lấy được chunk chứa điều kiện sau điều chỉnh đầy đủ hơn. |
| 2 | Không | Không | Không | Cả ba lấy đúng tài liệu EVN ở top-1 nhưng không lấy được section chứa `10.000.000 đồng` và `15 suất` trong top-3. |
| 3 | Không | Có một phần: `uet-goertek-2027#0`, `#2` | Không | Sentence lấy được thông tin của hai mô hình ở hai chunk khác nhau. |
| 4 | Có: `uet-final-term-scholarship-graduates-2026#3` | Có: `uet-final-term-scholarship-graduates-2026#0` | Không | Heading và Sentence đều lấy được bảng/mức 4.000.000 đồng. |
| 5 | Có: `uet-mb-best-of-chasing-2026#1` | Có: `uet-mb-best-of-chasing-2026#0` | Có: `uet-mb-best-of-chasing-2026#1` | Cả ba đều lấy được deadline; Sentence đưa vào top-1. |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Điều kiện Data Nest | RecursiveChunker | Có | Chunk `uet-data-nest-adjustment-2026-2027#1` chứa điều kiện sau điều chỉnh. |
| 2 | Giá trị và chỉ tiêu EVN | Chưa có chiến lược đạt | Không | Đây là failure case chung: đúng tài liệu nhưng sai section. |
| 3 | Hai mô hình Goertek | SentenceChunker | Có | Hai mảnh chứa thông tin Việt Nam/Trung Quốc được đưa vào top-3. |
| 4 | Mức học bổng CLC CNTT loại Giỏi | SentenceChunker | Có | Chunk top-1 chứa mức 4.000.000 đồng. |
| 5 | Deadline MB Chasing | SentenceChunker | Có | Chunk top-1 chứa thời hạn 12h00 ngày 10/08/2026. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Trong output của cả ba thành viên, query 1 có và không có `metadata_filter={"audience": "student"}` cho kết quả top-3 giống hệt nhau. Điều này cho thấy query hiện tại chưa thật sự cần filter: các chunk đúng đã được xếp hạng cao và tài liệu `audience=all` không cạnh tranh trong top-3. Nhóm cần bổ sung một câu hỏi có hai tài liệu cùng chủ đề nhưng khác audience, hoặc điều chỉnh corpus/query, để chứng minh filter làm thay đổi kết quả và cải thiện precision.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- SentenceChunker đạt coverage nội dung top-3 tốt nhất: 4/5 query, trong khi Heading và Recursive đạt 2/5.
- Chunk đúng tài liệu chưa chắc trả lời được câu hỏi: query EVN thường lấy đúng `doc_id` ở top-1 nhưng không lấy section chứa giá trị và số suất.
- Chunk theo heading phù hợp với tài liệu học bổng, nhưng phải tránh tạo chunk chỉ có heading như section “Hai mô hình chương trình” của Goertek.

**Bài học rút ra khi so sánh trong nhóm:**
Trên cùng corpus và cùng embedding backend, số chunk và vị trí thông tin thay đổi đáng kể theo chiến lược: Sentence tạo 32 chunk, Recursive tạo 33 chunk và Heading tạo 42 chunk. Sentence giữ được câu trả lời ở nhiều query nhất, còn Heading dễ giải thích theo cấu trúc tài liệu nhưng có thể tách heading khỏi nội dung. Nhóm cũng nhận ra cần đánh giá nội dung chunk và câu trả lời của agent, không chỉ kiểm tra tài liệu gốc có xuất hiện trong top-3.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
Nhóm sẽ cải tiến HeadingChunker để gộp heading cha với subsection đầu tiên hoặc gắn heading cha vào mọi chunk con, tránh chunk chỉ chứa tiêu đề. Nhóm cũng sẽ thiết kế lại benchmark query và metadata audience để có một tình huống filter thực sự làm thay đổi kết quả; đồng thời ghi thêm agent answer và chuỗi bằng chứng bắt buộc để chấm grounding đầy đủ.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 9/ 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **33 / 40** |
