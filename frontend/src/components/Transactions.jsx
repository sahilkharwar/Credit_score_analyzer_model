import { useEffect, useState } from "react";
import api from "../services/api";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    const loadTransactions = async () => {
      try {
        // Get first available user
        const usersRes = await api.get("/users");
        const firstUser =
          usersRes.data.users?.[0] || usersRes.data[0];

        if (!firstUser?.user_id) return;

        // Get spending data
        const spendRes = await api.get(
          `/spending-hook/${firstUser.user_id}`
        );

        const s = spendRes.data;

        setTransactions([
          {
            name: "Salary",
            amount: 38000,
            type: "income",
            date: "Today",
          },
          {
            name: "Food Delivery",
            amount: s.food_delivery,
            type: "expense",
            date: "22 Sep",
          },
          {
            name: "Shopping",
            amount: s.shopping,
            type: "expense",
            date: "21 Sep",
          },
          {
            name: "Subscriptions",
            amount: s.subscriptions,
            type: "expense",
            date: "20 Sep",
          },
        ]);
      } catch (err) {
        console.error(err);
      }
    };

    loadTransactions();
  }, []);

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200">
      <h3 className="text-lg font-semibold mb-4">
        Recent Transactions
      </h3>

      <div className="space-y-4">
        {transactions.map((t, index) => (
          <div
            key={index}
            className="flex items-center justify-between border-b border-slate-100 pb-3 last:border-0"
          >
            <div className="flex items-center gap-3">
              <div
                className={`p-2 rounded-full ${
                  t.type === "income"
                    ? "bg-green-100"
                    : "bg-red-100"
                }`}
              >
                {t.type === "income" ? (
                  <ArrowDownRight
                    size={18}
                    className="text-green-600"
                  />
                ) : (
                  <ArrowUpRight
                    size={18}
                    className="text-red-500"
                  />
                )}
              </div>

              <div>
                <p className="font-medium">{t.name}</p>
                <p className="text-xs text-slate-500">
                  {t.date}
                </p>
              </div>
            </div>

            <span
              className={`font-semibold ${
                t.type === "income"
                  ? "text-green-600"
                  : "text-red-500"
              }`}
            >
              {t.type === "income" ? "+" : "-"}₹
              {t.amount.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}