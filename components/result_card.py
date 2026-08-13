import streamlit as st

from models.carbon import CarbonEstimate, DailyEntry


def render_estimate_result(estimate: CarbonEstimate) -> None:
    st.subheader("Resultado del día")
    col_total, col_source = st.columns(2)
    col_total.metric("Huella estimada", f"{estimate.total_kg_co2:.2f} kg CO₂e")
    col_source.caption(f"Fuente: {estimate.source}")

    if not estimate.breakdown:
        st.warning(
            "No se detectaron actividades reconocibles. "
            "Prueba frases como: «Comí carne y viajé 20 km en bus»."
        )
        return

    st.markdown("**Desglose**")
    for label, kg_co2 in estimate.breakdown:
        st.progress(min(kg_co2 / max(estimate.total_kg_co2, 0.001), 1.0))
        st.write(f"- **{label}**: {kg_co2:.2f} kg CO₂e")


def render_history(entries: list[DailyEntry]) -> None:
    if not entries:
        st.info("Aún no hay registros. Escribe tu primera actividad del día.")
        return

    st.subheader("Historial de hoy")
    total_day = sum(entry.estimate.total_kg_co2 for entry in entries)
    st.metric("Total acumulado hoy", f"{total_day:.2f} kg CO₂e")

    rows = [
        {
            "Hora": entry.timestamp.strftime("%H:%M"),
            "Actividad": entry.text,
            "CO₂e (kg)": entry.estimate.total_kg_co2,
            "Fuente": entry.estimate.source,
        }
        for entry in reversed(entries)
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
