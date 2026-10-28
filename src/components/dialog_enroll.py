import time
import streamlit as st
from src.database.db import get_subject_by_code, is_student_enrolled, enroll_student_to_subject


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write("Enter the subject code provided by your instructor:")
    join_code = st.text_input("Subject Code", placeholder="e.g. CS101")

    if st.button("Enroll Now", type="primary", use_container_width=True):
        if join_code:
            code = join_code.strip().upper()
            subject = get_subject_by_code(code)
            if subject:
                student_id = st.session_state.student_data["student_id"]
                if is_student_enrolled(student_id, subject["subject_id"]):
                    st.warning("You are already enrolled in this subject!")
                else:
                    enroll_student_to_subject(student_id, subject["subject_id"])
                    st.success(f"Successfully enrolled in {subject['name']}!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error(f"No subject found with code '{code}'. Please check and try again.")
        else:
            st.warning("Please enter a subject code.")
