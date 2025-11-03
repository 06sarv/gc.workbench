import streamlit as st

def header():
    st.markdown(
        "<h1 class='main-header'>Genetic Counselling Workbench</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: var(--text-secondary); font-size: 1.1rem; margin-bottom: 2rem;'>"
        "Integrated interpretation, batch VCF analysis, and RAG assistant tailored for genetic counselors."
        "</p>",
        unsafe_allow_html=True
    )

def sidebar_controls():
    st.sidebar.header("Workflow Settings")
    st.sidebar.markdown("""
    - **Single Variant**: HGVS or rsID
    - **Batch**: Upload VCF (≤ 50 analyzed per run)
    - **AI Copilot**: Ask variant or general counseling questions
    """)
    st.sidebar.divider()
