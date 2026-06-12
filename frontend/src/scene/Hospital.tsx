import React from "react";

interface HospitalProps {
  position: [number, number, number];
  rotation?: [number, number, number];
}

export function Hospital({ position, rotation = [0, 0, 0] }: HospitalProps) {
  return (
    <group position={position} rotation={rotation}>
      {/* Base / Edificio Principal (Color Blanco) */}
      <mesh position={[0, 6, 0]} castShadow receiveShadow>
        <boxGeometry args={[12, 12, 10]} />
        <meshStandardMaterial color="#f8f9fa" roughness={0.6} />
      </mesh>
      
      {/* Entrada (Toldo) */}
      <mesh position={[0, 2, 5.5]} castShadow receiveShadow>
        <boxGeometry args={[4, 1, 3]} />
        <meshStandardMaterial color="#2255aa" roughness={0.8} />
      </mesh>
      {/* Pilares Entrada */}
      <mesh position={[-1.5, 1, 6.5]} castShadow receiveShadow>
        <cylinderGeometry args={[0.2, 0.2, 2]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>
      <mesh position={[1.5, 1, 6.5]} castShadow receiveShadow>
        <cylinderGeometry args={[0.2, 0.2, 2]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>

      {/* Cruz Roja Frontal */}
      <group position={[0, 8, 5.1]}>
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[1, 3, 0.2]} />
          <meshStandardMaterial color="#d92222" emissive="#d92222" emissiveIntensity={0.3} />
        </mesh>
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[3, 1, 0.2]} />
          <meshStandardMaterial color="#d92222" emissive="#d92222" emissiveIntensity={0.3} />
        </mesh>
      </group>

      {/* Cruz Roja Techo (Helipuerto o indicación) */}
      <group position={[0, 12.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <mesh position={[0, 0, 0]}>
          <planeGeometry args={[1, 3]} />
          <meshStandardMaterial color="#d92222" />
        </mesh>
        <mesh position={[0, 0, 0]}>
          <planeGeometry args={[3, 1]} />
          <meshStandardMaterial color="#d92222" />
        </mesh>
        <mesh position={[0, 0, -0.01]}>
          <planeGeometry args={[5, 5]} />
          <meshStandardMaterial color="#dddddd" />
        </mesh>
      </group>

      {/* Ventanas Laterales y Frontales */}
      {Array.from({ length: 3 }).map((_, floor) => (
        <group key={floor} position={[0, 4 + floor * 2.5, 0]}>
          <mesh position={[-3, 0, 5.05]}>
             <planeGeometry args={[1.5, 1.2]} />
             <meshStandardMaterial color="#aaddff" />
          </mesh>
          <mesh position={[3, 0, 5.05]}>
             <planeGeometry args={[1.5, 1.2]} />
             <meshStandardMaterial color="#aaddff" />
          </mesh>
        </group>
      ))}
    </group>
  );
}
