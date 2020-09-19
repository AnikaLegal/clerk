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


from core.models import Submission, Client

from .utils import (
    filter_by_start_date,
    datetime_to_day,
    datetime_to_month,
    df_download_link,
    filter_by_topic_choice,
    filter_by_completed,
)


def run_submissions():
    st.header("Submissions")

    # Display download link for external analysis
    data_df = get_submission_df(["topic", "created_at", "complete"])
    df_download_link(data_df, "Download submission CSV", "submissions")

    st.subheader("Completed Submissions")
    st.text("All intake form submissions that have been fully filled out and submitted")
    key = "submissions-completed"
    data_df = get_submission_df(["topic", "created_at", "complete"])
    data_df = data_df[data_df["complete"] == 1]
    data_df = filter_by_topic_choice(data_df, key)
    data_df["date_rollup"] = data_df["created_at"].apply(datetime_to_month)
    topic_bar_chart(data_df, "date_rollup")

    st.subheader("Intake completion rate")
    st.text("Successes (form submitted) divided by attempts (one or more answers)")
    attempt_df = get_client_df(["created_at"])
    attempt_df["date_rollup"] = attempt_df["created_at"].apply(datetime_to_month)
    attempts = attempt_df["date_rollup"].value_counts()
    success_df = get_submission_df(["created_at", "complete"])
    success_df = success_df[success_df["complete"] == 1]
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


def get_submission_df(fields):
    data = Submission.objects.order_by("created_at").values_list(*fields)
    return pd.DataFrame(data, columns=fields)
