export const BRAND = {
  name: "IMAN LANGARAN",
  monogram: "IL",
  role: "Creative Developer",
  heroTitle: "CREATIVE\nDEVELOPER",
  heroSubtitle: "I BUILD DIGITAL EXPERIENCES.",
  email: "hello@imanlangaran.com",
} as const;

export type NavId = "about" | "work" | "skills" | "contact";

export const NAV_LINKS: ReadonlyArray<{ id: NavId; index: string; label: string }> = [
  { id: "about", index: "01", label: "About" },
  { id: "work", index: "02", label: "Work" },
  { id: "skills", index: "03", label: "Skills" },
  { id: "contact", index: "04", label: "Contact" },
];

export const SOCIALS = [
  { label: "GitHub", href: "https://github.com/iman-langaran" },
  { label: "LinkedIn", href: "https://www.linkedin.com/in/iman-langaran" },
  { label: "Email", href: "mailto:hello@imanlangaran.com" },
] as const;