from typing import Callable

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

    def answer(self, question: str, top_k: int = 3) -> str:
        decision = self.router.route(question)
        if decision.needs_clarification:
            return decision.clarification_question

        records = self.store.search_with_filter(
            question,
            top_k=top_k,
            metadata_filter=decision.metadata_filter,
        )
        if not records:
            return "Không tìm thấy thông tin phù hợp trong kho dữ liệu."

        context_parts = []
        for index, record in enumerate(records, start=1):
            metadata = record.get("metadata", {})
            source = metadata.get("source") or metadata.get("source_url") or metadata.get("doc_id", "unknown")
            context_parts.append(f"[{index}] Nguồn: {source}\n{record['content']}")

        prompt = (
            "Bạn là trợ lý hỏi đáp dựa trên tài liệu. Chỉ sử dụng thông tin trong "
            "ngữ cảnh được cung cấp; nếu không đủ bằng chứng, hãy nói rõ là không "
            "tìm thấy thông tin. Khi trả lời, trích dẫn số của các đoạn nguồn như "
            "[1]. Không được tự suy đoán khi câu hỏi còn thiếu thông tin.\n\n"
            f"Intent đã định tuyến: {decision.intent}\n"
            f"Câu hỏi: {question}\n\n"
            "Ngữ cảnh:\n"
            + "\n\n".join(context_parts)
        )
        return self.llm_fn(prompt)
