import streamlit as st
from utils.database import fetch_runs


st.title("📜 Training Feed")


runs = fetch_runs()
st.write(runs)