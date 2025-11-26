import streamlit as st
import pandas as pd
from utils.garmin import parse_garmin_csv


st.title("📥 Garmin Import")


file = st.file_uploader("Upload CSV", type="csv")
if file:
    df = pd.read_csv(file)
    st.write(parse_garmin_csv(df))