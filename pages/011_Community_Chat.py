import streamlit as st
from supabase import create_client
import time

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# Extract logged-in username from session
def get_current_username():
    if "user_profile" in st.session_state and st.session_state.user_profile:
        return st.session_state.user_profile.get("username", None)
    return None


@st.fragment(run_every=3)
def display_messages(group_name, current_user):
    try:
        response = supabase.table("chat_messages") \
            .select("*") \
            .eq("group_name", group_name) \
            .order("created_at", desc=True) \
            .limit(20) \
            .execute()

        messages = response.data[::-1]

        if not messages:
            st.info("No messages yet. Be the first to say hi!")
            return

        chat_container = st.container()
        with chat_container:
            for msg in messages:
                role = "user" if msg["username"] == current_user else "assistant"
                with st.chat_message(name=msg["username"], avatar="👨‍🎓" if role == "assistant" else "🙍‍♂️"):
                    st.write(f"**{msg['username']}:** {msg['message']}")
                    st.caption(msg["created_at"])

    except Exception as err:
        st.error(f"Error connecting to chat: {err}")


supabase = init_connection()

st.title("LogeekMind Community Chat 💬")

with st.sidebar:
    st.write("### Chat Settings")

    current_username = get_current_username()
    is_logged_in = current_username is not None

    if is_logged_in:
        st.success(f"Signed in as: **{current_username}**")
    else:
        st.warning("You are currently viewing as a **Guest**.")

    group = st.selectbox(
        "Select a Room",
        ["General Lobby", "Homework Help", "Exam Prep", "Chill Zone"]
    )

# MESSAGE DISPLAY
display_messages(group, current_username)


# MESSAGE INPUT SECTION
if is_logged_in:

    prompt = st.chat_input("Say something...")

    if prompt:
        new_message = {
            "username": current_username,
            "message": prompt,
            "group_name": group
        }

        try:
            supabase.table("chat_messages").insert(new_message).execute()
            st.rerun()

        except Exception as e:
            st.error(f"Could not send message: {e}")

else:
    st.chat_input("You must sign in to send messages.", disabled=True)


# Manual refresh button
if st.button("Refresh Chat"):
    st.rerun()
