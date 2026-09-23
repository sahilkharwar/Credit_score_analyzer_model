import { useCredit } from "../context/CreditContext";

export default function ScoreGauge() {
  const { creditData } = useCredit();

  const score = creditData.score || 300;
  const percentage = ((score - 300) / 550) * 100;
  const angle = (percentage / 100) * 180 - 90;

  const status =
    score >= 730
      ? "Excellent"
      : score >= 620
      ? "Good"
      : "Needs Improvement";

  const color =
    score >= 730
      ? "#16A34A"
      : score >= 620
      ? "#2563EB"
      : "#EA580C";

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 h-80">
      <h3 className="text-lg font-semibold">Credit Score</h3>
      <p className="text-sm text-slate-500">Live ML Prediction</p>

      <div className="flex justify-center items-center mt-5">
        <div className="relative w-72 h-44">
          <svg viewBox="0 0 240 140" className="w-full h-full">
            <path
              d="M30 110 A90 90 0 0 1 210 110"
              fill="none"
              stroke="#E5E7EB"
              strokeWidth="14"
              strokeLinecap="round"
            />

            <path
              d="M30 110 A90 90 0 0 1 210 110"
              fill="none"
              stroke={color}
              strokeWidth="14"
              strokeLinecap="round"
              pathLength="100"
              strokeDasharray={`${percentage} 100`}
            />

            <g transform={`rotate(${angle} 120 110)`}>
              <line
                x1="120"
                y1="110"
                x2="120"
                y2="30"
                stroke="#0F172A"
                strokeWidth="3"
                strokeLinecap="round"
              />
              <circle cx="120" cy="110" r="5" fill="#0F172A" />
            </g>
          </svg>

          {/* Centered score */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pt-4">
            <h1 className="text-5xl font-bold text-slate-900">
              {score}
            </h1>

            <p
              className="font-semibold mt-1"
              style={{ color }}
            >
              {status}
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-between text-sm text-slate-400 mt-2">
        <span>300</span>
        <span>850</span>
      </div>
    </div>
  );
}