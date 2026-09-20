from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.chunking import RecursiveChunker
from src.embeddings import _mock_embed
from src.models import Document
from src.store import EmbeddingStore

DEFAULT_CORPUS = Path("data/ecommerce/corpus.md")


def load_corpus_documents(corpus_path: Path, chunk_size: int = 800) -> list[Document]:
    """Read one merged corpus file and turn it into searchable chunks."""
    content = corpus_path.read_text(encoding="utf-8")
    chunks = RecursiveChunker(chunk_size=chunk_size).chunk(content)
    corpus_id = corpus_path.stem
    return [
        Document(
            id=f"{corpus_id}#{index}",
            content=chunk,
            metadata={
                "doc_id": corpus_id,
                "source": str(corpus_path),
                "extension": corpus_path.suffix.lower(),
            },
        )
        for index, chunk in enumerate(chunks)
    ]


def build_store(corpus_path: Path) -> EmbeddingStore:
    """Build an in-memory index from the merged corpus file."""
    documents = load_corpus_documents(corpus_path)
    store = EmbeddingStore(collection_name=corpus_path.stem, embedding_fn=_mock_embed)
    store.add_documents(documents)
    return store


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--query", default="Điều kiện bảo hành MacBook là gì?")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    store = build_store(args.corpus)
    print(f"Indexed {store.get_collection_size()} chunks from {args.corpus}")
    for index, result in enumerate(store.search(args.query, top_k=args.top_k), start=1):
        preview = result["content"][:160].replace(chr(10), " ")
        print(f"{index}. score={result['score']:.3f} source={result['metadata']['source']}")
        print(f"   {preview}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
