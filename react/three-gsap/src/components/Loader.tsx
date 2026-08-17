import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { BRAND } from "../data/brand";
import { readMotion } from "../utils/motion";

type Props = {
  onComplete: () => void;
};

/**
 * Minimal black loading state: IL monogram, a thin progress bar and a mono
 * percentage counting 0→100. On completion it animates its own exit — the
 * veil lifts and the brand fades — THEN calls onComplete, so Layout can
 * safely unmount it and fire the content entrance on a stable DOM.
 */
export default function Loader({ onComplete }: Props) {
  const [progress, setProgress] = useState(0);
  const veilRef = useRef<HTMLDivElement>(null);
  const brandRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const reduced = readMotion().reduced;

    if (reduced) {
      const t = setTimeout(onComplete, 200);
      return () => clearTimeout(t);
    }

    const obj = { v: 0 };
    const tween = gsap.to(obj, {
      v: 100,
      duration: 2.2,
      ease: "power2.inOut",
      onUpdate: () => setProgress(Math.round(obj.v)),
      onComplete: () => {
        const veil = veilRef.current;
        const brand = brandRef.current;
        if (veil && brand) {
          const exit = gsap.timeline({
            onComplete: () => onComplete(),
          });
          exit.to(brand, { autoAlpha: 0, y: -24, duration: 0.45, ease: "power3.out" }, 0);
          exit.to(
            veil,
            { yPercent: -100, duration: 1, ease: "power4.inOut" },
            0.15
          );
          exit.to(
            veil,
            { autoAlpha: 0, duration: 0.2 },
            1
          );
        } else {
          onComplete();
        }
      },
    });

    return () => {
      tween.kill();
    };
  }, [onComplete]);

  return (
    <div
      ref={veilRef}
      role="status"
      className="fixed inset-0 z-[80] flex flex-col items-center justify-center bg-night"
    >
      {/* Visually hidden, single announcement — avoids announcing every tick */}
      <span className="sr-only">Loading complete</span>

      <div ref={brandRef} aria-hidden className="flex flex-col items-center">
        <span className="display-lg text-ink">{BRAND.monogram}</span>
        <span className="label-mono mt-3 text-muted">LOADING</span>
      </div>

      <div aria-hidden className="mt-12 h-px w-40 overflow-hidden bg-surface">
        <div
          className="h-full bg-accent transition-[width] duration-150"
          style={{ width: `${progress}%` }}
        />
      </div>
      <span aria-hidden className="label-mono mt-4 text-muted tabular-nums">
        {String(progress).padStart(3, "0")}%
      </span>
    </div>
  );
}