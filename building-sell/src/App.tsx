import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

import Nav from "./components/Nav";
import Hero from "./components/Hero";
import Manifesto from "./components/Manifesto";
import Capabilities from "./components/Capabilities";
import Work from "./components/Work";
import Process from "./components/Process";
import FinalCTA from "./components/FinalCTA";
import Footer from "./components/Footer";

gsap.registerPlugin(ScrollTrigger, useGSAP);

export default function App() {
  return (
    <div className="min-h-screen bg-paper text-ink">
      <Nav />
      <main>
        <Hero />
        <Manifesto />
        <Capabilities />
        <Work />
        <Process />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
}