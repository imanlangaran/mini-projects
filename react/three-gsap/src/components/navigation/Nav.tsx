import { BRAND, NAV_LINKS, type NavId } from "../../data/brand";
import { setNavHover } from "../../state/cameraRig";
import { cn } from "../../utils/cn";

type Props = {
  activeId: NavId | null;
  onNavigate: (id: NavId | "top") => void;
};

/**
 * Fixed top bar. Each link carries data-scene-target + data-nav-item so the
 * entrance timeline and the camera rig can both find it. Clicking glides the
 * camera via scrollTo and highlights the active monolith.
 *
 * On small screens the brand shortens and links drop the index numerals so
 * the row fits without clipping (≥44px tap targets).
 */
export default function Nav({ activeId, onNavigate }: Props) {
  return (
    <header className="fixed inset-x-0 top-0 z-40">
      <div className="flex items-center justify-between gap-4 px-5 py-4 sm:px-6 sm:py-5 md:px-10">
        <a
          href="#top"
          data-cursor=""
          data-nav-item=""
          aria-label={`${BRAND.name} — back to top`}
          className="label-mono text-ink transition-colors hover:text-accent"
          onClick={(e) => {
            e.preventDefault();
            onNavigate("top");
          }}
        >
          <span className="hidden sm:inline">
            {BRAND.monogram} // {BRAND.name}
          </span>
          <span className="inline sm:hidden">{BRAND.monogram}</span>
        </a>

        <nav aria-label="Primary" className="flex items-center gap-1 sm:gap-3 md:gap-9">
          {NAV_LINKS.map(({ id, index, label }) => (
            <a
              key={id}
              href={`#${id}`}
              data-scene-target={id}
              data-nav-item=""
              data-cursor=""
              aria-current={activeId === id ? "true" : undefined}
              className={cn(
                "group relative label-mono px-2 py-3 text-muted transition-colors hover:text-ink",
                "min-h-[44px] flex items-center",
                activeId === id && "text-ink"
              )}
              onPointerEnter={() => setNavHover(id)}
              onPointerLeave={() => setNavHover(null)}
              onClick={(e) => {
                e.preventDefault();
                onNavigate(id);
              }}
            >
              <span className="mr-1 hidden text-accent/80 sm:inline">{index}</span>
              <span>{label}</span>
              <span className="absolute -bottom-0.5 left-0 h-px w-full origin-left scale-x-0 bg-accent transition-transform duration-300 group-hover:scale-x-100" />
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}