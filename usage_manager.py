import streamlit as st
from supabase import create_client


@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def premium_gate(feature_name):

    if 'user' in st.session_state:
        return True

    st.warning(f"🔒 You must be logged in to **{feature_name}**.")
    return False


def check_guest_limit(feature_name, limit=1):

    if 'user' in st.session_state:
        return True

    usage_key = f"usage_count_{feature_name}"

    if usage_key not in st.session_state:
        st.session_state[usage_key] = 0

    if st.session_state[usage_key] >= limit:
        st.warning(f"🔒 You have reached the free limit for **{feature_name}** as a guest.")
        st.info("""Sign up for a free account to use this feature without limits!""")

        return False  # Block access

    st.session_state[usage_key] += 1
    return True

def log_usage(user_id, feature_name, action, metadata=None):
    if metadata is None:
        metadata = {}

    return supabase.table("usage_log").insert({
        "user_id": user_id,
        "feature_name": feature_name,
        "action": action,
        "metadata": metadata
    }).execute()


def log_performance(user_id, feature, score, total_questions, correct_answers, extra=None):
    """
    Logs a user's performance on a feature into the performance_log table.

    Args:
        user_id (str): The user's unique ID.
        feature (str): Name of the feature used (e.g., "Quiz Generator", "Exam Simulator").
        score (int): The score achieved.
        total_questions (int): Total number of questions in the session.
        correct_answers (int): Number of correct answers.
        extra (dict, optional): Any extra data to store.
    """
    supabase.table("performance_log").insert({
        "user_id": user_id,
        "feature": feature,
        "score": score,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "extra": extra or {}
    }).execute()

def get_user_performance(user_id):
    return supabase.table("performance_log") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .execute().data