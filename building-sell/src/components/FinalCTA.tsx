import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

export default function FinalCTA() {
  const section = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const sectionEl = section.current!;
      gsap.fromTo(
        ".cta-line",
        { yPercent: 110 },
        {
          yPercent: 0,
          stagger: 0.1,
          ease: "power3.out",
          duration: 1.0,
          scrollTrigger: { trigger: sectionEl, start: "top 80%", toggleActions: "play none none reverse" },
        }
      );
      gsap.fromTo(
        ".cta-sub",
        { autoAlpha: 0, y: 18 },
        {
          autoAlpha: 1,
          y: 0,
          duration: 0.9,
          stagger: 0.12,
          scrollTrigger: { trigger: sectionEl, start: "top 70%", toggleActions: "play none none reverse" },
        }
      );
    },
    { scope: section }
  );

  return (
    <section
      ref={section}
      id="contact"
      aria-label="Start a project"
      className="cta-block relative flex min-h-[90vh] flex-col justify-center overflow-hidden bg-ink text-paper"
    >
      {/* faint watermark */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.08]" aria-hidden="true">
        <div className="pointer-events-none absolute inset-0 [background-image:repeating-linear-gradient(90deg,transparent,transparent_22px,rgba(243,238,229,0.5)_22px,rgba(243,238,229,0.5)_23px)]" />
      </div>

      <div className="relative z-10 mx-auto w-full max-w-[1400px] px-4 py-24 sm:px-8 lg:px-12">
        <p className="label-mono mb-10 flex items-center gap-3 text-paper/50">
          <span className="inline-block h-px w-10 bg-accent" />
          THE OFFER / 05
        </p>

        <h3 className="display-xl text-[13vw] leading-[0.92] sm:text-[10vw] lg:text-[8.5vw]">
          <span className="reveal-mask block">
            <span className="cta-line block">Make us an</span>
          </span>
          <span className="reveal-mask block">
            <span className="cta-line block italic text-accent">offer worth </span>
          </span>
          <span className="reveal-mask block">
            <span className="cta-line block">building.</span>
          </span>
        </h3>

        <div className="cta-sub mt-14 flex flex-col gap-8 md:flex-row md:items-center md:justify-between">
          <p className="max-w-sm text-lg text-paper/70">
            One or two commissions a year. If you have ground, a vision, and patience for craft — write to us.
          </p>
          <div className="flex flex-wrap items-center gap-4">
            <a
              href="mailto:studio@meridian.build"
              className="group inline-flex items-center gap-4 border border-paper/70 px-8 py-4 text-sm font-medium uppercase tracking-widest text-paper transition-colors hover:bg-paper hover:text-ink"
            >
              studio@meridian.build
              <span className="transition-transform duration-300 group-hover:translate-x-1" aria-hidden="true">
                →
              </span>
            </a>
            <a
              href="#top"
              className="label-mono text-paper/60 transition-colors hover:text-paper"
            >
              Back to top ↑
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}