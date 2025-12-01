import streamlit as st
import requests
import traceback
import json


OPENAI_URL = "https://api.openai.com/v1/chat/completions"


# =========================================================
# CALL OPENAI USING RAW HTTPS (NO CLIENT — NO PROXIES BUG)
# =========================================================
def call_ai(prompt: str):
    """
    Sends a chat completion request using raw HTTPS.
    Avoids the Client() constructor completely.
    """
    debug = []

    if "OPENAI_API_KEY" not in st.secrets:
        debug.append("❌ OPENAI_API_KEY missing from st.secrets.")
        st.session_state["debug_info"] = "\n".join(debug)
        return "❌ Missing API key."

    api_key = st.secrets["OPENAI_API_KEY"]
    debug.append("🔑 API key loaded.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful running coach."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(OPENAI_URL, headers=headers, json=body, timeout=30)
        debug.append(f"🌐 Status Code: {response.status_code}")

        if response.status_code != 200:
            debug.append(f"❌ Error Response:\n{response.text}")
            st.session_state["debug_info"] = "\n".join(debug)
            return f"❌ OpenAI API Error:\n{response.text}"

        data = response.json()
        debug.append("✅ Successfully parsed OpenAI response.")

        st.session_state["debug_info"] = "\n".join(debug)

        return data["choices"][0]["message"]["content"]

    except Exception:
        error_text = traceback.format_exc()
        st.session_state["debug_info"] = f"❌ Exception:\n{error_text}"
        return f"❌ Exception contacting OpenAI:\n{error_text}"


# =========================================================
# DEBUG INFO VIEWER
# =========================================================
def get_debug_info():
    return st.session_state.get("debug_info", "No debug info yet.")
