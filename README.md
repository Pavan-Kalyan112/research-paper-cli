# 🧪 Research Paper Fetcher CLI

A powerful command-line tool to **search**, **summarize**, and **save** research papers from **PubMed** using its full query syntax. Powered by **local LLMs like Ollama** for summarization.
A command-line tool to search, fetch, and export research papers from PubMed, with optional LLM summarization using Ollama.

---

## 📁 Project Structure
research-paper-fetcher-cli/
│
├── src/pubmed_featcher # Core modules
│           ├── init.py
│           ├── fetch.py # Fetches papers from PubMed
│           ├── data_pipeline.py # Parses PubMed results
│           ├── summarize.py # Sends abstracts to LLM (Ollama)
│           ├── embedding.py # Generates embeddings using sentence-transformers
            └── cli.py # Utility functions
            ├── filters.py # RAG: FAISS-based retrieval
│           ├── retriever.py # RAG: FAISS-based retrieval
│           └── utils.py # Utility functions           
│
├
├── requirements.txt # Required Python packages
├── pyproject.toml # Poetry project configuration
├── potery.lock 
├── README.md # Project documentation
└── test/ # Unit tests
    └── test_cli.py
    └── test_embedder.py
    └── test_llm.py
    └── test_filters.py
    └── test_utils.py # Utility functions
    └── test_pubmed.py
    └── test_data_pipeline.py
    └── test_summary.py


## 🔍 Features
✅ Search PubMed papers using flexible query strings

🤖 Summarize abstracts using local LLMs like llama3 via Ollama

📄 Export papers in CSV, PDF, or Markdown

📥 Download raw JSON for future use

💡 Intelligent metadata extraction:

* PubmedID, 
* Title, 
* Publication Date,
* Non-academicAuthor(s),
* CompanyAffiliation(s),
* Corresponding Author Email

---

## 🛠️ How the Code is Organized

| Module            | Role                                                                 |
|-------------------|----------------------------------------------------------------------|
| `cli.py`          | Parses user input and triggers the main pipeline                     |
| `fetcher/fetch.py`| Makes HTTP requests to PubMed and fetches paper metadata             |
| `fetcher/parser.py`| Parses titles, authors, abstracts from raw API results              |
| `fetcher/summarize.py` | Sends content to Ollama for summarization                       |
| `fetcher/embedding.py` | Generates embeddings using `sentence-transformers`               |
| `fetcher/retriever.py` | Uses FAISS to retrieve top-k similar abstracts (RAG)             |
| `fetcher/utils.py`     | Common utility functions (file saving, formatting)               |

---

## 🧠 LLM Integration

This tool can optionally summarize abstracts using **Ollama** running locally (e.g., `mistral`). You can toggle this using:
🔍 RAG (Retrieval-Augmented Generation)

🧠 Embeddings

🧰 Tools/Libraries used

🧠 LLM via Ollama

# Enhanced Flowchart Explanation: LLM + RAG + Embeddings in CLI Tool
┌────────────────────────┐
│      User Input        │
│ --query, --summarize   │
│ --rag, --embedding     │
└─────────┬──────────────┘
          │
          ▼
┌─────────────────────────────┐
│ Parse CLI Arguments         │
│ (argparse)                  │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│ Fetch Papers from PubMed API                │
│ (requests + PubMed E-Utils query)           │
└─────────┬────────────────────────────────────┘
          │
          ▼
┌───────────────────────────────┐
│ Extract Title + Abstract      │
│ from Each Paper               │
└─────────┬─────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│ (Optional) Convert Abstracts to Embeddings  │
│ → Using SentenceTransformers (e.g., all-MiniLM) │
│ → For later RAG-based summarization         │
└─────────┬────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│ (Optional) Retrieval Step (RAG)             │
│ → Use FAISS to retrieve similar papers      │
│ → Based on embedding similarity (cosine)    │
└─────────┬────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│ Summarize Abstract or Retrieved Context     │
│ → Send to Ollama (local LLM)                │
│    via HTTP POST                            │
└─────────┬────────────────────────────────────┘
          ▼
┌─────────────────────────────────────────────┐
│ Receive Response (Summary) from LLM         │
│ Add it to Final Output Structure            │
└─────────┬────────────────────────────────────┘
          ▼
┌─────────────────────────────────────────────┐
│ Save Output:                                │
│ → CSV / Markdown / JSON                     │
│ → Include title, abstract, summary, etc.    │
└─────────────────────────────────────────────┘

## ⚙️ Installation & Setup

### 1 Clone the repository

git clone https://github.com/Pavan-Kalyan112/Research-Paper-Fetcher-CLI.git
cd Research-Paper-Fetcher-CLI

### 2 Install dependencies using Poetry
```bash
poetry install
```

## 🚀 Usage

### Run the tool from the CLI using Poetry:

Search for papers on a given topic:

## 📌 CLI Usage Commands

### ➤ Search PubMed papers:
```bash
poetry run pubmed-cli "covid vaccine"

```
--llm
## ➤ 🤖Enable LLM summarization (requires Ollama):

```bash
poetry run pubmed-cli "covid vaccine" --llm
```

##  💾 Export Results

Export search results in various formats:

## ➤ Save output to CSV:
```bash
poetry run pubmed-cli "covid vaccine" --file papers.csv --format csv
```
## ➤ Save as PDF:
```bash
poetry run pubmed-cli "covid vaccine" --file output.pdf --format pdf
```

## ➤ Save as Markdown:
```bash
poetry run pubmed-cli "covid vaccine" --file result.md --format md
```

## ➤ Download raw paper data as JSON:
```bash
poetry run pubmed-cli "covid vaccine" --download --file raw_data
```

## ➤ Enable debug logs:
```bash
poetry run pubmed-cli "covid vaccine" --llm --debug
```

## 🐞 Enable Debug Logs

Run with debug logs enabled (useful for troubleshooting):
```bash
poetry run pubmed-cli "covid vaccine" --debug --limit 1
```
#  CSV/Output Columns
| Field                          | Description                                         |
| ------------------------------ | --------------------------------------------------- |
| **PubmedID**                   | Unique identifier for the paper                     |
| **Title**                      | Title of the paper                                  |
| **Publication Date**           | Year of publication                                 |
| **Non-academicAuthor(s)**      | Authors from non-academic institutions              |
| **CompanyAffiliation(s)**      | Authors affiliated with companies                   |
| **Corresponding Author Email** | Author contact email                                |
| **Summary** (optional)         | LLM-generated abstract summary (if `--llm` is used) |


# 💬 GPT-powered Chat Mode (RAG)
#### Ask questions across papers using GPT-based RAG:
```bash
poetry run pubmed-cli --rag
```

## 🧪 Testing

Run all unit tests using:
```bash
poetry run pytest
```

| Tool                                                          | Description               |      |
| ------------------------------------------------------------- | ------------------------- | ---- |
| 🧬 [Entrez API](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | Fetch papers from PubMed  |      |
| 📦 [Poetry](https://python-poetry.org/)                       | Dependency management     |      |
| 🤗 [Ollama](https://ollama.com/)                              | Local LLM serving backend |      |
| 📄 [FPDF](https://pyfpdf.github.io/fpdf2/)                    | PDF generation            |      |
| 🌈 [Rich](https://rich.readthedocs.io/en/stable/)             | Stylish CLI output        |      |
| 🧪 [Pytest](https://docs.pytest.org/en/7.1.x/)                | Unit testing              |      |


# ================ Build & Publish to Test PyPI ================

Step 1: Build the package
```bash
poetry build
```
Step 2: Upload to Test PyPI
```bash
poetry publish --repository testpypi
```
# ================== PubMed Fetcher CLI project locally, from install to execution ==============

### STEP 1: Clone or Move into Your Project Directory
```bash
cd "C:\.\Research-Paper-Fetcher-CLI"
```
### STEP 2: (Optional) Create & Activate Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\activate
```
### STEP 3: Install Required Packages

### # If you're using poetry:

```bash
poetry install

```

#### Or if you're using requirements.txt (manual setup):

```bash

pip install -r requirements.txt
```

#### If not available, install these manually:

```bash

pip install requests rich python-dotenv
```

#### And for development:

```bash

pip install pytest build twine
```
## STEP 4: Run Unit Tests (Optional)
#### Make sure everything works:
```bash
poetry run pytest
# or just
pytest
```

# STEP 5: Build the Package (Only for PyPI or TestPyPI Upload)
```bash
python -m build

It creates .whl and .tar.gz files in the dist/ directory.
```
# STEP 6: Upload to Test PyPI (If needed)
```bash
python -m twine upload --repository testpypi dist/*
```
# STEP 7: Install the Package (from local or TestPyPI)
```bash
If installing locally:


pip install dist/pubmed_fetcher_cli_pavan-0.1.0-py3-none-any.whl
Or from Test PyPI (replace <token> if needed):

```
```bash
pip install --index-url https://test.pypi.org/simple/ pubmed-fetcher-cli-pavan
```
 # STEP 8: Run the CLI Tool
Once installed, you can use:

```bash

pubmed-cli "covid vaccine" --limit 2 --llm
```
If it says 'pubmed-cli' is not recognized, then try:

```bash
python -m pubmed_fetcher.cli "covid vaccine" --limit 2 --llm
```

### 🔧 Optional Flags

| Flag             | Description                                      | Example Usage                                      |
|------------------|--------------------------------------------------|----------------------------------------------------|
| `--llm`          | Use LLM to summarize abstracts                   | `pubmed-cli "covid vaccine" --llm`                 |
| `--format`       | Output format: `csv`, `pdf`, or `md`             | `--format pdf`                                     |
| `--file`         | Output filename (used with `--format`)           | `--file output.pdf`                                |
| `--download`     | Download and save raw JSON data only             | `--download --file raw_data`                       |
| `--debug`        | Enable debug logging and show internal logs      | `--debug`                                          |

> Combine flags as needed.  
> Example:  
> `pubmed-cli "covid vaccine" --limit 5 --llm --format csv --file result.csv --debug`
