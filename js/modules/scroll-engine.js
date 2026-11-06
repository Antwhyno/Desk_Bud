function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

export function initScrollEngine() {
  const streamFill = document.getElementById("streamFill");
  const telemetryValue = document.getElementById("telemetryValue");
  const sketchSection = document.getElementById("architecture");
  const renderLayer = document.getElementById("renderLayer");
  const wipeLaserLine = document.getElementById("wipeLaserLine");
  const wipePercent = document.getElementById("wipePercent");
  const deskObjects = document.querySelectorAll(".desk-obj");

  function updateOnScroll() {
    const scrollY = window.scrollY;
    const maxScroll = Math.max(
      document.documentElement.scrollHeight - window.innerHeight,
      1
    );
    const globalProgress = clamp(scrollY / maxScroll, 0, 1);

    if (streamFill) {
      streamFill.style.transform = `scaleY(${globalProgress.toFixed(4)})`;
    }

    if (telemetryValue) {
      const mhz = Math.round(globalProgress * 240);
      telemetryValue.textContent = `${String(mhz).padStart(3, "0")} MHz`;
    }

    deskObjects.forEach((object) => {
      const speed = parseFloat(object.getAttribute("data-speed") || "0.25");
      object.style.transform = `translate3d(0, ${-scrollY * speed}px, 0)`;
    });

    if (sketchSection && renderLayer && wipeLaserLine) {
      const rect = sketchSection.getBoundingClientRect();
      const scrollableDistance = Math.max(
        sketchSection.offsetHeight - window.innerHeight,
        1
      );
      const rawProgress = clamp(-rect.top / scrollableDistance, 0, 1);
      const wipeProgress =
        rawProgress <= 0.2 ? 0 : clamp((rawProgress - 0.2) / 0.8, 0, 1);

      const rightInset = ((1 - wipeProgress) * 100).toFixed(2);
      renderLayer.style.clipPath = `inset(0 ${rightInset}% 0 0)`;
      wipeLaserLine.style.left = `${(wipeProgress * 100).toFixed(2)}%`;

      if (wipePercent) {
        const pct = Math.round(wipeProgress * 100);
        wipePercent.textContent =
          pct === 0
            ? "00% · ESQUISSE CAO"
            : pct === 100
            ? "100% · PROTOTYPE ASSEMBLÉ"
            : `${String(pct).padStart(2, "0")}% · BALAYAGE EN COURS`;
      }
    }
  }

  let ticking = false;
  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          updateOnScroll();
          ticking = false;
        });
        ticking = true;
      }
    },
    { passive: true }
  );

  updateOnScroll();
}
