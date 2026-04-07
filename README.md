# LabFlow

LabFlow is a simple internal-tool style project for uploading experiment CSV files,
validating them, processing them, and viewing status/results.

This version includes:

- a FastAPI backend with a `/health` endpoint
- a FastAPI `/upload` endpoint for CSV validation and processing
- a FastAPI `/job/{job_id}` endpoint for reading saved job results
- a Streamlit frontend for uploading CSV files and viewing validation results
- SQLite persistence with SQLAlchemy

## Project Structure

```text
labflow/
├── backend/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── validator.py
├── frontend/
│   ├── __init__.py
│   └── app.py
└── requirements.txt
```

## Local Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The Apps

Start the FastAPI backend:

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Start the Streamlit frontend in a separate terminal:

```bash
streamlit run frontend/app.py
```

The Streamlit app will be available at `http://localhost:8501`.

## CSV Validation Rules

The `/upload` endpoint checks that the CSV contains these required columns:

- `experiment_id`
- `sample_id`
- `compound_name`
- `concentration_mg_ml`
- `result`
- `run_date`
- `scientist`

It also validates that:

- `concentration_mg_ml` is numeric
- `result` is either `Positive` or `Negative`
- `sample_id` values are unique

If the CSV is valid, LabFlow creates a job in SQLite, processes the file, and stores:

- `status`
- `total_samples`
- `positive_rate`
- `created_at`
- `completed_at`
