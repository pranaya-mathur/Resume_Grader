import streamlit as st
import os
import pandas as pd
from parser.pdf_parser import extract_text_from_pdf
from parser.docx_parser import extract_text_from_docx
from llm.groq_client import analyze_resume_with_llm
from scoring.scorer import compute_final_score

st.title("AI-Grade Internal HR Resume Intelligence Engine")

uploaded_files = st.file_uploader(
    "Upload Resume PDFs or DOCX",
    type=["pdf", "docx"],
    accept_multiple_files=True,
)

results = []

if uploaded_files:
    os.makedirs("temp", exist_ok=True)

    for file in uploaded_files:
        file_path = os.path.join("temp", file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        if file.name.lower().endswith(".docx"):
            text = extract_text_from_docx(file_path)
        else:
            text = extract_text_from_pdf(file_path)
        llm_output = analyze_resume_with_llm(text)
        score, category = compute_final_score(llm_output, text)

        results.append({
            "Name": file.name,
            "Score": score,
            "Category": category
        })

    df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Shortlist CSV", csv, "shortlist.csv", "text/csv")
