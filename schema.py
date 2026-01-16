from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator

class Targeting(BaseModel):
    locations: List[str] = Field(..., description="Target locations")
    age_min: int = Field(default=18, ge=13)
    age_max: int = Field(default=65, le=65)
    interests: List[str] = Field(default_factory=list)

class AdSet(BaseModel):
    id: str = Field(..., description="Unique identifier for the ad set")
    name: str
    status: Literal["ACTIVE", "PAUSED"] = "PAUSED"
    budget_daily: int = Field(..., gt=0)
    targeting: Targeting

    @validator('budget_daily')
    def check_min_budget(cls, v):
        if v < 1000:
            raise ValueError('Daily budget must be at least 1,000 KRW')
        return v

class Campaign(BaseModel):
    id: str = Field(..., description="Unique identifier for the campaign")
    name: str
    objective: Literal["OUTCOME_SALES", "OUTCOME_TRAFFIC", "OUTCOME_AWARENESS"]
    status: Literal["ACTIVE", "PAUSED"] = "PAUSED"
    ad_sets: List[AdSet] = Field(default_factory=list)

class MarketingPlan(BaseModel):
    version: str
    campaigns: List[Campaign]
