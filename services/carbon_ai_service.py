import json

from openai import OpenAI

from models.carbon import Activity, CarbonEstimate
from services.carbon_calculator import calculate_footprint, format_factors_for_prompt
from services.nlp_parser import activities_from_ai_json, parse_natural_language
from services.recommendations import generate_recommendations
from utils.config import AppConfig


def _supplement_activities(
    primary: list[Activity], supplemental: list[Activity]
) -> list[Activity]:
    existing_types = {activity.description for activity in primary}
    merged = list(primary)
    for activity in supplemental:
        if activity.description not in existing_types:
            merged.append(activity)
            existing_types.add(activity.description)
    return merged

SYSTEM_PROMPT = """Eres un asistente de sostenibilidad para pequeños negocios.
Convierte descripciones en lenguaje natural a actividades estructuradas de huella de carbono.

Responde SOLO con JSON válido en esta forma:
{{
  "activities": [
    {{
      "category": "energy|transport|waste|water|food",
      "type": "electricidad|camioneta_reparto|carne_general|pollo|...",
      "quantity": 0,
      "unit": "kWh|vehicles|km|m3|kg|meal"
    }}
  ],
  "clarifications": ["pregunta si falta información crítica"]
}}

Tipos permitidos (usa el campo "type" exactamente):
{ factors }

Reglas:
- Extrae TODAS las actividades mencionadas en el texto, aunque pertenezcan a categorías distintas.
- Una misma entrada puede incluir alimentación y transporte simultáneamente.
- Si mencionan varios alimentos (carne, pollo, pescado, huevos), crea una actividad por cada uno con quantity=1 y unit "meal".
- Si mencionan camionetas/vehículos de reparto, usa type "camioneta_reparto" y unit "vehicles".
- Si mencionan kWh o electricidad, usa type "electricidad" y unit "kWh".
- Si mencionan km en auto/coche, usa type "coche" y unit "km".
- Si la entrada es ambigua o falta cantidad clave, deja activities vacío y agrega preguntas en clarifications.
- No inventes datos que el usuario no mencionó.
- No incluyas texto fuera del JSON.
"""


class CarbonAIService:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._client = OpenAI(api_key=config.openai_api_key) if config.has_ai else None

    def estimate(self, text: str) -> CarbonEstimate:
        clarifications: list[str] = []

        if self._client is not None:
            try:
                activities, clarifications = self._parse_with_ai(text)
                local_activities = parse_natural_language(text)
                activities = _supplement_activities(activities, local_activities)
                if activities:
                    estimate = calculate_footprint(
                        activities, text, source="IA (OpenAI)", clarifications=clarifications
                    )
                    return self._with_recommendations(estimate)
                if clarifications:
                    return calculate_footprint([], text, source="IA (OpenAI)", clarifications=clarifications)
            except Exception:
                pass

        activities = parse_natural_language(text)
        if not activities:
            clarifications = [
                "Indica cantidades concretas, por ejemplo: "
                "'200 kWh de electricidad' o '5 camionetas de reparto'."
            ]

        estimate = calculate_footprint(
            activities,
            text,
            source="Análisis local",
            clarifications=clarifications if not activities else [],
        )
        return self._with_recommendations(estimate)

    def _with_recommendations(self, estimate: CarbonEstimate) -> CarbonEstimate:
        recommendations = generate_recommendations(estimate)
        return CarbonEstimate(
            activities=estimate.activities,
            breakdown=estimate.breakdown,
            total_kg_co2=estimate.total_kg_co2,
            original_text=estimate.original_text,
            source=estimate.source,
            category_totals=estimate.category_totals,
            recommendations=recommendations,
            clarifications=estimate.clarifications,
        )

    def _parse_with_ai(self, text: str) -> tuple[list[Activity], list[str]]:
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
        clarifications = [
            str(item).strip()
            for item in payload.get("clarifications", [])
            if str(item).strip()
        ]
        return activities_from_ai_json(json.dumps(activities_raw)), clarifications
