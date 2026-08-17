export type SkillGroup = {
  label: string;
  level: number; // 0..100
  keywords: readonly string[];
};

export const SKILL_GROUPS: SkillGroup[] = [
  {
    label: "Creative Development",
    level: 92,
    keywords: ["React", "TypeScript", "Three.js", "React Three Fiber", "GSAP"],
  },
  {
    label: "3D & Motion",
    level: 84,
    keywords: ["WebGL", "Shaders", "ScrollTrigger", "Lenis", "Post-processing"],
  },
  {
    label: "Engineering",
    level: 88,
    keywords: ["Node", "Python", "CLI Tooling", "Automation", "Git"],
  },
  {
    label: "Design",
    level: 78,
    keywords: ["Typography", "Editorial Layout", "Systems", "Prototyping"],
  },
];