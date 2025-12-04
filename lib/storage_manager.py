import json
import io
from datetime import datetime
from supabase import create_client
import streamlit as st


@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_connection()


BUCKET_NAME = "user-files"

import datetime

def now_iso():
    """Return current UTC timestamp in ISO format with Z suffix."""
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"



def _generate_path(username: str, filetype: str, ext: str):
    """Creates a unique path such as: solomon/exam_2025-01-20_10-22.json"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{username}/{filetype}_{timestamp}.{ext}"


def save_text(username: str, content: str, filetype: str = "note"):
    """Save plain text files to Supabase."""
    path = _generate_path(username, filetype, "txt")
    file_data = io.BytesIO(content.encode("utf-8"))

    response = supabase.storage.from_(BUCKET_NAME).upload(
        file=file_data,
        path=path,
        file_options={"content-type": "text/plain", "upsert": "false"}
    )
    return response, path


def save_json(username: str, obj: dict, filetype: str = "data"):
    """Save JSON or complex exam simulator data."""
    path = _generate_path(username, filetype, "json")
    file_data = io.BytesIO(json.dumps(obj).encode("utf-8"))

    response = supabase.storage.from_(BUCKET_NAME).upload(
        file=file_data,
        path=path,
        file_options={"content-type": "application/json", "upsert": "false"}
    )
    return response, path


def save_bytes(username: str, data: bytes, ext: str, filetype: str):
    """Generic function to save raw byte data (audio, images, PDFs, etc.)."""
    path = _generate_path(username, filetype, ext)
    file_data = io.BytesIO(data)

    mimetypes = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "pdf": "application/pdf",
        "txt": "text/plain",
    }
    mimetype = mimetypes.get(ext.lower(), "application/octet-stream")

    response = supabase.storage.from_(BUCKET_NAME).upload(
        file=file_data,
        path=path,
        file_options={"content-type": mimetype, "upsert": "false"}
    )
    return response, path


def list_user_files(username: str):
    """List all files belonging to the user."""
    try:
        response = supabase.storage.from_(BUCKET_NAME).list(path=username)
        return response
    except Exception:
        return []


def get_download_url(path: str):
    """Generate a downloadable public URL."""
    return supabase.storage.from_(BUCKET_NAME).get_public_url(path)


def delete_file(path: str):
    """Delete a file from the bucket."""
    return supabase.storage.from_(BUCKET_NAME).remove(path)

# -----------------------------
# Helpers for "My Library" page
# -----------------------------
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

