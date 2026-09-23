import { TrendingUp, TrendingDown, Brain } from "lucide-react";

export default function ShapCards({ features = [], tip = "" }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm p-6 mt-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <div className="bg-blue-100 p-2 rounded-lg">
          <Brain className="text-blue-600" size={22} />
        </div>

        <div>
          <h2 className="text-2xl font-bold">
            SHAP Explainability
          </h2>
          <p className="text-sm text-slate-500">
            Top features influencing the AI credit score
          </p>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-6">
        {features.length === 0 ? (
          <div className="col-span-3 py-12 text-center border-2 border-dashed border-slate-200 rounded-xl">
            <Brain className="mx-auto text-slate-300" size={38} />
            <p className="text-slate-500 mt-3 font-medium">
              No SHAP explanation yet
            </p>
            <p className="text-sm text-slate-400">
              Run a credit prediction to generate feature importance.
            </p>
          </div>
        ) : (
          features.map((item, index) => {
            const impact = item.impact ?? item.impact_points ?? 0;
            const positive = impact >= 0;

            return (
              <div
                key={index}
                className="border rounded-xl p-5 hover:shadow-md transition bg-slate-50"
              >
                <div className="flex justify-between items-center">
                  <p className="text-sm text-slate-500">
                    {item.feature}
                  </p>

                  {positive ? (
                    <TrendingUp className="text-green-600" size={18} />
                  ) : (
                    <TrendingDown className="text-red-500" size={18} />
                  )}
                </div>

                <h3
                  className={`text-3xl font-bold mt-3 ${
                    positive ? "text-green-600" : "text-red-500"
                  }`}
                >
                  {positive ? "+" : ""}
                  {impact}
                </h3>

                <div className="mt-4 h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      positive ? "bg-green-500" : "bg-red-500"
                    }`}
                    style={{
                      width: `${Math.min(Math.abs(impact) * 5, 100)}%`,
                    }}
                  />
                </div>

                <p className="text-xs text-slate-400 mt-2">
                  SHAP Contribution
                </p>
              </div>
            );
          })
        )}
      </div>

      {/* Recommendation */}
      {tip && (
        <div className="mt-8 rounded-xl bg-blue-50 border border-blue-200 p-5">
          <div className="flex items-center gap-2 mb-2">
            <Brain className="text-blue-600" size={20} />
            <h3 className="font-semibold text-blue-700">
              AI Improvement Recommendation
            </h3>
          </div>

          <p className="text-slate-700 leading-relaxed">
            {tip}
          </p>
        </div>
      )}
    </div>
  );
}