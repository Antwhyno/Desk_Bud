import { initFlavourObserver, initRevealObserver } from "./modules/flavour-observer.js";
import { initNav } from "./modules/nav.js";
import { initScrollEngine } from "./modules/scroll-engine.js";
import { initSimulator } from "./modules/simulator.js";
import { initTicker } from "./modules/ticker.js";

initNav();
initFlavourObserver();
initRevealObserver();
initScrollEngine();
initSimulator();
initTicker();
