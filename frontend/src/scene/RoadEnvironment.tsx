import React, { useMemo } from "react";
import * as THREE from "three";
import { Building } from "./Building";
import { Hospital } from "./Hospital";
import { PoliceStation } from "./PoliceStation";
import { Store, GasStation } from "./StoreAndGasStation";
import { FireStation, Bank, FoodShop } from "./CityBuildings";
import { Cinema, School, OfficeTower, Supermarket } from "./MoreBuildings";
import { Church, Pharmacy, Hotel, RadioTower, ParkFountain, StreetLamp, Playground } from "./ExtraBuildings";

function Tree({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh position={[0, 1.5, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[0.3, 0.4, 3, 8]} />
        <meshStandardMaterial color="#5c4033" roughness={0.9} />
      </mesh>
      <mesh position={[0, 4, 0]} castShadow receiveShadow>
        <coneGeometry args={[2, 3, 8]} />
        <meshStandardMaterial color="#2d5a27" roughness={0.8} />
      </mesh>
      <mesh position={[0, 5.5, 0]} castShadow receiveShadow>
        <coneGeometry args={[1.5, 2.5, 8]} />
        <meshStandardMaterial color="#3a7033" roughness={0.8} />
      </mesh>
    </group>
  );
}

export const parkSize = 75; 
export const roadWidth = 20; 
export const buildingEdge = parkSize + roadWidth / 2 + 12; // ~ moved further from the road

export const playgrounds: [number, number, number][] = [
  [22, 0, 0],     // Cerca de la fuente
  [-40, 0, -40],  // Esquina superior izquierda
  [40, 0, 40],    // Esquina inferior derecha
  [-40, 0, 40],   // Esquina inferior izquierda
  [40, 0, -40]    // Esquina superior derecha
];

export const treePositions: [number, number, number][] = [];
// Parque central (pocos)
for (let i = 0; i < 20; i++) { // Aumenté un poco los árboles
  let tx = 0, tz = 0, valid = false;
  let attempts = 0;
  while (!valid && attempts < 50) {
    tx = (Math.random() * (parkSize * 2 - 30)) - (parkSize - 15);
    tz = (Math.random() * (parkSize * 2 - 30)) - (parkSize - 15);
    
    // Evitar fuente central
    let isSafe = Math.sqrt(tx * tx + tz * tz) > 25;
    
    // Evitar todos los playgrounds
    if (isSafe) {
      for (const pg of playgrounds) {
        const dx = tx - pg[0];
        const dz = tz - pg[2];
        if (Math.sqrt(dx * dx + dz * dz) < 18) {
          isSafe = false;
          break;
        }
      }
    }
    
    if (isSafe) {
      valid = true;
    }
    attempts++;
  }
  if (valid) treePositions.push([tx, 0, tz]);
}
// Afuera de los edificios (muchos - verde a los costados)
for (let i = 0; i < 300; i++) {
  const angle = Math.random() * Math.PI * 2;
  // Empujar atrás de la segunda fila de edificios (buildingEdge + 55)
  const radius = buildingEdge + 55 + Math.random() * 120;
  treePositions.push([Math.cos(angle) * radius, 0, Math.sin(angle) * radius]);
}

export function RoadEnvironment() {

  // Faroles a lo largo de la carretera
  const lamps = useMemo(() => {
    const arr = [];
    const innerEdge = parkSize - roadWidth / 2 - 1;
    const outerEdge = parkSize + roadWidth / 2 + 1;
    // Evitar intersecciones
    for (let i = -parkSize + roadWidth / 2 + 5; i <= parkSize - roadWidth / 2 - 5; i += 15) {
      // Interior del circuito
      arr.push([innerEdge, 0, i] as [number, number, number]);
      arr.push([-innerEdge, 0, i] as [number, number, number]);
      arr.push([i, 0, innerEdge] as [number, number, number]);
      arr.push([i, 0, -innerEdge] as [number, number, number]);
      // Exterior del circuito
      arr.push([outerEdge, 0, i] as [number, number, number]);
      arr.push([-outerEdge, 0, i] as [number, number, number]);
      arr.push([i, 0, outerEdge] as [number, number, number]);
      arr.push([i, 0, -outerEdge] as [number, number, number]);
    }
    return arr;
  }, []);

  // Líneas amarillas punteadas
  const lines = useMemo(() => {
    const arr = [];
    const step = 6;
    const half = parkSize;
    for (let i = -half; i < half; i += step) {
      arr.push({ pos: [parkSize, 0.01, i] as [number, number, number], rot: [-Math.PI / 2, 0, 0] as [number, number, number] });
      arr.push({ pos: [-parkSize, 0.01, i] as [number, number, number], rot: [-Math.PI / 2, 0, 0] as [number, number, number] });
      arr.push({ pos: [i, 0.01, -parkSize] as [number, number, number], rot: [-Math.PI / 2, 0, Math.PI / 2] as [number, number, number] });
      arr.push({ pos: [i, 0.01, parkSize] as [number, number, number], rot: [-Math.PI / 2, 0, Math.PI / 2] as [number, number, number] });
    }
    return arr;
  }, []);

  const groundSize = buildingEdge * 2 + 500; // Suficientemente grande para los árboles de afuera

  return (
    <group>
      {/* Suelo verde bien extendido */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[0, -0.1, 0]}>
        <planeGeometry args={[groundSize, groundSize]} />
        <meshStandardMaterial color="#4a7c36" roughness={1} polygonOffset polygonOffsetFactor={2} polygonOffsetUnits={2} />
      </mesh>

      {/* --- CARRETERAS --- */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[-parkSize, 0.01, 0]}>
        <planeGeometry args={[roadWidth, parkSize * 2 + roadWidth]} />
        <meshStandardMaterial color="#555555" roughness={0.8} polygonOffset polygonOffsetFactor={1} polygonOffsetUnits={1} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[parkSize, 0.01, 0]}>
        <planeGeometry args={[roadWidth, parkSize * 2 + roadWidth]} />
        <meshStandardMaterial color="#555555" roughness={0.8} polygonOffset polygonOffsetFactor={1} polygonOffsetUnits={1} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[0, 0.01, -parkSize]}>
        <planeGeometry args={[parkSize * 2 - roadWidth, roadWidth]} />
        <meshStandardMaterial color="#555555" roughness={0.8} polygonOffset polygonOffsetFactor={1} polygonOffsetUnits={1} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[0, 0.01, parkSize]}>
        <planeGeometry args={[parkSize * 2 - roadWidth, roadWidth]} />
        <meshStandardMaterial color="#555555" roughness={0.8} polygonOffset polygonOffsetFactor={1} polygonOffsetUnits={1} />
      </mesh>

      {/* Líneas amarillas */}
      {lines.map((l, i) => (
        <mesh key={`line-${i}`} position={[l.pos[0], 0.05, l.pos[2]]} rotation={l.rot}>
          <planeGeometry args={[0.4, 3]} />
          <meshStandardMaterial color="#dddd44" emissive="#bbbb11" roughness={0.4} polygonOffset polygonOffsetFactor={-1} polygonOffsetUnits={-1} />
        </mesh>
      ))}

      {/* Faroles de calle */}
      {lamps.map((pos, i) => (
        <StreetLamp key={`lamp-${i}`} position={pos} />
      ))}

      {/* Árboles */}
      {treePositions.map((pos, i) => (
        <Tree key={`tree-${i}`} position={pos} />
      ))}

      {/* Fuente en el centro del parque */}
      <ParkFountain position={[0, 0, 0]} />

      {/* Juegos esparcidos por el parque */}
      {playgrounds.map((pos, i) => (
        <Playground key={`pg-${i}`} position={pos} />
      ))}

      {/* ============================================================ */}
      {/* === EDIFICIOS TEMÁTICOS REALISTAS EN TODA LA CARRETERA === */}
      {/* ============================================================ */}
      
      {/* -- Borde DERECHO (X = +buildingEdge), mirando al parque -- */}
      <FoodShop position={[buildingEdge, 0, -72]} rotation={[0, -Math.PI / 2, 0]} />
      <Hospital position={[buildingEdge, 0, -54]} rotation={[0, -Math.PI / 2, 0]} />
      <Pharmacy position={[buildingEdge, 0, -36]} rotation={[0, -Math.PI / 2, 0]} />
      <OfficeTower position={[buildingEdge, 0, -18]} rotation={[0, -Math.PI / 2, 0]} />
      <GasStation position={[buildingEdge, 0, 0]} rotation={[0, -Math.PI / 2, 0]} />
      <Bank position={[buildingEdge, 0, 18]} rotation={[0, -Math.PI / 2, 0]} />
      <Hotel position={[buildingEdge, 0, 36]} rotation={[0, -Math.PI / 2, 0]} />
      <FireStation position={[buildingEdge, 0, 54]} rotation={[0, -Math.PI / 2, 0]} />
      <Store position={[buildingEdge, 0, 72]} rotation={[0, -Math.PI / 2, 0]} color="#7755aa" />

      {/* -- Borde IZQUIERDO (X = -buildingEdge), mirando al parque -- */}
      <Bank position={[-buildingEdge, 0, -72]} rotation={[0, Math.PI / 2, 0]} />
      <Supermarket position={[-buildingEdge, 0, -54]} rotation={[0, Math.PI / 2, 0]} />
      <RadioTower position={[-buildingEdge, 0, -36]} rotation={[0, Math.PI / 2, 0]} />
      <PoliceStation position={[-buildingEdge, 0, -18]} rotation={[0, Math.PI / 2, 0]} />
      <Cinema position={[-buildingEdge, 0, 0]} rotation={[0, Math.PI / 2, 0]} />
      <Store position={[-buildingEdge, 0, 18]} rotation={[0, Math.PI / 2, 0]} color="#d4a373" />
      <Church position={[-buildingEdge, 0, 36]} rotation={[0, Math.PI / 2, 0]} />
      <FoodShop position={[-buildingEdge, 0, 54]} rotation={[0, Math.PI / 2, 0]} />
      <OfficeTower position={[-buildingEdge, 0, 72]} rotation={[0, Math.PI / 2, 0]} />

      {/* -- Borde SUPERIOR (Z = -buildingEdge), mirando al parque -- */}
      <Cinema position={[-72, 0, -buildingEdge]} rotation={[0, 0, 0]} />
      <School position={[-54, 0, -buildingEdge]} rotation={[0, 0, 0]} />
      <Store position={[-36, 0, -buildingEdge]} rotation={[0, 0, 0]} color="#aa5577" />
      <Pharmacy position={[-18, 0, -buildingEdge]} rotation={[0, 0, 0]} />
      <Bank position={[0, 0, -buildingEdge]} rotation={[0, 0, 0]} />
      <OfficeTower position={[18, 0, -buildingEdge]} rotation={[0, 0, 0]} />
      <Hotel position={[36, 0, -buildingEdge]} rotation={[0, 0, 0]} />
      <GasStation position={[54, 0, -buildingEdge]} rotation={[0, 0, 0]} />
      <FireStation position={[72, 0, -buildingEdge]} rotation={[0, 0, 0]} />

      {/* -- Borde INFERIOR (Z = +buildingEdge), mirando al parque -- */}
      <Hotel position={[-72, 0, buildingEdge]} rotation={[0, Math.PI, 0]} />
      <Church position={[-54, 0, buildingEdge]} rotation={[0, Math.PI, 0]} />
      <FireStation position={[-36, 0, buildingEdge]} rotation={[0, Math.PI, 0]} />
      <Cinema position={[-18, 0, buildingEdge]} rotation={[0, Math.PI, 0]} />
      <Supermarket position={[0, 0, buildingEdge]} rotation={[0, Math.PI, 0]} />
      <RadioTower position={[18, 0, buildingEdge]} rotation={[0, Math.PI, 0]} />
      <Hospital position={[36, 0, buildingEdge]} rotation={[0, Math.PI, 0]} />
      <OfficeTower position={[54, 0, buildingEdge]} rotation={[0, Math.PI, 0]} />
      <Store position={[72, 0, buildingEdge]} rotation={[0, Math.PI, 0]} color="#55aa77" />

      {/* ============================================================ */}
      {/* === ESQUINAS (En diagonal hacia el cruce) === */}
      {/* ============================================================ */}
      <Hospital position={[buildingEdge, 0, buildingEdge]} rotation={[0, Math.PI / 4, 0]} />
      <OfficeTower position={[-buildingEdge, 0, buildingEdge]} rotation={[0, -Math.PI / 4, 0]} />
      <Cinema position={[buildingEdge, 0, -buildingEdge]} rotation={[0, Math.PI * 3 / 4, 0]} />
      <Supermarket position={[-buildingEdge, 0, -buildingEdge]} rotation={[0, -Math.PI * 3 / 4, 0]} />

      {/* ============================================================ */}
      {/* === SEGUNDA FILA DE EDIFICIOS (EXTERIOR) === */}
      {/* ============================================================ */}
      {/* Borde DERECHO Exterior */}
      <Bank position={[buildingEdge + 35, 0, -72]} rotation={[0, -Math.PI / 2, 0]} />
      <Cinema position={[buildingEdge + 35, 0, -54]} rotation={[0, -Math.PI / 2, 0]} />
      <Church position={[buildingEdge + 35, 0, -36]} rotation={[0, -Math.PI / 2, 0]} />
      <Supermarket position={[buildingEdge + 35, 0, -18]} rotation={[0, -Math.PI / 2, 0]} />
      <School position={[buildingEdge + 35, 0, 0]} rotation={[0, -Math.PI / 2, 0]} />
      <Pharmacy position={[buildingEdge + 35, 0, 18]} rotation={[0, -Math.PI / 2, 0]} />
      <OfficeTower position={[buildingEdge + 35, 0, 36]} rotation={[0, -Math.PI / 2, 0]} />
      <PoliceStation position={[buildingEdge + 35, 0, 54]} rotation={[0, -Math.PI / 2, 0]} />
      <FoodShop position={[buildingEdge + 35, 0, 72]} rotation={[0, -Math.PI / 2, 0]} />

      {/* Borde IZQUIERDO Exterior */}
      <Hotel position={[-(buildingEdge + 35), 0, -72]} rotation={[0, Math.PI / 2, 0]} />
      <FireStation position={[-(buildingEdge + 35), 0, -54]} rotation={[0, Math.PI / 2, 0]} />
      <Bank position={[-(buildingEdge + 35), 0, -36]} rotation={[0, Math.PI / 2, 0]} />
      <School position={[-(buildingEdge + 35), 0, -18]} rotation={[0, Math.PI / 2, 0]} />
      <RadioTower position={[-(buildingEdge + 35), 0, 0]} rotation={[0, Math.PI / 2, 0]} />
      <Hospital position={[-(buildingEdge + 35), 0, 18]} rotation={[0, Math.PI / 2, 0]} />
      <Cinema position={[-(buildingEdge + 35), 0, 36]} rotation={[0, Math.PI / 2, 0]} />
      <Pharmacy position={[-(buildingEdge + 35), 0, 54]} rotation={[0, Math.PI / 2, 0]} />
      <OfficeTower position={[-(buildingEdge + 35), 0, 72]} rotation={[0, Math.PI / 2, 0]} />

      {/* Borde SUPERIOR Exterior */}
      <Supermarket position={[-72, 0, -(buildingEdge + 35)]} rotation={[0, 0, 0]} />
      <Church position={[-54, 0, -(buildingEdge + 35)]} rotation={[0, 0, 0]} />
      <PoliceStation position={[-36, 0, -(buildingEdge + 35)]} rotation={[0, 0, 0]} />
      <OfficeTower position={[-18, 0, -(buildingEdge + 35)]} rotation={[0, 0, 0]} />
      <Hotel position={[0, 0, -(buildingEdge + 35)]} rotation={[0, 0, 0]} />
      <Pharmacy position={[18, 0, -(buildingEdge + 35)]} rotation={[0, 0, 0]} />
      <Cinema position={[36, 0, -(buildingEdge + 35)]} rotation={[0, 0, 0]} />
      <Bank position={[54, 0, -(buildingEdge + 35)]} rotation={[0, 0, 0]} />
      <FoodShop position={[72, 0, -(buildingEdge + 35)]} rotation={[0, 0, 0]} />

      {/* Borde INFERIOR Exterior */}
      <School position={[-72, 0, buildingEdge + 35]} rotation={[0, Math.PI, 0]} />
      <Pharmacy position={[-54, 0, buildingEdge + 35]} rotation={[0, Math.PI, 0]} />
      <RadioTower position={[-36, 0, buildingEdge + 35]} rotation={[0, Math.PI, 0]} />
      <Supermarket position={[-18, 0, buildingEdge + 35]} rotation={[0, Math.PI, 0]} />
      <Bank position={[0, 0, buildingEdge + 35]} rotation={[0, Math.PI, 0]} />
      <Cinema position={[18, 0, buildingEdge + 35]} rotation={[0, Math.PI, 0]} />
      <Church position={[36, 0, buildingEdge + 35]} rotation={[0, Math.PI, 0]} />
      <Hotel position={[54, 0, buildingEdge + 35]} rotation={[0, Math.PI, 0]} />
      <OfficeTower position={[72, 0, buildingEdge + 35]} rotation={[0, Math.PI, 0]} />

    </group>
  );
}
