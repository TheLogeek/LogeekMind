import streamlit as st
import pandas as pd
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import time

# --- CONFIG ---
ADMIN_ID = st.secrets["ADMIN_ID"]

# --- INITIALIZE SUPABASE ---
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- CHECK ADMIN ACCESS ---
if 'user' in st.session_state:
    user_id = st.session_state.user.id
else:
    st.warning("Log in to view this dashboard.")
    st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
    st.stop()

if user_id != ADMIN_ID:
    st.error("❌ You are not authorised to access this page.")
    st.stop()

st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🛡️ LogeekMind Admin Dashboard")

# AUTO REFRESH
st_autorefresh(interval=60000, key="admin_refresh")  # refresh every 60 seconds

# FETCH DATA FROM SUPABASE
def get_total_users():
    response = supabase.table("profiles").select("*").execute()
    return len(response.data) if response.data else 0

def get_active_users():
    response = supabase.table("usage_log").select("username, created_at").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert(None)
        last_24h = pd.Timestamp.now() - pd.Timedelta(days=1)
        return df[df['created_at'] >= last_24h]['username'].nunique()
    return 0

def get_feature_usage():
    response = supabase.table("usage_log").select("feature_name").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df = df.groupby("feature_name").size().reset_index(name="Usage")
        return df
    return pd.DataFrame(columns=["feature_name", "Usage"])

def get_top_users(n=5):
    response = supabase.table("usage_log").select("username").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df = df.groupby("username").size().reset_index(name="usage_count").sort_values("usage_count", ascending=False)
        return df.head(n)
    return pd.DataFrame(columns=["username", "usage_count"])

def get_daily_activity(days=7):
    response = supabase.table("usage_log").select("created_at").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert(None).dt.date
        recent_days = pd.date_range(end=pd.Timestamp.now().date(), periods=days)
        activity = df[df['created_at'].isin(recent_days)].groupby('created_at').size()
        activity = activity.reindex(recent_days.date, fill_value=0)
        return activity
    return pd.Series([0]*days, index=pd.date_range(end=pd.Timestamp.now().date(), periods=days).date)

# --- KPI METRICS ---
total_users = get_total_users()
active_users = get_active_users()
top_user_df = get_top_users(1)
top_user = top_user_df.iloc[0]['username'] if not top_user_df.empty else "N/A"

col1, col2, col3 = st.columns(3)
col1.metric("Total Users", total_users)
col2.metric("Active Users (24h)", active_users)
col3.metric("Top User (by usage)", top_user)

st.markdown("---")

# --- FEATURE USAGE CHARTS WITH INTERACTIVITY ---
feature_df = get_feature_usage()
if not feature_df.empty:
    # Initialize selected_feature in session state
    if "selected_feature" not in st.session_state:
        st.session_state.selected_feature = None

    st.subheader("Feature Usage (Interactive)")

    # Bar Chart
    bar_fig = px.bar(feature_df, x="feature_name", y="Usage", text="Usage")
    bar_fig.update_traces(marker_color='skyblue')
    bar_fig.update_layout(clickmode='event+select', title="Click a bar to filter table below")
    bar_clicked = st.plotly_chart(bar_fig, use_container_width=True)

    # Pie Chart
    pie_fig = px.pie(feature_df, values="Usage", names="feature_name", title="Feature Usage Pie Chart")
    pie_fig.update_traces(textinfo='percent+label')
    pie_clicked = st.plotly_chart(pie_fig, use_container_width=True)

    # Capture clicks via Plotly events
    selected_feature = st.session_state.get("selected_feature")
    if bar_fig and st.session_state.get("selected_feature") is not None:
        selected_feature = st.session_state.selected_feature
    st.write(f"🔹 Currently filtering by feature: {selected_feature or 'None'}")

else:
    st.info("No feature usage data yet.")

# --- DAILY ACTIVITY TREND ---
st.subheader("Daily Activity (Last 7 Days)")
daily_activity = get_daily_activity(7)
st.line_chart(daily_activity)

# --- TOP USERS TABLE ---
top_users_df = get_top_users(10)
if not top_users_df.empty:
    st.subheader("Top 10 Users by Feature Usage")
    st.dataframe(top_users_df)
else:
    st.info("No user usage data yet.")

# --- SEARCHABLE USAGE TABLE ---
st.subheader("All User Activity")
all_usage_resp = supabase.table("usage_log").select("*").execute()
if all_usage_resp.data:
    all_usage_df = pd.DataFrame(all_usage_resp.data)
    all_usage_df['created_at'] = pd.to_datetime(all_usage_df['created_at']).dt.tz_convert(None)

    # Filters
    search_user = st.text_input("Search by User name")
    search_feature = st.text_input("Search by Feature Name", value=st.session_state.get("selected_feature") or "")

    filtered_df = all_usage_df.copy()
    if search_user:
        filtered_df = filtered_df[filtered_df['username'].str.contains(search_user)]
    if search_feature:
        filtered_df = filtered_df[filtered_df['feature_name'].str.contains(search_feature)]

    st.dataframe(filtered_df)
else:
    st.info("No user activity logs yet.")

st.markdown("---")
st.caption(f"Last refreshed: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
