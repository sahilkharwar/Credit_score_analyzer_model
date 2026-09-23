import Sidebar from "../components/Sidebar";
import StatCard from "../components/StatCard";
import ScoreGauge from "../components/ScoreGauge";
import SpendingChart from "../components/SpendingChart";
import PortfolioChart from "../components/PortfolioChart";
import Transactions from "../components/Transactions";
import { useCredit } from "../context/CreditContext";

export default function Dashboard() {
  const { creditData } = useCredit();

  return (
    <div className="flex min-h-screen bg-slate-100">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        <div className="p-8 max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <p className="text-sm font-medium text-blue-600">
              AI Powered Financial Analytics
            </p>

            <h1 className="text-4xl font-bold text-slate-900 mt-1">
              Welcome back, Sahil
            </h1>

            <p className="text-slate-500 mt-2">
              Monitor your credit score, expenses and investment growth.
            </p>
          </div>

          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <StatCard
              title="Credit Score"
              value={creditData.score}
              color="blue"
            />

            <StatCard
              title="Monthly Income"
              value={`₹${creditData.income.toLocaleString()}`}
              color="green"
            />

            <StatCard
              title="Risk Level"
              value={creditData.risk}
              color="orange"
            />
          </div>

          {/* Score + Spending */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-7 items-start">
            <div className="h-full">
              <ScoreGauge />
            </div>

            <div className="h-full">
              <SpendingChart />
            </div>
          </div>

          {/* Portfolio + Transactions */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mt-7 items-start">
            <div className="xl:col-span-2 h-full">
              <PortfolioChart />
            </div>

            <div className="h-full">
              <Transactions />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}