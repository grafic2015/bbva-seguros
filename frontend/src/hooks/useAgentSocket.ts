import { useEffect } from "react";
import { useStore } from "../store";
import type { WSEvent } from "../types";

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
    fetch("/api/status")
      .then((r) => r.json())
      .then((d) => {
        if (d.leads) setLeads(d.leads);
      })
      .catch(() => {});

    const proto = location.protocol === "https:" ? "wss" : "ws";
    const url = `${proto}://${location.host}/ws`;
    let ws: WebSocket | null = null;
    let retry = 0;
    let stopped = false;

    const connect = () => {
      ws = new WebSocket(url);
      ws.onopen = () => {
        setConnected(true);
        retry = 0;
        // Refrescar leads al reconectar
        fetch("/api/status")
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

          applyEvent(event);
        } catch {}
      };
      ws.onclose = () => {
        setConnected(false);
        if (stopped) return;
        retry = Math.min(retry + 1, 5);
        setTimeout(connect, 500 * retry);
      };
      ws.onerror = () => ws?.close();
    };

    connect();
    return () => {
      stopped = true;
      ws?.close();
    };
  }, [applyEvent, setConnected, setLeads]);
}

export async function startAgent(agent: string) {
  await fetch(`/api/agents/${agent}/start`, { method: "POST" });
}

export async function stopAgent(agent: string) {
  await fetch(`/api/agents/${agent}/stop`, { method: "POST" });
}
