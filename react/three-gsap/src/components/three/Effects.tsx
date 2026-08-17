import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";

/**
 * Subtle cinematic grade: a whisper of bloom on the accent emissives and a
 * soft vignette. Mounted only on desktop, high-quality, non-reduced-motion.
 */
export default function Effects() {
  return (
    <EffectComposer>
      <Bloom
        intensity={0.35}
        luminanceThreshold={0.9}
        luminanceSmoothing={0.2}
        mipmapBlur
        radius={0.6}
      />
      <Vignette eskil={false} offset={0.22} darkness={0.78} />
    </EffectComposer>
  );
}