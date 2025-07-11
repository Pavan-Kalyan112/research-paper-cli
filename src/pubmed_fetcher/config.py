from pathlib import Path

# 📁 Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔍 PubMed API config
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
PUBMED_DB = "pubmed"
PUBMED_RETMODE = "xml"
DEFAULT_FETCH_LIMIT = 5

# 📂 File and cache paths
CACHE_FILE = BASE_DIR / ".last_results.json"
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

# 📄 Default export settings
DEFAULT_FORMAT = "csv"

# 🧠 LLM config (Ollama)
LLM_ENABLED = True
LLM_MODEL_NAME = "mistral"             # Locally running LLM (via Ollama)
LLM_SUMMARY_MAX_TOKENS = 500          # Tokens to use in abstract summary

# 🤖 RAG setup (all local)
RAG_VECTOR_STORE_PATH = BASE_DIR / "data" / "vector_store"
RAG_VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)

RAG_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RAG_CHUNK_SIZE = 500
RAG_CHUNK_OVERLAP = 50

# 📝 Log path
LOG_FILE = BASE_DIR / "pubmed_fetcher.log"
