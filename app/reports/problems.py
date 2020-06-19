"""
Client problems report
"""
import streamlit as st
import pandas as pd

from .utils import (
    filter_by_start_date,
    filter_by_end_date,
    get_submission_df,
    plot_category_counts,
    df_download_link,
)


def run_problems():
    st.header("Client Issues")
    st.text("A breakdown of the kinds of issues our clients have")
    df = get_submission_df()
    df = df[df["complete"] == 1]
    df = filter_by_start_date(df, "created_at", "referral")
    repairs_df = df[df["topic"] == "REPAIRS"]
    covid_df = df[df["topic"] == "COVID"]

    st.subheader("Repairs client issues")
    num_repairs_cases = len(repairs_df)
    st.text(f"Found {num_repairs_cases} submitted repairs cases")
    plot_category_counts(repairs_df, "DEFECT_TYPE")

    st.subheader("COVID client issues")
    num_covid_cases = len(covid_df)
    st.text(f"Found {num_covid_cases} submitted repairs cases")
    plot_category_counts(covid_df, "ISSUE_TYPE")

