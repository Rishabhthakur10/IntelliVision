import time
import streamlit as st
from src.database.db import get_subject_by_code, is_student_enrolled, enroll_student_to_subject


@st.dialog("Quick Subject Enrollment")
def auto_enroll_dialog(subject_code):
    student_id = st.session_state.student_data["student_id"]
    code = subject_code.strip().upper()
    subject = get_subject_by_code(code)

    if not subject:
        st.error(f"Subject code '{code}' was not found.")
        if st.button("Close"):
            st.query_params.clear()
            st.rerun()
        return

    if is_student_enrolled(student_id, subject["subject_id"]):
        st.info(f"You are already enrolled in **{subject['name']}**.")
        if st.button("Continue to Dashboard"):
            st.query_params.clear()
            st.rerun()
        return

    st.markdown(f"Would you like to enroll in **{subject['name']}** (`{subject['subject_code']}` - {subject['section']})?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Decline", use_container_width=True):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button("Join Course Now", type="primary", use_container_width=True):
            enroll_student_to_subject(student_id, subject["subject_id"])
            st.success("Successfully enrolled!")
            st.query_params.clear()
            time.sleep(1.2)
            st.rerun()
