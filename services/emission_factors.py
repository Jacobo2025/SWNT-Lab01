from dataclasses import dataclass


@dataclass(frozen=True)
class EmissionFactor:
    key: str
    label: str
    category: str
    kg_co2_per_unit: float
    unit: str


EMISSION_FACTORS: dict[str, EmissionFactor] = {
    "carne_res": EmissionFactor("carne_res", "Comida con carne de res", "alimentacion", 6.5, "comida"),
    "carne_general": EmissionFactor("carne_general", "Comida con carne", "alimentacion", 4.5, "comida"),
    "pollo": EmissionFactor("pollo", "Comida con pollo", "alimentacion", 1.5, "comida"),
    "pescado": EmissionFactor("pescado", "Comida con pescado", "alimentacion", 2.0, "comida"),
    "vegetariano": EmissionFactor("vegetariano", "Comida vegetariana", "alimentacion", 1.0, "comida"),
    "coche": EmissionFactor("coche", "Viaje en coche", "transporte", 0.21, "km"),
    "bus": EmissionFactor("bus", "Viaje en bus", "transporte", 0.089, "km"),
    "metro": EmissionFactor("metro", "Viaje en metro/tren urbano", "transporte", 0.041, "km"),
    "tren": EmissionFactor("tren", "Viaje en tren", "transporte", 0.041, "km"),
    "avion": EmissionFactor("avion", "Viaje en avión", "transporte", 0.255, "km"),
    "moto": EmissionFactor("moto", "Viaje en moto", "transporte", 0.113, "km"),
    "bicicleta": EmissionFactor("bicicleta", "Viaje en bicicleta", "transporte", 0.0, "km"),
    "electricidad": EmissionFactor("electricidad", "Consumo eléctrico", "energia", 0.45, "kwh"),
    "cigarrillo": EmissionFactor("cigarrillo", "Cigarrillo fumado", "habitos", 0.014, "cigarrillo"),
}


def get_factor(key: str) -> EmissionFactor | None:
    return EMISSION_FACTORS.get(key)
