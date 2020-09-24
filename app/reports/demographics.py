"""
Client problems report
"""
from datetime import datetime

import streamlit as st
import pandas as pd

from .utils import (
    filter_by_start_date,
    filter_by_end_date,
    get_issue_df,
    plot_category_counts,
    df_download_link,
    filter_by_topic_choice,
)


def run_demographics():
    st.header("Client Demographics")
    st.text("A breakdown of who our clients are.")
    df = get_issue_df()
    df = df[df["is_submitted"] == 1]
    df = filter_by_topic_choice(df, key="demo")
    df = filter_by_start_date(df, "created_at", key="demo")

    st.subheader("Client ages")
    df["client_age"] = df["CLIENT_DOB"].apply(dob_str_to_age)
    age_categories = [
        "15-20",
        "20-25",
        "25-30",
        "30-35",
        "35-40",
        "40-45",
        "45-50",
        "50-60",
        "60-65",
        "65-70",
        "70+",
    ]
    plot_histogram(df, "client_age", "Age", age_categories, max_val=90)

    st.subheader("Client weekly income")
    earnings_categories = [
        "0-0250",
        "0250-500",
        "0500-0750",
        "0750-1000",
        "1000-1250",
        "1250-1500",
        "1500-1750",
        "1750-2000",
        "2000+",
    ]
    plot_histogram(df, "CLIENT_WEEKLY_EARNINGS", "Weekly Earnings", earnings_categories)

    st.subheader("Client special circumstances")
    df["Answers"] = df["CLIENT_SPECIAL_CIRCUMSTANCES"]
    plot_category_counts(df, "Answers")


def plot_histogram(
    df, value_col, label_name, buckets, min_val=float("-inf"), max_val=float("inf")
):
    df[label_name] = "Unknown"
    for bucket_name in buckets:
        bucket_parts = bucket_name.replace("+", "").split("-")
        if len(bucket_parts) > 1:
            start_val, end_val = [int(p) for p in bucket_parts]
        else:
            start_val = int(bucket_parts[0])
            end_val = float("inf")

        mask = (df[value_col] < start_val) | (df[value_col] >= end_val)
        df[label_name] = df[label_name].where(mask, bucket_name)

    df[label_name] = df[label_name].where(df[value_col] < max_val, "Unknown")
    df[label_name] = df[label_name].where(df[value_col] > min_val, "Unknown")
    df[label_name] = df[label_name].where(df[value_col].notnull(), "Unknown")
    plot_category_counts(df, label_name)


def dob_str_to_age(s: str):
    if s == "111-1-1":
        return
    try:
        # Mon Feb 08 1993
        dt = datetime.strptime(s, "%a %b %M %Y")
    except ValueError:
        try:
            # 1995-6-6
            dt = datetime.strptime(s, "%Y-%d-%M")
        except ValueError:
            return

    delta = datetime.now() - dt
    return int(delta.days // 365.25)
