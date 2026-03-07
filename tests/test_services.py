import unittest

from app.models import CityTier, DeliverySegment, TriggerEvent, WeeklyQuoteRequest, WorkerProfile
from app.services import FraudEngine, RiskEngine, payout_for_trigger


class ServiceTests(unittest.TestCase):
    def sample_request(self) -> WeeklyQuoteRequest:
        profile = WorkerProfile(
            worker_id="wrk_101",
            age=29,
            delivery_segment=DeliverySegment.FOOD,
            city="Bengaluru",
            city_tier=CityTier.METRO,
            avg_weekly_income_inr=6200,
            avg_weekly_hours=54,
            preferred_zone_id="BLR-HSR",
        )
        return WeeklyQuoteRequest(
            profile=profile,
            historical_disruption_days_per_week=2,
            heat_risk_index=0.5,
            rain_flood_risk_index=0.7,
            pollution_risk_index=0.4,
        )

    def test_risk_score_in_range(self):
        req = self.sample_request()
        score = RiskEngine.compute_risk_score(req)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_premium_affordability_cap(self):
        req = self.sample_request()
        premium = RiskEngine.compute_weekly_premium(req)
        self.assertLessEqual(premium, 0.035 * req.profile.avg_weekly_income_inr)

    def test_fraud_score_blocks_suspicious_claims(self):
        trigger = TriggerEvent(
            zone_id="BLR-HSR",
            event_type="heavy_rain",
            severity=0.2,
            expected_hours_lost=6,
        )
        score = FraudEngine.fraud_score(trigger, gps_distance_km=8, duplicate_in_24h=True)
        self.assertGreaterEqual(score, 0.6)
        self.assertFalse(FraudEngine.is_claim_allowed(score))

    def test_payout_capped_by_sum_insured(self):
        req = self.sample_request()
        trigger = TriggerEvent(
            zone_id="BLR-HSR",
            event_type="curfew",
            severity=0.8,
            expected_hours_lost=40,
        )
        payout = payout_for_trigger(req.profile, trigger)
        self.assertLessEqual(payout, RiskEngine.compute_weekly_sum_insured(req.profile))


if __name__ == "__main__":
    unittest.main()
