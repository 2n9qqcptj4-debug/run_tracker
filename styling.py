import streamlit as st


def inject_css():
    st.markdown(
"""
<style>
body { font-family: 'Inter', sans-serif; }
.card { padding: 1rem; background: #111; border-radius: 12px; }
</style>
""",
unsafe_allow_html=True,
)