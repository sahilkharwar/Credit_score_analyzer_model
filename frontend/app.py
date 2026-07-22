import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="FinTech Inclusion Dashboard", layout="wide")
st.title("💳 Credit Visibility & Micro-Investment Advisor")
st.caption("Alternative credit scoring + AI investment guidance for underserved, credit-invisible users")

# ---------------------------------------------------------------- load users
try:
    users_response = requests.get(
        f"{API_URL}/api/users",
        timeout=5
    ).json()
except requests.exceptions.ConnectionError:
    st.error("Backend not reachable. Start it first.")
    st.stop()

user_list = {u["name"] + " — " + u["occupation"]: u["user_id"] for u in users_response["users"]}

st.sidebar.header("👤 Select a Sample User")
selected_label = st.sidebar.selectbox("User Profile:", list(user_list.keys()))
selected_id = user_list[selected_label]

user_data = requests.get(f"{API_URL}/api/user/{selected_id}").json()

# session state to carry the chat flow forward
if "stage" not in st.session_state or st.session_state.get("current_user") != selected_id:
    st.session_state.stage = "score"
    st.session_state.current_user = selected_id
    st.session_state.risk_bucket = None
    st.session_state.savings_amount = None

tab1, tab2 = st.tabs(["📊 Credit Score", "💬 Investment Advisor Chat"])

# ============================================================== TAB 1
with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"{user_data['name']}")
        st.write(f"**Occupation:** {user_data['occupation']} ({user_data['city_tier']})")
        st.write(f"**Monthly Income:** ₹{user_data['monthly_income_inr']:,}")

        score_resp = requests.get(f"{API_URL}/api/score-credit/{selected_id}").json()
        predicted_score = score_resp["predicted_credit_score"]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=predicted_score,
            title={'text': "AI-Predicted Credit Likelihood Score"},
            gauge={
                'axis': {'range': [300, 850]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [300, 580], 'color': "#f8d7da"},
                    {'range': [580, 670], 'color': "#fff3cd"},
                    {'range': [670, 850], 'color': "#d4edda"},
                ],
            }))
        fig.update_layout(height=300, margin=dict(t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"**Tier:** {score_resp['credit_tier']}")
        st.caption("Score predicted by a trained XGBoost regression model — not a fixed formula.")

    with col2:
        st.subheader("Why this score? (SHAP explainability)")
        explanation = requests.get(f"{API_URL}/api/explain-score/{selected_id}").json()
        for feat in explanation["top_features"]:
            st.write(feat["label"])
        if explanation["improvement_tip"]:
            st.info(f"💡 **Tip to improve:** {explanation['improvement_tip']}")

        st.subheader("Raw signal inputs")
        signal_cols = ["utility_on_time_pct", "utility_bills_missed_12m",
                        "recharge_delay_std_days", "upi_inflow_regularity_score",
                        "essential_spending_ratio", "ecommerce_orders_30d"]
        st.dataframe(pd.DataFrame([{c: user_data[c] for c in signal_cols}]),
                     use_container_width=True, hide_index=True)

# ============================================================== TAB 2
with tab2:
    st.subheader("Conversational Micro-Investment Advisor")

    chat_box = st.container()

    # ---- Stage 1: tutor's spending hook ----
    if st.session_state.stage == "score":
        hook = requests.get(f"{API_URL}/api/spending-hook/{selected_id}").json()
        with chat_box:
            st.chat_message("assistant").write(hook["message"])
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Food delivery", f"₹{hook['food_delivery_spend_inr']}")
            c2.metric("Outings", f"₹{hook['outing_entertainment_spend_inr']}")
            c3.metric("Impulse buys", f"₹{hook['impulse_shopping_inr']}")
            c4.metric("Subscriptions", f"₹{hook['subscriptions_spend_inr']}")

        if st.button("👍 Yes, show me how that could grow"):
            st.session_state.savings_amount = hook["potential_micro_investment_savings_inr"]
            st.session_state.stage = "risk_quiz"
            st.rerun()

    # ---- Stage 2: risk quiz ----
    elif st.session_state.stage == "risk_quiz":
        with chat_box:
            st.chat_message("assistant").write(
                f"Great — let's find out how you'd handle ₹{st.session_state.savings_amount}/month "
                f"being invested. Answer a few quick questions:"
            )
        questions = requests.get(f"{API_URL}/api/risk-questions").json()["questions"]
        answers = {}
        with st.form("risk_form"):
            for q in questions:
                opts = list(q["options"].keys())
                labels = [f"{k}) {v[0]}" for k, v in q["options"].items()]
                choice = st.radio(q["text"], opts, format_func=lambda k, q=q: f"{k}) {q['options'][k][0]}",
                                   key=q["id"])
                answers[q["id"]] = choice
            submitted = st.form_submit_button("Submit answers")

        if submitted:
            resp = requests.post(f"{API_URL}/api/submit-risk-answers",
                                  json={"user_id": selected_id, "answers": answers}).json()
            st.session_state.risk_bucket = resp["risk_bucket"]
            st.session_state.recommended_instruments = resp["recommended_instruments"]
            st.session_state.stage = "result"
            st.rerun()

    # ---- Stage 3: recommendation + projection ----
    elif st.session_state.stage == "result":
        bucket = st.session_state.risk_bucket
        amount = st.session_state.savings_amount

        with chat_box:
            st.chat_message("assistant").write(
                f"Based on your answers, you're a **{bucket} risk** investor. "
                f"By trimming unnecessary spending, you unlocked **₹{amount}/month** to invest."
            )
            st.write(f"**Suggested instruments:** {', '.join(st.session_state.recommended_instruments)}")

        proj = requests.post(f"{API_URL}/api/investment-projection",
                              json={"monthly_investment": amount, "risk_bucket": bucket}).json()

        df_proj = pd.DataFrame({
            "Month": proj["months"],
            "Pessimistic": proj["pessimistic"],
            "Expected": proj["expected"],
            "Optimistic": proj["optimistic"],
        })

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_proj["Month"], y=df_proj["Expected"], name="Expected",
                                   line=dict(color="blue", width=3)))
        fig2.add_trace(go.Scatter(x=df_proj["Month"], y=df_proj["Optimistic"], name="Optimistic",
                                   line=dict(color="green", dash="dot")))
        fig2.add_trace(go.Scatter(x=df_proj["Month"], y=df_proj["Pessimistic"], name="Pessimistic",
                                   line=dict(color="red", dash="dot")))
        fig2.update_layout(title=f"5-Year Projected Growth (₹{amount}/month SIP)",
                            xaxis_title="Months", yaxis_title="Portfolio Value (₹)", height=400)
        st.plotly_chart(fig2, use_container_width=True)

        final_expected = df_proj["Expected"].iloc[-1]
        st.success(f"In 5 years, your ₹{amount}/month could grow to roughly ₹{final_expected:,.0f} "
                   f"under expected market conditions.")

        if st.button("🔄 Restart chat"):
            st.session_state.stage = "score"
            st.rerun()

st.markdown("---")
st.error("**🚨 FOR EDUCATIONAL PURPOSES ONLY. THIS PROTOTYPE DOES NOT CONSTITUTE REGULATED FINANCIAL ADVICE.**")
