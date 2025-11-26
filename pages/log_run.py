import streamlit as st
from utils.database import get_conn


st.title("📝 Log a Run")


with st.form("log_run"):
    date = st.date_input("Date")
    distance = st.number_input("Distance (mi)")
    submitted = st.form_submit_button("Save")


    if submitted:
        conn = get_conn()
        conn.execute(
            "INSERT INTO runs (date, distance) VALUES (?, ?)",
            (date.isoformat(), distance),
        )
        conn.commit()
        conn.close()
        st.success("Run saved!")