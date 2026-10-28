import streamlit as st


def header_home():
    logo_svg = """
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:20px; margin-top:20px">
        <div style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); width: 72px; height: 72px; border-radius: 20px; display:flex; align-items:center; justify-content:center; box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4);">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 2v2m0 16v2M2 12h2m16 0h2"/>
            </svg>
        </div>
        <h1 style='text-align:center; color:#FFFFFF; margin-top:12px; margin-bottom: 2px; font-weight:800; letter-spacing: -0.5px;'>INTELLIVISION</h1>
        <p style='color: #E0E7FF; font-size: 1.1rem; margin: 0; font-weight: 500;'>AI-Powered Automated Attendance System</p>
    </div>
    """
    st.markdown(logo_svg, unsafe_allow_html=True)


def header_dashboard():
    logo_svg = """
    <div style="display:flex; align-items:center; gap:14px; margin-bottom: 10px;">
        <div style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); width: 50px; height: 50px; border-radius: 14px; display:flex; align-items:center; justify-content:center; box-shadow: 0 6px 16px -2px rgba(79, 70, 229, 0.35);">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
                <circle cx="12" cy="12" r="3"/>
            </svg>
        </div>
        <div>
            <h2 style='text-align:left; color:#1E1B4B; margin: 0; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px;'>INTELLIVISION</h2>
            <span style='font-size: 0.8rem; color: #4338CA; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px;'>AI Attendance Portal</span>
        </div>
    </div>
    """
    st.markdown(logo_svg, unsafe_allow_html=True)
