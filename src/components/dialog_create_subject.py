import streamlit as st
from src.database.db import create_subject


@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of the new subject or course:")
    sub_id = st.text_input("Subject Code", placeholder="e.g. CS101, AI204")
    sub_name = st.text_input("Subject Name", placeholder="e.g. Introduction to Computer Vision")
    sub_section = st.text_input("Section", placeholder="e.g. Section A")

    if st.button("Create Subject Now", type="primary", use_container_width=True):
        if sub_id and sub_name and sub_section:
            try:
                create_subject(sub_id.strip().upper(), sub_name.strip(), sub_section.strip(), teacher_id)
                st.toast("Subject created successfully!", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating subject: {str(e)}")
        else:
            st.warning("Please fill in all the required fields.")
