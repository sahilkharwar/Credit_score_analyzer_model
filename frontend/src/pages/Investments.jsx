import { useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

export default function Investments() {
  const [amount, setAmount] = useState(2000);
  const [risk, setRisk] = useState("Medium");
  const [years, setYears] = useState(10);
  const [scenario, setScenario] = useState("expected");

  const [graph, setGraph] = useState([]);
  const [funds, setFunds] = useState([]);
  const [loading, setLoading] = useState(false);

  const calculate = async () => {
    setLoading(true);

    try {
      const res = await api.post("/investment-projection", {
        monthly_investment: Number(amount),
        risk_bucket: risk,
        years: Number(years),
      });

      const chart = res.data.months.map((m, i) => ({
        year: (m / 12).toFixed(1),
        pessimistic: Math.round(res.data.pessimistic[i]),
        expected: Math.round(res.data.expected[i]),
        optimistic: Math.round(res.data.optimistic[i]),
      }));

      setGraph(chart);
      setFunds(res.data.recommended_instruments);
    } catch (err) {
      console.error(err);
      alert("Unable to generate projection.");
    }

    setLoading(false);
  };

  const finalValue =
    graph.length > 0
      ? graph[graph.length - 1][scenario]
      : 0;

  return (
    <div className="flex min-h-screen bg-slate-100">
      <Sidebar />

      <main className="flex-1 p-8 overflow-y-auto">
        <div className="mb-8">
          <p className="text-sm font-medium text-blue-600">
            AI Powered Investment Advisor
          </p>

          <h1 className="text-4xl font-bold mt-1">
            Investment Planner
          </h1>

          <p className="text-slate-500 mt-2">
            Simulate long-term wealth creation with AI driven market scenarios.
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Left Panel */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-6">
              SIP Calculator
            </h2>

            <label className="text-sm text-slate-500">
              Monthly Investment
            </label>

            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full mt-2 mb-5 border rounded-lg p-3"
            />

            <label className="text-sm text-slate-500">
              Risk Profile
            </label>

            <select
              value={risk}
              onChange={(e) => setRisk(e.target.value)}
              className="w-full mt-2 border rounded-lg p-3"
            >
              <option>Low</option>
              <option>Medium</option>
              <option>High</option>
            </select>

            {/* Years Slider */}
            <div className="mt-6">
              <div className="flex justify-between mb-2">
                <label className="text-sm text-slate-500">
                  Investment Period
                </label>

                <span className="font-semibold">
                  {years} Years
                </span>
              </div>

              <input
                type="range"
                min="1"
                max="30"
                value={years}
                onChange={(e) => setYears(Number(e.target.value))}
                className="w-full accent-blue-600"
              />
            </div>

            <button
              onClick={calculate}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg py-3 mt-6 font-semibold"
            >
              {loading ? "Generating..." : "Generate Projection"}
            </button>

            {funds.length > 0 && (
              <div className="mt-8">
                <h3 className="font-semibold mb-3">
                  Recommended Instruments
                </h3>

                <div className="space-y-2">
                  {funds.map((fund, i) => (
                    <div
                      key={i}
                      className="bg-blue-50 text-blue-700 rounded-lg px-3 py-2 text-sm"
                    >
                      {fund}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Panel */}
          <div className="xl:col-span-2 bg-white rounded-2xl p-6 shadow-sm">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-xl font-semibold">
                  Portfolio Projection
                </h2>

                <p className="text-slate-500 text-sm">
                  Dynamic wealth forecast
                </p>
              </div>

              <div className="text-right">
                <p className="text-xs text-slate-500">
                  Projected Value
                </p>

                <h2 className="text-3xl font-bold text-green-600">
                  ₹{finalValue.toLocaleString()}
                </h2>
              </div>
            </div>

            {/* Scenario Buttons */}
            <div className="flex gap-3 mt-6">
              {["pessimistic", "expected", "optimistic"].map((item) => (
                <button
                  key={item}
                  onClick={() => setScenario(item)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                    scenario === item
                      ? "bg-blue-600 text-white"
                      : "bg-slate-100 text-slate-600"
                  }`}
                >
                  {item.charAt(0).toUpperCase() + item.slice(1)}
                </button>
              ))}
            </div>

            {/* Chart */}
            <div className="h-80 mt-6">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={graph}>
                  <defs>
                    <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563EB" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                    </linearGradient>
                  </defs>

                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
                  <Tooltip formatter={(v) => `₹${v.toLocaleString()}`} />

                  <Area
                    type="monotone"
                    dataKey={scenario}
                    stroke="#2563EB"
                    strokeWidth={3}
                    fill="url(#fill)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Bottom Stats */}
            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="bg-slate-50 rounded-xl p-4">
                <p className="text-xs text-slate-500">
                  Monthly SIP
                </p>

                <h3 className="text-xl font-bold">
                  ₹{Number(amount).toLocaleString()}
                </h3>
              </div>

              <div className="bg-slate-50 rounded-xl p-4">
                <p className="text-xs text-slate-500">
                  Duration
                </p>

                <h3 className="text-xl font-bold">
                  {years} Years
                </h3>
              </div>

              <div className="bg-slate-50 rounded-xl p-4">
                <p className="text-xs text-slate-500">
                  Scenario
                </p>

                <h3 className="text-xl font-bold capitalize">
                  {scenario}
                </h3>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}