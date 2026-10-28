import time
from PIL import Image
import numpy as np
import pandas as pd
import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card
from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject,
)
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding, is_voice_available


def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns([2, 1], vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        if st.button("← Back to Home", type="secondary", key="loginbackbtn"):
            st.session_state["login_type"] = None
            st.rerun()

    st.markdown("### Student FaceID Biometric Login")
    st.write("Scan your face to access your attendance records and course details.")

    login_mode = st.radio("Choose Input Method", ["📸 Live Camera", "📁 Upload Face Photo", "🔍 Manual Select (Demo)"], horizontal=True)

    img_array = None

    if login_mode == "📸 Live Camera":
        photo_source = st.camera_input("Center your face in the camera")
        if photo_source:
            img_array = np.array(Image.open(photo_source).convert("RGB"))

    elif login_mode == "📁 Upload Face Photo":
        uploaded_face = st.file_uploader("Upload a clear portrait photo of your face", type=["jpg", "png", "jpeg"], key="student_face_upload")
        if uploaded_face:
            img_array = np.array(Image.open(uploaded_face).convert("RGB"))
            st.image(img_array, caption="Uploaded Portrait", width=200)

    elif login_mode == "🔍 Manual Select (Demo)":
        all_students = get_all_students()
        if all_students:
            student_choice = st.selectbox("Select Enrolled Student", [f"{s['name']} (ID: {s['student_id']})" for s in all_students])
            if st.button("Access Portal as Selected Student", type="primary"):
                sel_id = int(student_choice.split("ID: ")[1].replace(")", ""))
                selected_student = next((s for s in all_students if s["student_id"] == sel_id), None)
                if selected_student:
                    st.session_state.is_logged_in = True
                    st.session_state.user_role = "student"
                    st.session_state.student_data = selected_student
                    st.toast(f"Welcome, {selected_student['name']}!", icon="👋")
                    st.rerun()
        else:
            st.info("No students enrolled yet.")

    show_registration = False

    if img_array is not None:
        with st.spinner("AI is verifying facial biometric signature..."):
            detected, all_ids, num_faces, annotated_img = predict_attendance(img_array)

            if num_faces == 0:
                st.warning("No face detected in the picture. Please ensure good lighting and face the camera directly.")
            elif num_faces > 1:
                st.warning("Multiple faces detected. Please ensure only your face is visible for login.")
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s["student_id"] == student_id), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = "student"
                        st.session_state.student_data = student
                        st.toast(f"Face Recognized! Welcome back, {student['name']}", icon="✅")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Face not recognized in system database. You can register your new profile below!")
                    show_registration = True

    if show_registration and img_array is not None:
        with st.container(border=True):
            st.subheader("New Student FaceID Registration")
            new_name = st.text_input("Enter Full Name", placeholder="e.g. Maya Lin")

            audio_data = None
            if is_voice_available():
                st.caption("Optional Voice Biometric Profile:")
                try:
                    audio_data = st.audio_input("Record a short voice sample (e.g. 'I am present')")
                except Exception:
                    audio_data = None

            if st.button("Register & Activate FaceID Profile", type="primary", use_container_width=True):
                if new_name.strip():
                    with st.spinner("Extracting 128-D facial vector and training classifier..."):
                        encodings, _ = get_face_embeddings(img_array)
                        if encodings:
                            face_emb = encodings[0].tolist()
                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(new_name.strip(), face_embedding=face_emb, voice_embedding=voice_emb)
                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = "student"
                                st.session_state.student_data = response_data[0]
                                st.success(f"Profile registered successfully for {new_name.strip()}!")
                                time.sleep(1.2)
                                st.rerun()
                        else:
                            st.error("Could not capture facial landmarks clearly. Please adjust lighting.")
                else:
                    st.warning("Please enter your name.")

    footer_dashboard()


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data["student_id"]

    c1, c2 = st.columns([2, 1], vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        st.markdown(f"**Welcome, {student_data['name']}**")
        st.caption(f"Student ID: #{student_id}")
        if st.button("Logout", type="secondary", key="loginbackbtn"):
            st.session_state["is_logged_in"] = False
            del st.session_state.student_data
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Fetch subjects and attendance logs
    with st.spinner("Loading student academic data..."):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    # Compute statistics
    total_logs = len(logs)
    total_attended = sum(1 for log in logs if log.get("is_present"))
    overall_rate = round((total_attended / total_logs * 100), 1) if total_logs > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Enrolled Courses", len(subjects))
    m2.metric("Sessions Attended", f"{total_attended} / {total_logs}")
    m3.metric("Overall Attendance", f"{overall_rate}%")
    status_label = "✅ Good Standing" if overall_rate >= 75 or total_logs == 0 else "⚠️ Shortage Warning"
    m4.metric("Eligibility Status", status_label)

    st.divider()

    c1, c2 = st.columns([2, 1], vertical_alignment="center")
    with c1:
        st.subheader("Your Enrolled Subjects")
    with c2:
        if st.button("➕ Enroll in New Subject", type="primary", use_container_width=True):
            enroll_dialog()

    stats_map = {}
    for log in logs:
        sid = log["subject_id"]
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]["total"] += 1
        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    if subjects:
        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node["subjects"]
            sid = sub["subject_id"]
            stats = stats_map.get(sid, {"total": 0, "attended": 0})
            sub_rate = round((stats["attended"] / stats["total"] * 100), 1) if stats["total"] > 0 else 100.0

            def make_unenroll_btn(subj_id, subj_name):
                def unenroll_button():
                    if st.button(f"Unenroll from {subj_name}", key=f"unenroll_{subj_id}", type="tertiary", use_container_width=True, icon=":material/delete_forever:"):
                        unenroll_student_to_subject(student_id, subj_id)
                        st.toast(f"Unenrolled from {subj_name} successfully!", icon="ℹ️")
                        st.rerun()
                return unenroll_button

            rate_badge = f"{sub_rate}%"
            with cols[i % 2]:
                subject_card(
                    name=sub["name"],
                    code=sub["subject_code"],
                    section=sub["section"],
                    stats=[
                        ("📅", "Conducted", stats["total"]),
                        ("✅", "Attended", stats["attended"]),
                        ("📊", "Rate", rate_badge),
                    ],
                    footer_callback=make_unenroll_btn(sid, sub["name"])
                )
    else:
        st.info("You are not enrolled in any courses yet. Click **Enroll in New Subject** above to join with a code.")

    # Individual Student Attendance History
    if logs:
        st.divider()
        st.subheader("Your Attendance History Log")
        history_data = []
        for l in logs:
            history_data.append({
                "Date & Time": l.get("timestamp", "").replace("T", " "),
                "Course": l["subjects"]["name"],
                "Course Code": l["subjects"]["subject_code"],
                "Section": l["subjects"]["section"],
                "Status": "✅ Present" if l.get("is_present") else "❌ Absent"
            })
        st.dataframe(pd.DataFrame(history_data), use_container_width=True, hide_index=True)

    footer_dashboard()
