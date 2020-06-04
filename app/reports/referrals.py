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


from questions.models import Submission

START_DATE = timezone.make_aware(datetime(year=2020, month=1, day=1))


def run_referrals():
    st.header("Referrals")

    # Display download link for external analysis
    data_df = get_referral_df()
    num_cases = len(data_df)
    st.text(
        f"Referral info for all completed cases from Jan 1 2020 onwards. Found {num_cases} completed cases"
    )
    df_download_link(data_df, "Download referrals CSV", "referrals")

    st.subheader("Referral channels")
    topic = st.selectbox(
        "Case type", ["All", "Repairs", "COVID"], key=f"topic-choice-referral"
    )
    if topic == "Repairs":
        data_df = data_df[data_df["topic"] == "REPAIRS"]
    elif topic == "COVID":
        data_df = data_df[data_df["topic"] == "COVID"]
    else:
        data_df = data_df

    num_cases = len(data_df)
    st.text(f"{num_cases} cases total.")
    topic_bar_chart(data_df, "CLIENT_REFERRAL")

    write_referrals(data_df, "CLIENT_REFERRAL_LEGAL_CENTRE", "Legal centre", topic)
    write_referrals(data_df, "CLIENT_REFERRAL_CHARITY", "Charity", topic)
    write_referrals(data_df, "CLIENT_REFERRAL_OTHER", "Other", topic)


def write_referrals(data_df, column, name, topic):
    st.subheader(f"Referrals from {name} for {topic} cases")
    mask = ~data_df[column].isnull()
    legal_df = data_df[mask]
    num_cases = len(legal_df)
    st.text(f"{num_cases} cases referred from {name} for {topic} cases.")
    plot_data = legal_df[column].value_counts()
    st.write(plot_data.to_dict())


def topic_bar_chart(data_df: pd.DataFrame, column: str):
    plot_data = {}
    for topic in data_df["topic"].unique():
        plot_data[topic] = data_df[data_df["topic"] == topic][column].value_counts()

    plot_df = pd.DataFrame(plot_data)
    st.bar_chart(plot_df)


def get_referral_df():
    query_fields = ["topic", "created_at", "answers", "complete"]
    questions = [
        "CLIENT_REFERRAL",
        "CLIENT_REFERRAL_LEGAL_CENTRE",
        "CLIENT_REFERRAL_CHARITY",
        "CLIENT_REFERRAL_OTHER",
    ]
    data = list(
        Submission.objects.filter(complete=True, created_at__gte=START_DATE)
        .order_by("created_at")
        .values(*["topic", "created_at", "answers", "complete"])
    )
    for datum in data:
        answers = {a["name"]: a.get("answer") for a in datum["answers"]}
        del datum["answers"]
        for question in questions:
            datum[question] = answers.get(question)

    return pd.DataFrame(data, columns=["topic", "created_at", "complete", *questions])


def df_download_link(df: pd.DataFrame, text: str, filename: str):
    """
    Generates a link allowing the data in a given panda dataframe to be downloaded
    """
    csv_bytes = df.to_csv(index=False).encode()
    b64_str = base64.b64encode(csv_bytes).decode()
    html_str = f'<a download="{filename}.csv" href="data:file/csv;name={filename}.csv;base64,{b64_str}">{text}</a>'
    st.markdown(html_str, unsafe_allow_html=True)
