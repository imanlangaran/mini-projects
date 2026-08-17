import { useGSAP } from "@gsap/react";
import { BRAND, SOCIALS } from "../../data/brand";
import { registerSectionReveals } from "../../animations/sectionReveals";
import TextReveal from "../animations/TextReveal";
import MagneticButton from "../MagneticButton";

/**
 * Closing statement — the destination of the whole journey. Magnetic email
 * CTA with the accent glow.
 */
export default function Contact() {
  useGSAP(
    () => {
      const el = document.getElementById("contact");
      if (el) registerSectionReveals(el);
    },
    { dependencies: [] }
  );

  return (
    <section
      id="contact"
      className="relative mx-auto flex min-h-screen max-w-5xl flex-col items-start justify-center px-6 py-32 md:px-10 md:py-44"
    >
      <span className="sec-label label-mono text-accent">04 — Contact</span>

      <h2 className="sec-title mt-8 display-xl text-ink" data-parallax="0.05">
        <TextReveal text={"LET'S BUILD\nSOMETHING\nMEMORABLE."} />
      </h2>

      <MagneticButton
        as="a"
        href={`mailto:${BRAND.email}`}
        ariaLabel={`Email ${BRAND.name} at ${BRAND.email}`}
        className="mt-14 inline-flex min-h-[56px] items-center gap-4 rounded-full border border-hairline px-8 py-4 label-mono text-ink transition-colors hover:border-accent hover:text-accent focus-visible:border-accent"
      >
        <span aria-hidden className="h-2 w-2 rounded-full bg-accent" />
        {BRAND.email}
      </MagneticButton>

      <div className="mt-16 flex flex-wrap gap-6 md:gap-8" data-reveal>
        {SOCIALS.map((s) => (
          <a
            key={s.label}
            href={s.href}
            target="_blank"
            rel="noreferrer"
            aria-label={`${BRAND.name} on ${s.label} (opens in a new tab)`}
            data-cursor=""
            className="label-mono px-2 py-3 text-muted transition-colors hover:text-ink"
          >
            {s.label} <span aria-hidden>↗</span>
          </a>
        ))}
      </div>
    </section>
  );
}