import streamlit as st


def footer_home():
    st.markdown("""
        <div style="
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
            color: #E0E7FF;
            font-size: 0.85rem;
        ">
            <b>IntelliVision</b> — Advanced AI Attendance System & Biometric Engine<br>
            <span style="opacity: 0.8;">Python • Streamlit • Computer Vision • Face Recognition</span>
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    st.markdown("""
        <div style="
            margin-top: 3rem;
            padding-top: 1.2rem;
            border-top: 1px solid #CBD5E1;
            text-align: center;
            color: #64748B;
            font-size: 0.85rem;
        ">
            <b>IntelliVision</b> — Attendance System with AI • Computer Vision & Biometrics
        </div>
    """, unsafe_allow_html=True)
