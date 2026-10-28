import os
import streamlit as st

supabase = None
USE_LOCAL_DB = True

try:
    url = None
    key = None
    # Check streamlit secrets
    if hasattr(st, "secrets") and "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    # Check environment variables
    elif os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

    if url and key and "your-supabase" not in url:
        from supabase import create_client, Client
        supabase: Client = create_client(url, key)
        USE_LOCAL_DB = False
except Exception:
    supabase = None
    USE_LOCAL_DB = True


def is_supabase_configured() -> bool:
    return supabase is not None and not USE_LOCAL_DB
