import { useMemo } from "react";
import * as THREE from "three";
import { Html } from "@react-three/drei";
import type { AgentId } from "../types";
import { AGENT_META } from "../types";

interface WorkstationProps {
  agent: AgentId;
  position: [number, number, number];
}

/** Un puesto de trabajo: escritorio + monitor + teclado + lámpara + taza. */
function Workstation({ agent, position }: WorkstationProps) {
  const color = AGENT_META[agent].color;

  return (
    <group position={position}>
      {/* Escritorio (tablero) */}
      <mesh position={[0, 0.75, 0]} castShadow receiveShadow>
        <boxGeometry args={[1.2, 0.06, 0.7]} />
        <meshStandardMaterial color="#6b4f3a" roughness={0.7} />
      </mesh>
      {/* Patas */}
      {[
        [-0.55, 0.375, -0.3],
        [0.55, 0.375, -0.3],
        [-0.55, 0.375, 0.3],
        [0.55, 0.375, 0.3],
      ].map((p, i) => (
        <mesh key={i} position={p as [number, number, number]} castShadow>
          <boxGeometry args={[0.06, 0.75, 0.06]} />
          <meshStandardMaterial color="#3a2a20" roughness={0.8} />
        </mesh>
      ))}

      {/* Monitor */}
      <mesh position={[0, 0.83, -0.15]} castShadow>
        <boxGeometry args={[0.18, 0.04, 0.18]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
      <mesh position={[0, 0.95, -0.15]} castShadow>
        <boxGeometry args={[0.05, 0.2, 0.05]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
      <mesh position={[0, 1.2, -0.15]} castShadow>
        <boxGeometry args={[0.85, 0.5, 0.05]} />
        <meshStandardMaterial color="#222" />
      </mesh>
      <mesh position={[0, 1.2, -0.12]}>
        <planeGeometry args={[0.78, 0.43]} />
        <meshBasicMaterial color={color} />
      </mesh>

      {/* Teclado + mouse */}
      <mesh position={[0, 0.79, 0.15]} castShadow>
        <boxGeometry args={[0.5, 0.025, 0.18]} />
        <meshStandardMaterial color="#2a2a2a" />
      </mesh>
      <mesh position={[0.32, 0.79, 0.17]} castShadow>
        <boxGeometry args={[0.08, 0.025, 0.12]} />
        <meshStandardMaterial color="#2a2a2a" />
      </mesh>

      {/* Lámpara */}
      <mesh position={[-0.5, 0.83, -0.25]} castShadow>
        <cylinderGeometry args={[0.07, 0.09, 0.04, 16]} />
        <meshStandardMaterial color="#444" />
      </mesh>
      <mesh position={[-0.5, 1.05, -0.25]} castShadow>
        <cylinderGeometry args={[0.015, 0.015, 0.4, 8]} />
        <meshStandardMaterial color="#666" />
      </mesh>
      <mesh position={[-0.5, 1.27, -0.18]} rotation={[0.5, 0, 0]} castShadow>
        <coneGeometry args={[0.08, 0.12, 16, 1, true]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.4} side={THREE.DoubleSide} />
      </mesh>

      {/* Taza de café */}
      <mesh position={[0.5, 0.83, -0.25]} castShadow>
        <cylinderGeometry args={[0.05, 0.045, 0.1, 16]} />
        <meshStandardMaterial color="#f0f0f0" />
      </mesh>
    </group>
  );
}

/** Tele plana montada en pared con el color del agente. */
function WallTV({ position, color }: { position: [number, number, number]; color: string }) {
  return (
    <group position={position}>
      {/* Marco */}
      <mesh castShadow>
        <boxGeometry args={[1.1, 0.7, 0.06]} />
        <meshStandardMaterial color="#0a0a0a" roughness={0.4} />
      </mesh>
      {/* Pantalla brillante */}
      <mesh position={[0, 0, 0.1]}>
        <planeGeometry args={[1.0, 0.6]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={1.2}
          toneMapped={false}
        />
      </mesh>
      {/* Soporte */}
      <mesh position={[0, -0.55, 0]}>
        <boxGeometry args={[0.4, 0.04, 0.04]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
    </group>
  );
}

interface OfficeProps {
  stations: Record<AgentId, [number, number, number]>;
}

export function Office({ stations }: OfficeProps) {
  // Piso de tablones de madera (vetas verticales)
  const floorMat = useMemo(() => {
    const size = 512;
    const c = document.createElement("canvas");
    c.width = c.height = size;
    const ctx = c.getContext("2d")!;
    // base
    ctx.fillStyle = "#8a5e3c";
    ctx.fillRect(0, 0, size, size);
    // tablones
    const plankW = size / 6;
    for (let i = 0; i < 6; i++) {
      const x = i * plankW;
      const shade = 0.85 + Math.random() * 0.2;
      ctx.fillStyle = `rgba(${Math.floor(120 * shade)}, ${Math.floor(80 * shade)}, ${Math.floor(50 * shade)}, 1)`;
      ctx.fillRect(x, 0, plankW - 2, size);
      // vetas
      ctx.strokeStyle = "rgba(60, 35, 20, 0.4)";
      ctx.lineWidth = 1;
      for (let y = 0; y < 8; y++) {
        ctx.beginPath();
        ctx.moveTo(x + 4, (y * size) / 8 + Math.random() * 10);
        ctx.bezierCurveTo(
          x + plankW * 0.3, (y * size) / 8 + Math.random() * 15,
          x + plankW * 0.6, (y * size) / 8 + Math.random() * 15,
          x + plankW - 4, (y * size) / 8 + Math.random() * 10
        );
        ctx.stroke();
      }
    }
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(3, 3);
    return new THREE.MeshStandardMaterial({ map: tex, roughness: 0.75 });
  }, []);

  // Material de pared (color crema con leve textura)
  const wallColor = "#d4c8b0";
  const accentColor = "#b89e7a";

  return (
    <group>
      {/* Piso de madera */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow material={floorMat}>
        <planeGeometry args={[20, 14]} />
      </mesh>


      {/* 3 Televisores en la pared del fondo (uno por agente) */}
      <WallTV position={[-1.9, 2.5, -2.25]} color="#3fb950" />
      <WallTV position={[0, 2.5, -2.25]} color="#f0883e" />
      <WallTV position={[1.9, 2.5, -2.25]} color="#58a6ff" />

      {/* Sofá decorativo al fondo izquierdo */}
      <group position={[-7, 0, -1.5]}>
        {/* Base */}
        <mesh position={[0, 0.3, 0]} castShadow receiveShadow>
          <boxGeometry args={[2.4, 0.4, 0.9]} />
          <meshStandardMaterial color="#5a4055" roughness={0.9} />
        </mesh>
        {/* Respaldo */}
        <mesh position={[0, 0.75, -0.4]} castShadow>
          <boxGeometry args={[2.4, 0.8, 0.2]} />
          <meshStandardMaterial color="#5a4055" roughness={0.9} />
        </mesh>
        {/* Cojines */}
        <mesh position={[-0.6, 0.55, 0.1]} castShadow>
          <boxGeometry args={[0.9, 0.2, 0.7]} />
          <meshStandardMaterial color="#6c4f68" roughness={0.9} />
        </mesh>
        <mesh position={[0.6, 0.55, 0.1]} castShadow>
          <boxGeometry args={[0.9, 0.2, 0.7]} />
          <meshStandardMaterial color="#6c4f68" roughness={0.9} />
        </mesh>
      </group>

      {/* Mesita ratona con libros */}
      <group position={[-7, 0, 0.2]}>
        <mesh position={[0, 0.3, 0]} castShadow receiveShadow>
          <boxGeometry args={[1.2, 0.05, 0.7]} />
          <meshStandardMaterial color="#6b4f3a" roughness={0.7} />
        </mesh>
        {[[-0.4, 0.3, -0.25], [0.4, 0.3, -0.25], [-0.4, 0.3, 0.25], [0.4, 0.3, 0.25]].map((p, i) => (
          <mesh key={i} position={p as [number, number, number]} castShadow>
            <cylinderGeometry args={[0.03, 0.03, 0.3, 8]} />
            <meshStandardMaterial color="#3a2a20" />
          </mesh>
        ))}
        {/* Libros */}
        <mesh position={[-0.3, 0.36, 0]} castShadow>
          <boxGeometry args={[0.18, 0.07, 0.25]} />
          <meshStandardMaterial color="#a83c3c" />
        </mesh>
        <mesh position={[-0.1, 0.36, 0]} castShadow>
          <boxGeometry args={[0.18, 0.07, 0.25]} />
          <meshStandardMaterial color="#3c5aa8" />
        </mesh>
      </group>

      {/* Biblioteca a la derecha */}
      <group position={[7, 0, -1.7]}>
        {/* Mueble */}
        <mesh position={[0, 1.1, 0]} castShadow receiveShadow>
          <boxGeometry args={[2.2, 2.2, 0.4]} />
          <meshStandardMaterial color="#5a3f28" roughness={0.8} />
        </mesh>
        {/* Estantes con libros (colores) */}
        {[0.5, 1.1, 1.7].map((y, idx) => (
          <group key={idx} position={[0, y, 0.22]}>
            {Array.from({ length: 8 }).map((_, i) => (
              <mesh
                key={i}
                position={[-0.9 + i * 0.25, 0, 0]}
                castShadow
              >
                <boxGeometry args={[0.18, 0.4, 0.18]} />
                <meshStandardMaterial
                  color={
                    ["#a83c3c", "#3c5aa8", "#3ca85a", "#a8973c", "#7a3ca8", "#3ca89a"][
                      (i + idx) % 6
                    ]
                  }
                />
              </mesh>
            ))}
          </group>
        ))}
      </group>

      {/* Plantas en esquinas */}
      <group position={[-3.5, 0, -1.8]}>
        <mesh castShadow>
          <cylinderGeometry args={[0.18, 0.22, 0.4, 16]} />
          <meshStandardMaterial color="#5a3a25" />
        </mesh>
        <mesh position={[0, 0.5, 0]} castShadow>
          <sphereGeometry args={[0.38, 16, 16]} />
          <meshStandardMaterial color="#3d6b3a" roughness={0.9} />
        </mesh>
      </group>
      <group position={[3.5, 0, -1.8]}>
        <mesh castShadow>
          <cylinderGeometry args={[0.18, 0.22, 0.4, 16]} />
          <meshStandardMaterial color="#5a3a25" />
        </mesh>
        <mesh position={[0, 0.5, 0]} castShadow>
          <sphereGeometry args={[0.38, 16, 16]} />
          <meshStandardMaterial color="#3d6b3a" roughness={0.9} />
        </mesh>
      </group>

      {/* Lámpara de pie a la izquierda del sofá */}
      <group position={[-8.5, 0, -1.5]}>
        <mesh castShadow>
          <cylinderGeometry args={[0.2, 0.25, 0.08, 16]} />
          <meshStandardMaterial color="#333" />
        </mesh>
        <mesh position={[0, 1, 0]} castShadow>
          <cylinderGeometry args={[0.02, 0.02, 2, 8]} />
          <meshStandardMaterial color="#444" />
        </mesh>
        <mesh position={[0, 2.05, 0]} castShadow>
          <coneGeometry args={[0.3, 0.4, 16, 1, true]} />
          <meshStandardMaterial color="#fff4d6" emissive="#ffd6a0" emissiveIntensity={0.5} side={THREE.DoubleSide} />
        </mesh>
      </group>

      {/* Alfombras individuales por agente con sus colores */}
      {(Object.keys(stations) as AgentId[]).map((id) => {
        const [x, , z] = stations[id];
        const color = AGENT_META[id].color;
        return (
          <group key={`space-${id}`}>
            {/* Alfombra */}
            <mesh
              rotation={[-Math.PI / 2, 0, 0]}
              position={[x, 0.006, z - 0.5]}
              receiveShadow
            >
              <planeGeometry args={[3.2, 2.5]} />
              <meshStandardMaterial
                color={color}
                emissive={color}
                emissiveIntensity={0.3}
                roughness={0.4}
                opacity={1}
                transparent
              />
            </mesh>


          </group>
        );
      })}



      {/* Estaciones de trabajo */}
      {(Object.keys(stations) as AgentId[]).map((id) => {
        const [x, , z] = stations[id];
        return <Workstation key={id} agent={id} position={[x, 0, z - 1.0]} />;
      })}
    </group>
  );
}
