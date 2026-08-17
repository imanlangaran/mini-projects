import { useEffect, useMemo, useRef } from "react";
import { createScrollEngine, type ScrollEngine } from "../animations/scrollEngine";
import { setScrollTarget } from "../animations/scrollEngine";

/**
 * Creates one Lenis instance synced to GSAP's ticker. The engine is kept in
 * a ref so consumers (nav, loader, back-to-top) can stop/start/scrollTo
 * without tearing down the whole page.
 */
export function useLenis() {
  const engineRef = useRef<ScrollEngine | null>(null);

  const api = useMemo(
    () => ({
      scrollTo: (target: string | number, opts?: { duration?: number; immediate?: boolean }) => {
        engineRef.current?.scrollTo(target, opts);
      },
      stop: () => engineRef.current?.stop(),
      start: () => engineRef.current?.start(),
      lenis: () => engineRef.current?.lenis,
    }),
    []
  );

  useEffect(() => {
    const engine = createScrollEngine();
    engineRef.current = engine;

    const container = document.getElementById("app-shell");
    if (container) setScrollTarget(container);

    return () => {
      engine.destroy();
      engineRef.current = null;
    };
  }, []);

  return api;
}