from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.recommendation import SoilInput, RecommendationResponse
from ..models.recommendation import Recommendation
from ..services.crop_plan import build_crop_plan
from pathlib import Path
import logging

logger = logging.getLogger("cropwise.recommend")

router = APIRouter(prefix="/api", tags=["recommend"])

# lazy model cache
_artifact = None

def get_artifact():
    global _artifact
    if _artifact is not None:
        return _artifact
    p = Path(__file__).parent.parent / "ml" / "artifacts" / "model.joblib"
    if p.exists():
        try:
            import joblib
            _artifact = joblib.load(str(p))
            return _artifact
        except Exception:
            logger.exception("Failed to load model artifact from %s — falling back to heuristic", p)
    else:
        logger.warning("Model artifact not found at %s — run train.py to enable ML predictions", p)
    return None


def reset_artifact_cache():
    """Drop the cached artifact (called after a retrain replaces the file)."""
    global _artifact
    _artifact = None

def limiting_factor(inp: SoilInput, top_crop: str) -> str | None:
    if inp.rainfall < 60 and top_crop in ("rice","jute","coconut"):
        return f"Low rainfall ({inp.rainfall}mm) may limit {top_crop} — consider irrigation"
    if inp.ph < 5.5:
        return f"Acidic soil pH {inp.ph} — consider liming for {top_crop}"
    if inp.ph > 8.0:
        return f"Alkaline soil pH {inp.ph} — may reduce nutrient uptake for {top_crop}"
    if inp.N < 20:
        return f"Low nitrogen ({inp.N}) — apply urea/organic matter for {top_crop}"
    return None

@router.post("/recommend", response_model=RecommendationResponse)
def recommend(inp: SoilInput, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    from ..models.field import Field as FieldModel
    from ..services.rerank import rerank, current_season
    from ..ml.rf_model import predict_top3, predict_yield

    artifact = get_artifact()
    soil = inp.model_dump(exclude={"field_id", "soil_type"})

    # resolve soil type: explicit input wins, else from the linked field
    field = db.get(FieldModel, inp.field_id) if inp.field_id is not None else None
    if inp.field_id is not None and field is None:
        raise HTTPException(status_code=404, detail="field not found")
    soil_type = inp.soil_type or (field.soil_type if field else None)

    # predict top-5 from the model (re-ranked down to top-3 below)
    used_model = False
    if artifact is not None:
        try:
            top = predict_top3(artifact, soil, top_n=5)
            used_model = True
        except Exception:
            logger.exception("predict_top3 failed — falling back to heuristic")
            top = _heuristic(soil)
    else:
        top = _heuristic(soil)

    season = current_season()
    top, adjustment_notes = rerank(top, soil_type=soil_type, season=season)
    top = top[:3]

    # expected yield from the feedback-trained regressor (None until enough data)
    for c in top:
        try:
            c["expected_yield"] = predict_yield(artifact, soil, c["crop"]) if artifact else None
        except Exception:
            c["expected_yield"] = None

    rec = Recommendation(
        field_id=inp.field_id,
        N=inp.N, P=inp.P, K=inp.K,
        temperature=inp.temperature, humidity=inp.humidity,
        ph=inp.ph, rainfall=inp.rainfall,
        top_crops=top,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    plan_inputs = {**soil, "soil_type": soil_type} if soil_type else soil
    guide = {}
    for c in top:
        try:
            plan = build_crop_plan(c["crop"], field=field, inputs=plan_inputs)
            growing = plan["growing"]
            guide[c["crop"]] = {
                "soil_prep": growing["soil_prep"],
                "sowing": growing["sowing"],
                "irrigation": growing["irrigation"],
                "harvest": growing["harvest"],
            }
        except Exception:
            logger.exception("Could not build a plan for %s", c["crop"])
            guide[c["crop"]] = {
                "soil_prep": "Prepare a fine, well-drained seedbed for your soil type.",
                "sowing": "Follow your regional sowing calendar for this crop.",
                "irrigation": "Irrigate at flowering and fruit or grain filling; avoid waterlogging.",
                "harvest": "Harvest when the crop reaches maturity for your variety.",
            }
    return RecommendationResponse(
        id=rec.id, top_crops=top, growing_guide=guide,
        limiting_factor=limiting_factor(inp, top[0]["crop"]),
        created_at=rec.created_at,
        model_used=used_model,
        adjustment_notes=adjustment_notes,
        season=season,
        soil_type_applied=soil_type,
        field_id=inp.field_id,
        N=inp.N,
        P=inp.P,
        K=inp.K,
        temperature=inp.temperature,
        humidity=inp.humidity,
        ph=inp.ph,
        rainfall=inp.rainfall,
    )

def _heuristic(soil: dict):
    """Fallback when model not available."""
    scores = {}
    # simple rules
    if soil["rainfall"] > 150: scores["rice"] = 0.85
    if soil["temperature"] > 25 and soil["humidity"] > 70: scores["coconut"] = 0.7
    if soil["ph"] > 6.5: scores["chickpea"] = 0.65
    scores.setdefault("maize", 0.6)
    scores.setdefault("cotton", 0.5)
    scores.setdefault("banana", 0.45)
    ranked = sorted(scores.items(), key=lambda x: -x[1])[:3]
    total = sum(s for _, s in ranked)
    return [{"crop": k, "confidence": v / total} for k, v in ranked]
