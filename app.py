import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import json
import re

# -----------------------------
# Configuration
# -----------------------------
API_URL = "http://localhost:8000/extract-metrics"


st.set_page_config(
    page_title="Portfolio Metrics Explorer",
    layout="centered"
)

# -----------------------------
# Helpers
# -----------------------------

def extract_json_from_llm(text: str) -> dict:
    """
    Extract first JSON object from LLM output.
    Handles markdown fences and extra text.
    """
    text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM output")

    return json.loads(match.group(0))


def clean_numeric(value: str):
    """
    Very lightweight numeric cleaning for charts.
    """
    if not value:
        return None

    cleaned = (
        value.replace("$", "")
             .replace("M", "")
             .replace("%", "")
             .replace(",", "")
             .strip()
    )

    try:
        return float(cleaned)
    except ValueError:
        return None


# -----------------------------
# UI
# -----------------------------

st.title("📊 Portfolio Metrics Extraction")
st.write(
    "Upload a portfolio company PDF to extract and review key financial "
    "and operating metrics."
)

uploaded_file = st.file_uploader(
    "Upload PDF report",
    type=["pdf"]
)

# -----------------------------
# Main flow
# -----------------------------

if uploaded_file:
    with st.spinner("Extracting metrics from PDF..."):
        response = requests.post(
            API_URL,
            files={"file": uploaded_file}
        )

    if response.status_code != 200:
        st.error("API request failed")
        st.text(response.text)
        st.stop()

    data = response.json()

    if "metrics" not in data:
        st.error("Unexpected API response")
        st.json(data)
        st.stop()

    raw_metrics = data["metrics"]

    try:
        metrics = extract_json_from_llm(raw_metrics)
    except Exception as e:
        st.error("Failed to parse metrics from AI output")
        st.write("Error:", str(e))
        st.subheader("Raw AI Output")
        st.text(raw_metrics)
        st.stop()

    # -----------------------------
    # Display table
    # -----------------------------

    st.success("Metrics extracted successfully")

    df = pd.DataFrame([metrics])
    st.subheader("Extracted Metrics")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)

    st.download_button(
        label="⬇️ Download metrics as CSV",
        data=csv,
        file_name="extracted_metrics.csv",
        mime="text/csv"
    )

    # -----------------------------
    # Bar chart
    # -----------------------------

    chart_fields = ["revenue", "headcount", "gross_margin"]
    chart_data = {}

    for field in chart_fields:
        numeric_value = clean_numeric(metrics.get(field))
        if numeric_value is not None:
            chart_data[field.replace("_", " ").title()] = numeric_value

    if chart_data:
        st.subheader("Key Metrics Overview")

        fig, ax = plt.subplots()
        ax.bar(chart_data.keys(), chart_data.values())
        ax.set_ylabel("Value")
        ax.set_title("Extracted Metrics")

        st.pyplot(fig)
    else:
        st.info("No numeric metrics available for visualization.")
