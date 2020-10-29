import pandas as pd
import streamlit as st
import json

from core.models import Client, Issue
from .utils import datetime_to_month


def fetch_data():
    joined = {
        "referrer": [], 
        "topic": [],
        "created_at": []
    }

    # Perform crude conditional join
    for issue in Issue.objects.all():
        for client in Client.objects.all():
            if "CLIENT_EMAIL" in issue.answers:
                issue_email = issue.answers["CLIENT_EMAIL"]
            else:
                continue
            if issue_email == client.email:
                joined["referrer"].append(client.referrer)
                joined["topic"].append(issue.topic)
                joined["created_at"].append(issue.created_at)
                break

    return pd.DataFrame(joined)

def generate_monthly_chart(data, referrer):
    st.subheader("Submitted issues per month")
    filtered = data[data["referrer"] == referrer]
    filtered["Case count"] = filtered["created_at"].apply(datetime_to_month)
    histogram = filtered["Case count"].value_counts()
    st.bar_chart(histogram)

def run_cases():
    st.header("Cases by Referral")
    st.text("View the number of cases submitted by a referral per month.")
    data = fetch_data()

    option = st.selectbox(
        label="Referrer name",
        options=[i for i in data["referrer"].unique() if len(i)]
    )
    generate_monthly_chart(data, option)
