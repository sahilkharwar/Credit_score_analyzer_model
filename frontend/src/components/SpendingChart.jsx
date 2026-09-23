import { useEffect, useState } from "react";
import api from "../services/api";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const COLORS = ["#2563EB", "#7C3AED", "#F59E0B", "#10B981"];

export default function SpendingChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const usersRes = await api.get("/users");
        const user = usersRes.data.users?.[0] || usersRes.data[0];

        if (!user?.user_id) return;

        const res = await api.get(`/spending-hook/${user.user_id}`);
        const s = res.data;

        setData([
          { name: "Food", value: s.food_delivery },
          { name: "Shopping", value: s.shopping },
          { name: "Subscriptions", value: s.subscriptions },
          { name: "Savings", value: s.possible_savings },
        ]);
      } catch (err) {
        console.error(err);
      }
    };

    loadData();
  }, []);

  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 min-h-[340px] flex flex-col">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold">Monthly Spending</h3>
        <p className="text-sm text-slate-500">Live spending analysis</p>
      </div>

      {/* Donut Chart */}
      <div className="flex justify-center items-center h-36 my-3">
        <div className="w-44 h-44">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
              <Pie
                data={data}
                dataKey="value"
                cx="50%"
                cy="50%"
                innerRadius={42}
                outerRadius={58}
                paddingAngle={3}
                stroke="#FFFFFF"
                strokeWidth={2}
              >
                {data.map((entry, index) => (
                  <Cell key={index} fill={COLORS[index]} />
                ))}
              </Pie>

              <Tooltip formatter={(value) => [`₹${value.toLocaleString()}`, "Amount"]} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-auto">
        <div className="mb-3">
          <p className="text-xs text-slate-400">Total Monthly Expense</p>
          <h3 className="text-2xl font-bold">
            ₹{total.toLocaleString()}
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-x-4 gap-y-2">
          {data.map((item, index) => (
            <div key={index} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: COLORS[index] }}
              />
              <span className="text-sm text-slate-600">{item.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}