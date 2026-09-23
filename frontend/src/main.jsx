import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import { CreditProvider } from "./context/CreditContext";

import "./index.css";
import App from "./App";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <CreditProvider>
        <App />
      </CreditProvider>
    </BrowserRouter>
  </StrictMode>
);