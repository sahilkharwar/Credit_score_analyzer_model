
import pandas as pd
import numpy as np
import json
import os

np.random.seed(42)

PERSONAS = [
    {"occupation": "Kirana Shop Owner", "city_tier": "Tier-3"},
    {"occupation": "Gig Delivery Worker", "city_tier": "Tier-2"},
    {"occupation": "College Student / Freelancer", "city_tier": "Tier-2"},
    {"occupation": "Small Artisan / Handloom", "city_tier": "Rural"},
    {"occupation": "Private School Teacher", "city_tier": "Tier-3"},
    {"occupation": "Auto Rickshaw Driver", "city_tier": "Tier-3"},
    {"occupation": "Beautician / Salon Owner", "city_tier": "Tier-2"},
    {"occupation": "IT Engineer", "city_tier": "Tier-2"},
    {"occupation": "Repair Shop Owner", "city_tier": "Tier-2"},

]

FIRST_NAMES = ["Ramesh", "Priya", "Ankit", "Sunita", "Vikram", "Aisha", "Rajesh",
               "Meena", "Suresh", "Kavita", "Deepak", "Pooja", "Manoj", "Sneha",
               "Arjun", "Neha", "Rohit", "Divya", "Karan", "Anjali", "Sanjay",
               "Ritu", "Amit", "Shweta", "Vivek", "Nisha", "Prakash", "Swati",
               "Harish", "Rekha", "Ravi", "Pallavi", "Siddharth", "Anita",
               "Rakesh", "Sunil", "Kiran"]
LAST_NAMES = ["Kumar", "Sharma", "Verma", "Devi", "Singh", "Begum", "Patel",
              "Joshi", "Das", "Rao", "Yadav", "Hegde", "Tiwari", "Kulkarni",
              "Nair", "Gupta", "Reddy", "Chauhan", "Iyer", "Bose", "Chatterjee", 
              "Mehta", "Kapoor", "Chopra", "Malhotra", "Saxena", "Bhatia", "Jain", 
              "Choudhury", "Ghosh", "Sinha", "Ranganathan", ]


def generate_synthetic_fintech_dataset(num_users=500):
    data = []
    for i in range(num_users):
        persona = PERSONAS[i % len(PERSONAS)]
        user_id = f"USR_{1001 + i}"
        name = f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}"

        # --- Income ---
        monthly_income_inr = int(np.random.choice(
            [12000, 15000, 20000, 25000, 30000, 35000, 40000, 50000]))

        # --- Non-traditional credit signals ---
        recharge_freq_days = int(np.random.choice([28, 30, 45, 60], p=[0.5, 0.3, 0.1, 0.1]))
        recharge_delay_std_days = round(float(np.random.uniform(0.5, 12.0)), 1)
        avg_recharge_inr = int(np.random.choice([199, 299, 479, 666, 719]))

        utility_on_time_pct = round(float(np.random.uniform(40.0, 100.0)), 1)
        utility_bills_missed_12m = int(np.random.choice([0, 1, 2, 3, 4], p=[0.55, 0.2, 0.12, 0.08, 0.05]))
        avg_utility_bill_inr = int(np.random.uniform(300, 2500))

        ecommerce_orders_30d = int(np.random.poisson(lam=3))
        essential_spending_ratio = round(float(np.random.uniform(0.35, 0.95)), 2)
        upi_inflow_regularity_score = round(float(np.random.uniform(0.25, 0.98)), 2)
        min_wallet_balance_inr = int(np.random.uniform(100, 5000))

        # --- EMI (loan installment) signals ---
        # Not everyone has an active EMI (loan/BNPL/appliance installment etc.)
        # EMI scales directly with income: low-income users get low EMIs,
        # high-income users get proportionally higher EMIs — no fixed cap.
        has_emi = bool(np.random.random() < 0.65)
        if has_emi:
            monthly_emi_inr = monthly_income_inr * float(np.random.uniform(0.08, 0.25))
            avg_yearly_emi_inr = int(monthly_emi_inr * 12)
            # Delay likelihood tracks the same underlying discipline as their
            # other bill-payment behavior (utility/UPI), plus a bit of noise.
            delay_prob = 0.10 + (1 - upi_inflow_regularity_score) * 0.35 + (utility_bills_missed_12m * 0.05)
            emi_delay_months_12m = min(4, int(np.random.binomial(12, min(max(delay_prob, 0.0), 0.9))))
        else:
            avg_yearly_emi_inr = 0
            emi_delay_months_12m = 0

        # --- Discretionary spending breakdown ---
        non_essential_budget = monthly_income_inr * (1 - essential_spending_ratio)
        food_delivery_spend_inr = int(non_essential_budget * np.random.uniform(0.15, 0.45))
        outing_entertainment_spend_inr = int(non_essential_budget * np.random.uniform(0.1, 0.3))
        impulse_shopping_inr = int(non_essential_budget * np.random.uniform(0.1, 0.35))
        subscriptions_spend_inr = int(non_essential_budget * np.random.uniform(0.02, 0.1))

        total_unnecessary_spend_inr = (food_delivery_spend_inr + outing_entertainment_spend_inr
                                        + impulse_shopping_inr + subscriptions_spend_inr)

        # how much of that could realistically be redirected to investing (25% cut)
        potential_savings = int(total_unnecessary_spend_inr * 0.25)
        potential_micro_investment_savings_inr = max(500, round(potential_savings / 100) * 100)

        # --- Risk appetite bucket (used as ground-truth-ish label) ---
        if upi_inflow_regularity_score > 0.80 and utility_bills_missed_12m == 0:
            risk_bucket = np.random.choice(["Low", "Medium"], p=[0.7, 0.3])
        elif upi_inflow_regularity_score < 0.50 or utility_bills_missed_12m > 2:
            risk_bucket = np.random.choice(["Medium", "High"], p=[0.4, 0.6])
        else:
            risk_bucket = np.random.choice(["Low", "Medium", "High"], p=[0.3, 0.4, 0.3])

        # --- Rule-based LABEL credit score (ground truth for training the ML model) ---
        base_score = 500
        base_score += (utility_on_time_pct * 2.0)
        base_score -= (utility_bills_missed_12m * 35)
        base_score += (upi_inflow_regularity_score * 100)
        base_score -= (recharge_delay_std_days * 8)
        base_score += (essential_spending_ratio * 40)
        emi_burden_ratio = (avg_yearly_emi_inr / 12) / monthly_income_inr if monthly_income_inr else 0
        base_score -= (emi_burden_ratio * 80)      # heavier EMI load vs. income -> lower score
        base_score -= (emi_delay_months_12m * 10)  # each delayed EMI month is a strong red flag
        base_score += np.random.normal(0, 12)  # small noise so ML model isn't trivially perfect
        credit_score_label = int(np.clip(base_score, 300, 850))

        user_profile = {
            "user_id": user_id,
            "name": name,
            "occupation": persona["occupation"],
            "city_tier": persona["city_tier"],
            "monthly_income_inr": monthly_income_inr,

            "recharge_freq_days": recharge_freq_days,
            "recharge_delay_std_days": recharge_delay_std_days,
            "avg_recharge_inr": avg_recharge_inr,
            "utility_on_time_pct": utility_on_time_pct,
            "utility_bills_missed_12m": utility_bills_missed_12m,
            "avg_utility_bill_inr": avg_utility_bill_inr,
            "ecommerce_orders_30d": ecommerce_orders_30d,
            "essential_spending_ratio": essential_spending_ratio,
            "upi_inflow_regularity_score": upi_inflow_regularity_score,
            "min_wallet_balance_inr": min_wallet_balance_inr,
            "avg_yearly_emi_inr": avg_yearly_emi_inr,
            "emi_delay_months_12m": emi_delay_months_12m,

            "food_delivery_spend_inr": food_delivery_spend_inr,
            "outing_entertainment_spend_inr": outing_entertainment_spend_inr,
            "impulse_shopping_inr": impulse_shopping_inr,
            "subscriptions_spend_inr": subscriptions_spend_inr,
            "total_unnecessary_spend_inr": total_unnecessary_spend_inr,
            "potential_micro_investment_savings_inr": potential_micro_investment_savings_inr,

            "risk_appetite_bucket": risk_bucket,
            "credit_score_label": credit_score_label,
        }
        data.append(user_profile)

    return pd.DataFrame(data)


if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    df_users = generate_synthetic_fintech_dataset(num_users=500)
    df_users.to_csv(os.path.join(out_dir, "synthetic_user_profiles.csv"), index=False)
    with open(os.path.join(out_dir, "synthetic_users.json"), "w") as f:
        json.dump(df_users.to_dict(orient="records"), f, indent=2)
    print(f"Dataset generated: {df_users.shape[0]} users, {df_users.shape[1]} columns")
