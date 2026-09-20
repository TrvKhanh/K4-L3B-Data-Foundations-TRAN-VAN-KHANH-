import os
import re

directory = "data/ecommerce"

detailed_text = """
**Chi tiết quyền lợi Gói 1 đổi 1 VIP (12 tháng / 24 tháng):**
- **Sản phẩm ứng dụng:** Điện thoại, máy tính bảng mới/cũ, tai nghe cao cấp mới, đồng hồ thông minh Apple/Samsung mới (áp dụng tương tự cho MacBook).
- **Quyền lợi và dịch vụ bảo hành:**
  + Bao test 1 đổi 1 toàn bộ phần cứng máy tính (Bao gồm lỗi nhân vật lý - Lỗi pin dưới 80%).
  + Không giới hạn số lần bảo trì thay đổi máy nếu phát hiện lỗi (trong phạm vi bảo hành) trong thời gian tham gia.
  + Đổi máy tương thích sản phẩm bảo hành.
  + Được chuyển quyền sở hữu sản phẩm và gói bảo hành trong thời gian tham gia.
  + Khách hàng sử dụng dịch vụ Bảo hành mở rộng của CellphoneS có đặc quyền +3% tổng giá trị máy thu cũ khi lên đời trong thời gian bảo hành của thiết bị.
- **Điều kiện bảo hành:** Sản phẩm bị lỗi do nhà sản xuất.
- **Lưu ý:** Gói bảo hành không có hiệu lực với các sản phẩm bị biến đổi như ban đầu (cấn, móp, cong, vênh, nứt,...) và các sản phẩm bị vào nước hoặc đã được sửa chữa.
- **Xử lý thời gian:** Trong vòng 24h và tối đa 14 ngày làm việc tuỳ thuộc vào trạng thái của sản phẩm.
"""

for filename in os.listdir(directory):
    if filename.startswith("macbook") and filename.endswith(".md"):
        filepath = os.path.join(directory, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Find where to insert. We can insert right before "## 4." or "### IV." or "## D." or "### 4."
        # Let's use regex to find the last section (Lưu ý / Miễn trừ trách nhiệm)
        # We will insert `detailed_text` before it.
        
        match = re.search(r'\n(## 4\.|### IV\.|## D\.|### 4\.)', content)
        if match:
            insert_pos = match.start()
            new_content = content[:insert_pos] + "\n" + detailed_text + "\n" + content[insert_pos:]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {filename}")
        else:
            print(f"Could not find insertion point in {filename}")

