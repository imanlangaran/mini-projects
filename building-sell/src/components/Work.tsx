import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

const PROJECTS = [
  {
    name: "The Haywood",
    place: "Lakewood / 04",
    detail: "4-bed courtyard residence",
    accent: "#C34A2F",
  },
  {
    name: "House Rowan",
    place: "Boulder / 07",
    detail: "Passive-solar hillside home",
    accent: "#9A6A3C",
  },
  {
    name: "Wend & Weir",
    place: "Portland / 02",
    detail: "Split-level timber loft",
    accent: "#3F4A3C",
  },
  {
    name: "The Upland",
    place: "Napa / 11",
    detail: "Stone & glass vineyard house",
    accent: "#7A5C48",
  },
  {
    name: "Ironwood",
    place: "Bend / 08",
    detail: "Weathering-steel retreat",
    accent: "#C34A2F",
  },
];

export default function Work() {
  const section = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      // Only enable the horizontal track on wider screens (>= 1024).
      const mm = gsap.matchMedia();
      mm.add("(min-width: 1024px)", () => {
        const track = section.current!.querySelector(".work-track")!;
        const getScrollAmount = () => {
          const trackEl = track as HTMLElement;
          return trackEl.scrollWidth - window.innerWidth;
        };
        const sectionEl = section.current!;
        const tween = gsap.to(track, {
          x: () => -getScrollAmount(),
          ease: "none",
          scrollTrigger: {
            trigger: sectionEl,
            start: "top top",
            end: () => "+=" + getScrollAmount(),
            pin: true,
            scrub: 1,
          },
        });

        // Progress bar
        gsap.fromTo(
          ".work-progress",
          { scaleX: 0 },
          {
            scaleX: 1,
            ease: "none",
            scrollTrigger: {
              trigger: sectionEl,
              start: "top top",
              end: () => "+=" + getScrollAmount(),
              scrub: true,
            },
          }
        );

        // Reveal project images/text as each panel enters the viewport (horizontal)
        gsap.utils.toArray<HTMLElement>(".work-card").forEach((card) => {
          gsap.fromTo(
            card.querySelector(".work-card-media"),
            { autoAlpha: 0, scale: 1.08 },
            {
              autoAlpha: 1,
              scale: 1,
              duration: 0.6,
              ease: "power2.out",
              scrollTrigger: {
                containerAnimation: tween,
                trigger: card,
                start: "left 85%",
                toggleActions: "play none none reset",
              },
            }
          );
        });

        return () => {};
      });

      return () => mm.revert();
    },
    { scope: section }
  );

  return (
    <section ref={section} id="work" aria-label="Selected work" className="work-pin relative overflow-hidden bg-paper2">
      <div className="absolute left-4 top-8 z-10 sm:left-8 lg:left-12">
        <p className="label-mono flex items-center gap-3 text-ink/60">
          <span className="inline-block h-px w-10 bg-accent" />
          SELECTED WORK / 03
        </p>
      </div>

      <div className="work-track flex h-screen w-max items-center gap-8 px-8 pt-16 lg:gap-14 lg:px-12">
        {/* intro panel */}
        <div className="flex h-[70vh] w-[72vw] shrink-0 flex-col justify-center sm:w-[50vw] lg:w-[32vw]">
          <h3 className="display-lg text-6xl lg:text-7xl">
            Homes,
            <br />
            <span className="italic text-accent">each one</span>
            <br />
            singular.
          </h3>
          <p className="mt-8 max-w-sm text-ink/70">
            A short catalogue of the places we have built and sold — drag nothing, just scroll.
          </p>
        </div>

        {PROJECTS.map((p) => (
          <article
            key={p.name}
            className="work-card flex h-[70vh] w-[82vw] shrink-0 flex-col justify-end sm:w-[60vw] lg:w-[44vw]"
          >
            <div className="group relative h-[80%] w-full overflow-hidden">
              {/* abstract "rendering" panel as the project visual */}
              <div
                className="work-card-media absolute inset-0"
                style={{
                  background: `linear-gradient(135deg, ${p.accent} 0%, ${p.accent}99 55%, ${p.accent}66 100%)`,
                }}
              >
                <div className="absolute inset-0 opacity-30 [background-image:repeating-linear-gradient(90deg,transparent,transparent_18px,rgba(28,25,23,0.25)_18px,rgba(28,25,23,0.25)_19px)]" />
                <span className="label-mono absolute left-5 top-5 text-paper/80">{p.place}</span>
                <span className="display-xl absolute bottom-4 right-5 text-7xl text-paper/25">{p.place.split(" /")[0]}</span>
              </div>
            </div>
            <div className="flex items-baseline justify-between pb-2 pt-5">
              <h4 className="display-lg text-3xl lg:text-4xl">{p.name}</h4>
              <p className="label-mono text-ink/60">{p.detail}</p>
            </div>
          </article>
        ))}

        {/* outro panel */}
        <div className="flex h-[70vh] w-[80vw] shrink-0 flex-col justify-center px-2 sm:w-[50vw] lg:w-[28vw]">
          <p className="label-mono mb-6 text-ink/60">That’s eleven and counting.</p>
          <a
            href="#contact"
            className="display-lg inline-flex items-center gap-4 text-4xl text-ink transition-colors hover:text-accent lg:text-5xl"
          >
            See everything <span aria-hidden="true">→</span>
          </a>
        </div>
      </div>

      {/* progress bar */}
      <div className="absolute inset-x-8 bottom-8 z-10 lg:inset-x-12">
        <div className="flex items-center gap-4">
          <span className="label-mono text-ink/50">03</span>
          <div className="h-px flex-1 bg-ink/15">
            <div className="work-progress h-full origin-left scale-x-0 bg-accent" style={{ height: 2 }} />
          </div>
          <span className="label-mono text-ink/50">11</span>
        </div>
      </div>
    </section>
  );
}