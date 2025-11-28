# melvor-wiki-bot

A local pipeline for scraping the Melvor Idle Wiki, building a retrieval-augmented knowledge base (RAG), and answering gameplay questions using wiki content. Future stages may integrate Reddit fetch/post logic.

## Quick Start

```bash
git clone git@github.com:wguDataNinja/melvor-wiki-bot.git
cd melvor-wiki-bot
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or use pyproject.toml
```

To test that the project structure loads correctly:

```bash
python src/melvor_wiki_bot/cli/demo_answer.py
```

## Repository Structure

```
melvor-wiki-bot/
  README.md
  .gitignore
  pyproject.toml

  docs/
    wiki_manifest.json
    wiki_page_registry.json
    melvor_wiki_rag_plan.md

  src/
    melvor_wiki_bot/
      __init__.py
      config.py

      wiki/
        __init__.py
        manifest.py
        scrape.py
        models.py

      rag/
        __init__.py
        chunking.py
        embeddings.py
        retrieval.py
        answer.py

      cli/
        __init__.py
        demo_answer.py

  scripts/
    wiki_scrape_run.py
    wiki_build_index.py
    wiki_demo_question.py

  tests/
    __init__.py
    test_manifest.py
    test_chunking.py
```

## Goals

- Scrape and canonicalize Melvor Wiki pages.
- Chunk and embed wiki content for similarity search.
- Retrieve relevant wiki passages for user questions.
- Produce structured answers with citations.
- Later: integrate with Reddit for automated replies.
