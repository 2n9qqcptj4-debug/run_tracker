import streamlit as st
from openai import OpenAI
import traceback


# =========================================================
# CREATE OPENAI CLIENT SAFELY
# =========================================================
def get_client():
    """
    Creates an OpenAI client using Streamlit secrets.
    Does NOT pass unsupported args (like proxies).
    """

    debug = []

    # Make sure key exists
    if "OPENAI_API_KEY" not in st.secrets:
        debug.append("❌ OPENAI_API_KEY is NOT in st.secrets!")
        return None

    api_key = st.secrets["OPENAI_API_KEY"]
    debug.append(f"🔑 API key loaded: {api_key[:4]}...")

    try:
        client = OpenAI(api_key=api_key)
        debug.append("✅ OpenAI client successfully created.")
        st.session_state["debug_info"] = "\n".join(debug)
        return client

    except Exception as e:
        debug.append(f"❌ Failed to initialize client: {e}")
        st.session_state["debug_info"] = "\n".join(debug)
        return None


# =========================================================
# CALL OPENAI SAFELY
# =========================================================
def call_ai(prompt: str):
    """
    Sends a prompt to OpenAI and returns the response text.
    """

    client = get_client()

    if client is None:
        return "❌ OpenAI client not initialized. Check API key in Streamlit secrets."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    except Exception as e:
        st.session_state["debug_info"] = f"❌ Error calling OpenAI:\n{traceback.format_exc()}"
        return f"❌ OpenAI Error:\n{e}"


# =========================================================
# DEBUG INFO VIEWER
# =========================================================
def get_debug_info():
    """
    Returns whatever debug info has been captured.
    """
    return st.session_state.get("debug_info", "No debug info yet.")
