import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import { RoadEnvironment } from "./RoadEnvironment";
import { Car, ROAD_WAYPOINTS_OUTER, ROAD_WAYPOINTS_INNER } from "./Car";
import { useStore } from "../store";
import { AGENT_META } from "../types";

function Loader() {
  return (
    <Html center>
      <div style={{ color: "#8b949e", fontSize: 13 }}>Cargando ciudad...</div>
    </Html>
  );
}

export function Scene() {
  const agents = useStore((s) => s.agents);

  const instagramAgent = agents.instagram;
  const leadsAgent     = agents.leads;

  return (
    <Canvas shadows camera={{ position: [0, 30, 45], fov: 50, near: 1, far: 1000 }}>
      <color attach="background" args={["#87ceeb"]} />

      <ambientLight intensity={0.6} />
      <directionalLight
        position={[50, 100, 50]}
        intensity={1.5}
        color="#ffffff"
        castShadow
        shadow-mapSize={[4096, 4096]}
        shadow-camera-left={-200}
        shadow-camera-right={200}
        shadow-camera-top={200}
        shadow-camera-bottom={-200}
        shadow-bias={-0.001}
      />

      {/* Entorno Urbano */}
      <RoadEnvironment />

      {/* Autos con agentes vinculados */}
      <Suspense fallback={<Loader />}>
        {/* Auto Rojo → Instagram Monitor Agent | Flechas del teclado */}
        <Car
          initialPosition={ROAD_WAYPOINTS_OUTER[0]}
          color="#d9381e"
          controls="arrows"
          agentName={AGENT_META.instagram.name}
          agentStatus={instagramAgent?.status}
          agentColor={AGENT_META.instagram.color}
          waypoints={ROAD_WAYPOINTS_OUTER}
        />

        {/* Auto Azul → Leads Manager Agent | WASD */}
        <Car
          initialPosition={ROAD_WAYPOINTS_INNER[0]}
          color="#1e5bd9"
          controls="wasd"
          agentName={AGENT_META.leads.name}
          agentStatus={leadsAgent?.status}
          agentColor={AGENT_META.leads.color}
          waypoints={ROAD_WAYPOINTS_INNER}
        />
      </Suspense>

      <OrbitControls
        target={[0, 2, 0]}
        enablePan={true}
        minDistance={5}
        maxDistance={500}
        maxPolarAngle={Math.PI / 2 - 0.02}
      />
    </Canvas>
  );
}
