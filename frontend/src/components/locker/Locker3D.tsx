import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
import * as THREE from "three";

import type { Locker } from "../../types/locker";

interface Props {
  locker: Locker;
  position: [number, number, number];
}

export default function Locker3D({ locker, position }: Props) {
  const doorRef = useRef<THREE.Group>(null);

  const isOpen = locker.doorStatus === "OPEN";

  const ledColor =
    locker.status === "AVAILABLE"
      ? "#22c55e"
      : locker.status === "RESERVED"
        ? "#facc15"
        : locker.status === "OCCUPIED"
          ? "#ef4444"
          : "#64748b";

  useFrame((_, delta) => {
    if (!doorRef.current) return;

    const targetRotation = isOpen ? -Math.PI / 2 : 0;

    doorRef.current.rotation.y = THREE.MathUtils.damp(
      doorRef.current.rotation.y,
      targetRotation,
      6,
      delta,
    );
  });

  return (
    <group position={position}>
      {/* Thân tủ */}
      <mesh position={[0, 0, -0.22]}>
        <boxGeometry args={[1.15, 1.1, 0.5]} />
        <meshStandardMaterial
          color="#343b4b"
          metalness={0.75}
          roughness={0.35}
        />
      </mesh>

      {/* Khoang bên trong */}
      <mesh position={[0, 0, 0.035]}>
        <boxGeometry args={[1.03, 0.98, 0.025]} />
        <meshStandardMaterial color="#111827" />
      </mesh>

      {/* Cửa tủ, bản lề bên trái */}
      <group ref={doorRef} position={[-0.56, 0, 0.08]}>
        <mesh position={[0.56, 0, 0]}>
          <boxGeometry args={[1.12, 1.07, 0.055]} />
          <meshStandardMaterial
            color="#737d90"
            metalness={0.85}
            roughness={0.28}
          />
        </mesh>

        {/* Số tủ */}
        <Text
          position={[0.56, 0.17, 0.035]}
          fontSize={0.18}
          color="#ffffff"
          anchorX="center"
          anchorY="middle"
        >
          {locker.number}
        </Text>

        {/* LED */}
        <mesh position={[0.56, -0.04, 0.04]}>
          <boxGeometry args={[0.24, 0.035, 0.015]} />
          <meshStandardMaterial
            color={ledColor}
            emissive={ledColor}
            emissiveIntensity={2}
          />
        </mesh>

        {/* Tay nắm */}
        <mesh position={[1.01, -0.02, 0.07]}>
          <boxGeometry args={[0.045, 0.24, 0.06]} />
          <meshStandardMaterial
            color="#101827"
            metalness={0.8}
            roughness={0.25}
          />
        </mesh>
      </group>
    </group>
  );
}
