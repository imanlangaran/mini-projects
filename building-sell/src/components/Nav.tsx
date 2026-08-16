import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

const NAV_LINKS = [
  { label: "Manifesto", href: "#manifesto", index: "01" },
  { label: "Capabilities", href: "#capabilities", index: "02" },
  { label: "Work", href: "#work", index: "03" },
  { label: "Process", href: "#process", index: "04" },
];

export default function Nav() {
  const nav = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const ctx = gsap.context(() => {
        // Appear after the intro veil clears.
        gsap.fromTo(
          ".nav-inner",
          { y: -24, autoAlpha: 0 },
          { y: 0, autoAlpha: 1, duration: 0.9, ease: "power3.out", delay: 1.9 }
        );
      }, nav);

      return () => ctx.revert();
    },
    { scope: nav }
  );

  return (
    <header ref={nav} className="fixed inset-x-0 top-0 z-50">
      <div className="nav-inner opacity-0">
        <nav
          aria-label="Primary"
          className="mx-auto flex max-w-[1400px] items-center justify-between px-4 py-5 sm:px-8 lg:px-12"
        >
          <a
            href="#top"
            className="label-mono flex items-center gap-3 text-ink transition-opacity hover:opacity-70"
            aria-label="MERIDIAN — back to top"
          >
            <span className="grid h-6 w-6 place-items-center border border-ink/40">
              <span className="block h-2 w-2 bg-accent" />
            </span>
            MERIDIAN
          </a>

          <ul className="hidden items-center gap-8 md:flex">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  className="label-mono group inline-flex items-center gap-2 text-ink/80 transition-colors hover:text-ink"
                >
                  <span className="text-accent">{link.index}</span>
                  <span className="relative">
                    {link.label}
                    <span className="absolute -bottom-1 left-0 h-px w-0 bg-ink transition-all duration-300 group-hover:w-full" />
                  </span>
                </a>
              </li>
            ))}
          </ul>

          <a
            href="#contact"
            className="label-mono hidden border border-ink/40 px-4 py-2 text-ink transition-colors hover:bg-ink hover:text-paper sm:block"
          >
            START A PROJECT
          </a>

          {/* Mobile: index + menu hint */}
          <button
            type="button"
            aria-label="Open menu"
            className="grid h-9 w-9 place-items-center border border-ink/40 md:hidden"
            onClick={() => document.querySelector("#manifesto")?.scrollIntoView({ behavior: "smooth" })}
          >
            <span className="block h-3.5 w-5 space-y-1.5" aria-hidden="true">
              <span className="block h-px w-full bg-ink" />
              <span className="block h-px w-3/4 bg-ink" />
            </span>
          </button>
        </nav>
      </div>
    </header>
  );
}