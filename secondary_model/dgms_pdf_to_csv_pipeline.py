"""
DGMS Accident Report Parser and Cleaner
---------------------------------------
Converts DGMS-format PDF reports (e.g., VOLUME_II_NON_COAL_2015.pdf)
into a structured CSV (dgms_accidents_clean.csv)
compatible with the Streamlit Mining Safety Dashboard.

Author: Sukrat | IIT Dhanbad | AI Hackathon 2025
"""

import pdfplumber
import re
import pandas as pd
from datetime import datetime


# ======================================================
# 1️⃣ EXTRACT TEXT FROM PDF
# ======================================================
def extract_text_from_pdf(pdf_path):
    print("🔍 Extracting text from PDF...")
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    print("✅ Text extraction complete.")
    return text


# ======================================================
# 2️⃣ PARSE ACCIDENT ENTRIES
# ======================================================
def parse_accidents(text, default_year=2015):
    print("🧩 Parsing accident entries...")

    entries = re.split(r"\bCode\s*[:\-]", text)
    data = []

    for entry in entries[1:]:
        # Accident code (e.g. "0111 Fall of Roof")
        code_match = re.search(r"([0-9]{3,4}\s*[A-Za-z].*?)(?:\n|$)", entry)
        code_text = code_match.group(1).strip().replace("\n", " ") if code_match else None

        # Date extraction
        date_match = re.search(r"Date\s*[:\-]\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", entry)
        date_obj = None
        if date_match:
            date_str = date_match.group(1)
            for fmt in ("%d.%m.%y", "%d-%m-%y", "%d/%m/%y", "%d.%m.%Y", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue

        # Metadata
        mine = re.search(r"Mine\s*[:\-]\s*(.*)", entry)
        owner = re.search(r"Owner\s*[:\-]\s*(.*)", entry)
        district = re.search(r"District\s*[:\-]\s*(.*)", entry)
        state = re.search(r"State\s*[:\-]\s*(.*)", entry)
        persons = re.search(r"Persons\s*Killed\s*[:\-]\s*(.*)", entry)
        desc = re.search(r"Description\s*[:\-]\s*(.*)", entry)

        # Fatalities/injuries
        fatalities = len(re.findall(r"\b(killed|died)\b", entry, re.IGNORECASE))
        injuries = len(re.findall(r"\b(injured)\b", entry, re.IGNORECASE))
        severity = "Fatal" if fatalities > 0 else "Serious" if injuries > 0 else "Minor"

        if not code_text and not mine and not date_obj:
            continue

        data.append({
            "accident_code": code_text,
            "date": date_obj.strftime("%Y-%m-%d") if date_obj else None,
            "year": date_obj.year if date_obj else default_year,
            "state": state.group(1).strip() if state else None,
            "district": district.group(1).strip() if district else None,
            "mine_name": mine.group(1).strip() if mine else None,
            "mine_type": "Opencast" if "Opencast" in entry else "Underground",
            "owner": owner.group(1).strip() if owner else None,
            "severity": severity,
            "fatalities": fatalities,
            "injuries": injuries,
            "persons_killed": persons.group(1).strip() if persons else None,
            "description": desc.group(1).strip() if desc else None,
        })

    print(f"✅ Parsed {len(data)} accidents.")
    return pd.DataFrame(data)


# ======================================================
# 3️⃣ CLEAN AND ENRICH DATA
# ======================================================
def clean_and_enrich_data(df):
    print("🧼 Cleaning and enriching data...")

    # Split accident code → number + type
    df[["code_number", "accident_type"]] = df["accident_code"].str.extract(r"(\d+)\s*(.*)")
    df["code_number"] = df["code_number"].astype(str).str.zfill(4)

    # Intelligent cause mapping
    def map_cause(acc_type):
        if pd.isna(acc_type):
            return "Other"
        acc_type = acc_type.lower()
        if "roof" in acc_type or "side" in acc_type:
            return "Ground Control Failure"
        if any(w in acc_type for w in ["wagon", "truck", "conveyor", "tanker", "transport", "movement", "dumper"]):
            return "Transportation Accident"
        if any(w in acc_type for w in ["electric", "power", "cable"]):
            return "Electrical Hazard"
        if any(w in acc_type for w in ["explosion", "fire", "blowout"]):
            return "Explosion / Fire"
        if "fall of person" in acc_type or "height" in acc_type:
            return "Fall from Height"
        if "drown" in acc_type or "water" in acc_type:
            return "Drowning / Flooding"
        if "machine" in acc_type or "machinery" in acc_type:
            return "Machinery Failure"
        return "Other"

    df["cause"] = df["accident_type"].apply(map_cause)

    # Normalize text
    for col in ["state", "district", "mine_name", "owner", "accident_type", "cause"]:
        df[col] = df[col].astype(str).str.strip().str.title().replace("Nan", "")

    # Clean types
    df["mine_type"] = df["mine_type"].replace("Unknown", "Underground")
    df["accident_id"] = range(1, len(df) + 1)

    # Reorder columns
    ordered_cols = [
        "accident_id", "accident_code", "code_number", "date", "year", "state", "district",
        "mine_name", "mine_type", "owner", "accident_type", "cause",
        "severity", "fatalities", "injuries", "persons_killed", "description"
    ]
    df = df[ordered_cols]
    print("✅ Data cleaned, enriched, and standardized.")
    return df


# ======================================================
# 4️⃣ SAVE TO CSV
# ======================================================
def save_to_csv(df, out_path="dgms_accidents_clean.csv"):
    df.to_csv(out_path, index=False)
    print(f"💾 Saved cleaned dataset → {out_path}")


# ======================================================
# 5️⃣ MAIN PIPELINE
# ======================================================
def main():
    pdf_path = "VOLUME_II_NON_COAL_2015.pdf"  # Change this for other reports
    text = extract_text_from_pdf(pdf_path)
    df_raw = parse_accidents(text, default_year=2015)
    df_clean = clean_and_enrich_data(df_raw)
    save_to_csv(df_clean)
    print("\n🎉 DGMS accident extraction pipeline complete! File ready for Streamlit dashboard.")


if __name__ == "__main__":
    main()
