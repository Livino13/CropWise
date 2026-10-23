from typing import Optional

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    crop: str = Field(min_length=1, max_length=50)
    field_id: Optional[int] = None
    N: Optional[float] = Field(default=None, ge=0, le=200)
    P: Optional[float] = Field(default=None, ge=0, le=200)
    K: Optional[float] = Field(default=None, ge=0, le=250)
    temperature: Optional[float] = Field(default=None, ge=-10, le=60)
    humidity: Optional[float] = Field(default=None, ge=0, le=100)
    ph: Optional[float] = Field(default=None, ge=0, le=14)
    rainfall: Optional[float] = Field(default=None, ge=0, le=3500)
    soil_type: Optional[str] = Field(default=None, max_length=50)
    include_ai: bool = False


class PlanField(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class PlanBasis(BaseModel):
    weather: Optional[str] = None
    soil: Optional[str] = None
    personalized: bool = False
    notes: list[str] = []


class GrowingPlan(BaseModel):
    sowing: str
    harvest: str
    irrigation: str
    soil_prep: str
    risks: list[str] = []


class NPKPlan(BaseModel):
    n: float
    p: float
    k: float


class PlanProduct(BaseModel):
    name: str
    kg_per_ha: float
    kg_per_acre: float
    bags_per_acre: float


class PlanStage(BaseModel):
    stage: str
    share: str
    products: str
    urea_kg: Optional[float] = None
    dap_kg: Optional[float] = None
    mop_kg: Optional[float] = None


class FertilizerPlan(BaseModel):
    unit: str
    target: Optional[NPKPlan] = None
    available: Optional[NPKPlan] = None
    deficit: Optional[NPKPlan] = None
    products: list[PlanProduct] = []
    stages: list[PlanStage] = []
    personalized: bool = False
    ph_advice: Optional[str] = None
    notes: list[str] = []


class PlanPest(BaseModel):
    pest: str
    treatment: str
    organic: str


class CropPlanResponse(BaseModel):
    crop: str
    field: Optional[PlanField] = None
    personalized: bool = False
    basis: PlanBasis
    growing: GrowingPlan
    fertilizer: FertilizerPlan
    pests: list[PlanPest] = []
    ai_explanation: Optional[str] = None
