export type Quality = "low" | "medium" | "high";

const reducedQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
const coarseQuery = window.matchMedia("(pointer: coarse)");

export type MotionFlags = {
  reduced: boolean;
  mobile: boolean;
  desktop: boolean;
  coarse: boolean;
  dpr: number;
  quality: Quality;
};

/** Read the current motion/device flags. Pure snapshot — not a hook. */
export function readMotion(): MotionFlags {
  const reduced = reducedQuery.matches;
  const coarse = coarseQuery.matches;
  const width = window.innerWidth;
  const mobile = width < 768 || coarse;
  const dpr = Math.min(window.devicePixelRatio || 1, mobile ? 1.5 : 1.75);
  const quality: Quality = reduced ? "low" : mobile ? "medium" : "high";
  return { reduced, mobile, desktop: !reduced && !mobile, coarse, dpr, quality };
}

export function dprClamp(mobile: boolean): [number, number] {
  return [1, Math.min(window.devicePixelRatio || 1, mobile ? 1.5 : 1.75)];
}

export const isTouchDevice = () => coarseQuery.matches;