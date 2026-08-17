import type { NavId } from "../data/brand";

export type DestinationPose = {
  id: NavId;
  position: [number, number, number];
  /** extra per-object drift/rotation for idle float */
  float: { amp: number; period: number };
};

/** Single source of truth for the four nav monoliths in the corridor. */
export const DESTINATIONS: DestinationPose[] = [
  { id: "about", position: [3.4, 0, -5], float: { amp: 0.05, period: 2.4 } },
  { id: "work", position: [-3.4, 0, -11], float: { amp: 0.06, period: 3.0 } },
  { id: "skills", position: [3.4, 0, -17], float: { amp: 0.07, period: 3.6 } },
  { id: "contact", position: [-3.4, 0, -23], float: { amp: 0.04, period: 2.8 } },
];

export const DESTINATION_LABELS: Record<NavId, string> = {
  about: "ABOUT",
  work: "WORK",
  skills: "SKILLS",
  contact: "CONTACT",
};