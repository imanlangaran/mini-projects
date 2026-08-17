import { useGSAP } from "@gsap/react";
import { registerSectionReveals } from "../../animations/sectionReveals";
import TextReveal from "../animations/TextReveal";

/**
 * Calm narrative section — typography and whitespace carry the weight.
 * Uses the shared registerSectionReveals factory for its reveals.
 */
export default function About() {
  useGSAP(
    () => {
      const el = document.getElementById("about");
      if (el) registerSectionReveals(el);
    },
    { dependencies: [] }
  );

  return (
    <section
      id="about"
      className="relative mx-auto max-w-5xl px-6 py-32 md:px-10 md:py-44"
    >
      <span className="sec-label label-mono text-accent">01 — About</span>

      <h2 className="sec-title mt-8 display-lg text-ink" data-parallax="0.06">
        <TextReveal text={"I build quiet, precise\ndigital instruments."} />
      </h2>

      <p className="sec-paragraph mt-10 max-w-prose text-lg text-ink/85 leading-relaxed">
        <TextReveal
          text={
            "Three years shaping interfaces where every pixel has a job.\n" +
            "I care about the moment between click and response — the easing,\n" +
            "the weight, the narrative a scroll can carry."
          }
        />
      </p>

      <div className="mt-16 grid grid-cols-2 gap-8 md:grid-cols-3">
        {[
          ["03+", "years of practice"],
          ["12", "shipments a year"],
          ["∞", "curiosity"],
        ].map(([num, label]) => (
          <div key={label} data-reveal>
            <span className="display-lg text-ink">{num}</span>
            <p className="label-mono mt-2 text-muted">{label}</p>
          </div>
        ))}
      </div>
    </section>
  );
}