import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    html = f"""
        <div style="
            background: #FFFFFF;
            border-left: 6px solid #4F46E5;
            padding: 22px 24px;
            border-radius: 16px;
            border: 1px solid #E2E8F0;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        ">
            <h3 style="margin: 0; color: #0F172A; font-size: 1.35rem; font-weight: 700;">{name}</h3>
            <p style="color: #64748B; margin: 8px 0 14px 0; font-size: 0.95rem;">
                Code: <span style="background: #EEF2FF; color: #4338CA; font-weight: 600; padding: 3px 10px; border-radius: 6px; font-family: monospace;">{code}</span> 
                &nbsp;|&nbsp; Section: <span style="font-weight: 600; color: #334155;">{section}</span>
            </p>
    """

    if stats:
        html += """<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 8px;">"""
        for icon, label, value in stats:
            html += f"""
                <div style="
                    background: #F1F5F9;
                    padding: 6px 14px;
                    border-radius: 10px;
                    font-size: 0.88rem;
                    color: #334155;
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                ">
                    <span>{icon}</span> <b>{value}</b> <span>{label}</span>
                </div>
            """
        html += "</div>"

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
