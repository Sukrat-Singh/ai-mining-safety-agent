"""
DGMS 2015 Accident Report → Structured Dataset
----------------------------------------------
Extracts and cleans accident data from 'VOLUME_II_NON_COAL_2015.pdf'
and generates a CSV (dgms_accidents_2015_final.csv)
compatible with your Streamlit Mining Safety Dashboard.

Author: Sukrat | IIT Dhanbad | AI Hackathon 2025
"""

import pdfplumber
import re
import pandas as pd
from datetime import datetime


# ======================================================
# 1️⃣  EXTRACT TEXT FROM PDF
# ======================================================
def extract_text(pdf_path):
    """Extract text from all pages"""
    print("🔍 Extracting text from PDF...")
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                text += txt + "\n"
    print("✅ Text extracted successfully.")
    return text


# ======================================================
# 2️⃣  PARSE ACCIDENT BLOCKS
# ======================================================
def parse_accidents(text):
    """Parse individual accident entries using regex"""
    print("🧩 Parsing accident records...")
    # Split using "Code" keyword (each record starts with it)
    entries = re.split(r'\bCode\s*[:\-]', text)
    data = []

    for entry in entries[1:]:
        # Accident code (e.g., 0111 Fall of Roof)
        code = re.search(r'([0-9]{3,4}\s*[-–]?\s*[A-Za-z].*?)(?:\n|$)', entry)
        code = code.group(1).strip().replace("\n", " ") if code else None

        # Date
        date_match = re.search(r'Date\s*[:\-]\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})', entry)
        date_str = date_match.group(1) if date_match else None
        date_obj = None
        if date_str:
            for fmt in ("%d.%m.%y", "%d-%m-%y", "%d/%m/%y", "%d.%m.%Y", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue

        # Fields
        mine = re.search(r'Mine\s*[:\-]\s*(.*)', entry)
        owner = re.search(r'Owner\s*[:\-]\s*(.*)', entry)
        district = re.search(r'District\s*[:\-]\s*(.*)', entry)
        state = re.search(r'State\s*[:\-]\s*(.*)', entry)
        description = re.search(r'Description\s*[:\-]\s*(.*)', entry)
        persons = re.search(r'Persons\s*Killed\s*[:\-]\s*(.*)', entry)

        # Fatalities / Injuries
        fatalities = len(re.findall(r'\b(killed|died)\b', entry, re.IGNORECASE))
        injuries = len(re.findall(r'\b(injured)\b', entry, re.IGNORECASE))

        severity = "Minor"
        if fatalities > 0:
            severity = "Fatal"
        elif injuries > 0:
            severity = "Serious"

        # Skip completely empty entries
        if not (date_obj or mine or code):
            continue

        data.append({
            "accident_code": code,
            "date": date_obj.strftime("%Y-%m-%d") if date_obj else None,
            "year": date_obj.year if date_obj else 2015,
            "state": state.group(1).strip() if state else None,
            "district": district.group(1).strip() if district else None,
            "mine_name": mine.group(1).strip() if mine else None,
            "mine_type": "Underground" if "Underground" in entry else "Opencast" if "Opencast" in entry else "Unknown",
            "owner": owner.group(1).strip() if owner else None,
            "severity": severity,
            "fatalities": fatalities,
            "injuries": injuries,
            "persons_killed": persons.group(1).strip() if persons else None,
            "description": description.group(1).strip() if description else None,
        })

    print(f"✅ Parsed {len(data)} accident entries.")
    return pd.DataFrame(data)


# ======================================================
# 3️⃣  CLEAN AND STRUCTURE DATA
# ======================================================
def clean_and_enrich(df):
    """Standardize, split accident codes, and categorize causes"""
    print("🧼 Cleaning and enriching data...")

    # Split accident_code → number + type
    df[["code_number", "accident_type"]] = df["accident_code"].str.extract(r"(\d+)\s*(.*)")
    df["code_number"] = df["code_number"].astype(str).str.zfill(4)

    # Categorize cause based on accident_type
    def categorize_cause(acc_type):
        if pd.isna(acc_type):
            return "Other"
        acc_type = acc_type.lower()
        if "roof" in acc_type or "side" in acc_type:
            return "Ground Control Failure"
        elif any(word in acc_type for word in ["wagon", "truck", "conveyor", "tanker", "movement", "transport"]):
            return "Transportation Accident"
        elif "electric" in acc_type or "power" in acc_type:
            return "Electrical Hazard"
        elif "explosion" in acc_type or "fire" in acc_type or "blowout" in acc_type:
            return "Explosion / Fire"
        elif "fall of person" in acc_type or "height" in acc_type:
            return "Fall from Height"
        elif "drowning" in acc_type or "water" in acc_type:
            return "Drowning / Flooding"
        elif "machine" in acc_type or "mechanical" in acc_type:
            return "Machinery Failure"
        else:
            return "Other"

    df["cause"] = df["accident_type"].apply(categorize_cause)

    # Clean text
    cols = ["state", "district", "mine_name", "owner", "accident_type", "cause"]
    for c in cols:
        df[c] = df[c].astype(str).str.strip().str.title().replace("Nan", "")

    # Fix unknown mine types
    df["mine_type"] = df["mine_type"].replace("Unknown", "Underground")
    df["accident_id"] = range(1, len(df) + 1)

    # Keep only relevant columns in Streamlit order
    df = df[
        [
            "accident_id",
            "accident_code",
            "code_number",
            "date",
            "year",
            "state",
            "district",
            "mine_name",
            "mine_type",
            "owner",
            "accident_type",
            "cause",
            "severity",
            "fatalities",
            "injuries",
            "persons_killed",
            "description",
        ]
    ]
    print("✅ Data cleaned and ready.")
    return df


# ======================================================
# 4️⃣  SAVE TO CSV
# ======================================================
def save_to_csv(df, output_path="dgms_accidents_2015_final.csv"):
    df.to_csv(output_path, index=False)
    print(f"💾 Saved structured dataset → {output_path}")


# ======================================================
# 5️⃣  MAIN PIPELINE
# ======================================================
def main():
    pdf_path = "data/VOLUME_II_NON_COAL_2015.pdf"
    text = extract_text(pdf_path)
    df = parse_accidents(text)
    df = clean_and_enrich(df)
    save_to_csv(df)
    print("\n🎉 DGMS 2015 extraction pipeline complete! CSV ready for Streamlit dashboard.")


if __name__ == "__main__":
    main()
