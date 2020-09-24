"""
Entrypoint for Streamlit server
"""
import base64
from datetime import datetime

import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
from django.utils import timezone
from django.conf import settings


from core.models import Issue
from .utils import filter_by_start_date, filter_by_end_date, df_download_link


MIN_START_DATE = timezone.make_aware(datetime(year=2020, month=1, day=1))


def run_referrals():
    st.header("Referrals")

    # Display download link for external analysis
    data_df = get_referral_df()
    num_cases = len(data_df)
    st.text("Referral info for all completed cases from Jan 1 2020 onwards.")
    st.text(f"Found {num_cases} submitted cases from that date onwards.")
    df_download_link(data_df, "Download referrals CSV", "referrals")

    st.subheader("Referral channels")
    topic = st.selectbox(
        "Case type", ["All", "Repairs", "COVID"], key=f"topic-choice-referral"
    )
    data_df = filter_by_start_date(data_df, "created_at", "referral")
    data_df = filter_by_end_date(data_df, "created_at", "referral")

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
    query_fields = ["topic", "created_at", "answers", "is_submitted"]
    questions = [
        "CLIENT_REFERRAL",
        "CLIENT_REFERRAL_LEGAL_CENTRE",
        "CLIENT_REFERRAL_CHARITY",
        "CLIENT_REFERRAL_OTHER",
    ]
    data = list(
        Issue.objects.filter(is_submitted=True, created_at__gte=MIN_START_DATE)
        .order_by("created_at")
        .values(*["topic", "created_at", "answers", "is_submitted"])
    )
    for datum in data:
        answers = datum["answers"]
        del datum["answers"]
        for question in questions:
            datum[question] = answers.get(question)

    return pd.DataFrame(
        data, columns=["topic", "created_at", "is_submitted", *questions]
    )

