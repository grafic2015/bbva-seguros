import React from "react";

export function Store({ position, rotation = [0, 0, 0], color = "#d4a373" }: { position: [number, number, number], rotation?: [number, number, number], color?: string }) {
  return (
    <group position={position} rotation={rotation}>
      <mesh position={[0, 3, 0]} castShadow receiveShadow>
        <boxGeometry args={[8, 6, 8]} />
        <meshStandardMaterial color={color} roughness={0.8} />
      </mesh>
      
      {/* Toldo */}
      <mesh position={[0, 4, 4.5]} rotation={[Math.PI / 6, 0, 0]} castShadow>
        <boxGeometry args={[6, 2, 0.2]} />
        <meshStandardMaterial color="#e63946" />
      </mesh>

      {/* Vidriera */}
      <mesh position={[0, 1.5, 4.1]}>
        <planeGeometry args={[6, 3]} />
        <meshStandardMaterial color="#aaddff" />
      </mesh>
    </group>
  );
}

export function GasStation({ position, rotation = [0, 0, 0] }: { position: [number, number, number], rotation?: [number, number, number] }) {
  return (
    <group position={position} rotation={rotation}>
      {/* Piso / Plataforma */}
      <mesh position={[0, 0.1, 0]} receiveShadow>
        <boxGeometry args={[12, 0.2, 8]} />
        <meshStandardMaterial color="#aaaaaa" />
      </mesh>

      {/* Pilares */}
      <mesh position={[-5, 3, 0]} castShadow>
        <boxGeometry args={[0.5, 6, 0.5]} />
        <meshStandardMaterial color="#ffaa00" />
      </mesh>
      <mesh position={[5, 3, 0]} castShadow>
        <boxGeometry args={[0.5, 6, 0.5]} />
        <meshStandardMaterial color="#ffaa00" />
      </mesh>

      {/* Techo */}
      <mesh position={[0, 6.2, 0]} castShadow receiveShadow>
        <boxGeometry args={[14, 0.5, 10]} />
        <meshStandardMaterial color="#fefefe" />
      </mesh>

      {/* Surtidores */}
      <mesh position={[-2, 1, 0]} castShadow>
        <boxGeometry args={[1, 2, 1]} />
        <meshStandardMaterial color="#2255aa" />
      </mesh>
      <mesh position={[2, 1, 0]} castShadow>
        <boxGeometry args={[1, 2, 1]} />
        <meshStandardMaterial color="#2255aa" />
      </mesh>
    </group>
  );
}
