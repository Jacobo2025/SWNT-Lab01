import streamlit as st

from views.home import render_home
from utils.config import AppConfig

st.set_page_config(
    page_title="EcoTrack",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%); }
    div[data-testid="stMetricValue"] { color: #15803d; }
    </style>
    """,
    unsafe_allow_html=True,
)

config = AppConfig.from_env()
render_home(config)
