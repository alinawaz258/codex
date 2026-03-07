# Suraksha GigProtect (Phase 1 Submission)

AI-enabled **parametric income protection** for India’s gig delivery workforce.

> **Persona focus:** Food delivery partners (Zomato/Swiggy).  
> **Coverage scope:** Loss of income only due to external disruptions.  
> **Explicit exclusions:** Health, life, accidents, and vehicle repair coverage.

## Problem & Approach
Delivery partners can lose 20-30% income during heavy rain, heatwaves, pollution spikes, and sudden local closures. Suraksha GigProtect uses a **weekly parametric model**: if a verified disruption event happens in a worker’s active zone, the system auto-computes eligible lost-income payout.

## Weekly Premium Model (Mandatory Constraint)
Prototype pricing:

`weekly_premium = base_by_segment × city_tier_multiplier × risk_multiplier`

Risk multiplier is derived from an explainable risk score (0-100) using:
- heat risk index
- rain/flood risk index
- pollution risk index
- historical disruption days/week

Guardrail: weekly premium capped at **3.5% of weekly income**.

## Parametric Triggers
- **Environmental:** heavy rain, flood risk, extreme heat, severe pollution
- **Social:** curfew, strike, zone closure

Claims are event-driven, not bill-driven.

## AI/ML Plan
### Phase 1 (this repo)
- Explainable scoring prototype for dynamic weekly pricing
- Rule-based fraud heuristics (GPS mismatch, duplicate claims, anomaly patterns)

### Phase 2
- Train disruption-probability model for zone-wise dynamic weekly repricing
- Build automated trigger ingestion from weather/mock platform feeds

### Phase 3
- Advanced fraud detection (GPS spoof patterns, sequence anomalies)
- Admin dashboard with claim forecasts and loss-ratio analytics

## Current Code (Initiation Build)
This phase-1 codebase provides core domain logic and test coverage for:
1. Worker onboarding data model
2. Weekly quote generation (premium + sum insured + risk score)
3. Trigger-based claim evaluation
4. Fraud score gating
5. Payout computation for lost-income hours

## Repository Structure
```text
.
├── app/
│   ├── main.py        # callable workflow functions + demo runner
│   ├── models.py      # core dataclasses and enums
│   └── services.py    # risk, premium, fraud, payout logic
├── tests/
│   └── test_services.py
├── requirements.txt
└── README.md
```

## Run
```bash
python -m app.main
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Phase-1 Deliverable Checklist Mapping
- ✅ Persona-based scenarios and workflow
- ✅ Weekly premium and parametric trigger strategy
- ✅ AI/ML integration roadmap
- ✅ Executable initiation code and tests
- ✅ Ready foundation for Phase 2 automation
