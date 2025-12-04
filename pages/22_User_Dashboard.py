import streamlit as st
import pandas as pd
import altair as alt
import usage_manager as um

st.title("📊 Your Performance Dashboard")

if "user" in st.session_state:
    user_id = st.session_state.user.id
else:
    st.warning("Please log in to view your dashboard.")
    st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
    st.stop()

data = um.get_user_performance(user_id)

if not data:
    st.info("No performance data available yet. Use the Exam Simulator or Quiz Generator.")
    st.stop()

df = pd.DataFrame(data)

# Percentage chart
chart = alt.Chart(df).mark_line(point=True).encode(
    x="created_at:T",
    y="percentage:Q",
    color="feature:N",
    tooltip=["feature", "score", "total", "percentage", "created_at"]
)

st.altair_chart(chart, use_container_width=True)

# Summary stats
st.subheader("📌 Summary")
st.write(df.groupby("feature")["percentage"].mean().round(2))
