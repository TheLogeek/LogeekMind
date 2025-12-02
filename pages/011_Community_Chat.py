# chat.py
import streamlit as st
from supabase import create_client
import datetime
import time
from typing import Optional

# ---------------------------
# CONFIG / CONNECTION
# ---------------------------
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# ---------------------------
# HELPERS: session / user
# ---------------------------
def get_current_username() -> Optional[str]:
    """
    Reads username from the session structure used at sign-in:
        st.session_state.user_profile['username']
    Returns None for guests.
    """
    if "user_profile" in st.session_state and st.session_state.user_profile:
        return st.session_state.user_profile.get("username")
    return None

# ---------------------------
# UI THEME (neon / blue)
# small CSS — tweak as desired
# ---------------------------
THEME_CSS = """
<style>
/* page background and fonts */
[data-testid="stAppViewContainer"] { background: linear-gradient(180deg,#061025 0%, #07152b 60%); }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#061325 0%, #071a2f 60%); color: #dbe9ff; }

/* message bubble */
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

/* incoming / others */
.logeek-msg.incoming { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.03); }

/* outgoing / me */
.logeek-msg.me {
    background: linear-gradient(90deg, rgba(6,134,255,0.12), rgba(4,197,255,0.08));
    border: 1px solid rgba(4,197,255,0.18);
    margin-left: auto;
}

/* username pill */
.user-pill { font-weight:600; color:#bfe8ff; font-size:12px; margin-bottom:4px; }

/* caption */
.msg-caption { font-size:11px; color: #9fbfdb; margin-top:4px; }

/* reaction chip */
.react-chip {
    display:inline-block;
    padding:4px 8px;
    margin-right:6px;
    border-radius:999px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.02);
    font-size:13px;
}

/* online pill */
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

/* typing ribbon */
.typing-ribbon {
    color: #cfeeff;
    font-style: italic;
    margin-top: 8px;
    font-size:13px;
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ---------------------------
# PRESENCE / TYPING / REACTIONS HELPERS
# ---------------------------
def now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def safe_from_iso(s: str) -> datetime.datetime:
    # accepts strings with and without trailing Z
    if s is None:
        return datetime.datetime.utcfromtimestamp(0)
    if s.endswith("Z"):
        s = s[:-1]
    return datetime.datetime.fromisoformat(s)

# Presence: upsert user's last ping
def upsert_presence(username: str):
    if not username:
        return
    supabase.table("online_users").upsert({
        "username": username,
        "last_ping": now_iso()
    }).execute()

# Get online users (last_ping within threshold_seconds)
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

# Typing status
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
    # consider typing only if updated in last 10s
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

# reactions helpers
def add_reaction(message_id: str, username: str, emoji: str):
    if not username:
        return
    supabase.table("message_reactions").insert({
        "message_id": message_id,
        "username": username,
        "emoji": emoji,
        "created_at": now_iso()
    }).execute()

def get_reactions_for_message(message_id: str):
    resp = supabase.table("message_reactions") \
        .select("emoji, count:count") \
        .eq("message_id", message_id) \
        .group("emoji") \
        .execute()
    # Some Supabase clients/drivers don't support group in select like this;
    # fallback to fetching all and counting in Python:
    if not resp.data:
        # fallback
        resp2 = supabase.table("message_reactions").select("*").eq("message_id", message_id).execute()
        data = resp2.data or []
        counts = {}
        for r in data:
            e = r.get("emoji")
            counts[e] = counts.get(e, 0) + 1
        return counts
    else:
        # if response.data present, try to convert
        try:
            counts = {}
            for r in resp.data:
                # expect structure like {"emoji":"❤️","count":3}
                emoji = r.get("emoji")
                cnt = r.get("count") or r.get("count:count") or 0
                counts[emoji] = cnt
            return counts
        except Exception:
            return {}

# ---------------------------
# DISPLAY: Online users (sidebar)
# ---------------------------
@st.fragment(run_every=5)
def show_online_users_component():
    online = get_online_users()
    st.write("### 👥 Online")
    if online:
        for u in online:
            st.markdown(f"<div class='online-pill'>{u}</div>", unsafe_allow_html=True)
    else:
        st.write("No one is online right now.")

# ---------------------------
# DISPLAY: Typing indicator (below chat)
# ---------------------------
@st.fragment(run_every=2)
def show_typing_indicator_component(group_name: str, current_username: Optional[str]):
    typing = get_typing_users(group_name, exclude_username=current_username)
    if typing:
        text = "💬 " + ", ".join(typing) + " typing..."
        st.markdown(f"<div class='typing-ribbon'>{text}</div>", unsafe_allow_html=True)

# ---------------------------
# MAIN: display messages (real-time fragment)
# ---------------------------
@st.fragment(run_every=3)
def display_messages(group_name: str, current_user: Optional[str]):
    """
    Fetches last 20 messages for group_name, orders ascending for display.
    Renders messages with reaction buttons and delete for owners.
    """
    try:
        resp = supabase.table("chat_messages") \
            .select("*") \
            .eq("group_name", group_name) \
            .order("created_at", desc=True) \
            .limit(20) \
            .execute()

        rows = resp.data or []
        # rows are newest->oldest; reverse for display oldest->newest
        messages = rows[::-1]

        if not messages:
            st.info("No messages yet. Be the first to say hi!")
            return

        # chat container
        chat_container = st.container()
        with chat_container:
            for msg in messages:
                msg_id = msg.get("id")
                author = msg.get("username") or "Unknown"
                text = msg.get("message") or ""
                created_at = msg.get("created_at") or ""
                is_me = (author == current_user)

                # style class
                cls = "logeek-msg me" if is_me else "logeek-msg incoming"
                username_pill = f"<div class='user-pill'>{author}</div>"
                timestamp = f"<div class='msg-caption'>{created_at}</div>"

                # message HTML wrapper
                st.markdown(
                    f"""
                    <div style="display:flex; flex-direction:column; gap:4px;">
                        {username_pill}
                        <div class="{cls}">{st.session_state.get('emoji_prefix','')}{text}</div>
                        {timestamp}
                    </div>
                    """, unsafe_allow_html=True)

                # reactions display
                counts = get_reactions_for_message(msg_id)
                if counts:
                    chips = " ".join([f"<span class='react-chip'>{e} {c}</span>" for e, c in counts.items()])
                    st.markdown(chips, unsafe_allow_html=True)

                # Reaction buttons + delete button (in columns)
                cols = st.columns([1,1,1,1,1])
                emojis = ["❤️", "👍", "😂", "🔥"]
                for i, e in enumerate(emojis):
                    key = f"react_{msg_id}_{e}"
                    if cols[i].button(e, key=key):
                        # non-blocking: add reaction for current user; if not logged in, ignore
                        current_username = get_current_username()
                        if current_username:
                            add_reaction(msg_id, current_username, e)
                            st.experimental_rerun()
                        else:
                            st.warning("Sign in to react to messages.")

                # Delete
                if is_me:
                    if cols[-1].button("🗑 Delete", key=f"del_{msg_id}"):
                        # delete message by id
                        supabase.table("chat_messages").delete().eq("id", msg_id).execute()
                        # also remove reactions tied to it (optional)
                        supabase.table("message_reactions").delete().eq("message_id", msg_id).execute()
                        st.experimental_rerun()

    except Exception as err:
        st.error(f"Error connecting to chat: {err}")

# ---------------------------
# APP LAYOUT / SIDEBAR
# ---------------------------
st.title("LogeekMind Community Chat 💬")

with st.sidebar:
    st.write("### Chat Settings")
    current_username = get_current_username()
    is_logged_in = current_username is not None

    if is_logged_in:
        st.success(f"Signed in as: **{current_username}**")
    else:
        st.warning("You are currently viewing as a **Guest**.")

    # Room choice
    group = st.selectbox("Select a Room", ["General Lobby", "Homework Help", "Exam Prep", "Chill Zone"])

    # Render online users within sidebar
    show_online_users_component()

# persist these globals in session_state so fragments can access them across runs
if "current_group" not in st.session_state:
    st.session_state.current_group = group
else:
    # update if user changed selection
    st.session_state.current_group = group

# ---------------------------
# PRESENCE: ping if logged in
# ---------------------------
# Upsert presence on each run (and via fragment)
if is_logged_in:
    upsert_presence(current_username)

# Also ensure presence is updated periodically in a fragment
@st.fragment(run_every=10)
def presence_ping_fragment(username):
    if username:
        upsert_presence(username)

# run the fragment (it is safe to call)
presence_ping_fragment(current_username)

# ---------------------------
# MESSAGE DISPLAY (everyone)
# ---------------------------
display_messages(st.session_state.current_group, current_username)

# Show typing indicator below messages
show_typing_indicator_component(st.session_state.current_group, current_username)

# ---------------------------
# MESSAGE INPUT (only for logged-in users)
# ---------------------------
# 'Guests can view but not send'
if is_logged_in:
    # Indicate typing when input area is present. We'll set typing True,
    # then set False after send — this is a simple reasonable approximation.
    set_typing_status(current_username, st.session_state.current_group, True)

    prompt = st.chat_input("Say something... (press Enter to send)")

    if prompt:
        # Insert message
        new_message = {
            "username": current_username,
            "message": prompt,
            "group_name": st.session_state.current_group,
            "created_at": now_iso()
        }
        try:
            supabase.table("chat_messages").insert(new_message).execute()
            # Clear typing flag
            set_typing_status(current_username, st.session_state.current_group, False)
            # force UI update
            st.rerun()
        except Exception as e:
            st.error(f"Could not send message: {e}")
else:
    # Guest: disabled chat_input with clear hint
    st.chat_input("Sign in to join the conversation.", disabled=True)
    # Also ensure we clear any typing flags for guests
    # (If previously logged-in user left, we shouldn't be marked typing)
    guest_username = get_current_username()
    if not guest_username:
        # best-effort: clear any stale typing statuses for this session
        try:
            # We cannot identify which to clear reliably; but leave as is.
            pass
        except Exception:
            pass

# Manual refresh (optional)
if st.button("Refresh Chat"):
    st.rerun()
