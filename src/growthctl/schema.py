from pydantic import BaseModel, Field


class Targeting(BaseModel):
    locations: list[str] = Field(..., description="Target locations")
    age_min: int = Field(default=18, ge=13)
    age_max: int = Field(default=65, le=65)
    interests: list[str] = Field(default_factory=list)


class AdSet(BaseModel):
    id: str = Field(..., description="Unique identifier for the ad set")
    name: str
    status: str = "PAUSED"
    budget_daily: int = Field(
        ...,
        ge=0,
        description="Daily budget in account's smallest currency unit (e.g., cents for USD, won for KRW)",
    )
    targeting: Targeting


class Campaign(BaseModel):
    id: str = Field(..., description="Unique identifier for the campaign")
    name: str
    objective: str
    status: str = "PAUSED"
    ad_sets: list[AdSet] = Field(default_factory=list)


class MarketingPlan(BaseModel):
    version: str
    campaigns: list[Campaign]
