import gsap from "gsap";
import { EASE } from "./easing";

/**
 * The cinematic entrance: runs after the loader's veil has lifted. Reveals
 * the whole experience in a deliberate order — hero type, meta, nav, then
 * the interaction cue. Targeted at classes scoped under `scope`.
 *
 * The loader animates its OWN exit; this timeline starts on a stable DOM.
 */
export function buildEntranceTimeline(scope: HTMLElement) {
  const tl = gsap.timeline({ defaults: { ease: EASE.EXPO } });

  // Pre-hide everything the entrance reveals, so nothing flashes before its
  // slot. Reduced-motion callers skip this timeline entirely.
  gsap.set(scope.querySelectorAll("[data-hero-fade], [data-nav-item], [data-scroll-cue]"), {
    autoAlpha: 0,
  });
  gsap.set(scope.querySelectorAll(".hero-line .line-inner"), { yPercent: 110 });

  // 1. Hero title lines mask in (staggered).
  tl.to(
    scope.querySelectorAll(".hero-line .line-inner"),
    { yPercent: 0, duration: 1.25, stagger: 0.12, ease: EASE.INOUT },
    0.1
  );

  // 2. Hero eyebrow + subtitle.
  tl.fromTo(
    scope.querySelectorAll("[data-hero-fade]"),
    { autoAlpha: 0, y: 18 },
    { autoAlpha: 1, y: 0, duration: 0.9, stagger: 0.1, ease: EASE.OUT },
    0.5
  );

  // 3. Nav drops in.
  tl.fromTo(
    scope.querySelectorAll("[data-nav-item]"),
    { autoAlpha: 0, y: -16 },
    { autoAlpha: 1, y: 0, duration: 0.7, stagger: 0.06, ease: EASE.OUT },
    0.7
  );

  // 4. Scroll cue pulse starts.
  tl.fromTo(
    scope.querySelectorAll("[data-scroll-cue]"),
    { autoAlpha: 0 },
    { autoAlpha: 1, duration: 0.6, ease: EASE.OUT },
    0.95
  );

  return tl;
}