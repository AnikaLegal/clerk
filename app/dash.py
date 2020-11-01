"""
Entrypoint for Streamlit reports server
"""
import django
import streamlit as st

django.setup()

from reports.issues import run_issues
from reports.referrals import run_referrals
from reports.problems import run_problems
from reports.demographics import run_demographics
from reports.cases import run_cases

def run_streamlit():
    st.sidebar.header("Anika Reports")
    page = st.sidebar.selectbox("Select a report", list(PAGES.keys()))
    page_runner = PAGES[page]
    page_runner()


PAGES = {
    "Cases by Referral": run_cases,
    "Submissions": run_issues,
    "Referrals": run_referrals,
    "Client Issues": run_problems,
    "Demographics": run_demographics,
}

run_streamlit()
