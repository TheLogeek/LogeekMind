import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import usage_manager as um

st.set_page_config(page_title="Your Performance Dashboard", layout="wide")
st.title("📊 Your Performance Dashboard")

# Check if user is logged in
if 'user' not in st.session_state:
    st.warning("Please log in to view your dashboard.")
    st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
    st.stop()

user_id = st.session_state.user.id

# Fetch user performance data
data = um.get_user_performance(user_id)

if not data:
    st.info("No performance data available yet. Use the Exam Simulator or Quiz Generator.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(data)

# Ensure correct types
df["score"] = pd.to_numeric(df.get("score", 0), errors="coerce")
df["total"] = pd.to_numeric(df.get("total_questions", 0), errors="coerce")
df["percentage"] = pd.to_numeric((df.get("score", 0) / (df.get("total_questions", 0)) * 100), errors="coerce")
df["created_at"] = pd.to_datetime(df.get("created_at"), errors="coerce")
df = df.dropna(subset=["score", "total", "percentage", "created_at"])

# Line chart: Performance over time
st.subheader("📈 Performance Over Time")

plt.figure(figsize=(12, 5))
sns.lineplot(data=df, x="created_at", y="percentage", hue="feature", marker="o")
plt.title("Your Performance Trend")
plt.ylabel("Score Percentage")
plt.xlabel("Date")
plt.xticks(rotation=45)
plt.legend(title="Feature")
plt.tight_layout()
st.pyplot(plt.gcf())
plt.clf()  # Clear figure for next chart

# Bar chart: Average performance per feature
st.subheader("📊 Average Performance by Feature")
avg_df = df.groupby("feature")["percentage"].mean().reset_index()

plt.figure(figsize=(8, 5))
sns.barplot(data=avg_df, x="feature", y="percentage", palette="viridis")
plt.title("Average Score by Feature")
plt.ylabel("Average Percentage")
plt.xlabel("Feature")
plt.ylim(0, 100)
plt.xticks(rotation=30)
plt.tight_layout()
st.pyplot(plt.gcf())
plt.clf()

# Table: Recent Attempts
st.subheader("📝 Recent Attempts")
recent_df = df.sort_values("created_at", ascending=False).head(10)
recent_df_display = recent_df[["created_at", "feature", "score", "total", "percentage"]].copy()
recent_df_display["created_at"] = recent_df_display["created_at"].dt.strftime("%Y-%m-%d %H:%M")
st.table(recent_df_display)

# KPI metrics
st.subheader("📌 Summary Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Attempts", len(df))
with col2:
    st.metric("Average Score (%)", round(df["percentage"].mean(), 2))
with col3:
    st.metric("Best Score (%)", df["percentage"].max())
