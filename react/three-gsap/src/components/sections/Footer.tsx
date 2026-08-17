import { BRAND, NAV_LINKS, type NavId } from "../../data/brand";

type Props = {
  onNavigate: (id: NavId | "top") => void;
};

/**
 * Ending. A slowly settling watermark of the name, the monogram, a small
 * nav and colophon — plus a smooth return-to-top through the same corridor.
 */
export default function Footer({ onNavigate }: Props) {
  const year = new Date().getFullYear();

  return (
    <footer className="relative overflow-hidden border-t border-hairline px-6 py-20 md:px-10">
      <div
        className="pointer-events-none absolute -bottom-10 left-1/2 -translate-x-1/2 select-none whitespace-nowrap display-xl text-ink/5"
        aria-hidden
      >
        {BRAND.name}
      </div>

      <div className="relative flex flex-col items-center gap-8">
        <a
          href="#top"
          data-cursor=""
          aria-label="Back to top"
          className="flex h-12 w-12 items-center justify-center rounded-full border border-hairline label-mono text-ink transition-colors hover:border-accent hover:text-accent md:h-16 md:w-16"
          onClick={(e) => {
            e.preventDefault();
            onNavigate("top");
          }}
        >
          {BRAND.monogram}
        </a>

        <nav aria-label="Footer" className="flex flex-wrap justify-center gap-4 md:gap-6">
          {NAV_LINKS.map(({ id, label }) => (
            <a
              key={id}
              href={`#${id}`}
              data-cursor=""
              className="label-mono px-2 py-3 text-muted transition-colors hover:text-ink"
              onClick={(e) => {
                e.preventDefault();
                onNavigate(id);
              }}
            >
              {label}
            </a>
          ))}
        </nav>

        <p className="label-mono text-muted">
          © {year} {BRAND.name} — Built with React, Three.js &amp; GSAP.
        </p>
      </div>
    </footer>
  );
}