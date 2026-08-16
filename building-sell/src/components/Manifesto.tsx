import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

const STATS = [
  { value: "09", label: "Homes delivered" },
  { value: "$4.2M", label: "Median sale price" },
  { value: "6wk", label: "Avg. time to sell" },
  { value: "100%", label: "Design-led end to end" },
];

export default function Manifesto() {
  const section = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      gsap.fromTo(
        ".manifesto-line",
        { yPercent: 110 },
        {
          yPercent: 0,
          stagger: 0.09,
          ease: "power3.out",
          duration: 1.0,
          scrollTrigger: { trigger: ".manifesto-head", start: "top 78%", toggleActions: "play none none reverse" },
        }
      );
      gsap.fromTo(
        ".manifesto-stat",
        { autoAlpha: 0, y: 24 },
        {
          autoAlpha: 1,
          y: 0,
          stagger: 0.08,
          ease: "power3.out",
          duration: 0.8,
          scrollTrigger: { trigger: ".manifesto-stats", start: "top 85%", toggleActions: "play none none reverse" },
        }
      );
    },
    { scope: section }
  );

  return (
    <section ref={section} id="manifesto" aria-label="Manifesto" className="relative overflow-hidden py-28 lg:py-40">
      <div className="mx-auto max-w-[1400px] px-4 sm:px-8 lg:px-12">
        <div className="manifesto-head">
          <p className="label-mono mb-8 flex items-center gap-3 text-ink/50">
            <span className="inline-block h-px w-10 bg-accent" />
            MANIFESTO / 01
          </p>
          <h2 className="display-lg max-w-4xl">
            <span className="reveal-mask block">
              <span className="manifesto-line block">A home is not a product. It is a place</span>
            </span>
            <span className="reveal-mask block">
              <span className="manifesto-line block">
                where a life <span className="italic text-accent">takes shape.</span>
              </span>
            </span>
            <span className="reveal-mask block">
              <span className="manifesto-line block">We treat the ground as sacred, the</span>
            </span>
            <span className="reveal-mask block">
              <span className="manifesto-line block">build as craft, and the sale as trust.</span>
            </span>
          </h2>
          <p className="mt-10 max-w-xl text-lg leading-relaxed text-ink/70">
            MERIDIAN is a small studio — designers and builders and sellers working as one team. We deliver a dozen
            homes a decade, each one uncommonly considered, each one engineered to find the owner who deserves it.
          </p>
        </div>

        {/* stats */}
        <dl className="manifesto-stats mt-20 grid grid-cols-2 gap-px overflow-hidden border-t border-hairline border-l lg:grid-cols-4">
          {STATS.map((s) => (
            <div key={s.label} className="manifesto-stat border-r border-b border-hairline bg-paper/60 px-8 py-10">
              <dt className="order-2 block text-sm text-ink/60">{s.label}</dt>
              <dd className="order-1 block">
                <span className="display-lg text-[2.75rem] text-ink">{s.value}</span>
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}