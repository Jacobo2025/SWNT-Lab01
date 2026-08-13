import streamlit as st

SAAS_THEME = """
<style>
    .stApp {
        background: linear-gradient(160deg, #f8fafc 0%, #ecfdf5 45%, #ffffff 100%);
    }
    .block-container {
        padding-top: 1.5rem;
        max-width: 1100px;
    }
    .ecotrack-header {
        background: linear-gradient(135deg, #065f46 0%, #059669 100%);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        color: white;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px rgba(5, 150, 105, 0.18);
    }
    .ecotrack-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .ecotrack-header p {
        margin: 0.35rem 0 0;
        opacity: 0.92;
        font-size: 0.95rem;
    }
    .ecotrack-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stMetricValue"] {
        color: #047857;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        color: #475569;
    }
    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid #cbd5e1;
    }
    .stButton > button[kind="primary"] {
        background: #059669;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }
    .stButton > button[kind="primary"]:hover {
        background: #047857;
    }
</style>
"""


def apply_theme() -> None:
    st.markdown(SAAS_THEME, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        """
        <div class="ecotrack-header">
            <h1>EcoTrack AI</h1>
            <p>Estima la huella de carbono de tu negocio con lenguaje natural.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
