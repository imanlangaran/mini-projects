import * as THREE from "three";

/**
 * Architectural "floor plate" tower:
 * - Stacked thin slabs (BoxGeometry) drifting slowly, with a wireframe shell
 * - Fine dust particles adrift around the volume
 * - Mouse parallax on the camera, subtle edge lighting
 * - Pauses when off-screen, clamps DPR, disposes fully on unmount
 */
export default class HeroScene {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private clock = new THREE.Clock();
  private stack = new THREE.Group();
  private particles!: THREE.Points;
  private ray?: THREE.Mesh;

  private mouse = { x: 0, y: 0 };
  private target = { x: 0, y: 0 };
  private raf = 0;
  private running = true;

  private onResize: () => void;
  private onVisibility: () => void;

  constructor(private container: HTMLElement) {
    const width = container.clientWidth;
    const height = container.clientHeight;

    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.Fog(0xf3eee5, 18, 30);

    this.camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 100);
    this.camera.position.set(0, 1.5, 9);

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: "high-performance",
      });
    } catch {
      // WebGL unavailable — degrade silently (the hero simply shows the
      // intentional paper backdrop without the 3D layer).
      throw new Error("WebGL not supported");
    }
    this.renderer = renderer;
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.1;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(this.renderer.domElement);
    this.renderer.domElement.setAttribute("aria-hidden", "true");

    this.buildLights();
    this.buildStack();
    this.buildParticles();

    this.onResize = () => this.handleResize();
    this.onVisibility = () => this.handleVisibility();
    window.addEventListener("resize", this.onResize, { passive: true });
    document.addEventListener("visibilitychange", this.onVisibility);
    window.addEventListener("pointermove", this.handlePointer, { passive: true });

    this.loop();
  }

  /* ---------------------------------- build --------------------------------- */

  private buildLights() {
    const ambient = new THREE.AmbientLight(0xffffff, 1.1);
    this.scene.add(ambient);

    const key = new THREE.DirectionalLight(0xfff4e0, 2.6);
    key.position.set(4, 6, 6);
    this.scene.add(key);

    const fill = new THREE.DirectionalLight(0xdfe6ff, 1.1);
    fill.position.set(-6, -2, 4);
    this.scene.add(fill);

    const rim = new THREE.DirectionalLight(0xc34a2f, 0.6);
    rim.position.set(-2, -4, -3);
    this.scene.add(rim);
  }

  private buildStack() {
    this.stack.rotation.x = -0.22;
    this.stack.rotation.y = -0.5;
    this.scene.add(this.stack);

    const slabGeo = new THREE.BoxGeometry(3.4, 0.16, 3.4);
    const slabMat = new THREE.MeshStandardMaterial({
      color: 0xf8f4ec,
      roughness: 0.5,
      metalness: 0.05,
    });
    const edgeMat = new THREE.MeshStandardMaterial({
      color: 0x1c1917,
      metalness: 0,
      roughness: 0.9,
    });

    const count = 6;
    for (let i = 0; i < count; i++) {
      const scale = 1 - i * 0.05;
      const slab = new THREE.Mesh(slabGeo, slabMat);
      slab.position.y = i * 0.78 - 1.9;
      slab.rotation.y = (i % 2 === 0 ? 1 : -1) * 0.06;
      slab.scale.setScalar(scale);
      this.stack.add(slab);

      // thin vertical "section band" rising from each slab edge
      const band = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.8, 3.4 * scale), edgeMat);
      band.position.copy(slab.position);
      band.position.y += 0.39;
      this.stack.add(band);
    }

    // a single accent "core"
    const core = new THREE.Mesh(
      new THREE.BoxGeometry(0.18, 0.18, 0.18),
      new THREE.MeshStandardMaterial({ color: 0xc34a2f, roughness: 0.35 })
    );
    core.position.y = 0.2;
    this.stack.add(core);

    this.ray = new THREE.Mesh(
      new THREE.CylinderGeometry(0.012, 0.012, 9, 8),
      new THREE.MeshBasicMaterial({ color: 0x1c1917, transparent: true, opacity: 0.3 })
    );
    this.ray.position.y = -4.4;
    this.stack.add(this.ray);
  }

  private buildParticles() {
    const count = 220;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const radius = 2.4 + Math.random() * 3.4;
      const y = (Math.random() - 0.5) * 6;
      positions[i * 3] = Math.cos(angle) * radius;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = Math.sin(angle) * radius;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({
      color: 0x1c1917,
      size: 0.045,
      transparent: true,
      opacity: 0.35,
      depthWrite: false,
    });
    this.particles = new THREE.Points(geo, mat);
    this.scene.add(this.particles);
  }

  /* --------------------------------- events -------------------------------- */

  private handlePointer = (e: PointerEvent) => {
    this.mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    this.mouse.y = (e.clientY / window.innerHeight) * 2 - 1;
  };

  private handleResize() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  private handleVisibility() {
    if (document.hidden) this.pause();
    else this.resume();
  }

  /* ------------------------------- lifecycle ------------------------------- */

  setMotion(motion: boolean) {
    if (!motion) this.pause();
    else this.resume();
  }

  private pause() {
    this.running = false;
    if (this.raf) cancelAnimationFrame(this.raf);
  }

  private resume() {
    if (this.running) return;
    this.running = true;
    this.clock.getDelta(); // reset delta so no jump
    this.loop();
  }

  private loop = () => {
    if (!this.running) return;
    this.raf = requestAnimationFrame(this.loop);

    const t = this.clock.getElapsedTime();

    // gentle drift
    this.stack.position.y = Math.sin(t * 0.4) * 0.12;
    this.stack.rotation.y = -0.5 + Math.sin(t * 0.2) * 0.08;

    const bands = this.stack.children;
    for (let i = 0; i < bands.length; i++) {
      if (i % 2 === 0) continue;
      bands[i].position.y += Math.sin(t * 0.7 + i) * 0.001;
    }

    // particles drift upward
    const pos = this.particles.geometry.attributes.position.array as Float32Array;
    for (let i = 1; i < pos.length; i += 3) {
      pos[i] += 0.0022;
      if (pos[i] > 3) pos[i] = -3;
    }
    this.particles.geometry.attributes.position.needsUpdate = true;

    // smooth camera parallax toward pointer
    this.target.x += (this.mouse.x - this.target.x) * 0.04;
    this.target.y += (this.mouse.y - this.target.y) * 0.04;
    this.camera.position.x = this.target.x * 0.7;
    this.camera.position.y = 1.5 + this.target.y * 0.45;
    this.camera.lookAt(0, 0.4, 0);

    this.renderer.render(this.scene, this.camera);
  }

  dispose() {
    this.pause();
    window.removeEventListener("resize", this.onResize);
    document.removeEventListener("visibilitychange", this.onVisibility);
    window.removeEventListener("pointermove", this.handlePointer);

    this.scene.traverse((obj) => {
      if (obj instanceof THREE.Mesh) {
        obj.geometry.dispose();
        const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
        mats.forEach((m) => m.dispose());
      }
    });
    this.scene.traverse((obj) => obj instanceof THREE.Points && obj.geometry.dispose());
    (this.particles.material as THREE.Material).dispose();

    this.renderer.dispose();
    if (this.renderer.domElement.parentElement === this.container) {
      this.container.removeChild(this.renderer.domElement);
    }
  }
}