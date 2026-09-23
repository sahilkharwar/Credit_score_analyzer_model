import { useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";
import { useCredit } from "../context/CreditContext";
import ShapCards from "../components/ShapCards";

export default function CreditAnalysis() {
  const { creditData, setCreditData } = useCredit();

  const [form, setForm] = useState({
    income: creditData.income || 38000,
    age: 22,
    savings: 12000,
    loan: 45000,
  });

  const [loading, setLoading] = useState(false);
  const [shap, setShap] = useState([]);
  const [tip, setTip] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const predict = async () => {
    setLoading(true);

    try {
      // Predict credit score
      const scoreRes = await api.post("/score-credit", {
        income: Number(form.income),
        age: Number(form.age),
        savings: Number(form.savings),
        loan: Number(form.loan),
      });

      setCreditData({
        score: scoreRes.data.score,
        risk: scoreRes.data.risk,
        income: Number(form.income),
      });

      // Get available users
      const usersRes = await api.get("/users");

      const firstUser =
        usersRes.data.users?.[0] ||
        usersRes.data[0];

      if (firstUser?.user_id) {
        const explainRes = await api.get(
          `/explain-score/${firstUser.user_id}`
        );

        setShap(explainRes.data.top_features || []);
        setTip(explainRes.data.improvement_tip || "");
      } else {
        setShap([]);
        setTip("No user data available for SHAP explanation.");
      }
    } catch (err) {
      console.error(err);
      alert("Unable to connect to FastAPI backend.");
    }

    setLoading(false);
  };

  const progress = (creditData.score / 850) * 100;

  return (
    <div className="flex min-h-screen bg-slate-100">
      <Sidebar />

      <main className="flex-1 p-8 overflow-y-auto">
        {/* Header */}
        <div className="mb-8">
          <p className="text-blue-600 text-sm font-medium">
            AI Powered Credit Intelligence
          </p>

          <h1 className="text-4xl font-bold mt-1">
            Credit Analysis
          </h1>

          <p className="text-slate-500 mt-2">
            Predict customer credit score using XGBoost and Explainable AI.
          </p>
        </div>

        {/* Top Section */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* Form */}
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-6">
              Customer Financial Profile
            </h2>

            <div className="space-y-5">
              <div>
                <label className="text-sm text-slate-500">
                  Monthly Income (₹)
                </label>
                <input
                  type="number"
                  name="income"
                  value={form.income}
                  onChange={handleChange}
                  className="w-full mt-2 border rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="text-sm text-slate-500">
                  Age
                </label>
                <input
                  type="number"
                  name="age"
                  value={form.age}
                  onChange={handleChange}
                  className="w-full mt-2 border rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="text-sm text-slate-500">
                  Savings (₹)
                </label>
                <input
                  type="number"
                  name="savings"
                  value={form.savings}
                  onChange={handleChange}
                  className="w-full mt-2 border rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="text-sm text-slate-500">
                  Current Loan (₹)
                </label>
                <input
                  type="number"
                  name="loan"
                  value={form.loan}
                  onChange={handleChange}
                  className="w-full mt-2 border rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <button
                onClick={predict}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 rounded-lg font-semibold transition"
              >
                {loading ? "Running ML Model..." : "Predict Credit Score"}
              </button>
            </div>
          </div>

          {/* Result */}
          <div className="bg-white rounded-2xl shadow-sm p-6 flex flex-col justify-center">
            <p className="text-slate-500 text-sm">
              Predicted Credit Score
            </p>

            <h1 className="text-7xl font-bold text-blue-600 mt-2">
              {creditData.score}
            </h1>

            <div className="mt-6">
              <p className="text-sm text-slate-500">
                Risk Category
              </p>

              <div className="inline-flex mt-2 px-4 py-2 rounded-full bg-blue-100 text-blue-700 font-semibold">
                {creditData.risk}
              </div>
            </div>

            <div className="mt-8">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-500">
                  Score Progress
                </span>
                <span className="font-semibold">
                  {creditData.score}/850
                </span>
              </div>

              <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-600 rounded-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>

              <div className="flex justify-between text-xs text-slate-400 mt-2">
                <span>300</span>
                <span>850</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-8">
              <div className="bg-slate-50 rounded-xl p-4">
                <p className="text-xs text-slate-500">
                  Income
                </p>
                <h3 className="font-bold text-lg">
                  ₹{creditData.income.toLocaleString()}
                </h3>
              </div>

              <div className="bg-slate-50 rounded-xl p-4">
                <p className="text-xs text-slate-500">
                  Savings
                </p>
                <h3 className="font-bold text-lg">
                  ₹{Number(form.savings).toLocaleString()}
                </h3>
              </div>
            </div>
          </div>
        </div>

        {/* SHAP Explainability */}
        <ShapCards features={shap} tip={tip} />
      </main>
    </div>
  );
}