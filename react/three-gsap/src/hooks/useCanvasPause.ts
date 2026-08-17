import { useEffect } from "react";
import { useThree } from "@react-three/fiber";

/**
 * Pauses the R3F render loop when the tab is hidden (`frameloop="demand"`
 * costs nothing until the tab is visible again). Under reduced-motion the
 * loop drops to "demand" anyway once the static frame is cached by the
 * renderer's last paint.
 */
export function useCanvasPause(reduced: boolean) {
  const { setFrameloop } = useThree();

  useEffect(() => {
    if (reduced) {
      setFrameloop("demand");
      return;
    }

    const onVisibility = () => {
      if (document.hidden) setFrameloop("demand");
      else setFrameloop("always");
    };
    const onFocus = () => setFrameloop("always");

    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("focus", onFocus);

    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("focus", onFocus);
    };
  }, [setFrameloop, reduced]);
}