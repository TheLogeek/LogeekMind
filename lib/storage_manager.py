import time
import io
import streamlit as st
import base64
from supabase import create_client
from typing import Optional, Dict, Any

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def upload_file_to_bucket(bucket: str, user_id: str, file_bytes: bytes, filename: str) -> str:
    """
    Uploads bytes to Supabase Storage under path: <user_id>/<timestamp>_<filename>
    Returns: storage_path (string). Raises exceptions on error.
    """
    ts = int(time.time())
    safe_filename = filename.replace(" ", "_")
    path = f"{user_id}/{ts}_{safe_filename}"
    # Upload
    res = supabase.storage.from_(bucket).upload(path, io.BytesIO(file_bytes), {'cacheControl': '3600', 'upsert': False})
    if res.get('error'):
        raise Exception(res['error'])
    # Return path; use this to create public/private URLs later
    return path


def create_content_record(user_id: str, title: str, content_type: str,
                          storage_path: Optional[str]=None, filename: Optional[str]=None,
                          content_json: Optional[Dict]=None, size_bytes: Optional[int]=None) -> Dict:
    """
    Inserts a row into user_contents and returns the inserted row.
    """
    payload = {
        "user_id": user_id,
        "title": title,
        "content_type": content_type,
        "storage_path": storage_path,
        "filename": filename,
        "content": content_json,
        "size_bytes": size_bytes
    }
    res = supabase.table("user_contents").insert(payload).select("*").execute()
    if res.error:
        raise Exception(res.error.message if hasattr(res.error, 'message') else res.error)
    # Supabase returns .data as list
    return res.data[0]


def list_user_contents(user_id: str, limit: int = 100) -> list:
    """
    Returns list of items for a user, newest first.
    """
    res = supabase.table("user_contents").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    if res.error:
        raise Exception(res.error.message if hasattr(res.error, 'message') else res.error)
    return res.data or []


def get_content_item(item_id: str, user_id: str) -> Optional[dict]:
    res = supabase.table("user_contents").select("*").eq("id", item_id).eq("user_id", user_id).single().execute()
    if res.error:
        # return None if not found or unauthorized
        return None
    return res.data


def delete_content_item(item_id: str, user_id: str, bucket: Optional[str]=None) -> bool:
    """
    Deletes the metadata row; optionally removes the file from storage if storage_path exists and bucket provided.
    Returns True on success.
    """
    item = get_content_item(item_id, user_id)
    if not item:
        raise Exception("Item not found or you don't have permission.")

    storage_path = item.get("storage_path")
    # delete metadata row
    res = supabase.table("user_contents").delete().eq("id", item_id).execute()
    if res.error:
        raise Exception(res.error)
    # delete file too if requested
    if storage_path and bucket:
        del_res = supabase.storage.from_(bucket).remove([storage_path])
        if del_res.get("error"):
            # log but don't fail hard
            print("Warning: file delete returned error:", del_res)
    return True


def get_public_url_for_path(bucket: str, storage_path: str, expires_in_seconds: int = 3600) -> str:
    # prefer signed url for private buckets
    signed = supabase.storage.from_(bucket).create_signed_url(storage_path, expires_in_seconds)
    if signed and signed.get("signedURL"):
        return signed["signedURL"]
    # fallback to public
    public = supabase.storage.from_(bucket).get_public_url(storage_path)
    return public.get("publicURL") or ""
