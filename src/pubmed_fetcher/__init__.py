# src/pubmed_fetcher/__init__.py

from .summary import summarize_abstract
from .pubmed import search_and_fetch
from .utils import save_as_csv, save_as_pdf, save_as_markdown
from .chat import chat_with_llm  # ✅ UPDATED

__all__ = [
    "summarize_abstract",
    "search_and_fetch",
    "save_as_csv",
    "save_as_pdf",
    "save_as_markdown",
    "chat_with_llm"  # ✅ INCLUDED
]

