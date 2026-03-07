from __future__ import annotations

from app.models import TriggerEvent, WeeklyQuoteRequest, WorkerProfile


SEGMENT_BASE_PREMIUM = {
    "food": 49,
    "grocery": 45,
    "ecommerce": 39,
}

CITY_TIER_MULTIPLIER = {
    "metro": 1.2,
    "tier_2": 1.0,
    "tier_3": 0.9,
}


class RiskEngine:
    """Simple explainable scoring model for Phase 1 prototyping.

    This is intentionally transparent for judges and can later be replaced
    with a trained model in Phase 2/3.
    """

    @staticmethod
    def compute_risk_score(request: WeeklyQuoteRequest) -> float:
        weather_score = (
            0.4 * request.heat_risk_index
            + 0.45 * request.rain_flood_risk_index
            + 0.15 * request.pollution_risk_index
        )
        disruption_frequency = request.historical_disruption_days_per_week / 7

        score = 100 * (0.7 * weather_score + 0.3 * disruption_frequency)
        return round(min(max(score, 0), 100), 2)

    @staticmethod
    def compute_weekly_premium(request: WeeklyQuoteRequest) -> float:
        profile = request.profile
        base = SEGMENT_BASE_PREMIUM[profile.delivery_segment.value]
        tier_multiplier = CITY_TIER_MULTIPLIER[profile.city_tier.value]
        risk_score = RiskEngine.compute_risk_score(request)

        # Risk loading from 0% to 100% for scores 0-100.
        risk_multiplier = 1 + (risk_score / 100)
        premium = base * tier_multiplier * risk_multiplier

        # Affordability cap: max 3.5% of weekly income.
        affordability_cap = 0.035 * profile.avg_weekly_income_inr
        return round(min(premium, affordability_cap), 2)

    @staticmethod
    def compute_weekly_sum_insured(profile: WorkerProfile) -> float:
        # Protect up to 65% of weekly earnings from external disruption.
        return round(0.65 * profile.avg_weekly_income_inr, 2)


class FraudEngine:
    """Prototype fraud heuristics for automated claim gating."""

    @staticmethod
    def fraud_score(trigger: TriggerEvent, gps_distance_km: float, duplicate_in_24h: bool) -> float:
        score = 0.0
        if gps_distance_km > 4:
            score += 0.45
        if duplicate_in_24h:
            score += 0.35
        if trigger.severity < 0.3 and trigger.expected_hours_lost > 5:
            score += 0.3
        return round(min(score, 1.0), 2)

    @staticmethod
    def is_claim_allowed(score: float) -> bool:
        return score < 0.6


def payout_for_trigger(profile: WorkerProfile, trigger: TriggerEvent) -> float:
    hourly_rate = profile.avg_weekly_income_inr / max(profile.avg_weekly_hours, 1)
    raw_loss = hourly_rate * trigger.expected_hours_lost
    capped_loss = min(raw_loss, RiskEngine.compute_weekly_sum_insured(profile))
    return round(max(capped_loss, 0), 2)
