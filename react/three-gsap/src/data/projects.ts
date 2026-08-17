export type FlexDirection = "arrow";

export type Project = {
  id: string;
  index: string;
  title: string;
  tagline: string;
  year: string;
  services: readonly string[];
  /** CSS gradient seed — replaced with real imagery later. */
  gradient: string;
};

export const PROJECTS: Project[] = [
  {
    id: "meridian",
    index: "01",
    title: "MERIDIAN",
    tagline: "A design–build studio for the next generation of homes.",
    year: "2025",
    services: ["React", "Three.js", "GSAP", "ScrollTrigger"],
    gradient: "linear-gradient(140deg, #2a2624 0%, #141416 55%, #3b2f28 100%)",
  },
  {
    id: "partleave",
    index: "02",
    title: "PARTLEAVE",
    tagline: "Automated leave-request workflows, scripted end to end.",
    year: "2025",
    services: ["Node", "Automation", "Scripting"],
    gradient: "linear-gradient(140deg, #1f232b 0%, #141416 55%, #2a2b3b 100%)",
  },
  {
    id: "subtitle",
    index: "03",
    title: "SUBTITLE SYNC",
    tagline: "Translation tooling that keeps narration and timing honest.",
    year: "2024",
    services: ["Python", "NLP", "Tooling"],
    gradient: "linear-gradient(140deg, #26221c 0%, #141416 55%, #3a3126 100%)",
  },
  {
    id: "gitreport",
    index: "04",
    title: "GIT EVENT REPORT",
    tagline: "Turn noisy commit streams into quiet, readable summaries.",
    year: "2024",
    services: ["Node", "Git", "CLI"],
    gradient: "linear-gradient(140deg, #1c2320 0%, #141416 55%, #24312a 100%)",
  },
];