"""
Entrypoint for Streamlit server
"""
import base64
from datetime import datetime

import django
import streamlit as st
import pandas as pd
import altair as alt
from django.utils import timezone
from django.conf import settings

django.setup()

from questions.models import Submission


def run_streamlit():
    st.header("Submissions")
    st.subheader("All Submissions")
    cols = ["topic", "created_at", "num_answers", "complete"]
    data = Submission.objects.order_by("created_at").values_list(*cols)
    data_df = pd.DataFrame(data, columns=cols)
    df_download_link(data_df, "Download submission CSV", "submissions")
    data_df["day"] = data_df["created_at"].apply(datetime_to_month)
    covid_mask = data_df["topic"] == "COVID"
    repairs_mask = data_df["topic"] == "REPAIRS"
    covid_counts = data_df[covid_mask]["day"].value_counts()
    repairs_counts = data_df[repairs_mask]["day"].value_counts()
    plot_df = pd.DataFrame({"Repairs": repairs_counts, "COVID": covid_counts})
    st.bar_chart(plot_df)

    st.subheader("Completed Submissions")
    cols = ["topic", "created_at", "num_answers", "complete"]
    data = Submission.objects.order_by("created_at").values_list(*cols)
    data_df = pd.DataFrame(data, columns=cols)
    data_df = data_df[data_df["complete"] == 1]
    data_df["month"] = data_df["created_at"].apply(datetime_to_month)
    covid_mask = data_df["topic"] == "COVID"
    repairs_mask = data_df["topic"] == "REPAIRS"
    covid_counts = data_df[covid_mask]["month"].value_counts()
    repairs_counts = data_df[repairs_mask]["month"].value_counts()
    plot_df = pd.DataFrame({"Repairs": repairs_counts, "COVID": covid_counts})
    st.bar_chart(plot_df)


def datetime_to_month(dt):
    return datetime(year=dt.year, month=dt.month, day=1)


def df_download_link(df: pd.DataFrame, text: str, filename: str):
    """
    Generates a link allowing the data in a given panda dataframe to be downloaded
    """
    csv_bytes = df.to_csv(index=False).encode()
    b64_str = base64.b64encode(csv_bytes).decode()
    html_str = f'<a download="{filename}.csv" href="data:file/csv;name={filename}.csv;base64,{b64_str}">{text}</a>'
    st.markdown(html_str, unsafe_allow_html=True)
