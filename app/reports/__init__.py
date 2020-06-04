"""
Entrypoint for Streamlit server
"""
import django
import streamlit as st

django.setup()

from .submissions import run_submissions
from .referrals import run_referrals


def run_streamlit():
    st.sidebar.header("Anika Reports")
    page = st.sidebar.selectbox("Select a report", list(PAGES.keys()))
    page_runner = PAGES[page]
    page_runner()


PAGES = {
    "Submissions": run_submissions,
    "Referrals": run_referrals,
}
