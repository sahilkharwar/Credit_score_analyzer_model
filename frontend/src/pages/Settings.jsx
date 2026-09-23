import { useState } from "react";
import Sidebar from "../components/Sidebar";
import { useCredit } from "../context/CreditContext";
import {
  User,
  ShieldCheck,
  Database,
  Brain,
  Server,
  Bell,
  CheckCircle,
} from "lucide-react";

export default function Settings() {
  const { creditData } = useCredit();

  const [notifications, setNotifications] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  return (
    <div className="flex min-h-screen bg-slate-100">
      <Sidebar />

      <main className="flex-1 p-8 overflow-y-auto">
        {/* Header */}
        <div className="mb-8">
          <p className="text-blue-600 text-sm font-medium">
            Application Preferences
          </p>

          <h1 className="text-4xl font-bold mt-1">
            Settings
          </h1>

          <p className="text-slate-500 mt-2">
            Manage your profile, AI model information and application settings.
          </p>
        </div>

        {/* Profile */}
        <div className="bg-white rounded-2xl shadow-sm p-6 mb-6">
          <div className="flex items-center gap-4">
            <div className="bg-blue-100 p-4 rounded-full">
              <User size={30} className="text-blue-600" />
            </div>

            <div>
              <h2 className="text-xl font-bold">Sahil Kharwar</h2>
              <p className="text-slate-500">
                MSc Information Technology • AI & ML
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs text-slate-500">Current Score</p>
              <h3 className="text-2xl font-bold text-blue-600">
                {creditData.score}
              </h3>
            </div>

            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs text-slate-500">Risk</p>
              <h3 className="text-2xl font-bold">{creditData.risk}</h3>
            </div>

            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs text-slate-500">Income</p>
              <h3 className="text-lg font-bold">
                ₹{creditData.income.toLocaleString()}
              </h3>
            </div>

            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs text-slate-500">Version</p>
              <h3 className="text-lg font-bold">v1.0</h3>
            </div>
          </div>
        </div>

        {/* AI + Backend */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-4">
              <Brain className="text-blue-600" />
              <h2 className="text-xl font-semibold">AI Model</h2>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Model</span>
                <span className="font-medium">XGBoost Regressor</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">Explainability</span>
                <span className="font-medium">SHAP TreeExplainer</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">Prediction Range</span>
                <span className="font-medium">300 – 850</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">Status</span>

                <div className="flex items-center gap-2 text-green-600 font-medium">
                  <CheckCircle size={16} />
                  Online
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-4">
              <Server className="text-green-600" />
              <h2 className="text-xl font-semibold">Backend</h2>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Framework</span>
                <span className="font-medium">FastAPI</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">API</span>
                <span className="font-medium">127.0.0.1:8000</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">Database</span>
                <span className="font-medium">Synthetic Dataset</span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">Connection</span>

                <div className="flex items-center gap-2 text-green-600 font-medium">
                  <CheckCircle size={16} />
                  Connected
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div className="bg-white rounded-2xl shadow-sm p-6 mb-6">
          <div className="flex items-center gap-3 mb-5">
            <Bell className="text-orange-500" />
            <h2 className="text-xl font-semibold">
              Application Preferences
            </h2>
          </div>

          <div className="space-y-5">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-medium">Push Notifications</p>
                <p className="text-sm text-slate-500">
                  Receive prediction & investment alerts
                </p>
              </div>

              <button
                onClick={() => setNotifications(!notifications)}
                className={`w-14 h-7 rounded-full transition ${
                  notifications ? "bg-blue-600" : "bg-slate-300"
                }`}
              >
                <div
                  className={`w-6 h-6 bg-white rounded-full transition transform ${
                    notifications ? "translate-x-7" : "translate-x-1"
                  }`}
                />
              </button>
            </div>

            <div className="flex justify-between items-center">
              <div>
                <p className="font-medium">Auto Refresh Dashboard</p>
                <p className="text-sm text-slate-500">
                  Keep analytics synchronized automatically
                </p>
              </div>

              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`w-14 h-7 rounded-full transition ${
                  autoRefresh ? "bg-blue-600" : "bg-slate-300"
                }`}
              >
                <div
                  className={`w-6 h-6 bg-white rounded-full transition transform ${
                    autoRefresh ? "translate-x-7" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* About */}
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <div className="flex items-center gap-3 mb-4">
            <ShieldCheck className="text-indigo-600" />
            <h2 className="text-xl font-semibold">About FinSight</h2>
          </div>

          <p className="text-slate-600 leading-7">
            FinSight is an AI-powered transparent credit scoring and
            micro-investment advisory platform developed using React,
            FastAPI, XGBoost and SHAP Explainable AI. The system predicts
            credit scores, explains the influencing financial factors and
            generates long-term investment projections based on user risk
            profiles.
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="text-center bg-slate-50 rounded-xl p-3">
              <Database className="mx-auto text-blue-600 mb-2" size={22} />
              <p className="text-xs text-slate-500">Frontend</p>
              <h4 className="font-semibold">React</h4>
            </div>

            <div className="text-center bg-slate-50 rounded-xl p-3">
              <Server className="mx-auto text-green-600 mb-2" size={22} />
              <p className="text-xs text-slate-500">Backend</p>
              <h4 className="font-semibold">FastAPI</h4>
            </div>

            <div className="text-center bg-slate-50 rounded-xl p-3">
              <Brain className="mx-auto text-purple-600 mb-2" size={22} />
              <p className="text-xs text-slate-500">ML Model</p>
              <h4 className="font-semibold">XGBoost</h4>
            </div>

            <div className="text-center bg-slate-50 rounded-xl p-3">
              <ShieldCheck className="mx-auto text-orange-500 mb-2" size={22} />
              <p className="text-xs text-slate-500">Explainability</p>
              <h4 className="font-semibold">SHAP</h4>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t text-sm text-slate-500 flex justify-between">
            <span>FinSight v1.0</span>
            <span>© 2026 Final Year Project</span>
          </div>
        </div>
      </main>
    </div>
  );
}