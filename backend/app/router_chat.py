from fastapi import APIRouter
from .schemas import ChatRequest, ChatResponse
from .nlp import parse_query
from .router_props import sgp_probability, prop_probability
from .schemas import PropProbabilityRequest, SGPRequest

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/ask", response_model=ChatResponse)
def ask(req: ChatRequest):
    legs, rationale = parse_query(req.query)
    if not legs:
        return {"answer": "Sorry, I couldn't parse any player props from that.", "legs": []}

    if len(legs) == 1:
        p = prop_probability(PropProbabilityRequest(leg=legs[0]))
        ans = f"Pr[{legs[0].prop} ≥ {legs[0].threshold}] ≈ {p['probability']:.3f} (n={p['sample_size']})."
        return {"answer": ans + " " + rationale, "legs": legs, "probabilities": p}
    else:
        s = sgp_probability(SGPRequest(legs=legs))
        ans = f"Joint Pr ≈ {s['joint_probability']:.3f} across {len(legs)} legs."
        return {"answer": ans + " " + rationale, "legs": legs, "probabilities": s}