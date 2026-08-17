import { useMemo } from "react";
import * as THREE from "three";

/** A single grid line built with an imperative Line — no R3F attribute edge cases. */
function GridLine({
  a,
  b,
  color,
  opacity,
}: {
  a: [number, number, number];
  b: [number, number, number];
  color: string;
  opacity: number;
}) {
  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry().setFromPoints(
      [new THREE.Vector3(...a), new THREE.Vector3(...b)]
    );
    return g;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const mat = useMemo(() => new THREE.LineBasicMaterial({ color, transparent: true, opacity }), [color, opacity]);

  return <primitive object={new THREE.Line(geo, mat)} />;
}

/**
 * Dark floor plane with a faint converging grid — gives the corridor a
 * strong optical read toward the vanishing point. Cheap: one plane + one
 * line-grid (instanced lines), no texture.
 */
export default function Floor() {
  // Converging grid lines toward -z.
  const { verticals, horizontals } = useMemo(() => {
    const span = 60;
    const depth = 46;
    const verticals: Array<[number, number, number, number, number, number]> = [];
    for (let i = -8; i <= 8; i++) {
      const x = i * 2.2;
      verticals.push([x, 0, 1, x, 0, -depth]);
    }
    const horizontals: Array<[number, number, number, number, number, number]> = [];
    for (let z = 0; z > -depth; z -= 6) {
      horizontals.push([-span / 2, 0, z, span / 2, 0, z]);
    }
    return { verticals, horizontals };
  }, []);

  return (
    <group>
      {/* Solid dark plane to catch contact shadow / fog */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, -(46 / 2) + 1]} receiveShadow>
        <planeGeometry args={[120, 46]} />
        <meshStandardMaterial color="#0a0a0b" roughness={0.94} metalness={0.08} />
      </mesh>

      {/* Grid lines — BufferGeometry created imperatively avoids the R3F
          bufferAttribute/args edge cases entirely. */}
      {verticals.map(([x1, , z1, x2, , z2], i) => (
        <GridLine key={`v${i}`} a={[x1, 0, z1]} b={[x2, 0, z2]} color="#1d1d20" opacity={0.5} />
      ))}
      {horizontals.map(([x1, , z1, x2, , z2], i) => (
        <GridLine key={`h${i}`} a={[x1, 0, z1]} b={[x2, 0, z2]} color="#1d1d20" opacity={0.4} />
      ))}
    </group>
  );
}