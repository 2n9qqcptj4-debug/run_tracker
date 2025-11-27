import streamlit as st
from openai import OpenAI
from openai import APIConnectionError, RateLimitError, APIError


# ------------------------------------------------------
# GET CLIENT — With full Streamlit-safe validation
# ------------------------------------------------------
def get_client():
    # Detect missing secrets block entirely
    if "OPENAI_API_KEY" not in st.secrets:
        st.error(
            "❌ **OPENAI_API_KEY is missing from Streamlit Secrets.**\n\n"
            "Go to **Manage App → Secrets** and add:\n\n"
            "```toml\n"
            "OPENAI_API_KEY=\"your_actual_api_key_here\"\n"
            "```"
        )
        raise KeyError("Streamlit secrets missing OPENAI_API_KEY")

    key = st.secrets["OPENAI_API_KEY"]

    # Detect empty key
    if not key or key.strip() == "":
        st.error(
            "❌ **Your OPENAI_API_KEY in Streamlit Secrets is empty.**\n\n"
            "Update it in **Manage App → Secrets**."
        )
        raise ValueError("OPENAI_API_KEY exists but is empty.")

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=key)
        return client

    except Exception as e:
        st.error(f"❌ Failed to initialize OpenAI client:\n\n```\n{e}\n```")
        raise


# ------------------------------------------------------
# CALL AI — For chat completion requests
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
        st.error("⚠️ **OpenAI rate limit reached. Try again in a moment.**")
        return "Rate limit reached. Please try again."

    except APIConnectionError:
        st.error("🌐 **Network issue connecting to OpenAI.**")
        return "Connection error. Please try again."

    except APIError as e:
        st.error(f"🔥 **OpenAI internal error:**\n\n```\n{e}\n```")
        return "OpenAI server error."

    except Exception as e:
        st.error(
            f"🚨 **Unexpected error while contacting OpenAI:**\n\n```\n{e}\n```"
        )
        return "Unexpected error contacting AI."


# ------------------------------------------------------
# OPTIONAL: SHORTCUT FOR SYSTEM + USER MESSAGES
# ------------------------------------------------------
def call_ai_system(system_msg: str, user_msg: str) -> str:
    """
    Cleaner interface for prompts using system + user roles.
    """
    try:
        client = get_client()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=2000,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Unexpected AI error:\n\n```\n{e}\n```")
        return "AI error."
