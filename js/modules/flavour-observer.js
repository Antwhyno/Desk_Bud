export function initFlavourObserver() {
  const root = document.documentElement;
  const telemetryStatus = document.getElementById("telemetryStatus");
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
}

export function initRevealObserver() {
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

  revealElements.forEach((element) => revealObserver.observe(element));
}
