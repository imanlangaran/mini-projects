import { useRef, useState } from "react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { useLenis } from "../hooks/useLenis";
import { usePrefersReducedMotion } from "../hooks/usePrefersReducedMotion";
import { buildEntranceTimeline } from "../animations/entranceTimeline";
import { setupMasterTimeline, destroyMasterTimeline } from "../animations/masterTimeline";
import { setNavActive, setPointer, cameraRig } from "../state/cameraRig";
import type { NavId } from "../data/brand";
import Nav from "./navigation/Nav";
import Hero from "./sections/Hero";
import About from "./sections/About";
import Work from "./sections/Work";
import Skills from "./sections/Skills";
import Contact from "./sections/Contact";
import Footer from "./sections/Footer";
import CustomCursor from "./CustomCursor";
import Loader from "./Loader";

type Props = {
  introDone: boolean;
  onIntroDone: () => void;
};

/**
 * The experience shell: owns Lenis, the loader gate, the cinematic entrance
 * timeline and nav↔camera navigation. The fixed 3D canvas is rendered by
 * App beneath this, so the DOM here layers on top (z-10).
 */
export default function Layout({ introDone, onIntroDone }: Props) {
  const mainRef = useRef<HTMLDivElement>(null);
  const lenis = useLenis();
  const reduced = usePrefersReducedMotion();
  const [activeId, setActiveId] = useState<NavId | null>(null);

  // Forward pointer to the camera rig for parallax.
  useGSAP(
    () => {
      const onMove = (e: PointerEvent) => {
        setPointer((e.clientX / window.innerWidth) * 2 - 1, -(e.clientY / window.innerHeight) * 2 + 1);
        // Smooth the pointer inside the rig for damped parallax.
        cameraRig.mouseSmooth.x += (cameraRig.mouse.x - cameraRig.mouseSmooth.x) * 0.06;
        cameraRig.mouseSmooth.y += (cameraRig.mouse.y - cameraRig.mouseSmooth.y) * 0.06;
      };
      window.addEventListener("pointermove", onMove, { passive: true });
      return () => window.removeEventListener("pointermove", onMove);
    },
    []
  );

  // Cinematic entrance — runs once when the loader completes. Skipped
  // entirely under reduced-motion (content is immediately visible).
  useGSAP(
    () => {
      if (!introDone || !mainRef.current) return;

      let tl: ReturnType<typeof buildEntranceTimeline> | undefined;
      if (!reduced) {
        tl = buildEntranceTimeline(mainRef.current);
      }

      // Arm the scroll-driven camera and let Lenis go as soon as the loader
      // has lifted. Re-measure pinned/scrub positions against final layout.
      setupMasterTimeline();
      lenis.start();
      requestAnimationFrame(() => ScrollTrigger.refresh());

      return () => {
        destroyMasterTimeline();
        tl?.kill();
      };
    },
    { dependencies: [introDone, reduced] }
  );

  // Navigation: glide the camera to a section. "top" means scroll to 0.
  const navigate = (id: NavId | "top") => {
    if (id === "top") {
      setActiveId(null);
      setNavActive(null);
      lenis.scrollTo(0, { duration: 1.8 });
      return;
    }
    setActiveId(id);
    setNavActive(id);
    const target = document.getElementById(id);
    if (target) lenis.scrollTo(`#${id}`, { duration: 1.6 });
  };

  return (
    <div id="app-shell" ref={mainRef} className="relative z-10">
      {!reduced && <CustomCursor />}
      <Nav activeId={activeId} onNavigate={navigate} />

      <main>
        <Hero onNavigate={navigate} />
        <About />
        <Work />
        <Skills />
        <Contact />
      </main>

      <Footer onNavigate={navigate} />

      {!introDone && <Loader onComplete={onIntroDone} />}
    </div>
  );
}