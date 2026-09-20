import re
from typing import Any, Callable

from .router import HybridIntentRouter
from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(
        self,
        store: EmbeddingStore,
        llm_fn: Callable[[str], str],
        router: HybridIntentRouter | None = None,
        llm_router: Callable[[str], str] | None = None,
    ) -> None:
        self.store = store
        self.llm_fn = llm_fn
        self.router = router or HybridIntentRouter(
            embedding_fn=store._embedding_fn,
            llm_router=llm_router,
        )
        self.last_trace: list[dict[str, Any]] = []  # Initialize last_trace

    def retrieve(self, question: str, top_k: int = 3) -> list[dict[str, Any]]:
        decision = self.router.route(question)
        if decision.needs_clarification:
            self.last_trace = []
            return []

        records = self.store.search_with_filter(
            question,
            top_k=top_k,
            metadata_filter=decision.metadata_filter,
        )
        self.last_trace = []
        for index, record in enumerate(records, start=1):
            metadata = record.get("metadata", {})
            source = metadata.get("source_url") or metadata.get("source") or metadata.get("doc_id", "unknown")
            self.last_trace.append({
                "citation": f"S{index}",
                "chunk_id": record.get("id", "unknown"),
                "score": record.get("score", 0.0),
                "source": source,
                "content": record["content"],
                "intent": decision.intent,
                "metadata_filter": decision.metadata_filter,
            })
        return records

    def answer(self, question: str, top_k: int = 3) -> str:
        decision = self.router.route(question)
        if decision.needs_clarification:
            self.last_trace = []
            return decision.clarification_question

        records = self.retrieve(question, top_k=top_k)
        if not records:
            return "Không tìm thấy thông tin phù hợp trong kho dữ liệu."

        context_parts = []
        citations = []
        for trace in self.last_trace:  # Iterate through last_trace for citations
            context_parts.append(
                f"[{trace['citation']}] Nguồn: {trace['source']} | chunk: {trace['chunk_id']}\n"
                f"{trace['content']}"
            )
            citations.append(f"[{trace['citation']}] {trace['source']} (chunk: {trace['chunk_id']})")

        prompt = (
            "Bạn là trợ lý hỏi đáp dựa trên tài liệu. Chỉ sử dụng thông tin trong "
            "ngữ cảnh được cung cấp; nếu không đủ bằng chứng, hãy nói rõ là không "
            "tìm thấy thông tin. Khi trả lời, bắt buộc trích dẫn nguồn bằng mã "
            "[S1], [S2] tương ứng với context. Không được tự suy đoán khi câu hỏi "
            "còn thiếu thông tin.\n\n"
            f"Intent đã định tuyến: {decision.intent}\n"
            f"Câu hỏi: {question}\n\n"
            "Ngữ cảnh:\n"
            + "\n\n".join(context_parts)
        )
        answer = self.llm_fn(prompt).strip()  # Get the answer from the LLM
        if not re.search(r"\[S\d+\]", answer):
            answer += "\n\nNguồn tham khảo:\n" + "\n".join(citations)
        return answer
