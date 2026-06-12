import { create } from "zustand";
import type { AgentId, AgentState, AgentsState, WSEvent, AgentPosition, ActivityType, Lead } from "./types";

interface Store {
  agents: AgentsState;
  positions: Record<AgentId, AgentPosition>;
  connected: boolean;
  selected: AgentId;
  leads: Lead[];
  showResults: boolean;
  roaming: Record<AgentId, boolean>;
  setRoaming: (agent: AgentId, v: boolean) => void;
  setShowResults: (v: boolean) => void;
  setLeads: (leads: Lead[]) => void;
  setSelected: (a: AgentId) => void;
  applyEvent: (e: WSEvent) => void;
  setConnected: (c: boolean) => void;
  setAgentPosition: (agent: AgentId, pos: [number, number, number]) => void;
  setAgentTarget: (agent: AgentId, target: [number, number, number]) => void;
  setAgentActivity: (agent: AgentId, activity: ActivityType) => void;
}

const empty: AgentState = { status: "idle", mensaje: "", logs: [] };

const INITIAL_POSITIONS: Record<AgentId, [number, number, number]> = {
  instagram: [-50, 0, 0],
  leads:     [ 50, 0, 0],
};

export const useStore = create<Store>((set) => ({
  agents: {
    instagram: { ...empty, mensaje: "Esperando iniciar monitoreo..." },
    leads:     { ...empty, mensaje: "Esperando procesar dashboard..." },
  },
  positions: {
    instagram: { current: INITIAL_POSITIONS.instagram, target: INITIAL_POSITIONS.instagram, activity: "idle" },
    leads:     { current: INITIAL_POSITIONS.leads,     target: INITIAL_POSITIONS.leads,     activity: "idle" },
  },
  connected: false,
  selected: "instagram",
  leads: [],
  showResults: false,
  roaming: { instagram: false, leads: false },
  setRoaming: (agent, v) => set((s) => ({
    roaming: { ...s.roaming, [agent]: v },
  })),
  setShowResults: (v) => set({ showResults: v }),
  setLeads: (leads) => set({ leads }),
  setSelected: (a) => set({ selected: a }),
  setConnected: (c) => set({ connected: c }),
  setAgentPosition: (agent, pos) => set((s) => ({
    positions: { ...s.positions, [agent]: { ...s.positions[agent], current: pos } }
  })),
  setAgentTarget: (agent, target) => set((s) => ({
    positions: { ...s.positions, [agent]: { ...s.positions[agent], target, activity: "walking" } }
  })),
  setAgentActivity: (agent, activity) => set((s) => ({
    positions: { ...s.positions, [agent]: { ...s.positions[agent], activity } }
  })),
  applyEvent: (e) =>
    set((s) => {
      if (e.type === "snapshot") {
        // Merge cautiously — only update known agents
        const merged: AgentsState = { ...s.agents };
        (["instagram", "leads"] as AgentId[]).forEach((id) => {
          if (e.agents[id]) merged[id] = { ...s.agents[id], ...e.agents[id] };
        });
        return { agents: merged };
      }
      if (e.type === "agent_state") {
        return {
          agents: { ...s.agents, [e.agent]: { ...s.agents[e.agent], ...e.state } },
        };
      }
      if (e.type === "agent_log") {
        const cur = s.agents[e.agent];
        if (!cur) return s;
        return {
          agents: {
            ...s.agents,
            [e.agent]: { ...cur, logs: [...(cur.logs || []), e.line].slice(-200) },
          },
        };
      }
      if (e.type === "results") {
        return { leads: e.leads ?? [] };
      }
      return s;
    }),
}));
