import streamlit as st

def inject_css():
    st.markdown(
        """
        <style>
        body { font-family: 'Nunito Sans', sans-serif; }
        .main-header { font-size: 2.5rem; text-align: center; margin-top: -1.5rem; }
        .section-header { font-size: 1.4rem; margin-top: 1.5rem; border-bottom: 2px solid #3c82f6; padding-bottom: 0.3rem; }
        .info-card { background: #eef4ff; border-radius: 12px; padding: 1rem 1.2rem; border-left: 4px solid #3c82f6; color: #1e293b; }
        .warning-card { background: #fff7ea; border-left: 4px solid #ffa500; border-radius: 12px; padding: 1rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
