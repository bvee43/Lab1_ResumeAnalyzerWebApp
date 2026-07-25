"""
analyzer.py — the 8 analysis functions and the pure-Python score calculator.

Task 4 of the lab (Track A).
Study material references:
  §4 The Multi-Stage Pipeline
  §7.2 Weighted Aggregation

Each of the 8 analysis functions calls ask_json() or ask_text() exactly once.
compute_overall_score() makes NO LLM call — it is pure Python arithmetic.

Imports you will need (already written for you):
"""

import json

from llm import ask_json, ask_text
from prompts import (
    RESUME_PROFILE_PROMPT,
    JD_PROFILE_PROMPT,
    KEYWORD_MATCH_PROMPT,
    BULLET_QUALITY_PROMPT,
    JARGON_AUDIT_PROMPT,
    STRUCTURE_AUDIT_PROMPT,
    BACKGROUND_FIT_PROMPT,
    OVERALL_SUMMARY_PROMPT,
    DEGREE_ALIGNMENT_PROMPT,
)


# ---------------------------------------------------------------------------
# Extraction functions (§6.1)
# ---------------------------------------------------------------------------

def extract_resume_profile(resume_text: str) -> dict:
    """
    Convert plain résumé text to a structured candidate profile dict.

    Calls: ask_json(RESUME_PROFILE_PROMPT, user, max_tokens=2000)
    User message format: "RÉSUMÉ TEXT:\\n\\n{resume_text}"

    Returns:
        Candidate profile dict matching the schema in RESUME_PROFILE_PROMPT.
    """
    user = f"RÉSUMÉ TEXT:\n\n{resume_text}"
    return ask_json(RESUME_PROFILE_PROMPT, user, max_tokens=2000)


def extract_jd_profile(jd_text: str) -> dict:
    """
    Convert plain job-description text to a structured JD profile dict.

    Calls: ask_json(JD_PROFILE_PROMPT, user, max_tokens=1500)
    User message format: "JOB DESCRIPTION TEXT:\\n\\n{jd_text}"

    Returns:
        JD profile dict matching the schema in JD_PROFILE_PROMPT.
    """
    user = f"JOB DESCRIPTION TEXT:\n\n{jd_text}"
    return ask_json(JD_PROFILE_PROMPT, user, max_tokens=1500)


# ---------------------------------------------------------------------------
# Evaluation functions (§6.2)
# ---------------------------------------------------------------------------

def analyse_keyword_match(resume_profile: dict, jd_profile: dict) -> dict:
    """
    Compare résumé keywords against JD requirements.

    Calls: ask_json(KEYWORD_MATCH_PROMPT, user, max_tokens=3000)
    User message format:
        "RÉSUMÉ PROFILE:\\n{json_dump}\\n\\nJD PROFILE:\\n{json_dump}"
    Use json.dumps(profile, indent=2) to serialise each profile.

    Returns:
        Keyword match dict with keys: present, missing, keyword_match_score.
    """
    resume_json = json.dumps(resume_profile, indent=2)
    jd_json = json.dumps(jd_profile, indent=2)
    user = f"RÉSUMÉ PROFILE:\n{resume_json}\n\nJD PROFILE:\n{jd_json}"
    return ask_json(KEYWORD_MATCH_PROMPT, user, max_tokens=3000)


def analyse_bullets(resume_profile: dict) -> dict:
    """
    Score every bullet in the résumé against the Action→Technology→Impact rubric.

    Calls: ask_json(BULLET_QUALITY_PROMPT, user, max_tokens=3000)
    User message format: "RÉSUMÉ PROFILE:\\n{json_dump}"

    Returns:
        Bullet quality dict with keys: bullets, bullet_quality_avg.
    """
    resume_json = json.dumps(resume_profile, indent=2)
    user = f"RÉSUMÉ PROFILE:\n{resume_json}"
    return ask_json(BULLET_QUALITY_PROMPT, user, max_tokens=3000)


def analyse_jargon(
    resume_profile: dict,
    jd_profile: dict,
) -> dict:
    """
    Detect résumé terminology that may not literally keyword-match the JD,
    and flag likely-equivalent phrasing the JD would recognise.

    Calls: ask_json(JARGON_AUDIT_PROMPT, user, max_tokens=1500)
    User message format:
        "RÉSUMÉ PROFILE:\\n{json_dump}\\n\\nJD PROFILE:\\n{json_dump}"

    Args:
        resume_profile: Output of extract_resume_profile().
        jd_profile: Output of extract_jd_profile().

    Returns:
        Jargon audit dict with keys: flags, jargon_score.
    """
    resume_json = json.dumps(resume_profile, indent=2)
    jd_json = json.dumps(jd_profile, indent=2)
    user = f"RÉSUMÉ PROFILE:\n{resume_json}\n\nJD PROFILE:\n{jd_json}"
    return ask_json(JARGON_AUDIT_PROMPT, user, max_tokens=1500)


def analyse_structure(resume_text: str) -> dict:
    """
    Audit general ATS-parseability formatting.

    Calls: ask_json(STRUCTURE_AUDIT_PROMPT, user, temperature=0.0, max_tokens=1500)
    User message format: "RÉSUMÉ TEXT:\\n\\n{resume_text}"

    Returns:
        Structure audit dict with keys: ats_red_flags, structure_score, etc.
    """
    user = f"RÉSUMÉ TEXT:\n\n{resume_text}"
    return ask_json(STRUCTURE_AUDIT_PROMPT, user, temperature=0.0, max_tokens=1500)


def analyse_background_fit(resume_profile: dict, jd_profile: dict) -> dict:
    """
    Assess how well the candidate's stated education/experience background
    plausibly aligns with what this role is asking for.

    Calls: ask_json(BACKGROUND_FIT_PROMPT, user, max_tokens=600)
    User message format:
        "RÉSUMÉ PROFILE:\\n{json_dump}\\n\\nJD PROFILE:\\n{json_dump}"

    Args:
        resume_profile: Output of extract_resume_profile().
        jd_profile: Output of extract_jd_profile().

    Returns:
        Background fit dict with keys: background_fit_score, alignment_commentary, etc.
    """
    resume_json = json.dumps(resume_profile, indent=2)
    jd_json = json.dumps(jd_profile, indent=2)
    user = f"RÉSUMÉ PROFILE:\n{resume_json}\n\nJD PROFILE:\n{jd_json}"
    return ask_json(BACKGROUND_FIT_PROMPT, user, max_tokens=600)


def summarise_overall(report: dict) -> str:
    """
    Generate a 3-bullet plain Markdown executive summary of the full report.

    NOTE: uses ask_text(), not ask_json() — returns a plain string, not a dict.

    Calls: ask_text(OVERALL_SUMMARY_PROMPT, user, max_tokens=400)
    User message format: "ANALYSIS REPORT:\\n{json_dump}"

    Only send the fields the summary needs — omit the raw résumé text to save tokens.
    Keys to include: overall_score, passes_ats_threshold, keyword_match, bullets,
    jargon, structure, background_fit.

    Returns:
        Plain Markdown string (3 bullet points).
    """
    summary_input = {
        "overall_score": report["overall_score"],
        "passes_ats_threshold": report["passes_ats_threshold"],
        "keyword_match": report["keyword_match"],
        "bullets": report["bullets"],
        "jargon": report["jargon"],
        "structure": report["structure"],
        "background_fit": report["background_fit"],
    }
    user = f"ANALYSIS REPORT:\n{json.dumps(summary_input, indent=2)}"
    return ask_text(OVERALL_SUMMARY_PROMPT, user, max_tokens=400)

def analyse_degree_alignment(jd_profile: dict, degree_program: str) -> dict:
    """JD profile + degree -> degree alignment dict."""
    user = (
        f"DEGREE PROGRAM: {degree_program}\n\n"
        f"JD PROFILE:\n{json.dumps(jd_profile, indent=2)}"
    )
    return ask_json(DEGREE_ALIGNMENT_PROMPT, user, max_tokens=600)

# ---------------------------------------------------------------------------
# Score aggregation (§7.2) — NO LLM call
# ---------------------------------------------------------------------------

def compute_overall_score(report: dict) -> int:
    """
    Compute the weighted composite score from sub-scores already in report.

    This function makes NO LLM call. It is pure Python arithmetic.

    Weights:
        keyword_match_score  40%  (report["keyword_match"]["keyword_match_score"])
        bullet_quality_avg   25%  (report["bullets"]["bullet_quality_avg"])
        structure_score      15%  (report["structure"]["structure_score"])
        jargon_score         10%  (report["jargon"]["jargon_score"])
        degree_alignment     10%  (report["degree_alignment"]["degree_alignment_score"])

    Returns:
        int — weighted average, rounded to the nearest whole number.
    """
    keyword_match_score = report.get("keyword_match", {}).get("keyword_match_score", 0)
    bullet_quality_avg = report.get("bullets", {}).get("bullet_quality_avg", 0)
    structure_score = report.get("structure", {}).get("structure_score", 0)
    jargon_score = report.get("jargon", {}).get("jargon_score", 0)
    background_fit_score = report.get("background_fit", {}).get("background_fit_score", 0)
    degree = report.get("degree_alignment", {}).get("degree_alignment_score", 0)

    total = (
        keyword_match_score * 0.40
        + bullet_quality_avg * 0.25
        + structure_score * 0.15
        + jargon_score * 0.10
        + degree * 0.10
    )

    return int(round(total))
