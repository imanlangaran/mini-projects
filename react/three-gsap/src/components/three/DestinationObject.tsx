import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import type { NavId } from "../../data/brand";
import { DESTINATIONS, DESTINATION_LABELS } from "../../scenes/destinationPoses";
import { cameraRig } from "../../state/cameraRig";

type Props = {
  id: NavId;
};

const CORE_MATERIAL = new THREE.MeshStandardMaterial({
  color: "#2a2a2e",
  roughness: 0.55,
  metalness: 0.5,
});

const DARK_MATERIAL = new THREE.MeshStandardMaterial({
  color: "#26262a",
  roughness: 0.5,
  metalness: 0.5,
});

const THERMAL_MATERIAL = new THREE.MeshStandardMaterial({
  color: "#2b2420",
  roughness: 0.5,
  metalness: 0.5,
});

const WIRE_MATERIAL = new THREE.MeshBasicMaterial({
  color: "#9c978e",
  wireframe: true,
  transparent: true,
  opacity: 0.7,
});

const RING_MATERIAL = new THREE.MeshBasicMaterial({
  color: "#9c978e",
  transparent: true,
  opacity: 0.5,
});

/** Shared across the two contact-plate accents. */
const RING_TORUS = new THREE.MeshStandardMaterial({
  color: "#c34a2f",
  emissive: "#c34a2f",
  emissiveIntensity: 0.7,
});

/** Contact portal core — shared, never created inside render. */
const PORTAL_MATERIAL = new THREE.MeshBasicMaterial({
  color: "#c34a2f",
  transparent: true,
});

/**
 * A nav destination monolith. Hover/active is written to `cameraRig` by the
 * DOM proxy elements (nav links / section triggers); this component only
 * reads those ids and pulses accent emissive + scale. Click handling is on
 * the DOM proxy too — geometry never raycasts (canvas is pointer-events:none).
 *
 * These are intentionally REFERENCE-EQUAL materials shared across frames;
 * R3F reuses them instead of cloning, so memory stays flat.
 */
export default function DestinationObject({ id }: Props) {
  const groupRef = useRef<THREE.Group>(null);
  const coreGroupRef = useRef<THREE.Group>(null);
  const pose = DESTINATIONS.find((d) => d.id === id)!;

  useFrame((state) => {
    const g = groupRef.current;
    if (!g) return;
    const t = state.clock.elapsedTime;

    // Float.
    g.position.y = Math.sin(t * pose.float.period) * pose.float.amp;

    // Hover: lift + scale up a touch.
    const target = cameraRig.hoveredId === id || cameraRig.activeNavId === id ? 1.08 : 1;
    g.scale.x += (target - g.scale.x) * 0.08;
    g.scale.y += (target - g.scale.y) * 0.08;
    g.scale.z += (target - g.scale.z) * 0.08;

    // Slow spin for the work panels & skills constellation.
    if (coreGroupRef.current) {
      coreGroupRef.current.rotation.y = id === "work" ? t * 0.35 : Math.sin(t * 0.3);
    }
  });

  const active = cameraRig.activeNavId === id || cameraRig.hoveredId === id;

  return (
    <group ref={groupRef} position={pose.position}>
      <group ref={coreGroupRef}>
        {id === "about" && (
          <>
            <mesh rotation={[0.1, 0.4, 0]} material={CORE_MATERIAL}>
              <boxGeometry args={[1.4, 2.6, 0.22]} />
            </mesh>
            <mesh position={[0, -0.35, 0.14]} rotation={[-Math.PI / 2, 0, 0]} material={RING_MATERIAL}>
              <ringGeometry args={[0.3, 0.42, 40]} />
            </mesh>
          </>
        )}

        {id === "work" && (
          <>
            {[1, 2, 3].map((i) => (
              <mesh
                key={i}
                position={[0, (i - 2) * 1.3, 0]}
                rotation={[0, i * 0.5, 0]}
                material={i % 2 === 0 ? DARK_MATERIAL : THERMAL_MATERIAL}
              >
                <boxGeometry args={[2.4, 0.5, 0.5]} />
              </mesh>
            ))}
          </>
        )}

        {id === "skills" && (
          <>
            <mesh material={WIRE_MATERIAL}>
              <icosahedronGeometry args={[1.1, 0]} />
            </mesh>
            <mesh rotation={[Math.PI / 2, 0, 0]} material={RING_TORUS}>
              <torusGeometry args={[1.7, 0.015, 8, 90]} />
            </mesh>
          </>
        )}

        {id === "contact" && (
          <mesh material={PORTAL_MATERIAL}>
            <octahedronGeometry args={[0.8, 0]} />
          </mesh>
        )}
      </group>

      {/* Float label above the object */}
      <Html position={[0, 2.4, 0]} center distanceFactor={14} zIndexRange={[20, 0]}>
        <div
          className="pointer-events-none whitespace-nowrap label-mono text-ink"
          style={{ opacity: active ? 1 : 0.45 }}
        >
          {DESTINATION_LABELS[id]}
        </div>
      </Html>
    </group>
  );
}