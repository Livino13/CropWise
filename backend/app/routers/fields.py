from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from ..core.database import get_db
from ..models.field import Field
from ..schemas.field import FieldCreate, FieldUpdate, FieldResponse

router = APIRouter(prefix="/api/fields", tags=["fields"])

@router.get("", response_model=list[FieldResponse])
def list_fields(db: Session = Depends(get_db)):
    return db.query(Field).order_by(Field.created_at.desc()).all()

@router.post("", response_model=FieldResponse, status_code=201)
def create_field(data: FieldCreate, db: Session = Depends(get_db)):
    payload = data.model_dump()
    if payload.get("soil_n") is not None:
        payload["soil_tested_at"] = datetime.now(timezone.utc)
    f = Field(**payload)
    db.add(f); db.commit(); db.refresh(f)
    return f

@router.get("/{field_id}", response_model=FieldResponse)
def get_field(field_id: int, db: Session = Depends(get_db)):
    f = db.query(Field).filter(Field.id == field_id).first()
    if not f: raise HTTPException(404, "Field not found")
    return f

@router.put("/{field_id}", response_model=FieldResponse)
def update_field(field_id: int, data: FieldUpdate, db: Session = Depends(get_db)):
    f = db.query(Field).filter(Field.id == field_id).first()
    if not f: raise HTTPException(404, "Field not found")
    updates = data.model_dump(exclude_unset=True)
    if updates.get("soil_n") is not None:
        updates["soil_tested_at"] = datetime.now(timezone.utc)
    for k, v in updates.items():
        setattr(f, k, v)
    db.commit(); db.refresh(f)
    return f

@router.delete("/{field_id}", status_code=204)
def delete_field(field_id: int, db: Session = Depends(get_db)):
    f = db.query(Field).filter(Field.id == field_id).first()
    if not f: raise HTTPException(404, "Field not found")
    db.delete(f); db.commit()
