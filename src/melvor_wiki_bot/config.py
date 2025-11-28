from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

WIKI_MANIFEST_PATH = DOCS_DIR / "wiki_manifest.json"
WIKI_PAGE_REGISTRY_PATH = DOCS_DIR / "wiki_page_registry.json"