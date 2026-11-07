const MODEL_URL = new URL("../../assets/Desk_Bud-V1.gltf", import.meta.url);
const ROTATION = Math.PI * 2;
const INITIAL_ROTATION = (430 / 360) * ROTATION;
const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

export function initModelViewer() {
  const section = document.getElementById("modele-3d");
  const canvas = document.getElementById("modelCanvas");
  const status = document.getElementById("modelStatus");
  const rotationValue = document.getElementById("modelRotationValue");

  if (!section || !canvas || !status || !rotationValue) {
    return;
  }

  let visible = false;
  let frameId = 0;
  let targetRotation = INITIAL_ROTATION;
  let currentRotation = INITIAL_ROTATION;
  let pivot;
  let renderer;
  let camera;
  let previousTime = 0;
  let initialized = false;

  function updateScrollProgress() {
    const scrollDistance = Math.max(
      section.offsetHeight - window.innerHeight,
      1
    );
    const progress = clamp(
      -section.getBoundingClientRect().top / scrollDistance,
      0,
      1
    );

    targetRotation = INITIAL_ROTATION + progress * ROTATION;
    rotationValue.textContent = `${String(Math.round(progress * 360)).padStart(3, "0")}°`;
  }

  function resizeRenderer() {
    if (!renderer || !camera) {
      return;
    }

    const width = canvas.clientWidth;
    const height = canvas.clientHeight;

    if (width === 0 || height === 0) {
      return;
    }

    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  function animate(now) {
    if (!visible || !renderer || !camera || !pivot) {
      frameId = 0;
      return;
    }

    const delta = previousTime === 0 ? 0 : (now - previousTime) / 1000;
    previousTime = now;
    updateScrollProgress();

    const lerpFactor = 1 - Math.exp(-10 * delta);
    currentRotation += (targetRotation - currentRotation) * lerpFactor;
    pivot.rotation.y = currentRotation;

    renderer.render(pivot.parent, camera);
    frameId = window.requestAnimationFrame(animate);
  }

  function startAnimation() {
    if (frameId === 0) {
      previousTime = 0;
      frameId = window.requestAnimationFrame(animate);
    }
  }

  function setStatus(message, isError = false) {
    status.textContent = message;
    status.classList.toggle("is-error", isError);
  }

  async function loadModel() {
    if (initialized) {
      return;
    }
    initialized = true;

    try {
      const [
        {
          AmbientLight,
          Box3,
          Color,
          DirectionalLight,
          Group,
          GridHelper,
          PerspectiveCamera,
          Scene,
          SRGBColorSpace,
          Vector3,
          WebGLRenderer
        },
        { GLTFLoader }
      ] = await Promise.all([
        import("three"),
        import("three/addons/loaders/GLTFLoader.js")
      ]);

      const scene = new Scene();
      scene.background = new Color("#15181f");

      camera = new PerspectiveCamera(38, 1, 0.01, 100);
      camera.position.set(3.2, 2.1, 4.4);
      camera.lookAt(0, 0, 0);

      renderer = new WebGLRenderer({
        canvas,
        antialias: true,
        alpha: false
      });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.outputColorSpace = SRGBColorSpace;
      resizeRenderer();

      scene.add(new AmbientLight("#ffffff", 1));

      const keyLight = new DirectionalLight("#ffffff", 2);
      keyLight.position.set(3, 5, 4);
      scene.add(keyLight);

      const fillLight = new DirectionalLight("#9ccaff", 0.7);
      fillLight.position.set(-4, 2, -3);
      scene.add(fillLight);

      const grid = new GridHelper(5, 24, "#ff6b35", "#454955");
      grid.position.y = -1.35;
      grid.material.transparent = true;
      grid.material.opacity = 0.3;
      scene.add(grid);

      pivot = new Group();
      scene.add(pivot);

      const loader = new GLTFLoader();
      loader.load(
        MODEL_URL.href,
        (gltf) => {
          const model = gltf.scene;
          const bounds = new Box3().setFromObject(model);
          const center = bounds.getCenter(new Vector3());
          const size = bounds.getSize(new Vector3());
          const radius = Math.max(size.x, size.y, size.z) / 2;

          model.position.sub(center);
          pivot.add(model);
          pivot.scale.setScalar(1.35 / radius);

          setStatus("Utilisez le défilement pour faire tourner le modèle");
          resizeRenderer();
          startAnimation();
        },
        undefined,
        (error) => {
          console.error("Impossible de charger le modèle 3D du Desk Bud.", error);
          setStatus("Chargement 3D impossible. Vérifiez le fichier et la connexion.", true);
        }
      );

      window.addEventListener("resize", resizeRenderer);
      resizeRenderer();
    } catch (error) {
      console.error("Impossible de démarrer le visualiseur 3D.", error);
      setStatus("Visualiseur 3D indisponible. Vérifiez votre connexion.", true);
    }
  }

  const visibilityObserver = new IntersectionObserver(
    ([entry]) => {
      visible = entry.isIntersecting;

      if (visible) {
        updateScrollProgress();
        loadModel();
        startAnimation();
      }
    },
    { rootMargin: "100px 0px" }
  );

  visibilityObserver.observe(section);

  updateScrollProgress();
}
