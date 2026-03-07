from __future__ import annotations

from app.models import (
    ClaimDecision,
    CityTier,
    DeliverySegment,
    TriggerEvent,
    WeeklyQuoteRequest,
    WeeklyQuoteResponse,
    WorkerProfile,
)
from app.services import FraudEngine, RiskEngine, payout_for_trigger


def onboard(profile: WorkerProfile) -> dict[str, str]:
    return {
        "worker_id": profile.worker_id,
        "status": "onboarded",
        "message": "Worker profile captured for weekly risk pricing",
    }


def quote(request: WeeklyQuoteRequest) -> WeeklyQuoteResponse:
    risk_score = RiskEngine.compute_risk_score(request)
    premium = RiskEngine.compute_weekly_premium(request)
    sum_insured = RiskEngine.compute_weekly_sum_insured(request.profile)

    return WeeklyQuoteResponse(
        weekly_premium_inr=premium,
        weekly_sum_insured_inr=sum_insured,
        risk_score=risk_score,
        explanation=(
            "Weekly premium is based on delivery segment, city tier, disruption frequency "
            "and weather/environmental risk indices."
        ),
    )


def evaluate_claim(
    profile: WorkerProfile,
    trigger: TriggerEvent,
    gps_distance_km: float,
    duplicate_in_24h: bool = False,
) -> ClaimDecision:
    fraud_score = FraudEngine.fraud_score(trigger, gps_distance_km, duplicate_in_24h)
    allowed = FraudEngine.is_claim_allowed(fraud_score)

    payout = payout_for_trigger(profile, trigger) if allowed else 0
    decision = "approved" if allowed else "manual_review"
    reason = (
        "Parametric trigger hit and fraud score under threshold"
        if allowed
        else "High anomaly score; sent for manual review"
    )

    return ClaimDecision(
        trigger_eligible=trigger.severity >= 0.4,
        suggested_payout_inr=payout,
        fraud_score=fraud_score,
        decision=decision,
        reason=reason,
    )


if __name__ == "__main__":
    profile = WorkerProfile(
        worker_id="wrk_demo_1",
        age=28,
        delivery_segment=DeliverySegment.FOOD,
        city="Bengaluru",
        city_tier=CityTier.METRO,
        avg_weekly_income_inr=6000,
        avg_weekly_hours=52,
        preferred_zone_id="BLR-HSR",
    )

    request = WeeklyQuoteRequest(
        profile=profile,
        historical_disruption_days_per_week=2,
        heat_risk_index=0.6,
        rain_flood_risk_index=0.7,
        pollution_risk_index=0.4,
    )
    print("Onboarding:", onboard(profile))
    print("Quote:", quote(request))
