from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Sequence

from melvor_wiki_bot.config import OUTPUTS_DIR


def _load_chunks(chunks_path: Path) -> list[dict]:
    chunks: list[dict] = []
    with chunks_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))
    return chunks


def embed_texts(texts: Sequence[str]) -> List[List[float]]:
    """
    Placeholder embedding function.

    TODO:
      - Replace this with a real embedding backend (OpenAI, local model, etc).
      - The function should return one vector (list[float]) per input string.

    For now this returns a fixed small-dim vector based on text length,
    just so the pipeline can be exercised end-to-end.
    """
    vectors: List[List[float]] = []
    for t in texts:
        length = len(t)
        # Tiny fake embedding: [len, len%10, len%7]
        vectors.append([float(length), float(length % 10), float(length % 7)])
    return vectors


def make_embeddings(
    chunks_path: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    """
    Load wiki chunks and write per-chunk embeddings.

    Input:
      - wiki_chunks.jsonl (one JSON object per chunk)
    Output:
      - wiki_embeddings.jsonl (one JSON object per chunk):
        { "chunk_id": "...", "embedding": [..numbers..] }
    """
    chunks_path = chunks_path or (OUTPUTS_DIR / "wiki_chunks" / "wiki_chunks.jsonl")
    out_root = output_dir or (OUTPUTS_DIR / "wiki_chunks")
    out_root.mkdir(parents=True, exist_ok=True)
    embeddings_path = out_root / "wiki_embeddings.jsonl"

    chunks = _load_chunks(chunks_path)
    texts = [c.get("text", "") for c in chunks]
    chunk_ids = [c["chunk_id"] for c in chunks]

    vectors = embed_texts(texts)
    if len(vectors) != len(chunk_ids):
        raise RuntimeError("embed_texts returned mismatched vector count")

    with embeddings_path.open("w", encoding="utf-8") as f:
        for cid, vec in zip(chunk_ids, vectors):
            row = {
                "chunk_id": cid,
                "embedding": vec,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return embeddings_path


def main() -> None:
    path = make_embeddings()
    print(f"Wrote embeddings to {path}")


if __name__ == "__main__":
    main()
