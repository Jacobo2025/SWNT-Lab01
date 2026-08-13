from datetime import datetime

import streamlit as st

from components.result_card import (
    render_category_chart,
    render_estimate_result,
    render_history,
    render_trend_chart,
)
from components.styles import render_header
from models.carbon import DailyEntry
from services.carbon_ai_service import CarbonAIService
from utils.config import AppConfig

EXAMPLE_TEXT = (
    "Durante el día consumimos 200 kWh de electricidad "
    "y usamos 5 camionetas de reparto."
)


def _init_session_state() -> None:
    if "entries" not in st.session_state:
        st.session_state.entries = []
    if "last_estimate" not in st.session_state:
        st.session_state.last_estimate = None


def render_dashboard(config: AppConfig) -> None:
    _init_session_state()
    service = CarbonAIService(config)
    render_header()

    total_footprint = sum(entry.estimate.total_kg_co2 for entry in st.session_state.entries)
    top_category = "-"
    if st.session_state.entries:
        category_totals: dict[str, float] = {}
        for entry in st.session_state.entries:
            for category, value in entry.estimate.category_totals:
                category_totals[category] = category_totals.get(category, 0.0) + value
        if category_totals:
            top_category = max(category_totals, key=category_totals.get)

    metric_cols = st.columns(3)
    metric_cols[0].metric("Huella total", f"{total_footprint:.2f} kg CO₂e")
    metric_cols[1].metric("Registros", len(st.session_state.entries))
    metric_cols[2].metric("Categoría principal", top_category)

    if config.has_ai:
        st.caption("IA activa · OpenAI")
    else:
        st.caption("Modo local · Configura OPENAI_API_KEY para IA avanzada")

    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.markdown('<div class="ecotrack-card">', unsafe_allow_html=True)
        st.subheader("Registro de actividad")
        with st.form("activity_form", clear_on_submit=False):
            user_text = st.text_area(
                "Describe las actividades de tu negocio",
                placeholder=EXAMPLE_TEXT,
                height=130,
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Analizar con IA", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            text = user_text.strip()
            if not text:
                st.error("Escribe al menos una actividad para analizar.")
            else:
                with st.spinner("Interpretando actividades..."):
                    estimate = service.estimate(text)
                st.session_state.last_estimate = estimate
                st.session_state.entries.append(
                    DailyEntry(timestamp=datetime.now(), text=text, estimate=estimate)
                )

        if st.session_state.last_estimate is not None:
            render_estimate_result(st.session_state.last_estimate)

    with right:
        st.markdown('<div class="ecotrack-card">', unsafe_allow_html=True)
        render_category_chart(st.session_state.entries)
        render_trend_chart(st.session_state.entries)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    render_history(st.session_state.entries)

    if st.session_state.entries and st.button("Limpiar registros"):
        st.session_state.entries = []
        st.session_state.last_estimate = None
        st.rerun()
