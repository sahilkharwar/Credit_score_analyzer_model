import { createContext, useContext, useState } from "react";

const CreditContext = createContext();

export function CreditProvider({ children }) {
  const [creditData, setCreditData] = useState({
    score: 742,
    risk: "Medium",
    income: 38000,
  });

  return (
    <CreditContext.Provider value={{ creditData, setCreditData }}>
      {children}
    </CreditContext.Provider>
  );
}

export const useCredit = () => useContext(CreditContext);