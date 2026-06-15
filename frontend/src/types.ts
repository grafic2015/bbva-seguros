export type AgentId = "instagram" | "leads";

export type AgentStatus = "idle" | "running" | "done" | "error";

export type ActivityType = "idle" | "walking" | "working" | "sleeping";

export interface AgentState {
  status: AgentStatus;
  mensaje: string;
  leads_encontrados?: number;
  total_leads?: number;
  logs: string[];
}

export interface AgentPosition {
  current: [number, number, number];
  target: [number, number, number];
  activity: ActivityType;
}

export type AgentsState = Record<AgentId, AgentState>;

/** Un lead de seguros automotrices gestionado por los agentes. */
export interface Lead {
  id?: number;
  usuario: string;
  nombre?: string;
  comentario?: string;
  post_id?: string;
  dm_enviado?: boolean;
  estado: "nuevo" | "interesado" | "en_seguimiento" | "convertido" | "rechazado";
  fecha_contacto?: string;
  actualizado?: string;
  respuesta?: string;
  telefono?: string;
  email?: string;
}

export type WSEvent =
  | { type: "snapshot"; agents: AgentsState }
  | { type: "agent_state"; agent: AgentId; state: AgentState }
  | { type: "agent_log"; agent: AgentId; line: string }
  | { type: "results"; leads: Lead[] }
  | { type: "ping" };

export const AGENT_META: Record<AgentId, { name: string; color: string; emoji: string; description: string }> = {
  instagram: { name: "Instagram Monitor", color: "#e1306c", emoji: "📸", description: "Monitorea comentarios y envía DMs automáticos" },
  leads:     { name: "Leads Manager",     color: "#00b4d8", emoji: "📋", description: "Gestiona y hace seguimiento de los contactos" },
};
