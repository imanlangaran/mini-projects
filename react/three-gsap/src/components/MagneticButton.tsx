import { useRef, type ReactNode } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

type Props = {
  children: ReactNode;
  strength?: number;
  className?: string;
  as?: "a" | "button";
  href?: string;
  onClick?: () => void;
  ariaLabel?: string;
};

/**
 * Magnetic wrapper: the element is pulled toward the pointer within a small
 * radius and springs back on leave. Disabled when reduced-motion is on.
 */
export default function MagneticButton({
  children,
  strength = 0.35,
  className,
  as = "button",
  href,
  onClick,
  ariaLabel,
}: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const el = ref.current;
      if (!el || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

      const xTo = gsap.quickTo(el, "x", { duration: 0.4, ease: "power3.out" });
      const yTo = gsap.quickTo(el, "y", { duration: 0.4, ease: "power3.out" });

      const onMove = (e: PointerEvent) => {
        const rect = el.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        xTo((e.clientX - cx) * strength);
        yTo((e.clientY - cy) * strength);
      };
      const onLeave = () => {
        xTo(0);
        yTo(0);
      };

      el.addEventListener("pointermove", onMove);
      el.addEventListener("pointerleave", onLeave);
      return () => {
        el.removeEventListener("pointermove", onMove);
        el.removeEventListener("pointerleave", onLeave);
      };
    },
    { scope: ref }
  );

  const Tag = as;
  // Only open external http(s) links in a new tab. mailto: links must stay in
  // the current tab — target="_blank" breaks the mail client experience.
  const isExternal = as === "a" && href?.startsWith("http");
  const props = as === "a"
    ? {
        href,
        ...(isExternal ? { target: "_blank", rel: "noreferrer" } : {}),
      }
    : { type: "button" as const };

  return (
    <div ref={ref} className="inline-block will-change-transform">
      <Tag
        {...props}
        aria-label={ariaLabel}
        onClick={onClick}
        className={className}
        data-cursor=""
      >
        {children}
      </Tag>
    </div>
  );
}