import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, ContactShadows } from "@react-three/drei";

import Locker3D from "./Locker3D";
import { useLockerStore } from "../../stores/lockerStore";

export default function LockerScene() {
  const lockers = useLockerStore((state) => state.lockers);

  return (
    <div className="h-full w-full">
      <Canvas
        camera={{
          position: [5, 3, 8],
          fov: 42,
        }}
        shadows
      >
        <color attach="background" args={["#e8edf5"]} />

        <ambientLight intensity={1.2} />

        <directionalLight position={[5, 8, 5]} intensity={2.5} castShadow />

        <Environment preset="city" />

        {/* Hệ thống tủ */}
        <group position={[0, 0.15, 0]}>
          {lockers.map((locker, index) => {
            const col = index % 4;
            const row = Math.floor(index / 4);

            return (
              <Locker3D
                key={locker.id}
                locker={locker}
                position={[(col - 1.5) * 1.18, (1 - row) * 1.13, 0]}
              />
            );
          })}
        </group>

        {/* Sàn */}
        <mesh
          rotation={[-Math.PI / 2, 0, 0]}
          position={[0, -1.65, 0]}
          receiveShadow
        >
          <planeGeometry args={[30, 30]} />
          <meshStandardMaterial color="#dce3ec" />
        </mesh>

        <ContactShadows
          position={[0, -1.64, 0]}
          opacity={0.4}
          scale={12}
          blur={2.5}
        />

        <OrbitControls
          enablePan={false}
          minDistance={4}
          maxDistance={14}
          maxPolarAngle={Math.PI / 2}
        />
      </Canvas>
    </div>
  );
}
