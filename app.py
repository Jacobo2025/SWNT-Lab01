import streamlit as st

from components.styles import apply_theme
from utils.config import AppConfig
from views.dashboard import render_dashboard

st.set_page_config(
    page_title="EcoTrack AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_theme()

config = AppConfig.from_env()
render_dashboard(config)
