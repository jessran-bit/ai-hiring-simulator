import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Hiring Simulator", layout="wide")

st.title("AI Hiring Simulator: Biased vs Clean Data")
st.markdown(
    """
This simulator shows how small scoring rules can produce unfair hiring outcomes.

You can switch between:
- **Biased model**: uses problematic proxy signals
- **Clean model**: focuses more on job-relevant factors
"""
)

st.sidebar.header("Simulation Controls")

dataset_option = st.sidebar.radio(
    "Choose dataset:",
    ["Biased Data", "Clean Data"]
)

show_explanations = st.sidebar.checkbox("Show scoring explanations", value=True)

if dataset_option == "Biased Data":
    df = pd.read_csv("data/candidates_biased.csv")
else:
    df = pd.read_csv("data/candidates_clean.csv")


def compute_biased_score(row):
    score = 0

    # Job-relevant factors
    score += row["years_experience"] * 2
    score += row["skills_score"]

    # Problematic bias-like rules / proxy penalties
    if row["career_gap_months"] > 6:
        score -= 8

    if row["women_org_signal"] == 1:
        score -= 10

    if row["soft_language_resume"] == 1:
        score -= 5

    return score


def compute_clean_score(row):
    score = 0

    # Focus on job-relevant signals
    score += row["years_experience"] * 2
    score += row["skills_score"]

    # Mild handling of long career gap, but not harshly penalized
    if row["career_gap_months"] > 6:
        score -= 2

    return score


if dataset_option == "Biased Data":
    df["ai_score"] = df.apply(compute_biased_score, axis=1)
else:
    df["ai_score"] = df.apply(compute_clean_score, axis=1)

ranked_df = df.sort_values(by="ai_score", ascending=False).reset_index(drop=True)
ranked_df.index = ranked_df.index + 1
ranked_df.index.name = "Rank"

st.subheader("Candidate Profiles")
st.dataframe(
    ranked_df[
        [
            "candidate_name",
            "years_experience",
            "skills_score",
            "career_gap_months",
            "women_org_signal",
            "soft_language_resume",
            "ai_score",
        ]
    ],
    use_container_width=True,
)

top_candidate = ranked_df.iloc[0]["candidate_name"]
lowest_candidate = ranked_df.iloc[-1]["candidate_name"]

col1, col2 = st.columns(2)

with col1:
    st.metric("Top-ranked candidate", top_candidate)

with col2:
    st.metric("Lowest-ranked candidate", lowest_candidate)

st.subheader("What to Notice")
st.markdown(
    """
- The **biased dataset/model** penalizes signals that may indirectly relate to gender.
- The **clean dataset/model** focuses more on experience and skills.
- Even when gender is not directly included, **proxy variables** can still create unfair outcomes.
"""
)

if show_explanations:
    st.subheader("How the scoring works")

    if dataset_option == "Biased Data":
        st.code(
            """
score = years_experience * 2
score += skills_score

if career_gap_months > 6:
    score -= 8

if women_org_signal == 1:
    score -= 10

if soft_language_resume == 1:
    score -= 5
""",
            language="python",
        )
        st.warning(
            "This model uses proxy-like features that can unfairly disadvantage some candidates."
        )
    else:
        st.code(
            """
score = years_experience * 2
score += skills_score

if career_gap_months > 6:
    score -= 2
""",
            language="python",
        )
        st.success(
            "This model is cleaner because it relies more on job-relevant factors."
        )

st.subheader("Reflection Questions")
st.markdown(
    """
1. Who was ranked lower, and why?  
2. Were the penalties based on actual job ability?  
3. What happens when biased assumptions are scaled through AI?  
4. If this were used in real hiring, who gets filtered out unfairly?
"""
)
