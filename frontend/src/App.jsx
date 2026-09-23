import { Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import CreditAnalysis from "./pages/CreditAnalysis";
import Investments from "./pages/Investments";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/credit" element={<CreditAnalysis />} />
      <Route path="/investments" element={<Investments />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  );
}