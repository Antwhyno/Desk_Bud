export function initTicker() {
  const tickerTrack = document.getElementById("tickerTrack");

  if (!tickerTrack) {
    return;
  }

  let offset = 0;
  let lastTime = performance.now();
  const speedPxPerSec = 55;

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
