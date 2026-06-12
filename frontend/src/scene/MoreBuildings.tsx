import React from "react";

interface Props {
  position: [number, number, number];
  rotation?: [number, number, number];
}

export function Cinema({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      {/* Edificio principal - Beige/Crema */}
      <mesh position={[0, 6, 0]} castShadow receiveShadow>
        <boxGeometry args={[14, 12, 10]} />
        <meshStandardMaterial color="#e8d5b7" roughness={0.7} />
      </mesh>
      
      {/* Marquesina Azul brillante */}
      <mesh position={[0, 5, 5.1]} castShadow>
        <boxGeometry args={[12, 3, 1]} />
        <meshStandardMaterial color="#2255aa" emissive="#1133aa" emissiveIntensity={0.4} />
      </mesh>
      {/* Pantalla / Cartel luminoso */}
      <mesh position={[0, 5, 5.7]}>
        <planeGeometry args={[10, 2]} />
        <meshStandardMaterial color="#ffffff" emissive="#eeeeff" emissiveIntensity={0.8} />
      </mesh>
      
      {/* Luces decorativas */}
      {[-4, -2, 0, 2, 4].map((x, i) => (
        <mesh key={i} position={[x, 7, 5.1]}>
          <sphereGeometry args={[0.3, 8, 8]} />
          <meshStandardMaterial color="#ffcc44" emissive="#ffcc44" emissiveIntensity={0.8} />
        </mesh>
      ))}

      {/* Entrada con puertas de vidrio */}
      <mesh position={[0, 1.5, 5.1]}>
        <planeGeometry args={[6, 3]} />
        <meshStandardMaterial color="#88bbdd" opacity={0.7} transparent />
      </mesh>
    </group>
  );
}

export function School({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      <mesh position={[0, 4, 0]} castShadow receiveShadow>
        <boxGeometry args={[16, 8, 8]} />
        <meshStandardMaterial color="#e8a87c" roughness={0.8} /> {/* Ladrillo claro */}
      </mesh>
      
      {/* Reloj en el centro superior */}
      <mesh position={[0, 7.5, 4.1]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[1.5, 1.5, 0.2, 16]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>
      <mesh position={[0, 7.5, 4.2]}>
        <boxGeometry args={[0.1, 1, 0.05]} />
        <meshStandardMaterial color="#000" />
      </mesh>

      {/* Ventanas típicas de colegio */}
      {[-5, -2, 2, 5].map((x, i) => (
        <group key={i}>
          <mesh position={[x, 2, 4.1]}>
            <planeGeometry args={[2, 1.5]} />
            <meshStandardMaterial color="#88ccff" />
          </mesh>
          <mesh position={[x, 5, 4.1]}>
            <planeGeometry args={[2, 1.5]} />
            <meshStandardMaterial color="#88ccff" />
          </mesh>
        </group>
      ))}

      {/* Asta de bandera */}
      <mesh position={[-6, 4, 6]} castShadow>
        <cylinderGeometry args={[0.05, 0.05, 8]} />
        <meshStandardMaterial color="#cccccc" />
      </mesh>
      <mesh position={[-5.3, 7, 6]} castShadow>
        <planeGeometry args={[1.5, 1]} />
        <meshStandardMaterial color="#0055ff" /> {/* Simula una bandera estática */}
      </mesh>
    </group>
  );
}

export function OfficeTower({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      {/* Rascacielos moderno - Cristal celeste/plateado */}
      <mesh position={[0, 15, 0]} castShadow receiveShadow>
        <boxGeometry args={[10, 30, 10]} />
        <meshStandardMaterial color="#7ca8c4" roughness={0.15} metalness={0.6} />
      </mesh>

      {/* Franjas horizontales blancas (pisos) */}
      {[3, 7, 11, 15, 19, 23, 27].map((y, i) => (
        <mesh key={i} position={[0, y, 0]}>
          <boxGeometry args={[10.1, 0.15, 10.1]} />
          <meshStandardMaterial color="#e0e8f0" />
        </mesh>
      ))}

      {/* Coronamiento superior */}
      <mesh position={[0, 30.1, 0]}>
        <boxGeometry args={[10.2, 0.4, 10.2]} />
        <meshStandardMaterial color="#c0c8d0" metalness={0.5} roughness={0.3} />
      </mesh>

      {/* Helipuerto en el techo */}
      <mesh position={[0, 30.5, 0]}>
        <cylinderGeometry args={[3, 3, 0.1, 16]} />
        <meshStandardMaterial color="#888888" />
      </mesh>
      <mesh position={[0, 30.56, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[2, 2]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>
    </group>
  );
}

export function Supermarket({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      <mesh position={[0, 4, 0]} castShadow receiveShadow>
        <boxGeometry args={[20, 8, 12]} />
        <meshStandardMaterial color="#ffffff" roughness={0.7} />
      </mesh>
      
      {/* Franja verde corporativa típica */}
      <mesh position={[0, 6, 6.1]}>
        <planeGeometry args={[20, 1.5]} />
        <meshStandardMaterial color="#22aa44" />
      </mesh>

      {/* Letras simuladas / Logo */}
      <mesh position={[0, 6, 6.15]}>
        <boxGeometry args={[6, 0.8, 0.1]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>

      {/* Puertas corredizas automáticas */}
      <mesh position={[0, 2, 6.1]}>
        <planeGeometry args={[4, 4]} />
        <meshStandardMaterial color="#aaddff" opacity={0.6} transparent />
      </mesh>
      
      {/* Algunos detalles de pósters */}
      <mesh position={[-6, 3, 6.1]}>
        <planeGeometry args={[2, 3]} />
        <meshStandardMaterial color="#ffaa00" />
      </mesh>
      <mesh position={[6, 3, 6.1]}>
        <planeGeometry args={[2, 3]} />
        <meshStandardMaterial color="#ff4444" />
      </mesh>
    </group>
  );
}
