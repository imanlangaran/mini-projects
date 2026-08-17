import { useEffect, useState } from "react";

function reducedQuery() {
  return window.matchMedia("(prefers-reduced-motion: reduce)");
}

export function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(() => reducedQuery().matches);

  useEffect(() => {
    const query = reducedQuery();
    const onChange = (e: MediaQueryListEvent) => setReduced(e.matches);
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, []);

  return reduced;
}