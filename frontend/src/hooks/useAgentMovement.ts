/**
 * Hook que mueve un agente a lo largo de una ruta de waypoints.
 * Se llama cada frame desde AgentAvatar vía useFrame.
 */

import { useRef, useCallback } from "react";
import * as THREE from "three";
import type { AgentId, ActivityType } from "../types";
import { useStore } from "../store";
import { findPath, ACTIVITY_TARGETS, ROAM_WAYPOINTS } from "../nav/navigation";

const WALK_SPEED = 3.5;  // unidades por segundo
const ARRIVE_DIST = 0.15;

// Límites de habitaciones (x, z) — puertas en el centro
const ROOM_BOUNDS: Record<AgentId, { xMin: number; xMax: number; zMin: number; zMax: number }> = {
  instagram: { xMin: -15.5, xMax: -5.5, zMin: -13, zMax: 13 },   // Instagram Monitor
  leads:     { xMin: -5.5,  xMax: 5.5,  zMin: -13, zMax: 13 },   // Leads Manager
};

// Muebles que el avatar NO debe pisar (AABB en coords del mundo).
// Las camas y el frente de los escritorios se dejan libres (son destinos de dormir/trabajar).
const OBSTACLES: { xMin: number; xMax: number; zMin: number; zMax: number }[] = [
  // Escritorios (z[-3.9,-2.9]); el avatar trabaja parado al frente en z≈-2.0
  { xMin: -11.95, xMax: -9.55, zMin: -3.9, zMax: -2.9 },  // Cartero
  { xMin: -1.2,   xMax:  1.2,  zMin: -3.9, zMax: -2.9 },  // Detective
  { xMin:  9.55,  xMax: 11.95, zMin: -3.9, zMax: -2.9 },  // Buscador
  // Mesa del comedor (Cartero)
  { xMin: -12.25, xMax: -9.25, zMin: 7.8, zMax: 9.2 },
  // Isla de la cocina (Buscador)
  { xMin:  9.4,   xMax: 12.1,  zMin: 7.3, zMax: 8.7 },
];

const AVATAR_RADIUS = 0.35;

// Verifica límites de la habitación
function inRoom(agentId: AgentId, x: number, z: number): boolean {
  const b = ROOM_BOUNDS[agentId];
  if (!b) return true;
  return x >= b.xMin && x <= b.xMax && z >= b.zMin && z <= b.zMax;
}

// Verifica si la posición cae dentro de algún mueble (expandido por el radio del avatar)
function inObstacle(x: number, z: number): boolean {
  const r = AVATAR_RADIUS;
  for (const o of OBSTACLES) {
    if (x > o.xMin - r && x < o.xMax + r && z > o.zMin - r && z < o.zMax + r) return true;
  }
  return false;
}

// Una posición es válida si está en la habitación y libre de muebles
function canStand(agentId: AgentId, x: number, z: number): boolean {
  return inRoom(agentId, x, z) && !inObstacle(x, z);
}

export function useAgentMovement(agentId: AgentId) {
  const setAgentPosition = useStore((s) => s.setAgentPosition);
  const setAgentActivity  = useStore((s) => s.setAgentActivity);

  // ruta actual: lista de posiciones a seguir en orden
  const pathRef     = useRef<[number, number, number][]>([]);
  const activityRef = useRef<ActivityType>("idle");
  const posRef      = useRef<THREE.Vector3>(new THREE.Vector3(
    ...useStore.getState().positions[agentId].current
  ));

  /** Solicita ir a una actividad destino */
  const goTo = useCallback((activity: ActivityType) => {
    activityRef.current = activity;
    const targetId = ACTIVITY_TARGETS[agentId]?.[activity] ?? ACTIVITY_TARGETS[agentId]?.idle;
    const cur = posRef.current;
    pathRef.current = findPath([cur.x, cur.y, cur.z], targetId);
    setAgentActivity(agentId, "walking");
  }, [agentId, setAgentActivity]);

  /** Empieza a pasear aleatoriamente */
  const roam = useCallback(() => {
    activityRef.current = "idle";
    const options = ROAM_WAYPOINTS[agentId] ?? [];
    const pick = options[Math.floor(Math.random() * options.length)];
    const cur = posRef.current;
    pathRef.current = findPath([cur.x, cur.y, cur.z], pick);
    setAgentActivity(agentId, "walking");
  }, [agentId, setAgentActivity]);

  /** Detiene al avatar en el lugar (limpia la ruta) */
  const halt = useCallback(() => {
    activityRef.current = "idle";
    pathRef.current = [];
    setAgentActivity(agentId, "idle");
  }, [agentId, setAgentActivity]);

  /** Llamar en useFrame — devuelve si el avatar está en movimiento */
  const tick = useCallback((dt: number): boolean => {
    if (pathRef.current.length === 0) return false;

    const target = new THREE.Vector3(...pathRef.current[0]);
    const diff = target.clone().sub(posRef.current);
    diff.y = 0;
    const dist = diff.length();

    if (dist < ARRIVE_DIST) {
      posRef.current.copy(target);
      pathRef.current.shift();

      if (pathRef.current.length === 0) {
        // Llegó al destino
        setAgentActivity(agentId, activityRef.current === "idle" ? "idle" : activityRef.current);
        setAgentPosition(agentId, [posRef.current.x, posRef.current.y, posRef.current.z]);
        return false;
      }
      return true;
    }

    diff.normalize().multiplyScalar(WALK_SPEED * dt);
    const nx = posRef.current.x + diff.x;
    const nz = posRef.current.z + diff.z;
    const ox = posRef.current.x;
    const oz = posRef.current.z;

    // Colisión con sliding: intenta el movimiento completo; si choca con un
    // mueble o pared, desliza por el eje que sí esté libre.
    if (canStand(agentId, nx, nz)) {
      posRef.current.x = nx;
      posRef.current.z = nz;
    } else if (canStand(agentId, nx, oz)) {
      posRef.current.x = nx;          // desliza en X
    } else if (canStand(agentId, ox, nz)) {
      posRef.current.z = nz;          // desliza en Z
    }
    // si nada es válido, se queda (no atraviesa el mueble)

    setAgentPosition(agentId, [posRef.current.x, posRef.current.y, posRef.current.z]);
    return true;
  }, [agentId, setAgentPosition, setAgentActivity]);

  return { goTo, roam, halt, tick, posRef };
}
