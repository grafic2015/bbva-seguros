import { useEffect, useState } from "react";
import type { Lead } from "../types";

const API = import.meta.env.VITE_API_URL || "";

const ESTADO_META: Record<string, { label: string; color: string; bg: string; emoji: string }> = {
  nuevo:          { label: "Nuevo",          color: "#d29922", bg: "#d2992222", emoji: "🆕" },
  interesado:     { label: "Interesado",     color: "#e1306c", bg: "#e1306c22", emoji: "👍" },
  en_seguimiento: { label: "En seguimiento", color: "#58a6ff", bg: "#58a6ff22", emoji: "🔄" },
  convertido:     { label: "Aprobado",       color: "#3fb950", bg: "#3fb95022", emoji: "✅" },
  rechazado:      { label: "Rechazado",      color: "#f85149", bg: "#f8514922", emoji: "❌" },
};

/** Tabla de leads como página completa (misma vista del modal ResultsPanel). */
export function LeadsView() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("todos");

  const cargar = () => {
    fetch(`${API}/api/status`)
      .then((r) => r.json())
      .then((d) => setLeads(d.leads || []))
      .catch(() => {});
  };

  useEffect(() => {
    cargar();
    const t = setInterval(cargar, 15000); // refresco automático cada 15s
    return () => clearInterval(t);
  }, []);

  const query = search.toLowerCase();
  const filtered = leads.filter((l) => {
    const matchStatus = filterStatus === "todos" || l.estado === filterStatus;
    const matchSearch = !query ||
      (l.usuario || "").toLowerCase().includes(query) ||
      (l.nombre  || "").toLowerCase().includes(query) ||
      (l.comentario || "").toLowerCase().includes(query);
    return matchStatus && matchSearch;
  });

  const stats = {
    total:          leads.length,
    nuevos:         leads.filter((l) => l.estado === "nuevo").length,
    interesados:    leads.filter((l) => l.estado === "interesado").length,
    en_seguimiento: leads.filter((l) => l.estado === "en_seguimiento").length,
    convertidos:    leads.filter((l) => l.estado === "convertido").length,
    rechazados:     leads.filter((l) => l.estado === "rechazado").length,
  };

  const handleUpdateStatus = async (usuario: string, nuevoEstado: string) => {
    setLeads((prev) => prev.map((l) =>
      l.usuario === usuario ? { ...l, estado: nuevoEstado as Lead["estado"] } : l
    ));
    try {
      await fetch(`${API}/api/leads/${encodeURIComponent(usuario)}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ estado: nuevoEstado }),
      });
    } catch {}
  };

  const handleDelete = async (lead: Lead) => {
    if (!lead.id) return;
    if (!confirm(`¿Eliminar el lead @${lead.usuario}? Esta acción no se puede deshacer.`)) return;
    setLeads((prev) => prev.filter((l) => l.id !== lead.id));
    try {
      await fetch(`${API}/api/leads/${lead.id}`, { method: "DELETE" });
    } catch {}
  };

  const exportCSV = () => {
    if (!leads.length) return;
    const headers = ["Usuario", "Nombre", "Estado", "Comentario", "DM Enviado", "Fecha Contacto", "Teléfono", "Email"];
    const rows = leads.map((l) => [
      l.usuario, l.nombre || "", l.estado, l.comentario || "",
      l.dm_enviado ? "Sí" : "No", l.fecha_contacto || "", l.telefono || "", l.email || "",
    ].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(","));
    const csv  = [headers.join(","), ...rows].join("\n");
    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url; a.download = "leads_seguros_bbva.csv"; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        {/* Header */}
        <div style={styles.header}>
          <div>
            <h2 style={styles.title}>📋 Leads · Seguros BBVA</h2>
            <div style={styles.subtitle}>
              {leads.length} contactos totales · {filtered.length} mostrados
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="text"
              placeholder="Buscar usuario, nombre..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={styles.searchInput}
            />
            <button style={styles.exportBtn} onClick={exportCSV}>⬇ CSV</button>
          </div>
        </div>

        {/* Stats bar */}
        <div style={styles.statsBar}>
          {Object.entries(ESTADO_META).map(([key, meta]) => (
            <button
              key={key}
              style={{
                ...styles.statChip,
                background: filterStatus === key ? meta.bg : "#161b22",
                border: `1px solid ${filterStatus === key ? meta.color : "#30363d"}`,
                color: filterStatus === key ? meta.color : "#8b949e",
              }}
              onClick={() => setFilterStatus(filterStatus === key ? "todos" : key)}
            >
              {meta.emoji} {meta.label}
              <span style={{ ...styles.chipCount, background: meta.bg, color: meta.color }}>
                {stats[key as keyof typeof stats] ?? 0}
              </span>
            </button>
          ))}
          <button
            style={{
              ...styles.statChip,
              background: filterStatus === "todos" ? "#1f6feb22" : "#161b22",
              border: `1px solid ${filterStatus === "todos" ? "#58a6ff" : "#30363d"}`,
              color: filterStatus === "todos" ? "#58a6ff" : "#8b949e",
              marginLeft: "auto",
            }}
            onClick={() => setFilterStatus("todos")}
          >
            Todos
            <span style={{ ...styles.chipCount, background: "#58a6ff22", color: "#58a6ff" }}>
              {stats.total}
            </span>
          </button>
        </div>

        {/* Tabla */}
        <div style={styles.tableWrap}>
          {filtered.length === 0 ? (
            <div style={styles.empty}>
              {leads.length === 0
                ? "🔍 Aún no hay leads. El bot los va a cargar cuando capture comentarios o DMs."
                : "No hay leads que coincidan con los filtros."}
            </div>
          ) : (
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Usuario</th>
                  <th style={styles.th}>Nombre</th>
                  <th style={styles.th}>Estado</th>
                  <th style={styles.th}>Comentario</th>
                  <th style={styles.th}>DM</th>
                  <th style={styles.th}>Fecha</th>
                  <th style={styles.th}>Contacto</th>
                  <th style={styles.th}>Gestionar</th>
                  <th style={styles.th}>Eliminar</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((lead, i) => {
                  const m = ESTADO_META[lead.estado] ?? ESTADO_META.nuevo;
                  return (
                    <tr key={(lead.usuario || "") + i} style={{ background: i % 2 ? "#0d1117" : "transparent" }}>
                      <td style={styles.td}>
                        <a href={`https://instagram.com/${lead.usuario}`} target="_blank" rel="noreferrer" style={styles.igLink}>
                          @{lead.usuario}
                        </a>
                      </td>
                      <td style={{ ...styles.td, color: "#8b949e" }}>{lead.nombre || "—"}</td>
                      <td style={styles.td}>
                        <span style={{ ...styles.badge, background: m.bg, color: m.color }}>
                          {m.emoji} {m.label}
                        </span>
                      </td>
                      <td style={{ ...styles.td, maxWidth: 220, color: "#8b949e" }}>
                        <span title={lead.comentario} style={{ display: "block", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {lead.comentario || "—"}
                        </span>
                      </td>
                      <td style={{ ...styles.td, textAlign: "center" }}>
                        {lead.dm_enviado
                          ? <span style={{ color: "#3fb950", fontWeight: 700 }}>✓</span>
                          : <span style={{ color: "#6e7681" }}>—</span>}
                      </td>
                      <td style={{ ...styles.td, color: "#8b949e", whiteSpace: "nowrap" }}>
                        {lead.fecha_contacto
                          ? new Date(lead.fecha_contacto).toLocaleDateString("es-AR")
                          : "—"}
                      </td>
                      <td style={styles.td}>
                        {(lead.telefono || lead.email) ? (
                          <div style={{ display: "flex", gap: 4 }}>
                            {lead.telefono && <a href={`tel:${lead.telefono}`} style={styles.contactLink}>📞</a>}
                            {lead.email && <a href={`mailto:${lead.email}`} style={styles.contactLink}>✉️</a>}
                          </div>
                        ) : <span style={{ color: "#6e7681" }}>—</span>}
                      </td>
                      <td style={styles.td}>
                        <select
                          value={lead.estado}
                          onChange={(e) => handleUpdateStatus(lead.usuario, e.target.value)}
                          style={{ ...styles.select, color: m.color }}
                        >
                          {Object.entries(ESTADO_META).map(([k, v]) => (
                            <option key={k} value={k}>{v.emoji} {v.label}</option>
                          ))}
                        </select>
                      </td>
                      <td style={{ ...styles.td, textAlign: "center" }}>
                        <button
                          onClick={() => handleDelete(lead)}
                          style={styles.deleteBtn}
                          title="Eliminar lead"
                        >
                          🗑
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: { minHeight: "100vh", background: "#0d1117", padding: 24, display: "flex", justifyContent: "center" },
  card: {
    width: "min(1700px, 100%)", maxHeight: "calc(100vh - 48px)", display: "flex", flexDirection: "column",
    background: "#161b22", border: "1px solid #30363d", borderRadius: 16,
    boxShadow: "0 24px 80px #000c", overflow: "hidden", color: "#e6edf3",
  },
  header: {
    display: "flex", alignItems: "center", justifyContent: "space-between",
    padding: "22px 28px", borderBottom: "1px solid #30363d",
    background: "linear-gradient(135deg, #161b22, #0d1117)",
  },
  title: { margin: 0, fontSize: 30, fontWeight: 700 },
  subtitle: { fontSize: 17, color: "#8b949e", marginTop: 5 },
  searchInput: {
    padding: "12px 18px", borderRadius: 10, border: "1px solid #30363d",
    background: "#0d1117", color: "#e6edf3", fontSize: 17, width: 300, outline: "none",
  },
  exportBtn: {
    background: "#1a472a", color: "#3fb950", border: "1px solid #3fb95044",
    padding: "12px 20px", borderRadius: 10, cursor: "pointer", fontWeight: 700, fontSize: 16,
  },
  statsBar: {
    display: "flex", gap: 10, flexWrap: "wrap",
    padding: "14px 24px", borderBottom: "1px solid #30363d", background: "#0d1117",
  },
  statChip: {
    display: "flex", alignItems: "center", gap: 8,
    padding: "9px 18px", borderRadius: 22, cursor: "pointer", fontSize: 16, fontWeight: 600,
  },
  chipCount: { fontSize: 15, fontWeight: 700, padding: "2px 10px", borderRadius: 12 },
  tableWrap: { overflow: "auto", flex: 1 },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 17 },
  th: {
    position: "sticky", top: 0, background: "#0d1117", textAlign: "left",
    padding: "16px 20px", color: "#8b949e", fontWeight: 600, fontSize: 14,
    textTransform: "uppercase", borderBottom: "1px solid #30363d", whiteSpace: "nowrap",
  },
  td: { padding: "16px 20px", borderBottom: "1px solid #21262d", verticalAlign: "middle", fontSize: 17 },
  badge: { fontSize: 15, padding: "5px 14px", borderRadius: 14, fontWeight: 700, whiteSpace: "nowrap" },
  igLink: { color: "#e1306c", textDecoration: "none", fontWeight: 700 },
  contactLink: { textDecoration: "none", fontSize: 22 },
  select: {
    background: "#21262d", border: "1px solid #30363d",
    borderRadius: 8, padding: "8px 10px", fontSize: 15, cursor: "pointer", fontWeight: 600,
  },
  deleteBtn: {
    background: "#3a1f1f", border: "1px solid #f8514944", color: "#f85149",
    borderRadius: 8, padding: "8px 14px", fontSize: 18, cursor: "pointer",
  },
  empty: { padding: 80, textAlign: "center", color: "#8b949e", fontSize: 18 },
};
