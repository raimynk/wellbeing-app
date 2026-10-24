import json
import os
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT / "model.joblib"))

bundle = None
if MODEL_PATH.exists():
    bundle = joblib.load(MODEL_PATH)

app = FastAPI(
    title="Student Wellbeing Habits API",
    description="Educational regression demo for exploring self-reported habit data; not a clinical tool.",
    version="1.0.0",
)
allowed_origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class StudentHabits(BaseModel):
    age: int = Field(ge=10, le=100)
    gender: str = Field(min_length=1, max_length=40)
    country: str = Field(min_length=1, max_length=80)
    academic_level: str = Field(min_length=1, max_length=60)
    most_used_platform: str = Field(min_length=1, max_length=60)
    purpose_of_use: str = Field(min_length=1, max_length=60)
    avg_daily_usage_hours: float = Field(ge=0, le=24)
    daily_unlocks: int = Field(ge=0, le=2000)
    study_hours: float = Field(ge=0, le=24)
    physical_activity_hours: float = Field(ge=0, le=24)
    sleep_hours_per_night: float = Field(ge=0, le=24)
    stress_level: str = Field(min_length=1, max_length=40)

@app.get("/")
def root():
    return {"name": "Student Wellbeing Habits API", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": bundle is not None}

@app.get("/metrics")
def metrics():
    if bundle is None:
        raise HTTPException(status_code=503, detail="Model is not trained yet. Run train_model.py first.")
    return {"model": bundle["model_name"], "test_metrics": bundle["metrics"], "target": bundle["target"]}

@app.post("/predict")
def predict(data: StudentHabits):
    if bundle is None:
        raise HTTPException(status_code=503, detail="Model is not trained yet. Ask the project owner to train and deploy it.")
    input_names = {
        "age": "Age", "gender": "Gender", "country": "Country",
        "academic_level": "Academic_Level", "most_used_platform": "Most_Used_Platform",
        "purpose_of_use": "Purpose_Of_Use", "avg_daily_usage_hours": "Avg_Daily_Usage_Hours",
        "daily_unlocks": "Daily_Unlocks", "study_hours": "Study_Hours",
        "physical_activity_hours": "Physical_Activity_Hours",
        "sleep_hours_per_night": "Sleep_Hours_Per_Night", "stress_level": "Stress_Level",
    }
    frame = pd.DataFrame([{input_names[key]: value for key, value in data.model_dump().items()}])
    estimate = float(bundle["pipeline"].predict(frame)[0])
    return {
        "predicted_score": round(estimate, 2),
        "target": bundle["target"],
        "model": bundle["model_name"],
        "notice": "An estimate learned from the supplied dataset; not a clinical assessment or diagnosis.",
    }

