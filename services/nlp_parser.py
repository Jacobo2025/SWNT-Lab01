import json
import re

from models.carbon import Activity
from services.emission_factors import EMISSION_FACTORS, resolve_factor_key
from services.flight_estimator import estimate_flight_distance_km

DELIVERY_VAN_PATTERN = re.compile(
    r"(\d+)\s*(?:camionetas?|veh[ií]culos?|vans?)\b|"
    r"(?:usamos|utilizamos|operamos)\s+(\d+)\s*(?:camionetas?|veh[ií]culos?)",
    re.I,
)

ENERGY_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:kwh|kilovatios?-?hora?s?)\b",
    re.I,
)

GAS_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:m3|m³|metros c[uú]bicos)\b.*\b(?:gas|gas natural)\b|"
    r"\b(?:gas|gas natural)\b.*?(\d+(?:[.,]\d+)?)\s*(?:m3|m³)",
    re.I,
)

DISTANCE_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:km|kilómetros|kilometros)\b",
    re.I,
)

TRANSPORT_KEYWORDS: list[tuple[str, re.Pattern[str]]] = [
    ("camioneta_reparto", re.compile(r"\b(camioneta|reparto|delivery|van)\b", re.I)),
    ("coche", re.compile(r"\b(coche|auto|carro|taxi)\b", re.I)),
    ("bus", re.compile(r"\b(bus|autobús|autobus)\b", re.I)),
    ("avion", re.compile(r"\b(avión|avion|vuelo)\b", re.I)),
]

FOOD_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("carne_res", re.compile(r"\b(res|ternera|bistec)\b", re.I)),
    ("pescado", re.compile(r"\b(pescado|at[uú]n|salmon|salm[oó]n)\b", re.I)),
    ("pollo", re.compile(r"\b(pollo)\b", re.I)),
    ("huevos", re.compile(r"\b(huevos?)\b", re.I)),
    ("vegetariano", re.compile(r"\b(vegetariano|vegano|ensalada|legumbres)\b", re.I)),
    ("carne_general", re.compile(r"\b(carne|carnes)\b", re.I)),
]


def _parse_number(value: str) -> float:
    return float(value.replace(",", "."))


def _extract_count(pattern: re.Pattern[str], text: str) -> float | None:
    match = pattern.search(text)
    if not match:
        return None
    for group in match.groups():
        if group:
            return _parse_number(group)
    return None


def _match_business_energy(text: str) -> list[Activity]:
    kwh_match = ENERGY_PATTERN.search(text)
    if kwh_match and re.search(r"\b(electric|el[eé]ctric|luz|kwh|energ[ií]a)\b", text, re.I):
        factor = EMISSION_FACTORS["electricidad"]
        return [
            Activity(
                category=factor.category,
                description=factor.key,
                quantity=_parse_number(kwh_match.group(1)),
                unit=factor.unit,
            )
        ]
    return []


def _match_delivery_vans(text: str) -> list[Activity]:
    count = _extract_count(DELIVERY_VAN_PATTERN, text)
    if count is None:
        return []

    if not re.search(r"\b(camioneta|reparto|delivery|van|veh[ií]culo)\b", text, re.I):
        return []

    factor = EMISSION_FACTORS["camioneta_reparto"]
    return [
        Activity(
            category=factor.category,
            description=factor.key,
            quantity=count,
            unit=factor.unit,
        )
    ]


def _match_food(text: str) -> list[Activity]:
    activities: list[Activity] = []
    matched_keys: set[str] = set()

    for key, pattern in FOOD_PATTERNS:
        if not pattern.search(text):
            continue
        if key == "carne_general" and "carne_res" in matched_keys:
            continue

        factor = EMISSION_FACTORS[key]
        activities.append(
            Activity(
                category=factor.category,
                description=factor.key,
                quantity=1.0,
                unit=factor.unit,
            )
        )
        matched_keys.add(key)

    return activities


def _match_transport_distance(text: str) -> list[Activity]:
    distance = _extract_count(DISTANCE_PATTERN, text)
    if distance is None:
        distance = estimate_flight_distance_km(text)
    if distance is None:
        return []

    for key, pattern in TRANSPORT_KEYWORDS:
        if pattern.search(text):
            factor = EMISSION_FACTORS[key]
            unit = factor.unit if key != "camioneta_reparto" else "km"
            return [
                Activity(
                    category=factor.category,
                    description=key,
                    quantity=distance,
                    unit=unit,
                )
            ]
    return []


def _match_gas(text: str) -> list[Activity]:
    match = GAS_PATTERN.search(text)
    if not match:
        return []
    quantity = next(group for group in match.groups() if group)
    factor = EMISSION_FACTORS["gas_natural"]
    return [
        Activity(
            category=factor.category,
            description=factor.key,
            quantity=_parse_number(quantity),
            unit=factor.unit,
        )
    ]


def parse_natural_language(text: str) -> list[Activity]:
    normalized = text.strip()
    if not normalized:
        return []

    activities: list[Activity] = []
    activities.extend(_match_food(normalized))
    activities.extend(_match_business_energy(normalized))
    activities.extend(_match_delivery_vans(normalized))
    activities.extend(_match_gas(normalized))
    if not any(a.description == "camioneta_reparto" for a in activities):
        activities.extend(_match_transport_distance(normalized))
    return activities


def activities_from_ai_json(raw: str) -> list[Activity]:
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("La respuesta de IA debe ser una lista de actividades.")

    activities: list[Activity] = []
    for item in data:
        if not isinstance(item, dict):
            continue

        raw_type = str(item.get("type") or item.get("factor_key") or "").strip()
        factor_key = resolve_factor_key(raw_type)
        if factor_key is None:
            continue

        factor = EMISSION_FACTORS[factor_key]
        quantity = float(item.get("quantity", 1))
        activities.append(
            Activity(
                category=str(item.get("category", factor.category)),
                description=factor_key,
                quantity=quantity,
                unit=str(item.get("unit", factor.unit)),
            )
        )
    return activities
