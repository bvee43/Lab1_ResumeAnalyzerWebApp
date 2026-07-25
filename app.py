import streamlit as st
from dotenv import load_dotenv

from parse import read_resume_pdf
from analyzer import (
    extract_resume_profile, extract_jd_profile, analyse_keyword_match,
    analyse_bullets, analyse_jargon, analyse_structure, analyse_background_fit,
    summarise_overall, compute_overall_score,
)

import json
import sys
from datetime import datetime
from pathlib import Path
import os

load_dotenv()
VALID_DEGREES = ["RTIS", "IMGD", "UXGD", "BFA"]

st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste Job Description", height=250)
degree = st.selectbox("Select Degree", VALID_DEGREES)
run = st.button("Analyze Resume")

if run:
    if not resume_file or not jd_text:
        st.error("Please upload resume and paste job description.")
        st.stop()

    load_dotenv()

    try:
        # 1. Parse resume
        resume_text = read_resume_pdf(resume_file)

        # 2. Read JD
        # jd_text already comes from the Streamlit text area,
        # so there's no need to call read_jd_text()

        # 3. Extract resume profile
        st.write("Extracting resume profile...")
        resume_profile = extract_resume_profile(resume_text)

        # 4. Extract JD profile
        st.write("Extracting JD profile...")
        jd_profile = extract_jd_profile(jd_text)

        # 5. Keyword match
        st.write("Analysing keywords...")
        keyword_match = analyse_keyword_match(
            resume_profile,
            jd_profile
        )

        # 6. Bullet audit
        bullets = analyse_bullets(resume_profile)

        # 7. Other analyses
        jargon = analyse_jargon(resume_profile, jd_profile)
        structure = analyse_structure(resume_text)
        background_fit = analyse_background_fit(
            resume_profile,
            jd_profile
        )

        # Build report
        report = {
            "meta": {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
            },
            "resume_profile": resume_profile,
            "jd_profile": jd_profile,
            "keyword_match": keyword_match,
            "bullets": bullets,
            "jargon": jargon,
            "structure": structure,
            "background_fit": background_fit,
        }

        report["overall_score"] = compute_overall_score(report)
        report["passes_ats_threshold"] = report["overall_score"] >= 60

        # 8. Summary
        report["summary"] = summarise_overall(report)

    except RuntimeError as e:
        st.error(str(e))
        st.stop()

    # Display results
    st.metric("Overall Score", f"{report['overall_score']}/100")

    if report["passes_ats_threshold"]:
        st.success("PASS")
    else:
        st.error("FAIL")

    st.markdown(report["summary"])
    st.json(report)