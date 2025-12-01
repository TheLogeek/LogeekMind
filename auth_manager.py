import streamlit as st
from supabase import create_client
import time


# Connect to Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_connection()


def check_username_availability(username):
    """Checks if a username is already taken in the database."""
    try:
        # Query the profiles table
        response = supabase.table("profiles").select("username").eq("username", username).execute()
        # If any data is returned, the username exists
        if response.data:
            return False  # Username taken
        return True  # Username available
    except Exception as e:
        print(f"Error checking username: {e}")
        return False


def sign_up_user(email, password, username, terms_accepted):
    """Signs up a new user with metadata."""
    # 1. Check uniqueness first to save an API call
    if not check_username_availability(username):
        return False, "Username already taken. Please choose another."

    try:
        # 2. Create user in Supabase Auth
        # We pass username and terms status in metadata so the Trigger can grab it
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username,
                    "terms_accepted": terms_accepted,
                    "terms_version": "v1.0"
                }
            }
        })

        if response.user:
            return True, "Account created! Please check your email to confirm."
        else:
            return False, "Signup failed."

    except Exception as e:
        return False, str(e)


def sign_in_user(email, password):

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.user = response.user

        profile_response = supabase.table("profiles").select("*").eq("id", response.user.id).single().execute()
        if profile_response.data:
            st.session_state.user_profile = profile_response.data

        return True, "Login successful!"
    except Exception as e:
        return False, str(e)


def sign_out_user():
    supabase.auth.sign_out()
    for key in ['user', 'user_profile', 'chat_history']:
        if key in st.session_state:
            del st.session_state[key]