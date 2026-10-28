from datetime import datetime
import pandas as pd
import streamlit as st

from src.database.db import get_enrolled_students
from src.pipelines.voice_pipeline import is_voice_available, process_bulk_audio
from src.components.dialog_attendance_results import show_attendance_result


@st.dialog("AI Voice Biometric Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write("Record classroom roll call audio where students state their name and presence. The AI matches vocal acoustics with registered voice profiles.")

    if not is_voice_available():
        st.warning("Voice Biometrics feature requires `resemblyzer` and `librosa` installed in the environment. Please use **AI Face Analysis** on the main screen for computer vision attendance!")
        return

    audio_data = st.audio_input("Record classroom roll call")

    if st.button("Analyze Voice Biometrics", use_container_width=True, type="primary"):
        if not audio_data:
            st.warning("Please record audio first.")
            return

        with st.spinner("Processing acoustic features and comparing voice embeddings..."):
            enrolled_students = get_enrolled_students(selected_subject_id)
            if not enrolled_students:
                st.warning("No students are enrolled in this course.")
                return

            candidates_dict = {
                s["students"]["student_id"]: s["students"].get("voice_embedding")
                for s in enrolled_students if s["students"].get("voice_embedding")
            }

            if not candidates_dict:
                st.error("None of the enrolled students have voice profiles registered yet.")
                return

            audio_bytes = audio_data.read()
            detected_scores = process_bulk_audio(audio_bytes, candidates_dict)

            results = []
            attendance_to_log = []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                student = node["students"]
                score = detected_scores.get(student["student_id"], 0.0)
                is_present = bool(score > 0)

                results.append({
                    "Name": student["name"],
                    "ID": student["student_id"],
                    "Vocal Match": f"{score:.2f}" if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    "student_id": student["student_id"],
                    "subject_id": selected_subject_id,
                    "timestamp": current_timestamp,
                    "is_present": bool(is_present)
                })

            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get("voice_attendance_results"):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)
