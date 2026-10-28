import streamlit as st
from PIL import Image


@st.dialog("Capture or Upload Classroom Photos")
def add_photos_dialog():
    st.write("Add classroom photos to analyze faces and mark student attendance automatically.")

    if "photo_tab" not in st.session_state:
        st.session_state.photo_tab = "upload"

    t1, t2 = st.columns(2)

    with t1:
        type_upload = "primary" if st.session_state.photo_tab == "upload" else "tertiary"
        if st.button("📁 Upload Photos", type=type_upload, use_container_width=True):
            st.session_state.photo_tab = "upload"
            st.rerun()

    with t2:
        type_camera = "primary" if st.session_state.photo_tab == "camera" else "tertiary"
        if st.button("📸 Live Camera", type=type_camera, use_container_width=True):
            st.session_state.photo_tab = "camera"
            st.rerun()

    if st.session_state.photo_tab == "upload":
        uploaded_files = st.file_uploader(
            "Choose classroom image files (PNG, JPG, JPEG)",
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True,
            key="dialog_upload"
        )
        if uploaded_files:
            for f in uploaded_files:
                st.session_state.attendance_images.append(Image.open(f))
            st.toast(f"{len(uploaded_files)} photo(s) added successfully!", icon="📸")
            st.rerun()

    if st.session_state.photo_tab == "camera":
        cam_photo = st.camera_input("Take Snapshot of Classroom", key="dialog_cam")
        if cam_photo:
            st.session_state.attendance_images.append(Image.open(cam_photo))
            st.toast("Classroom photo captured!", icon="📸")
            st.rerun()

    st.divider()
    if st.button("Done & Review Photos", type="primary", use_container_width=True):
        st.rerun()
