# src/ingestion/sanitizer.py
import re

HEADER = re.compile(r"^\s*STATEMENT NO", re.IGNORECASE)
CODE_LINE = re.compile(r"^Code\s*:", re.IGNORECASE)

def clean_page(text: str):
    lines = []
    for line in text.splitlines():
        if HEADER.match(line.strip()): 
            continue
        if CODE_LINE.match(line.strip()):
            continue
        lines.append(line)

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)  # normalize spaces
    return cleaned.strip()
