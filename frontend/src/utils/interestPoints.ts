// Puntos de interés en la casa
// Casa real: x ∈ [-16, +16], z ∈ [-13, +13]  (W=32, D=26)
// Paredes tomadas de House.tsx — cajas de colisión con espesor generoso (0.6)

export interface InterestPoint {
  name: string;
  position: [number, number, number];
  type: "bed" | "chair" | "random" | "waypoint";
}

export interface Wall {
  name: string;
  x1: number;
  x2: number;
  z1: number;
  z2: number;
  thickness: number;
}

// ─── Muros de colisión ────────────────────────────────────────────────────
// Cada pared tiene 0.6 unidades de espesor (±0.3 del centro visual)
// para que no haya huecos donde el avatar pueda escaparse.

const H = 0.3; // semiespesor de pared

export const WALLS: Wall[] = [

  // ── Paredes externas ──────────────────────────────────────────────────
  // Norte z=-13
  { name: "ext_north",    x1: -16.3, x2:  16.3, z1: -13-H, z2: -13+H, thickness: 0.6 },
  // Sur   z=+13  (gap de puerta en x ∈ [-11.65, -9.95])
  { name: "ext_south_w",  x1: -16.3, x2: -11.65, z1: 13-H, z2:  13+H, thickness: 0.6 },
  { name: "ext_south_e",  x1:  -9.95, x2: 16.3,  z1: 13-H, z2:  13+H, thickness: 0.6 },
  // Este  x=+16
  { name: "ext_east",     x1:  16-H, x2:  16+H, z1: -13.3, z2:  13.3, thickness: 0.6 },
  // Oeste x=-16
  { name: "ext_west",     x1: -16-H, x2: -16+H, z1: -13.3, z2:  13.3, thickness: 0.6 },

  // ── División vertical OESTE x=-5.5 ───────────────────────────────────
  // Tramo norte: z=-13 a z=-4  (sin puerta)
  { name: "dw_north",  x1: -5.5-H, x2: -5.5+H, z1: -13.0, z2:  -4.0, thickness: 0.6 },
  // Tramo oficina: puerta en z ∈ [0.2, 1.8]
  { name: "dw_mid_n",  x1: -5.5-H, x2: -5.5+H, z1:  -4.0, z2:   0.2, thickness: 0.6 },
  { name: "dw_mid_s",  x1: -5.5-H, x2: -5.5+H, z1:   1.8, z2:   4.0, thickness: 0.6 },
  // Tramo sur: puerta en z ∈ [7.7, 9.3]
  { name: "dw_sou_n",  x1: -5.5-H, x2: -5.5+H, z1:   4.0, z2:   7.7, thickness: 0.6 },
  { name: "dw_sou_s",  x1: -5.5-H, x2: -5.5+H, z1:   9.3, z2:  13.0, thickness: 0.6 },

  // ── División vertical ESTE x=+5.5 ────────────────────────────────────
  { name: "de_north",  x1:  5.5-H, x2:  5.5+H, z1: -13.0, z2:  -4.0, thickness: 0.6 },
  { name: "de_mid_n",  x1:  5.5-H, x2:  5.5+H, z1:  -4.0, z2:   0.2, thickness: 0.6 },
  { name: "de_mid_s",  x1:  5.5-H, x2:  5.5+H, z1:   1.8, z2:   4.0, thickness: 0.6 },
  { name: "de_sou_n",  x1:  5.5-H, x2:  5.5+H, z1:   4.0, z2:   7.7, thickness: 0.6 },
  { name: "de_sou_s",  x1:  5.5-H, x2:  5.5+H, z1:   9.3, z2:  13.0, thickness: 0.6 },

  // ── Pared NORTE z=-4 (separa dorms de oficinas) ───────────────────────
  // Puerta Cartero    x ∈ [-8.8, -7.2]
  { name: "nw_1", x1: -16.0,  x2:  -8.8, z1: -4-H, z2: -4+H, thickness: 0.6 },
  { name: "nw_2", x1:  -7.2,  x2:  -5.5, z1: -4-H, z2: -4+H, thickness: 0.6 },
  // Puerta Detective  x ∈ [+2.2, +3.8]
  { name: "nc_1", x1:  -5.5,  x2:   2.2, z1: -4-H, z2: -4+H, thickness: 0.6 },
  { name: "nc_2", x1:   3.8,  x2:   5.5, z1: -4-H, z2: -4+H, thickness: 0.6 },
  // Puerta Buscadora  x ∈ [+12.2, +13.8]
  { name: "ne_1", x1:   5.5,  x2:  12.2, z1: -4-H, z2: -4+H, thickness: 0.6 },
  { name: "ne_2", x1:  13.8,  x2:  16.0, z1: -4-H, z2: -4+H, thickness: 0.6 },

  // ── Pared SUR z=+4 (separa oficinas de comedor/baño/cocina) ──────────
  // Puerta Cartero/Comedor   x ∈ [-11.55, -9.95]
  { name: "sw_1", x1: -16.0,  x2: -11.55, z1: 4-H, z2: 4+H, thickness: 0.6 },
  { name: "sw_2", x1:  -9.95, x2:  -5.5,  z1: 4-H, z2: 4+H, thickness: 0.6 },
  // Puerta Detective/Baño    x ∈ [-0.8, +0.8]
  { name: "sc_1", x1:  -5.5,  x2:  -0.8,  z1: 4-H, z2: 4+H, thickness: 0.6 },
  { name: "sc_2", x1:   0.8,  x2:   5.5,  z1: 4-H, z2: 4+H, thickness: 0.6 },
  // Puerta Buscadora/Cocina  x ∈ [+9.95, +11.55]
  { name: "se_1", x1:   5.5,  x2:   9.95, z1: 4-H, z2: 4+H, thickness: 0.6 },
  { name: "se_2", x1:  11.55, x2:  16.0,  z1: 4-H, z2: 4+H, thickness: 0.6 },
];

// ─── Puertas (punto central de cada abertura) ─────────────────────────────
export const DOORS: Array<[number, number, number]> = [
  // División OESTE x=-5.5
  [-5.5, 0,  1.0],   // puerta oficinas (z=1)
  [-5.5, 0,  8.5],   // puerta sur (z=8.5)
  // División ESTE x=+5.5
  [ 5.5, 0,  1.0],
  [ 5.5, 0,  8.5],
  // Pared NORTE z=-4
  [ -8.0, 0, -4.0],  // dorm Cartero
  [  3.0, 0, -4.0],  // dorm Detective
  [ 13.0, 0, -4.0],  // dorm Buscadora
  // Pared SUR z=+4
  [-10.75, 0,  4.0], // → Comedor
  [   0.0, 0,  4.0], // → Baño
  [ 10.75, 0,  4.0], // → Cocina
  // Puerta de entrada exterior
  [-10.75, 0, 12.9],
];

// ─── Interest points ───────────────────────────────────────────────────────
export const INTEREST_POINTS: InterestPoint[] = [
  // Camas (dormitorios norte)
  { name: "Cama Cartero",    position: [-10.75, 0, -8.5], type: "bed" },
  { name: "Cama Detective",  position: [  0,    0, -8.5], type: "bed" },
  { name: "Cama Buscadora",  position: [ 10.75, 0, -8.5], type: "bed" },
  // Workstations (living central)
  { name: "Silla Cartero",   position: [-10.75, 0, -1.2], type: "chair" },
  { name: "Silla Detective", position: [  0,    0, -1.2], type: "chair" },
  { name: "Silla Buscadora", position: [ 10.75, 0, -1.2], type: "chair" },
  // Puntos aleatorios en espacios abiertos
  { name: "Comedor",   position: [-10.75, 0,  8.5], type: "random" },
  { name: "Cocina",    position: [ 10.75, 0,  8.5], type: "random" },
  { name: "Living",    position: [  0,    0,  0  ], type: "random" },
  { name: "Pasillo W", position: [ -8.0,  0,  0  ], type: "random" },
  { name: "Pasillo E", position: [  8.0,  0,  0  ], type: "random" },
  // Waypoints en puertas
  ...DOORS.map((pos, i) => ({
    name: `Puerta ${i}`,
    position: pos,
    type: "waypoint" as const,
  })),
];

// ─── Bounds ────────────────────────────────────────────────────────────────
export const BOUNDS = {
  minX: -15.5,
  maxX:  15.5,
  minZ: -12.5,
  maxZ:  12.5,
  y: 0,
};

// ─── Helpers ───────────────────────────────────────────────────────────────
export function getRandomWalkPoint(): [number, number, number] {
  const randomPoints = INTEREST_POINTS.filter(p => p.type === "random");
  if (randomPoints.length === 0) return [0, 0, 0];
  const chosen = randomPoints[Math.floor(Math.random() * randomPoints.length)];
  return chosen.position;
}

export function getWorkPoint(agentIndex: number): [number, number, number] {
  const points = INTEREST_POINTS.filter(p => p.type === "chair");
  return points[agentIndex % points.length].position;
}

export function getSleepPoint(agentIndex: number): [number, number, number] {
  const points = INTEREST_POINTS.filter(p => p.type === "bed");
  return points[agentIndex % points.length].position;
}

export function distanceTo(
  from: [number, number, number],
  to:   [number, number, number]
): number {
  const dx = to[0] - from[0];
  const dz = to[2] - from[2];
  return Math.sqrt(dx * dx + dz * dz);
}

export function moveTowards(
  from:     [number, number, number],
  to:       [number, number, number],
  distance: number
): [number, number, number] {
  const dx   = to[0] - from[0];
  const dz   = to[2] - from[2];
  const dist = Math.sqrt(dx * dx + dz * dz);
  if (dist < distance) return to;
  const ratio = distance / dist;
  return [from[0] + dx * ratio, from[1], from[2] + dz * ratio];
}

// ─── Colisión con muros ─────────────────────────────────────────────────────
// Radio reducido (0.3) porque las paredes ya son gruesas (0.6)
export function isCollidingWithWall(
  pos:    [number, number, number],
  radius: number = 0.3
): boolean {
  for (const wall of WALLS) {
    if (
      pos[0] + radius > wall.x1 &&
      pos[0] - radius < wall.x2 &&
      pos[2] + radius > wall.z1 &&
      pos[2] - radius < wall.z2
    ) {
      return true;
    }
  }
  return false;
}

// ─── Pathfinding con waypoints ─────────────────────────────────────────────
export function findPath(
  from: [number, number, number],
  to:   [number, number, number]
): [number, number, number][] {
  if (!hasDirectObstacle(from, to)) {
    return [to];
  }

  // Elige la puerta que minimiza distancia total from→door→to
  const bestDoor = DOORS.reduce<[number, number, number]>((best, door) => {
    const costBest = distanceTo(from, best) + distanceTo(best, to);
    const costDoor = distanceTo(from, door) + distanceTo(door, to);
    return costDoor < costBest ? door : best;
  }, DOORS[0]);

  // Si aún hay obstáculo desde la puerta al destino, buscar segunda puerta
  if (hasDirectObstacle(bestDoor, to)) {
    const secondDoor = DOORS
      .filter(d => d !== bestDoor)
      .reduce<[number, number, number]>((best, door) => {
        const costBest = distanceTo(bestDoor, best) + distanceTo(best, to);
        const costDoor = distanceTo(bestDoor, door) + distanceTo(door, to);
        return costDoor < costBest ? door : best;
      }, DOORS[0]);
    return [bestDoor, secondDoor, to];
  }

  return [bestDoor, to];
}

function hasDirectObstacle(
  from: [number, number, number],
  to:   [number, number, number]
): boolean {
  const steps = Math.ceil(distanceTo(from, to) / 0.3);
  for (let i = 0; i <= steps; i++) {
    const t = steps > 0 ? i / steps : 0;
    const check: [number, number, number] = [
      from[0] + (to[0] - from[0]) * t,
      from[1],
      from[2] + (to[2] - from[2]) * t,
    ];
    if (isCollidingWithWall(check)) return true;
  }
  return false;
}
