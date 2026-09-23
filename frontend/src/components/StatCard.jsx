const colors = {
  blue: "text-blue-600 bg-blue-50",
  green: "text-green-600 bg-green-50",
  orange: "text-orange-500 bg-orange-50",
};

export default function StatCard({ title, value, color }) {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200">
      <div
        className={`w-11 h-11 rounded-xl flex items-center justify-center mb-4 ${colors[color]}`}
      >
        <div className="w-3 h-3 bg-current rounded-full" />
      </div>

      <p className="text-slate-500 text-sm">{title}</p>

      <h2 className="text-3xl font-bold mt-2">{value}</h2>
    </div>
  );
}