from models.carbon import CarbonEstimate


CATEGORY_TIPS: dict[str, list[str]] = {
    "energy": [
        "Cambia a iluminación LED y equipos con certificación energética.",
        "Programa el aire acondicionado y revisa picos de consumo eléctrico.",
    ],
    "transport": [
        "Optimiza rutas de reparto para reducir km recorridos por camioneta.",
        "Evalúa vehículos híbridos o eléctricos para flotas urbanas.",
    ],
    "waste": [
        "Separa residuos reciclables para disminuir emisiones de vertederos.",
        "Negocia con proveedores que usen menos empaques.",
    ],
    "water": [
        "Instala aireadores en grifos y detecta fugas de forma periódica.",
    ],
    "food": [
        "Incorpora opciones vegetarianas o de menor impacto en menús frecuentes.",
        "Prioriza proteínas locales y de estación para reducir la huella alimentaria.",
    ],
}


def generate_recommendations(estimate: CarbonEstimate, max_items: int = 3) -> tuple[str, ...]:
    if estimate.total_kg_co2 <= 0:
        return (
            "Registra actividades con cantidades claras (ej. kWh, número de vehículos).",
        )

    tips: list[str] = []
    for category, _ in estimate.category_totals:
        for tip in CATEGORY_TIPS.get(category, []):
            if tip not in tips:
                tips.append(tip)
            if len(tips) >= max_items:
                return tuple(tips)

    if not tips:
        tips.append("Monitorea tus emisiones semanalmente para detectar mejoras rápidas.")

    return tuple(tips[:max_items])
