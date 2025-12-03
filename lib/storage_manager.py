import time
import io
import streamlit as st
from supabase import create_client
from typing import Optional, Dict

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()


def log(msg: str):
    print(f"[STORAGE_MANAGER] {msg}")


# ----------------------------------------
# SAFE WRAPPER
# ----------------------------------------
def safe_try(func):
    def wrapper(*args, **kwargs):
        try:
            log(f"Calling {func.__name__}()")
            result = func(*args, **kwargs)

            if result is None:
                raise Exception(f"{func.__name__} returned None")

            log(f"{func.__name__} SUCCESS → {result}")
            return result

        except Exception as e:
            log(f"{func.__name__} ERROR → {e}")
            raise Exception(f"{func.__name__} failed: {str(e)}")
    return wrapper


# ----------------------------------------
# UPLOAD FILE
# ----------------------------------------
@safe_try
def upload_file_to_bucket(bucket: str, user_id: str, file_bytes: bytes, filename: str):
    ts = int(time.time())
    safe_filename = filename.replace(" ", "_")
    path = f"{user_id}/{ts}_{safe_filename}"

    log(f"Uploading to bucket={bucket}, path={path}")

    res = supabase.storage.from_(bucket).upload(
        path,
        io.BytesIO(file_bytes),
        {"cacheControl": "3600", "upsert": False}
    )

    if isinstance(res, dict) and res.get("error"):
        raise Exception(res["error"])

    log(f"Upload successful → {path}")
    return path


# ----------------------------------------
# CREATE RECORD
# ----------------------------------------
@safe_try
def create_content_record(
    user_id: str,
    title: str,
    content_type: str,
    storage_path: Optional[str] = None,
    filename: Optional[str] = None,
    content_json: Optional[Dict] = None,
    size_bytes: Optional[int] = None,
) -> Dict:

    payload = {
        "user_id": user_id,
        "title": title,
        "content_type": content_type,
        "storage_path": storage_path,
        "filename": filename,
        "content": content_json,
        "size_bytes": size_bytes
    }

    log(f"INSERT PAYLOAD → {payload}")

    res = supabase.table("user_contents").insert(payload).select("*").execute()

    if not hasattr(res, "data") or not isinstance(res.data, list):
        raise Exception("Invalid insert response")

    if len(res.data) == 0:
        raise Exception("Insert returned empty data list")

    log("DB insert successful")
    return res.data[0]


# ----------------------------------------
# LIST ITEMS
# ----------------------------------------
@safe_try
def list_user_contents(user_id: str, limit: int = 100) -> list:
    log(f"Fetching items for user={user_id}")

    res = (
        supabase.table("user_contents")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    if not hasattr(res, "data"):
        raise Exception("Invalid response structure")

    return res.data or []


# ----------------------------------------
# GET ITEM
# ----------------------------------------
@safe_try
def get_content_item(item_id: str, user_id: str) -> Optional[dict]:
    res = (
        supabase.table("user_contents")
        .select("*")
        .eq("id", item_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not hasattr(res, "data"):
        return None

    return res.data


# ----------------------------------------
# DELETE ITEM
# ----------------------------------------
@safe_try
def delete_content_item(item_id: str, user_id: str, bucket: Optional[str] = None) -> bool:
    item = get_content_item(item_id, user_id)
    if not item:
        raise Exception("Item not found")

    storage_path = item.get("storage_path")

    res = supabase.table("user_contents").delete().eq("id", item_id).execute()

    if not hasattr(res, "data"):
        raise Exception("Delete response malformed")

    if storage_path and bucket:
        log(f"Deleting file from bucket={bucket}, path={storage_path}")
        del_res = supabase.storage.from_(bucket).remove([storage_path])

        if isinstance(del_res, dict) and del_res.get("error"):
            print("Warning: file deletion error:", del_res["error"])

    return True


# ----------------------------------------
# SIGNED URL
# ----------------------------------------
@safe_try
def get_public_url_for_path(bucket: str, storage_path: str, expires_in_seconds: int = 3600) -> str:
    signed = supabase.storage.from_(bucket).create_signed_url(storage_path, expires_in_seconds)

    if isinstance(signed, dict) and signed.get("signedURL"):
        return signed["signedURL"]

    public = supabase.storage.from_(bucket).get_public_url(storage_path)
    if isinstance(public, dict):
        return public.get("publicURL", "")

    return ""
