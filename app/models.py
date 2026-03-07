from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DeliverySegment(str, Enum):
    FOOD = "food"
    GROCERY = "grocery"
    ECOMMERCE = "ecommerce"


class CityTier(str, Enum):
    METRO = "metro"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


@dataclass
class WorkerProfile:
    worker_id: str
    age: int
    delivery_segment: DeliverySegment
    city: str
    city_tier: CityTier
    avg_weekly_income_inr: float
    avg_weekly_hours: float
    preferred_zone_id: str


@dataclass
class WeeklyQuoteRequest:
    profile: WorkerProfile
    historical_disruption_days_per_week: float
    heat_risk_index: float
    rain_flood_risk_index: float
    pollution_risk_index: float


@dataclass
class WeeklyQuoteResponse:
    weekly_premium_inr: float
    weekly_sum_insured_inr: float
    risk_score: float
    explanation: str


@dataclass
class TriggerEvent:
    zone_id: str
    event_type: str
    severity: float
    expected_hours_lost: float


@dataclass
class ClaimDecision:
    trigger_eligible: bool
    suggested_payout_inr: float
    fraud_score: float
    decision: str
    reason: str
