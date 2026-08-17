import { useRef, useState } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { PROJECTS } from "../../data/projects";
import WorkCard from "./WorkCard";
import TextReveal from "../animations/TextReveal";

/**
 * Pinned horizontal showcase. On ≥1024px the track translates horizontally
 * while the page stays pinned; below that the cards stack vertically.
 * The track tween is stored in a ref and passed to each WorkCard via props
 * for its `containerAnimation` reveals + camera swing.
 */
export default function Work() {
  const sectionRef = useRef<HTMLElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const barRef = useRef<HTMLDivElement>(null);
  const [container, setContainer] = useState<gsap.core.Animation | null>(null);

  useGSAP(
    () => {
      const section = sectionRef.current;
      const track = trackRef.current;
      if (!section || !track) return;

      const mm = gsap.matchMedia();

      mm.add("(min-width: 1024px) and (prefers-reduced-motion: no-preference)", () => {
        const tween = gsap.to(track, {
          x: () => -(track.scrollWidth - window.innerWidth),
          ease: "none",
          scrollTrigger: {
            trigger: section,
            start: "top top",
            end: () => `+=${track.scrollWidth - window.innerWidth}`,
            pin: true,
            scrub: 1,
            anticipatePin: 1,
            onUpdate: (self) => {
              if (barRef.current) {
                barRef.current.style.transform = `scaleX(${self.progress})`;
              }
            },
          },
        });
        setContainer(tween);
        return () => {
          setContainer(null);
        };
      });

      // Mobile fallback: simple reveals, no pin.
      mm.add("(max-width: 1023px)", () => {
        gsap.utils.toArray<HTMLElement>("[data-reveal]").forEach((el) => {
          gsap.fromTo(
            el,
            { autoAlpha: 0, y: 30 },
            {
              autoAlpha: 1,
              y: 0,
              duration: 0.8,
              ease: "power3.out",
              scrollTrigger: { trigger: el, start: "top 85%" },
            }
          );
        });
      });

      return () => mm.revert();
    },
    { scope: sectionRef }
  );

  return (
    <section
      ref={sectionRef}
      id="work"
      className="sticky-section relative flex min-h-screen flex-col justify-center overflow-hidden py-20 md:py-24"
    >
      <div className="mx-auto w-full max-w-5xl px-6 md:px-10">
        <span className="sec-label label-mono text-accent">02 — Work</span>
        <h2 className="sec-title mt-6 display-lg text-ink">
          <TextReveal text={"Selected\nwork."} />
        </h2>
      </div>

      <div
        ref={trackRef}
        role="region"
        aria-label="Selected projects — horizontally scrollable"
        className="mt-10 flex snap-x snap-proximity gap-6 overflow-x-auto px-6 pb-4 md:gap-8 lg:overflow-visible lg:px-10"
        style={{ scrollbarWidth: "thin", scrollbarColor: "rgba(239,233,224,0.25) transparent" }}
      >
        {PROJECTS.map((p, i) => (
          <WorkCard key={p.id} project={p} index={i} container={container} />
        ))}

        <div className="flex shrink-0 items-center justify-center px-10" role="note">
          <span className="label-mono text-muted">
            MORE COMING
            <br />
            SOON <span aria-hidden>↗</span>
          </span>
        </div>
      </div>

      <div className="mx-auto mt-10 hidden w-full max-w-5xl px-6 lg:block md:px-10">
        <div className="h-px w-full bg-surface">
          <div
            ref={barRef}
            className="h-px w-full origin-left bg-accent"
            style={{ transform: "scaleX(0)" }}
          />
        </div>
      </div>
    </section>
  );
}