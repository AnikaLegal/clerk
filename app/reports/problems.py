"""
Client problems report
"""
import streamlit as st
import pandas as pd

from .utils import (
    filter_by_start_date,
    filter_by_end_date,
    get_issue_df,
    plot_category_counts,
    df_download_link,
)


def run_problems():
    st.header("Client Issues")
    st.text("A breakdown of the kinds of issues our clients have")
    df = get_issue_df()
    df = df[df["is_submitted"] == 1]
    df = filter_by_start_date(df, "created_at", "referral")
    repairs_df = df[df["topic"] == "REPAIRS"]
    rr_df = df[df["topic"] == "RENT_REDUCTION"]

    st.subheader("Repairs client issues")
    num_repairs_cases = len(repairs_df)
    st.text(f"Found {num_repairs_cases} submitted repairs cases")
    plot_category_counts(repairs_df, "DEFECT_TYPE")

    download_df = repairs_df[["DEFECT_TYPE", "DEFECT_DESCRIPTION"]].copy()
    df_download_link(
        download_df, "Download repairs issue type CSV", "repairs-issue-types"
    )

    st.subheader("Rent reduction client issues")
    num_covid_cases = len(rr_df)
    st.text(f"Found {num_covid_cases} submitted rent reduction cases")
    plot_category_counts(rr_df, "ISSUE_TYPE")

    download_df = rr_df[["ISSUE_TYPE", "ISSUE_DESCRIPTION"]].copy()
    df_download_link(download_df, "Download COVID issue type CSV", "covid-issue-types")
