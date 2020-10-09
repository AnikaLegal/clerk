"""
Entrypoint for Streamlit server
"""
import django
import streamlit as st

django.setup()

from .issues import run_issues
from .referrals import run_referrals
from .problems import run_problems
from .demographics import run_demographics


def run_streamlit():
    st.sidebar.header("Anika Reports")
    page = st.sidebar.selectbox("Select a report", list(PAGES.keys()))
    page_runner = PAGES[page]
    page_runner()


PAGES = {
    "Submissions": run_issues,
    "Referrals": run_referrals,
    "Client Issues": run_problems,
    "Demographics": run_demographics,
}
