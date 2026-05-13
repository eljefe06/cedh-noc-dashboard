import { statusClass, statusColor } from './status-colors.js';
import { sparkline } from './sparkline.js';

export function renderDashboard(state) {
  renderHeader(state);
  renderVpsCards(state.servers);
  renderServicesGrid(state.servers);
  renderLogsPanel(state);
  renderSslPanel(state);
  renderDeploysPanel(state);
}

// ── Header ────────────────────────────────────────────────────────────────────

function renderHeader(state) {
  setText('hdr-uptime', `UP ${state.uptime.human}`);

  const incEl = document.getElementById('hdr-incidents');
  if (incEl) {
    incEl.textContent = `INC ${state.incidents_open}`;
    incEl.className = state.incidents_open > 0 ? 'hdr-metric hdr-metric--warn' : 'hdr-metric';
  }

  const main = state.servers.find(s => s.name === 'vps-myrock');
  if (main?.metrics) {
    setText('hdr-load', `LOAD ${main.metrics.load_1m.toFixed(2)}`);
  }

  document.body.dataset.status = state.overall_status;
}

// ── VPS Cards ─────────────────────────────────────────────────────────────────

function renderVpsCards(servers) {
  const el = document.getElementById('vps-cards');
  if (!el) return;
  el.innerHTML = servers.map(vpsCardHtml).join('');
}

function vpsCardHtml(server) {
  const color = statusColor(server.status);
  const m = server.metrics;

  return `
<div class="vps-card vps-card--${server.status}" data-server="${server.name}">
  <div class="vps-card__header">
    <span class="vps-card__arrow" style="color:${color}">▸</span>
    <span class="vps-card__name">${server.display_name.toUpperCase()}</span>
    <span class="vps-card__meta">${server.provider.toUpperCase()}·${server.region.toUpperCase()} // ${server.specs.vcpu}c/${server.specs.ram_gb}g</span>
  </div>
  ${server.agent_reachable ? metricsHtml(m) : agentDownHtml()}
</div>`;
}

function metricsHtml(m) {
  return `
<div class="vps-metrics">
  ${metricRowHtml('CPU',  m.cpu_percent,  70, 90, m.cpu_percent + '%')}
  ${metricRowHtml('RAM',  m.ram_percent,  75, 90, m.ram_percent + '%')}
  ${metricRowHtml('DISK', m.disk_percent, 80, 90, m.disk_percent + '%')}
  ${metricRowHtml('NET',  Math.min(m.net_rx_mbps * 10, 100), 70, 90, fmtNet(m.net_rx_mbps))}
</div>`;
}

function metricRowHtml(label, pct, warn, crit, display) {
  const cls = pct >= crit ? 'status-bad' : pct >= warn ? 'status-warn' : 'status-ok';
  return `
<div class="vps-metric">
  <span class="vps-metric__label">${label}</span>
  <span class="vps-metric__value ${cls}">${display}</span>
  <div class="vps-bar"><div class="vps-bar__fill ${cls}" style="width:${Math.min(pct, 100)}%"></div></div>
</div>`;
}

function agentDownHtml() {
  return `<div class="vps-agent-down">AGENTE NO RESPONDE</div>`;
}

function fmtNet(mbps) {
  return mbps >= 1 ? `${mbps.toFixed(1)}M` : `${(mbps * 1000).toFixed(0)}K`;
}

// ── Services Grid ─────────────────────────────────────────────────────────────

function renderServicesGrid(servers) {
  const el = document.getElementById('services-grid');
  if (!el) return;

  const high = servers.flatMap(s =>
    s.services.filter(svc => svc.criticality === 'high').map(svc => ({ ...svc, _server: s.name }))
  ).slice(0, 8);

  el.innerHTML = high.map(serviceCardHtml).join('');
}

function serviceCardHtml(svc) {
  const color = statusColor(svc.status);
  const pill  = statusClass(svc.status);
  const blink = (svc.status === 'down' || svc.status === 'critical') ? ' svc-pill--blink' : '';
  const history = svc.extra?.latency_history;
  const pillText = svc.latency_ms != null ? `${svc.latency_ms}ms` : svc.status.toUpperCase();

  const meta1 = svc.p95_ms_24h != null
    ? `<span class="svc-meta__label">p95</span><span class="svc-meta__value">${svc.p95_ms_24h}ms</span>`
    : '';
  const meta2 = svc.http_status != null
    ? `<span class="svc-meta__label">http</span><span class="svc-meta__value">${svc.http_status}</span>`
    : svc.type !== 'http'
    ? `<span class="svc-meta__label">type</span><span class="svc-meta__value">${svc.type}</span>`
    : '';

  return `
<div class="svc-card svc-card--${svc.status}" data-service="${svc.name}">
  <div class="svc-card__topbar" style="background:${color}; box-shadow:0 0 8px ${color}80"></div>
  <div class="svc-card__header">
    <span class="svc-card__name">${svc.name}</span>
    <span class="svc-pill ${pill}${blink}">${pillText}</span>
  </div>
  <div class="svc-card__meta">
    <div class="svc-meta__row">${meta1}</div>
    <div class="svc-meta__row">${meta2}</div>
  </div>
  <div class="svc-sparkline">${sparkline(history, { color })}</div>
</div>`;
}

// ── Bottom Panels ─────────────────────────────────────────────────────────────

function renderLogsPanel(state) {
  const el = document.getElementById('panel-logs');
  if (!el) return;

  const incidents = state.recent_incidents;
  if (!incidents?.length) {
    el.innerHTML = emptyHtml('sin actividad reciente');
    return;
  }

  el.innerHTML = incidents.slice(0, 7).map(inc => `
<div class="log-line">
  <span class="log-time">${relTime(inc.started_at)}</span>
  <span class="log-tag log-tag--${inc.severity}">${inc.severity.toUpperCase()}</span>
  <span class="log-msg">${inc.summary}</span>
</div>`).join('');
}

function renderSslPanel(state) {
  const el = document.getElementById('panel-ssl');
  if (!el) return;

  const certs = state.servers.flatMap(s => s.ssl ?? []);
  if (!certs.length) {
    el.innerHTML = emptyHtml('sin datos ssl');
    return;
  }

  const sorted = [...certs].sort((a, b) => a.days_left - b.days_left);
  el.innerHTML = sorted.slice(0, 7).map(cert => `
<div class="ssl-line">
  <span class="ssl-domain">${cert.domain}</span>
  <span class="ssl-days ${statusClass(cert.status)}">${cert.days_left}d</span>
</div>`).join('');
}

function renderDeploysPanel(state) {
  const el = document.getElementById('panel-deploys');
  if (!el) return;

  const deploys = state.servers.flatMap(s => s.deploys ?? []);
  if (!deploys.length) {
    el.innerHTML = emptyHtml('sin deploys recientes');
    return;
  }

  const sorted = [...deploys].sort((a, b) => new Date(b.deployed_at) - new Date(a.deployed_at));
  el.innerHTML = sorted.slice(0, 5).map(d => `
<div class="deploy-line">
  <span class="deploy-time">${relTime(d.deployed_at)}</span>
  <span class="deploy-repo">${d.repo}</span>
  <span class="deploy-sha">${d.commit_sha.slice(0, 7)}</span>
  <span class="deploy-msg">${d.commit_message.slice(0, 32)}</span>
</div>`).join('');
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function emptyHtml(msg) {
  return `<div class="panel__empty">─ ${msg}</div>`;
}

function relTime(iso) {
  const diff = (Date.now() - new Date(iso)) / 1000;
  if (diff < 60)    return `${Math.floor(diff)}s`;
  if (diff < 3600)  return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}d`;
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}
