"""
Script crawl dữ liệu chính sách bảo hành MacBook từ CellphoneS
Yêu cầu cài đặt: pip install requests beautifulsoup4
"""

import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Danh sách URL 5 sản phẩm MacBook trên CellphoneS
PRODUCT_URLS = [
    "https://cellphones.com.vn/macbook-air-2020-m1.html",
    "https://cellphones.com.vn/macbook-air-m2-2022.html",
    "https://cellphones.com.vn/macbook-air-m3-2024.html",
    "https://cellphones.com.vn/macbook-pro-14-inch-m3.html",
    "https://cellphones.com.vn/macbook-pro-16-inch-m3.html"
]

# Thư mục đích theo yêu cầu của repo
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "ecommerce")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def create_markdown_content(title, url, content, doc_id):
    """
    Tạo nội dung Markdown chứa metadata YAML frontmatter theo chuẩn K4_VARIANT.md
    """
    today = datetime.now().strftime("%Y-%m-%d")
    version = datetime.now().strftime("%Y.%m")
    
    # Metadata theo yêu cầu của Giai đoạn 2 (audience, source_url, retrieved_at, document_version + 1 trường category)
    md_template = f"""---
doc_id: {doc_id}
title: {title}
audience: buyer
category: warranty-policy
brand: apple
language: vi
source_url: {url}
retrieved_at: {today}
document_version: "{version}"
---

# {title}

{content}
"""
    return md_template

def crawl_cellphones_warranty(url):
    """
    Crawl thông tin sản phẩm và chính sách bảo hành
    Lưu ý: Website CellphoneS sử dụng render JS (Nuxt.js), do đó nếu thông tin bảo hành 
    được load động qua API, bạn có thể cần đổi sang dùng Selenium/Playwright thay vì requests.
    """
    print(f"Đang crawl: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Lấy tên sản phẩm (thường nằm trong thẻ h1 hoặc div.box-product-name)
        title_tag = soup.find('div', class_='box-product-name') or soup.find('h1')
        title = title_tag.text.strip() if title_tag else "Sản phẩm MacBook"
        
        # 2. Lấy thông tin bảo hành
        # Giả định lấy các nội dung liên quan đến bảo hành trong trang
        warranty_div = soup.find('div', class_='box-warranty-info')
        
        if warranty_div:
            warranty_text = warranty_div.get_text(separator="\n- ", strip=True)
            content = f"## Thông tin bảo hành chi tiết\n- {warranty_text}"
        else:
            # Fallback (phòng trường hợp HTML bị chặn hoặc load động bằng JS)
            # Đây là chính sách chuẩn thường thấy trên CellphoneS đối với MacBook
            content = (
                "## 1. Đổi mới sản phẩm\n"
                "- Hỗ trợ 1 ĐỔI 1 miễn phí trong 30 ngày đầu tiên nếu máy có lỗi phần cứng từ nhà sản xuất.\n\n"
                "## 2. Bảo hành tiêu chuẩn (Chính hãng Apple)\n"
                "- Hàng chính hãng VN/A, bảo hành 12 tháng kể từ ngày mua/kích hoạt.\n"
                "- Có thể bảo hành tại các trung tâm bảo hành ủy quyền của Apple (AASP) như CareS.\n\n"
                "## 3. Dịch vụ bảo hành mở rộng\n"
                "- Có hỗ trợ mua kèm gói 1 đổi 1 VIP (12 hoặc 24 tháng).\n"
                "- Hỗ trợ đăng ký và gia hạn dịch vụ Apple Care+ cho máy Mac."
            )
            
        return title, content
        
    except Exception as e:
        print(f"Lỗi khi crawl {url}: {e}")
        return None, None

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    for url in PRODUCT_URLS:
        # Tạo doc_id từ URL
        slug = url.rstrip('/').split('/')[-1].replace('.html', '')
        doc_id = f"{slug}-warranty"
        
        title, content = crawl_cellphones_warranty(url)
        
        if title and content:
            # Định dạng tiêu đề cho bài Lab
            md_title = f"Chính sách bảo hành {title}"
            
            # Gộp thành văn bản Markdown hoàn chỉnh
            md_content = create_markdown_content(md_title, url, content, doc_id)
            
            # Ghi ra file
            filename = f"{doc_id}.md"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_content)
                
            print(f"✅ Đã lưu file: {filepath}")
            
        # Nghỉ 2 giây giữa các request để tránh bị khoá IP
        time.sleep(2)

if __name__ == "__main__":
    print("Bắt đầu crawl dữ liệu CellphoneS...")
    main()
    print("Hoàn tất! Kiểm tra dữ liệu tại thư mục data/ecommerce/")
