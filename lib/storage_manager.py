import json
from datetime import datetime
from supabase import create_client
import streamlit as st
import os

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()
BUCKET_NAME = "user-files"


def now_iso():
    """Return current UTC timestamp in ISO format with Z suffix."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _generate_path(username: str, filetype: str, ext: str):
    """Generate unique path like: username/filetype_2025-12-03_10-22.ext"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{username}/{filetype}_{timestamp}.{ext}"


def save_bytes(username: str, local_file_path: str, filetype: str = "file"):
    """
    Upload a local file to Supabase.
    - local_file_path: path to the file on disk
    Returns (response, storage_path)
    """
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(f"{local_file_path} does not exist")

    ext = local_file_path.split(".")[-1]
    path = _generate_path(username, filetype, ext)

    try:
        with open(local_file_path, "rb") as f:
            response = supabase.storage.from_(BUCKET_NAME).upload(
                file=f,
                path=path,
                file_options={"content-type": "application/octet-stream", "upsert": "false"}
            )
        return response, path
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None, None


def save_text(username: str, local_file_path: str, filetype: str = "note"):
    """Upload a local text file"""
    return save_bytes(username, local_file_path, filetype=filetype)


def save_json(username: str, local_file_path: str, filetype: str = "data"):
    """Upload a local JSON file"""
    return save_bytes(username, local_file_path, filetype=filetype)


def list_user_files(username: str):
    """List all files belonging to the user"""
    try:
        resp = supabase.storage.from_(BUCKET_NAME).list(path=username)
        return resp
    except Exception:
        return []


def get_download_url(path: str):
    """Generate a downloadable public URL"""
    return supabase.storage.from_(BUCKET_NAME).get_public_url(path)


def delete_file(path: str):
    """Delete a file from the bucket"""
    return supabase.storage.from_(BUCKET_NAME).remove(path)


def upload_file_to_bucket(user_id: str, file_bytes: bytes, filename: str):
    """
    Wrapper to save a file to the user's folder in the bucket.
    Returns the storage path for DB reference.
    """
    path = f"{user_id}/{filename}"
    return save_bytes(user_id, file_bytes, ext=filename.split(".")[-1], filetype=filename.rsplit(".",1)[0])[1]
    # Returns the path (second item from save_bytes) for creating a content record



def create_content_record(user_id: str, title: str, content_type: str, storage_path: str,
                          filename: str, size_bytes: int, content_json: dict):
    """
    Creates a DB record for the file in your 'user_library' table.
    Adjust table/columns according to your Supabase schema.
    """
    data = {
        "user_id": user_id,
        "title": title,
        "content_type": content_type,
        "storage_path": storage_path,
        "filename": filename,
        "size_bytes": size_bytes,
        "content_json": content_json,
        "created_at": now_iso()
    }
    try:
        supabase.table("user_library").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Failed to create library record: {e}")
        return False