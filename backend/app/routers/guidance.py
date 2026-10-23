import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.field import Field
from ..schemas.guidance import (
    FertilizerGuidance,
    GuidanceRequest,
    GuidanceResponse,
    NPKTotal,
    PestGuidance,
    StageDose,
)
from ..services.agronomy import (
    CROP_NPK_TARGET,
    DOSE_UNIT,
    FERTILIZER_STAGES,
    PEST_GUIDE,
    SOIL_FERT_PRACTICE,
    SOURCE_NOTE,
)

router = APIRouter(prefix="/api", tags=["guidance"])

_SHARE_FRACTION = re.compile(r"(\d+)\s*%|(\d+)\s*/\s*(\d+)|half|third|quarter", re.IGNORECASE)


def _stage_fraction(share: str) -> Optional[float]:
    m = _SHARE_FRACTION.search(share)
    if not m:
        return None
    if m.group(1):
        return int(m.group(1)) / 100.0
    if m.group(2) and m.group(3):
        return int(m.group(2)) / int(m.group(3))
    word = m.group(0).lower()
    return {"half": 0.5, "third": 1 / 3, "quarter": 0.25}.get(word)


@router.post("/guidance", response_model=GuidanceResponse)
def guidance(req: GuidanceRequest, db: Session = Depends(get_db)):
    crop = req.crop.lower().strip().replace(" ", "_")
    if crop not in CROP_NPK_TARGET or crop not in PEST_GUIDE:
        raise HTTPException(
            status_code=404,
            detail=f"No guidance for '{req.crop}'. This tool covers {len(CROP_NPK_TARGET)} crops.",
        )

    field: Optional[Field] = None
    if req.field_id is not None:
        field = db.get(Field, req.field_id)
        if field is None:
            raise HTTPException(status_code=404, detail="Field not found")

    soil_type = (req.soil_type or getattr(field, "soil_type", None) or "").strip()
    soil_canon = {k.lower(): k for k in SOIL_FERT_PRACTICE}
    soil_type_applied = soil_canon.get(soil_type.lower())

    unit = DOSE_UNIT.get(crop, "kg/ha")
    target = CROP_NPK_TARGET.get(crop)
    notes: list[str] = []
    deficit = None
    personalized = False
    ph_advice = None

    if soil_type_applied is None and soil_type:
        notes.append(f"Soil type '{soil_type}' is not in our practice table; generic advice shown.")
    if field is None and req.soil_type is None:
        notes.append("Pass a field_id (with a soil test) or soil_type for personalized advice.")

    if field is not None and field.soil_ph is not None:
        if field.soil_ph < 5.5:
            ph_advice = (
                f"Soil pH {field.soil_ph} is acidic — apply agricultural lime at 1–2 t/ha before "
                "the season and re-test; liming improves nutrient availability."
            )
        elif field.soil_ph > 8.0:
            ph_advice = (
                f"Soil pH {field.soil_ph} is alkaline — apply gypsum 2–4 t/ha or sulphur 100–200 kg/ha "
                "to lower pH over time; use acidifying fertilizers (e.g. ammonium forms)."
            )
        else:
            ph_advice = f"Soil pH {field.soil_ph} is in a good range for most crops."

    if target is not None and unit == "kg/ha" and field is not None:
        has_test = any(v is not None for v in (field.soil_n, field.soil_p, field.soil_k))
        if has_test:
            deficit_n = max(0.0, target["n"] - (field.soil_n or 0.0))
            deficit_p = max(0.0, target["p"] - (field.soil_p or 0.0))
            deficit_k = max(0.0, target["k"] - (field.soil_k or 0.0))
            deficit = NPKTotal(n=round(deficit_n, 1), p=round(deficit_p, 1), k=round(deficit_k, 1))
            personalized = True
            notes.append(
                f"Deficit = crop target minus your soil test "
                f"(N {field.soil_n} / P {field.soil_p} / K {field.soil_k} kg/ha available)."
            )

    stages: list[StageDose] = []
    for s in FERTILIZER_STAGES.get(crop, []):
        adjusted = None
        if personalized and deficit is not None:
            frac = _stage_fraction(s["share"])
            if frac is not None and target and target["n"] > 0:
                grams_n = deficit.n * frac
                adjusted = f"≈{grams_n:.0f} kg N over this stage"
        stages.append(
            StageDose(stage=s["stage"], share=s["share"], products=s["products"], adjusted_amount=adjusted)
        )

    fertilizer = FertilizerGuidance(
        unit=unit,
        total_npk=NPKTotal(**target) if target else None,
        deficit=deficit,
        personalized=personalized,
        stages=stages,
        soil_practices=SOIL_FERT_PRACTICE.get(soil_type_applied, []) if soil_type_applied else [],
        ph_advice=ph_advice,
        notes=notes,
    )

    pests = [PestGuidance(**p) for p in PEST_GUIDE.get(crop, [])]

    return GuidanceResponse(
        crop=crop,
        soil_type_applied=soil_type_applied,
        fertilizer=fertilizer,
        pests=pests,
        source_note=SOURCE_NOTE,
    )
