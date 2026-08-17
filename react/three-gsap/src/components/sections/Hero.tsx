import { BRAND, type NavId } from "../../data/brand";
import TextReveal from "../animations/TextReveal";

type Props = {
  onNavigate: (id: NavId | "top") => void;
};

/**
 * Full-viewport editorial hero. The 3D corridor renders behind (fixed
 * canvas). This component owns the foreground typography; the entrance
 * timeline in Layout drives the reveals via .hero-line / [data-hero-fade].
 */
export default function Hero({ onNavigate }: Props) {
  return (
    <section
      id="top"
      className="relative flex min-h-screen flex-col justify-center px-6 md:px-10"
    >
      <div className="label-mono text-muted" data-hero-fade>
        {BRAND.name} — {BRAND.role}
      </div>

      <h1 className="mt-6 display-xl text-ink">
        <TextReveal text={BRAND.heroTitle} className="hero-line" />
      </h1>

      <p className="mt-8 max-w-prose text-base text-muted md:text-lg" data-hero-fade>
        {BRAND.heroSubtitle}
        <br />
        I design systems, write code, and animate the space between.
      </p>

      <a
        href="#work"
        aria-label="Explore my work"
        data-scroll-cue
        data-cursor=""
        className="group mt-12 inline-flex min-h-[48px] items-center gap-3 label-mono text-ink transition-colors hover:text-accent"
        onClick={(e) => {
          e.preventDefault();
          onNavigate("work");
        }}
      >
        <span aria-hidden className="h-px w-8 bg-ink transition-all duration-300 group-hover:w-12 group-hover:bg-accent" />
        EXPLORE
      </a>

      <div
        className="pointer-events-none absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
        aria-hidden
        data-scroll-cue
      >
        <span className="label-mono text-muted">SCROLL</span>
        <span className="block h-10 w-px bg-gradient-to-b from-ink/50 to-transparent" />
      </div>
    </section>
  );
}