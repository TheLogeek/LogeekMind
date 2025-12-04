import streamlit as st
from lib.storage_manager import list_user_contents, get_content_item, delete_content_item, get_public_url_for_path
from io import BytesIO
from supabase import create_client

st.set_page_config(page_title="My Library", layout="wide")
st.title("📚 My Library")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

if 'user' not in st.session_state or st.session_state.user is None:
    st.info("Please log in to access your library.")
    st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
    st.stop()

user_id = st.session_state.user.id

try:
    items = list_user_contents(user_id)
except Exception as e:
    st.error(f"Failed to fetch library: {e}")
    st.stop()

if not items:
    st.info("Your library is empty. Save generated content from features like the Exam Simulator or Lecture Audio.")
    st.stop()

# Show items grouped
for item in items:
    with st.expander(f"{item.get('title')} — {item.get('filename') or item.get('content_type')} — {item.get('created_at')}", expanded=False):
        st.write(f"**Type:** {item.get('content_type')}")
        st.write(f"**Description:** {item.get('description') or '—'}")
        st.write(f"**Size:** {item.get('size_bytes') or '—'} bytes")
        # options: preview or download
        storage_path = item.get('storage_path')
        if storage_path:
            # generate signed url for preview/download (1 hour)
            try:
                url = get_public_url_for_path("user-files", storage_path, expires_in_seconds=3600)
            except Exception as e:
                url = None
                st.warning("Could not generate preview URL.")
            if item.get('content_type', '').startswith("audio"):
                if url:
                    st.audio(url)
                st.markdown(f"[Download audio]({url})")
            elif item.get('content_type') in ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"):
                if url:
                    st.markdown(f"[Download DOCX]({url})")
                else:
                    st.info("No preview available. Download instead.")
            else:
                # for JSON or text content, show content field
                content_json = item.get('content')
                if content_json:
                    st.json(content_json)
                elif url:
                    st.markdown(f"[Download/View]({url})")
        else:
            if item.get('content'):
                st.json(item.get('content'))

        # Delete action
        if st.button("Delete", key=f"delete_{item.get('id')}"):
            try:
                delete_content_item(item.get('id'), user_id, bucket="user-files")
                st.success("Deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Delete failed: {e}")
