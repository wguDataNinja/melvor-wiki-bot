import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

from melvor_wiki_bot.config import OUTPUTS_DIR
from melvor_wiki_bot.wiki.manifest import load_manifest, WikiManifestEntry


logger = logging.getLogger(__name__)


def _safe_get_text(node) -> str:
    if node is None:
        return ""
    return node.get_text(strip=True)


def probe_page(entry: WikiManifestEntry) -> Dict[str, Any]:
    headers = {
        "User-Agent": "melvor-wiki-bot/0.1 (probe script)"
    }

    try:
        resp = requests.get(entry.url, headers=headers, timeout=15)
    except Exception as e:
        logger.error("Request failed for %s: %s", entry.url, e)
        return {
            "page_id": entry.page_id,
            "url": entry.url,
            "http_status": None,
            "error": str(e),
        }

    status = resp.status_code
    html = resp.text

    result: Dict[str, Any] = {
        "page_id": entry.page_id,
        "url": entry.url,
        "http_status": status,
        "has_mw_content_text": False,
        "has_mw_parser_output": False,
        "num_headings": {},
        "has_toc": False,
        "num_tables": 0,
        "num_content_table_wrappers": 0,
        "num_infobox_tables": 0,
        "notes": [],
    }

    if status != 200:
        result["notes"].append("non_200_status")
        return result

    soup = BeautifulSoup(html, "lxml")

    content_div = soup.select_one("div#mw-content-text")
    if content_div is None:
        result["notes"].append("missing_mw_content_text")
        return result
    result["has_mw_content_text"] = True

    parser_output = content_div.select_one(".mw-parser-output")
    if parser_output is None:
        result["notes"].append("missing_mw_parser_output")
        return result
    result["has_mw_parser_output"] = True

    heading_counts: Dict[str, int] = {"h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0}
    for level in ["h2", "h3", "h4", "h5", "h6"]:
        heading_counts[level] = len(parser_output.find_all(level))
    result["num_headings"] = heading_counts

    toc = parser_output.select_one("div#toc.toc")
    result["has_toc"] = toc is not None

    tables = parser_output.find_all("table")
    result["num_tables"] = len(tables)

    content_table_wrappers = parser_output.find_all("div", class_="content-table-wrapper")
    result["num_content_table_wrappers"] = len(content_table_wrappers)

    infobox_tables = parser_output.select("table.wikitable.infobox")
    result["num_infobox_tables"] = len(infobox_tables)

    if all(count == 0 for count in heading_counts.values()):
        result["notes"].append("no_headings")

    paragraphs = parser_output.find_all("p")
    if not paragraphs and tables:
        result["notes"].append("no_paragraphs_but_tables")

    return result


def run_probe(output_path: Path | None = None) -> Path:
    output_dir = OUTPUTS_DIR / "wiki_probe"
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path or (output_dir / "wiki_structure_probe.jsonl")

    manifest = load_manifest()
    logger.info("Loaded %d manifest entries", len(manifest))

    with jsonl_path.open("w", encoding="utf-8") as f:
        for entry in manifest:
            result = probe_page(entry)
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    logger.info("Wrote probe results to %s", jsonl_path)
    return jsonl_path


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    run_probe()


if __name__ == "__main__":
    main()
