import React from "react";
// Vite reload fix

interface Props {
  position: [number, number, number];
  rotation?: [number, number, number];
}

// Iglesia / Capilla con campanario
export function Church({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      {/* Nave principal */}
      <mesh position={[0, 4, 0]} castShadow receiveShadow>
        <boxGeometry args={[10, 8, 12]} />
        <meshStandardMaterial color="#f5e6c8" roughness={0.8} />
      </mesh>

      {/* Techo a dos aguas */}
      <mesh position={[0, 9, 0]} rotation={[0, Math.PI / 2, 0]} castShadow>
        <cylinderGeometry args={[6.5, 6.5, 10, 4]} />
        <meshStandardMaterial color="#8b4513" roughness={0.9} />
      </mesh>

      {/* Campanario */}
      <mesh position={[0, 10, -4]} castShadow>
        <boxGeometry args={[3, 8, 3]} />
        <meshStandardMaterial color="#f0dcc0" roughness={0.7} />
      </mesh>
      <mesh position={[0, 15, -4]} castShadow>
        <coneGeometry args={[2.5, 4, 4]} />
        <meshStandardMaterial color="#8b4513" roughness={0.8} />
      </mesh>

      {/* Cruz en la punta */}
      <mesh position={[0, 17.5, -4]}>
        <boxGeometry args={[0.2, 1.5, 0.2]} />
        <meshStandardMaterial color="#cccccc" metalness={0.6} />
      </mesh>
      <mesh position={[0, 17.8, -4]}>
        <boxGeometry args={[1, 0.2, 0.2]} />
        <meshStandardMaterial color="#cccccc" metalness={0.6} />
      </mesh>

      {/* Puerta principal (arco) */}
      <mesh position={[0, 2, 6.1]}>
        <planeGeometry args={[3, 4]} />
        <meshStandardMaterial color="#5a3a1a" />
      </mesh>

      {/* Vitral circular */}
      <mesh position={[0, 6, 6.1]}>
        <circleGeometry args={[1.5, 16]} />
        <meshStandardMaterial color="#4488cc" emissive="#2244aa" emissiveIntensity={0.3} />
      </mesh>
    </group>
  );
}

// Farmacia
export function Pharmacy({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      <mesh position={[0, 3.5, 0]} castShadow receiveShadow>
        <boxGeometry args={[8, 7, 8]} />
        <meshStandardMaterial color="#ffffff" roughness={0.6} />
      </mesh>

      {/* Cruz verde (símbolo de farmacia) */}
      <mesh position={[0, 5, 4.1]}>
        <boxGeometry args={[0.5, 2.5, 0.1]} />
        <meshStandardMaterial color="#00cc44" emissive="#00aa33" emissiveIntensity={0.6} />
      </mesh>
      <mesh position={[0, 5, 4.1]}>
        <boxGeometry args={[2.5, 0.5, 0.1]} />
        <meshStandardMaterial color="#00cc44" emissive="#00aa33" emissiveIntensity={0.6} />
      </mesh>

      {/* Toldo verde */}
      <mesh position={[0, 3, 4.5]} rotation={[Math.PI / 8, 0, 0]} castShadow>
        <boxGeometry args={[7, 1.5, 0.15]} />
        <meshStandardMaterial color="#00aa33" />
      </mesh>

      {/* Vitrina */}
      <mesh position={[0, 1.5, 4.1]}>
        <planeGeometry args={[6, 3]} />
        <meshStandardMaterial color="#cceecc" opacity={0.7} transparent />
      </mesh>
    </group>
  );
}

// Hotel
export function Hotel({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      {/* Cuerpo principal */}
      <mesh position={[0, 10, 0]} castShadow receiveShadow>
        <boxGeometry args={[12, 20, 10]} />
        <meshStandardMaterial color="#d4af37" roughness={0.4} metalness={0.3} />
      </mesh>

      {/* Franja dorada decorativa */}
      <mesh position={[0, 20.1, 0]}>
        <boxGeometry args={[12.2, 0.3, 10.2]} />
        <meshStandardMaterial color="#ffd700" metalness={0.8} roughness={0.2} />
      </mesh>

      {/* Entrada con marquesina */}
      <mesh position={[0, 2, 5.5]} castShadow>
        <boxGeometry args={[6, 0.3, 3]} />
        <meshStandardMaterial color="#8b0000" />
      </mesh>
      {/* Pilares de la marquesina */}
      <mesh position={[-2.5, 1, 6.5]} castShadow>
        <cylinderGeometry args={[0.2, 0.2, 2, 8]} />
        <meshStandardMaterial color="#ffd700" metalness={0.8} />
      </mesh>
      <mesh position={[2.5, 1, 6.5]} castShadow>
        <cylinderGeometry args={[0.2, 0.2, 2, 8]} />
        <meshStandardMaterial color="#ffd700" metalness={0.8} />
      </mesh>

      {/* Ventanas en cada piso */}
      {[4, 8, 12, 16].map((y, fi) => (
        [-4, -1.5, 1.5, 4].map((x, ci) => (
          <mesh key={`${fi}-${ci}`} position={[x, y, 5.1]}>
            <planeGeometry args={[1.5, 2]} />
            <meshStandardMaterial color="#88ccff" />
          </mesh>
        ))
      ))}

      {/* Puerta principal */}
      <mesh position={[0, 1.5, 5.1]}>
        <planeGeometry args={[3, 3]} />
        <meshStandardMaterial color="#331100" />
      </mesh>
    </group>
  );
}

// Estación de Radio / Telecomunicaciones
export function RadioTower({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      {/* Edificio base */}
      <mesh position={[0, 3, 0]} castShadow receiveShadow>
        <boxGeometry args={[6, 6, 6]} />
        <meshStandardMaterial color="#556677" roughness={0.7} />
      </mesh>

      {/* Antena principal */}
      <mesh position={[0, 15, 0]} castShadow>
        <cylinderGeometry args={[0.15, 0.15, 18, 6]} />
        <meshStandardMaterial color="#cccccc" metalness={0.9} />
      </mesh>

      {/* Estructura triangular de soporte */}
      <mesh position={[-1.5, 10, 0]} castShadow>
        <cylinderGeometry args={[0.08, 0.08, 14, 4]} />
        <meshStandardMaterial color="#aaaaaa" metalness={0.8} />
      </mesh>
      <mesh position={[1.5, 10, 0]} castShadow>
        <cylinderGeometry args={[0.08, 0.08, 14, 4]} />
        <meshStandardMaterial color="#aaaaaa" metalness={0.8} />
      </mesh>

      {/* Luz roja arriba (baliza) */}
      <mesh position={[0, 24.2, 0]}>
        <sphereGeometry args={[0.4, 8, 8]} />
        <meshStandardMaterial color="#ff0000" emissive="#ff0000" emissiveIntensity={2} />
      </mesh>

      {/* Plato parabólico */}
      <mesh position={[2, 8, 3.1]} rotation={[0, 0, Math.PI / 6]}>
        <cylinderGeometry args={[1.5, 0.3, 0.3, 16]} />
        <meshStandardMaterial color="#dddddd" metalness={0.7} />
      </mesh>
    </group>
  );
}

// Fuente del Parque Central
export function ParkFountain({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      {/* Base circular */}
      <mesh position={[0, 0.3, 0]} receiveShadow>
        <cylinderGeometry args={[6, 7, 0.6, 24]} />
        <meshStandardMaterial color="#999999" roughness={0.5} />
      </mesh>

      {/* Agua */}
      <mesh position={[0, 0.35, 0]}>
        <cylinderGeometry args={[5.5, 5.5, 0.2, 24]} />
        <meshStandardMaterial color="#4499cc" opacity={0.7} transparent roughness={0.1} />
      </mesh>

      {/* Columna central */}
      <mesh position={[0, 2, 0]} castShadow>
        <cylinderGeometry args={[0.5, 0.6, 3, 12]} />
        <meshStandardMaterial color="#aaaaaa" roughness={0.4} />
      </mesh>

      {/* Plato superior */}
      <mesh position={[0, 3.5, 0]} castShadow>
        <cylinderGeometry args={[2, 2.5, 0.4, 16]} />
        <meshStandardMaterial color="#999999" roughness={0.4} />
      </mesh>
      <mesh position={[0, 3.55, 0]}>
        <cylinderGeometry args={[1.8, 1.8, 0.15, 16]} />
        <meshStandardMaterial color="#4499cc" opacity={0.7} transparent roughness={0.1} />
      </mesh>

      {/* Chorro superior (esfera de agua) */}
      <mesh position={[0, 4.5, 0]}>
        <sphereGeometry args={[0.4, 12, 12]} />
        <meshStandardMaterial color="#88ddff" opacity={0.5} transparent emissive="#44aacc" emissiveIntensity={0.3} />
      </mesh>
    </group>
  );
}

// Faroles de calle
export function StreetLamp({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh position={[0, 3, 0]} castShadow>
        <cylinderGeometry args={[0.1, 0.15, 6, 8]} />
        <meshStandardMaterial color="#333333" metalness={0.8} />
      </mesh>
      <mesh position={[0, 6.2, 0]}>
        <sphereGeometry args={[0.4, 8, 8]} />
        <meshStandardMaterial color="#ffffcc" emissive="#ffeeaa" emissiveIntensity={1} />
      </mesh>
    </group>
  );
}

// Juegos de plaza (Playground)
export function Playground({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      {/* Suelo de arena/goma */}
      <mesh position={[0, 0.1, 0]} receiveShadow>
        <boxGeometry args={[22, 0.2, 14]} />
        <meshStandardMaterial color="#e5c07b" roughness={0.9} />
      </mesh>

      {/* Tobogán */}
      <group position={[-5, 0, -3]}>
        {/* Escaleras */}
        <mesh position={[0, 1.5, -1.5]} rotation={[0.5, 0, 0]} castShadow>
          <boxGeometry args={[1, 3, 0.2]} />
          <meshStandardMaterial color="#c62828" />
        </mesh>
        {/* Plataforma */}
        <mesh position={[0, 3, 0]} castShadow>
          <boxGeometry args={[1.5, 0.2, 1.5]} />
          <meshStandardMaterial color="#1565c0" />
        </mesh>
        {/* Rampa */}
        <mesh position={[0, 1.5, 2]} rotation={[-0.6, 0, 0]} castShadow>
          <boxGeometry args={[1, 4, 0.2]} />
          <meshStandardMaterial color="#fbc02d" roughness={0.3} />
        </mesh>
      </group>

      {/* Hamacas / Columpios */}
      <group position={[5, 0, -3]}>
        <mesh position={[-2, 2, 0]} castShadow>
          <cylinderGeometry args={[0.1, 0.1, 4]} />
          <meshStandardMaterial color="#2e7d32" />
        </mesh>
        <mesh position={[2, 2, 0]} castShadow>
          <cylinderGeometry args={[0.1, 0.1, 4]} />
          <meshStandardMaterial color="#2e7d32" />
        </mesh>
        <mesh position={[0, 4, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
          <cylinderGeometry args={[0.1, 0.1, 4.2]} />
          <meshStandardMaterial color="#2e7d32" />
        </mesh>
        {/* Asientos */}
        <mesh position={[-1, 1, 0]} castShadow>
          <boxGeometry args={[0.8, 0.1, 0.4]} />
          <meshStandardMaterial color="#ef6c00" />
        </mesh>
        <mesh position={[1, 1, 0]} castShadow>
          <boxGeometry args={[0.8, 0.1, 0.4]} />
          <meshStandardMaterial color="#ef6c00" />
        </mesh>
      </group>

      {/* Calesita / Merry-go-round */}
      <group position={[0, 0, 3]}>
        <mesh position={[0, 0.6, 0]} castShadow>
          <cylinderGeometry args={[2, 2, 0.2, 16]} />
          <meshStandardMaterial color="#8e24aa" />
        </mesh>
        <mesh position={[0, 1.5, 0]} castShadow>
          <cylinderGeometry args={[0.1, 0.1, 2]} />
          <meshStandardMaterial color="#eeeeee" metalness={0.8} />
        </mesh>
        {/* Agarraderas */}
        <mesh position={[1.5, 1.5, 0]} castShadow>
          <cylinderGeometry args={[0.05, 0.05, 1.5]} />
          <meshStandardMaterial color="#ffeb3b" />
        </mesh>
        <mesh position={[-1.5, 1.5, 0]} castShadow>
          <cylinderGeometry args={[0.05, 0.05, 1.5]} />
          <meshStandardMaterial color="#ffeb3b" />
        </mesh>
        <mesh position={[0, 1.5, 1.5]} castShadow>
          <cylinderGeometry args={[0.05, 0.05, 1.5]} />
          <meshStandardMaterial color="#ffeb3b" />
        </mesh>
        <mesh position={[0, 1.5, -1.5]} castShadow>
          <cylinderGeometry args={[0.05, 0.05, 1.5]} />
          <meshStandardMaterial color="#ffeb3b" />
        </mesh>
      </group>

      {/* Sube y baja / Seesaw */}
      <group position={[-6, 0, 4]}>
        <mesh position={[0, 0.6, 0]} castShadow>
          <cylinderGeometry args={[0.2, 0.3, 1]} />
          <meshStandardMaterial color="#1565c0" />
        </mesh>
        <mesh position={[0, 1.1, 0]} rotation={[0, 0, 0.2]} castShadow>
          <boxGeometry args={[4, 0.1, 0.4]} />
          <meshStandardMaterial color="#d84315" />
        </mesh>
        {/* Asientos */}
        <mesh position={[-1.8, 1.4, 0]} rotation={[0, 0, 0.2]} castShadow>
          <boxGeometry args={[0.4, 0.1, 0.4]} />
          <meshStandardMaterial color="#ffee58" />
        </mesh>
        <mesh position={[1.8, 0.6, 0]} rotation={[0, 0, 0.2]} castShadow>
          <boxGeometry args={[0.4, 0.1, 0.4]} />
          <meshStandardMaterial color="#ffee58" />
        </mesh>
      </group>

      {/* Trepador de red (Cubo) */}
      <group position={[6, 0, 3]}>
        <mesh position={[0, 1.5, 0]} castShadow>
          <boxGeometry args={[3, 3, 3]} />
          <meshStandardMaterial color="#00acc1" wireframe={true} />
        </mesh>
      </group>
    </group>
  );
}
