from dataclasses import dataclass


@dataclass(frozen=True)
class EmissionFactor:
    key: str
    label: str
    category: str
    kg_co2_per_unit: float
    unit: str


EMISSION_FACTORS: dict[str, EmissionFactor] = {
    # Energía
    "electricidad": EmissionFactor(
        "electricidad", "Consumo eléctrico", "energy", 0.45, "kWh"
    ),
    "gas_natural": EmissionFactor(
        "gas_natural", "Consumo de gas natural", "energy", 2.0, "m3"
    ),
    # Transporte empresarial
    "camioneta_reparto": EmissionFactor(
        "camioneta_reparto",
        "Camioneta de reparto (día de operación)",
        "transport",
        15.0,
        "vehicles",
    ),
    "flota_liviana": EmissionFactor(
        "flota_liviana", "Vehículo liviano (día de operación)", "transport", 12.0, "vehicles"
    ),
    "coche": EmissionFactor("coche", "Viaje en coche", "transport", 0.21, "km"),
    "bus": EmissionFactor("bus", "Viaje en bus", "transport", 0.089, "km"),
    "avion": EmissionFactor("avion", "Viaje en avión", "transport", 0.255, "km"),
    # Residuos y operación
    "residuos": EmissionFactor(
        "residuos", "Generación de residuos", "waste", 0.5, "kg"
    ),
    "agua": EmissionFactor(
        "agua", "Consumo de agua", "water", 0.001, "m3"
    ),
    # Alimentación
    "carne_res": EmissionFactor(
        "carne_res", "Comida con carne de res", "food", 6.5, "meal"
    ),
    "carne_general": EmissionFactor(
        "carne_general", "Comida con carne", "food", 4.5, "meal"
    ),
    "pollo": EmissionFactor(
        "pollo", "Comida con pollo", "food", 1.5, "meal"
    ),
    "pescado": EmissionFactor(
        "pescado", "Comida con pescado", "food", 2.0, "meal"
    ),
    "huevos": EmissionFactor(
        "huevos", "Comida con huevos", "food", 1.0, "meal"
    ),
    "vegetariano": EmissionFactor(
        "vegetariano", "Comida vegetariana", "food", 1.0, "meal"
    ),
}

TYPE_ALIASES: dict[str, str] = {
    "electricity": "electricidad",
    "electricidad": "electricidad",
    "delivery_van": "camioneta_reparto",
    "camioneta": "camioneta_reparto",
    "camioneta_reparto": "camioneta_reparto",
    "van": "camioneta_reparto",
    "natural_gas": "gas_natural",
    "gas": "gas_natural",
    "car": "coche",
    "flight": "avion",
    "waste": "residuos",
    "water": "agua",
    "beef": "carne_res",
    "meat": "carne_general",
    "chicken": "pollo",
    "fish": "pescado",
    "salmon": "pescado",
    "eggs": "huevos",
    "egg": "huevos",
}


def resolve_factor_key(raw_type: str) -> str | None:
    normalized = raw_type.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in EMISSION_FACTORS:
        return normalized
    return TYPE_ALIASES.get(normalized)


def get_factor(key: str) -> EmissionFactor | None:
    resolved = resolve_factor_key(key)
    if resolved is None:
        return None
    return EMISSION_FACTORS.get(resolved)
