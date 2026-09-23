import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

const data = [
  { month: "Jan", score: 610 },
  { month: "Feb", score: 640 },
  { month: "Mar", score: 670 },
  { month: "Apr", score: 710 },
  { month: "May", score: 742 },
];

export default function ScoreChart() {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 h-80">
      <h3 className="font-semibold text-lg">Credit Score Progress</h3>
      <p className="text-slate-500 text-sm mb-4">
        Last 5 months performance
      </p>

      <ResponsiveContainer width="100%" height="82%">
        <LineChart data={data}>
          <CartesianGrid stroke="#E5E7EB" vertical={false} />
          <XAxis dataKey="month" />
          <YAxis domain={[580, 780]} />
          <Tooltip />
          <Line
            dataKey="score"
            stroke="#2563EB"
            strokeWidth={3}
            dot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}