import json

from openai import OpenAI

from models.carbon import CarbonEstimate
from services.carbon_calculator import calculate_footprint, format_factors_for_prompt
from models.carbon import Activity
from services.nlp_parser import activities_from_ai_json, parse_natural_language
from utils.config import AppConfig

SYSTEM_PROMPT = """Eres un asistente ambiental experto en huella de carbono.
Analiza el texto del usuario y extrae actividades concretas del día.

Responde SOLO con un JSON válido con esta forma:
{{"activities": [{{"factor_key": "...", "quantity": 1, "unit": "..."}}]}}

Cada actividad debe incluir:
- "factor_key": una de las claves permitidas
- "quantity": número (por ejemplo km recorridos o comidas)
- "unit": unidad (km, comida, kwh)

Factores permitidos:
{ factors }

Reglas:
- Si menciona carne sin especificar tipo, usa "carne_general".
- Para transporte terrestre, extrae los kilómetros del texto; si no hay cifra, usa 5 km como estimado razonable.
- Para vuelos entre ciudades sin km explícitos, estima la distancia aérea en km (ej. Bogotá-París ≈ 8600 km).
- Si menciona avión/vuelo sin ciudades ni km, usa 1500 km como vuelo medio.
- Para cigarrillos usa "cigarrillo" con quantity = número de cigarrillos.
- Para comidas, quantity=1 por cada comida mencionada.
- No incluyas explicaciones fuera del JSON.
"""


class CarbonAIService:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._client = OpenAI(api_key=config.openai_api_key) if config.has_ai else None

    def estimate(self, text: str) -> CarbonEstimate:
        if self._client is not None:
            try:
                activities = self._parse_with_ai(text)
                if activities:
                    return calculate_footprint(activities, text, source="IA (OpenAI)")
            except Exception:
                pass

        activities = parse_natural_language(text)
        return calculate_footprint(activities, text, source="Análisis local")

    def _parse_with_ai(self, text: str) -> list[Activity]:
        prompt = SYSTEM_PROMPT.format(factors=format_factors_for_prompt())
        response = self._client.chat.completions.create(
            model=self._config.openai_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)
        activities_raw = payload.get("activities", [])
        return activities_from_ai_json(json.dumps(activities_raw))
