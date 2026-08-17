import { lazy, Suspense, useState } from "react";
import Layout from "./components/layout";
import ErrorBoundary from "./components/ErrorBoundary";

// R3F bundle is heavy — lazy so it doesn't block first paint. The loader
// burns time compiling it behind the veil.
const Experience = lazy(() => import("./components/three/Experience"));

export default function App() {
  const [introDone, setIntroDone] = useState(false);

  return (
    <div className="relative">
      {/* Fixed 3D corridor behind everything — isolated in an ErrorBoundary so
          a scene crash never blanks the DOM experience. */}
      <div className="canvas-fixed" aria-hidden>
        <ErrorBoundary>
          <Suspense fallback={null}>
            <Experience deferred={introDone} />
          </Suspense>
        </ErrorBoundary>
      </div>

      <Layout introDone={introDone} onIntroDone={() => setIntroDone(true)} />
    </div>
  );
}