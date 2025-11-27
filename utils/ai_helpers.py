import streamlit as st

def get_client():
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("❌ OPENAI_API_KEY is NOT present in Streamlit secrets.")
        raise KeyError("OPENAI_API_KEY missing in st.secrets")

    if not st.secrets["OPENAI_API_KEY"]:
        st.error("❌ OPENAI_API_KEY exists but is EMPTY.")
        raise ValueError("OPENAI_API_KEY is empty")

    st.success("✅ OPENAI_API_KEY successfully loaded.")
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

from openai import OpenAI


def get_client():
    # Uses the OPENAI_API_KEY stored in Streamlit secrets
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def call_ai(prompt: str):
    client = get_client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content

