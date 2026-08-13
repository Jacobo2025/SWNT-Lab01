from datetime import datetime

import streamlit as st

from components.result_card import render_estimate_result, render_history
from models.carbon import DailyEntry
from services.carbon_ai_service import CarbonAIService
from utils.config import AppConfig

EXAMPLE_TEXT = "Hoy comí carne y viajé 20 km en bus"


def _init_session_state() -> None:
    if "entries" not in st.session_state:
        st.session_state.entries = []
    if "last_estimate" not in st.session_state:
        st.session_state.last_estimate = None


def render_home(config: AppConfig) -> None:
    _init_session_state()
    service = CarbonAIService(config)

    st.title("EcoTrack")
    st.markdown(
        "Registra tu **huella de carbono diaria** escribiendo tus actividades "
        "en lenguaje natural. La IA estimará los kg de CO₂ equivalente."
    )

    if config.has_ai:
        st.success("Modo IA activo (OpenAI).")
    else:
        st.info(
            "Modo análisis local activo. Configura `OPENAI_API_KEY` "
            "para estimaciones con IA."
        )

    with st.form("carbon_form", clear_on_submit=False):
        user_text = st.text_area(
            "¿Qué hiciste hoy?",
            placeholder=EXAMPLE_TEXT,
            height=120,
        )
        submitted = st.form_submit_button("Calcular huella", type="primary")

    if submitted:
        text = user_text.strip()
        if not text:
            st.error("Escribe al menos una actividad para calcular tu huella.")
        else:
            with st.spinner("Analizando tu día..."):
                estimate = service.estimate(text)
            st.session_state.last_estimate = estimate
            st.session_state.entries.append(
                DailyEntry(timestamp=datetime.now(), text=text, estimate=estimate)
            )

    if st.session_state.last_estimate is not None:
        render_estimate_result(st.session_state.last_estimate)

    st.divider()
    render_history(st.session_state.entries)

    if st.session_state.entries and st.button("Limpiar historial de hoy"):
        st.session_state.entries = []
        st.session_state.last_estimate = None
        st.rerun()
