import os
import pandas as pd
import streamlit as st
from src.chunking import FixedSizeChunker, SentenceChunker, RecursiveChunker

st.set_page_config(page_title="Data & Chunking Visualizer", layout="wide")

st.title("Phân tích Dữ liệu & Thuật toán Chunking")

# Define paths
DATA_DIR = "data/ecommerce"
CSV_PATH = os.path.join(DATA_DIR, "sources.csv")

# Create tabs
tab1, tab2 = st.tabs(["📊 1. Trực quan hóa nguồn dữ liệu", "✂️ 2. Chạy thuật toán Chunking"])

# ----------------- TAB 1: DATA VISUALIZATION -----------------
with tab1:
    st.header("Trực quan hóa Nguồn Dữ liệu (Corpus)")
    
    if os.path.exists(CSV_PATH):
        # Load CSV manifest
        df = pd.read_csv(CSV_PATH)
        
        # Calculate lengths
        lengths = []
        for path in df['file_path']:
            full_path = os.path.join(os.path.dirname(DATA_DIR), "..", path) if not os.path.exists(path) else path
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    lengths.append(len(f.read()))
            else:
                lengths.append(0)
        
        df['char_count'] = lengths
        
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Tổng số tài liệu", len(df))
        c2.metric("Tổng số ký tự (Corpus)", sum(lengths))
        c3.metric("Chiều dài trung bình", f"{int(sum(lengths)/len(lengths))} ký tự" if lengths else "0")
        
        st.subheader("Bảng Metadata (sources.csv)")
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Phân bố chiều dài tài liệu")
        st.bar_chart(data=df, x="doc_id", y="char_count", use_container_width=True)
        
        st.subheader("Xem nhanh nội dung")
        selected_doc = st.selectbox("Chọn tài liệu để xem nội dung:", df['doc_id'])
        if selected_doc:
            doc_path = df[df['doc_id'] == selected_doc]['file_path'].values[0]
            if os.path.exists(doc_path):
                with open(doc_path, "r", encoding="utf-8") as f:
                    st.text_area("Nội dung (Raw Text)", f.read(), height=300)
            else:
                st.error("Không tìm thấy file trên ổ cứng.")
    else:
        st.warning(f"Không tìm thấy file {CSV_PATH}. Hãy chắc chắn bạn đã crawl dữ liệu.")


# ----------------- TAB 2: CHUNKING VISUALIZER -----------------
with tab2:
    st.header("Thuật toán Chunking Chuyên Biệt")
    
    @st.cache_data
    def get_data_files():
        if not os.path.exists(DATA_DIR):
            return []
        return [f for f in os.listdir(DATA_DIR) if f.endswith(".md")]

    files = get_data_files()

    if not files:
        st.warning(f"Không tìm thấy file .md nào trong {DATA_DIR}.")
    else:
        # Chọn file
        selected_file = st.selectbox("Chọn nguồn dữ liệu để Chunk:", files)
        file_path = os.path.join(DATA_DIR, selected_file)
        
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        # Khởi tạo session_state để lưu kết quả nếu chưa có
        if "res_fixed" not in st.session_state:
            st.session_state.res_fixed = None
        if "res_sent" not in st.session_state:
            st.session_state.res_sent = None
        if "res_rec" not in st.session_state:
            st.session_state.res_rec = None
            
        # Nút xóa toàn bộ kết quả (nếu muốn dọn dẹp)
        if st.button("🔄 Xóa / Reset Kết Quả"):
            st.session_state.res_fixed = None
            st.session_state.res_sent = None
            st.session_state.res_rec = None

        # Tạo 3 Khung (Columns) song song trong cùng 1 Tab
        col_fixed, col_sentence, col_recursive = st.columns(3)
        
        # Hàm hỗ trợ hiển thị
        def render_chunks(chunks, bg_color):
            st.caption(f"Tổng số: **{len(chunks)} chunks**")
            for i, c in enumerate(chunks):
                length = len(c)
                st.markdown(
                    f'''<div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 15px; font-size: 15px; border: 1px solid #ddd; color: #333; line-height: 1.6;">
                    <div style="font-weight: bold; margin-bottom: 8px; color: #555;">Chunk #{i+1} <span style="font-weight: normal; font-size: 12px; margin-left: 10px;">({length} ký tự)</span></div>
                    {c.replace(chr(10), "<br>")}
                    </div>''', 
                    unsafe_allow_html=True
                )

        # Khung 1: Fixed-Size
        with col_fixed:
            with st.container(border=True):
                st.subheader("📏 Fixed-Size Chunker")
                fixed_size = st.number_input("Chunk Size", min_value=50, max_value=2000, value=300, step=50, key="fixed_size")
                fixed_overlap = st.number_input("Overlap", min_value=0, max_value=500, value=50, step=10, key="fixed_overlap")
                
                if st.button("🚀 Chạy Fixed-Size", key="btn_fixed", use_container_width=True):
                    chunker = FixedSizeChunker(chunk_size=fixed_size, overlap=fixed_overlap)
                    st.session_state.res_fixed = chunker.chunk(file_content)
                    
                if st.session_state.res_fixed is not None:
                    st.divider()
                    render_chunks(st.session_state.res_fixed, "#e6f7ff")

        # Khung 2: Sentence
        with col_sentence:
            with st.container(border=True):
                st.subheader("📝 Sentence Chunker")
                sentence_max = st.number_input("Max Sentences/Chunk", min_value=1, max_value=10, value=3, step=1, key="sent_max")
                
                if st.button("🚀 Chạy Sentence", key="btn_sent", use_container_width=True):
                    chunker = SentenceChunker(max_sentences_per_chunk=sentence_max)
                    st.session_state.res_sent = chunker.chunk(file_content)
                    
                if st.session_state.res_sent is not None:
                    st.divider()
                    render_chunks(st.session_state.res_sent, "#f6ffed")

        # Khung 3: Recursive
        with col_recursive:
            with st.container(border=True):
                st.subheader("🔄 Recursive Chunker")
                rec_size = st.number_input("Chunk Size (Mục tiêu)", min_value=50, max_value=2000, value=300, step=50, key="rec_size")
                st.caption("Dấu phân cách: `\\n\\n`, `\\n`, `. `, ` `")
                
                if st.button("🚀 Chạy Recursive", key="btn_rec", use_container_width=True):
                    chunker = RecursiveChunker(chunk_size=rec_size)
                    st.session_state.res_rec = chunker.chunk(file_content)
                    
                if st.session_state.res_rec is not None:
                    st.divider()
                    render_chunks(st.session_state.res_rec, "#f9f0ff")
