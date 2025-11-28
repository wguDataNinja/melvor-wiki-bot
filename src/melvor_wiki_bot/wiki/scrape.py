from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup, Tag

from melvor_wiki_bot.config import OUTPUTS_DIR
from melvor_wiki_bot.wiki.manifest import WikiManifestEntry, load_manifest
from melvor_wiki_bot.wiki.models import WikiPageStructured, WikiSection, WikiTable


def _fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "melvor-wiki-bot/0.1 (full scraper)"
    }
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.text


def _strip_html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ", strip=True)
    return " ".join(text.split())


def _collect_lead_section(parser_output: Tag) -> Optional[WikiSection]:
    children: List[Tag] = [c for c in parser_output.children if isinstance(c, Tag)]
    lead_nodes: List[Tag] = []

    for child in children:
        if child.name in {"h2", "h3", "h4", "h5", "h6"}:
            break
        if child.name == "div" and child.get("id") == "toc":
            continue
        lead_nodes.append(child)

    if not lead_nodes:
        return None

    html = "".join(str(n) for n in lead_nodes)
    plain_text = _strip_html_to_text(html)

    if not plain_text:
        return None

    return WikiSection(
        heading_level=0,
        heading_id=None,
        heading_text=None,
        html=html,
        plain_text=plain_text,
    )


def _collect_heading_sections(parser_output: Tag) -> List[WikiSection]:
    sections: List[WikiSection] = []
    children: List[Tag] = [c for c in parser_output.children if isinstance(c, Tag)]

    i = 0
    n = len(children)
    while i < n:
        node = children[i]
        if node.name not in {"h2", "h3", "h4", "h5", "h6"}:
            i += 1
            continue

        level = int(node.name[1])
        headline = node.select_one(".mw-headline")
        heading_text = headline.get_text(strip=True) if headline else node.get_text(strip=True)
        heading_id = headline.get("id") if headline and headline.has_attr("id") else node.get("id")

        i += 1
        content_nodes: List[Tag] = []
        while i < n:
            nxt = children[i]
            if nxt.name in {"h2", "h3", "h4", "h5", "h6"}:
                nxt_level = int(nxt.name[1])
                if nxt_level <= level:
                    break
            if nxt.name == "div" and nxt.get("id") == "toc":
                i += 1
                continue
            content_nodes.append(nxt)
            i += 1

        html = "".join(str(n) for n in content_nodes)
        plain_text = _strip_html_to_text(html)

        sections.append(
            WikiSection(
                heading_level=level,
                heading_id=heading_id,
                heading_text=heading_text,
                html=html,
                plain_text=plain_text,
            )
        )

    return sections


def _extract_tables(parser_output: Tag) -> List[WikiTable]:
    tables: List[WikiTable] = []
    for table in parser_output.find_all("table"):
        classes = table.get("class", []) or []
        classes_set = set(classes)

        if "infobox" in classes_set:
            kind = "metadata"
        elif table.find_parent("div", class_="content-table-wrapper") is not None:
            kind = "nav_template"
        else:
            kind = "table"

        heading_tag = table.find_previous(
            ["h2", "h3", "h4", "h5", "h6"],
            attrs={"class": "mw-headline"},
        )
        section_heading_id: Optional[str] = None
        if heading_tag is not None:
            if heading_tag.has_attr("id"):
                section_heading_id = heading_tag.get("id")
            else:
                headline = heading_tag.select_one(".mw-headline")
                if headline is not None and headline.has_attr("id"):
                    section_heading_id = headline.get("id")

        tables.append(
            WikiTable(
                kind=kind,
                section_heading_id=section_heading_id,
                html=str(table),
            )
        )
    return tables


def scrape_wiki_page(entry: WikiManifestEntry) -> WikiPageStructured:
    html = _fetch_html(entry.url)
    soup = BeautifulSoup(html, "lxml")

    page_title_tag = soup.select_one("#firstHeading .mw-page-title-main")
    page_title = page_title_tag.get_text(strip=True) if page_title_tag else entry.title

    canonical_link = soup.select_one("div.printfooter a[href]")
    canonical_url = canonical_link.get("href") if canonical_link and canonical_link.has_attr("href") else entry.url

    content_div = soup.select_one("div#mw-content-text")
    if content_div is None:
        raise RuntimeError(f"Missing #mw-content-text for page_id={entry.page_id}")

    parser_output = content_div.select_one(".mw-parser-output")
    if parser_output is None:
        raise RuntimeError(f"Missing .mw-parser-output for page_id={entry.page_id}")

    lead_section = _collect_lead_section(parser_output)
    heading_sections = _collect_heading_sections(parser_output)

    sections: List[WikiSection] = []
    if lead_section is not None:
        sections.append(lead_section)
    sections.extend(heading_sections)

    tables = _extract_tables(parser_output)

    page = WikiPageStructured(
        page_id=entry.page_id,
        page_title=page_title,
        url=canonical_url,
        last_updated_version=None,
        sections=sections,
        tables=tables,
    )
    return page


def scrape_all_to_files(output_dir: Path | None = None) -> Path:
    out_root = output_dir or (OUTPUTS_DIR / "wiki_structured")
    out_root.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest()
    for entry in manifest:
        page = scrape_wiki_page(entry)
        target = out_root / f"{entry.page_id}.json"
        data = {
            "page_id": page.page_id,
            "page_title": page.page_title,
            "url": page.url,
            "meta": {
                "last_updated_version": page.last_updated_version,
            },
            "sections": [asdict(s) for s in page.sections],
            "tables": [asdict(t) for t in page.tables],
        }
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return out_root


def main() -> None:
    out_dir = scrape_all_to_files()
    print(f"Wrote structured wiki JSON to {out_dir}")


if __name__ == "__main__":
    main()
