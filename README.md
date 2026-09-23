# FinSight

**AI-Powered Transparent Credit Scoring & Micro-Investment Advisor**

FinSight is a full-stack fintech application that predicts credit scores using XGBoost, explains every prediction with SHAP Explainable AI, and generates dynamic long-term investment projections using React and FastAPI.

---

## Features

- AI Credit Score Prediction (300–850)
- XGBoost Machine Learning Model
- SHAP Explainable AI
- Financial Analytics Dashboard
- Dynamic Spending Insights
- 1–30 Year SIP Investment Forecast
- Pessimistic / Expected / Optimistic Scenarios
- FastAPI REST API
- React + Tailwind Frontend

---

## Tech Stack

| Layer            | Technology                  |
| ---------------- | --------------------------- |
| Frontend         | React + Vite + Tailwind CSS |
| Backend          | FastAPI                     |
| Machine Learning | XGBoost                     |
| Explainable AI   | SHAP                        |
| Charts           | Recharts                    |
| Language         | Python & JavaScript         |

---

## Architecture

React Frontend

↓

Axios REST API

↓

FastAPI Backend

↓

XGBoost Credit Scoring

↓

SHAP Explainable AI

↓

Synthetic Financial Dataset

---

## Installation

### Clone Repository

```bash
git clone https://github.com/sahilkharwar/Credit_score_analyzer_model.git
cd Credit_score_analyzer_model
```

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

python -m uvicorn main:app --reload
```

Backend runs at:

`http://127.0.0.1:8000`

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at:

`http://localhost:5173`

---

## Project Structure

```text
Credit_score_analyzer_model/

├── backend/
│   ├── main.py
│   ├── credit_model.json
│   ├── model_config.json
│   ├── synthetic_users.json
│   ├── train_model.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── README.md
└── .gitignore
```

---

## Machine Learning

The credit scoring engine uses **XGBoost Regression** trained on synthetic financial behavior.

Input features include:

- Monthly Income
- Savings Ratio
- Debt-to-Income Ratio
- Utility Payment Behaviour
- UPI Regularity
- Recharge Consistency

The model predicts a score between **300–850** and classifies users into Low, Medium, or High risk categories.

---

## Explainable AI

Every prediction is interpreted using **SHAP TreeExplainer**, allowing users to understand the top financial features influencing their credit score instead of receiving a black-box prediction.

---

## Investment Planner

Users can simulate wealth creation from **1–30 years** by selecting:

- Monthly SIP
- Risk Profile
- Market Scenario

The application generates projections for:

- Pessimistic
- Expected
- Optimistic

using compound growth visualization with interactive charts.

---

## Disclaimer

This project is developed for academic and educational purposes. The financial predictions are generated from synthetic data and should not be considered real financial advice.

---

## Author

**Sahil Kharwar**

MSc Information Technology (AI & ML)

GitHub: https://github.com/sahilkharwar
