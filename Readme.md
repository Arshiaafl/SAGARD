# Portfolio Metrics Extraction – Proof of Concept

## Overview

This project is a lightweight proof of concept for extracting key financial and operating metrics from portfolio company reporting packages delivered as PDFs.

Portfolio reports vary significantly in structure and terminology, which makes manual comparison across companies and time periods slow and error-prone. This PoC explores how a software-driven approach can reduce manual effort and make portfolio insights available more quickly.

The goal is **not** to build a production system, but to demonstrate:

* How to approach an ambiguous, document-heavy data problem
* Reasonable scoping decisions for a 1–2 hour exercise
* Use of modern tools for working with unstructured documents
* Clear communication of assumptions and next steps

---

## High-Level Approach

The solution is split into two lightweight components:

1. **Backend API (FastAPI)**

   * Ingests PDF reports
   * Extracts raw text from PDFs
   * Uses a large language model (Gemini) to semantically extract metrics
   * Returns structured output

2. **Frontend (Streamlit)**

   * Allows non-technical users to upload a PDF
   * Displays extracted metrics in a table
   * Provides a simple bar chart for quick visual review
   * Enables CSV export for downstream analysis

---

## Metrics in Scope

For the crawl phase, the PoC focuses on a small, high-value set of metrics commonly used in portfolio monitoring:

* Company name
* Reporting period
* Revenue
* Gross margin
* Headcount
* ARR (if applicable)
* EBITDA (if applicable)
* Churn (if applicable)

Not all metrics are expected to appear in every report. Missing metrics are explicitly returned as `null`.

---

## Technical Implementation

### PDF Processing

* PDFs are processed using `pdfplumber`
* Assumption: reports are text-based (OCR for scanned PDFs is out of scope)

### Metric Extraction

* A large language model (Gemini) is used to extract metrics semantically
* The model is guided with a fixed schema and clear rules:

  * Do not infer or guess values
  * Preserve original units and formatting
  * Return missing values as `null`

### Output Organization

* Extracted metrics are normalized into a consistent structure
* Results are displayed in a tabular format suitable for review
* Metrics can be exported as CSV for use in dashboards or internal reports

---

## Running the Project

### Backend (FastAPI)

```bash
pip install fastapi uvicorn pdfplumber google-generativeai python-dotenv
export GOOGLE_API_KEY=your_api_key_here
uvicorn main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

### Frontend (Streamlit)

```bash
pip install streamlit requests pandas matplotlib
streamlit run app.py
```

The UI will be available at:

```
http://localhost:8501
```

---

## Assumptions & Limitations

* PDFs are machine-readable (no OCR)
* Extraction accuracy depends on document clarity and labeling
* No persistence layer is included (in-memory / session-based only)

These tradeoffs were made intentionally to keep the PoC focused and lightweight.

---

## Potential Next Steps

If this approach were extended beyond the crawl phase, logical next steps could include:

* OCR support for scanned PDFs
* Batch processing of large PDF folders
* Improved table extraction
* Metric confidence scoring
* Persistent storage (database)
* Portfolio-level aggregation and comparison dashboards
* Using RAG for more and heavier documents


---

## Summary

This proof of concept demonstrates how unstructured portfolio reporting data can be ingested, normalized, and reviewed using modern document processing and AI-based techniques. While intentionally lightweight, the architecture is designed to evolve naturally into a more robust internal analytics tool.


