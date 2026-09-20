from __future__ import annotations

from pathlib import Path

import streamlit as st

from src import (
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    KnowledgeBaseAgent,
    RecursiveChunker,
    SentenceChunker,
    _mock_embed,
)

DATA_DIR = Path("data/ecommerce")
CORPUS_PATH = DATA_DIR / "corpus.md"

st.set_page_config(page_title="Ecommerce RAG Chat", page_icon="Q", layout="wide")


@st.cache_data(show_spinner=False)
def read_corpus() -> str:
    return CORPUS_PATH.read_text(encoding="utf-8")


@st.cache_resource(show_spinner=False)
def build_agent(strategy: str, chunk_size: int, overlap: int, sentence_limit: int) -> KnowledgeBaseAgent:
    corpus = read_corpus()
    if strategy == "Fixed-size":
        chunks = FixedSizeChunker(chunk_size=chunk_size, overlap=min(overlap, chunk_size - 1)).chunk(corpus)
    elif strategy == "Sentence":
        chunks = SentenceChunker(max_sentences_per_chunk=sentence_limit).chunk(corpus)
    else:
        chunks = RecursiveChunker(chunk_size=chunk_size).chunk(corpus)

    documents = [
        Document(
            id=f"corpus#{index}",
            content=chunk,
            metadata={
                "doc_id": "corpus",
                "source": str(CORPUS_PATH),
                "chunk_strategy": strategy,
            },
        )
        for index, chunk in enumerate(chunks)
    ]
    store = EmbeddingStore(collection_name="ecommerce-corpus", embedding_fn=_mock_embed)
    store.add_documents(documents)
    return KnowledgeBaseAgent(
        store=store,
        llm_fn=lambda prompt: "Dựa trên các nguồn được truy xuất, thông tin phù hợp nằm trong ngữ cảnh. [S1]",
    )


def render_trace(agent: KnowledgeBaseAgent) -> None:
    st.subheader("Retrieval trace")
    if not agent.last_trace:
        st.caption("Chưa có chunk nào được truy xuất.")
        return

    for trace in agent.last_trace:
        with st.expander(
            f"[{trace['citation']}] score {trace['score']:.3f} - {trace['chunk_id']}",
            expanded=False,
        ):
            st.caption(f"Nguồn: {trace['source']} - Intent: {trace['intent']}")
            if trace["metadata_filter"]:
                st.caption(f"Metadata filter: {trace['metadata_filter']}")
            st.code(trace["content"], language="markdown")


st.title("Ecommerce Knowledge Chat")
st.caption("Hỏi đáp có citation và kiểm tra trực tiếp các chunk đã được retrieval.")

with st.sidebar:
    st.header("Index settings")
    strategy = st.selectbox("Chunking strategy", ["Fixed-size", "Sentence", "Recursive"])
    chunk_size = st.slider("Chunk size", 200, 1600, 800, 100)
    overlap = st.slider("Overlap", 0, 300, 80, 20)
    sentence_limit = st.slider("Sentences per chunk", 1, 8, 3)
    top_k = st.slider("Retrieved chunks", 1, 8, 3)
    st.divider()
    st.metric("Corpus", CORPUS_PATH.name)

try:
    agent = build_agent(strategy, chunk_size, overlap, sentence_limit)
except FileNotFoundError:
    st.error(f"Không tìm thấy {CORPUS_PATH}. Chạy: python scripts/merge_ecommerce_corpus.py")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ví dụ: MacBook Air M1 được bảo hành bao lâu?")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    answer = agent.answer(question, top_k=top_k)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

render_trace(agent)
