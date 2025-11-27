import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta

from utils.database import fetch_runs


def render_calendar_page():
    st.title("📆 Training Calendar")

    df = fetch_runs()
    if df.empty:
        st.info("No runs logged yet. Log a run to see the calendar.")
        return

    df["date_dt"] = pd.to_datetime(df["date"]).dt.date

    today = date.today()
    year = st.sidebar.number_input("Year", min_value=2000, max_value=2100, value=today.year)
    month = st.sidebar.number_input("Month", min_value=1, max_value=12, value=today.month)

    cal = calendar.Calendar(firstweekday=0)
    month_days = list(cal.itermonthdates(year, month))

    st.subheader(f"{calendar.month_name[month]} {year}")

    # 7 columns for days of the week
    cols = st.columns(7)
    for i, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        cols[i].markdown(f"**{name}**")

    week_cols = st.columns(7)
    col_index = 0

    for d in month_days:
        if d.month != month:
            # gray out other-month days
            week_cols[col_index].markdown(f"<span style='color: gray'>{d.day}</span>", unsafe_allow_html=True)
        else:
            day_runs = df[df["date_dt"] == d]
            miles = day_runs["distance"].sum()
            label = f"**{d.day}**"
            if miles > 0:
                label += f"<br/>{miles:.1f} mi"
            week_cols[col_index].markdown(label, unsafe_allow_html=True)

        col_index += 1
        if col_index == 7:
            col_index = 0
            week_cols = st.columns(7)


def main():
    render_calendar_page()


if __name__ == "__main__":
    main()
