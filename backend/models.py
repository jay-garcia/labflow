from sqlalchemy import Column, DateTime, Float, Integer, String

from backend.database import Base


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True, unique=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False)
    total_samples = Column(Integer, nullable=True)
    positive_rate = Column(Float, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
