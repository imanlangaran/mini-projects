import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

const CAPABILITIES = [
  {
    index: "02",
    num: "A",
    title: "Design",
    blurb:
      "Every project begins as a conversation with the land. We draw, model, and prototype in-house until the massing, light, and material feel inevitable.",
    points: ["Architecture & massing", "Interior + material", "Landscape integration", "Light studies"],
  },
  {
    index: "03",
    num: "B",
    title: "Build",
    blurb:
      "Our own crews and trusted trades finish every detail to a signed-off standard. No hand-offs, no dilution of intent — the people who drew it build it.",
    points: ["General contracting", "Custom fabrication", "Quality assurance", "Procurement"],
  },
  {
    index: "04",
    num: "C",
    title: "Sell",
    blurb:
      "Marketing begins at groundbreak. We photograph, stage, and curate a release that finds the exact buyer your home was built for.",
    points: ["Positioning & naming", "Editorial photography", "Curated releases", "Buyer qualification"],
  },
];

export default function Capabilities() {
  const section = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const panels = gsap.utils.toArray<HTMLElement>(".cap-panel");
      if (panels.length < 2) return;

      // Single pin on the container + one scrubbed timeline of pure
      // transforms. Each panel is a full-viewport absolute layer; the
      // stack reads: current panel slides up off-stage while the next
      // rises from below. One pin = one spacer = no layout juggling.
      const tl = gsap.timeline({
        defaults: { ease: "none" },
        scrollTrigger: {
          trigger: section.current,
          start: "top top",
          end: () => "+=" + (panels.length + 1) * window.innerHeight,
          pin: true,
          scrub: 1,
        },
      });

      panels.forEach((panel, i) => {
        if (i === 0) {
          tl.to(panel, { yPercent: -100 }, 0);
          return;
        }
        // next panel rises into place as the previous one leaves
        tl.fromTo(panel, { yPercent: 100 }, { yPercent: 0 }, i - 1);
      });
    },
    { scope: section }
  );

  return (
    <section ref={section} id="capabilities" aria-label="What we do" className="relative">
      <div className="mx-auto max-w-[1400px] px-4 sm:px-8 lg:px-12">
        <div className="flex items-end justify-between pb-12 lg:pb-0">
          <p className="label-mono flex items-center gap-3 text-ink/50">
            <span className="inline-block h-px w-10 bg-accent" />
            CAPABILITIES / 02
          </p>
        </div>
      </div>

      <div className="cap-list relative h-[300vh]">
        {CAPABILITIES.map((cap) => (
          <article
            key={cap.title}
            className="cap-panel absolute inset-0 flex h-screen w-full flex-col justify-center bg-paper px-4 sm:px-8 lg:px-12"
          >
            <div className="mx-auto grid w-full max-w-[1400px] gap-10 lg:grid-cols-12 lg:items-center">
              <div className="lg:col-span-4">
                <span className="display-xl block text-[9rem] leading-none text-ink/[0.06] lg:text-[13rem]">{cap.num}</span>
              </div>
              <div className="lg:col-span-5">
                <p className="label-mono mb-5 text-ink/50">STEP {cap.index}</p>
                <h3 className="display-lg text-5xl lg:text-7xl">{cap.title}</h3>
                <p className="mt-6 max-w-md text-lg leading-relaxed text-ink/70">{cap.blurb}</p>
              </div>
              <div className="hidden lg:col-span-3 lg:block">
                <ul className="space-y-5 border-l border-hairline pl-6">
                  {cap.points.map((p) => (
                    <li key={p} className="label-mono flex items-center gap-3 text-ink/70">
                      <span className="inline-block h-1 w-1 rounded-full bg-accent" aria-hidden="true" />
                      {p}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}