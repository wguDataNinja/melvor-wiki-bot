import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from melvor_wiki_bot.config import WIKI_MANIFEST_PATH


@dataclass
class WikiManifestEntry:
    page_id: str
    title: str
    url: str
    category: str | None = None


def load_manifest(path: Path | None = None) -> List[WikiManifestEntry]:
    manifest_path = path or WIKI_MANIFEST_PATH
    with manifest_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    entries: List[WikiManifestEntry] = []
    for item in data:
        entries.append(
            WikiManifestEntry(
                page_id=item["page_id"],
                title=item["title"],
                url=item["url"],
                category=item.get("category"),
            )
        )
    return entries
