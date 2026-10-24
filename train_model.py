import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FEATURES = [
    "Age", "Gender", "Country", "Academic_Level", "Most_Used_Platform",
    "Purpose_Of_Use", "Avg_Daily_Usage_Hours", "Daily_Unlocks", "Study_Hours",
    "Physical_Activity_Hours", "Sleep_Hours_Per_Night", "Stress_Level",
]
TARGET = "Mental_Health_Score"
NUMERIC = ["Age", "Avg_Daily_Usage_Hours", "Daily_Unlocks", "Study_Hours", "Physical_Activity_Hours", "Sleep_Hours_Per_Night"]
CATEGORICAL = [c for c in FEATURES if c not in NUMERIC]

def build_pipeline(estimator):
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore"))])
    prep = ColumnTransformer([("numeric", numeric, NUMERIC), ("categorical", categorical, CATEGORICAL)])
    return Pipeline([("prepare", prep), ("model", estimator)])

def metrics_for(y_true, y_pred):
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 4),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }

def main():
    parser = argparse.ArgumentParser(description="Train and compare regression pipelines from an authorized CSV dataset.")
    parser.add_argument("--data", default="data/students.csv", help="CSV path (not included; supply a dataset you may use)")
    parser.add_argument("--target", default=TARGET, help="Numeric outcome column in your CSV")
    parser.add_argument("--output", default="model.joblib")
    parser.add_argument("--metrics", default="metrics.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    missing = [name for name in FEATURES + [args.target] if name not in df.columns]
    if missing:
        raise SystemExit("CSV is missing required columns: " + ", ".join(missing))
    df = df[FEATURES + [args.target]].copy()
    df[args.target] = pd.to_numeric(df[args.target], errors="coerce")
    df = df.dropna(subset=[args.target])
    if len(df) < 20:
        raise SystemExit("Need at least 20 labeled rows for a basic train/test comparison.")
    X, y = df[FEATURES], df[args.target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=args.seed)

    candidates = {
        "Linear Regression": build_pipeline(LinearRegression()),
        "Random Forest": build_pipeline(RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=args.seed, n_jobs=-1)),
    }
    results = {}
    for name, pipeline in candidates.items():
        pipeline.fit(X_train, y_train)
        results[name] = {"pipeline": pipeline, "metrics": metrics_for(y_test, pipeline.predict(X_test))}
    chosen = min(results, key=lambda name: results[name]["metrics"]["mae"])

    # Refit the selected approach on all available labeled rows for deployment.
    final_pipeline = build_pipeline(LinearRegression() if chosen == "Linear Regression" else RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=args.seed, n_jobs=-1))
    final_pipeline.fit(X, y)
    bundle = {
        "pipeline": final_pipeline,
        "model_name": chosen,
        "target": args.target,
        "metrics": results[chosen]["metrics"],
        "comparison": {name: item["metrics"] for name, item in results.items()},
        "feature_names": FEATURES,
        "training_rows": int(len(df)),
        "random_seed": args.seed,
    }
    joblib.dump(bundle, args.output)
    Path(args.metrics).write_text(json.dumps({k: v for k, v in bundle.items() if k != "pipeline"}, indent=2), encoding="utf-8")
    print(json.dumps({"selected_model": chosen, "comparison": bundle["comparison"], "saved_model": args.output}, indent=2))

if __name__ == "__main__":
    main()
