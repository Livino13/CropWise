from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=True)
    N = Column(Float, nullable=False)
    P = Column(Float, nullable=False)
    K = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False)
    top_crops = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    actual_crop = Column(String(50), nullable=True)
    actual_yield = Column(Float, nullable=True)
    feedback_rating = Column(Integer, nullable=True)
    feedback_notes = Column(Text, nullable=True)
    field = relationship("Field", back_populates="recommendations")
