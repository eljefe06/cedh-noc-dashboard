import { fetchStatus } from './api.js';
import { renderDashboard } from './render.js';

const POLL_INTERVAL = 5000;
let errorSince = null;

function tick() {
  return fetchStatus()
    .then(state => {
      renderDashboard(state);
      hideError();
      errorSince = null;
    })
    .catch(() => {
      if (!errorSince) errorSince = Date.now();
      showError(errorSince);
    });
}

function showError(since) {
  const overlay = document.getElementById('api-error');
  const timeEl  = document.getElementById('api-error-time');
  overlay?.classList.remove('hidden');
  if (timeEl && since) {
    const s = Math.floor((Date.now() - since) / 1000);
    timeEl.textContent = `Último estado: hace ${s}s`;
  }
}

function hideError() {
  document.getElementById('api-error')?.classList.add('hidden');
}

function updateClock() {
  const el = document.getElementById('hdr-time');
  if (el) el.textContent = new Date().toLocaleTimeString('es-MX', { hour12: false });
}

function checkOrientation() {
  const warn = document.getElementById('portrait-warning');
  if (!warn) return;
  warn.classList.toggle('hidden', window.innerWidth >= window.innerHeight);
}

// ── Init ──────────────────────────────────────────────────────────────────────

checkOrientation();
window.addEventListener('resize', checkOrientation);

updateClock();
setInterval(updateClock, 1000);

tick();
setInterval(tick, POLL_INTERVAL);
