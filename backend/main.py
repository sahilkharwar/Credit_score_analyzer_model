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
import random

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

with open(os.path.join(HERE, "companies.json")) as f:
    COMPANIES_DB = json.load(f)

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

# --- Step-up SIP: the monthly contribution isn't flat for all 60 months —
# it increases by ₹100 every 6 months, which is how real step-up SIPs work
# and better reflects rising income/savings capacity over time.
STEP_UP_AMOUNT = 100
STEP_UP_EVERY_MONTHS = 6


def stepped_contribution(base_amount: float, month: int) -> float:
    """Monthly contribution for a given month (1-indexed) under the step-up SIP."""
    increments = (month - 1) // STEP_UP_EVERY_MONTHS
    return base_amount + STEP_UP_AMOUNT * increments

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
            "avg_yearly_emi_inr": "Where possible, avoid stacking multiple EMIs at once so your total installment load stays a small share of income.",
            "emi_delay_months_12m": "Set up auto-debit for your EMI so it's never paid late, even by a few days.",
        }
        tip = tips.get(weakest_feat)

    return {"user_id": user_id, "top_features": formatted, "improvement_tip": tip}


@app.get("/api/spending-hook/{user_id}")
def spending_hook(user_id: str):
    """Tutor's idea: surface discretionary spending and a savings offer."""
    user = USER_INDEX.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    monthly_emi_inr = round(user["avg_yearly_emi_inr"] / 12)
    emi_delay_months = user["emi_delay_months_12m"]
    has_emi_delay = emi_delay_months > 0

    # If the user has a history of delaying their EMI, be more conservative
    # about how much of their "spare" money we suggest investing — paying
    # the EMI on time matters more than starting an SIP.
    base_savings = user["potential_micro_investment_savings_inr"]
    if has_emi_delay:
        recommended_investment_amount_inr = max(300, round(base_savings * 0.7 / 100) * 100)
    else:
        recommended_investment_amount_inr = base_savings

    emi_caution = None
    if has_emi_delay:
        emi_caution = (
            f"Heads up: you've delayed your EMI payment in {emi_delay_months} of the last "
            f"12 months. It's worth prioritizing on-time EMI payments (₹{monthly_emi_inr}/month) "
            f"before investing more — so we've suggested a smaller, safer starting amount."
        )

    return {
        "user_id": user_id,
        "food_delivery_spend_inr": user["food_delivery_spend_inr"],
        "outing_entertainment_spend_inr": user["outing_entertainment_spend_inr"],
        "impulse_shopping_inr": user["impulse_shopping_inr"],
        "subscriptions_spend_inr": user["subscriptions_spend_inr"],
        "total_unnecessary_spend_inr": user["total_unnecessary_spend_inr"],
        "potential_micro_investment_savings_inr": base_savings,
        "avg_yearly_emi_inr": user["avg_yearly_emi_inr"],
        "monthly_emi_inr": monthly_emi_inr,
        "emi_delay_months_12m": emi_delay_months,
        "recommended_investment_amount_inr": recommended_investment_amount_inr,
        "emi_caution": emi_caution,
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
    """
    SIP compound-growth projection across 3 market scenarios, with a
    step-up contribution that increases by ₹100 every 6 months instead of
    staying flat.
    """
    if req.risk_bucket not in RISK_RATES:
        raise HTTPException(status_code=400, detail="Invalid risk bucket")
    months = np.arange(1, 61)  # 5 years

    def calculate_compound(rate):
        monthly_rate = rate / 12
        value = 0.0
        values = []
        for m in range(1, 61):
            contribution = stepped_contribution(req.monthly_investment, m)
            value = (value + contribution) * (1 + monthly_rate)
            values.append(value)
        return values

    # Total principal invested also grows with the step-up schedule, so it
    # has to be accumulated month by month rather than a flat multiplication.
    total_invested = []
    running_total = 0.0
    for m in range(1, 61):
        running_total += stepped_contribution(req.monthly_investment, m)
        total_invested.append(round(running_total, 2))

    rates = RISK_RATES[req.risk_bucket]
    return {
        "months": months.tolist(),
        "pessimistic": calculate_compound(rates["pessimistic"]),
        "expected": calculate_compound(rates["expected"]),
        "optimistic": calculate_compound(rates["optimistic"]),
        "total_invested": total_invested,
        "starting_monthly_investment": req.monthly_investment,
        "final_monthly_investment": stepped_contribution(req.monthly_investment, 60),
        "step_up_note": f"Contribution increases by ₹{STEP_UP_AMOUNT} every {STEP_UP_EVERY_MONTHS} months.",
        "disclaimer": "EDUCATIONAL PURPOSES ONLY. NOT REGULATED FINANCIAL ADVICE.",
    }


@app.post("/api/recommend-portfolio")
def recommend_portfolio(req: InvestmentRequest):
    """
    Builds a personalized mini-portfolio: picks up to 4 companies matching
    the user's risk bucket that they can actually afford, allocates a
    slightly different monthly amount to each (max ₹50 apart between any
    two), and simulates 5-year growth month-by-month with a per-stock
    interest rate that starts between 3-12% p.a. and shifts by 0.5-1.5
    percentage points EVERY SINGLE MONTH (clamped to the 3-12% band) —
    rather than a single flat compound-interest formula. The total monthly
    contribution is a step-up SIP: it increases by ₹100 every 6 months.
    """
    if req.risk_bucket not in RISK_RATES:
        raise HTTPException(status_code=400, detail="Invalid risk bucket")
    if req.monthly_investment <= 0:
        raise HTTPException(status_code=400, detail="monthly_investment must be positive")

    suitable_stocks = [c for c in COMPANIES_DB if c["risk_bucket"] == req.risk_bucket]
    affordable_stocks = [c for c in suitable_stocks if c["current_price"] <= req.monthly_investment]

    # Fallback: if nothing in-bucket is affordable, widen to all affordable stocks
    # regardless of bucket so the user still gets a portfolio.
    if not affordable_stocks:
        affordable_stocks = [c for c in COMPANIES_DB if c["current_price"] <= req.monthly_investment]
    if not affordable_stocks:
        raise HTTPException(
            status_code=400,
            detail="No companies are affordable at this monthly investment amount "
                   f"(cheapest share available is ₹{min(c['current_price'] for c in COMPANIES_DB):.2f})."
        )

    # Seeded by risk+amount so the same inputs always reproduce the same
    # portfolio, allocations, and simulated rate path (reproducible demo).
    rng = random.Random(f"{req.risk_bucket}_{req.monthly_investment}")
    selected_stocks = rng.sample(affordable_stocks, min(4, len(affordable_stocks)))
    n = len(selected_stocks)

    # --- Unequal monthly allocations, but any two are at most ₹50 apart,
    #     and they still sum exactly to the user's monthly investment. ---
    base_alloc = req.monthly_investment / n
    if n > 1:
        raw_deltas = [rng.uniform(-25, 25) for _ in range(n)]
        mean_delta = sum(raw_deltas) / n
        deltas = [d - mean_delta for d in raw_deltas]  # sum(deltas) == 0

        # Safety clamp: guarantee max-min spread across allocations is <= 50,
        # even in an unlucky draw, by rescaling (rescaling a zero-sum vector
        # keeps the sum at zero, so allocations still add up correctly).
        spread = max(deltas) - min(deltas)
        if spread > 50:
            scale = 50 / spread
            deltas = [d * scale for d in deltas]

        allocations = [round(base_alloc + d, 2) for d in deltas]
        # Fix any rounding drift on the last stock so the total is exact.
        drift = round(req.monthly_investment - sum(allocations), 2)
        allocations[-1] = round(allocations[-1] + drift, 2)
    else:
        allocations = [round(float(req.monthly_investment), 2)]

    months_range = np.arange(1, 61)  # 5 years
    portfolio_value = np.zeros(60)
    portfolio_details = []

    for stock, allocated_amount in zip(selected_stocks, allocations):
        # Two separate forces drive the price now:
        #   1) DRIFT — the long-run trend, in [3%, 12%] p.a., shifting by
        #      0.5-1.5 points EVERY SINGLE MONTH (clamped to the band).
        #   2) VOLATILITY — random monthly noise on top of the drift, which
        #      CAN be negative. This is what actually produces the up-down
        #      wiggle; drift alone only ever pushes the line upward.
        current_annual_rate = rng.uniform(0.03, 0.12)
        MONTHLY_VOLATILITY = 0.05  # ~5% monthly std-dev of noise around the drift

        stock_values = []
        rate_history = []
        current_share_price = stock["current_price"]
        shares_owned = 0.0
        yearly_prices = []

        for m in range(1, 61):
            # Drift shift, every single month.
            variation = rng.uniform(0.005, 0.015)
            direction = rng.choice([-1, 1])
            current_annual_rate += variation * direction
            current_annual_rate = max(0.03, min(0.12, current_annual_rate))
            monthly_drift = current_annual_rate / 12

            # Volatility shock — the source of the up/down movement.
            monthly_shock = rng.gauss(0, MONTHLY_VOLATILITY)
            monthly_return = monthly_drift + monthly_shock
            monthly_return = max(monthly_return, -0.20)  # floor a single-month crash at -20%

            current_share_price = max(1.0, current_share_price * (1 + monthly_return))

            # Step-up SIP: this stock's slice of the total monthly investment
            # grows in the same proportion as the overall step-up (+₹100
            # every 6 months to the total), keeping the original allocation
            # ratio between stocks intact.
            step_up_scale = stepped_contribution(req.monthly_investment, m) / req.monthly_investment
            this_month_contribution = allocated_amount * step_up_scale

            # Real SIP behaviour: buy shares at THIS month's price, then
            # value = shares owned so far x current price. When price dips,
            # the portfolio value can dip too, even though contributions
            # keep flowing in (and you're buying more shares while it's cheap).
            shares_owned += this_month_contribution / current_share_price
            accumulated_value = shares_owned * current_share_price

            stock_values.append(accumulated_value)
            rate_history.append(current_annual_rate)

            if m % 12 == 0:
                yearly_prices.append(round(current_share_price, 2))

        portfolio_value += np.array(stock_values)
        shares_per_month = allocated_amount / stock["current_price"]
        avg_annual_rate = float(np.mean(rate_history))
        yearly_avg_rates = [float(np.mean(rate_history[y * 12:(y + 1) * 12])) for y in range(5)]

        detail = {
            "Ticker": stock["ticker"],
            "Company": stock["company_name"],
            "Sector": stock["sector"],
            "Share Price (₹)": stock["current_price"],
            "Monthly Allocation (₹)": allocated_amount,
            "Final Monthly Allocation (₹)": round(allocated_amount * stepped_contribution(req.monthly_investment, 60) / req.monthly_investment, 2),
            "Approx Shares/Month": round(shares_per_month, 2),
            "Avg Simulated Return": f"{avg_annual_rate * 100:.2f}%",
            "Projected_Values": [round(v, 2) for v in stock_values],
        }
        for y in range(5):
            detail[f"Year {y + 1} (Price | Avg Rate)"] = (
                f"₹{yearly_prices[y]} | {yearly_avg_rates[y] * 100:.2f}%"
            )
        portfolio_details.append(detail)

    # Total principal invested also follows the step-up schedule.
    total_invested = []
    running_total = 0.0
    for m in range(1, 61):
        running_total += stepped_contribution(req.monthly_investment, m)
        total_invested.append(round(running_total, 2))

    return {
        "months": months_range.tolist(),
        "projected_values": np.round(portfolio_value, 2).tolist(),
        "total_invested": total_invested,
        "starting_monthly_investment": req.monthly_investment,
        "final_monthly_investment": stepped_contribution(req.monthly_investment, 60),
        "step_up_note": f"Contribution increases by ₹{STEP_UP_AMOUNT} every {STEP_UP_EVERY_MONTHS} months.",
        "portfolio": portfolio_details,
        "disclaimer": "EDUCATIONAL PURPOSES ONLY. NOT REGULATED FINANCIAL ADVICE.",
    }


@app.get("/")
def root():
    return {"status": "ok", "message": "FinTech Micro-Investment API is running"}
