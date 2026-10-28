import io
import streamlit as st
import segno


@st.dialog("Share Course & QR Code")
def share_subject_dialog(subject_name, subject_code):
    join_url = f"http://localhost:8501/?join-code={subject_code}"

    st.markdown(f"#### **{subject_name}** (`{subject_code}`)")
    st.write("Share this code or QR code with students so they can enroll instantly.")

    qr = segno.make(join_url)
    out = io.BytesIO()
    qr.save(out, kind="png", scale=8, border=2)

    col1, col2 = st.columns([1, 1], vertical_alignment="center")

    with col1:
        st.markdown("**Subject Code:**")
        st.code(subject_code, language="text")
        st.markdown("**Join Link:**")
        st.code(join_url, language="text")
        st.caption("Students can enter this code in their portal or open this link.")

    with col2:
        st.image(out.getvalue(), caption="Scan to Enroll", use_container_width=True)
