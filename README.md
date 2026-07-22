# Credit Visibility & Micro-Investment Advisor

A full working prototype: real XGBoost credit scoring + SHAP explainability,
plus a conversational investment advisor that opens with a discretionary-
spending savings hook (your tutor's idea) before assessing risk tolerance
(the hackathon's required flow).

## Setup
```
pip install -r requirements.txt
```

## 1. Generate the dataset (60 synthetic users)
```
cd backend
python generate_dataset.py
```

## 2. Train the XGBoost model + build the SHAP explainer
```
python train_model.py
```
This creates `credit_model.json` (the trained model, saved in XGBoost's
native portable format — not pickle, so it loads reliably across machines/
OSes/versions) and `model_config.json`. The SHAP explainer is rebuilt
fresh each time the API starts (fast, and avoids any serialization
issues). You only need to re-run this step if you regenerate the dataset.

## 3. Run the backend API
```
uvicorn main:app --reload
```
Interactive API docs: http://127.0.0.1:8000/docs

## 4. Run the frontend (in a new terminal)
```
cd ../frontend
streamlit run app.py
```
Opens at http://localhost:8501

## What's actually ML/AI here (not hardcoded)
- **XGBoost regressor** trained on 6 non-traditional signals (utility
  payment %, missed bills, recharge volatility, UPI regularity,
  essential-spend ratio, e-commerce frequency) predicts each user's
  credit-likelihood score. The rule-based formula from the original
  brainstorm now only generates training LABELS — the live prediction
  comes from the trained model, verified at 200+ test-time inference calls.
- **SHAP TreeExplainer** computes true per-user feature attributions for
  the top-3 explanation and improvement tip — genuinely different per user,
  not an if/else ladder.
- **Rule-scored risk quiz** (3 questions) buckets users into
  Low/Medium/High, which drives instrument mapping + the SIP projection.

## Your tutor's idea, merged in
The chat flow opens with `GET /api/spending-hook/{user_id}` — it surfaces
the user's food delivery / outings / impulse-shopping spend and proposes
redirecting 25% of it into a monthly SIP, *before* moving into the
required risk-profiling questions. Nothing from the original problem
statement's requirements was dropped; the tutor's angle is the "hook",
the credit-scoring + risk-profiling core is still the backbone.

## Project structure
```
fintech_app/
├── backend/
│   ├── generate_dataset.py   # synthetic data (incl. discretionary spend)
│   ├── train_model.py        # trains XGBoost + builds SHAP explainer
│   ├── main.py                # FastAPI app — all endpoints
│   ├── synthetic_users.json   # generated dataset (60 users)
│   ├── credit_model.json      # trained model, native XGBoost format (generated)
│   └── model_config.json      # feature list + labels (generated)
├── frontend/
│   └── app.py                 # Streamlit web app (2 tabs: score, chat)
├── requirements.txt
└── README.md
```
