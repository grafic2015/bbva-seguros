import { useAgentSocket } from "./hooks/useAgentSocket";
import { Scene } from "./scene/Scene";
import { ControlPanel } from "./components/ControlPanel";
import { ResultsPanel } from "./components/ResultsPanel";

export default function App() {
  useAgentSocket();

  return (
    <div className="app-container" style={{ display: "flex", height: "100vh", width: "100vw", background: "#0d1117" }}>
      <ControlPanel />
      <div style={{ flex: 1, position: "relative" }}>
        <Scene />

        {/* Overlay superior: título y controles */}
        <div style={overlay}>
          <h1 style={{ margin: 0, fontSize: 15, color: "#e1306c", fontWeight: 700 }}>
            📸 Seguros BBVA — Ciudad de Agentes
          </h1>
          <span style={{ fontSize: 11, color: "#8b949e" }}>
            🔴 Flechas · 🔵 WASD · Auto-piloto cuando no hay input
          </span>
        </div>
      </div>

      {/* Panel de resultados (tabla de leads) */}
      <ResultsPanel />
    </div>
  );
}

const overlay: React.CSSProperties = {
  position: "absolute", top: 16, left: 16,
  padding: "8px 14px", background: "#161b22cc",
  border: "1px solid #30363d", borderRadius: 8,
  backdropFilter: "blur(8px)",
  display: "flex", flexDirection: "column", gap: 2,
};
