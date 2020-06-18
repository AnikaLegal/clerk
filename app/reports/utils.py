"""
Entrypoint for Streamlit server
"""
import base64
from datetime import datetime

import pandas as pd
import streamlit as st
from django.utils import timezone

from questions.models import Submission

DEFAULT_FIELDS = ["topic", "created_at", "answers", "complete"]


def plot_histogram(df, fieldname):
    defects = []
    for ds in df[fieldname]:
        if type(ds) is str:
            defects.append(ds)
        else:
            defects += ds

    plot_df = pd.Series(defects, name=fieldname).value_counts()
    st.bar_chart(plot_df)


def get_submission_df(fields=DEFAULT_FIELDS):
    data = Submission.objects.order_by("created_at").values(*fields)
    for datum in data:
        for a in datum["answers"]:
            datum[a["name"]] = a.get("answer")

        del datum["answers"]

    return pd.DataFrame(data)


def df_download_link(df: pd.DataFrame, text: str, filename: str):
    """
    Generates a link allowing the data in a given panda dataframe to be downloaded
    """
    csv_bytes = df.to_csv(index=False).encode()
    b64_str = base64.b64encode(csv_bytes).decode()
    html_str = f'<a download="{filename}.csv" href="data:file/csv;name={filename}.csv;base64,{b64_str}">{text}</a>'
    st.markdown(html_str, unsafe_allow_html=True)


def filter_by_end_date(data_df: pd.DataFrame, date_field: str, key: str):
    start_date = st.date_input(
        "End date",
        value=data_df[date_field].max(),
        min_value=data_df[date_field].min(),
        max_value=data_df[date_field].max(),
        key=f"end-date-{key}",
    )
    start_date = timezone.make_aware(datetime_to_day(start_date))
    return data_df[data_df[date_field] <= start_date]


def filter_by_start_date(data_df: pd.DataFrame, date_field: str, key: str):
    start_date = st.date_input(
        "Start date",
        value=data_df[date_field].min(),
        min_value=data_df[date_field].min(),
        max_value=data_df[date_field].max(),
        key=f"start-date-{key}",
    )
    start_date = timezone.make_aware(datetime_to_day(start_date))
    return data_df[data_df[date_field] >= start_date]


def datetime_to_month(dt):
    return datetime(year=dt.year, month=dt.month, day=1)


def datetime_to_day(dt):
    return datetime(year=dt.year, month=dt.month, day=dt.day)
