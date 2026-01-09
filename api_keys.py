import streamlit as st
import os

def get_secret(key_name, section="general"):
    """
    Attempts to retrieve a secret from Streamlit secrets, then environment variables.
    """
    # 1. Try st.secrets
    try:
        # Check if keys are directly at root or under a section
        if key_name in st.secrets:
            return st.secrets[key_name]
        elif section in st.secrets and key_name in st.secrets[section]:
            return st.secrets[section][key_name]
    except FileNotFoundError:
        pass # secrets.toml might not exist if running raw python script (not streamlit)
    
    # 2. Try OS Environment Variable
    if key_name in os.environ:
        return os.environ[key_name]
        
    return ""

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")

# Gmail Configuration
EMAIL_SENDER = get_secret("EMAIL_SENDER")
EMAIL_PASSWORD = get_secret("EMAIL_PASSWORD")
