import streamlit as st
from supabase import create_client, Client

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_supabase()

def sign_in_or_sign_up(email, password):
    """
    Tries to sign in. If user doesn't exist, tries to sign up.
    Returns: (success_boolean, message_or_user)
    """
    # 1. Try Login
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            return True, response.user
    except Exception as e:
        # If error is NOT "Invalid login credentials", fail immediately (e.g. network error)
        # Note: Supabase error messages vary, but usually contain specific strings.
        # We proceed to signup attempt if it looks like a missing user or just try anyway.
        pass

    # 2. Try Signup if Login failed
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            # Check if session is present (implies no email confirm needed)
            if response.session:
                return True, response.user
            else:
                return False, "Account created! Please check your email to confirm."
    except Exception as e:
        error_msg = str(e)
        if "User already registered" in error_msg or "already exists" in error_msg:
             return False, "Incorrect password."
        return False, f"Error: {error_msg}"
    
    return False, "Authentication failed."

def get_user_session():
    """Returns the current session user if logged in."""
    # Supabase-py manages session internally mostly, but for Streamlit 
    # we often rely on session_state to track UI state.
    # However, to check if the token is valid:
    user = supabase.auth.get_user()
    return user
