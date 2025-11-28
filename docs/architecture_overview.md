
# Melvor Wiki Bot – Architecture Overview

This document provides a concise but complete technical description of the
project architecture, data flow, and all major modules/scripts.  
It is the primary reference for understanding how the system works end-to-end.

---

# 1. High-Level Purpose

The project builds a local Retrieval-Augmented Generation (RAG) system using
content scraped from the Melvor Idle Wiki.  
The pipeline:

1. Define which wiki pages to use (manifest)
2. Probe structure of each page (optional diagnostics)
3. Scrape full content into structured JSON
4. Chunk into retrieval units
5. Embed chunks
6. Build a retrieval index
7. Answer questions with citations

Everything is local, simple, and testable.

---

# 2. Directory Layout

melvor-wiki-bot/
│
├── docs/
│   ├── architecture_overview.md   ← this file
│   ├── melvor_wiki_rag_plan.md   ← overall plan & phases
│   ├── wiki_manifest.json         ← curated page list
│   └── wiki_page_registry.json    ← titles + short descriptions
│
├── dev/
│   ├── dev-log.md
│   └── github_setup.md
│
├── outputs/                       ← all generated artifacts (gitignored)
│   ├── wiki_probe/
│   ├── wiki_structured/
│   ├── wiki_chunks/
│   └── …
│
├── scripts/
│   ├── wiki_probe_run.py          ← probe phase
│   ├── wiki_scrape_run.py         ← scraping phase
│   ├── wiki_make_chunks.py        ← chunking phase
│   ├── wiki_make_embeddings.py    ← embeddings
│   └── wiki_search_demo.py        ← retrieval demonstration
│
├── src/melvor_wiki_bot/
│   ├── config.py
│   │
│   ├── wiki/
│   │   ├── manifest.py
│   │   ├── models.py
│   │   ├── probe.py
│   │   └── scrape.py
│   │
│   ├── rag/
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── retrieval.py
│   │   └── answer.py
│   │
│   ├── cli/
│   │   └── demo_answer.py
│   │
│   └── init.py
│
└── tests/
└── test_manifest.py

---

# 3. Data Flow Overview

manifest.json → probe → scrape → structured JSON
↓
chunking → wiki_chunks.jsonl
↓
embeddings → wiki_embeddings.jsonl
↓
retrieval index → answer generation

Each phase consumes the previous phase’s output.

---

# 4. The Manifest System

File: `docs/wiki_manifest.json`  
Code: `src/melvor_wiki_bot/wiki/manifest.py`

Purpose:
- Define which wiki pages to scrape
- Stable page IDs
- Canonical URLs with revision locks (`oldid=xxxxxx`)

Example entry:

{
“page_id”: “combat”,
“title”: “Combat”,
“url”: “https://…”,
“category”: “combat_guide”
}

Used by probe, scraper, and chunker.

---

# 5. Probe Layer (Structure Analysis)

Script: `scripts/wiki_probe_run.py`  
Module: `src/melvor_wiki_bot/wiki/probe.py`  
Output: `outputs/wiki_probe/wiki_structure_probe.jsonl`

Purpose:
- Fetch each page
- Inspect DOM structure
- Detect anomalies before scraping

Checks include:
- HTTP status
- presence of `#mw-content-text`
- presence of `.mw-parser-output`
- heading distribution
- table count
- TOC presence

This step is optional but helps catch unexpected structural changes.

---

# 6. Full Scraper (Sections + Tables)

Script: `scripts/wiki_scrape_run.py`  
Module: `src/melvor_wiki_bot/wiki/scrape.py`  
Output: one JSON file per page under:  
`outputs/wiki_structured/<page_id>.json`

Extractor rules:
- Works off `.mw-parser-output`
- Builds hierarchical sections (lead + h2–h6)
- Extracts `html`, `plain_text`
- Extracts all tables under `.mw-parser-output` with simple classification
- Captures: page_title, url, metadata

Structured JSON format:

{
“page_id”: “…”,
“page_title”: “…”,
“url”: “…”,
“sections”: [
{
“heading_level”: 2,
“heading_text”: “Overview”,
“plain_text”: “…”,
“html”: “…”
}
],
“tables”: […]
}

This forms the canonical scraped knowledge.

---

# 7. Chunking Layer

Script: `scripts/wiki_make_chunks.py`  
Module: `src/melvor_wiki_bot/rag/chunking.py`  
Output: `outputs/wiki_chunks/wiki_chunks.jsonl`

Purpose:
- Convert structured pages into retrieval-ready text chunks
- Every chunk corresponds to:
  - the lead section, or
  - an h2–h6 section

Chunk schema:

{
“chunk_id”: “pageid__3”,
“page_id”: “pageid”,
“page_title”: “Title”,
“url”: “…”,
“heading_level”: 2,
“heading_text”: “Overview”,
“text”: “plain text…”,
“meta”: {
“section_index”: 3,
“category”: “from manifest”
}
}

No overlap/merge logic yet.  
Very easy to modify in future (e.g., by word count or embeddings context).

---

# 8. Embedding Layer

Script: `scripts/wiki_make_embeddings.py`  
Module: `src/melvor_wiki_bot/rag/embeddings.py`  
Output:  
`outputs/wiki_chunks/wiki_embeddings.jsonl`

Current implementation:
- Loads chunks
- Computes **dummy embeddings** (short vector `[len, unique_words, avg_word_len]`)
- Writes one JSON line per embedding

This scaffolding makes retrieval work without real embeddings.  
Later: drop in any embedding model.

Example:

{“chunk_id”: “combat__2”, “embedding”: [3821, 212, 4]}

---

# 9. Retrieval Layer

Script: `scripts/wiki_search_demo.py`  
Module: `src/melvor_wiki_bot/rag/retrieval.py`

Current implementation:
- Loads chunks + dummy embeddings
- Uses cosine similarity
- Returns top-k matches with:
  - page title
  - URL
  - snippet of text

Example result:

	1.	[0.9972] Into the Abyss Expansion — Where to Purchase the Expansion

Later: swap in FAISS + real embeddings.

---

# 10. Answer Pipeline (RAG)

Module: `src/melvor_wiki_bot/rag/answer.py`  
(Scaffolded but not implemented yet)

Workflow will be:
1. Retrieve top-k chunks
2. Build structured prompt
3. Run LLM local/inference
4. Add citations using:
   `docs/wiki_page_registry.json`
5. Return answer + sources

Will integrate into `cli/demo_answer.py`.

---

# 11. Script Summary

| Script | Purpose |
|-------|---------|
| `wiki_probe_run.py` | Run structure probe on manifest pages |
| `wiki_scrape_run.py` | Scrape all wiki pages to structured JSON |
| `wiki_make_chunks.py` | Produce retrieval chunks |
| `wiki_make_embeddings.py` | Generate embeddings for chunks |
| `wiki_search_demo.py` | Test retrieval pipeline |
| `demo_answer.py` | Will run RAG answer (future) |

All scripts follow the same pattern:

source .venv/bin/activate
export PYTHONPATH=src
python scripts/.py

---

# 12. Components Ready for Extension

### Replace embeddings  
Drop in OpenAI, ollama, sentence-transformers, etc.

### Replace similarity search  
Swap dummy cosine → FAISS, HNSW, local vector DB.

### Improve chunking  
Switch to token-based chunking or overlap-based.

### Add raw HTML caching  
Scraper currently fetches live pages each run.

### Add Reddit integration  
Optional future module for syncing questions → answers.

---

# 13. Known Constraints

- Dummy embeddings → low accuracy retrieval  
- No caching of raw HTML  
- No HTML sanitization beyond plain text stripping  
- No diffs when wiki page revisions change  
- Chunking tied to wiki heading structure  

All of these can be upgraded without rewriting the pipeline.

---

# 14. Minimal Commands Cheat Sheet

1. Probe all pages

python scripts/wiki_probe_run.py

2. Scrape all structured pages

python scripts/wiki_scrape_run.py

3. Build chunks

python scripts/wiki_make_chunks.py

4. Build embeddings

python scripts/wiki_make_embeddings.py

5. Run retrieval demo

python scripts/wiki_search_demo.py “your query”

---

# 15. Summary

This document describes:
- project structure  
- data flow  
- each subsystem  
- each script  
- scraping → chunks → embeddings → retrieval pipeline  

It serves as the primary technical reference for
internal understanding and future maintenance.


