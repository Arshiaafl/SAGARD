from fastapi import FastAPI, UploadFile, File, HTTPException
import pdfplumber
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv() 

app = FastAPI(title="Portfolio Metrics Extraction API")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def extract_text_from_pdf(file: UploadFile) -> str:
    text = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text[:12000]

def extract_metrics_with_gemini(text: str) -> str:
    prompt = f"""
You are a financial analyst extracting metrics from company performance reports.

Extract the following metrics if present anywhere in the document
(including tables or narrative text).

Metrics:
- Company Name
- Period
- Revenue (Sales, Net Revenue)
- Gross Margin
- ARR
- EBITDA
- Churn
- Headcount

Rules:
- If a metric is missing, return null
- Keep original numeric formatting and units
- Do NOT infer or guess
- Return VALID JSON ONLY
- Use exactly this schema:

{{
  "company": string | null,
  "period": string | null,
  "revenue": string | null,
  "gross_margin": string | null,
  "headcount": string | null,
  "arr": string | null,
  "ebitda": string | null,
  "churn": string | null
}}

Text:
\"\"\"
{text}
\"\"\"
"""
    response = model.generate_content(prompt)
    return response.text

@app.get("/")
def read_root():
    return {
        "service": "Portfolio Metrics Extraction API",
        "status": "running"
    }

@app.post("/extract-metrics")
async def extract_metrics(file: UploadFile = File(...)):
    extracted_text = extract_text_from_pdf(file)
    metrics_json = extract_metrics_with_gemini(extracted_text)

    return {
        "filename": file.filename,
        "metrics": metrics_json
    }