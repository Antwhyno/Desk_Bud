export function initNav() {
  const sommaireBtn = document.getElementById("sommaireBtn");
  const sommaireMenu = document.getElementById("sommaireMenu");

  if (!sommaireBtn || !sommaireMenu) {
    return;
  }

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
