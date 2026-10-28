import streamlit as st
from src.database.db import create_attendance


def show_attendance_result(df, logs):
    st.write("Please review attendance detection results before confirming and saving to database:")

    # Summary metric pills
    present_count = sum(1 for log in logs if log.get("is_present"))
    total_count = len(logs)
    rate = round((present_count / total_count * 100), 1) if total_count > 0 else 0

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Present Students", f"{present_count} / {total_count}")
    col_m2.metric("Absent Students", f"{total_count - present_count}")
    col_m3.metric("Attendance Rate", f"{rate}%")

    st.dataframe(df, hide_index=True, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Discard Results", use_container_width=True):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.session_state.annotated_results = []
            st.rerun()

    with col2:
        if st.button("Confirm & Save Attendance", use_container_width=True, type="primary"):
            try:
                create_attendance(logs)
                st.toast("Attendance successfully recorded into system!", icon="✅")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.session_state.annotated_results = []
                st.rerun()
            except Exception as e:
                st.error(f"Save failed: {str(e)}")


@st.dialog("Review Attendance Results")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)
