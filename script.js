/**
 * DESK BUD — PROJET NSI
 * Mécaniques implémentées :
 * 1. Changement de palette au scroll (IntersectionObserver -50% 0px -50% 0px)
 * 2. Télémétrie d'ascension en direct (000 MHz -> 240 MHz) & fil central (scaleY)
 * 3. Sketch-to-Render wipe sur la section sticky avec hold de 20% + ligne laser 2px
 * 4. Ticker calibré en pixels par seconde (indépendant de la largeur d'écran)
 * 5. Simulateur interactif des états du Desk Bud
 */

document.addEventListener("DOMContentLoaded", () => {
  const root = document.documentElement;
  const streamFill = document.getElementById("streamFill");
  const telemetryValue = document.getElementById("telemetryValue");
  const telemetryStatus = document.getElementById("telemetryStatus");

  // =========================================================================
  // 1. MENU SOMMAIRE MOBILE
  // =========================================================================
  const sommaireBtn = document.getElementById("sommaireBtn");
  const sommaireMenu = document.getElementById("sommaireMenu");

  if (sommaireBtn && sommaireMenu) {
    sommaireBtn.addEventListener("click", () => {
      const isOpen = sommaireMenu.classList.toggle("is-open");
      sommaireBtn.setAttribute("aria-expanded", String(isOpen));
    });

    sommaireMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        sommaireMenu.classList.remove("is-open");
        sommaireBtn.setAttribute("aria-expanded", "false");
      });
    });
  }

  // =========================================================================
  // 2. FLAVOUR TRICK : INTERSECTION OBSERVER AU MILIEU DE L'ÉCRAN
  // =========================================================================
  const flavourSections = document.querySelectorAll("[data-flavour-section]");

  const flavourObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const flavour = entry.target.getAttribute("data-flavour-section");
          const status = entry.target.getAttribute("data-status");
          if (flavour) {
            root.dataset.flavour = flavour;
          }
          if (status && telemetryStatus) {
            telemetryStatus.textContent = status;
          }
        }
      });
    },
    {
      rootMargin: "-50% 0px -50% 0px",
      threshold: 0
    }
  );

  flavourSections.forEach((section) => flavourObserver.observe(section));

  // =========================================================================
  // 3. RÉVÉLATION SUR COURBES DE VITESSE (REVEAL ON SCROLL)
  // =========================================================================
  const revealElements = document.querySelectorAll(".reveal");

  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
        }
      });
    },
    { threshold: 0.14 }
  );

  revealElements.forEach((el) => revealObserver.observe(el));

  // =========================================================================
  // 4. SCROLL LOOP : STREAM CENTRAL, PARALLAXE OBJETS & SKETCH-TO-RENDER WIPE
  // =========================================================================
  const sketchSection = document.getElementById("architecture");
  const renderLayer = document.getElementById("renderLayer");
  const wipeLaserLine = document.getElementById("wipeLaserLine");
  const wipePercent = document.getElementById("wipePercent");
  const deskObjects = document.querySelectorAll(".desk-obj");

  function clamp(val, min, max) {
    return Math.min(Math.max(val, min), max);
  }

  function updateOnScroll() {
    const scrollY = window.scrollY;
    const maxScroll = Math.max(
      document.documentElement.scrollHeight - window.innerHeight,
      1
    );
    const globalProgress = clamp(scrollY / maxScroll, 0, 1);

    // A. Fil conducteur central (scaleY)
    if (streamFill) {
      streamFill.style.transform = `scaleY(${globalProgress.toFixed(4)})`;
    }

    // B. Compteur de télémétrie (comme l'altimètre 3 214 m des Maths au Sommet)
    if (telemetryValue) {
      const mhz = Math.round(globalProgress * 240);
      telemetryValue.textContent = `${String(mhz).padStart(3, "0")} MHz`;
    }

    // C. Parallaxe différentielle des 4 objets du bureau (0.18 à 0.42x le scroll)
    deskObjects.forEach((obj) => {
      const speed = parseFloat(obj.getAttribute("data-speed") || "0.25");
      obj.style.transform = `translate3d(0, ${-scrollY * speed}px, 0)`;
    });

    // D. Sketch-to-Render Wipe avec maintien des 20 premiers pourcents
    if (sketchSection && renderLayer && wipeLaserLine) {
      const rect = sketchSection.getBoundingClientRect();
      const scrollableDistance = Math.max(
        sketchSection.offsetHeight - window.innerHeight,
        1
      );
      const rawProgress = clamp(-rect.top / scrollableDistance, 0, 1);

      // Hold the sketch for the first 20%, then wipe from 0 to 1
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

  // =========================================================================
  // 5. SIMULATEUR INTERACTIF DU DESK BUD (HERO)
  // =========================================================================
  const interactiveFace = document.getElementById("interactiveFace");
  const oledSubtext = document.getElementById("oledSubtext");
  const modeButtons = document.querySelectorAll(".tactile-btn");

  const modeLabels = {
    focus: "POMODORO · 25:00",
    happy: "PAUSE ACTIVE · +5 MIN",
    code: "WATCHER · 0 ERREUR"
  };

  modeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const mode = btn.getAttribute("data-face") || "focus";
      modeButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      if (interactiveFace) {
        interactiveFace.setAttribute("data-mode", mode);
      }
      if (oledSubtext && modeLabels[mode]) {
        oledSubtext.textContent = modeLabels[mode];
      }
    });
  });

  // =========================================================================
  // 6. TICKER À VITESSE CONSTANTE EN PX/SECONDE (POUR MOBILE & DESKTOP)
  // =========================================================================
  const tickerTrack = document.getElementById("tickerTrack");
  if (tickerTrack) {
    let offset = 0;
    let lastTime = performance.now();
    const speedPxPerSec = 55; // Vitesse constante en px/s

    function animateTicker(now) {
      const dt = (now - lastTime) / 1000;
      lastTime = now;
      offset -= speedPxPerSec * dt;

      const halfWidth = tickerTrack.scrollWidth / 2;
      if (halfWidth > 0 && Math.abs(offset) >= halfWidth) {
        offset += halfWidth;
      }

      tickerTrack.style.transform = `translate3d(${offset.toFixed(1)}px, 0, 0)`;
      requestAnimationFrame(animateTicker);
    }

    requestAnimationFrame(animateTicker);
  }
});