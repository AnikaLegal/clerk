"""
Entrypoint for Streamlit server
"""
import base64
from datetime import datetime

import django
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
from django.utils import timezone
from django.conf import settings

django.setup()

from questions.models import Submission


def run_streamlit():
    st.header("Submissions")

    # Display download link for external analysis
    data_df = get_submission_df(["topic", "created_at", "num_answers", "complete"])
    df_download_link(data_df, "Download submission CSV", "submissions")

    # Get completed submissions grouped by month
    st.subheader("Completed Submissions")
    st.text("All intake form submissions that have been fully filled out and submitted")
    key = "submissions-completed"
    data_df = get_submission_df(["topic", "created_at", "num_answers", "complete"])
    data_df = data_df[data_df["complete"] == 1]
    data_df = topic_choice(data_df, key)
    data_df = date_rollup_choice(data_df, key)
    topic_bar_chart(data_df, "date_rollup")

    # Get all submissions grouped by month
    st.subheader("All intake attempts")
    st.text(
        "An attempt is a user visiting the intake form and filling in zero or more questions"
    )
    key = "all-submissions"
    data_df = get_submission_df(["topic", "created_at", "num_answers", "complete"])
    data_df = filter_by_num_answers(data_df, key)
    data_df = topic_choice(data_df, key)
    data_df = date_rollup_choice(data_df, key)
    topic_bar_chart(data_df, "date_rollup")

    st.subheader("Number of questions answered")
    st.text(
        "Number of questions answered per submission, incomplete submissions included"
    )
    key = "num-answers"
    data_df = get_submission_df(["topic", "created_at", "num_answers", "complete"])
    data_df = topic_choice(data_df, key)
    data_df = filter_by_start_date(data_df, key)
    chart = (
        alt.Chart(data_df)
        .mark_bar()
        .encode(alt.X("num_answers:Q", bin=True), y="count()", color="topic")
    )
    st.altair_chart(chart, use_container_width=True)


def topic_choice(data_df: pd.DataFrame, key: str):
    topic = st.selectbox(
        "Case type", ["All", "Repairs", "COVID"], key=f"topic-choice-{key}"
    )
    if topic == "Repairs":
        return data_df[data_df["topic"] == "REPAIRS"]
    elif topic == "COVID":
        return data_df[data_df["topic"] == "COVID"]
    else:
        return data_df


def topic_bar_chart(data_df: pd.DataFrame, column: str):
    plot_data = {}
    for topic in data_df["topic"].unique():
        plot_data[topic] = data_df[data_df["topic"] == topic][column].value_counts()

    plot_df = pd.DataFrame(plot_data)
    st.bar_chart(plot_df)


def date_rollup_choice(data_df: pd.DataFrame, key: str):
    rollup_choice = st.selectbox(
        "Reporting period", ["Month", "Day"], key=f"-date-rollup-{key}"
    )
    rollup_func = datetime_to_month if rollup_choice == "Month" else datetime_to_day
    data_df["date_rollup"] = data_df["created_at"].apply(rollup_func)
    return data_df


def filter_by_num_answers(data_df: pd.DataFrame, key: str):
    min_qs = st.slider(
        "Minimum number of questions answered",
        0,
        int(data_df.num_answers.max()),
        key=f"num-answers-{key}",
    )
    return data_df[data_df["num_answers"] >= min_qs]


def filter_by_start_date(data_df: pd.DataFrame, key: str):
    start_date = st.date_input(
        "Start date",
        value=data_df.created_at.min(),
        min_value=data_df.created_at.min(),
        max_value=data_df.created_at.max(),
        key=f"start-date-{key}",
    )
    start_date = timezone.make_aware(datetime_to_day(start_date))
    return data_df[data_df["created_at"] >= start_date]


def get_submission_df(fields):
    data = Submission.objects.order_by("created_at").values_list(*fields)
    return pd.DataFrame(data, columns=fields)


def datetime_to_month(dt):
    return datetime(year=dt.year, month=dt.month, day=1)


def datetime_to_day(dt):
    return datetime(year=dt.year, month=dt.month, day=dt.day)


def df_download_link(df: pd.DataFrame, text: str, filename: str):
    """
    Generates a link allowing the data in a given panda dataframe to be downloaded
    """
    csv_bytes = df.to_csv(index=False).encode()
    b64_str = base64.b64encode(csv_bytes).decode()
    html_str = f'<a download="{filename}.csv" href="data:file/csv;name={filename}.csv;base64,{b64_str}">{text}</a>'
    st.markdown(html_str, unsafe_allow_html=True)
