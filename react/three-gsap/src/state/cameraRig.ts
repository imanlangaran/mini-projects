import * as THREE from "three";
import type { ScrollTrigger } from "gsap/ScrollTrigger";
import type { Quality } from "../utils/motion";

/**
 * Module-scope mutable singleton shared between the DOM world and the R3F
 * world. Every value here is mutated each frame — this is intentionally NOT
 * React state, so writing to it never triggers a re-render.
 */
export const cameraRig = {
  camera: null as THREE.PerspectiveCamera | null,
  viewport: { width: 1, height: 1 },
  // Lerped pointer in NDC-ish space used for gentle parallax.
  mouse: new THREE.Vector2(0, 0),
  mouseSmooth: new THREE.Vector2(0, 0),
  // 0..1 written by the full-page master ScrollTrigger.
  scrollProgress: 0,
  scrollTrigger: null as ScrollTrigger | null,
  // 0..1 written by WorkCard (per-project camera swing).
  workTrackProgress: 0,
  hoveredId: null as string | null,
  activeNavId: null as string | null,
  quality: "high" as Quality,
  // Signs that interaction should steer the camera toward a destination.
  navIntensity: 0,
};

export function setPointer(nx: number, ny: number) {
  cameraRig.mouse.set(nx, ny);
}

export function setNavHover(id: string | null) {
  cameraRig.hoveredId = id;
}

export function setNavActive(id: string | null) {
  cameraRig.activeNavId = id;
}