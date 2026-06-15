import { useStore } from "../store";
import { startAgent, stopAgent } from "../hooks/useAgentSocket";
import { AGENT_META, type AgentId } from "../types";

export function ControlPanel() {
  const agents      = useStore((s) => s.agents);
  const connected   = useStore((s) => s.connected);
  const leads       = useStore((s) => s.leads);

  // Estadísticas calculadas desde los leads
  const stats = {
    total:          leads.length,
    nuevos:         leads.filter((l) => l.estado === "nuevo").length,
    interesados:    leads.filter((l) => l.estado === "interesado").length,
    en_seguimiento: leads.filter((l) => l.estado === "en_seguimiento").length,
    convertidos:    leads.filter((l) => l.estado === "convertido").length,
    rechazados:     leads.filter((l) => l.estado === "rechazado").length,
  };

  return (
    <div style={styles.panel}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.logo}>
          <span style={{ fontSize: 32 }}>🚗</span>
          <div>
            <div style={{ fontSize: 26, fontWeight: 700, color: "#e6edf3" }}>Seguros BBVA</div>
            <div style={{ fontSize: 16, color: "#8b949e" }}>Dashboard de Agentes</div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ ...styles.dot, background: connected ? "#3fb950" : "#f85149" }} />
          <span style={{ fontSize: 18, color: connected ? "#3fb950" : "#f85149" }}>
            {connected ? "En línea" : "Sin conexión"}
          </span>
        </div>
      </div>

      {/* Stats de leads */}
      <div style={styles.statsCard}>
        <div style={styles.statsTitle}>📊 Leads Totales</div>
        <div style={styles.statsGrid}>
          <div style={styles.statItem}>
            <span style={{ ...styles.statVal, color: "#58a6ff" }}>{stats.total}</span>
            <span style={styles.statLabel}>Total</span>
          </div>
          <div style={styles.statItem}>
            <span style={{ ...styles.statVal, color: "#d29922" }}>{stats.nuevos}</span>
            <span style={styles.statLabel}>Nuevos</span>
          </div>
          <div style={styles.statItem}>
            <span style={{ ...styles.statVal, color: "#e1306c" }}>{stats.interesados}</span>
            <span style={styles.statLabel}>Interesados</span>
          </div>
          <div style={styles.statItem}>
            <span style={{ ...styles.statVal, color: "#3fb950" }}>{stats.convertidos}</span>
            <span style={styles.statLabel}>Convertidos</span>
          </div>
        </div>
        {/* Barra de progreso de conversión */}
        {stats.total > 0 && (
          <div style={{ marginTop: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 18, color: "#8b949e", marginBottom: 3 }}>
              <span>Tasa de conversión</span>
              <span>{Math.round((stats.convertidos / stats.total) * 100)}%</span>
            </div>
            <div style={styles.progressTrack}>
              <div style={{
                ...styles.progressFill,
                width: `${(stats.convertidos / stats.total) * 100}%`,
                background: "linear-gradient(90deg, #e1306c, #3fb950)",
              }} />
            </div>
          </div>
        )}
      </div>

      {/* Ver tabla de leads */}
      <button
        id="btn-ver-leads"
        style={styles.bigBtn}
        onClick={() => window.open(`${location.origin}${location.pathname}?view=leads`, "_blank")}
      >
        📋 Ver tabla de Leads
      </button>

      <div style={styles.divider} />
      <div style={{ fontSize: 18, color: "#8b949e", textTransform: "uppercase", letterSpacing: 1 }}>
        Agentes Activos
      </div>

      {/* Tarjeta de cada agente */}
      {(Object.keys(AGENT_META) as AgentId[]).map((id) => {
        const a    = agents[id];
        const meta = AGENT_META[id];
        const isRunning = a.status === "running";

        return (
          <div key={id} style={{ ...styles.agentCard, borderColor: isRunning ? meta.color : "#30363d" }}>
            {/* Header de la tarjeta */}
            <div style={styles.agentHeader}>
              <span style={{ fontSize: 24 }}>{meta.emoji}</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 18, fontWeight: 700, color: meta.color }}>{meta.name}</div>
                <div style={{ fontSize: 14, color: "#8b949e", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {meta.description}
                </div>
              </div>
              <span style={{ ...styles.badge, ...badgeColor(a.status) }}>{a.status}</span>
            </div>

            {/* Mensaje de estado */}
            <div style={styles.agentMsg}>{a.mensaje || "Esperando..."}</div>

            {/* Stats del agente */}
            {id === "instagram" && (
              <div style={styles.agentStat}>
                🎯 Leads encontrados: <strong style={{ color: meta.color }}>{a.leads_encontrados ?? 0}</strong>
              </div>
            )}
            {id === "leads" && (
              <div style={styles.agentStat}>
                📁 Leads gestionados: <strong style={{ color: meta.color }}>{a.total_leads ?? stats.total}</strong>
              </div>
            )}

            {/* Últimos logs */}
            {a.logs && a.logs.length > 0 && (
              <div style={styles.logBox}>
                {a.logs.slice(-3).map((log, i) => (
                  <div key={i} style={styles.logLine}>▸ {log}</div>
                ))}
              </div>
            )}

            {/* Botones de control */}
            <div style={styles.btnRow}>
              <button
                id={`btn-start-${id}`}
                style={{
                  ...styles.btn,
                  background: isRunning ? "#1a2e1a" : "#238636",
                  opacity: isRunning ? 0.5 : 1,
                  cursor: isRunning ? "not-allowed" : "pointer",
                }}
                disabled={isRunning}
                onClick={() => startAgent(id)}
              >
                ▶ Iniciar
              </button>
              <button
                id={`btn-stop-${id}`}
                style={{
                  ...styles.btn,
                  background: isRunning ? "#3a1f1f" : "#21262d",
                  opacity: isRunning ? 1 : 0.5,
                  cursor: isRunning ? "pointer" : "not-allowed",
                }}
                disabled={!isRunning}
                onClick={() => stopAgent(id)}
              >
                ⏹ Detener
              </button>
            </div>
          </div>
        );
      })}

      {/* Instrucciones de manejo */}
      <div style={styles.helpBox}>
        <div style={{ fontSize: 14, color: "#8b949e", marginBottom: 4, fontWeight: 600 }}>🎮 Controles de autos</div>
        <div style={{ fontSize: 12, color: "#6e7681", lineHeight: 1.6 }}>
          <div>🔴 Auto rojo: <kbd style={styles.kbd}>↑↓←→</kbd></div>
          <div>🔵 Auto azul: <kbd style={styles.kbd}>W A S D</kbd></div>
          <div style={{ marginTop: 4, color: "#58a6ff" }}>✨ Auto-piloto cuando no hay input</div>
        </div>
      </div>
    </div>
  );
}

function badgeColor(s: string): React.CSSProperties {
  switch (s) {
    case "running": return { background: "#1f6feb33", color: "#58a6ff", animation: "pulse 2s infinite" };
    case "done":    return { background: "#3fb95033", color: "#3fb950" };
    case "error":   return { background: "#f8514933", color: "#f85149" };
    default:        return { background: "#30363d",   color: "#8b949e" };
  }
}

const styles: Record<string, React.CSSProperties> = {
  panel: {
    width: 250, padding: 12, background: "#0d1117",
    borderRight: "1px solid #30363d", color: "#e6edf3",
    display: "flex", flexDirection: "column", gap: 10, overflowY: "auto",
  },
  header: {
    display: "flex", alignItems: "center", justifyContent: "space-between",
    paddingBottom: 8, borderBottom: "1px solid #21262d",
  },
  logo: { display: "flex", alignItems: "center", gap: 8 },
  dot:  { width: 8, height: 8, borderRadius: "50%", flexShrink: 0 },
  statsCard: {
    background: "#161b22", border: "1px solid #30363d", borderRadius: 10, padding: "8px 10px",
  },
  statsTitle: { fontSize: 13, color: "#8b949e", marginBottom: 8, fontWeight: 600, textTransform: "uppercase" as const },
  statsGrid: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 2 },
  statItem: { display: "flex", flexDirection: "column" as const, alignItems: "center" },
  statVal:  { fontSize: 24, fontWeight: 700 },
  statLabel:{ fontSize: 9, color: "#6e7681", textTransform: "uppercase" as const },
  progressTrack: { height: 4, background: "#21262d", borderRadius: 2, overflow: "hidden" },
  progressFill:  { height: "100%", borderRadius: 2, transition: "width 0.5s ease" },
  bigBtn: {
    background: "linear-gradient(135deg, #e1306c, #833ab4)",
    color: "white", border: "none", padding: "12px 10px",
    borderRadius: 8, cursor: "pointer", fontWeight: 700, fontSize: 16,
    boxShadow: "0 4px 12px #e1306c44",
    transition: "transform 0.1s, box-shadow 0.2s",
  },
  divider: { height: 1, background: "#21262d", margin: "2px 0" },
  agentCard: {
    background: "#161b22", border: "1px solid #30363d", borderRadius: 10, padding: 10,
    display: "flex", flexDirection: "column" as const, gap: 6,
    transition: "border-color 0.3s",
  },
  agentHeader: { display: "flex", alignItems: "center", gap: 8 },
  agentMsg: { fontSize: 13, color: "#8b949e", minHeight: 16 },
  agentStat: { fontSize: 13, color: "#e6edf3" },
  logBox: {
    background: "#0d1117", borderRadius: 6, padding: "6px 8px",
    maxHeight: 64, overflow: "hidden",
  },
  logLine: { fontSize: 12, color: "#6e7681", lineHeight: 1.5, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" as const },
  badge: {
    fontSize: 12, padding: "3px 10px", borderRadius: 10,
    fontWeight: 700, textTransform: "uppercase" as const, flexShrink: 0,
  },
  btnRow: { display: "flex", gap: 6, marginTop: 2 },
  btn: {
    flex: 1, color: "#e6edf3", border: "none",
    padding: "9px 6px", borderRadius: 6,
    fontSize: 13, fontWeight: 700,
    transition: "opacity 0.2s",
  },
  helpBox: {
    background: "#161b22", border: "1px solid #30363d", borderRadius: 8, padding: "8px 10px",
    marginTop: "auto",
  },
  kbd: {
    background: "#21262d", border: "1px solid #30363d", borderRadius: 4,
    padding: "2px 6px", fontSize: 12, color: "#e6edf3", fontFamily: "monospace",
  },
};
