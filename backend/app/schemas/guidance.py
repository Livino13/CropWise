from typing import Optional
from pydantic import BaseModel, Field


class GuidanceRequest(BaseModel):
    crop: str = Field(min_length=1, max_length=50)
    soil_type: Optional[str] = Field(default=None, max_length=50)
    field_id: Optional[int] = Field(default=None)


class StageDose(BaseModel):
    stage: str
    share: str
    products: str
    adjusted_amount: Optional[str] = None


class PestGuidance(BaseModel):
    pest: str
    treatment: str
    organic: str


class NPKTotal(BaseModel):
    n: float
    p: float
    k: float


class FertilizerGuidance(BaseModel):
    unit: str
    total_npk: Optional[NPKTotal] = None
    deficit: Optional[NPKTotal] = None
    personalized: bool = False
    stages: list[StageDose]
    soil_practices: list[str] = []
    ph_advice: Optional[str] = None
    notes: list[str] = []


class GuidanceResponse(BaseModel):
    crop: str
    soil_type_applied: Optional[str] = None
    fertilizer: FertilizerGuidance
    pests: list[PestGuidance]
    source_note: str
