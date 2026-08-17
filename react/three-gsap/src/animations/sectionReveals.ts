import gsap from "gsap";
import { EASE } from "./easing";

/**
 * Shared ScrollTrigger factory applied to every content section. Centralizes
 * the standard reveal patterns so section components stay declarative:
 *
 *   <header class="sec-label">…</header>
 *   <h2 class="sec-title"><span class="reveal-mask"><span class="line-inner">…</span></span></h2>
 *   <p class="sec-paragraph"><span class="line-inner">…</span></p>
 *   <div data-parallax="0.15">…</div>
 *
 * All triggers are created inside the caller's gsap.context (reverted on
 * unmount / StrictMode remount).
 */
export function registerSectionReveals(section: HTMLElement) {
  const els = {
    label: section.querySelectorAll(".sec-label"),
    title: section.querySelectorAll(".sec-title .line-inner"),
    paragraph: section.querySelectorAll(".sec-paragraph .line-inner"),
    rows: section.querySelectorAll("[data-reveal]"),
    parallax: section.querySelectorAll<HTMLElement>("[data-parallax]"),
  };

  const tl = gsap.timeline({
    defaults: { ease: EASE.OUT, duration: 1 },
    scrollTrigger: {
      trigger: section,
      start: "top 72%",
      toggleActions: "play none none reverse",
    },
  });

  if (els.label.length) {
    tl.from(els.label, { autoAlpha: 0, y: 14, duration: 0.7 }, 0);
  }
  if (els.title.length) {
    tl.from(els.title, { yPercent: 110, duration: 1.1 }, 0.05);
  }
  if (els.paragraph.length) {
    tl.from(els.paragraph, { yPercent: 110, stagger: 0.08, duration: 0.9 }, 0.15);
  }
  if (els.rows.length) {
    tl.from(
      els.rows,
      { autoAlpha: 0, y: 24, stagger: 0.08, duration: 0.8 },
      0.2
    );
  }

  // Parallax drift — scrubbed, no timeline dependency.
  if (els.parallax.length && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    els.parallax.forEach((el) => {
      const speed = Number(el.dataset.parallax ?? 0.12);
      gsap.fromTo(
        el,
        { y: () => speed * 120 },
        {
          y: () => -speed * 120,
          ease: "none",
          scrollTrigger: { trigger: section, start: "top bottom", end: "bottom top", scrub: true },
        }
      );
    });
  }

  return tl;
}