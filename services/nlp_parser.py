import json
import re

from models.carbon import Activity
from services.emission_factors import EMISSION_FACTORS
from services.flight_estimator import estimate_flight_distance_km


FOOD_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("carne_res", re.compile(r"\b(res|ternera|bistec|hamburguesa de res)\b", re.I)),
    ("pollo", re.compile(r"\b(pollo|pollo asado|pechuga)\b", re.I)),
    ("pescado", re.compile(r"\b(pescado|atún|salmon|salmón)\b", re.I)),
    ("vegetariano", re.compile(r"\b(vegetariano|vegano|ensalada|legumbres)\b", re.I)),
    ("carne_general", re.compile(r"\b(carne|comí carne|almorcé carne|cena con carne)\b", re.I)),
]

TRANSPORT_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("bus", re.compile(r"\b(bus|autobús|autobus|colectivo)\b", re.I), "km"),
    ("coche", re.compile(r"\b(coche|auto|carro|taxi|uber)\b", re.I), "km"),
    ("metro", re.compile(r"\b(metro|subte|subterraneo|subterráneo)\b", re.I), "km"),
    ("tren", re.compile(r"\b(tren|ferrocarril|rail)\b", re.I), "km"),
    ("avion", re.compile(r"\b(avión|avion|vuelo|volé|vole)\b", re.I), "km"),
    ("moto", re.compile(r"\b(moto|motocicleta)\b", re.I), "km"),
    ("bicicleta", re.compile(r"\b(bici|bicicleta|ciclismo)\b", re.I), "km"),
]

ENERGY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("electricidad", re.compile(r"\b(electricidad|luz|kwh|kilovatios)\b", re.I)),
]

HABIT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("cigarrillo", re.compile(r"\b(cigarrillos?|fum[eé]|fumado|tabaco)\b", re.I)),
]

CIGARETTE_COUNT_PATTERN = re.compile(
    r"(\d+)\s*(?:cigarrillos?|pitillos?)\b|"
    r"(?:me\s+)?fum[eé]\s+(\d+)\b|"
    r"(\d+)\s+(?:cigarrillos?|pitillos?)\s+fumad",
    re.I,
)

DISTANCE_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:km|kilómetros|kilometros|k\b)",
    re.I,
)
ENERGY_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:kwh|kilovatios?-?hora?s?)\b",
    re.I,
)


def _parse_number(value: str) -> float:
    return float(value.replace(",", "."))


def _extract_distance(text: str) -> float | None:
    match = DISTANCE_PATTERN.search(text)
    if match:
        return _parse_number(match.group(1))
    return None


def _extract_energy(text: str) -> float | None:
    match = ENERGY_PATTERN.search(text)
    if match:
        return _parse_number(match.group(1))
    return None


def _extract_cigarette_count(text: str) -> float | None:
    match = CIGARETTE_COUNT_PATTERN.search(text)
    if not match:
        return None
    for group in match.groups():
        if group:
            return _parse_number(group)
    return None


def _match_food(text: str) -> list[Activity]:
    for key, pattern in FOOD_PATTERNS:
        if pattern.search(text):
            factor = EMISSION_FACTORS[key]
            return [
                Activity(
                    category=factor.category,
                    description=key,
                    quantity=1.0,
                    unit=factor.unit,
                )
            ]
    return []


def _match_transport(text: str) -> list[Activity]:
    distance = _extract_distance(text)

    if distance is None:
        flight_distance = estimate_flight_distance_km(text)
        if flight_distance is not None:
            distance = flight_distance

    if distance is None:
        return []

    for key, pattern, unit in TRANSPORT_PATTERNS:
        if pattern.search(text):
            factor = EMISSION_FACTORS[key]
            return [
                Activity(
                    category=factor.category,
                    description=key,
                    quantity=distance,
                    unit=unit,
                )
            ]
    return []


def _match_habits(text: str) -> list[Activity]:
    count = _extract_cigarette_count(text)
    if count is None:
        return []

    for key, pattern in HABIT_PATTERNS:
        if pattern.search(text):
            factor = EMISSION_FACTORS[key]
            return [
                Activity(
                    category=factor.category,
                    description=key,
                    quantity=count,
                    unit=factor.unit,
                )
            ]
    return []


def _match_energy(text: str) -> list[Activity]:
    kwh = _extract_energy(text)
    if kwh is None:
        return []

    for key, pattern in ENERGY_PATTERNS:
        if pattern.search(text):
            factor = EMISSION_FACTORS[key]
            return [
                Activity(
                    category=factor.category,
                    description=key,
                    quantity=kwh,
                    unit=factor.unit,
                )
            ]
    return []


def parse_natural_language(text: str) -> list[Activity]:
    normalized = text.strip()
    if not normalized:
        return []

    activities: list[Activity] = []
    activities.extend(_match_food(normalized))
    activities.extend(_match_transport(normalized))
    activities.extend(_match_habits(normalized))
    activities.extend(_match_energy(normalized))
    return activities


def activities_from_ai_json(raw: str) -> list[Activity]:
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("La respuesta de IA debe ser una lista de actividades.")

    activities: list[Activity] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        key = str(item.get("factor_key", "")).strip()
        if key not in EMISSION_FACTORS:
            continue
        factor = EMISSION_FACTORS[key]
        quantity = float(item.get("quantity", 1))
        activities.append(
            Activity(
                category=factor.category,
                description=key,
                quantity=quantity,
                unit=str(item.get("unit", factor.unit)),
            )
        )
    return activities
