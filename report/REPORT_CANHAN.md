# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Đức Minh - 2A202602895
**Nhóm:** TwoMenSquad
**Ngày:** 19/9/2026
> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Độ tương tự cosine đo mức độ giống nhau về hướng giữa 2 vector embedding embedding. Cosine similarity cao thường thể hiện 2 câu có ý nghĩa tương đồng gần nhau nhưng có thể có cách viết khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: Tôi sẽ hoàn thành bài lab này trước hạn
- Câu B: Bài lab này sẽ được hoàn thành trước hạn bởi tôi
- Tại sao tương đồng: Cùng ý nghĩa, chỉ tráo đổi vai trò chủ, vị ngữ

**Ví dụ có độ tương tự THẤP:**
- Câu A: Thế giới sẽ trở nên hoang tàn
- Câu B: Mai trời sẽ tạnh mưa và nắng đẹp
- Tại sao khác: Khác nhau hoàn toàn về ý nghĩa

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Cosine similarity được ưu tiên hơn khoảng cách Euclid vì nó tập trung vào hướng của vector, tức là nội dung ngữ nghĩa, thay vì độ lớn tuyệt đối của vector. Điều này phù hợp với text embedding vì các văn bản dài hơn có thể tạo ra vector có độ lớn khác nhau nhưng vẫn có cùng chủ đề.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* số chunk = ceil((độ dài tài liệu - overlap) / (chunk_size - overlap))
> *Đáp án:*ceil((10.000 - 50) / (500 - 50))
= ceil(9.950 / 450)
= ceil(22,11)
= 23

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Nếu tăng overlap lên 100: ceil((10.000 - 100) / (500 - 100))
= ceil(9.900 / 400)
= ceil(24,75)
= 25

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Hàm sử dụng biểu thức chính quy `(?<=[.!?])(?:\s+|\n+)` để tách văn bản sau các dấu kết thúc câu `.`, `!` và `?`. Sau khi tách, các câu được loại bỏ khoảng trắng thừa, bỏ câu rỗng và gom lại thành từng nhóm tối đa `max_sentences_per_chunk` câu. Với văn bản rỗng hoặc chỉ chứa khoảng trắng, hàm trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán thử các separator theo thứ tự ưu tiên `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng là từng ký tự. Base case là khi đoạn văn bản không dài hơn `chunk_size`; khi đó đoạn được trả về trực tiếp. Nếu không còn separator phù hợp, văn bản được cắt cứng theo `chunk_size`; các mảnh nhỏ liền kề được gom lại để hạn chế tạo ra quá nhiều chunk vụn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
`add_documents` tạo một record cho mỗi `Document`, gồm `id`, `content`, `metadata` và vector embedding, sau đó lưu vào danh sách in-memory. Metadata được sao chép và tự bổ sung `doc_id` nếu chưa có. Khi search, query được embedding bằng cùng embedding function, sau đó tính dot product với các vector đã lưu, sắp xếp score giảm dần và trả về tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
`search_with_filter` lọc các record theo metadata trước rồi mới thực hiện similarity search trên tập ứng viên còn lại. Cách này giúp các kết quả không đúng đối tượng không chiếm vị trí trong top-k. `delete_document` tạo lại danh sách store, loại bỏ mọi chunk có `metadata["doc_id"]` trùng với `doc_id` được yêu cầu và trả về `True` nếu có record bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
`answer` trước tiên gọi `store.search` để lấy các chunk liên quan nhất. Nội dung các chunk được đánh số và ghép thành phần “Ngữ cảnh” trong prompt, sau đó prompt cũng chứa câu hỏi và yêu cầu tác tử chỉ sử dụng thông tin trong ngữ cảnh. Cuối cùng, prompt được truyền vào `llm_fn` và kết quả trả về là câu trả lời của agent.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v
42 passed
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần trước hạn. | Sinh viên phải hoàn tất đăng ký môn học đúng thời hạn. | cao | 0.719204 | Có |
| 2 | Thư viện mở cửa từ 8 giờ sáng. | Ký túc xá nằm gần khu giảng đường. | thấp | 0.233252 | Có |
| 3 | Học bổng dành cho sinh viên có thành tích tốt. | Sinh viên đạt kết quả học tập cao có thể được nhận học bổng. | cao | 0.891843 | Có |
| 4 | Cần nộp đơn trước ngày 30/9. | Thư viện có nhiều sách tham khảo. | thấp | 0.096913 | Có |
| 5 | Mật khẩu không được chia sẻ cho người khác. | Không nên cung cấp thông tin đăng nhập cho người khác. | cao | 0.570649 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
Kết quả dùng local multilingual embedding cho thấy cặp 3 có độ tương đồng cao nhất (`0.891843`), còn cặp 4 có độ tương đồng thấp nhất (`0.096913`), phù hợp với dự đoán ban đầu. Cặp 5 là điểm đáng chú ý: hai câu cùng nói về bảo mật thông tin nhưng score (`0.570649`) thấp hơn cặp 1 và cặp 3, cho thấy embedding vẫn nhạy với cách diễn đạt và từ vựng cụ thể. Nhìn chung, local embedding đã phản ánh tốt hơn quan hệ ngữ nghĩa so với `MockEmbedder`, nhưng score cần được so sánh tương đối trong cùng tập câu thay vì áp dụng một ngưỡng tuyệt đối cho mọi chủ đề.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Điều kiện để sinh viên được xét học bổng Data Nest là gì? | `uet-data-nest-adjustment-2026-2027#0`: thông báo điều chỉnh đối tượng Data Nest. | 0.772884 | Một phần — top-3 có thêm `uet-data-nest-2026-2027#1`, nhưng chưa có đầy đủ điều kiện sau điều chỉnh. | Agent trả lời: **“Không tìm thấy đủ thông tin để trả lời câu hỏi trong các chunk được truy xuất.”** Context chưa chứa đầy đủ điều kiện sau điều chỉnh. |
| 2 | Học bổng EVN có giá trị bao nhiêu và có bao nhiêu suất? | `uet-evn-2025-2026#0`: tiêu đề và phần giới thiệu chương trình EVN. | 0.657033 | Không — top-3 không chứa section `Giá trị và chỉ tiêu`. | Agent trả lời: **“Không tìm thấy đủ thông tin để trả lời câu hỏi trong các chunk được truy xuất.”** Context không có **10.000.000 đồng/sinh viên/năm học** và **15 suất**. |
| 3 | Chương trình Goertek có những mô hình đào tạo nào? | `uet-goertek-2027#0`: tiêu đề và công văn giới thiệu chương trình. | 0.479062 | Không — top-3 có heading “Hai mô hình chương trình” nhưng không có nội dung hai mô hình. | Agent trả lời: **“Không tìm thấy đủ thông tin để trả lời câu hỏi trong các chunk được truy xuất.”** Context chỉ có tiêu đề, chưa có nội dung hai mô hình. |
| 4 | Sinh viên chương trình CLC CNTT loại Giỏi được nhận học bổng kỳ cuối bao nhiêu? | `uet-final-term-scholarship-graduates-2026#0`: thông báo cấp học bổng kỳ cuối. | 0.714526 | Có — top-3 có `#3` chứa bảng mức học bổng. | Sau khi sửa kiểm tra không phân biệt hoa/thường bằng `casefold()`, Agent trả lời: **“Sinh viên chương trình CLC CNTT loại Giỏi nhận học bổng 4.000.000 đồng/sinh viên/tháng.”** |
| 5 | Hạn đăng ký học bổng The Best of MB Chasing 2026 là khi nào? | `uet-mb-best-of-chasing-2026#0`: tiêu đề và giới thiệu chương trình. | 0.867222 | Có — top-3 có `uet-mb-best-of-chasing-2026#1` chứa thời hạn. | Agent trả lời: **“Hạn đăng ký học bổng The Best of MB Chasing 2026 là 12h00 ngày 10/08/2026.”** |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5 nếu tính cả query 1 có fragment liên quan; chỉ 2 / 5 nếu yêu cầu chunk chứa đủ toàn bộ gold answer.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
SentenceChunker của Nguyễn Ngọc Vĩnh đạt coverage tốt hơn với 4/5 query, trong khi heading chunking của tôi có ưu điểm là giữ được cấu trúc mục của tài liệu. Kết quả query EVN cho thấy lấy đúng `doc_id` ở top-1 chưa đủ; chunk phải chứa đúng con số hoặc điều kiện cần trả lời. Ngoài ra, metadata filter ở query Data Nest không làm thay đổi top-3, nên cần thiết kế query và corpus có khác biệt audience rõ hơn.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5/ 5 |
| Hướng tiếp cận của tôi (My Approach) | 10/ 10 |
| Hoàn thiện code (Core Implementation — tests) | 30/ 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) |10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
