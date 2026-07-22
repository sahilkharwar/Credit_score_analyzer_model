"""
Trains a real XGBoost regressor to predict credit_score_label from
non-traditional digital signals, then builds a SHAP TreeExplainer
for interpretability. Both are pickled for the FastAPI backend to load.

This is the actual ML/XAI layer referenced in the problem statement:
  - XGBoost = supervised learning on alternative data signals
  - SHAP    = explainable AI, gives per-user top-3 feature contributions
"""

import json
import os
import pickle

import numpy as np
import pandas as pd
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

HERE = os.path.dirname(os.path.abspath(__file__))

FEATURES = [
    "utility_on_time_pct",
    "utility_bills_missed_12m",
    "recharge_delay_std_days",
    "upi_inflow_regularity_score",
    "essential_spending_ratio",
    "ecommerce_orders_30d",
    "avg_yearly_emi_inr",
    "emi_delay_months_12m",
]

FEATURE_LABELS = {
    "utility_on_time_pct": "Utility bill payment consistency",
    "utility_bills_missed_12m": "Missed utility bills (past 12 months)",
    "recharge_delay_std_days": "Mobile recharge timing volatility",
    "upi_inflow_regularity_score": "Income / UPI inflow regularity",
    "essential_spending_ratio": "Essential vs. discretionary spending ratio",
    "ecommerce_orders_30d": "E-commerce order frequency (30 days)",
    "avg_yearly_emi_inr": "Average yearly EMI obligation",
    "emi_delay_months_12m": "Months EMI payment delayed (past 12 months)",
}


def main():
    with open(os.path.join(HERE, "synthetic_users.json")) as f:
        users = json.load(f)
    df = pd.DataFrame(users)

    X = df[FEATURES]
    y = df["credit_score_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBRegressor(
        n_estimators=150,
        max_depth=3,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    print(f"Trained XGBoost model — test MAE: {mae:.1f} credit-score points "
          f"(on a 300-850 scale)")

    # Save the model in XGBoost's own native format (JSON) — this is
    # portable across machines, OSes, and xgboost versions, unlike
    # raw pickle of the Booster which can corrupt across environments.
    model.save_model(os.path.join(HERE, "credit_model.json"))

    with open(os.path.join(HERE, "model_config.json"), "w") as f:
        json.dump({"features": FEATURES, "feature_labels": FEATURE_LABELS}, f, indent=2)

    print("Saved credit_model.json and model_config.json")
    print("(SHAP explainer is rebuilt at API startup from the loaded model — "
          "no need to pickle it.)")


if __name__ == "__main__":
    main()
