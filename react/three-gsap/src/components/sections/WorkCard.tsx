import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import type { Project } from "../../data/projects";
import { cameraRig } from "../../state/cameraRig";

type Props = {
  project: Project;
  /** index of the card within the horizontal track */
  index: number;
  /** the Work section's track tween (for containerAnimation) */
  container?: gsap.core.Animation | null;
};

/**
 * One project card inside the pinned showcase. The gradient "render" panel
 * stands in for imagery. As each card enters the viewport, it writes
 * `cameraRig.workTrackProgress` so CameraRig swings toward a matching pose.
 *
 * The card is NOT a link (copy is placeholder) — so it carries no role, is
 * not focusable, and doesn't receive `data-cursor` (which implies a click).
 */
export default function WorkCard({ project, index, container }: Props) {
  const cardRef = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const card = cardRef.current;
      if (!card) return;
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
      if (!container) return; // track not pinned on this viewport

      const enter = gsap.fromTo(
        card,
        { autoAlpha: 0, xPercent: 14 },
        {
          autoAlpha: 1,
          xPercent: 0,
          duration: 1,
          ease: "power3.out",
          scrollTrigger: {
            trigger: card,
            containerAnimation: container,
            start: "left 80%",
            toggleActions: "play none none reverse",
          },
        }
      );

      // Per-card camera swing: tween progress toward the card's share.
      const swing = gsap.to(cameraRig, {
        workTrackProgress: (index + 0.5) / 4,
        duration: 1.2,
        ease: "power2.out",
        scrollTrigger: {
          trigger: card,
          containerAnimation: container,
          start: "left 60%",
          end: "left 20%",
          scrub: 1,
        },
      });

      return () => {
        enter.scrollTrigger?.kill();
        swing.scrollTrigger?.kill();
      };
    },
    { dependencies: [index, container] }
  );

  return (
    <article
      ref={cardRef}
      data-reveal
      aria-label={`Project ${project.index}: ${project.title}`}
      className="group relative h-[70vh] w-[78vw] shrink-0 snap-start overflow-hidden rounded-xl border border-hairline bg-surface md:w-[52vw] lg:w-[40vw]"
    >
      {/* Render panel (imagery placeholder) */}
      <div
        className="absolute inset-0 opacity-80 transition-opacity duration-500 group-hover:opacity-100"
        style={{ background: project.gradient }}
        aria-hidden
      >
        <div className="absolute inset-0 bg-[radial-gradient(120%_80%_at_50%_0%,rgba(239,233,224,0.06),transparent_60%)]" />
      </div>

      <div className="absolute inset-x-0 top-0 flex items-center justify-between p-6 md:p-8">
        <span className="label-mono text-ink/70">PROJECT {project.index}</span>
        <span className="label-mono text-muted">{project.year}</span>
      </div>

      <div className="absolute inset-x-0 bottom-0 p-6 md:p-8">
        <h3 className="display-lg text-ink">{project.title}</h3>
        <p className="mt-2 max-w-md text-sm text-ink/80">{project.tagline}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {project.services.map((s) => (
            <span
              key={s}
              className="label-mono rounded-full border border-hairline px-2.5 py-0.5 text-ink/70"
            >
              {s}
            </span>
          ))}
        </div>
        {/* Always visible so the touch/keyboard experience doesn't lose the
            affordance; it's meta, not a link target. */}
        <span className="mt-6 inline-flex items-center gap-2 label-mono text-accent">
          CASE STUDY <span aria-hidden>→</span>
        </span>
      </div>
    </article>
  );
}