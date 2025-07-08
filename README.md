# 🧪 Research Paper Fetcher CLI

A powerful command-line tool to **search**, **summarize**, and **save** research papers from **PubMed** using its full query syntax. Powered by **local LLMs like Ollama** for summarization.

---

## 🔍 Features

- ✅ Search PubMed papers using flexible queries
- 📄 Outputs title, authors, abstract, and optional LLM-generated summary
- 💾 Save output in CSV / PDF / Markdown format
- 🤖 local LLM support (e.g., `llama3` via Ollama)
- 📥 Download raw paper data as JSON
- 🛠️ Built with `Poetry`, `requests`, and `rich`

---

## 🧠 LLM Integration

This tool can optionally summarize abstracts using **Ollama** running locally (e.g., `llama3`). You can toggle this using:

## 📌 CLI Usage Commands

### ➤ Search PubMed papers:
```bash
poetry run pubmed-cli "covid vaccine"

```
--llm
## ➤ Enable LLM summarization (requires Ollama):

```bash
poetry run pubmed-cli "covid vaccine" --llm
```

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
