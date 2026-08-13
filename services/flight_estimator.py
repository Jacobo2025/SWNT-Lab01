import math
import re
import unicodedata


# Coordenadas aproximadas de ciudades frecuentes en consultas de huella de carbono.
CITY_COORDINATES: dict[str, tuple[float, float]] = {
    "bogota": (4.711, -74.0721),
    "medellin": (6.2476, -75.5658),
    "cali": (3.4516, -76.532),
    "barranquilla": (10.9685, -74.7813),
    "cartagena": (10.391, -75.4794),
    "paris": (48.8566, 2.3522),
    "madrid": (40.4168, -3.7038),
    "londres": (51.5074, -0.1278),
    "london": (51.5074, -0.1278),
    "new york": (40.7128, -74.006),
    "nueva york": (40.7128, -74.006),
    "miami": (25.7617, -80.1918),
    "mexico": (19.4326, -99.1332),
    "ciudad de mexico": (19.4326, -99.1332),
    "lima": (-12.0464, -77.0428),
    "buenos aires": (-34.6037, -58.3816),
    "santiago": (-33.4489, -70.6693),
    "barcelona": (41.3851, 2.1734),
    "berlin": (52.52, 13.405),
    "roma": (41.9028, 12.4964),
    "tokio": (35.6762, 139.6503),
    "tokyo": (35.6762, 139.6503),
}

CITY_ROUTE_PATTERN = re.compile(
    r"(?:de|desde|from)\s+([a-záéíóúüñ\s]+?)\s+(?:a|hasta|to)\s+"
    r"([a-záéíóúüñ\s]+?)(?:\s+en|\s+con|,|\.|$)",
    re.I,
)

FLIGHT_KEYWORDS = re.compile(r"\b(avión|avion|vuelo|vol[eé]|viaj[eé])\b", re.I)


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.strip().lower())
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def _resolve_city(name: str) -> str | None:
    cleaned = _normalize_text(name)
    if cleaned in CITY_COORDINATES:
        return cleaned

    for city in CITY_COORDINATES:
        if city in cleaned or cleaned in city:
            return city
    return None


def haversine_km(origin: tuple[float, float], destination: tuple[float, float]) -> float:
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius_km = 6371.0

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(radius_km * c, 1)


def estimate_flight_distance_km(text: str) -> float | None:
    if not FLIGHT_KEYWORDS.search(text):
        return None

    match = CITY_ROUTE_PATTERN.search(text)
    if not match:
        return None

    origin_city = _resolve_city(match.group(1))
    destination_city = _resolve_city(match.group(2))
    if origin_city is None or destination_city is None:
        return None

    origin_coords = CITY_COORDINATES[origin_city]
    destination_coords = CITY_COORDINATES[destination_city]
    return haversine_km(origin_coords, destination_coords)
