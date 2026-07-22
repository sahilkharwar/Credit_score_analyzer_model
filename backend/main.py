"""
FastAPI backend for the Transparent Credit Scoring & AI Micro-Investment
Advisor prototype.

Real ML/AI used here (not hardcoded rules):
  - XGBoost regressor  -> predicts a credit-likelihood score from
                          non-traditional digital signals
  - SHAP TreeExplainer -> explains WHY the model gave that score
                          (top-3 feature contributions, in points)
  - Rule-based chatbot -> conversational flow: tutor's discretionary-
                          spending hook, then risk-tolerance questions,
                          then instrument mapping + SIP projection
"""

import json
import os

import numpy as np
import shap
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from xgboost import XGBRegressor

HERE = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="FinTech Micro-Investment API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------- load data
with open(os.path.join(HERE, "synthetic_users.json")) as f:
    USER_DB = json.load(f)
USER_INDEX = {u["user_id"]: u for u in USER_DB}

with open(os.path.join(HERE, "model_config.json")) as f:
    _cfg = json.load(f)
    FEATURES = _cfg["features"]
    FEATURE_LABELS = _cfg["feature_labels"]

MODEL = XGBRegressor()
MODEL.load_model(os.path.join(HERE, "credit_model.json"))

# Rebuilt fresh at startup — cheap, deterministic given the model, and
# avoids any pickle version/portability issues across machines.
EXPLAINER = shap.TreeExplainer(MODEL)

RISK_RATES = {
    "Low": {"pessimistic": 0.04, "expected": 0.06, "optimistic": 0.08},
    "Medium": {"pessimistic": 0.05, "expected": 0.10, "optimistic": 0.14},
    "High": {"pessimistic": -0.02, "expected": 0.15, "optimistic": 0.22},
}

RISK_INSTRUMENTS = {
    "Low": ["Digital Gold", "Liquid Mutual Funds", "Post Office Savings Schemes"],
    "Medium": ["Conservative Hybrid Funds", "Large-Cap Index Funds"],
    "High": ["Mid/Small-Cap Equity Mutual Funds", "Sectoral Index Funds"],
}

RISK_QUESTIONS = [
    {
        "id": "q1",
        "text": "If ₹1,000 you invested drops to ₹900 next month, what do you do?",
        "options": {
            "A": ("Withdraw it immediately", -1),
            "B": ("Leave it alone and wait", 0),
            "C": ("Invest ₹500 more while it's cheap", 1),
        },
    },
    {
        "id": "q2",
        "text": "How would you feel if your investment value changed every single day?",
        "options": {
            "A": ("Very uncomfortable, I want stability", -1),
            "B": ("A little nervous but okay with it", 0),
            "C": ("Fine with it, it's normal for growth", 1),
        },
    },
    {
        "id": "q3",
        "text": "What's the main reason you want to invest this money?",
        "options": {
            "A": ("Keep it safe and beat inflation slightly", -1),
            "B": ("Grow it steadily over a few years", 0),
            "C": ("Maximize growth, I can wait it out", 1),
        },
    },
]


# ---------------------------------------------------------------- schemas
class InvestmentRequest(BaseModel):
    monthly_investment: int
    risk_bucket: str


class RiskAnswers(BaseModel):
    user_id: str
    answers: dict  # {"q1": "A", "q2": "B", "q3": "C"}


# ---------------------------------------------------------------- endpoints
@app.get("/api/users")
def get_all_users():
    return {"users": USER_DB}


@app.get("/api/user/{user_id}")
def get_user(user_id: str):
    user = USER_INDEX.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/api/score-credit/{user_id}")
def score_credit(user_id: str):
    """Real XGBoost prediction (not the rule-based label)."""
    user = USER_INDEX.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    x = np.array([[user[f] for f in FEATURES]])
    predicted_score = float(MODEL.predict(x)[0])
    predicted_score = int(np.clip(predicted_score, 300, 850))

    if predicted_score >= 730:
        tier = "High Likelihood (Low Risk)"
    elif predicted_score >= 620:
        tier = "Moderate Likelihood"
    else:
        tier = "Needs Credit Building (High Risk)"

    return {"user_id": user_id, "predicted_credit_score": predicted_score,
            "credit_tier": tier}


@app.get("/api/explain-score/{user_id}")
def explain_credit_score(user_id: str):
    """Real SHAP explanation: top-3 feature contributions + a tip for the weakest one."""
    user = USER_INDEX.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    x = np.array([[user[f] for f in FEATURES]])
    shap_values = EXPLAINER(x)
    contributions = list(zip(FEATURES, shap_values.values[0]))
    contributions.sort(key=lambda t: abs(t[1]), reverse=True)
    top3 = contributions[:3]

    formatted = []
    for feat, val in top3:
        sign = "🟢" if val >= 0 else "🔴"
        formatted.append({
            "feature": FEATURE_LABELS[feat],
            "impact_points": round(float(val), 1),
            "label": f"{sign} {FEATURE_LABELS[feat]} ({'+' if val >= 0 else ''}{round(float(val),1)} pts)"
        })

    # improvement tip: weakest (most negative) of the top-3
    negative = [c for c in top3 if c[1] < 0]
    tip = None
    if negative:
        weakest_feat = negative[0][0]
        tips = {
            "utility_on_time_pct": "Set up auto-pay for utility bills so none are missed or late.",
            "utility_bills_missed_12m": "Clear any pending utility dues and avoid missing future ones.",
            "recharge_delay_std_days": "Recharge your prepaid plan 2 days before expiry, consistently, for 3 months.",
            "upi_inflow_regularity_score": "Try to route more of your income through UPI so inflow patterns look more consistent.",
            "essential_spending_ratio": "Track spending for a month and shift a bit more toward essentials vs. discretionary buys.",
            "ecommerce_orders_30d": "Keep e-commerce order patterns steady rather than sporadic bulk buying.",
        }
        tip = tips.get(weakest_feat)

    return {"user_id": user_id, "top_features": formatted, "improvement_tip": tip}


@app.get("/api/spending-hook/{user_id}")
def spending_hook(user_id: str):
    """Tutor's idea: surface discretionary spending and a savings offer."""
    user = USER_INDEX.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user_id,
        "food_delivery_spend_inr": user["food_delivery_spend_inr"],
        "outing_entertainment_spend_inr": user["outing_entertainment_spend_inr"],
        "impulse_shopping_inr": user["impulse_shopping_inr"],
        "subscriptions_spend_inr": user["subscriptions_spend_inr"],
        "total_unnecessary_spend_inr": user["total_unnecessary_spend_inr"],
        "potential_micro_investment_savings_inr": user["potential_micro_investment_savings_inr"],
        "message": (
            f"You're spending about ₹{user['total_unnecessary_spend_inr']}/month on food "
            f"delivery, outings, impulse buys and subscriptions. If we trim that by just "
            f"25%, that's ₹{user['potential_micro_investment_savings_inr']}/month you could "
            f"invest instead — without changing your lifestyle much."
        ),
    }


@app.get("/api/risk-questions")
def get_risk_questions():
    return {"questions": RISK_QUESTIONS}


@app.post("/api/submit-risk-answers")
def submit_risk_answers(payload: RiskAnswers):
    """Scores the 3-question quiz into a risk bucket."""
    total = 0
    for q in RISK_QUESTIONS:
        choice = payload.answers.get(q["id"])
        if choice and choice in q["options"]:
            total += q["options"][choice][1]

    if total <= -2:
        bucket = "Low"
    elif total >= 2:
        bucket = "High"
    else:
        bucket = "Medium"

    return {
        "user_id": payload.user_id,
        "risk_score_raw": total,
        "risk_bucket": bucket,
        "recommended_instruments": RISK_INSTRUMENTS[bucket],
    }


@app.post("/api/investment-projection")
def get_investment_projection(req: InvestmentRequest):
    """SIP compound-growth projection across 3 market scenarios."""
    if req.risk_bucket not in RISK_RATES:
        raise HTTPException(status_code=400, detail="Invalid risk bucket")
    months = np.arange(1, 61)  # 5 years

    def calculate_compound(rate):
        monthly_rate = rate / 12
        if abs(monthly_rate) < 1e-9:
            return (req.monthly_investment * months).tolist()
        fv = req.monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        return fv.tolist()

    rates = RISK_RATES[req.risk_bucket]
    return {
        "months": months.tolist(),
        "pessimistic": calculate_compound(rates["pessimistic"]),
        "expected": calculate_compound(rates["expected"]),
        "optimistic": calculate_compound(rates["optimistic"]),
        "disclaimer": "EDUCATIONAL PURPOSES ONLY. NOT REGULATED FINANCIAL ADVICE.",
    }


@app.get("/")
def root():
    return {"status": "ok", "message": "FinTech Micro-Investment API is running"}
