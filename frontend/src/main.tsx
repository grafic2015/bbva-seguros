import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import AppSeguros from "./AppSeguros";
import { getToken, setToken, clearToken, installAuthFetch } from "./auth";

// Inyectar el token en todos los pedidos al API y manejar 401.
installAuthFetch();

const API = import.meta.env.VITE_API_URL || "";

type View = "panel3d" | "seguros";

function Login({ onOk }: { onOk: () => void }) {
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErr("");
    try {
      const r = await fetch(`${API}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: pw }),
      });
      if (r.ok) {
        const d = await r.json();
        setToken(d.token || "");
        onOk();
      } else {
        setErr("Contraseña incorrecta");
      }
    } catch {
      setErr("No se pudo conectar con el servidor");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={loginWrap}>
      <form onSubmit={submit} style={loginCard}>
        <h1 style={{ margin: 0, fontSize: 22, color: "#e6edf3" }}>🔐 BBVA Seguros</h1>
        <p style={{ margin: "4px 0 16px", color: "#8b949e", fontSize: 13 }}>
          Ingresá la contraseña para acceder al panel
        </p>
        <input
          type="password"
          value={pw}
          onChange={(e) => setPw(e.target.value)}
          placeholder="Contraseña"
          autoFocus
          style={loginInput}
        />
        {err && <div style={{ color: "#f85149", fontSize: 13, marginTop: 8 }}>{err}</div>}
        <button type="submit" disabled={loading} style={loginBtn}>
          {loading ? "Ingresando..." : "Ingresar"}
        </button>
      </form>
    </div>
  );
}

function Root() {
  const [authed, setAuthed] = useState<boolean>(!!getToken());
  const [view, setView] = useState<View>("panel3d");

  if (!authed) return <Login onOk={() => setAuthed(true)} />;

  return (
    <>
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
        <button
          onClick={() => { clearToken(); location.reload(); }}
          style={{ ...tab, color: "#f85149" }}
          title="Cerrar sesión"
        >
          ⎋
        </button>
      </div>

      {view === "panel3d" ? <App /> : <AppSeguros />}
    </>
  );
}

const loginWrap: React.CSSProperties = {
  position: "fixed", inset: 0, display: "flex", alignItems: "center",
  justifyContent: "center", background: "#0d1117",
};
const loginCard: React.CSSProperties = {
  display: "flex", flexDirection: "column", width: 320, padding: 28,
  background: "#161b22", border: "1px solid #30363d", borderRadius: 12,
};
const loginInput: React.CSSProperties = {
  padding: "10px 12px", borderRadius: 8, border: "1px solid #30363d",
  background: "#0d1117", color: "#e6edf3", fontSize: 14, outline: "none",
};
const loginBtn: React.CSSProperties = {
  marginTop: 14, padding: "10px", borderRadius: 8, border: "none",
  background: "#1f6feb", color: "#fff", fontSize: 14, fontWeight: 700, cursor: "pointer",
};

const switcher: React.CSSProperties = {
  position: "fixed", top: 12, left: "50%", transform: "translateX(-50%)",
  zIndex: 3000, display: "flex", gap: 6, padding: 4,
  background: "#161b22cc", border: "1px solid #30363d", borderRadius: 10,
  backdropFilter: "blur(8px)",
};
const tab: React.CSSProperties = {
  padding: "6px 14px", borderRadius: 7, border: "none", background: "transparent",
  color: "#8b949e", fontSize: 13, fontWeight: 700, cursor: "pointer",
};
const tabActive: React.CSSProperties = { background: "#1f6feb", color: "#fff" };

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
