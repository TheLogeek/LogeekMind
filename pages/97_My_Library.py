import streamlit as st
from lib.storage_manager import list_user_files, get_download_url, delete_file
from supabase import create_client

st.set_page_config(page_title="My Library", layout="wide")
st.title("📚 My Library")

# ---------------------------
# Supabase connection
# ---------------------------
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# ---------------------------
# Check login
# ---------------------------
if 'user' not in st.session_state or st.session_state.user is None:
    st.info("Please log in to access your library.")
    st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
    st.stop()

username = st.session_state.user.username

# ---------------------------
# Fetch user files
# ---------------------------
try:
    items = list_user_files(username)
except Exception as e:
    st.error(f"Failed to fetch library: {e}")
    st.stop()

if not items:
    st.info("Your library is empty. Save generated content from features like the Exam Simulator or Lecture Audio.")
    st.stop()

# ---------------------------
# Display user files
# ---------------------------
for item in items:
    file_path = item.get("name")  # Supabase returns {"name": "username/file.ext", ...}
    created_at = item.get("created_at") or "—"
    filename = file_path.split("/")[-1] if file_path else "Unknown"

    with st.expander(f"{filename} — {created_at}", expanded=False):
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        url = None
        try:
            url = get_download_url(file_path)
        except Exception:
            st.warning("Could not generate download URL.")

        # Preview depending on type
        if ext in ("mp3", "wav") and url:
            st.audio(url)
            st.markdown(f"[Download audio]({url})")
        elif ext in ("pdf",) and url:
            st.markdown(f"[Download PDF]({url})")
        elif ext in ("png", "jpg", "jpeg") and url:
            st.image(url)
            st.markdown(f"[Download Image]({url})")
        elif ext in ("txt",):
            # Try to fetch content as text
            try:
                r = supabase.storage.from_("user_library").download(file_path)
                text = r.decode("utf-8")
                st.text_area("Content", text, height=200)
                st.markdown(f"[Download Text File]({url})")
            except Exception:
                st.markdown(f"[Download Text File]({url})")
        elif ext in ("json",):
            try:
                r = supabase.storage.from_("user_library").download(file_path)
                import json
                data = json.loads(r.decode("utf-8"))
                st.json(data)
                st.markdown(f"[Download JSON]({url})")
            except Exception:
                st.markdown(f"[Download JSON]({url})")
        else:
            if url:
                st.markdown(f"[Download/View File]({url})")
            else:
                st.info("No preview available.")

        # Delete button
        if st.button("Delete", key=f"delete_{filename}"):
            try:
                delete_file(file_path)
                st.success("Deleted successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Delete failed: {e}")
