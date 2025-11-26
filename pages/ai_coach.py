import streamlit as st
from utils.ai_helpers import call_ai


st.title("🤖 AI Coach")


if st.button("Analyze Training"):
    st.write(call_ai("Analyze my recent training."))