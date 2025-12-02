import streamlit as st
from supabase import create_client
import datetime
import time
from typing import Optional

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def get_current_username() -> Optional[str]:
    """
    Reads username from the session structure used at sign-in:
        st.session_state.user_profile['username']
    Returns None for guests.
    """
    if "user_profile" in st.session_state and st.session_state.user_profile:
        return st.session_state.user_profile.get("username")
    return None

# ui theme
THEME_CSS = """
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(180deg,#061025 0%, #07152b 60%); }

.logeek-msg {
    padding: .6rem .8rem;
    border-radius: 12px;
    margin-bottom: .35rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    font-size: 14px;
    color: #e9f2ff;
    max-width: 78%;
    line-height:1.3;
}

.logeek-msg.incoming { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.03); }
.logeek-msg.me {
    background: linear-gradient(90deg, rgba(6,134,255,0.12), rgba(4,197,255,0.08));
    border: 1px solid rgba(4,197,255,0.18);
    margin-left: auto;
}

.user-pill { font-weight:600; color:#bfe8ff; font-size:12px; margin-bottom:4px; }
.msg-caption { font-size:11px; color: #9fbfdb; margin-top:4px; }

.online-pill {
    display:inline-block;
    margin: 4px 2px;
    padding: 6px 10px;
    border-radius: 999px;
    background: linear-gradient(90deg,#05a3ff, #002bff);
    color: white;
    font-weight:600;
    box-shadow: 0 2px 6px rgba(0,0,0,0.45);
    font-size:13px;
}

.typing-ribbon {
    color: #cfeeff;
    font-style: italic;
    margin-top: 8px;
    font-size:13px;
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

def now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def safe_from_iso(s: str) -> datetime.datetime:
    if s is None:
        return datetime.datetime.utcfromtimestamp(0)
    if s.endswith("Z"):
        s = s[:-1]
    return datetime.datetime.fromisoformat(s)

def upsert_presence(username: str):
    if not username:
        return
    supabase.table("online_users").upsert({
        "username": username,
        "last_ping": now_iso()
    }).execute()

def get_online_users(threshold_seconds: int = 20):
    resp = supabase.table("online_users").select("*").execute()
    data = resp.data or []
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(seconds=threshold_seconds)
    online = []
    for r in data:
        try:
            lp = safe_from_iso(r.get("last_ping"))
            if lp > cutoff:
                online.append(r.get("username"))
        except Exception:
            continue
    return sorted(list(set(online)))

def set_typing_status(username: str, group_name: str, is_typing: bool):
    if not username:
        return
    supabase.table("typing_status").upsert({
        "username": username,
        "group_name": group_name,
        "is_typing": is_typing,
        "updated_at": now_iso()
    }).execute()

def get_typing_users(group_name: str, exclude_username: Optional[str] = None):
    resp = supabase.table("typing_status").select("*").eq("group_name", group_name).execute()
    data = resp.data or []
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
    out = []
    for r in data:
        try:
            ua = safe_from_iso(r.get("updated_at"))
            if ua > cutoff and r.get("is_typing"):
                uname = r.get("username")
                if uname and uname != exclude_username:
                    out.append(uname)
        except Exception:
            continue
    return list(set(out))

# Online users (sidebar)
@st.fragment(run_every=5)
def show_online_users_component():
    online = get_online_users()
    st.write("### 👥 Online")
    if online:
        for u in online:
            st.markdown(f"<div class='online-pill'>{u}</div>", unsafe_allow_html=True)
    else:
        st.write("No one is online right now.")

# Typing indicator
@st.fragment(run_every=2)
def show_typing_indicator_component(group_name: str, current_username: Optional[str]):
    typing = get_typing_users(group_name, exclude_username=current_username)
    if typing:
        text = "💬 " + ", ".join(typing) + " typing..."
        st.markdown(f"<div class='typing-ribbon'>{text}</div>", unsafe_allow_html=True)


@st.fragment(run_every=3)
def display_messages(group_name: str, current_user: Optional[str]):
    try:
        resp = supabase.table("chat_messages") \
            .select("*") \
            .eq("group_name", group_name) \
            .order("created_at", desc=True) \
            .limit(20) \
            .execute()

        rows = resp.data or []
        messages = rows[::-1]

        if not messages:
            st.info("No messages yet. Be the first to say hi!")
            return

        chat_container = st.container()
        with chat_container:
            for msg in messages:
                msg_id = msg.get("id")
                author = msg.get("username") or "Unknown"
                text = msg.get("message") or ""
                created_at = msg.get("created_at") or ""
                is_me = (author == current_user)

                cls = "logeek-msg me" if is_me else "logeek-msg incoming"

                st.markdown(
                    f"""
                    <div style="display:flex; flex-direction:column; gap:4px;">
                        <div class='user-pill'>{author}</div>
                        <div class="{cls}">{text}</div>
                        <div class='msg-caption'>{created_at}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if is_me:
                    if st.button("🗑 Delete", key=f"del_{msg_id}"):
                        supabase.table("chat_messages").delete().eq("id", msg_id).execute()
                        st.rerun()

    except Exception as err:
        st.error(f"Error connecting to chat: {err}")

# layout
st.title("LogeekMind Community Chat 💬")

with st.sidebar:
    st.write("### Chat Settings")
    current_username = get_current_username()
    is_logged_in = current_username is not None

    if is_logged_in:
        st.success(f"Signed in as: **{current_username}**")
    else:
        st.warning("You are currently viewing as a **Guest**.")

    group = st.selectbox("Select a Room", ["General Lobby", "Homework Help", "Exam Prep", "Chill Zone"])
    show_online_users_component()

if "current_group" not in st.session_state:
    st.session_state.current_group = group
else:
    st.session_state.current_group = group


if is_logged_in:
    upsert_presence(current_username)

@st.fragment(run_every=10)
def presence_ping_fragment(username):
    if username:
        upsert_presence(username)

presence_ping_fragment(current_username)


display_messages(st.session_state.current_group, current_username)

show_typing_indicator_component(st.session_state.current_group, current_username)

if is_logged_in:
    set_typing_status(current_username, st.session_state.current_group, True)

    prompt = st.chat_input("Say something... (press Enter to send)")

    if prompt:
        new_message = {
            "username": current_username,
            "message": prompt,
            "group_name": st.session_state.current_group,
            "created_at": now_iso()
        }
        try:
            supabase.table("chat_messages").insert(new_message).execute()
            set_typing_status(current_username, st.session_state.current_group, False)
            st.rerun()
        except Exception as e:
            st.error(f"Could not send message: {e}")
else:
    st.chat_input("Sign in to join the conversation.", disabled=True)

if st.button("Refresh Chat"):
    st.rerun()
