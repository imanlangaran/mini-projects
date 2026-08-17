import { Canvas } from "@react-three/fiber";
import * as THREE from "three";
import { cameraRig } from "../../state/cameraRig";
import { readMotion, dprClamp } from "../../utils/motion";
import Scene from "./Scene";
import CameraRig from "./CameraRig";
import Effects from "./Effects";

type Props = {
  /** becomes true after the loader completes; gates camera movement */
  deferred: boolean;
};

/**
 * The single, fixed, full-viewport Canvas. Runs always behind the DOM.
 * Camera continuity across the whole page is preserved because there is
 * exactly one camera and one render loop.
 */
export default function Experience({ deferred }: Props) {
  const motion = readMotion();

  return (
    <Canvas
      frameloop="always"
      dpr={dprClamp(motion.mobile)}
      gl={{
        antialias: true,
        alpha: true,
        powerPreference: "high-performance",
      }}
      camera={{
        fov: 45,
        near: 0.1,
        far: 100,
        position: [0, 1.15, 12],
      }}
      onCreated={({ camera, viewport }) => {
        cameraRig.camera = camera as THREE.PerspectiveCamera;
        cameraRig.viewport = viewport;
        cameraRig.quality = motion.quality;
      }}
    >
      <color attach="background" args={["#0C0C0D"]} />
      <fog attach="fog" args={["#0C0C0D", 12, 42]} />
      {deferred && (
        <>
          <Scene />
          <CameraRig />
          {motion.desktop && motion.quality === "high" && <Effects />}
        </>
      )}
    </Canvas>
  );
}