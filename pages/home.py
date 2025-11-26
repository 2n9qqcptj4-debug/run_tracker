import streamlit as st
from utils.database import fetch_runs
from utils.metrics import prepare_metrics_df


st.title("🏠 Home")


runs = fetch_runs()
if runs.empty:
    st.info("No runs logged yet.")
else:
    st.write(runs.tail())