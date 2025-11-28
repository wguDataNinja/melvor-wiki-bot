# Melvor Wiki Scraping and RAG Plan  
**Status-aware, implementation-synced version**

Goal:  
Build a reliable scraping + retrieval pipeline for a curated set of Melvor Wiki pages, so a local LLM can answer Reddit-style questions using wiki content, with sources and quotes.

Current implementation status (today):

- ✔️ Manifest of wiki pages  
- ✔️ Probe scraper (structure analyzer)  
- ✔️ Full content scraper (sections + tables → JSON)  
- ⬜ Chunking + embeddings  
- ⬜ RAG answer pipeline with citations  

Reddit integration comes later.

---

# 1. Wiki Manifest

A curated list of the wiki pages we scrape.

File: `docs/wiki_manifest.json`

Structure:

```json
[
  {
    "page_id": "atlas_of_discovery_faq",
    "title": "Atlas of Discovery FAQ",
    "url": "https://wiki.melvoridle.com/index.php?title=Atlas_of_Discovery_FAQ&oldid=86187",
    "category": "expansion_faq"
  },
  {
    "page_id": "beginners_guide",
    "title": "Beginners Guide",
    "url": "https://wiki.melvoridle.com/index.php?title=Beginners_Guide&oldid=86859",
    "category": "general_guide"
  }
]
```

Notes:
- `page_id` is the stable internal key used throughout the pipeline.
- `url` typically includes an `oldid` revision lock for reproducibility.
- `category` is optional metadata for filtering or analytics.

A matching page registry (`docs/wiki_page_registry.json`) adds titles and descriptions for RAG citations.

---

# 2. Probe Scraper (structure analyzer)

Purpose:
- Fetch each wiki page once.
- Inspect only HTML structure.
- Validate MediaWiki patterns.
- Identify pages that need special handling.

Output:  
`outputs/wiki_probe/wiki_structure_probe.jsonl`  
(one JSON object per page)

Collected fields:
- `http_status`
- `has_mw_content_text`
- `has_mw_parser_output`
- heading counts (h2–h6)
- TOC presence
- table counts
- infobox counts
- `notes` array for anomalies (none found in current run)

Usage:
- Run once after modifying the manifest.
- Ensures the main scraper will behave consistently.

---

# 3. Full Content Scraper

Input:  
`docs/wiki_manifest.json`

Output (current implementation):  
- `outputs/wiki_structured/<page_id>.json`

*(Raw HTML caching can be added later, but is not currently implemented.)*

## 3.1. DOM Anchor

All content extraction is rooted at:

```
#mw-content-text > .mw-parser-output
```

If missing:
- Log an error  
- Skip page for now

## 3.2. Page Metadata

Extract:
- `page_title` from `#firstHeading .mw-page-title-main`
- canonical `url` from the printfooter link (fallback to manifest URL)
- `last_updated_version`  
  *(planned field — not yet parsed or populated)*

## 3.3. Sections

Sections are derived from the heading hierarchy.

Algorithm:
1. Iterate through children of `.mw-parser-output`.
2. **Lead section** = all nodes before first `h2–h6`, excluding TOC.  
   - Messageboxes may still appear here (cleanup optional).
3. **Heading sections**:
   - For each heading (h2–h6), gather all subsequent nodes until:
     - another heading of the same or higher level, or
     - end of document.
   - Extract:
     - `heading_level`
     - `heading_text`
     - `heading_id`
     - raw HTML
     - `plain_text` (HTML-stripped)

Result:
A linear sequence of structured sections.

## 3.4. Tables

Scraper extracts **all tables** under `.mw-parser-output` and classifies them:

- `"metadata"` — infobox-style tables  
- `"nav_template"` — tables inside `div.content-table-wrapper`  
- `"table"` — normal content tables  

Each table is optionally linked to the nearest preceding heading.

## 3.5. Structured JSON Format

Example:

```json
{
  "page_id": "combat",
  "page_title": "Combat",
  "url": "...",
  "meta": {
    "last_updated_version": null
  },
  "sections": [...],
  "tables": [...]
}
```

This structured JSON feeds the chunking and retrieval stages.

---

# 4. Chunking and Embeddings

**Not implemented yet.**

Plan:

Input:  
`outputs/wiki_structured/*.json`

Output:
- `outputs/wiki_chunks/wiki_chunks.jsonl`
- `outputs/wiki_chunks/wiki_embeddings.*` (FAISS or similar index)

## 4.1. Chunk Schema

Each chunk will contain:

```
chunk_id
page_id
page_title
url
heading_level / heading_text / heading_id
text (plain text)
metadata (section index, category, etc.)
```

Long sections can be split by:
- paragraphs  
- token length  
- semantic boundaries (optional)

## 4.2. Embeddings

- Use local embedding model (small, deterministic, fast)
- Store vectors in FAISS or another local index
- Maintain mapping: `chunk_id → metadata + text`

---

# 5. RAG Answer Pipeline with Citations

**Not implemented yet.**

Goal:
- Given a Reddit-style question, retrieve the best wiki chunks
- Feed them to an LLM
- Produce answer + citations

Steps:

## 5.1. Retrieval

1. Embed the query using the same embedding model.
2. Retrieve top-K chunks.
3. Optionally re-rank based on category (combat, guide, expansion, etc.).

## 5.2. Answer Prompt

Prompt contains:
- Original question
- Retrieved chunk text + metadata
- Instruction to answer using *only* the provided passages
- Instruction to cite:
  - page name  
  - or `[chunk_id]`  
  - or bracketed wiki titles (`[Beginners Guide]`)

## 5.3. Source List

At the end, list the pages referenced.

Use `docs/wiki_page_registry.json`:

```
title
url
super-short description
```

Examples:
- Beginners Guide — general intro  
- Combat Guide — core combat progression  
- AOD FAQ — expansion mechanics

---

# 6. Summary (Plans + Implementation)

1. **Manifest** — done  
2. **Probe** — done  
3. **Full scraper** — done  
4. **Chunking + embeddings** — next  
5. **RAG pipeline** — after chunking  

