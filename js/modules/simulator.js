export function initSimulator() {
  const interactiveFace = document.getElementById("interactiveFace");
  const oledSubtext = document.getElementById("oledSubtext");
  const modeButtons = document.querySelectorAll(".tactile-btn");

  const modeLabels = {
    focus: "POMODORO · 25:00",
    happy: "PAUSE ACTIVE · +5 MIN",
    code: "WATCHER · 0 ERREUR"
  };

  modeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const mode = button.getAttribute("data-face") || "focus";
      modeButtons.forEach((modeButton) => modeButton.classList.remove("active"));
      button.classList.add("active");

      if (interactiveFace) {
        interactiveFace.setAttribute("data-mode", mode);
      }
      if (oledSubtext && modeLabels[mode]) {
        oledSubtext.textContent = modeLabels[mode];
      }
    });
  });
}
