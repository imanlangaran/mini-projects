import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

const STEPS = [
  {
    num: "01",
    title: "The Brief",
    desc: "We walk the land, read the deed, and listen hard. Scope, budget, and the shape of the life starting there get written down before a line is drawn.",
  },
  {
    num: "02",
    title: "The Scheme",
    desc: "Massing, section, and light are resolved in physical models and drawings you can hold. Two rounds, then we set the design in stone.",
  },
  {
    num: "03",
    title: "The Build",
    desc: "Our crews take over. Framing to finish, each trade is vetted, each material approved against a signed specification. You will know where your money went.",
  },
  {
    num: "04",
    title: "The Passage",
    desc: "Staging, photography, and a quiet release. We qualify every inquiry and hand the keys — and the story of the house — to its new owner.",
  },
];

export default function Process() {
  const section = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      // Draw the vertical line of progress as the steps scroll by
      gsap.fromTo(
        ".process-line-fill",
        { scaleY: 0 },
        {
          scaleY: 1,
          ease: "none",
          transformOrigin: "top center",
          scrollTrigger: {
            trigger: ".process-list",
            start: "top 60%",
            end: "bottom 60%",
            scrub: true,
          },
        }
      );

      gsap.utils.toArray<HTMLElement>(".process-step").forEach((step) => {
        gsap.fromTo(
          step,
          {
            autoAlpha: 0,
            y: 40,
          },
          {
            autoAlpha: 1,
            y: 0,
            duration: 0.9,
            ease: "power2.out",
            scrollTrigger: {
              trigger: step,
              start: "top 78%",
              toggleActions: "play none none reverse",
            },
          }
        );
      });
    },
    { scope: section }
  );

  return (
    <section ref={section} id="process" aria-label="How we work" className="relative py-28 lg:py-40">
      <div className="mx-auto max-w-[1400px] px-4 sm:px-8 lg:px-12">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="label-mono mb-8 flex items-center gap-3 text-ink/50">
              <span className="inline-block h-px w-10 bg-accent" />
              THE PROCESS / 04
            </p>
            <h3 className="display-lg text-6xl lg:text-7xl">
              From ground
              <br />
              <span className="italic text-accent">to hand-off.</span>
            </h3>
          </div>
          <p className="max-w-sm text-lg leading-relaxed text-ink/70">
            Nothing is sold before it is built. Four phases, one team, total accountability — from the first walk to the
            final handshake.
          </p>
        </div>

        <div className="process-list mt-16 lg:mt-20">
          <div className="relative">
            {/* base + animated fill line */}
            <div className="absolute left-[5px] top-0 h-full w-px bg-ink/12 lg:left-1/2" aria-hidden="true" />
            <div className="process-line-fill absolute left-[5px] top-0 h-full w-px bg-accent lg:left-1/2" aria-hidden="true" />

            <div className="grid gap-16 lg:grid-cols-2 lg:gap-x-24 lg:gap-y-0">
              {STEPS.map((step, i) => (
                <div
                  key={step.num}
                  className={`process-step relative pl-10 ${i % 2 === 1 ? "lg:mt-32" : ""} ${
                    i === 3 ? "lg:col-start-1 lg:row-start-1" : ""
                  }`}
                  style={{ gridColumn: i % 2 === 0 ? "1" : "2" }}
                >
                  <span
                    className="absolute left-0 top-1 grid h-[11px] w-[11px] place-items-center rounded-full border border-accent bg-paper"
                    style={{ left: "0.06rem" }}
                    aria-hidden="true"
                  >
                    <span className="block h-[3px] w-[3px] rounded-full bg-accent" />
                  </span>
                  <p className="label-mono mb-3 text-ink/50">PHASE {step.num}</p>
                  <h4 className="display-lg text-3xl lg:text-4xl">{step.title}</h4>
                  <p className="mt-4 max-w-sm text-ink/70">{step.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}