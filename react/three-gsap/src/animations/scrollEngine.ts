import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";

export type ScrollEngine = {
  lenis: Lenis;
  stop: () => void;
  start: () => void;
  scrollTo: (target: string | number, opts?: { duration?: number; immediate?: boolean }) => void;
  destroy: () => void;
};

let scrollTarget: HTMLElement | null = null;

export function setScrollTarget(el: HTMLElement) {
  scrollTarget = el;
}

/**
 * Lenis is a native-scroll smooth scroller (it drives real window.scrollY),
 * so ScrollTrigger keeps using the window scroller — no scrollerProxy needed.
 * We only need to forward Lenis' scroll updates to ScrollTrigger and drive
 * Lenis' rAF from GSAP's ticker so both stay on one clock.
 */
export function createScrollEngine(opts?: {
  duration?: number;
  onScroll?: (y: number) => void;
}): ScrollEngine {
  const lenis = new Lenis({
    duration: opts?.duration ?? 1.15,
    smoothWheel: true,
    syncTouch: false,
    wheelMultiplier: 1,
    touchMultiplier: 1.4,
  });

  if (opts?.onScroll) {
    lenis.on("scroll", ({ scroll }) => opts.onScroll?.(scroll));
  }

  lenis.on("scroll", ScrollTrigger.update);

  const tick = (time: number) => lenis.raf(time * 1000);
  gsap.ticker.add(tick);
  gsap.ticker.lagSmoothing(0);

  // Respect reduced-motion: settle instantly.
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    lenis.stop();
  }

  if (scrollTarget) ScrollTrigger.refresh();

  return {
    lenis,
    stop: () => lenis.stop(),
    start: () => lenis.start(),
    scrollTo: (target, toOpts) => {
      lenis.scrollTo(target, {
        duration: toOpts?.immediate ? 0 : (toOpts?.duration ?? 1.6),
        easing: (t: number) => 1 - Math.pow(1 - t, 4),
      });
    },
    destroy: () => {
      gsap.ticker.remove(tick);
      lenis.destroy();
      ScrollTrigger.getAll().forEach((st) => st.kill());
    },
  };
}