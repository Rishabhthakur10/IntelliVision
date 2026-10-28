import streamlit as st


def style_background_home():
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%) !important;
                color: #FFFFFF !important;
            }

            .stApp div[data-testid="stColumn"] {
                background: rgba(255, 255, 255, 0.08) !important;
                backdrop-filter: blur(12px) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                padding: 2.2rem !important;
                border-radius: 2rem !important;
                box-shadow: 0 20px 35px -10px rgba(0, 0, 0, 0.3) !important;
                transition: transform 0.25s ease, box-shadow 0.25s ease !important;
            }

            .stApp div[data-testid="stColumn"]:hover {
                transform: translateY(-4px) !important;
                box-shadow: 0 25px 45px -10px rgba(0, 0, 0, 0.45) !important;
            }
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown("""
        <style>
            .stApp {
                background: #F8FAFC !important;
                color: #0F172A !important;
            }
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

            /* Hide Streamlit Default UI Chrome */
            #MainMenu, footer, header {
                visibility: hidden;
            }

            .block-container {
                padding-top: 1.5rem !important;
                padding-bottom: 2rem !important;
                max-width: 1100px !important;
            }

            h1, h2, h3, h4, h5, h6 {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
            }

            p, span, div, label, input, button {
                font-family: 'Outfit', sans-serif !important;
            }

            /* Custom button styles */
            button[kind="primary"] {
                border-radius: 1rem !important;
                background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
                color: white !important;
                padding: 10px 24px !important;
                border: none !important;
                font-weight: 600 !important;
                box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.35) !important;
                transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            }

            button[kind="secondary"] {
                border-radius: 1rem !important;
                background-color: #EC4899 !important;
                color: white !important;
                padding: 10px 24px !important;
                border: none !important;
                font-weight: 600 !important;
                box-shadow: 0 4px 14px 0 rgba(236, 72, 153, 0.35) !important;
                transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            }

            button[kind="tertiary"] {
                border-radius: 1rem !important;
                background-color: #0F172A !important;
                color: white !important;
                padding: 10px 24px !important;
                border: 1px solid #334155 !important;
                font-weight: 600 !important;
                transition: transform 0.2s ease !important;
            }

            button:hover {
                transform: translateY(-2px) !important;
            }
        </style>
    """, unsafe_allow_html=True)
