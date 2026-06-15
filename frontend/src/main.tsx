import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import AppSeguros from "./AppSeguros";

type View = "panel3d" | "seguros";

function Root() {
  const [view, setView] = useState<View>("panel3d");

  return (
    <>
      {/* Selector de vista (flotante) */}
      <div style={switcher}>
        <button
          onClick={() => setView("panel3d")}
          style={{ ...tab, ...(view === "panel3d" ? tabActive : {}) }}
        >
          🎮 Panel 3D
        </button>
        <button
          onClick={() => setView("seguros")}
          style={{ ...tab, ...(view === "seguros" ? tabActive : {}) }}
        >
          🚗 Gestión Seguros
        </button>
      </div>

      {view === "panel3d" ? <App /> : <AppSeguros />}
    </>
  );
}

const switcher: React.CSSProperties = {
  position: "fixed",
  top: 12,
  left: "50%",
  transform: "translateX(-50%)",
  zIndex: 3000,
  display: "flex",
  gap: 6,
  padding: 4,
  background: "#161b22cc",
  border: "1px solid #30363d",
  borderRadius: 10,
  backdropFilter: "blur(8px)",
};

const tab: React.CSSProperties = {
  padding: "6px 14px",
  borderRadius: 7,
  border: "none",
  background: "transparent",
  color: "#8b949e",
  fontSize: 13,
  fontWeight: 700,
  cursor: "pointer",
};

const tabActive: React.CSSProperties = {
  background: "#1f6feb",
  color: "#fff",
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
