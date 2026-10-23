from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.recommendation import Recommendation
from ..schemas.recommendation import FeedbackCreate

router = APIRouter(prefix="/api", tags=["feedback"])

@router.post("/feedback")
def submit_feedback(data: FeedbackCreate, db: Session = Depends(get_db)):
    rec = db.query(Recommendation).filter(Recommendation.id == data.recommendation_id).first()
    if not rec: raise HTTPException(404, "Recommendation not found")
    rec.actual_crop = data.actual_crop
    rec.actual_yield = data.actual_yield
    rec.feedback_rating = data.rating
    rec.feedback_notes = data.notes
    db.commit(); db.refresh(rec)
    return {"id": rec.id, "message": "Feedback saved"}

@router.get("/feedback/{rec_id}")
def get_feedback(rec_id: int, db: Session = Depends(get_db)):
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec: raise HTTPException(404, "Not found")
    return {"id": rec.id, "actual_crop": rec.actual_crop, "actual_yield": rec.actual_yield,
            "rating": rec.feedback_rating, "notes": rec.feedback_notes}
