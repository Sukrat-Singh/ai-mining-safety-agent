# 🛠️ AI Mining Safety Accident Analysis Agent (RAG + Local LLM)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Local%20LLM-success)
![RAG](https://img.shields.io/badge/Tech-RAG-orange)
![Embeddings](https://img.shields.io/badge/Embeddings-SentenceTransformers-yellow)
![VectorDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple)
![LLM](https://img.shields.io/badge/LLM-Ollama-lightgrey)
![Hackathon](https://img.shields.io/badge/Built%20For-AI%20Hackathon-red)
![License](https://img.shields.io/badge/License-MIT-green)


A Retrieval-Augmented AI system that extracts, structures, indexes, and analyzes mining accident data from official DGMS mining safety reports. Supports conversational querying — fully offline, no API credits required.

This is a **production-style RAG pipeline**, not a demo chatbot.
Built for an **AI Hackathon** — solving real industrial safety problems in mining using RAG + Local LLMs

---

### 🔧 Additional Module: Streamlit Safety Intelligence UI
**A Streamlit + NLP-based Mining Safety Intelligence System**
**Located in `/secondary_model`**

---

## 📌 Overview

This project:

| Function          | Description                                      |
| ----------------- | ------------------------------------------------ |
| 📄 PDF Ingestion   | Reads DGMS accident reports                      |
| 🧾 Data Extraction | Converts text → structured records               |
| 💽 Storage         | Saves structured data as Parquet                 |
| 🔎 Vector Index    | Embeds accidents & stores in ChromaDB            |
| 🧠 AI Agent        | Answers mining safety questions conversationally |

### Sample Questions

```
Which mines in Rajasthan had fatal accidents in 2015?
What caused the accident at Khetri Copper Complex?
How many miners died due to roof fall incidents?
```

---

## 🧠 Architecture

- PDF ➜ text ➜ structured records (Pandas)
- Parquet storage
- Sentence-Transformers embeddings (local)
- Chroma vector DB
- Local LLM via **Ollama** (Llama-3 or Mistral)
- LangChain Runnable pipeline

> Fully local: **no OpenAI required after setup**

---

## 🧰 Tech Stack

| Layer         | Tech                                     |
| ------------- | ---------------------------------------- |
| PDF Parsing   | PyPDF, Regex                             |
| Storage       | Pandas, Parquet                          |
| Embeddings    | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector DB     | ChromaDB                                 |
| LLM           | Ollama (Llama3 / Mistral)                |
| RAG Framework | LangChain (Runnable API)                 |
| Environment   | Python 3.12, Windows                     |

---

## 📂 Project Structure

```
ai-mining-safety-agent/
├─ data/
│ ├─ raw/
│ ├─ interim/
│ └─ processed/
├─ indexes/ # chroma index
├─ scripts/
│ ├─ 01_ingest.py
│ ├─ 02_extract.py
│ ├─ 03_build_index.py
│ └─ 04_chat_cli.py
└─ src/
├─ ingestion/
├─ extraction/
└─ storage/
```

---

## ⚙️ Setup

### Clone repo

```bash
git clone https://github.com/Sukrat-Singh/ai-mining-safety-agent
cd ai-mining-safety-agent
```

### Create virtual environment

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

---

## 📥 1) Ingest PDF

Place PDF in `data/raw/`  
Then run:

```bash
python -m scripts.01_ingest
```

---

## 🧾 2) Extract Structured Records

```bash
python -m scripts.02_extract
```

---

## 🧠 3) Build Vector Index

```bash
python -m scripts.03_build_index
```

---

## 💬 4) Run Chat Assistant

### Install & start Ollama
(Windows download: https://ollama.com/download/windows)

```bash
ollama pull llama3     # or `mistral`
ollama serve           # keep this running
```

### Launch agent

```bash
python -m scripts.04_chat_cli
```

---

## ✅ Example Output

```
You: Which mines in Rajasthan had fatal accidents?

Assistant:
Fatal accidents were reported in Khetri Copper Complex and Kolihan Mine in Rajasthan.
```

---

## 🚀 Roadmap

- [ ] FastAPI web UI
- [ ] Streamlit reports dashboard
- [ ] Automatic PDF table extraction (LayoutLMv3)
- [ ] Trend analysis & visualization
- [ ] Offline full-stack RAG deployment bundle

---

## 🤝 Contributing

PRs welcome — meaningful improvements > cosmetic changes.

---

## 🧑‍💻 Author

**Sukrat**  
B.Tech CSE @ IIT (ISM) Dhanbad  

---

> **This is not a basic chatbot**  
This is a real-world AI system: PDF → structured data → vector store → local LLM → domain QA.
