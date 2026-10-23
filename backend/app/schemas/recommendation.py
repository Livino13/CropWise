from pydantic import BaseModel, Field as PydField
from typing import Optional
from datetime import datetime


class SoilInput(BaseModel):
    N: float = PydField(ge=0, le=200, description="Nitrogen kg/ha")
    P: float = PydField(ge=0, le=200, description="Phosphorus kg/ha")
    K: float = PydField(ge=0, le=250, description="Potassium kg/ha")
    temperature: float = PydField(ge=-10, le=60, description="Temperature °C")
    humidity: float = PydField(ge=0, le=100, description="Humidity %")
    ph: float = PydField(ge=0, le=14, description="Soil pH")
    rainfall: float = PydField(ge=0, le=3500, description="Rainfall mm")
    field_id: Optional[int] = None
    soil_type: Optional[str] = PydField(default=None, description="Optional soil type for re-ranking")


class CropResult(BaseModel):
    crop: str
    confidence: float
    model_confidence: Optional[float] = None
    adjustments: Optional[list[str]] = None
    expected_yield: Optional[float] = PydField(default=None, description="Estimated yield t/ha if yield model available")


class RecommendationResponse(BaseModel):
    id: int
    top_crops: list[CropResult]
    growing_guide: dict
    limiting_factor: Optional[str] = None
    created_at: datetime
    model_used: bool = True
    adjustment_notes: list[str] = []
    season: Optional[str] = None
    soil_type_applied: Optional[str] = None
    field_id: Optional[int] = None
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float


class HistoryItem(BaseModel):
    id: int
    field_id: Optional[int]
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    top_crops: list[dict]
    created_at: datetime
    actual_crop: Optional[str] = None
    actual_yield: Optional[float] = None
    feedback_rating: Optional[int] = None
    feedback_notes: Optional[str] = None
    model_config = {"from_attributes": True}


class HistoryUpdate(BaseModel):
    field_id: Optional[int] = PydField(default=None, description="Link recommendation to a field")


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
    limit: int
    offset: int


class FeedbackCreate(BaseModel):
    recommendation_id: int
    actual_crop: Optional[str] = None
    actual_yield: Optional[float] = None
    rating: Optional[int] = PydField(default=None, ge=1, le=5)
    notes: Optional[str] = None
