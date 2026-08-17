import { Suspense } from "react";
import { cameraRig } from "../../state/cameraRig";
import { DESTINATIONS } from "../../scenes/destinationPoses";
import { readMotion } from "../../utils/motion";
import Floor from "./Floor";
import Spine from "./Spine";
import Particles from "./Particles";
import DestinationObject from "./DestinationObject";

/**
 * The 3D world: a dark corridor with four destination monoliths + floor,
 * spine, particles. Quality-gated: fewer particles, no shadows on medium,
 * nothing on low (reduced motion still gets a static frame).
 *
 * Note: deliberately NO drei <Environment> / <ContactShadows> — those fetch
 * HDRs from a remote CDN and run extra render passes, which can throw on
 * flaky networks and crash the whole Canvas tree. Local lights + fog give
 * the same cinematic depth without the failure mode.
 */
export default function Scene() {
  const { quality } = readMotion();
  const particleCount = quality === "high" ? 600 : quality === "medium" ? 250 : 0;
  const shadows = quality === "high";

  return (
    <Suspense fallback={null}>
      {/* Local IBL-ish bounce: warm key + cool fill + accent rim */}
      <ambientLight intensity={0.45} />
      <hemisphereLight args={["#fff2e2", "#141416", 0.5]} />
      <directionalLight
        position={[4, 6, 8]}
        intensity={1.7}
        color="#fff2e2"
        castShadow={shadows}
        shadow-mapSize={[1024, 1024]}
        shadow-bias={-0.0004}
      />
      <directionalLight position={[-6, 4, -10]} intensity={0.55} color="#dfe6ff" />
      <pointLight position={[0, 1, -18]} intensity={2.6} distance={16} color="#c34a2f" />

      <Floor />
      <Spine />
      <Particles count={particleCount} />

      {DESTINATIONS.map((d) => (
        <DestinationObject key={d.id} id={d.id} />
      ))}
    </Suspense>
  );
}

// Re-export the rig so Experience can pass quality into it via props/state.
export { cameraRig };