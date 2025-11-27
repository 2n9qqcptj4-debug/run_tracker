import streamlit as st
from openai import OpenAI
from openai import APIConnectionError, RateLimitError, APIError


# ------------------------------------------------------
# GET CLIENT — Streamlit-safe, no proxies
# ------------------------------------------------------
def get_client():
    # Check key existence
    if "OPENAI_API_KEY" not in st.secrets:
        st.error(
            "❌ OPENAI_API_KEY missing in Streamlit Secrets.\n\n"
            "Go to **Manage App → Secrets** and add:\n"
            "```toml\nOPENAI_API_KEY=\"your_key_here\"\n```"
        )
        raise KeyError("Missing OPENAI_API_KEY")

    key = st.secrets["OPENAI_API_KEY"]

    # Check empty key
    if not key or key.strip() == "":
        st.error("❌ OPENAI_API_KEY is empty.")
        raise ValueError("Empty OPENAI_API_KEY")

    try:
        # Initialize official OpenAI client
        client = OpenAI(api_key=key)
        return client

    except Exception as e:
        st.error(f"❌ Failed to initialize OpenAI client:\n\n```\n{e}\n```")
        raise


# ------------------------------------------------------
# CALL AI — Chat Completion Wrapper
# ------------------------------------------------------
def call_ai(prompt: str) -> str:
    try:
        client = get_client()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1400,
            temperature=0.8,
        )

        return response.choices[0].message.content

    except RateLimitError:
        st.error("⚠️ OpenAI rate limit reached. Try again shortly.")
        return "Rate limit reached."

    except APIConnectionError:
        st.error("🌐 Network issue connecting to OpenAI.")
        return "Connection error."

    except APIError as e:
        st.error(f"🔥 OpenAI server error:\n\n```\n{e}\n```")
        return "OpenAI server error."

    except Exception as e:
        st.error(f"🚨 Unexpected AI error:\n\n```\n{e}\n```")
        return "Unexpected error."


# ------------------------------------------------------
# OPTIONAL SYSTEM+USER Prompt Function
# ------------------------------------------------------
def call_ai_system(system_msg: str, user_msg: str) -> str:
    try:
        client = get_client()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        return response.choices[0].message.content

    except Exception as e:
        st.error(f"🚨 AI Error:\n\n```\n{e}\n```")
        return "AI error."
