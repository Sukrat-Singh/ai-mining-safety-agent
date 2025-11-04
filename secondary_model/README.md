# ⛏️ AI-Powered DGMS Mining Safety Dashboard

> **A Streamlit + NLP-based Mining Safety Intelligence System built for AI Hackathon 2025 (IIT ISM Dhanbad)**  
> Analyze, visualize, and predict accident patterns from DGMS India mining reports (2015–2022).

---

## 🚀 Overview

The **DGMS Mining Safety AI Dashboard** transforms unstructured accident reports (PDFs) from the **Directorate General of Mines Safety (DGMS), India** into **interactive analytics and AI-driven insights**.

It combines **Natural Language Processing (NLP)**, **data visualization**, and **rule-based intelligence** to identify accident trends, root causes, and risk hotspots — enabling **data-driven safety decisions** for the mining industry.

---

## ✨ Key Features

### 📄 1. Automated PDF-to-Data Extraction
- Upload official DGMS accident reports (PDFs)
- Extracts structured information such as:
  - Accident Code  
  - Mine Name, Type & Owner  
  - State & District  
  - Date, Severity, Fatalities, Injuries  
  - Accident Cause (classified via NLP)

### 📊 2. Real-Time Analytics Dashboard
- Interactive visualizations with **Plotly**
- Trend, severity, and state-wise analysis
- Accident-type breakdown and cause distribution

### 🤖 3. AI-Powered Query Agent
- Ask natural language questions like:
  - “Show me all roof fall accidents in 2021”
  - “Which state had the highest fatalities?”
  - “Give safety recommendations for explosions”
- Returns filtered data + automated insights

### 🚨 4. Automated Alerts & Pattern Detection
- Detects safety anomalies and recurring risks
- Flags high-risk states or causes in real-time
- Displays critical & warning alerts dynamically

### 📈 5. Automated Report Generator
- Generate & download executive or detailed safety reports:
  - Executive Summary
  - State-wise Insights
  - Trend Analysis
- Downloadable CSV report for compliance use

---

## 🧠 Tech Stack

| Layer              | Technology                        |
| ------------------ | --------------------------------- |
| Frontend           | Streamlit                         |
| Visualization      | Plotly, Plotly Express            |
| NLP & Data Parsing | Regex, PDFPlumber                 |
| Data Processing    | Pandas, NumPy                     |
| Language           | Python 3.12                       |
| Data Sources       | DGMS Accident Reports (2015–2022) |

---

## ⚙️ Installation

### 🪶 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/dgms-mining-safety-ai.git
cd dgms-mining-safety-ai
```
---

## 📦 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### Typical dependencies:
```
streamlit
pandas
plotly
pdfplumber
numpy
```

---

## 💾 3. Add Data Files

Place your datasets in the project folder:
```
📂 project-root/
 ┣ 📄 dgms_accidents_2016_2022.csv
 ┣ 📄 VOLUME_II_NON_COAL_2015.pdf
 ┗ 📄 app.py
 ```
 ---

 ## 🧩 Running the App
### Start Streamlit
```python
streamlit run app.py
```
### Access in Browser
```
http://localhost:8501
```
---

## 🧠 How It Works

 - Upload a DGMS accident PDF (e.g., “VOLUME_II_NON_COAL_2015.pdf”)

 - The system uses pdfplumber + regex-based NLP parsing to extract structured accident data.

 - Cleaned data merges with your 2016–2022 dataset.

 - The dashboard auto-updates with:
   - Accident trends
    - Fatality analysis
    -  Root causes
    - State-wise insights
    - Alerts and recommendations

---

## 🧰 Directory Structure
```
📦 mining-safety-ai
 ┣ 📜 app.py                # Main Streamlit dashboard
 ┣ 📜 dgms_pdf_to_csv_pipeline.py  # PDF extraction + cleaning script
 ┣ 📜 dgms_accidents_2016_2022.csv # Historical dataset
 ┣ 📜 requirements.txt
 ┣ 📄 README.md
 ┗ 📂 extracted_data/
     ┗ dgms_accidents_2015_final.csv
```

---

## 📸 Screenshot

---

## 🧩 Sample Features in Action

 - Upload PDF (2015) → Extracts 23 new accidents

 - Dashboard auto-refreshes → Combines data (2015–2022)

 - AI Agent → Answers:
*“Show all methane-related fatal accidents in Jharkhand”*

 - Alerts Tab → Flags spikes in “Ground Control Failures”

 - Reports Tab → Exports CSV summary for DGMS compliance

---

## 🏗️ Future Enhancements

 - Integrate LangChain / OpenAI for true natural language reasoning

 - Deploy on Streamlit Cloud / Hugging Face Spaces

 - Add predictive modeling for accident forecasting

 - Enhance OCR support for scanned DGMS PDFs

---

 ## 👨‍💻 Author

**Sukrat Singh**
🎓 Engineering Student, IIT (ISM) Dhanbad
💡 Passionate about AI, Data Engineering & Safety Tech
📧 [email](24je0702@iitism.ac.in), [linkedin](www.linkedin.com/in/sukratsingh)