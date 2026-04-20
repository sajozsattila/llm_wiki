# IMPORTANT: separate imports
from mlx_lm import load as mlx_lm_load, stream_generate, sample_utils
from mlx_vlm import load as mlx_vlm_load, generate as vlm_generate
from mlx_vlm.prompt_utils import apply_chat_template as vlm_apply_chat_template
from mlx_vlm.utils import load_config as vlm_load_config

import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

# =========================
# MODEL TYPE DETECTION
# =========================
def is_vlm_model(model_name: str) -> bool:
    return "gemma" in model_name.lower()


# =========================
# MODEL CACHE
# =========================
def load_model_cached(model_name):
    if is_vlm_model(model_name):
        model, processor = mlx_vlm_load(model_name)
        config = vlm_load_config(model_name)
        return {
            "type": "vlm",
            "model": model,
            "processor": processor,
            "config": config,
        }
    else:
        model, tokenizer = mlx_lm_load(model_name)
        return {
            "type": "lm",
            "model": model,
            "tokenizer": tokenizer,
        }


import os
import re
from pathlib import Path
from typing import TypedDict

WIKI_PATH = os.environ.get("WIKI_PATH", "./wiki")
MIN_CONTEXT_LENGTH = int(os.environ.get("MIN_CONTEXT_LENGTH", "2"))
MAX_HOPS = int(os.environ.get("MAX_HOPS", "5"))


class WikiState(TypedDict):
    query: str
    search_intent: dict
    visited_pages: list[str]
    collected_context: list[dict]
    sources: list[str]
    answer: str
    should_continue: bool
    max_hops: int


def get_wiki_path() -> Path:
    return Path(WIKI_PATH)


def list_wiki_pages() -> list[str]:
    wiki_dir = get_wiki_path()
    if not wiki_dir.exists():
        return []
    return [f.stem for f in wiki_dir.glob("*.md")]


def read_wiki_page(page_name: str) -> str:
    wiki_dir = get_wiki_path()
    page_path = wiki_dir / f"{page_name}.md"
    if not page_path.exists():
        page_path = wiki_dir / f"{page_name}.md"
        for f in wiki_dir.glob("*.md"):
            if f.stem.lower() == page_name.lower():
                page_path = f
                break
    if not page_path.exists():
        raise FileNotFoundError(f"Wiki page '{page_name}' not found")
    return page_path.read_text(encoding="utf-8")


def extract_wiki_links(content: str) -> list[str]:
    link_pattern = r"\[\[([^\]]+)\]\]"
    links = re.findall(link_pattern, content)
    return list(set(links))


def extract_title(content: str) -> str:
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def extract_summary(content: str) -> str:
    match = re.search(r"\*\*Summary\*\*:\s*(.+?)(?:\n|$)", content)
    if match:
        return match.group(1).strip()
    return ""


def find_starting_pages(keywords: list[str]) -> list[str]:
    pages = list_wiki_pages()
    if not keywords:
        return pages[:1]
    matches = []
    keywords_lower = [k.lower() for k in keywords]
    for page in pages:
        page_lower = page.lower()
        if any(kw in page_lower for kw in keywords_lower):
            matches.append(page)
    return matches if matches else pages[:1]


def extract_relevant_passages(content: str, query: str) -> list[str]:
    lines = content.split("\n")
    relevant = []
    query_lower = query.lower()
    query_words = set(query_lower.split())
    for line in lines:
        line_lower = line.lower()
        if any(word in line_lower for word in query_words):
            cleaned = line.strip()
            if cleaned and not cleaned.startswith("#"):
                relevant.append(cleaned)
    return relevant[:10]