import React from "react";

interface Props {
  position: [number, number, number];
  rotation?: [number, number, number];
}

export function FireStation({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      {/* Edificio principal rojo */}
      <mesh position={[0, 4, 0]} castShadow receiveShadow>
        <boxGeometry args={[12, 8, 8]} />
        <meshStandardMaterial color="#c42b2b" roughness={0.7} />
      </mesh>
      
      {/* Portón de garaje gigante (para el camión) */}
      <mesh position={[-2, 2.5, 4.15]}>
        <planeGeometry args={[5, 5]} />
        <meshStandardMaterial color="#666666" />
      </mesh>
      
      {/* Puerta peatonal */}
      <mesh position={[4, 1.5, 4.1]}>
        <planeGeometry args={[1.5, 3]} />
        <meshStandardMaterial color="#222" />
      </mesh>

      {/* Torre de mangueras (clásico en estaciones antiguas) */}
      <mesh position={[4, 9, -2]} castShadow>
        <boxGeometry args={[3, 10, 3]} />
        <meshStandardMaterial color="#b22222" roughness={0.8} />
      </mesh>
      {/* Sirena en la torre */}
      <mesh position={[4, 14.5, -2]}>
        <cylinderGeometry args={[0.4, 0.4, 0.8, 8]} />
        <meshStandardMaterial color="#ffcc00" emissive="#ffaa00" emissiveIntensity={0.8} />
      </mesh>
      
      {/* Cartel Superior */}
      <mesh position={[0, 8.5, 4.0]}>
        <boxGeometry args={[6, 1, 0.2]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>
    </group>
  );
}

export function Bank({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      {/* Edificio principal (Piedra/Mármol) */}
      <mesh position={[0, 6, 0]} castShadow receiveShadow>
        <boxGeometry args={[10, 12, 10]} />
        <meshStandardMaterial color="#e0e0d5" roughness={0.4} />
      </mesh>
      
      {/* Base escalonada */}
      <mesh position={[0, 0.25, 5.5]} receiveShadow>
        <boxGeometry args={[12, 0.5, 3]} />
        <meshStandardMaterial color="#ccccc0" />
      </mesh>

      {/* Columnas clásicas (Estilo griego/romano) */}
      {[-3.5, -1.5, 0.5, 2.5].map((x, i) => (
        <mesh key={i} position={[x, 3.5, 6]} castShadow>
          <cylinderGeometry args={[0.4, 0.4, 6, 16]} />
          <meshStandardMaterial color="#f0f0e5" />
        </mesh>
      ))}

      {/* Techo del pórtico (Triangular) */}
      <mesh position={[-0.5, 7.5, 6]} rotation={[0, 0, 0]} castShadow>
        {/* Usamos un cono achatado o un prisma para el tímpano */}
        <cylinderGeometry args={[5, 5, 2, 3]} />
        {/* Hack: un cilindro triangular rotado para hacer el techo a dos aguas */}
        <meshStandardMaterial color="#d0d0c5" />
      </mesh>
      
      {/* Puertas blindadas */}
      <mesh position={[-0.5, 2, 4.1]}>
        <planeGeometry args={[3, 4]} />
        <meshStandardMaterial color="#b8860b" metalness={0.8} roughness={0.2} /> {/* Dorado/Bronce */}
      </mesh>
    </group>
  );
}

export function FoodShop({ position, rotation = [0, 0, 0] }: Props) {
  return (
    <group position={position} rotation={rotation}>
      <mesh position={[0, 3, 0]} castShadow receiveShadow>
        <boxGeometry args={[8, 6, 8]} />
        <meshStandardMaterial color="#fff" roughness={0.9} />
      </mesh>
      
      {/* Franja de color superior (Rojo/Amarillo típico de comida rápida) */}
      <mesh position={[0, 5.5, 4.15]}>
        <planeGeometry args={[8, 1]} />
        <meshStandardMaterial color="#d92222" />
      </mesh>
      
      {/* Cartel Gigante en el techo (Burger/Dona) */}
      <mesh position={[0, 8, 0]} rotation={[Math.PI/2, 0, 0]} castShadow>
        <torusGeometry args={[1.5, 0.5, 16, 32]} />
        <meshStandardMaterial color="#f4a460" /> {/* Color dona/pan */}
      </mesh>

      <mesh position={[0, 1.5, 4.1]}>
        <planeGeometry args={[6, 3]} />
        <meshStandardMaterial color="#222" /> {/* Vidrio oscuro */}
      </mesh>
    </group>
  );
}
