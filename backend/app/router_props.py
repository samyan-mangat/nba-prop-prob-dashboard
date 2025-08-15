from fastapi import APIRouter, HTTPException
from .schemas import PropProbabilityRequest, PropProbabilityResponse, SGPRequest, SGPResponse
from .props import marginal_over_probability, build_joint_dataset
from .copula import gaussian_copula_joint_overprob

router = APIRouter(prefix="/props", tags=["props"])

@router.post("/probability", response_model=PropProbabilityResponse)
def prop_probability(req: PropProbabilityRequest):
    p, n, details = marginal_over_probability(req.leg.player_id, req.leg.prop, req.leg.threshold, req.leg.date)
    return {"probability": p, "sample_size": n, "details": details}

@router.post("/sgp", response_model=SGPResponse)
def sgp_probability(req: SGPRequest):
    legs = [l.model_dump() for l in req.legs]
    df = build_joint_dataset(legs, cutoff=None)
    if df.empty:
        # Fallback to independence using separate marginals
        marginals = []
        for leg in req.legs:
            p, n, _ = marginal_over_probability(leg.player_id, leg.prop, leg.threshold, leg.date)
            marginals.append(p)
        joint = 1.0
        for p in marginals:
            joint *= p
        return {
            "joint_probability": joint,
            "per_leg": [{"marginal": m, "threshold": leg.threshold} for m, leg in zip(marginals, req.legs)],
            "kendall_tau": [[1.0 if i==j else 0.0 for j in range(len(req.legs))] for i in range(len(req.legs))],
            "sample_size": 0,
        }
    joint, marginals, taus = gaussian_copula_joint_overprob(df, legs, n_samples=req.n_samples)
    return {
        "joint_probability": joint,
        "per_leg": [{"marginal": m, "threshold": leg.threshold} for m, leg in zip(marginals, req.legs)],
        "kendall_tau": taus,
        "sample_size": int(len(df)),
    }