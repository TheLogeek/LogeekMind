import streamlit as st
import pandas as pd
from streamlit import session_state

st.title("GPA Calculator")
st.markdown("Enter your grades and credits to calculate your term GPA")

GRADE_POINTS = {
    "A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "E": 1.0, "F": 0.0
}

if 'courses' not in st.session_state:
    st.session_state.courses = [{'name': '', 'grade': 'A', 'units': 3}]

def add_course():
    st.session_state.courses.append({'name': '', 'grade': 'A', 'units': 3})

def calculate_gpa():
    total_units = 0
    total_grade_points = 0
    for course in st.session_state.courses:
        units = course['units']
        grade = course['grade']

        if grade in GRADE_POINTS:
            points = GRADE_POINTS[grade]
            total_units += units
            total_grade_points += (points * units)

    if total_units > 0:
        gpa = total_grade_points / total_units
        return round(gpa, 2)
    return 0.0

# GUI Layout
col_list = st.columns([2, 1, 1])
col_list[0].subheader("Course Name")
col_list[1].subheader("Grade")
col_list[2].subheader("Units")

for i, course in enumerate(st.session_state.courses):
    cols = st.columns([2, 1, 1])

    course['name'] = cols[0].text_input("Name", value=course['name'], label_visibility="collapsed", key=f"name_{i}")
    course['grade'] = cols[1].selectbox("Grade", options=list(GRADE_POINTS.keys()), index=list(GRADE_POINTS.keys(
    )).index(course['grade']), label_visibility="collapsed", key=f"grade_{i}")
    course['units'] = cols[2].number_input("Units", min_value=1, value=course['units'], step=1,
                                             label_visibility="collapsed", key=f"units_{i}")

st.button("➕ Add Another Course", on_click=add_course)

gpa_result = calculate_gpa()
st.divider()
st.metric(label="Calculated Term GPA", value=f"{gpa_result:.2f}", delta=f"Total Units: {sum(c['units'] for c in 
                                                                                              st.session_state.courses)}")