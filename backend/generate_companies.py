"""
Generates 50 synthetic companies with share prices between ₹50 and ₹500,
each tagged with a risk bucket and a realistic expected CAGR for that
bucket. Used by /api/recommend-portfolio to build a personalized
mini-portfolio for a user based on their risk profile and monthly budget.
"""

import json
import os
import random

random.seed(42)

SECTORS = ["Tech", "FMCG", "Pharma", "Energy", "Finance", "Retail",
           "Auto", "Infrastructure", "Textiles", "Agri"]


def generate_companies(num_companies=50):
    risk_levels = ["Low", "Medium", "High"]
    companies = []

    for i in range(1, num_companies + 1):
        price = round(random.uniform(50.0, 500.0), 2)
        risk = random.choice(risk_levels)
        sector = random.choice(SECTORS)

        if risk == "Low":
            cagr = random.uniform(0.05, 0.08)
        elif risk == "Medium":
            cagr = random.uniform(0.08, 0.14)
        else:
            cagr = random.uniform(0.12, 0.22)

        companies.append({
            "ticker": f"STK{i:03d}",
            "company_name": f"{sector} Enterprises {i}",
            "sector": sector,
            "current_price": price,
            "risk_bucket": risk,
            "expected_cagr": round(cagr, 3),
        })

    return companies


if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    companies = generate_companies(50)
    with open(os.path.join(out_dir, "companies.json"), "w") as f:
        json.dump(companies, f, indent=2)
    print(f"Generated {len(companies)} synthetic companies in companies.json")
