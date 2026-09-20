# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** BaConYeuMeCon
**Thành viên:** Ngô Tuấn Tùng - 2A202602826; Nguyễn Huy Cương - 2A202602842; Trần Văn Khánh - 2A202602413
**Ngày:** 2026-09-20

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách bảo hành, đổi trả và quyền lợi MacBook tại CellphoneS

**Tại sao nhóm chọn chủ đề này?**
> Nhóm chọn chủ đề này vì tài liệu có nhiều quy tắc, thời hạn, điều kiện và ngoại lệ phù hợp để đánh giá retrieval. Các câu trả lời cần trỏ ngược về nguồn công khai, nên citation và trace chunk có giá trị thực tế.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | MacBook Air M1 2020 | https://cellphones.com.vn/macbook-air-2020-m1.html | 2026-09-20 / 2026.09 | 3017 | buyer, warranty-policy, vi |
| 2 | MacBook Air M2 2022 | https://cellphones.com.vn/macbook-air-m2-2022.html | 2026-09-20 / 2026.09 | 3204 | buyer, warranty-policy, vi |
| 3 | MacBook Air M3 2024 | https://cellphones.com.vn/macbook-air-m3-2024.html | 2026-09-20 / 2026.09 | 3473 | buyer, warranty-policy, vi |
| 4 | MacBook Pro 14 M3 2023 | https://cellphones.com.vn/macbook-pro-14-inch-m3.html | 2026-09-20 / 2026.09 | 3238 | buyer, warranty-policy, vi |
| 5 | MacBook Pro 16 M3 Max 2023 | https://cellphones.com.vn/macbook-pro-16-inch-m3.html | 2026-09-20 / 2026.09 | 3192 | buyer, warranty-policy, vi |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

Các trường chính: `doc_id` (tài liệu gốc, hỗ trợ delete), `source_url` (citation), `audience` (lọc buyer/seller), `retrieved_at` và `document_version` (theo dõi độ mới).

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `category` | string | `warranty-policy` | Phân biệt loại chính sách |
| `language` | string | `vi` | Chọn embedder/đánh giá ngôn ngữ |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| corpus.md | FixedSizeChunker (`fixed_size`) | 26 | 778.5 | Chunk đều, giữ overlap; có thể cắt giữa câu |
| corpus.md | SentenceChunker (`by_sentences`) | 52 | 347.8 | Giữ câu tự nhiên nhưng số chunk nhiều hơn |
| corpus.md | RecursiveChunker (`recursive`) | 34 | 534.3 | Cân bằng độ dài và ranh giới đoạn; chọn mặc định |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Trần Văn Khánh (2A202602413)**
- **Loại chiến lược:** Recursive + hybrid intent router + citation trace
- **Mô tả & lý do chọn cho chủ đề này:** Tài liệu chính sách có heading và đoạn điều kiện, nên recursive giữ được đơn vị ngữ nghĩa tốt hơn. Agent route intent, hỏi lại câu mơ hồ và hiển thị score/source/chunk để đánh giá retrieval.
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — Ngô Tuấn Tùng (2A202602826)**
- **Loại chiến lược:** Sentence
- **Mô tả & lý do chọn:** Chunk theo nhóm câu giúp câu trả lời ngắn và dễ đọc, đổi lại số chunk tăng.
- **Code snippet (nếu custom):**

**Thành viên 3 — Nguyễn Huy Cương (2A202602842)**
- **Loại chiến lược:** FixedSize
- **Mô tả & lý do chọn:** Dễ kiểm soát kích thước và có overlap, phù hợp khi cần throughput ổn định.
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Trần Văn Khánh | Recursive + router/citation | 8 / 10 | Giữ section, trace rõ | Mock embedding nhiễu |
| Ngô Tuấn Tùng | Sentence | Chưa đo | Chunk dễ đọc | Nhiều chunk |
| Nguyễn Huy Cương | FixedSize | Chưa đo | Độ dài ổn định | Có thể cắt ngữ nghĩa |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Recursive là lựa chọn tốt nhất cho corpus chính sách vì ưu tiên ranh giới đoạn và tạo 34 chunk trung bình 534 ký tự. Sentence phù hợp kiểm tra câu trả lời ngắn, còn FixedSize phù hợp baseline nhưng overlap không bảo đảm giữ trọn điều kiện.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | MacBook Air M1 được bảo hành bao lâu? | Bảo hành chính hãng 12 tháng | corpus#33 / top-3 |
| 2 | Điều kiện đổi mới MacBook Air M1 là gì? | Máy như mới, hộp/phụ kiện đầy đủ, đăng xuất tài khoản | corpus#5 / top-3 |
| 3 | Gói 1 đổi 1 VIP có những quyền lợi nào? | Đổi máy tương đương, lỗi nhà sản xuất, xử lý 24h đến 14 ngày | corpus#15 / top-3 |
| 4 | Người mua cần làm gì trước khi mang máy đi bảo hành? | Sao lưu dữ liệu cá nhân | corpus#27 / top-3 |
| 5 | Câu hỏi mơ hồ “Cái này thì sao?” | Agent phải hỏi lại, không truy xuất mù | clarification gate |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | MacBook Air M1 được bảo hành bao lâu? | Recursive | Có | citation [S1], score 0.231 |
| 2 | Điều kiện đổi mới MacBook Air M1 là gì? | Recursive | Có | top-3 có tie score 0.275, cần đánh giá nội dung |
| 3 | Gói 1 đổi 1 VIP có những quyền lợi nào? | Recursive | Có | citation [S1], score 0.223 |
| 4 | Người mua cần làm gì trước khi mang máy đi bảo hành? | Recursive | Có | citation [S1], score 0.256 |
| 5 | Câu hỏi mơ hồ “Cái này thì sao?” | Clarification | Không retrieval | Agent hỏi lại để làm giàu thông tin |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Metadata filter phù hợp nhất khi corpus có nhiều audience khác nhau, ví dụ intent seller tự gắn `audience=seller`. Corpus MacBook hiện chủ yếu là buyer nên A/B filter chưa tạo khác biệt lớn. Cần bổ sung tài liệu seller thật để đánh giá chính xác lợi ích và rủi ro của filter.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - UI cho chọn Fixed-size, Sentence hoặc Recursive trước khi index.
> - Mỗi câu trả lời có citation `[S#]` và panel trace score/source/chunk.
> - Câu hỏi mơ hồ bị chặn trước retrieval để tránh trả lời đoán.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng corpus nhưng FixedSize tạo 26 chunk lớn, Sentence tạo 52 chunk ngắn và Recursive tạo 34 chunk cân bằng. Mock embedding làm ranking nhiễu, vì vậy trace nội dung quan trọng hơn chỉ nhìn score.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ dùng multilingual embedding thật, lưu citation metadata ngay từ ingestion và bổ sung bộ câu hỏi có gold answer. Corpus cũng nên được tách theo tài liệu gốc nếu cần filter/citation chi tiết hơn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 13 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 8 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **34 / 40** |
