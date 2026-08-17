/**
 * Central corridor "spine" — a long thin beam running +z→-z at eye height,
 * with a thin accent edge. Gives the camera tour a rail to follow.
 */
export default function Spine() {
  return (
    <group position={[0, 0, -18]}>
      <mesh position={[0, 1.2, 0]}>
        <boxGeometry args={[0.18, 0.18, 36]} />
        <meshStandardMaterial color="#26262a" roughness={0.5} metalness={0.6} />
      </mesh>
      {/* accent rail */}
      <mesh position={[0, 1.38, 0]}>
        <boxGeometry args={[0.04, 0.03, 36]} />
        <meshStandardMaterial
          color="#c34a2f"
          emissive="#c34a2f"
          emissiveIntensity={0.6}
          roughness={0.4}
        />
      </mesh>
      {/* small cubes floating along the spine as beat markers */}
      {[3, 8, 13, 18, 23, 28].map((z) => (
        <mesh key={z} position={[0, 1.6, 17 - z]}>
          <boxGeometry args={[0.28, 0.28, 0.28]} />
          <meshStandardMaterial color="#2b2b2f" roughness={0.6} metalness={0.4} />
        </mesh>
      ))}
    </group>
  );
}