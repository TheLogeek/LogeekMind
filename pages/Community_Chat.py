import streamlit as st
from supabase import create_client, ClientOptions
import time

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

st.title("LogeekMind Community Chat💬")

with st.sidebar:
    st.write("### Chat Settings")
    username = st.text_input("Enter a Username", key="chat_username")
    group = st.selectbox("Select a Room", ["General Lobby", "Homework Help", "Exam Prep", "Chill Zone"])

if not username:
    st.warning("please enter a username in the sidebar to join the chat.")
    st.stop()

try:
    response = supabase.table("chat_messages").select("*").eq("group_name", group).order("created_at",
                                                                                         desc=True).limit(20).execute()
    messages = response.data[::-1]

except Exception as e:
    st.error(f"Error connecting to chat: {e}")
    messages = []

chat_container = st.container()
with chat_container:
    for msg in messages:
        role = "user" if msg['username'] == username else "assistant"
        with st.chat_message(name=msg['username'], avatar="👨‍🎓" if role == "assistant" else "🙍‍♂️"):
            st.write(f"**{msg['username']}:** {msg['message']}")
            st.caption(msg['created_at'])

prompt = st.chat_input("Say something....")

if prompt:
    new_message = {
        "username": username,
        "message": prompt,
        "group_name": group
    }

    try:
        supabase.table("chat_messages").insert(new_message).execute()
        st.rerun()
    except Exception as e:
        st.error(f"Could not send message: {e}")

if st.button("Refresh Chat"):
    st.rerun()