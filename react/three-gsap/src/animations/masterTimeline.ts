import { ScrollTrigger } from "gsap/ScrollTrigger";
import { cameraRig } from "../state/cameraRig";
import { readMotion } from "../utils/motion";

/**
 * Sets up the single source of scroll progress: a full-page ScrollTrigger
 * scrubbed 0..1 over the whole document. It has no tween — its `onUpdate`
 * just writes `cameraRig.scrollProgress`, which CameraRig reads each frame.
 *
 * This avoids the "inert timeline" hack: the trigger is a pure carrier of
 * scroll progress, and the R3F camera drives itself from it.
 */
export function setupMasterTimeline() {
  const motion = readMotion();
  if (motion.reduced) return; // reduced: no scroll-driven camera movement

  const trigger = ScrollTrigger.create({
    start: "top top",
    end: "bottom bottom",
    scrub: 0.9,
    onUpdate: (self) => {
      cameraRig.scrollProgress = self.progress;
    },
  });

  cameraRig.scrollProgress = 0;
  cameraRig.scrollTrigger = trigger;

  return trigger;
}

export function destroyMasterTimeline() {
  cameraRig.scrollTrigger?.kill();
  cameraRig.scrollTrigger = null;
  cameraRig.scrollProgress = 0;
}