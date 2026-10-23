"""Personalized crop plan endpoint.

Computes growing and fertilizer guidance from the field's soil values, the
7-day Open-Meteo forecast and (when needed) modelled SoilGrids pH. Gemini is
only used to narrate the computed plan; it never creates the numbers.
"""
import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.field import Field
from ..schemas.plan import CropPlanResponse, PlanRequest
from ..services.crop_plan import build_crop_plan
from ..services.crop_profiles import CROP_PROFILES
from ..services.field_data import fetch_soil_properties, fetch_weather
from ..services.plan_narrative import explain_plan

router = APIRouter(prefix="/api", tags=["plan"])
logger = logging.getLogger(__name__)


def _normalize_crop(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


@router.post("/plan", response_model=CropPlanResponse)
async def crop_plan(req: PlanRequest, db: Session = Depends(get_db)):
    crop = _normalize_crop(req.crop)
    if crop not in CROP_PROFILES:
        raise HTTPException(status_code=404, detail="crop not found")

    field = db.get(Field, req.field_id) if req.field_id is not None else None
    if req.field_id is not None and field is None:
        raise HTTPException(status_code=404, detail="field not found")

    inputs = req.model_dump(
        exclude={"crop", "field_id", "include_ai"}, exclude_none=True
    )

    weather = None
    soil_est = None
    if field is not None and field.latitude is not None and field.longitude is not None:
        tasks = [fetch_weather(field.latitude, field.longitude)]
        needs_soilgrids = (
            field.soil_ph is None
            and req.ph is None
        )
        if needs_soilgrids:
            tasks.append(fetch_soil_properties(field.latitude, field.longitude))
        results = await asyncio.gather(*tasks)
        weather = results[0]
        if len(results) > 1:
            soil_est = results[1]

    try:
        plan = build_crop_plan(
            crop,
            field=field,
            inputs=inputs,
            weather=weather,
            soil_est=soil_est,
        )
    except Exception:
        logger.exception("Failed to build plan for %s", crop)
        raise HTTPException(
            status_code=500,
            detail="Could not calculate a plan for this crop. Please try again.",
        )

    if req.include_ai:
        plan["ai_explanation"] = await explain_plan(plan)
    return plan
