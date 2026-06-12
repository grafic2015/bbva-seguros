import { useEffect, useMemo, useRef, useCallback } from "react";
import { useFrame } from "@react-three/fiber";
import { useGLTF, Html } from "@react-three/drei";
import { SkeletonUtils } from "three-stdlib";
import * as THREE from "three";
import type { AgentId, ActivityType } from "../types";
import { AGENT_META } from "../types";
import { useStore } from "../store";
import { useAgentMovement } from "../hooks/useAgentMovement";
import { keysPressed } from "../utils/keyboard";

const MODEL_URL = "https://threejs.org/examples/models/gltf/Soldier.glb";
useGLTF.preload(MODEL_URL);

const commandHandlers = new Map<AgentId, (activity: ActivityType) => void>();
const roamHandlers    = new Map<AgentId, () => void>();
const haltHandlers    = new Map<AgentId, () => void>();

export function commandAgent(agent: AgentId, activity: ActivityType) {
  commandHandlers.get(agent)?.(activity);
}
export function roamAgent(agent: AgentId) {
  roamHandlers.get(agent)?.();
}
export function haltAgent(agent: AgentId) {
  haltHandlers.get(agent)?.();
}

interface Props {
  agent: AgentId;
  selected: boolean;
  onClick: () => void;
}

export function AgentAvatar({ agent, selected, onClick }: Props) {
  const meta = AGENT_META[agent];
  const group = useRef<THREE.Group>(null!);

  const storePos      = useStore((s) => s.positions[agent].current);
  const storeActivity = useStore((s) => s.positions[agent].activity);
  const agentStatus   = useStore((s) => s.agents[agent].status);

  const { scene, animations } = useGLTF(MODEL_URL);

  const cloned = useMemo(() => {
    const c = SkeletonUtils.clone(scene) as THREE.Object3D;
    const tint = new THREE.Color(meta.color);
    c.traverse((o) => {
      const m = o as THREE.Mesh;
      if (m.isMesh) {
        m.castShadow = true;
        m.receiveShadow = true;
        const orig = m.material as THREE.Material | THREE.Material[];
        const cloneOne = (mat: THREE.Material) => {
          const cm = (mat as THREE.MeshStandardMaterial).clone();
          if ((cm as THREE.MeshStandardMaterial).color) {
            (cm as THREE.MeshStandardMaterial).color.set(tint);
            (cm as THREE.MeshStandardMaterial).color.multiplyScalar(0.8);
          }
          return cm;
        };
        m.material = Array.isArray(orig) ? orig.map(cloneOne) : cloneOne(orig);
      }
    });
    return c;
  }, [scene, meta.color]);

  const mixer = useMemo(() => new THREE.AnimationMixer(cloned), [cloned]);
  const actionsByName = useMemo(() => {
    const map: Record<string, THREE.AnimationAction> = {};
    for (const clip of animations) map[clip.name] = mixer.clipAction(clip);
    return map;
  }, [mixer, animations]);

  const { goTo, roam, halt, tick, posRef } = useAgentMovement(agent);
  const roaming = useStore((s) => s.roaming?.[agent] ?? false);

  // Movimiento directo por teclado (si está seleccionado)
  const moveByKeyboard = useCallback((dx: number, dz: number) => {
    const curPos = posRef.current;
    const ROOM_BOUNDS: Record<AgentId, { xMin: number; xMax: number; zMin: number; zMax: number }> = {
      instagram: { xMin: -15.5, xMax: -5.5, zMin: -13, zMax: 13 },
      leads:     { xMin: -5.5,  xMax: 5.5,  zMin: -13, zMax: 13 },
    };
    const bounds = ROOM_BOUNDS[agent];
    const newX = Math.max(bounds.xMin, Math.min(bounds.xMax, curPos.x + dx));
    const newZ = Math.max(bounds.zMin, Math.min(bounds.zMax, curPos.z + dz));
    curPos.x = newX;
    curPos.z = newZ;
  }, [agent, posRef]);

  const playAnim = useCallback((name: string, loop = true) => {
    const idle = actionsByName["Idle"];
    const walk = actionsByName["Walk"] ?? idle;
    const run  = actionsByName["Run"]  ?? walk;
    const target = name === "Walk" ? walk : name === "Run" ? run : idle;
    Object.values(actionsByName).forEach((a) => { if (a && a !== target) a.stop(); });
    if (!target) return;
    target.reset();
    target.setLoop(loop ? THREE.LoopRepeat : THREE.LoopOnce, Infinity);
    target.clampWhenFinished = true;
    target.setEffectiveWeight(1);
    target.play();
  }, [actionsByName]);

  useEffect(() => {
    commandHandlers.set(agent, goTo);
    roamHandlers.set(agent, roam);
    haltHandlers.set(agent, halt);
    return () => {
      commandHandlers.delete(agent);
      roamHandlers.delete(agent);
      haltHandlers.delete(agent);
    };
  }, [agent, goTo, roam, halt]);

  useEffect(() => {
    if (!roaming) halt();
  }, [roaming, halt]);

  useEffect(() => {
    group.current.position.set(...storePos);
    posRef.current.set(...storePos);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const currentAnim = useRef<string>("");
  const applyPose = useCallback((activity: ActivityType, moving: boolean) => {
    if (moving) {
      group.current.rotation.set(0, 0, 0);
      const anim = agentStatus === "running" ? "Run" : "Walk";
      playAnim(anim);
      return;
    }

    switch (activity) {
      case "working":
        playAnim("Idle");
        group.current.rotation.x = -0.3;
        group.current.position.y = -0.55;
        break;
      case "sleeping":
        playAnim("Idle");
        group.current.rotation.x = -Math.PI / 2;
        group.current.position.y = 0.35;
        break;
      default:
        group.current.rotation.x = 0;
        group.current.position.y = 0;
        playAnim("Idle");
    }
  }, [agentStatus, playAnim]);

  const roamTimerRef = useRef(0);

  useFrame((state, dt) => {
    mixer.update(dt);

    const moving = tick(dt);
    const activity = useStore.getState().positions[agent].activity;
    const isSelected = useStore.getState().selected === agent;

    group.current.position.x = posRef.current.x;
    group.current.position.z = posRef.current.z;

    // Control de teclado si está seleccionado
    if (isSelected) {
      let moveX = 0, moveZ = 0;
      if (keysPressed["arrowup"] || keysPressed["w"]) moveZ -= 0.08;
      if (keysPressed["arrowdown"] || keysPressed["s"]) moveZ += 0.08;
      if (keysPressed["arrowleft"] || keysPressed["a"]) moveX -= 0.08;
      if (keysPressed["arrowright"] || keysPressed["d"]) moveX += 0.08;
      if (moveX !== 0 || moveZ !== 0) {
        moveByKeyboard(moveX, moveZ);
      }
    }

    if (moving) {
      const path = (window as any).__agentPath?.[agent];
      if (path && path.length > 0) {
        const tx = path[0][0] - posRef.current.x;
        const tz = path[0][2] - posRef.current.z;
        if (Math.abs(tx) + Math.abs(tz) > 0.01) {
          const targetAngle = Math.atan2(tx, tz);
          group.current.rotation.y = THREE.MathUtils.lerp(
            group.current.rotation.y,
            targetAngle,
            0.15,
          );
        }
      }
      applyPose("walking", true);
      roamTimerRef.current = 0;
    } else {
      applyPose(activity as ActivityType, false);

      const roamEnabled = useStore.getState().roaming?.[agent] ?? false;
      if (activity === "idle" && roamEnabled) {
        roamTimerRef.current += dt;
        if (roamTimerRef.current > 8) {
          roamTimerRef.current = 0;
          roam();
        }
      }
    }

    if (activity === "working" && !moving) {
      group.current.rotation.y = THREE.MathUtils.lerp(group.current.rotation.y, Math.PI, 0.08);
    }
  });

  useEffect(() => { return () => { mixer.stopAllAction(); }; }, [mixer]);

  return (
    <group ref={group} onClick={onClick} scale={1.8}>
      <primitive object={cloned} />

      {/* Aura — sube a y=0.08 para no enterrarse en alfombras, emisiva para brillar */}
      <mesh position={[0, 0.04, 0]} rotation={[-Math.PI / 2, 0, 0]} renderOrder={5}>
        <ringGeometry args={[0.6, 1.0, 48]} />
        <meshBasicMaterial
          color={meta.color}
          transparent
          opacity={selected ? 1 : 0.6}
          depthTest={false}
          polygonOffset
          polygonOffsetFactor={-1}
          polygonOffsetUnits={-1}
        />
      </mesh>

      {/* Etiqueta arriba de la cabeza — zIndexRange bajo para que los modales queden encima */}
      <Html position={[0, 2.5, 0]} scale={1} center zIndexRange={[0, 0]}>
        <div style={{
          fontSize: '16px',
          fontWeight: 'bold',
          color: '#ffffff',
          textShadow: '2px 2px 6px rgba(0,0,0,1)',
          textAlign: 'center',
          whiteSpace: 'nowrap',
          padding: '6px 12px',
          backgroundColor: 'rgba(0,0,0,0.8)',
          borderRadius: '8px',
          border: `2px solid ${meta.color}`,
          pointerEvents: 'none',
          position: 'relative',
          zIndex: 0,
        }}>
          {meta.name}
        </div>
      </Html>
    </group>
  );
}
