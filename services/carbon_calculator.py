from collections import defaultdict

from models.carbon import Activity, CarbonEstimate
from services.emission_factors import EMISSION_FACTORS, get_factor


def calculate_footprint(
    activities: list[Activity],
    original_text: str,
    source: str,
    clarifications: list[str] | None = None,
) -> CarbonEstimate:
    breakdown: list[tuple[str, float]] = []
    category_accumulator: dict[str, float] = defaultdict(float)

    for activity in activities:
        factor = get_factor(activity.description)
        if factor is None:
            continue

        kg_co2 = round(activity.quantity * factor.kg_co2_per_unit, 3)
        label = f"{factor.label} ({activity.quantity:g} {activity.unit})"
        breakdown.append((label, kg_co2))
        category_accumulator[factor.category] += kg_co2

    total = round(sum(value for _, value in breakdown), 3)
    category_totals = tuple(
        sorted(category_accumulator.items(), key=lambda item: item[1], reverse=True)
    )

    return CarbonEstimate(
        activities=tuple(activities),
        breakdown=tuple(breakdown),
        total_kg_co2=total,
        original_text=original_text,
        source=source,
        category_totals=category_totals,
        clarifications=tuple(clarifications or ()),
    )


def format_factors_for_prompt() -> str:
    lines = []
    for factor in EMISSION_FACTORS.values():
        lines.append(
            f'- type: "{factor.key}" | category: "{factor.category}" | '
            f"{factor.label} ({factor.kg_co2_per_unit} kg CO2e por {factor.unit})"
        )
    return "\n".join(lines)
