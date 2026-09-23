import {
  LayoutDashboard,
  Wallet,
  TrendingUp,
  Settings,
  ShieldCheck,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const MenuItem = ({ to, icon: Icon, label }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
        isActive
          ? "bg-blue-600 text-white shadow-lg"
          : "text-slate-300 hover:bg-slate-800 hover:text-white"
      }`
    }
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </NavLink>
);

export default function Sidebar() {
  return (
    <aside className="w-64 min-h-screen bg-slate-900 text-white p-6 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 mb-10">
        <div className="bg-blue-600 p-2 rounded-xl">
          <ShieldCheck size={24} />
        </div>

        <div>
          <h1 className="text-xl font-bold">FinSight</h1>
          <p className="text-xs text-slate-400">AI Credit Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="space-y-2 flex-1">
        <MenuItem
          to="/"
          icon={LayoutDashboard}
          label="Dashboard"
        />

        <MenuItem
          to="/credit"
          icon={Wallet}
          label="Credit Analysis"
        />

        <MenuItem
          to="/investments"
          icon={TrendingUp}
          label="Investment Planner"
        />

        <MenuItem
          to="/settings"
          icon={Settings}
          label="Settings"
        />
      </nav>

      {/* Bottom Card */}
      <div className="bg-slate-800 rounded-xl p-4 mt-8">
        <p className="text-xs text-slate-400">
          System Status
        </p>

        <div className="flex items-center gap-2 mt-2">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-sm font-medium">
            ML Model Online
          </span>
        </div>

        <p className="text-xs text-slate-500 mt-3">
          FastAPI + XGBoost
        </p>
      </div>
    </aside>
  );
}