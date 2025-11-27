import streamlit as st
from datetime import date


def render_settings_page():
    st.title("⚙ Settings")

    st.subheader("Race Goal")

    race_name = st.text_input(
        "Goal Race Name",
        value=st.session_state.get("race_goal_name", "Pittsburgh Half Marathon"),
    )
    race_date = st.date_input(
        "Race Date",
        value=st.session_state.get("race_goal_date", date(2026, 5, 3)),
    )
    target_time = st.text_input(
        "Target Time (HH:MM:SS)",
        value=st.session_state.get("race_goal_time", "01:39:59"),
    )

    st.subheader("Display Preferences")

    theme = st.selectbox(
        "Theme Preference",
        ["System Default", "Light", "Dark"],
        index=2 if st.session_state.get("theme", "Dark") == "Dark" else 0,
    )

    units = st.selectbox(
        "Units",
        ["Miles", "Kilometers"],
        index=0 if st.session_state.get("units", "Miles") == "Miles" else 1,
    )

    if st.button("Save Settings"):
        st.session_state["race_goal_name"] = race_name
        st.session_state["race_goal_date"] = race_date
        st.session_state["race_goal_time"] = target_time
        st.session_state["theme"] = theme
        st.session_state["units"] = units

        # also store condensed values used by AI Coach
        st.session_state["race_goal"] = f"{race_name} in {target_time}"
        st.session_state["race_date_str"] = race_date.isoformat()

        st.success("Settings saved!")


def main():
    render_settings_page()


if __name__ == "__main__":
    main()
