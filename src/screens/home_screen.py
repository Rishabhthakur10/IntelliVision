import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():
    style_background_home()
    style_base_layout()

    header_home()

    st.markdown("""
        <div style="text-align: center; max-width: 680px; margin: 0 auto 30px auto; color: #E0E7FF; font-size: 1.05rem; line-height: 1.6;">
            Next-generation automated attendance powered by Computer Vision and Machine Learning.
            Identify multiple students simultaneously from photos or webcam streams with high precision.
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
            <div style="display:flex; align-items:center; gap: 14px; margin-bottom: 12px;">
                <span style="font-size: 2rem;">🎓</span>
                <div>
                    <h2 style="color: #FFFFFF !important; margin: 0; font-size: 1.6rem;">Student Portal</h2>
                    <span style="color: #CBD5E1; font-size: 0.85rem;">FaceID Login & Attendance Tracking</span>
                </div>
            </div>
            <p style="color: #E2E8F0; font-size: 0.95rem; margin-bottom: 18px;">
                • FaceID biometrics instant check-in<br>
                • View course enrollment & eligibility<br>
                • Real-time attendance rate breakdown<br>
                • Join courses with 1-click codes
            </p>
        """, unsafe_allow_html=True)

        if st.button("Enter Student Portal", type="primary", use_container_width=True, icon=":material/arrow_outward:"):
            st.session_state["login_type"] = "student"
            st.rerun()

    with col2:
        st.markdown("""
            <div style="display:flex; align-items:center; gap: 14px; margin-bottom: 12px;">
                <span style="font-size: 2rem;">👨‍🏫</span>
                <div>
                    <h2 style="color: #FFFFFF !important; margin: 0; font-size: 1.6rem;">Teacher Portal</h2>
                    <span style="color: #CBD5E1; font-size: 0.85rem;">Classroom AI Scanning & Analytics</span>
                </div>
            </div>
            <p style="color: #E2E8F0; font-size: 0.95rem; margin-bottom: 18px;">
                • Take attendance from photos or webcam<br>
                • Bounding box student verification<br>
                • Manage courses and generate QR codes<br>
                • Export detailed attendance logs to CSV
            </p>
        """, unsafe_allow_html=True)

        if st.button("Enter Teacher Portal", type="secondary", use_container_width=True, icon=":material/arrow_outward:"):
            st.session_state["login_type"] = "teacher"
            st.rerun()

    # Quick Demo Hint
    st.markdown("""
        <div style="
            margin-top: 35px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px dashed rgba(255, 255, 255, 0.2);
            border-radius: 14px;
            padding: 12px 20px;
            text-align: center;
            color: #C7D2FE;
            font-size: 0.85rem;
        ">
            💡 <b>Quick Demo Teacher Access:</b> Username: <code style="color: #FFFFFF; background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px;">prof.sharma</code> | Password: <code style="color: #FFFFFF; background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px;">teacher123</code>
        </div>
    """, unsafe_allow_html=True)

    footer_home()
