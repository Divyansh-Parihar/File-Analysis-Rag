# 📄 File Analysis

An AI-powered document analysis tool that summarizes uploaded files and answers questions about their content — entirely locally using **Ollama** (no API keys required).

Built with a **Streamlit** frontend and a **Flask** backend, communicating via REST API.

---

## ✨ Features

- 📑 **Multi-format Support** — Analyze PDF, DOCX, CSV, and Markdown files
- 🤖 **Local LLM** — Powered by [Ollama](https://ollama.com/) (`qwen2.5:0.5b`) — fully offline, no API keys
- 🧠 **RAG (Retrieval-Augmented Generation)** — Ask questions about your document using ChromaDB vector search
- 📊 **Structured Summaries** — Returns a title, a detailed summary, and key topics discussed
- 🔁 **Smart Chunking** — Long documents are split, summarized in chunks, then merged into one final summary
- 📋 **Rotating Logs** — All events logged to `logs/file_analysis.log` with console + file handlers

---

## 🏗️ Architecture

```
┌─────────────────────┐         HTTP (REST)        ┌──────────────────────────┐
│   Streamlit (UI)    │ ─────── POST /summarize ──► │   Flask Backend          │
│     main.py         │                             │     routes.py            │
└─────────────────────┘                             └──────────┬───────────────┘
                                                               │
                                                    ┌──────────▼───────────────┐
                                                    │   Document Classifier    │
                                                    │     extractor.py         │
                                                    │  (PDF/DOCX/CSV/MD)       │
                                                    └──────────┬───────────────┘
                                                               │
                                                    ┌──────────▼───────────────┐
                                                    │   RAG Engine             │
                                                    │     rag.py               │
                                                    │  LangChain + ChromaDB    │
                                                    │  + Ollama (local LLM)    │
                                                    └──────────────────────────┘
```

---

## 📁 Project Structure

```
File_Analysis/
│
├── main.py            # Streamlit UI — file uploader & result display
├── routes.py          # Flask REST API — /summarize endpoint
├── extractor.py       # File parsers for PDF, DOCX, CSV, Markdown
├── rag.py             # LangChain RAG logic — summarization & querying
├── logger.py          # Centralized rotating logger (file + console)
├── requirement.txt    # Python dependencies
├── .streamlit/
│   └── config.toml   # Streamlit server config (max upload size: 1024 MB)
└── logs/              # Auto-generated runtime logs (gitignored)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running locally

### 1. Pull the required Ollama models

```bash
ollama pull qwen2.5:0.5b
ollama pull llama3.2:3b
```

### 2. Clone the repository

```bash
git clone https://github.com/Divyansh-Parihar/File-Analysis-Rag.git
cd File_Analysis
```

### 3. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirement.txt
```

### 5. Run the Flask backend

```bash
python routes.py
```

> Flask will start on `http://localhost:5000`

### 6. Run the Streamlit frontend (in a new terminal)

```bash
streamlit run main.py
```

> Streamlit will open at `http://localhost:8501`

---

## 🧪 Supported File Types

| Format | Extension | Parser Used |
|--------|-----------|-------------|
| PDF | `.pdf` | PyMuPDF |
| Word Document | `.docx` | python-docx |
| CSV / Spreadsheet | `.csv` | pandas |
| Markdown | `.md` | Built-in UTF-8 read |

---

## 🔍 How It Works

1. **Upload** a file via the Streamlit UI
2. The frontend sends it to the Flask backend via `POST /summarize`
3. The backend identifies the file type and routes it to the correct **extractor**
4. The extractor reads the raw text and passes it to the **RAG engine**
5. If the document is small (single chunk), the LLM summarizes it directly
6. If the document is large, it is **split into chunks**, each chunk is summarized, and then all chunk summaries are **merged** into one final structured summary
7. The result — **title**, **summary**, and **key topics** — is returned and displayed in the UI

---

## 📦 Dependencies

| Library | Purpose |
|---------|---------|
| `streamlit` | Web UI |
| `flask` | REST API backend |
| `langchain` | LLM orchestration & prompt templates |
| `langchain-ollama` | Ollama integration for LangChain |
| `langchain-chroma` | ChromaDB vector store integration |
| `chromadb` | Vector database for RAG |
| `pymupdf` | PDF text extraction |
| `python-docx` | DOCX text extraction |
| `pandas` | CSV parsing & statistics |

---

## 📝 Logging

All modules use a centralized logger (`logger.py`) that writes to:

- **Console** — `INFO` level and above
- **File** — `logs/file_analysis.log` — `DEBUG` level and above, with rotating backups (max 5 MB × 3 files)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---