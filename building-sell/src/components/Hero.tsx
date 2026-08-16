import { useRef, useEffect, useState } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import HeroScene from "../three/HeroScene";

const HEADLINE = ["We build homes", "worth selling."];

function usePrefersReducedMotion() {
  const [reduce, setReduce] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduce(mq.matches);
    const onChange = (e: MediaQueryListEvent) => setReduce(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduce;
}

export default function Hero() {
  const section = useRef<HTMLElement>(null);
  const reduce = usePrefersReducedMotion();

  useGSAP(
    () => {
      const sectionEl = section.current!;

      // Mount the 3D scene once (canvas host is always rendered under the
      // intro fade). Degrades gracefully if WebGL is unavailable.
      let scene: HeroScene | null = null;
      try {
        scene = new HeroScene(sectionEl.querySelector(".hero-canvas") as HTMLElement);
        scene.setMotion(!reduce);
      } catch {
        scene = null;
      }

      const intro = gsap.timeline({ defaults: { ease: "power3.out" } });

      intro
        // intro veil lifts
        .to(".intro-veil", { yPercent: -100, duration: 1.0, ease: "power4.inOut" }, 0.3)
        // headline clip reveals
        .fromTo(".line-inner", { yPercent: 110 }, { yPercent: 0, duration: 1.1, stagger: 0.14 }, 0.55)
        // supporting copy + copy row
        .fromTo(".hero-support", { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.8 }, 1.2)
        .fromTo(".hero-meta", { autoAlpha: 0, y: 12 }, { autoAlpha: 1, y: 0, duration: 0.8 }, 1.35);

      // 3D canvas drift-in (canvas is present from mount; the scene runs
      // underneath while this fade completes)
      gsap.fromTo(
        ".hero-canvas",
        { autoAlpha: 0, y: 60, scale: 0.94 },
        { autoAlpha: 1, y: 0, scale: 1, duration: 1.6, ease: "power3.out", delay: 0.9 }
      );

      // enormous outline word drifts past behind the headline
      gsap.to(".hero-watermark", {
        yPercent: 18,
        ease: "none",
        scrollTrigger: {
          trigger: sectionEl,
          start: "top top",
          end: "bottom top",
          scrub: true,
        },
      });

      // canvas parallaxes upward as user scrolls away (subtle depth)
      gsap.to(".hero-canvas", {
        yPercent: -12,
        ease: "none",
        scrollTrigger: {
          trigger: sectionEl,
          start: "top top",
          end: "bottom top",
          scrub: true,
        },
      });

      gsap.to(".scroll-cue", { opacity: 0.25, repeat: -1, yoyo: true, duration: 1.1, ease: "sine.inOut" });

      return () => scene?.dispose();
    },
    { scope: section, dependencies: [reduce] }
  );

  return (
    <section
      ref={section}
      id="top"
      aria-label="Introduction"
      className="relative flex min-h-screen flex-col overflow-hidden"
    >
      {/* intro veil */}
      <div className="intro-veil pointer-events-none absolute inset-0 z-30 bg-paper" aria-hidden="true" />

      {/* watermarked background word */}
      <div className="hero-watermark pointer-events-none select-none absolute inset-x-0 top-[6%] z-0 flex justify-center overflow-hidden" aria-hidden="true">
        <span className="display-xl text-center text-[20vw] leading-none text-ink/[0.05]">REFINED</span>
      </div>

      {/* 3D canvas container */}
      <div className="hero-canvas canvas-abs z-[1]" aria-hidden="true" />

      <div className="relative z-10 mx-auto flex w-full max-w-[1400px] flex-col justify-between gap-12 px-4 pt-28 pb-8 sm:px-8 lg:px-12 lg:pt-32">
        {/* eyebrow */}
        <p className="hero-meta label-mono flex items-center gap-3 text-ink/60" style={{ opacity: 0 }}>
          <span className="inline-block h-px w-10 bg-accent" />
          A design-build development studio
        </p>

        {/* headline */}
        <h1 className="display-xl mt-6" lang="en">
          {HEADLINE.map((line, i) => (
            <span key={line} className="reveal-mask block">
              <span className="line-inner block will-change-transform">
                {i === 1 ? (
                  <em className="normal-case font-serif italic text-accent">selling.</em>
                ) : (
                  line
                )}
              </span>
            </span>
          ))}
        </h1>

        <div className="hero-support flex flex-col gap-10 md:flex-row md:items-end md:justify-between" style={{ opacity: 0 }}>
          <p className="max-w-md text-lg leading-relaxed text-ink/75">
            From first sketch to sold sign — we conceive, construct, and market a small number of exceptional homes every year.
          </p>
          <div className="hero-meta flex items-center gap-4 self-start md:self-auto">
            <a
              href="#work"
              className="group inline-flex items-center gap-3 border border-ink bg-ink px-6 py-3.5 text-sm font-medium text-paper transition-colors hover:bg-transparent hover:text-ink"
            >
              View the work
              <span
                aria-hidden="true"
                className="transition-transform duration-300 group-hover:translate-x-1"
              >
                →
              </span>
            </a>
            <a
              href="#capabilities"
              className="label-mono underline-offset-4 text-ink/70 transition-colors hover:text-ink hover:underline"
            >
              How we work ↓
            </a>
          </div>
        </div>
      </div>

      {/* bottom meta strip + scroll cue */}
      <div className="hero-meta relative z-10 mx-auto flex w-full max-w-[1400px] items-center justify-between px-4 pb-7 sm:px-8 lg:px-12" style={{ opacity: 0 }}>
        <span className="label-mono text-ink/50">Est. 2016 — 03.4061° N</span>
        <span className="scroll-cue label-mono flex items-center gap-2 text-ink/50">
          <span className="inline-block h-8 w-px bg-ink/30" aria-hidden="true" />
          SCROLL
        </span>
      </div>
    </section>
  );
}