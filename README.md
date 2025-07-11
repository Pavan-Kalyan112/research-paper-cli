# 🧪 PubMed Research Paper Fetcher CLI Tool

A powerful Python CLI tool to search PubMed, summarize abstracts using LLMs, perform semantic search with FAISS, and answer questions using RAG. Designed for researchers and developers to easily interact with scientific literature from the command line.

---

##  Features

 **Fetch Research Papers**  
Use full PubMed query syntax to retrieve research articles.

 **Summarize with LLM**  
Summarize abstracts using local or remote LLMs like Mistral (via Ollama) or OpenAI.

 **Export Options**  
Export results to **CSV**, **PDF**, or **Markdown** formats.

 **Semantic Search with FAISS**  
Embed papers and perform vector-based similarity search using Sentence Transformers and FAISS.

 **Chat with Your Research Data**  
Interactive LLM-based chat over the summarized results.

 **RAG Mode**  
Retrieval-Augmented Generation for answering domain-specific questions over the data.

 **Keyword Filtering**  
Filter papers by keywords in titles or abstracts.

---
Research-Paper-Fetcher-CLI/
│
├── pyproject.toml              # Poetry config file (project metadata, dependencies)
├── README.md                   # Project description for GitHub/TestPyPI
├── LICENSE                     # License file (e.g., MIT)
├── .gitignore                  # Git ignored files
├── poetry.lock                 # Poetry lock file (auto-generated)
│
├── dist/                       # Generated distribution packages
│   ├── pubmed_fetcher-0.1.2.tar.gz
│   └── pubmed_fetcher-0.1.2-py3-none-any.whl
│
├── exports/                    # Generated output files (CSVs, PDFs, JSON)
│   └── Result.csv
│
├── tests/                      # Unit tests for the package
│   ├── test_cli.py
│   ├── test_chat.py
│   ├── test_config.py
│   ├── test_data_pipeline.py
│   ├── test_embedder.py
│   ├── test_filters.py
│   ├── test_llm.py
│   ├── test_pubmed.py
│   ├── test_rag.py
│   ├── test_semantic_search.py
│   ├── test_summary.py
│   └── test_utils.py
│
└── src/                        # Source code root
    └── pubmed_fetcher/         # Main Python package
        ├── __init__.py
        ├── cli.py              # Entry point for the command-line interface using argparse.
        ├── chat.py             # Interactive chat functionality powered by LLMs.
        ├── config.py           # Loads and manages configuration from .env or environment variables.
        ├── data_pipeline.py    # Cleans, parses, and prepares data from PubMed for further processing.
        ├── embedder.py         # Converts abstracts/summaries into embeddings using SentenceTransformer and manages FAISS indexing.
        ├── filters.py          # Handles keyword-based filtering and company-affiliation extraction.
        ├── llm.py              # Interfaces with an LLM (e.g., GPT) to generate paper summaries.
        ├── pubmed.py           # PFetches research papers from the PubMed API.
        ├── rag.py              # Implements a Retrieval-Augmented Generation assistant using indexed data.
        ├── semantic_search.py  # Supports FAISS-based and brute-force semantic search over embeddings.
        ├── summary.py          # Exports results to various formats (CSV, PDF, Markdown).
        └── utils.py            # Helper utilities used across modules.



## 📦 Installation

Install from **TestPyPI**

# Usage
After installation, use the CLI as follows:

### Basic Search and Save
```bash

python -m pubmed_fetcher.cli --query "cancer therapy" -l 10 --format csv -f cancer_results
```
### Summarize Abstracts with LLM
```bash

python -m pubmed_fetcher.cli --query "covid-19 vaccine" -l 5 --llm --format pdf -f covid_summary
```
### Start Semantic Search
```bash

python -m pubmed_fetcher.cli --query "machine learning in genomics" --llm --format csv -f ml_genomics
python -m pubmed_fetcher.cli --chat
```
### Use RAG Mode for Q&A
```bash

python -m pubmed_fetcher.cli --rag --use-file exports/ml_genomics.json
```

# CLI Options
| Argument           | Description                             |
| ------------------ | --------------------------------------- |
| `--query`          | PubMed search term                      |
| `--limit, -l`      | Number of articles to fetch             |
| `--file, -f`       | Output filename (without extension)     |
| `--format`         | Export format: `csv`, `pdf`, or `md`    |
| `--llm`            | Use LLM to summarize abstracts          |
| `--download`       | Save raw JSON from PubMed only          |
| `--filter-keyword` | Filter by keyword in title/abstract     |
| `--chat`           | Chat with summarized research using LLM |
| `--rag`            | Retrieval-Augmented Generation mode     |
| `--use-file`       | Specify a file for `--chat` or `--rag`  |
| `--debug`          | Enable debug logs                       |

# Output Files
* exports/your_file.csv — Fetched articles with metadata.

* exports/your_file.pdf — LLM summaries in PDF.

* exports/summarized_results.json — Input for chat/RAG.

* exports/faiss_index.bin — FAISS vector index.

* .last_results.json — Cached results.

# LLM Integration
* 🔗 Supports Ollama (e.g., mistral, llama2) locally

* Embeddings powered by **sentence-transformers (default: all-MiniLM-L6-v2)**

# Dependencies
* requests

* sentence-transformers

* faiss-cpu

* PyMuPDF (for PDF export)

* rich

* argparse


* ollama (if using local models)

# Author
Developed by **Pavan Kalyan Neelam**
For contributions or issues, please submit a pull request or open an issue.

