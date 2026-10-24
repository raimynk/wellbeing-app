# Student Wellbeing Habits: regression demo

A fresh implementation with a static form, FastAPI prediction service, reproducible training script, preprocessing pipeline, and a held-out comparison of Linear Regression and Random Forest. It is an educational model demo, not a clinical tool.

## Important: provide an authorized dataset

No dataset or trained model is bundled. Before training, place a CSV you are allowed to use at `data/students.csv`. It must include these columns: `Age`, `Gender`, `Country`, `Academic_Level`, `Most_Used_Platform`, `Purpose_Of_Use`, `Avg_Daily_Usage_Hours`, `Daily_Unlocks`, `Study_Hours`, `Physical_Activity_Hours`, `Sleep_Hours_Per_Night`, `Stress_Level`, and a numeric `Mental_Health_Score` target. If you use a different permitted target, pass `--target YOUR_COLUMN`.

Do not reuse a dataset unless its license or your permission allows it. Record its source, license/permission, collection method, and limitations in this README before publishing.

## Train locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python train_model.py --data data/students.csv
```

The script compares a Linear Regression baseline and a Random Forest using a held-out 20% split, chooses the lower-MAE model, refits it on the supplied labeled rows, and writes `model.joblib` and `metrics.json`. Review the dataset and metrics before using the model. Metrics do not establish clinical validity or generalization to other populations.

## Run the API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

API docs: `http://localhost:8000/docs`; health: `/health`; held-out metrics: `/metrics`; prediction: `POST /predict`.

## Deploy

Deploy the backend as a Render **Web Service** from the repository. Build command: `pip install -r requirements.txt`. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`. Ensure `model.joblib` exists in the deployed repository or is generated during a controlled build. Then set `CORS_ORIGINS` to the static site URL.

Deploy the frontend as a Render **Static Site** from the same repository, with blank build command and publish directory `.`. Before deploying, edit `app.js` and replace `https://YOUR-API-NAME.onrender.com` with the backend URL.

## Data protection and scope

The form sends submitted values to the API for inference. Do not enter identifiable or sensitive personal information. The API does not persist submissions. A model trained on self-reported survey data can reflect sampling, labeling, and measurement biases. This score is not a diagnosis or clinical assessment.

## Attribution

This is a new implementation. If any dataset, ideas, or other materials are reused from another project, add attribution and comply with the relevant license or permission terms here.

