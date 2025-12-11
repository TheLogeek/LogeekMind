import streamlit as st
from supabase import create_client
import time
from streamlit_cookies_controller import CookieController


# Connect to Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_connection()
controller = CookieController()


def check_username_availability(username):
    try:
        response = supabase.table("profiles").select("username").eq("username", username).execute()
        if response.data:
            return False  # Username taken
        return True  # Username available
    except Exception as e:
        print(f"Error checking username: {e}")
        return False


def sign_up_user(email, password, username, terms_accepted):
    if not check_username_availability(username):
        return False, "Username already taken. Please choose another."

    try:
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
            return True, "Account created! Please proceed to login."
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

        # Load profile
        profile_response = supabase.table("profiles").select("*").eq("id", response.user.id).single().execute()
        if profile_response.data:
            st.session_state.user_profile = profile_response.data

        return True, "Login successful!"

    except Exception as e:
        return False, str(e)

#AUTH_FILE = "auth.txt"

def save_auth(email, password):
    controller.set("auth_email", email)
    controller.set("auth_password", password)

def get_saved_auth():
    email = controller.get("auth_email")
    password = controller.get("auth_password")
    return email, password


def try_auto_login():
    saved_email, saved_password = get_saved_auth()
    if saved_email and saved_password:
        success, msg = sign_in_user(saved_email, saved_password)
        if success:
            pass
        else:
            pass


def sign_out_user():
    supabase.auth.sign_out()

    for key in ['user', 'user_profile', 'chat_history']:
        if key in st.session_state:
            del st.session_state[key]

    try:
        controller.remove('auth_email')
        controller.remove('auth_password')
    except:
        pass