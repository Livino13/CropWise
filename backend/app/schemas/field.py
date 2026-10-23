from pydantic import BaseModel, Field as PydField, field_validator
from typing import Optional, Literal
from datetime import datetime

SOIL_TYPES = {"Alluvial","Black","Red","Sandy","Loamy","Clayey","Laterite"}


class FieldCreate(BaseModel):
    name: str = PydField(min_length=1, max_length=100)
    latitude: Optional[float] = PydField(default=None, ge=-90, le=90)
    longitude: Optional[float] = PydField(default=None, ge=-180, le=180)
    area_hectares: Optional[float] = PydField(default=None, ge=0)
    soil_type: Optional[str] = PydField(default=None, max_length=50)
    soil_n: Optional[float] = PydField(default=None, ge=0, le=300)
    soil_p: Optional[float] = PydField(default=None, ge=0, le=300)
    soil_k: Optional[float] = PydField(default=None, ge=0, le=300)
    soil_ph: Optional[float] = PydField(default=None, ge=0, le=14)

    @field_validator("soil_type", mode="before")
    @classmethod
    def _soil_type(cls, v):
        if v == "":  # forms often submit '' for "no selection"
            return None
        if v is not None and v not in SOIL_TYPES:
            raise ValueError(f"soil_type must be one of {sorted(SOIL_TYPES)}")
        return v


class FieldUpdate(BaseModel):
    name: Optional[str] = PydField(default=None, min_length=1, max_length=100)
    latitude: Optional[float] = PydField(default=None, ge=-90, le=90)
    longitude: Optional[float] = PydField(default=None, ge=-180, le=180)
    area_hectares: Optional[float] = PydField(default=None, ge=0)
    soil_type: Optional[str] = PydField(default=None, max_length=50)
    soil_n: Optional[float] = PydField(default=None, ge=0, le=300)
    soil_p: Optional[float] = PydField(default=None, ge=0, le=300)
    soil_k: Optional[float] = PydField(default=None, ge=0, le=300)
    soil_ph: Optional[float] = PydField(default=None, ge=0, le=14)

    @field_validator("soil_type", mode="before")
    @classmethod
    def _soil_type(cls, v):
        if v == "":  # forms often submit '' for "no selection"
            return None
        if v is not None and v not in SOIL_TYPES:
            raise ValueError(f"soil_type must be one of {sorted(SOIL_TYPES)}")
        return v


class FieldResponse(BaseModel):
    id: int
    name: str
    latitude: Optional[float]
    longitude: Optional[float]
    area_hectares: Optional[float]
    soil_type: Optional[str]
    soil_n: Optional[float] = None
    soil_p: Optional[float] = None
    soil_k: Optional[float] = None
    soil_ph: Optional[float] = None
    soil_tested_at: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}
