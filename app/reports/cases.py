import pandas as pd
import streamlit as st
import json

from core.models import Issue
from .utils import datetime_to_month


def fetch_data():
    joined = {"referrer": [], "topic": [], "created_at": []}

    # Perform crude conditional join
    for issue in Issue.objects.select_related("client").all():
        joined["referrer"].append(issue.client.referrer)
        joined["topic"].append(issue.topic)
        joined["created_at"].append(issue.created_at)

    return pd.DataFrame(joined)


def generate_monthly_chart(data_df, referrer):
    st.subheader("Submitted issues per month")
    filtered_df = data_df[data_df["referrer"] == referrer]
    filtered_df["date_rollup"] = filtered_df["created_at"].apply(datetime_to_month)
    plot_data = {}
    for topic in data_df["topic"].unique():
        topic_mask = filtered_df["topic"] == topic
        plot_data[topic] = filtered_df[topic_mask]["date_rollup"].value_counts()

    plot_df = pd.DataFrame(plot_data)
    st.bar_chart(plot_df)


def run_cases():
    st.header("Cases by Referral")
    st.text("View the number of cases submitted by a referral per month.")
    data = fetch_data()

    option = st.selectbox(
        label="Referrer name", options=[i for i in data["referrer"].unique() if len(i)]
    )
    generate_monthly_chart(data, option)
