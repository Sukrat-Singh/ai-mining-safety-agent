import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import json
import pandas as pd
from pathlib import Path
from src.extraction.regex_bootstrap import split_records, parse_block

INPUT_FILE = "data/interim/2015_pages.jsonl"
OUT_FILE = "data/processed/2015.parquet"
SOURCE_FILE = "VOLUME_II_NON_COAL_2015.pdf"

def main():
    # Load clean page text
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        pages = [json.loads(line)["text"] for line in f]

    blob = "\n".join(pages)

    # Split into accident blocks
    blocks = split_records(blob)
    print(f"[INFO] Found {len(blocks)} accident blocks")

    # Parse each block
    records = []
    for b in blocks:
        rec = parse_block(b, SOURCE_FILE)
        records.append(rec.model_dump())

    # Save to parquet
    Path(os.path.dirname(OUT_FILE)).mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_parquet(OUT_FILE, index=False)

    print(f"[OK] Saved structured records → {OUT_FILE}")

if __name__ == "__main__":
    main()
