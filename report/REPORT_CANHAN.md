# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Văn Khánh - 2A202602413
**Nhóm:** BaConYeuMeCon
**Ngày:** 2026-09-20

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector có hướng gần nhau, nghĩa là embedding biểu diễn nội dung/chủ đề tương tự nhau. Giá trị gần 1 là tương đồng cao, gần 0 là ít liên quan.

**Ví dụ có độ tương tự CAO:**
- Câu A: Điều kiện bảo hành MacBook là gì?
- Câu B: MacBook được bảo hành trong bao lâu?
- Tại sao tương đồng: Cùng nói về chính sách và thời hạn bảo hành.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Điều kiện đổi mới MacBook là gì?
- Câu B: Công thức tính diện tích hình tròn là gì?
- Tại sao khác: Hai câu thuộc hai miền kiến thức khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào hướng của vector nên ít bị ảnh hưởng bởi độ dài văn bản. Với text embeddings, điều này thường phản ánh chủ đề tốt hơn khoảng cách Euclid thuần túy.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Bước nhảy là `500 - 50 = 450`; số chunk là `ceil((10000 - 500) / 450) + 1 = 22`.
> **Đáp án:** 22 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap 100, bước nhảy còn 400 nên số chunk tăng lên `ceil(9900 / 400) = 25`. Overlap lớn giúp giữ ngữ cảnh ở biên chunk nhưng làm tăng chi phí indexing.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> `SentenceChunker` dùng regex nhận diện dấu `.`, `!`, `?` đi kèm whitespace hoặc xuống dòng, sau đó gom tối đa N câu. Text rỗng trả về list rỗng và mỗi chunk được strip khoảng trắng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `RecursiveChunker` ưu tiên tách theo `\n\n`, `\n`, `. `, khoảng trắng rồi mới tách ký tự. Base case là text không vượt `chunk_size`; nếu hết separator thì fallback cắt theo độ dài để luôn tạo được chunk.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Store chuẩn hóa mỗi Document thành record gồm id, content, metadata và embedding, rồi giữ trong bộ nhớ. Search embed query, tính dot product với từng record, sắp xếp giảm dần và trả tối đa top-k cùng score.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc metadata trước khi similarity search để các slot top-k không bị chiếm bởi tài liệu sai. `delete_document` xóa mọi chunk có `metadata['doc_id']` bằng doc_id gốc.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent route intent trước, hỏi lại nếu câu mơ hồ, rồi lấy top-k chunk. Prompt đánh số citation `[S1]`, nêu nguồn/chunk, yêu cầu chỉ dùng context; trace giữ score, source và nội dung để kiểm chứng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
42 passed in 0.09s (`pytest -q`)
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Bảo hành MacBook / thời hạn bảo hành | Bảo hành MacBook / đổi mới | cao | mock embedding | Có thể nhiễu |
| 2 | Chính sách bảo hành | Công thức nấu ăn | thấp | mock embedding | Có thể nhiễu |
| 3 | Đổi trả và hoàn tiền | Người bán bảo hành | thấp | mock embedding | Có thể nhiễu |
| 4 | Điều kiện đổi mới | Lỗi phần cứng | cao | mock embedding | Có thể nhiễu |
| 5 | Apple Care+ | Quy trình hoàn tiền | thấp | mock embedding | Có thể nhiễu |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ là một số chunk có score thấp hoặc tie dù chứa cùng chủ đề. Điều này cho thấy embedding mock dựa trên hash không biểu diễn ngữ nghĩa thật; cần embedding multilingual để đánh giá retrieval công bằng.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | MacBook Air M1 được bảo hành bao lâu? | corpus#33 | 0.231 | Có, top-3; citation [S1] |
| 2 | Điều kiện đổi mới MacBook Air M1 là gì? | corpus#5 | 0.275 | Có, top-3; cần kiểm tra nội dung vì mock tie |
| 3 | Gói 1 đổi 1 VIP có những quyền lợi nào? | corpus#15 | 0.223 | Có, top-3; citation [S1] |
| 4 | Người mua cần làm gì trước khi mang máy đi bảo hành? | corpus#27 | 0.256 | Có, top-3; citation [S1] |
| 5 | Câu hỏi mơ hồ: “Cái này thì sao?” | Không retrieval | -- | Agent hỏi lại để làm rõ |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5 câu rõ; câu 5 được chặn để hỏi lại.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng citation và trace giúp phân biệt câu trả lời có bằng chứng với câu trả lời chỉ nghe hợp lý. Mock embedding phù hợp kiểm thử pipeline nhưng không đủ để kết luận chất lượng ngữ nghĩa; benchmark thật nên dùng multilingual embedding.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |
