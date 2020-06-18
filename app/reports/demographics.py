"""
Client problems report
"""
import streamlit as st
import pandas as pd

from .utils import (
    filter_by_start_date,
    filter_by_end_date,
    get_submission_df,
    plot_histogram,
    df_download_link,
)


def run_demographics():
    st.header("Client Demographics")
    st.text("A breakdown of who our clients are.")
    df = get_submission_df()
    df = df[df["complete"] == 1]

    st.header("TODO")

    # age_categories = ["15-20", "20-25", "25-30", "30-35", "35-40", "40-45", "45-50", "50+"]
    # for age_category in age_categories:

    # df['age_category'] = df['CLIENT_DOB']

    # plot_histogram(df, "age_category")
