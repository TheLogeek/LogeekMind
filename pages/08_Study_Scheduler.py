import streamlit as st
import pandas as pd
import random
import usage_manager as um

st.title("📅Study Scheduler")
st.markdown("Create a structured daily or weekly study plan by listing your subjects and estimated time needs.")

if 'subjects' not in st.session_state:
    st.session_state.subjects = [
        {'name': 'Math', 'priority': 3, 'time_hr': 2.0},
        {'name': 'English', 'priority': 2, 'time_hr': 1.5},
    ]

def add_subject():
    st.session_state.subjects.append({'name': '', 'priority': 1, 'time_hr': 1.0})

def generate_schedule():
    valid_subjects = [s for s in st.session_state.subjects if s['name'].strip() != '']

    schedule_data = []

    if not valid_subjects:
        st.error("Please add at least one subject to generate a study schedule.")
        return None

    total_time_needed = sum(s['time_hr'] for s in valid_subjects)

    DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    study_blocks = []

    for subject in valid_subjects:
        block_count = int(subject['time_hr'] * 2)

        weighted_count = block_count * subject['priority']
        study_blocks.extend([subject['name']] * weighted_count)

    random.shuffle(study_blocks)

    schedule = {day: [] for  day in DAYS}
    day_index = 0

    for block in study_blocks:
        day = DAYS[day_index % 7]
        schedule[day].append(block)
        day_index += 1

    schedule_data = []

    for day, subjects_list in schedule.items():
        daily_subjects = {}

        for subject_name in subjects_list:
            daily_subjects[subject_name] = daily_subjects.get(subject_name, 0) + 1

        plan_summary = []
        for subject, block_count in daily_subjects.items():
            total_minutes = block_count * 30

            hours = total_minutes // 60
            minutes = total_minutes % 60

            time_str = ""
            if hours > 0:
                time_str += f"{hours}hours "
            if minutes > 0:
                time_str += f"{minutes}minutes"

            if not time_str:
                continue

            plan_summary.append(f"{subject} ({time_str.strip()})")

        schedule_data.append({
            'Day': day,
            'Study Plan': ', '.join(plan_summary)
        })

    schedule_df = pd.DataFrame(schedule_data)

    st.metric(
        label="Total Weekly Study Time Allocated",
        value=f"{total_time_needed:.1f} Hours",
        delta=f"Based on {len(valid_subjects)} subjects."
    )

    return schedule_df

st.subheader("📚Subject Input")

cols = st.columns([3, 1.5, 1.5])
cols[0].write("Subject Name")
cols[1].write("Priority (1-5)")
cols[2].write("Time/Week (Hours)")

for i, subject in enumerate(st.session_state.subjects):
    c1, c2, c3 = st.columns([3, 1.5, 1.5])

    subject['name'] = c1.text_input("Name", value=subject['name'], label_visibility="collapsed", key=f"sub_name_{i}")
    subject['priority'] = c2.number_input("Priority", min_value=1, max_value=5, value=subject['priority'], step=1,
                                          label_visibility="collapsed", key=f"sub_priority_{i}")
    subject['time_hr'] = c3.number_input("Time", min_value=0.5, value=subject['time_hr'], step=0.5, format="%.1f",
                                         label_visibility="collapsed", key=f"sub_time_{i}")

st.button("➕Add Subject", on_click=add_subject)
st.divider()

if st.button("Generate Study Schedule", type="primary"):
    if not um.check_guest_limit("Study Scheduler", limit=5):
        login_link = st.page_link("pages/00_login.py", label="Login/Signup", icon="🔑")
        st.stop()
    schedule_df = generate_schedule()
    if schedule_df is not None:
        st.header("📅Your Weekly Study plan")
        st.dataframe(schedule_df, width='stretch', hide_index=True)
        st.success("Your schedule has been generated! Rememeber, this is a suggestion, feel free to adjust.")
