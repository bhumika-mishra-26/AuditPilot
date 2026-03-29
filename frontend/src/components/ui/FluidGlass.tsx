import * as THREE from 'three';
import { useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Environment, MeshTransmissionMaterial, RoundedBox } from '@react-three/drei';

export default function FluidGlass() {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none w-full h-full">
      <Canvas camera={{ position: [0, 0, 10], fov: 35 }} gl={{ alpha: true, antialias: true }}>
        {/* Subtle ambient light */}
        <ambientLight intensity={0.5} />
        {/* Night environment matches your dark theme and prevents the glass from turning bright white */}
        <Environment preset="night" />
        <FluidPill />
      </Canvas>
    </div>
  );
}

function FluidPill() {
  const barRef = useRef<THREE.Mesh>(null!);
  const { viewport } = useThree();

  const width = viewport.width;
  const height = viewport.height;
  const depth = 2.0;
  const radius = Math.min(width, height) / 2;

  useFrame((state, delta) => {
    // Subtle physical breathing
    if (barRef.current) {
        barRef.current.rotation.y = THREE.MathUtils.lerp(
            barRef.current.rotation.y,
            state.pointer.x * 0.1,
            0.1
        );
    }
  });

  return (
    <RoundedBox ref={barRef} args={[width, height, depth]} radius={radius} smoothness={64}>
      {/* 
        Using EXACT properties provided from your React Bits reference code
      */}
      <MeshTransmissionMaterial
        transmission={1}
        roughness={0}
        thickness={2}
        ior={1.15}
        chromaticAberration={0.05}
        anisotropy={0.01}
        color="#ffffff"
      />
    </RoundedBox>
  );
}
