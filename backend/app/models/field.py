from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base

class Field(Base):
    __tablename__ = "fields"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    area_hectares = Column(Float, nullable=True)
    soil_type = Column(String(50), nullable=True)
    # latest lab soil-test results (NPK kg/ha + pH)
    soil_n = Column(Float, nullable=True)
    soil_p = Column(Float, nullable=True)
    soil_k = Column(Float, nullable=True)
    soil_ph = Column(Float, nullable=True)
    soil_tested_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    recommendations = relationship("Recommendation", back_populates="field", cascade="all, delete-orphan")
