import { useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { CAMERA_PATH, pathProgressForScroll } from "../../data/cameraPath";
import { cameraRig } from "../../state/cameraRig";
import { readMotion } from "../../utils/motion";
import { useCanvasPause } from "../../hooks/useCanvasPause";

const _v = new THREE.Vector3();
const _target = new THREE.Vector3();

/**
 * THE only camera driver. Each frame it:
 *   1. computes a target pose from the master timeline's progress (0..1)
 *   2. damp-lerps the camera toward it (exponential smoothing, no springs)
 *   3. adds pointer parallax and a per-project workTrackProgress offset
 *   4. points the camera at the pose's `look` target
 *
 * Nothing else touches the camera — controls, nav and scroll all route here.
 */
export default function CameraRig() {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  const { reduced } = readMotion();
  useCanvasPause(reduced);

  const smooth = useRef({
    px: CAMERA_PATH[0].position[0],
    py: CAMERA_PATH[0].position[1],
    pz: CAMERA_PATH[0].position[2],
    lx: CAMERA_PATH[0].look[0],
    ly: CAMERA_PATH[0].look[1],
    lz: CAMERA_PATH[0].look[2],
  });

  useFrame(() => {
    if (cameraRig.camera !== camera) cameraRig.camera = camera;

    // Master scroll progress comes from the DOM-side ScrollTrigger.
    const baseProgress = cameraRig.scrollProgress;

    const idx = pathProgressForScroll(baseProgress);
    const i = Math.floor(idx);
    const f = idx - i;
    const p0 = CAMERA_PATH[i];
    const p1 = CAMERA_PATH[Math.min(i + 1, CAMERA_PATH.length - 1)];

    // Interpolate pose along the path.
    _v.set(
      p0.position[0] + (p1.position[0] - p0.position[0]) * f,
      p0.position[1] + (p1.position[1] - p0.position[1]) * f,
      p0.position[2] + (p1.position[2] - p0.position[2]) * f
    );
    _target.set(
      p0.look[0] + (p1.look[0] - p0.look[0]) * f,
      p0.look[1] + (p1.look[1] - p0.look[1]) * f,
      p0.look[2] + (p1.look[2] - p0.look[2]) * f
    );

    // Work-track swing: pull the camera sideways toward the current card.
    const workBlend = cameraRig.workTrackProgress;
    _v.x += (workBlend - 0.5) * 3.2;
    _v.y += (workBlend - 0.5) * 0.8;

    // Pointer parallax.
    const px = cameraRig.mouseSmooth.x;
    const py = cameraRig.mouseSmooth.y;
    _v.x += px * 0.4;
    _v.y += py * 0.25;

    // Expo-damp toward the pose.
    const s = smooth.current;
    const k = readMotion().reduced ? 1 : 0.06;
    s.px += (_v.x - s.px) * k;
    s.py += (_v.y - s.py) * k;
    s.pz += (_v.z - s.pz) * k;
    s.lx += (_target.x - s.lx) * k;
    s.ly += (_target.y - s.ly) * k;
    s.lz += (_target.z - s.lz) * k;

    camera.position.set(s.px, s.py, s.pz);
    camera.lookAt(s.lx, s.ly, s.lz);
  });

  return null;
}