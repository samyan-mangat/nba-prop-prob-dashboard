from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from datetime import date

PropName = Literal["pts", "reb", "ast", "stl", "blk", "tov", "fg3m"]
OpName = Literal[">=", ">", "over"]

class PlayerOut(BaseModel):
    id: int
    full_name: str
    team_abbrev: str | None = None

class PropLeg(BaseModel):
    player_id: int
    prop: PropName
    threshold: float
    op: OpName = ">="
    date: Optional[date] = None  # if specified, restrict history before date

class PropProbabilityRequest(BaseModel):
    leg: PropLeg

class PropProbabilityResponse(BaseModel):
    probability: float
    sample_size: int
    details: dict

class SGPRequest(BaseModel):
    legs: List[PropLeg] = Field(..., min_items=2)
    n_samples: int = 20000

class SGPLegResult(BaseModel):
    marginal: float
    threshold: float

class SGPResponse(BaseModel):
    joint_probability: float
    per_leg: List[SGPLegResult]
    kendall_tau: List[List[float]]
    sample_size: int

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    legs: List[PropLeg]
    probabilities: Optional[SGPResponse | PropProbabilityResponse] = None