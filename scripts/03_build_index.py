# scripts/03_build_index.py

import os
from pathlib import Path

# ensure project package is importable
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pandas as pd
from dotenv import load_dotenv

# Load env vars if present
load_dotenv()

# LangChain imports
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# our code
from src.storage.table import records_to_documents

DATA_FILE = "data/processed/2015.parquet"
INDEX_DIR = "indexes/accidents"

def main():
    print("[INFO] Loading accident records...")
    df = pd.read_parquet(DATA_FILE)

    docs = records_to_documents(df)
    print(f"[INFO] Preparing to embed {len(docs)} records...")

    # ✅ Local embedding model (no API key, no quota issues)
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # Create index directory
    Path(INDEX_DIR).mkdir(parents=True, exist_ok=True)

    print("[INFO] Creating vector index using Chroma...")
    Chroma.from_documents(
        docs,
        embedding=embeddings,
        persist_directory=INDEX_DIR
    )

    print(f"[✅ SUCCESS] Vector index stored in: {INDEX_DIR}")

if __name__ == "__main__":
    main()
