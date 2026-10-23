from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..core.database import get_db
from ..models.recommendation import Recommendation
from ..models.field import Field as FieldModel
from ..schemas.recommendation import HistoryItem, HistoryResponse, HistoryUpdate

router = APIRouter(prefix="/api", tags=["history"])

@router.get("/history")
def get_history(
    crop: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(Recommendation).order_by(Recommendation.created_at.desc())
    if from_date:
        q = q.filter(Recommendation.created_at >= from_date)
    if to_date:
        q = q.filter(Recommendation.created_at <= to_date)
    # total before crop filter — for JSON crop filter count after
    total_q = q
    if crop:
        # crop filter is JSON-inside; apply in Python but count correctly
        all_rows = total_q.all()
        filtered = [r for r in all_rows if any(c.get("crop") == crop for c in (r.top_crops or []))]
        total = len(filtered)
        items = filtered[offset: offset + limit]
    else:
        total = q.count()
        items = q.offset(offset).limit(limit).all()
    # Return paginated envelope; also backwards-compat: clients expecting a bare array
    # can unwrap `items`, but we return the envelope per spec.
    return HistoryResponse(items=items, total=total, limit=limit, offset=offset)


@router.patch("/history/{rec_id}")
def update_history(rec_id: int, data: HistoryUpdate, db: Session = Depends(get_db)):
    """Link an existing recommendation to a field (used by 'Save to field')."""
    rec = db.get(Recommendation, rec_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if data.field_id is not None and db.get(FieldModel, data.field_id) is None:
        raise HTTPException(status_code=404, detail="field not found")
    rec.field_id = data.field_id
    db.commit()
    db.refresh(rec)
    return {"id": rec.id, "field_id": rec.field_id}
