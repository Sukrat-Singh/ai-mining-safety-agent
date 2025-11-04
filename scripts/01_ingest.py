# scripts/01_ingest.py
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import json
from pathlib import Path
from src.ingestion.pdf_reader import read_pdf_text
from src.ingestion.sanitizer import clean_page

PDF_PATH = "data/raw/VOLUME_II_NON_COAL_2015.pdf"
OUT_PATH = "data/interim/2015_pages.jsonl"

def main():
    pages = read_pdf_text(PDF_PATH)
    Path(os.path.dirname(OUT_PATH)).mkdir(parents=True, exist_ok=True)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for p in pages:
            p["text"] = clean_page(p["text"])
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"[OK] Extracted & cleaned pages → {OUT_PATH} | total pages = {len(pages)}")

if __name__ == "__main__":
    main()
