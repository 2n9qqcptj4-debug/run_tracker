import streamlit as st
from openai import OpenAI

def get_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def call_ai(prompt: str):
    client = get_client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content
