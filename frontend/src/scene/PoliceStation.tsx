import React from "react";

interface PoliceStationProps {
  position: [number, number, number];
  rotation?: [number, number, number];
}

export function PoliceStation({ position, rotation = [0, 0, 0] }: PoliceStationProps) {
  return (
    <group position={position} rotation={rotation}>
      {/* Edificio principal (Gris Oscuro/Azul) */}
      <mesh position={[0, 5, 0]} castShadow receiveShadow>
        <boxGeometry args={[10, 10, 8]} />
        <meshStandardMaterial color="#2b3b4b" roughness={0.7} />
      </mesh>
      
      {/* Franja Azul y Blanca identificadora */}
      <mesh position={[0, 7.5, 4.05]}>
        <planeGeometry args={[10, 1]} />
        <meshStandardMaterial color="#0055ff" />
      </mesh>
      <mesh position={[0, 8.5, 4.05]}>
        <planeGeometry args={[10, 0.5]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>

      {/* Cartel "POLICE" simulado */}
      <mesh position={[0, 8, 4.1]}>
        <boxGeometry args={[4, 1.5, 0.2]} />
        <meshStandardMaterial color="#112233" />
      </mesh>

      {/* Sirenas en el techo */}
      <group position={[0, 10.2, 3]}>
        {/* Sirena Azul */}
        <mesh position={[-1.5, 0, 0]}>
          <cylinderGeometry args={[0.3, 0.3, 0.5, 8]} />
          <meshStandardMaterial color="#0044ff" emissive="#0044ff" emissiveIntensity={1} />
        </mesh>
        {/* Sirena Roja */}
        <mesh position={[1.5, 0, 0]}>
          <cylinderGeometry args={[0.3, 0.3, 0.5, 8]} />
          <meshStandardMaterial color="#ff0000" emissive="#ff0000" emissiveIntensity={1} />
        </mesh>
        <mesh position={[0, -0.1, 0]}>
          <boxGeometry args={[4, 0.2, 0.8]} />
          <meshStandardMaterial color="#333" />
        </mesh>
      </group>

      {/* Antena de Radio */}
      <mesh position={[-3, 12, -2]}>
        <cylinderGeometry args={[0.05, 0.05, 4]} />
        <meshStandardMaterial color="#aaaaaa" />
      </mesh>

      {/* Entrada */}
      <mesh position={[0, 1.5, 4.01]}>
        <planeGeometry args={[2, 3]} />
        <meshStandardMaterial color="#111111" />
      </mesh>
    </group>
  );
}
