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

