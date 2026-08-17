import { useGSAP } from "@gsap/react";
import { SKILL_GROUPS } from "../../data/skills";
import { registerSectionReveals } from "../../animations/sectionReveals";
import TextReveal from "../animations/TextReveal";

/**
 * Skills section — calm list with staggered reveals. The 3D constellation
 * (orbital nodes) lives in the shared scene behind, revealed by the camera.
 */
export default function Skills() {
  useGSAP(
    () => {
      const el = document.getElementById("skills");
      if (el) registerSectionReveals(el);
    },
    { dependencies: [] }
  );

  return (
    <section id="skills" className="relative mx-auto max-w-5xl px-6 py-32 md:px-10 md:py-44">
      <span className="sec-label label-mono text-accent">03 — Skills</span>
      <h2 className="sec-title mt-8 display-lg text-ink">
        <TextReveal text={"The instruments\nI trust."} />
      </h2>

      <div className="mt-16 space-y-10">
        {SKILL_GROUPS.map((group) => (
          <div key={group.label} data-reveal>
            <div className="flex items-baseline justify-between gap-6">
              <h3 className="text-xl text-ink md:text-2xl">{group.label}</h3>
              <span className="label-mono text-muted">{group.level}%</span>
            </div>
            <div
              className="mt-3 h-1 overflow-hidden bg-surface"
              role="progressbar"
              aria-label={`${group.label} proficiency`}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={group.level}
            >
              <div
                className="h-full bg-accent transition-[width] duration-700"
                style={{ width: `${group.level}%` }}
              />
            </div>
            <p className="mt-3 flex flex-wrap gap-2">
              {group.keywords.map((k) => (
                <span
                  key={k}
                  className="label-mono rounded-full border border-hairline px-3 py-1 text-muted"
                >
                  {k}
                </span>
              ))}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}