import streamlit as st

from models.carbon import CarbonEstimate, DailyEntry


def render_detected_activities(estimate: CarbonEstimate) -> None:
    if not estimate.activities:
        return

    st.markdown("**Actividades detectadas**")
    rows = [
        {
            "Categoría": activity.category,
            "Tipo": activity.description,
            "Cantidad": activity.quantity,
            "Unidad": activity.unit,
        }
        for activity in estimate.activities
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_estimate_result(estimate: CarbonEstimate) -> None:
    st.markdown('<div class="ecotrack-card">', unsafe_allow_html=True)
    st.subheader("Resultado de emisiones")

    if estimate.clarifications and not estimate.breakdown:
        for question in estimate.clarifications:
            st.warning(question)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    col_total, col_source = st.columns(2)
    col_total.metric("Huella estimada", f"{estimate.total_kg_co2:.2f} kg CO₂e")
    col_source.caption(f"Fuente: {estimate.source}")

    if not estimate.breakdown:
        st.warning(
            "No se detectaron actividades reconocibles. "
            "Prueba: «Usamos 5 camionetas de reparto y consumimos 200 kWh»."
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    render_detected_activities(estimate)

    st.markdown("**Desglose**")
    for label, kg_co2 in estimate.breakdown:
        st.progress(min(kg_co2 / max(estimate.total_kg_co2, 0.001), 1.0))
        st.write(f"- **{label}**: {kg_co2:.2f} kg CO₂e")

    if estimate.recommendations:
        st.markdown("**Recomendaciones**")
        for tip in estimate.recommendations:
            st.info(tip)

    st.markdown("</div>", unsafe_allow_html=True)


def render_category_chart(entries: list[DailyEntry]) -> None:
    totals: dict[str, float] = {}
    for entry in entries:
        for category, value in entry.estimate.category_totals:
            totals[category] = totals.get(category, 0.0) + value

    if not totals:
        st.caption("Sin datos de categorías todavía.")
        return

    st.markdown("**Distribución por categoría**")
    st.bar_chart(totals)


def render_trend_chart(entries: list[DailyEntry]) -> None:
    if len(entries) < 2:
        st.caption("Registra más actividades para ver tendencia.")
        return

    st.markdown("**Tendencia de registros**")
    trend = {
        entry.timestamp.strftime("%H:%M"): entry.estimate.total_kg_co2
        for entry in entries
    }
    st.line_chart(trend)


def render_history(entries: list[DailyEntry]) -> None:
    if not entries:
        st.info("Aún no hay registros. Describe la operación de tu negocio.")
        return

    st.subheader("Emisiones recientes")
    total = sum(entry.estimate.total_kg_co2 for entry in entries)
    st.metric("Total acumulado", f"{total:.2f} kg CO₂e")

    rows = [
        {
            "Hora": entry.timestamp.strftime("%H:%M"),
            "Descripción": entry.text,
            "CO₂e (kg)": entry.estimate.total_kg_co2,
            "Fuente": entry.estimate.source,
        }
        for entry in reversed(entries)
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
