from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Callable

from .embeddings import _mock_embed
from .chunking import _dot


@dataclass
class IntentDecision:
    intent: str
    confidence: float
    needs_clarification: bool
    clarification_question: str = ""
    metadata_filter: dict[str, str] = field(default_factory=dict)
    source: str = "semantic"


class HybridIntentRouter:
    """Route a question with lightweight semantic signals and an optional LLM."""

    INTENT_PROTOTYPES = {
        "warranty": "bảo hành sửa chữa lỗi nhà sản xuất thời hạn đổi máy MacBook",
        "returns": "đổi trả hoàn tiền điều kiện thời hạn sản phẩm người mua",
        "seller": "người bán đăng bán sản phẩm trách nhiệm bảo hành của người bán",
        "general": "thông tin chung về sản phẩm chính sách hướng dẫn",
    }
    INTENT_KEYWORDS = {
        "warranty": ("bảo hành", "bảo trì", "apple care", "đổi máy", "lỗi phần cứng"),
        "returns": ("đổi trả", "hoàn tiền", "trả hàng", "hoàn lại", "refund"),
        "seller": ("người bán", "seller", "đăng bán", "shop", "nhà bán hàng"),
    }

    def __init__(
        self,
        embedding_fn: Callable[[str], list[float]] | None = None,
        llm_router: Callable[[str], str] | None = None,
        min_confidence: float = 0.34,
    ) -> None:
        self.embedding_fn = embedding_fn or _mock_embed
        self.llm_router = llm_router
        self.min_confidence = min_confidence
        self._prototype_embeddings = {
            intent: self.embedding_fn(text)
            for intent, text in self.INTENT_PROTOTYPES.items()
        }

    def route(self, question: str) -> IntentDecision:
        normalized = self._normalize(question)
        if self._is_ambiguous(normalized):
            return IntentDecision(
                intent="clarification",
                confidence=0.0,
                needs_clarification=True,
                clarification_question=self._clarification_for(normalized),
                source="ambiguity-check",
            )

        scores = self._semantic_scores(normalized)
        best_intent, best_score = max(scores.items(), key=lambda item: item[1])
        second_score = sorted(scores.values(), reverse=True)[1]
        close_scores = best_score - second_score < 0.04

        if self.llm_router and (best_score < self.min_confidence or close_scores):
            llm_intent = self._route_with_llm(question)
            if llm_intent in self.INTENT_PROTOTYPES:
                return self._decision(llm_intent, max(best_score, 0.5), "llm")

        if best_score < self.min_confidence:
            return IntentDecision(
                intent="clarification",
                confidence=best_score,
                needs_clarification=True,
                clarification_question=self._clarification_for(normalized),
                source="semantic",
            )
        return self._decision(best_intent, best_score, "hybrid-semantic")

    def _semantic_scores(self, question: str) -> dict[str, float]:
        query_embedding = self.embedding_fn(question)
        query_words = set(re.findall(r"[\wÀ-ỹ]+", question.lower()))
        scores = {}
        for intent, prototype in self.INTENT_PROTOTYPES.items():
            semantic_score = _dot(query_embedding, self._prototype_embeddings[intent])
            keyword_score = sum(
                0.55 for keyword in self.INTENT_KEYWORDS.get(intent, ())
                if keyword in question
            )
            prototype_overlap = sum(
                0.03 for word in prototype.split() if word in query_words
            )
            scores[intent] = semantic_score + keyword_score + prototype_overlap
        return scores

    def _decision(self, intent: str, confidence: float, source: str) -> IntentDecision:
        metadata_filter = {"audience": "seller"} if intent == "seller" else {}
        return IntentDecision(
            intent=intent,
            confidence=confidence,
            needs_clarification=False,
            metadata_filter=metadata_filter,
            source=source,
        )

    def _route_with_llm(self, question: str) -> str:
        prompt = (
            "Classify the user question into exactly one label: warranty, returns, "
            "seller, general, or clarification. Return JSON only, for example "
            '{"intent":"warranty"}. Do not answer the question.\nQuestion: '
            + question
        )
        try:
            raw = self.llm_router(prompt).strip()
            match = re.search(r"\{.*?\}", raw, re.DOTALL)
            value = json.loads(match.group(0) if match else raw)
            return str(value.get("intent", "")).lower()
        except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
            return ""

    @staticmethod
    def _normalize(question: str) -> str:
        return re.sub(r"\s+", " ", question.strip().lower())

    @staticmethod
    def _is_ambiguous(question: str) -> bool:
        if not question or len(question.split()) < 3:
            return True
        vague_terms = ("này", "đó", "thế nào", "ra sao", "cái này", "this", "that", "it")
        return any(term in question for term in vague_terms) and not any(
            keyword in question
            for keywords in HybridIntentRouter.INTENT_KEYWORDS.values()
            for keyword in keywords
        )

    @staticmethod
    def _clarification_for(question: str) -> str:
        return (
            "Bạn muốn hỏi về nội dung nào: (1) bảo hành MacBook, "
            "(2) đổi trả/hoàn tiền, hay (3) chính sách dành cho người bán? "
            "Vui lòng cho biết sản phẩm và tình huống cụ thể."
        )
