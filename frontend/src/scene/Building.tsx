import React, { useMemo } from "react";
import * as THREE from "three";

interface BuildingProps {
  position: [number, number, number];
  width: number;
  height: number;
  depth: number;
  color: string;
  rotation?: [number, number, number];
}

export function Building({ position, width, height, depth, color, rotation = [0, 0, 0] }: BuildingProps) {
  const windows = useMemo(() => {
    const arr = [];
    const floors = Math.floor(height / 3);
    const colsX = Math.floor(width / 2.5);
    const colsZ = Math.floor(depth / 2.5);

    // Front (Z = depth/2)
    for (let f = 1; f < floors; f++) {
      for (let c = 0; c < colsX; c++) {
        arr.push({
          pos: [-width / 2 + (c + 0.5) * (width / colsX), 1.5 + f * 3, depth / 2 + 0.05] as [number, number, number],
          size: [1.2, 1.5] as [number, number],
          rot: [0, 0, 0] as [number, number, number],
          on: Math.random() > 0.4
        });
      }
    }
    // Back (Z = -depth/2)
    for (let f = 1; f < floors; f++) {
      for (let c = 0; c < colsX; c++) {
        arr.push({
          pos: [-width / 2 + (c + 0.5) * (width / colsX), 1.5 + f * 3, -depth / 2 - 0.05] as [number, number, number],
          size: [1.2, 1.5] as [number, number],
          rot: [0, Math.PI, 0] as [number, number, number],
          on: Math.random() > 0.4
        });
      }
    }
    // Left (X = -width/2)
    for (let f = 1; f < floors; f++) {
      for (let c = 0; c < colsZ; c++) {
        arr.push({
          pos: [-width / 2 - 0.05, 1.5 + f * 3, -depth / 2 + (c + 0.5) * (depth / colsZ)] as [number, number, number],
          size: [1.2, 1.5] as [number, number],
          rot: [0, -Math.PI / 2, 0] as [number, number, number],
          on: Math.random() > 0.4
        });
      }
    }
    // Right (X = width/2)
    for (let f = 1; f < floors; f++) {
      for (let c = 0; c < colsZ; c++) {
        arr.push({
          pos: [width / 2 + 0.05, 1.5 + f * 3, -depth / 2 + (c + 0.5) * (depth / colsZ)] as [number, number, number],
          size: [1.2, 1.5] as [number, number],
          rot: [0, Math.PI / 2, 0] as [number, number, number],
          on: Math.random() > 0.4
        });
      }
    }
    return arr;
  }, [width, height, depth]);

  return (
    <group position={position} rotation={rotation}>
      <mesh castShadow receiveShadow position={[0, height / 2, 0]}>
        <boxGeometry args={[width, height, depth]} />
        <meshStandardMaterial color={color} roughness={0.6} metalness={0.1} polygonOffset polygonOffsetFactor={1} polygonOffsetUnits={1} />
      </mesh>
      
      {/* Ventanas */}
      {windows.map((w, i) => (
        <mesh 
          key={i} 
          position={w.pos} 
          rotation={w.rot}
        >
          <planeGeometry args={[w.size[0], w.size[1]]} />
          <meshStandardMaterial 
            color={w.on ? "#ffffff" : "#111122"} 
            emissive={w.on ? "#ffffee" : "#000000"} 
            emissiveIntensity={w.on ? 1.5 : 0} 
            roughness={0.1}
            polygonOffset
            polygonOffsetFactor={-1}
            polygonOffsetUnits={-1}
          />
        </mesh>
      ))}
    </group>
  );
}
