import gsap from "gsap";

/**
 * Camera poses along the corridor tour. `position` is where the camera sits;
 * `look` is where it points. `pathProgressForScroll` maps master timeline
 * progress (scrollProgress ÷ total) onto a float index into this array.
 */
export type CameraPose = {
  position: [number, number, number];
  look: [number, number, number];
};

export const CAMERA_PATH: CameraPose[] = [
  // Hero — the corridor renders into view, camera holds here.
  { position: [0, 1.15, 12], look: [0, 0.4, 0] },
  // About — lean toward the reading slab.
  { position: [3.1, 1.75, 5.5], look: [-1.6, 0.55, -4] },
  // Work — pull back, look down the showcase corridor.
  { position: [0, 2.3, -1.5], look: [0, 0.8, -12] },
  // Skills — swing toward the orbital constellation.
  { position: [-3.1, 1.85, -8.5], look: [2.2, 0.5, -16] },
  // Contact — advance to the glowing portal.
  { position: [0, 1.4, -15.5], look: [0, 0.4, -23] },
];

export function pathProgressForScroll(progress: number): number {
  return gsap.utils.clamp(0, CAMERA_PATH.length - 1, progress * (CAMERA_PATH.length - 1));
}