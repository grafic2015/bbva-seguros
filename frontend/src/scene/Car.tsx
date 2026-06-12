import React, { useRef, useEffect } from "react";
import * as THREE from "three";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import { treePositions } from "./RoadEnvironment";

// ── Geometría de la carretera ─────────────────────────────────────────────────
// parkSize = 75, roadWidth = 20
// Centro de carril exterior: 75 + 5 = 80  (clockwise)
// Centro de carril interior: 75 - 5 = 70  (counter-clockwise)
const OUTER = 80;  // carril exterior (auto rojo, sentido horario)
const INNER = 70;  // carril interior (auto azul, sentido antihorario)

// Waypoints con esquinas achaflanadas para giros suaves
// Sentido HORARIO: top-left → top-right → bottom-right → bottom-left
export const ROAD_WAYPOINTS_OUTER: [number, number, number][] = [
  // Segmento superior (Z = -OUTER), de izquierda a derecha
  [-OUTER + 12, 0, -OUTER],
  [ OUTER - 12, 0, -OUTER],
  // Giro superior-derecho
  [ OUTER,      0, -OUTER + 12],
  // Segmento derecho (X = +OUTER), de arriba a abajo
  [ OUTER,      0,  OUTER - 12],
  // Giro inferior-derecho
  [ OUTER - 12, 0,  OUTER],
  // Segmento inferior (Z = +OUTER), de derecha a izquierda
  [-OUTER + 12, 0,  OUTER],
  // Giro inferior-izquierdo
  [-OUTER,      0,  OUTER - 12],
  // Segmento izquierdo (X = -OUTER), de abajo a arriba
  [-OUTER,      0, -OUTER + 12],
  // Giro superior-izquierdo (vuelve al inicio)
];

// Sentido ANTIHORARIO: top-right → top-left → bottom-left → bottom-right
export const ROAD_WAYPOINTS_INNER: [number, number, number][] = [
  // Segmento superior (Z = -INNER), de derecha a izquierda
  [ INNER - 10, 0, -INNER],
  [-INNER + 10, 0, -INNER],
  // Giro superior-izquierdo
  [-INNER,      0, -INNER + 10],
  // Segmento izquierdo (X = -INNER), de arriba a abajo
  [-INNER,      0,  INNER - 10],
  // Giro inferior-izquierdo
  [-INNER + 10, 0,  INNER],
  // Segmento inferior (Z = +INNER), de izquierda a derecha
  [ INNER - 10, 0,  INNER],
  // Giro inferior-derecho
  [ INNER,      0,  INNER - 10],
  // Segmento derecho (X = +INNER), de abajo a arriba
  [ INNER,      0, -INNER + 10],
  // Giro superior-derecho (vuelve al inicio)
];

interface CarProps {
  initialPosition?: [number, number, number];
  color?: string;
  controls?: "arrows" | "wasd";
  agentName?: string;
  agentStatus?: string;
  agentColor?: string;
  waypoints: [number, number, number][];
  children?: React.ReactNode;
}

const keys = {
  ArrowUp: false, ArrowDown: false, ArrowLeft: false, ArrowRight: false,
  w: false, s: false, a: false, d: false,
};

window.addEventListener("keydown", (e) => {
  const key = e.key.toLowerCase();
  if (Object.prototype.hasOwnProperty.call(keys, key)) (keys as any)[key] = true;
  if (Object.prototype.hasOwnProperty.call(keys, e.key)) (keys as any)[e.key] = true;
});
window.addEventListener("keyup", (e) => {
  const key = e.key.toLowerCase();
  if (Object.prototype.hasOwnProperty.call(keys, key)) (keys as any)[key] = false;
  if (Object.prototype.hasOwnProperty.call(keys, e.key)) (keys as any)[e.key] = false;
});

export function Car({
  initialPosition = [0, 0, 0],
  color = "#d9381e",
  controls,
  agentName,
  agentStatus,
  agentColor = "#ffffff",
  waypoints,
  children,
}: CarProps) {
  const group = useRef<THREE.Group>(null);

  const state = useRef({
    speed: 0,
    angle: 0,
    // Auto-piloto
    wpIndex: 0,                     // índice del waypoint actual
    autopilot: true,                // arranca en auto-piloto
  });

  // ── Bucle de física ───────────────────────────────────────────────────────────
  useFrame((_, delta) => {
    if (!group.current) return;

    // Detectar si hay input manual
    const hasInput = controls === "arrows"
      ? (keys.ArrowUp || keys.ArrowDown || keys.ArrowLeft || keys.ArrowRight)
      : controls === "wasd"
      ? (keys.w || keys.s || keys.a || keys.d)
      : false;

    // Conmutar auto-piloto
    if (hasInput) {
      state.current.autopilot = false;
    } else if (!hasInput && !state.current.autopilot) {
      // Volver al auto-piloto cuando el usuario suelta las teclas (con un pequeño delay implícito por fricción)
      if (Math.abs(state.current.speed) < 0.5) {
        state.current.autopilot = true;
      }
    }

    const acceleration = 35;
    const maxSpeed     = 50;
    const autopilotSpeed = 18;
    const friction     = 10;
    const turnSpeed    = 3.5;

    if (state.current.autopilot) {
      // ── AUTO-PILOTO: navegar al siguiente waypoint ──────────────────────────
      const wp = waypoints[state.current.wpIndex];
      const target = new THREE.Vector3(wp[0], wp[1], wp[2]);
      const dx = target.x - group.current.position.x;
      const dz = target.z - group.current.position.z;
      const dist = Math.sqrt(dx * dx + dz * dz);

      // Si llegamos al waypoint actual, avanzar al siguiente
      if (dist < 4) {
        state.current.wpIndex = (state.current.wpIndex + 1) % waypoints.length;
      }

      // Calcular ángulo hacia el target (invertido porque la velocidad se resta en la actualización de posición)
      const targetAngle = Math.atan2(-dx, -dz);

      // Interpolar suavemente el ángulo actual
      let angleDiff = targetAngle - state.current.angle;
      // Normalizar al rango [-π, π]
      while (angleDiff >  Math.PI) angleDiff -= 2 * Math.PI;
      while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;
      state.current.angle += angleDiff * Math.min(1, delta * 4);
      state.current.speed = autopilotSpeed;

    } else {
      // ── CONTROL MANUAL ───────────────────────────────────────────────────────
      let forward = false, backward = false, left = false, right = false;

      if (controls === "arrows") {
        forward = keys.ArrowUp; backward = keys.ArrowDown;
        left = keys.ArrowLeft;  right = keys.ArrowRight;
      } else if (controls === "wasd") {
        forward = keys.w; backward = keys.s;
        left = keys.a;    right = keys.d;
      }

      if (forward) {
        state.current.speed += acceleration * delta;
      } else if (backward) {
        state.current.speed -= acceleration * delta;
      } else {
        if (state.current.speed > 0) {
          state.current.speed = Math.max(0, state.current.speed - friction * delta);
        } else {
          state.current.speed = Math.min(0, state.current.speed + friction * delta);
        }
      }
      state.current.speed = Math.max(-maxSpeed / 2, Math.min(maxSpeed, state.current.speed));

      if (Math.abs(state.current.speed) > 0.1) {
        const dir = state.current.speed > 0 ? 1 : -1;
        if (left)  state.current.angle += turnSpeed * delta * dir;
        if (right) state.current.angle -= turnSpeed * delta * dir;
      }
    }

    // Aplicar rotación visual
    group.current.rotation.y = state.current.angle;

    // Calcular nueva posición
    const vx = Math.sin(state.current.angle) * state.current.speed;
    const vz = Math.cos(state.current.angle) * state.current.speed;
    let newX = group.current.position.x - vx * delta;
    let newZ = group.current.position.z - vz * delta;

    // Colisiones
    const limit = 86;
    let collided = false;
    if (newX > limit || newX < -limit) { newX = group.current.position.x; collided = true; }
    if (newZ > limit || newZ < -limit) { newZ = group.current.position.z; collided = true; }
    if (newX * newX + newZ * newZ < 100) { newX = group.current.position.x; newZ = group.current.position.z; collided = true; }
    for (const tp of treePositions) {
      const dx = newX - tp[0], dz = newZ - tp[2];
      if (dx * dx + dz * dz < 16) { newX = group.current.position.x; newZ = group.current.position.z; collided = true; break; }
    }

    if (collided) {
      state.current.speed = 0;
      // En auto-piloto avanzar al siguiente waypoint si colisiona
      if (state.current.autopilot) {
        state.current.wpIndex = (state.current.wpIndex + 1) % waypoints.length;
      }
    }

    group.current.position.x = newX;
    group.current.position.z = newZ;
  });

  // ── Determinar color e icono del cartel según el estado del agente ────────────
  const statusBgColor = agentStatus === "running" ? "#1f6feb33"
                      : agentStatus === "done"    ? "#3fb95033"
                      : agentStatus === "error"   ? "#f8514933"
                      : "#21262dbb";
  const statusBorderColor = agentStatus === "running" ? agentColor
                          : agentStatus === "done"    ? "#3fb950"
                          : agentStatus === "error"   ? "#f85149"
                          : "#30363d";
  const statusDot = agentStatus === "running" ? "🟢"
                  : agentStatus === "done"    ? "✅"
                  : agentStatus === "error"   ? "🔴"
                  : "⚪";

  return (
    <group ref={group} position={initialPosition}>

      {/* Nametag flotante 3D */}
      {agentName && (
        <Html
          position={[0, 14, 0]}
          center
          occlude={false}
          style={{ pointerEvents: "none" }}
        >
          <div style={{
            background: statusBgColor,
            border: `1px solid ${statusBorderColor}`,
            borderRadius: 10,
            padding: "5px 12px",
            backdropFilter: "blur(8px)",
            whiteSpace: "nowrap",
            userSelect: "none",
            transition: "all 0.3s",
            boxShadow: agentStatus === "running"
              ? `0 0 16px ${agentColor}66, 0 2px 8px #000a`
              : "0 2px 8px #000a",
          }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: agentColor, display: "flex", alignItems: "center", gap: 5 }}>
              {statusDot}
              <span>{agentName}</span>
            </div>
          </div>
        </Html>
      )}

      {/* Contenedor de hijos */}
      <group position={[0, 5, 0]}>{children}</group>

      {/* Modelo del Auto (Escalado x2) */}
      <group scale={[2, 2, 2]}>
        {/* Carrocería principal */}
        <mesh position={[0, 0.5, 0]} castShadow receiveShadow>
          <boxGeometry args={[2.5, 0.8, 5]} />
          <meshStandardMaterial color={color} roughness={0.4} metalness={0.6} />
        </mesh>
        {/* Cabina */}
        <mesh position={[0, 1.25, 0.5]} castShadow receiveShadow>
          <boxGeometry args={[2, 0.7, 2.5]} />
          <meshStandardMaterial color={color} roughness={0.4} metalness={0.6} />
        </mesh>
        {/* Ventanas */}
        <mesh position={[0, 1.25, 0.5]}>
          <boxGeometry args={[2.1, 0.5, 2.3]} />
          <meshStandardMaterial color="#111111" roughness={0.1} metalness={0.8} />
        </mesh>
        {/* Ruedas */}
        {([-1.3, 1.3] as number[]).map((x) =>
          ([1.5, -1.5] as number[]).map((z) => (
            <mesh key={`${x}-${z}`} position={[x, 0.4, z]} castShadow rotation={[0, 0, Math.PI / 2]}>
              <cylinderGeometry args={[0.4, 0.4, 0.3, 16]} />
              <meshStandardMaterial color="#222" roughness={0.8} />
            </mesh>
          ))
        )}
        {/* Luces delanteras */}
        <mesh position={[-0.8, 0.6, -2.51]}>
          <planeGeometry args={[0.4, 0.2]} />
          <meshStandardMaterial color="#ffffee" emissive="#ffffee" emissiveIntensity={2} />
        </mesh>
        <mesh position={[0.8, 0.6, -2.51]}>
          <planeGeometry args={[0.4, 0.2]} />
          <meshStandardMaterial color="#ffffee" emissive="#ffffee" emissiveIntensity={2} />
        </mesh>
        {/* Luces traseras */}
        <mesh position={[-0.8, 0.6, 2.51]} rotation={[0, Math.PI, 0]}>
          <planeGeometry args={[0.4, 0.2]} />
          <meshStandardMaterial color="#ff0000" emissive="#ff0000" emissiveIntensity={2} />
        </mesh>
        <mesh position={[0.8, 0.6, 2.51]} rotation={[0, Math.PI, 0]}>
          <planeGeometry args={[0.4, 0.2]} />
          <meshStandardMaterial color="#ff0000" emissive="#ff0000" emissiveIntensity={2} />
        </mesh>
      </group>
    </group>
  );
}
