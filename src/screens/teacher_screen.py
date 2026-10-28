from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects,
    get_attendance_for_teacher,
    get_enrolled_students,
)
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.pipelines.face_pipeline import predict_attendance


def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif "teacher_login_type" not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns([2, 1], vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        st.markdown(f"**Welcome, {teacher_data['name']}**")
        if st.button("Logout", type="secondary", key="loginbackbtn"):
            st.session_state["is_logged_in"] = False
            del st.session_state.teacher_data
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == "take_attendance" else "tertiary"
        if st.button("📸 Take Attendance", type=type1, use_container_width=True):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == "manage_subjects" else "tertiary"
        if st.button("📚 Manage Subjects", type=type2, use_container_width=True):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == "attendance_records" else "tertiary"
        if st.button("📊 Attendance Records", type=type3, use_container_width=True):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.subheader("Automated AI Attendance Scan")

    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    if "annotated_results" not in st.session_state:
        st.session_state.annotated_results = []

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.info("You haven't created any subjects yet. Switch to the **Manage Subjects** tab to create your first course!")
        return

    subject_options = {f"{s['name']} ({s['subject_code']} - {s['section']})": s["subject_id"] for s in subjects}

    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        selected_subject_label = st.selectbox("Select Target Course", options=list(subject_options.keys()))
    with col2:
        if st.button("Add Photos", type="primary", use_container_width=True, icon=":material/photo_prints:"):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    # Image Gallery
    if st.session_state.attendance_images:
        st.markdown(f"#### Classroom Photos ({len(st.session_state.attendance_images)} staged)")
        gallery_cols = st.columns(min(4, len(st.session_state.attendance_images)))
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % min(4, len(st.session_state.attendance_images))]:
                st.image(img, use_container_width=True, caption=f"Capture #{idx+1}")

    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns([1, 1.5, 1])

    with c1:
        if st.button("Clear All Photos", use_container_width=True, type="tertiary", icon=":material/delete:", disabled=not has_photos):
            st.session_state.attendance_images = []
            st.session_state.annotated_results = []
            st.rerun()

    with c2:
        if st.button("Run AI Face Analysis", use_container_width=True, type="primary", icon=":material/analytics:", disabled=not has_photos):
            with st.spinner("Analyzing classroom biometrics with Computer Vision..."):
                all_detected_ids = {}
                annotated_list = []

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert("RGB"))
                    detected, _, num_faces, annotated_img = predict_attendance(img_np)
                    annotated_list.append(annotated_img)

                    if detected:
                        for sid, meta in detected.items():
                            all_detected_ids.setdefault(int(sid), []).append(f"Photo #{idx+1} ({meta.get('confidence', '')})")

                st.session_state.annotated_results = annotated_list

                # Fetch enrolled students
                enrolled_students = get_enrolled_students(selected_subject_id)
                if not enrolled_students:
                    st.warning("No students are currently enrolled in this course. Please enroll students or share the course code.")
                else:
                    results = []
                    attendance_to_log = []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node["students"]
                        sources = all_detected_ids.get(int(student["student_id"]), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name": student["name"],
                            "ID": student["student_id"],
                            "Source / Confidence": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            "student_id": student["student_id"],
                            "subject_id": selected_subject_id,
                            "timestamp": current_timestamp,
                            "is_present": bool(is_present)
                        })

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button("Voice Roll Call", type="secondary", use_container_width=True, icon=":material/mic:"):
            voice_attendance_dialog(selected_subject_id)

    # Display annotated face verification preview if available
    if st.session_state.annotated_results:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🎯 AI Face Detection & Recognition Overlay")
        overlay_cols = st.columns(min(3, len(st.session_state.annotated_results)))
        for idx, ann_img in enumerate(st.session_state.annotated_results):
            with overlay_cols[idx % min(3, len(st.session_state.annotated_results))]:
                st.image(ann_img, use_container_width=True, caption=f"Analyzed #{idx+1}")


def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    col1, col2 = st.columns([2, 1], vertical_alignment="center")
    with col1:
        st.subheader("Manage Teaching Subjects")
    with col2:
        if st.button("➕ Create New Subject", type="primary", use_container_width=True):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("👥", "Students Enrolled", sub.get("total_students", 0)),
                ("📅", "Class Sessions", sub.get("total_classes", 0)),
            ]

            def make_share_callback(s):
                def share_btn():
                    if st.button(f"Share Code & QR: {s['subject_code']}", key=f"share_{s['subject_code']}", icon=":material/share:"):
                        share_subject_dialog(s["name"], s["subject_code"])
                return share_btn

            subject_card(
                name=sub["name"],
                code=sub["subject_code"],
                section=sub["section"],
                stats=stats,
                footer_callback=make_share_callback(sub)
            )
    else:
        st.info("No courses found. Click **Create New Subject** above to get started.")


def teacher_tab_attendance_records():
    st.subheader("Attendance Records & History")
    teacher_id = st.session_state.teacher_data["teacher_id"]
    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info("No attendance sessions have been recorded yet.")
        return

    data = []
    for r in records:
        ts = r.get("timestamp")
        formatted_time = "N/A"
        if ts:
            try:
                formatted_time = datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p")
            except Exception:
                formatted_time = ts

        data.append({
            "ts_group": ts.split(".")[0] if ts else "None",
            "Time": formatted_time,
            "Subject": r["subjects"]["name"],
            "Subject Code": r["subjects"]["subject_code"],
            "Section": r["subjects"].get("section", ""),
            "is_present": bool(r.get("is_present", False))
        })

    df = pd.DataFrame(data)

    # Metrics overview
    total_records = len(df)
    total_present = int(df["is_present"].sum())
    overall_rate = round((total_present / total_records * 100), 1) if total_records > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Attendance Logs", total_records)
    m2.metric("Total Present", total_present)
    m3.metric("Total Absent", total_records - total_present)
    m4.metric("Avg Attendance Rate", f"{overall_rate}%")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    summary = (
        df.groupby(["ts_group", "Time", "Subject", "Subject Code", "Section"])
        .agg(
            Present_Count=("is_present", "sum"),
            Total_Count=("is_present", "count")
        )
        .reset_index()
    )

    summary["Attendance Rate"] = (summary["Present_Count"] / summary["Total_Count"] * 100).round(1).astype(str) + "%"
    summary["Status"] = "✅ " + summary["Present_Count"].astype(str) + " / " + summary["Total_Count"].astype(str) + " Students Present"

    display_df = (
        summary.sort_values(by="ts_group", ascending=False)
        [["Time", "Subject", "Subject Code", "Section", "Status", "Attendance Rate"]]
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # CSV Export Button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Full Attendance Report (CSV)",
        data=csv,
        file_name=f"intellivision_attendance_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )


def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username.strip(), password)
    if teacher:
        st.session_state.user_role = "teacher"
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


def teacher_screen_login():
    c1, c2 = st.columns([2, 1], vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        if st.button("← Back to Home", type="secondary", key="loginbackbtn"):
            st.session_state["login_type"] = None
            st.rerun()

    st.markdown("### Instructor Login")
    teacher_username = st.text_input("Username", placeholder="e.g. prof.sharma")
    teacher_pass = st.text_input("Password", type="password", placeholder="Enter your password")

    st.divider()
    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button("Sign In", icon=":material/passkey:", type="primary", use_container_width=True):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("Welcome back!", icon="👋")
                st.rerun()
            else:
                st.error("Invalid username or password. Check your credentials.")

    with btnc2:
        if st.button("Register New Instructor", use_container_width=True):
            st.session_state.teacher_login_type = "register"
            st.rerun()

    st.markdown("""
        <div style="margin-top: 25px; padding: 12px; background: #EEF2FF; border-radius: 10px; font-size: 0.85rem; color: #3730A3;">
            <b>Demo Credentials:</b> Username: <code>prof.sharma</code> | Password: <code>teacher123</code>
        </div>
    """, unsafe_allow_html=True)

    footer_dashboard()


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required."
    if check_teacher_exists(teacher_username):
        return False, "Username is already taken."
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match."

    try:
        create_teacher(teacher_username.strip(), teacher_pass, teacher_name.strip())
        return True, "Instructor profile created successfully! You can now log in."
    except Exception as e:
        return False, f"Error: {str(e)}"


def teacher_screen_register():
    c1, c2 = st.columns([2, 1], vertical_alignment="center")
    with c1:
        header_dashboard()
    with c2:
        if st.button("← Back to Home", type="secondary", key="loginbackbtn"):
            st.session_state["login_type"] = None
            st.rerun()

    st.markdown("### Register Instructor Account")
    teacher_username = st.text_input("Username", placeholder="e.g. dr.alan")
    teacher_name = st.text_input("Full Name & Title", placeholder="e.g. Dr. Alan Turing")
    teacher_pass = st.text_input("Password", type="password", placeholder="Create a password")
    teacher_pass_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")

    st.divider()
    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button("Complete Registration", icon=":material/passkey:", type="primary", use_container_width=True):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        if st.button("Back to Login", use_container_width=True):
            st.session_state.teacher_login_type = "login"
            st.rerun()

    footer_dashboard()
