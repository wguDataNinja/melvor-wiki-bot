from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from melvor_wiki_bot.config import OUTPUTS_DIR
from melvor_wiki_bot.rag.embeddings import embed_texts


@dataclass
class RetrievalResult:
    chunk_id: str
    score: float
    page_id: str
    page_title: str
    heading_text: str | None
    text: str
    url: str


def _load_chunks(chunks_path: Path) -> Dict[str, dict]:
    chunks: Dict[str, dict] = {}
    with chunks_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            chunks[obj["chunk_id"]] = obj
    return chunks


def _load_embeddings(emb_path: Path) -> Dict[str, List[float]]:
    embs: Dict[str, List[float]] = {}
    with emb_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            embs[obj["chunk_id"]] = obj["embedding"]
    return embs


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def search_chunks(
    query: str,
    top_k: int = 5,
    chunks_path: Path | None = None,
    emb_path: Path | None = None,
) -> List[RetrievalResult]:
    chunks_path = chunks_path or (OUTPUTS_DIR / "wiki_chunks" / "wiki_chunks.jsonl")
    emb_path = emb_path or (OUTPUTS_DIR / "wiki_chunks" / "wiki_embeddings.jsonl")

    chunks = _load_chunks(chunks_path)
    embs = _load_embeddings(emb_path)

    # embed query using the same function used for chunks
    [q_vec] = embed_texts([query])

    scored: List[Tuple[str, float]] = []
    for cid, vec in embs.items():
        score = _cosine(q_vec, vec)
        scored.append((cid, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    scored = scored[:top_k]

    results: List[RetrievalResult] = []
    for cid, score in scored:
        chunk = chunks.get(cid)
        if not chunk:
            continue
        results.append(
            RetrievalResult(
                chunk_id=cid,
                score=score,
                page_id=chunk["page_id"],
                page_title=chunk["page_title"],
                heading_text=chunk.get("heading_text"),
                text=chunk["text"],
                url=chunk["url"],
            )
        )
    return results


def main() -> None:
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter query: ").strip()

    results = search_chunks(query, top_k=5)
    print(f"Top {len(results)} results for: {query!r}\n")
    for i, r in enumerate(results, start=1):
        heading = f" — {r.heading_text}" if r.heading_text else ""
        snippet = r.text[:280].replace("\n", " ")
        print(f"{i}. [{r.score:.4f}] {r.page_title}{heading}")
        print(f"   URL: {r.url}")
        print(f"   {snippet}...")
        print()


if __name__ == "__main__":
    main()
