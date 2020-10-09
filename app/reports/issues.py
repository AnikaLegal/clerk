"""
Entrypoint for Streamlit server
"""
from datetime import datetime

import django
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
from django.utils import timezone
from django.conf import settings


from core.models import Issue, Client

from .utils import (
    filter_by_start_date,
    datetime_to_day,
    datetime_to_month,
    df_download_link,
    filter_by_topic_choice,
    filter_by_completed,
)


def run_issues():
    st.header("Issues")

    # Display download link for external analysis
    data_df = get_issue_df(["topic", "created_at", "is_submitted"])
    df_download_link(data_df, "Download issue CSV", "issues")

    st.subheader("Submitted Issues")
    st.text("All intake form issues that have been fully filled out and submitted")
    key = "issues-completed"
    data_df = get_issue_df(["topic", "created_at", "is_submitted"])
    data_df = data_df[data_df["is_submitted"] == 1]
    data_df = filter_by_topic_choice(data_df, key)
    data_df["date_rollup"] = data_df["created_at"].apply(datetime_to_month)
    topic_bar_chart(data_df, "date_rollup")

    st.subheader("Intake completion rate")
    st.text("Successes (form submitted) divided by attempts (one or more answers)")
    attempt_df = get_client_df(["created_at"])
    attempt_df["date_rollup"] = attempt_df["created_at"].apply(datetime_to_month)
    attempts = attempt_df["date_rollup"].value_counts()
    success_df = get_issue_df(["created_at", "is_submitted"])
    success_df = success_df[success_df["is_submitted"] == 1]
    success_df["date_rollup"] = success_df["created_at"].apply(datetime_to_month)
    successes = success_df["date_rollup"].value_counts()
    st.bar_chart(successes / attempts)


def topic_bar_chart(data_df: pd.DataFrame, column: str):
    plot_data = {}
    for topic in data_df["topic"].unique():
        plot_data[topic] = data_df[data_df["topic"] == topic][column].value_counts()

    plot_df = pd.DataFrame(plot_data)
    st.bar_chart(plot_df)


def get_client_df(fields):
    data = Client.objects.order_by("created_at").values_list(*fields)
    return pd.DataFrame(data, columns=fields)


def get_issue_df(fields):
    data = Issue.objects.order_by("created_at").values_list(*fields)
    return pd.DataFrame(data, columns=fields)
