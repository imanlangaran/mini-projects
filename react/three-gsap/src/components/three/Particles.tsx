import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

type Props = {
  count: number;
};

/**
 * Drei-style dust drifting through the corridor. Count is quality-gated by
 * the parent (600 high / 250 medium / 0 low); positions are seeded once.
 */
export default function Particles({ count }: Props) {
  const ref = useRef<THREE.Points>(null);

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 18; // x
      arr[i * 3 + 1] = (Math.random() - 0.5) * 3 + 1; // y
      arr[i * 3 + 2] = -Math.random() * 34 - 1; // z
    }
    return arr;
  }, [count]);

  useFrame((_, delta) => {
    if (!ref.current) return;
    const time = performance.now() * 0.0001;
    ref.current.rotation.y = Math.sin(time) * 0.05;
    // Gentle z-drift so dust feels alive.
    ref.current.position.z += delta * 0.15;
    if (ref.current.position.z > 2) ref.current.position.z = -34;
  });

  if (count === 0) return null;

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        color="#9c978e"
        size={0.04}
        sizeAttenuation
        transparent
        opacity={0.55}
        depthWrite={false}
      />
    </points>
  );
}