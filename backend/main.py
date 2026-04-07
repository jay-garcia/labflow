import io
from datetime import datetime
from uuid import uuid4

import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import Job
from backend.validator import validate_experiment_csv


app = FastAPI(title="LabFlow API")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict[str, str | float | int | list[str] | None]:
    
    # Read the uploaded file into memory so pandas can load it as CSV.
    contents = await file.read()

    try:
        dataframe = pd.read_csv(io.BytesIO(contents))
    except Exception:
        return {
            "status": "invalid",
            "errors": ["The uploaded file could not be read as a CSV."],
        }

    # Use business logic to validate the actual data
    errors = validate_experiment_csv(dataframe)

    if errors:
        return {"status": "invalid", "errors": errors}

    job = Job(
        job_id=str(uuid4()),
        filename=file.filename or "uploaded_file.csv",
        status="processing",
        created_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        total_samples = int(len(dataframe))
        positive_samples = int((dataframe["result"] == "Positive").sum())
        positive_rate = positive_samples / total_samples if total_samples else 0.0

        job.status = "completed"
        job.total_samples = total_samples
        job.positive_rate = positive_rate
        job.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(job)

        return {
            "status": "valid",
            "job_id": job.job_id,
            "job_status": job.status,
            "error_message": job.error_message,
        }

    return {
        "status": "valid",
        "job_id": job.job_id,
        "job_status": job.status,
        "total_samples": job.total_samples,
        "positive_rate": job.positive_rate,
    }


@app.get("/job/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)) -> dict[str, str | float | int | None]:
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' was not found.")

    return {
        "job_id": job.job_id,
        "filename": job.filename,
        "status": job.status,
        "total_samples": job.total_samples,
        "positive_rate": job.positive_rate,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }
