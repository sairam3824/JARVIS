import { useFrame } from "@react-three/fiber";
import { Float, MeshDistortMaterial, OrbitControls, Points, PointMaterial } from "@react-three/drei";
import { useMemo, useRef } from "react";
import type { Mesh } from "three";
import { aiCoreMotion } from "@animations/presets";

export function AICoreScene() {
  const sphereRef = useRef<Mesh>(null);
  const particles = useMemo(
    () =>
      Float32Array.from({ length: aiCoreMotion.particleCount * 3 }, () => (Math.random() - 0.5) * 12),
    [],
  );

  useFrame((state) => {
    if (!sphereRef.current) return;
    sphereRef.current.rotation.y = state.clock.elapsedTime * aiCoreMotion.rotationSpeed;
    sphereRef.current.rotation.x = state.clock.elapsedTime * 0.08;
  });

  return (
    <>
      <ambientLight intensity={0.7} />
      <pointLight position={[3, 2, 4]} intensity={16} color="#62e0ff" />
      <Float speed={2.4} rotationIntensity={0.5} floatIntensity={1.5}>
        <mesh ref={sphereRef}>
          <icosahedronGeometry args={[1.45, 24]} />
          <MeshDistortMaterial color="#18b7ff" emissive="#62e0ff" emissiveIntensity={1.1} roughness={0.1} metalness={0.65} distort={0.28} speed={1.75} />
        </mesh>
      </Float>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[2.2, 0.02, 32, 240]} />
        <meshBasicMaterial color="#62e0ff" transparent opacity={0.58} />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0.8, 0]}>
        <torusGeometry args={[2.8, 0.018, 32, 240]} />
        <meshBasicMaterial color="#8ce8ff" transparent opacity={0.22} />
      </mesh>
      <Points positions={particles} stride={3} frustumCulled={false}>
        <PointMaterial transparent color="#8ce8ff" size={0.035} sizeAttenuation depthWrite={false} />
      </Points>
      <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.35} />
    </>
  );
}

