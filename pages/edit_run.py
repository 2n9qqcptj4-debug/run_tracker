import streamlit as st
import pandas as pd
from utils.database import fetch_runs, update_run, delete_run


def render_edit_run_page():
    st.title("✏️ Edit Run")

    df = fetch_runs()

    if df.empty:
        st.warning("No runs found. Log a run first.")
        return

    # --------------------------------------------------
    # Select the run to edit
    # --------------------------------------------------
    st.subheader("Choose a run to edit")

    df_sorted = df.sort_values("date", ascending=False)
    run_options = {
        f"{row['date']} – {row['run_type']} – {row['distance']} mi": row["id"]
        for _, row in df_sorted.iterrows()
    }

    selected_label = st.selectbox("Select a run:", list(run_options.keys()))
    selected_id = run_options[selected_label]

    # Get selected run record
    run = df[df["id"] == selected_id].iloc[0]

    # --------------------------------------------------
    # Edit Fields
    # --------------------------------------------------
    st.subheader("Edit Run Details")

    new_date = st.date_input("Date", pd.to_datetime(run["date"]))

    new_run_type = st.selectbox(
        "Run Type",
        ["Easy", "Tempo", "Interval", "Long", "Race", "Recovery"],
        index=["Easy", "Tempo", "Interval", "Long", "Race", "Recovery"].index(run["run_type"]),
    )

    new_distance = st.number_input(
        "Distance (miles)", min_value=0.0, value=float(run["distance"]), step=0.1
    )

    # Duration input
    new_duration = st.text_input(
        "Duration (HH:MM:SS)",
        value=str(run["duration"]) if isinstance(run["duration"], str) else "00:00:00",
    )

    new_avg_hr = st.number_input(
        "Avg HR (optional)",
        min_value=0,
        max_value=250,
        value=int(run["avg_hr"]) if pd.notna(run["avg_hr"]) else 0,
    )

    new_effort = st.slider("Effort (1–10)", 1, 10, int(run["effort"]))

    # --------------------------------------------------
    # Save Changes Button
    # --------------------------------------------------
    if st.button("💾 Save Changes"):
        update_run(
            run_id=selected_id,
            date=new_date,
            run_type=new_run_type,
            distance=new_distance,
            duration=new_duration,
            avg_hr=new_avg_hr,
            effort=new_effort,
        )
        st.success("Run updated successfully!")
        st.experimental_rerun()

    st.write("---")

    # --------------------------------------------------
    # DELETE RUN BUTTON
    # --------------------------------------------------
    st.subheader("❌ Delete This Run")

    delete_confirm = st.checkbox("I understand that this cannot be undone", key="delete_confirm")

    if st.button("🗑️ Delete Run"):
        if delete_confirm:
            delete_run(selected_id)
            st.error("Run deleted.")
            st.experimental_rerun()
        else:
            st.warning("Please check the confirmation box before deleting.")


def main():
    render_edit_run_page()


if __name__ == "__main__":
    main()
