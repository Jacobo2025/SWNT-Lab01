from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Activity:
    category: str
    description: str
    quantity: float
    unit: str


@dataclass(frozen=True)
class CarbonEstimate:
    activities: tuple[Activity, ...]
    breakdown: tuple[tuple[str, float], ...]
    total_kg_co2: float
    original_text: str
    source: str


@dataclass
class DailyEntry:
    timestamp: datetime
    text: str
    estimate: CarbonEstimate
    notes: str = field(default="")
