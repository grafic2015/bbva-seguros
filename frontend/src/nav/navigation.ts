/**
 * Grafo de waypoints — CADA cruce de pared tiene un nodo exactamente
 * en el centro de la puerta. Así el BFS nunca conecta dos nodos
 * de habitaciones diferentes sin pasar por la puerta.
 *
 * Layout de la casa (32×26):
 *   Columnas: Cartero x∈[-16,-5.5] | Detective x∈[-5.5,+5.5] | Buscadora x∈[+5.5,+16]
 *   Filas:    Dorms z∈[-13,-4] | Oficinas z∈[-4,+4] | Común z∈[+4,+13]
 *
 * Puertas:
 *   Pared norte (z=-4):   Cartero dorm/ofc en x=-8 | Det en x=+3 | Bus en x=+13
 *   Pared sur   (z=+4):   Cartero ofc/com en x=-10.75 | Det en x=0 | Bus en x=+10.75
 *   Pared vert  (x=-5.5): entre oficinas en z=+1
 *   Pared vert  (x=+5.5): entre oficinas en z=+1
 */

export type WaypointId = string;

export interface Waypoint {
  id: WaypointId;
  pos: [number, number, number];
  neighbors: WaypointId[];
}

const NODES: Waypoint[] = [

  // ══════════════════════════════════════════════════════════
  // DORMITORIOS (z ∈ [-13, -4])
  // ══════════════════════════════════════════════════════════

  // — Cartero —
  { id: "dc_bed",    pos: [-10.75, 0, -11.5], neighbors: ["dc_mid"] },
  { id: "dc_mid",    pos: [-10.75, 0,  -7.5], neighbors: ["dc_bed", "dc_door"] },
  { id: "dc_door",   pos: [  -8.0, 0,  -4.0], neighbors: ["dc_mid", "oc_door_n"] },  // ← puerta norte Cartero

  // — Detective —
  { id: "dd_bed",    pos: [  0,    0, -11.5], neighbors: ["dd_mid"] },
  { id: "dd_mid",    pos: [  0,    0,  -7.5], neighbors: ["dd_bed", "dd_door"] },
  { id: "dd_door",   pos: [  3.0,  0,  -4.0], neighbors: ["dd_mid", "od_door_n"] },  // ← puerta norte Detective

  // — Buscadora —
  { id: "db_bed",    pos: [ 10.75, 0, -11.5], neighbors: ["db_mid"] },
  { id: "db_mid",    pos: [ 10.75, 0,  -7.5], neighbors: ["db_bed", "db_door"] },
  { id: "db_door",   pos: [ 13.0,  0,  -4.0], neighbors: ["db_mid", "ob_door_n"] },  // ← puerta norte Buscadora

  // ══════════════════════════════════════════════════════════
  // OFICINAS (z ∈ [-4, +4])
  // ══════════════════════════════════════════════════════════

  // — Oficina Cartero —
  { id: "oc_door_n",  pos: [ -8.0,  0, -4.0], neighbors: ["dc_door",   "oc_north"] },  // entrada desde dorm
  { id: "oc_north",   pos: [-10.75, 0, -2.2], neighbors: ["oc_door_n", "oc_desk",  "oc_center"] },  // frente al escritorio (no encima)
  { id: "oc_desk",    pos: [-10.75, 0, -2.0], neighbors: ["oc_north",  "oc_center"] },   // posición frente al desk
  { id: "oc_center",  pos: [-10.75, 0,  0.5], neighbors: ["oc_desk",   "oc_north", "oc_door_e", "oc_south"] },
  { id: "oc_door_e",  pos: [  -5.5, 0,  1.0], neighbors: ["oc_center", "od_door_w"] },  // puerta vertical → Detective
  { id: "oc_south",   pos: [-10.75, 0,  3.0], neighbors: ["oc_center", "oc_door_s"] },
  { id: "oc_door_s",  pos: [-10.75, 0,  4.0], neighbors: ["oc_south",  "com_door"] },   // puerta sur → comedor

  // — Oficina Detective —
  { id: "od_door_n",  pos: [  3.0,  0, -4.0], neighbors: ["dd_door",   "od_north"] },
  { id: "od_north",   pos: [  0,    0, -2.2], neighbors: ["od_door_n", "od_desk",  "od_center"] },  // frente al escritorio
  { id: "od_desk",    pos: [  0,    0, -2.0], neighbors: ["od_north",  "od_center"] },
  { id: "od_center",  pos: [  0,    0,  0.5], neighbors: ["od_desk",   "od_north", "od_door_w", "od_door_e", "od_south"] },
  { id: "od_door_w",  pos: [ -5.5,  0,  1.0], neighbors: ["od_center", "oc_door_e"] }, // puerta → Cartero
  { id: "od_door_e",  pos: [  5.5,  0,  1.0], neighbors: ["od_center", "ob_door_w"] }, // puerta → Buscadora
  { id: "od_south",   pos: [  0,    0,  3.0], neighbors: ["od_center", "od_door_s"] },
  { id: "od_door_s",  pos: [  0,    0,  4.0], neighbors: ["od_south",  "ban_door"] },   // puerta sur → baño

  // — Oficina Buscadora —
  { id: "ob_door_n",  pos: [ 13.0,  0, -4.0], neighbors: ["db_door",   "ob_north"] },
  { id: "ob_north",   pos: [ 10.75, 0, -2.2], neighbors: ["ob_door_n", "ob_desk",  "ob_center"] },  // frente al escritorio
  { id: "ob_desk",    pos: [ 10.75, 0, -2.0], neighbors: ["ob_north",  "ob_center"] },
  { id: "ob_center",  pos: [ 10.75, 0,  0.5], neighbors: ["ob_desk",   "ob_north", "ob_door_w", "ob_south"] },
  { id: "ob_door_w",  pos: [  5.5,  0,  1.0], neighbors: ["ob_center", "od_door_e"] },
  { id: "ob_south",   pos: [ 10.75, 0,  3.0], neighbors: ["ob_center", "ob_door_s"] },
  { id: "ob_door_s",  pos: [ 10.75, 0,  4.0], neighbors: ["ob_south",  "coc_door"] },  // puerta sur → cocina

  // ══════════════════════════════════════════════════════════
  // ZONA SUR: COMEDOR / BAÑO / COCINA (z ∈ [+4, +13])
  // ══════════════════════════════════════════════════════════

  { id: "com_door",   pos: [-10.75, 0,  4.0], neighbors: ["oc_door_s", "com_center"] },
  { id: "com_center", pos: [-10.75, 0,  6.0], neighbors: ["com_door"] },   // antes de la mesa (no encima)

  { id: "ban_door",   pos: [  0,    0,  4.0], neighbors: ["od_door_s", "ban_center"] },
  { id: "ban_center", pos: [  0,    0,  6.0], neighbors: ["ban_door"] },   // zona libre del baño

  { id: "coc_door",   pos: [ 10.75, 0,  4.0], neighbors: ["ob_door_s", "coc_center"] },
  { id: "coc_center", pos: [ 10.75, 0,  6.0], neighbors: ["coc_door"] },   // antes de la isla (no encima)
];

// Mapa id → nodo
export const nodeMap = new Map<WaypointId, Waypoint>(
  NODES.map((n) => [n.id, n])
);

// ── Actividades destino ──────────────────────────────────────────────────────
export const ACTIVITY_TARGETS: Record<string, Record<string, WaypointId>> = {
  busqueda:  { working: "oc_desk",  sleeping: "dc_bed",  idle: "oc_center" },
  extractor: { working: "od_desk",  sleeping: "dd_bed",  idle: "od_center" },
  enviador:  { working: "ob_desk",  sleeping: "db_bed",  idle: "ob_center" },
};

// ── Puntos de paseo aleatorio (solo dentro de la propia área) ────────────────
export const ROAM_WAYPOINTS: Record<string, WaypointId[]> = {
  busqueda:  ["oc_center", "oc_north", "oc_south", "dc_mid", "com_center"],
  extractor: ["od_center", "od_north", "od_south", "dd_mid", "ban_center"],
  enviador:  ["ob_center", "ob_north", "ob_south", "db_mid", "coc_center"],
};

// ── BFS ──────────────────────────────────────────────────────────────────────
export function findPath(
  fromPos: [number, number, number],
  toId: WaypointId,
): [number, number, number][] {
  // Nodo más cercano al punto actual
  let startId = NODES[0].id;
  let best = Infinity;
  for (const n of NODES) {
    const dx = n.pos[0] - fromPos[0];
    const dz = n.pos[2] - fromPos[2];
    const d = dx * dx + dz * dz;
    if (d < best) { best = d; startId = n.id; }
  }
  if (startId === toId) return [nodeMap.get(toId)!.pos];

  // BFS
  const prev = new Map<WaypointId, WaypointId | null>([[startId, null]]);
  const queue: WaypointId[] = [startId];

  outer: while (queue.length) {
    const cur = queue.shift()!;
    for (const nb of nodeMap.get(cur)!.neighbors) {
      if (!prev.has(nb)) {
        prev.set(nb, cur);
        if (nb === toId) break outer;
        queue.push(nb);
      }
    }
  }

  if (!prev.has(toId)) return [nodeMap.get(toId)!.pos];

  // Reconstruir camino
  const path: WaypointId[] = [];
  let c: WaypointId | null = toId;
  while (c !== null) {
    path.unshift(c);
    c = prev.get(c) ?? null;
  }
  // Saltar el primer nodo si es el mismo punto de partida
  if (path.length > 1) path.shift();
  return path.map((id) => nodeMap.get(id)!.pos);
}
