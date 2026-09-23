import { useEffect, useState } from "react";
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

export default function PortfolioChart() {
  const [data, setData] = useState([]);
  const [scenario, setScenario] = useState("expected");

  useEffect(() => {
    const loadPortfolio = async () => {
      try {
        const res = await api.post("/investment-projection", {
          monthly_investment: 2000,
          risk_bucket: "Medium",
          years: 10,
        });

        const chart = res.data.months.map((month, i) => ({
          year: (month / 12).toFixed(1),
          pessimistic: Math.round(res.data.pessimistic[i]),
          expected: Math.round(res.data.expected[i]),
          optimistic: Math.round(res.data.optimistic[i]),
        }));

        setData(chart);
      } catch (err) {
        console.error(err);
      }
    };

    loadPortfolio();
  }, []);

  const finalValue =
    data.length > 0 ? data[data.length - 1][scenario] : 0;

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 h-full">
      {/* Header */}
      <div className="flex justify-between items-start mb-5">
        <div>
          <h3 className="text-lg font-semibold">
            Portfolio Growth
          </h3>
          <p className="text-sm text-slate-500">
            10-Year AI Investment Forecast
          </p>
        </div>

        <div className="text-right">
          <p className="text-xs text-slate-500">
            Projected Value
          </p>
          <h2 className="text-2xl font-bold text-green-600">
            ₹{finalValue.toLocaleString()}
          </h2>
        </div>
      </div>

      {/* Scenario Buttons */}
      <div className="flex gap-2 mb-4">
        {["pessimistic", "expected", "optimistic"].map((item) => (
          <button
            key={item}
            onClick={() => setScenario(item)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
              scenario === item
                ? "bg-blue-600 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {item.charAt(0).toUpperCase() + item.slice(1)}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="portfolioFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563EB" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />

            <XAxis
              dataKey="year"
              tick={{ fontSize: 11 }}
              tickMargin={8}
            />

            <YAxis
              tickFormatter={(v) => `${Math.round(v / 1000)}k`}
              tick={{ fontSize: 11 }}
            />

            <Tooltip
              formatter={(value) => `₹${value.toLocaleString()}`}
              labelFormatter={(label) => `Year ${label}`}
            />

            <Area
              type="monotone"
              dataKey={scenario}
              stroke="#2563EB"
              strokeWidth={3}
              fill="url(#portfolioFill)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Footer Stats */}
      <div className="grid grid-cols-3 gap-3 mt-5">
        <div className="bg-slate-50 rounded-lg p-3">
          <p className="text-xs text-slate-500">SIP</p>
          <h3 className="font-bold">₹2,000</h3>
        </div>

        <div className="bg-slate-50 rounded-lg p-3">
          <p className="text-xs text-slate-500">Duration</p>
          <h3 className="font-bold">10 Years</h3>
        </div>

        <div className="bg-slate-50 rounded-lg p-3">
          <p className="text-xs text-slate-500">Scenario</p>
          <h3 className="font-bold capitalize">{scenario}</h3>
        </div>
      </div>
    </div>
  );
}