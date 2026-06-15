import { useEffect } from "react";
import { useStore } from "../store";
import type { WSEvent } from "../types";
import { getToken } from "../auth";

// Request notification permission
if ("Notification" in window && Notification.permission === "default") {
  Notification.requestPermission();
}

export function useAgentSocket() {
  const applyEvent  = useStore((s) => s.applyEvent);
  const setConnected = useStore((s) => s.setConnected);
  const setLeads     = useStore((s) => s.setLeads);

  useEffect(() => {
    // Traer datos iniciales al cargar la página
    const apiUrl = import.meta.env.VITE_API_URL || "";
    fetch(`${apiUrl}/api/status`)
      .then((r) => r.json())
      .then((d) => {
        if (d.leads) setLeads(d.leads);
      })
      .catch(() => {});

    const proto = location.protocol === "https:" ? "wss" : "ws";
    let defaultWsUrl = `${proto}://${location.host}/ws`;
    const apiUrlForWs = import.meta.env.VITE_API_URL;
    if (apiUrlForWs) {
      defaultWsUrl = apiUrlForWs.replace(/^http/, 'ws') + '/ws';
    }
    let url = import.meta.env.VITE_WS_URL || defaultWsUrl;
    // Adjuntar el token de auth (el WS no puede usar headers)
    const token = getToken();
    if (token) url += (url.includes("?") ? "&" : "?") + "token=" + encodeURIComponent(token);
    let ws: WebSocket | null = null;
    let retry = 0;
    let stopped = false;

    const connect = () => {
      ws = new WebSocket(url);
      ws.onopen = () => {
        setConnected(true);
        retry = 0;
        // Refrescar leads al reconectar
        const apiUrl = import.meta.env.VITE_API_URL || "";
        fetch(`${apiUrl}/api/status`)
          .then((r) => r.json())
          .then((d) => { if (d.leads) setLeads(d.leads); })
          .catch(() => {});
      };
      ws.onmessage = (ev) => {
        try {
          const event = JSON.parse(ev.data) as WSEvent;

          // Notificaciones del browser
          if (event.type === "agent_state" && event.state.status === "done" && Notification.permission === "granted") {
            const agentName = event.agent === "instagram" ? "📸 Instagram Monitor" : "📋 Leads Manager";
            new Notification(`${agentName} terminó su tarea`, { body: event.state.mensaje });
          }
          if (event.type === "results" && event.leads && Notification.permission === "granted") {
            const prevCount = useStore.getState().leads.length;
            if (event.leads.length > prevCount) {
              const nuevos = event.leads.length - prevCount;
              new Notification(`🎉 ¡${nuevos} nuevo${nuevos > 1 ? "s" : ""} lead${nuevos > 1 ? "s" : ""} detectado${nuevos > 1 ? "s" : ""}!`, {
                body: `Total de contactos: ${event.leads.length}`,
              });
            }
          }

          // Ignorar pings del servidor
          if (event.type === "ping") return;
          applyEvent(event);
        } catch {}
      };
      ws.onclose = () => {
        setConnected(false);
        if (stopped) return;
        // Backoff progresivo: 1s, 2s, 4s, 8s, max 16s
        const delay = Math.min(1000 * Math.pow(2, retry), 16000);
        retry = Math.min(retry + 1, 5);
        setTimeout(connect, delay);
      };
      // No hacer nada en onerror para evitar spam en consola
      ws.onerror = () => { ws?.close(); };
    };

    connect();
    return () => {
      stopped = true;
      ws?.close();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}

export async function startAgent(agent: string) {
  const apiUrl = import.meta.env.VITE_API_URL || "";
  await fetch(`${apiUrl}/api/agents/${agent}/start`, { method: "POST" });
}

export async function stopAgent(agent: string) {
  const apiUrl = import.meta.env.VITE_API_URL || "";
  await fetch(`${apiUrl}/api/agents/${agent}/stop`, { method: "POST" });
}
