from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List

from melvor_wiki_bot.config import OUTPUTS_DIR
from melvor_wiki_bot.wiki.manifest import load_manifest


@dataclass
class WikiChunk:
    chunk_id: str
    page_id: str
    page_title: str
    url: str
    heading_level: int
    heading_id: str | None
    heading_text: str | None
    text: str
    meta: Dict[str, Any]


def _load_manifest_categories() -> Dict[str, str | None]:
    mapping: Dict[str, str | None] = {}
    for entry in load_manifest():
        mapping[entry.page_id] = entry.category
    return mapping


def _load_structured_page(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def make_chunks_for_page(
    page: Dict[str, Any],
    category: str | None = None,
) -> List[WikiChunk]:
    page_id = page["page_id"]
    page_title = page.get("page_title", page_id)
    url = page.get("url", "")
    sections = page.get("sections", [])

    chunks: List[WikiChunk] = []
    for idx, section in enumerate(sections):
        text = (section.get("plain_text") or "").strip()
        if not text:
            continue

        heading_level = int(section.get("heading_level", 0))
        heading_id = section.get("heading_id")
        heading_text = section.get("heading_text")

        chunk_id = f"{page_id}__{idx}"

        meta: Dict[str, Any] = {
            "section_index": idx,
            "category": category,
            "heading_level": heading_level,
        }

        chunks.append(
            WikiChunk(
                chunk_id=chunk_id,
                page_id=page_id,
                page_title=page_title,
                url=url,
                heading_level=heading_level,
                heading_id=heading_id,
                heading_text=heading_text,
                text=text,
                meta=meta,
            )
        )

    return chunks


def make_chunks(
    structured_dir: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    structured_dir = structured_dir or (OUTPUTS_DIR / "wiki_structured")
    output_dir = output_dir or (OUTPUTS_DIR / "wiki_chunks")
    output_dir.mkdir(parents=True, exist_ok=True)

    chunks_path = output_dir / "wiki_chunks.jsonl"

    manifest_categories = _load_manifest_categories()

    all_chunks: List[WikiChunk] = []

    for path in sorted(structured_dir.glob("*.json")):
        page = _load_structured_page(path)
        page_id = page["page_id"]
        category = manifest_categories.get(page_id)
        page_chunks = make_chunks_for_page(page, category=category)
        all_chunks.extend(page_chunks)

    with chunks_path.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")

    return chunks_path


def main() -> None:
    path = make_chunks()
    print(f"Wrote wiki chunks to {path}")


if __name__ == "__main__":
    main()
