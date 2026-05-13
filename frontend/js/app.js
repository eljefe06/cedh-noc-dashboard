// ── Status colors ─────────────────────────────────────────────────────────────

const STATUS_COLOR = {
  ok:       'var(--neon-lime)',
  warning:  'var(--neon-blue)',
  critical: 'var(--neon-magenta)',
  down:     'var(--neon-magenta)',
  unknown:  'var(--text-tertiary)',
};

const STATUS_SYMBOL = {
  ok:       '',
  warning:  '▲ ',
  critical: '✕ ',
  down:     '✕ ',
  unknown:  '? ',
};

const STATUS_CLASS = {
  ok:       'status-ok',
  warning:  'status-warn',
  critical: 'status-bad',
  down:     'status-bad',
  unknown:  'status-unknown',
};

function statusColor(s) { return STATUS_COLOR[s] ?? 'var(--text-tertiary)'; }
function statusClass(s) { return STATUS_CLASS[s] ?? 'status-unknown'; }

// ── Sparkline ─────────────────────────────────────────────────────────────────

function sparkline(data, color) {
  color = color || 'var(--neon-cyan)';
  const W = 100, H = 18, pad = 2;

  if (!data || data.length < 2) {
    return `<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"></svg>`;
  }

  const min = Math.min.apply(null, data);
  const max = Math.max.apply(null, data);
  const range = max - min || 1;

  const pts = data.map(function(v, i) {
    const x = (i / (data.length - 1)) * W;
    const y = H - pad - ((v - min) / range) * (H - pad * 2);
    return x.toFixed(1) + ',' + y.toFixed(1);
  }).join(' ');

  return `<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
}

// ── Mock data (inline para funcionar con file://) ─────────────────────────────

var MOCK_DATA = {"generated_at":"2026-05-13T10:00:00-07:00","schema_version":"1.0","overall_status":"ok","incidents_open":0,"uptime":{"since":"2026-04-29T03:18:00-07:00","seconds":1209682,"human":"14d 06:42"},"servers":[{"name":"vps-myrock","display_name":"OpenClaw","status":"ok","provider":"Hetzner","region":"nbg1","specs":{"vcpu":2,"ram_gb":8,"disk_gb":96},"tailscale_ip":"100.104.244.83","agent_reachable":true,"agent_last_seen":"2026-05-13T10:00:00-07:00","stale":false,"metrics":{"cpu_percent":12,"ram_percent":36,"disk_percent":56,"load_1m":1.07,"load_5m":1.20,"load_15m":1.20,"uptime_seconds":1209682,"net_rx_mbps":2.1,"net_tx_mbps":8.4},"services":[{"name":"pagokids.com.mx","type":"http","criticality":"high","status":"ok","http_status":200,"latency_ms":112,"p95_ms_24h":189,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":"https://pagokids.com.mx/","extra":{"latency_history":[98,112,105,118,110,115,108,102,119,112,107,115,110,112,108,119,112,105,118,112]}},{"name":"myrock.com.mx","type":"http","criticality":"medium","status":"ok","http_status":200,"latency_ms":89,"p95_ms_24h":142,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":"https://myrock.com.mx/","extra":{"latency_history":[82,89,85,92,88,90,84,91,87,89,85,92,88,89,91,84,90,87,89,89]}},{"name":"n8n","type":"http","criticality":"medium","status":"ok","http_status":200,"latency_ms":204,"p95_ms_24h":312,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":null,"extra":{"latency_history":[190,204,198,215,205,200,210,204,196,206,202,204,208,202,198,204,201,198,210,204]}}],"ssl":[{"domain":"myrock.com.mx","days_left":62,"expires_at":"2026-07-14T00:00:00-07:00","issuer":"Let's Encrypt","status":"ok","checked_externally":true,"last_checked":"2026-05-13T10:00:00-07:00"},{"domain":"pagokids.com.mx","days_left":55,"expires_at":"2026-07-07T00:00:00-07:00","issuer":"Let's Encrypt","status":"ok","checked_externally":true,"last_checked":"2026-05-13T10:00:00-07:00"}],"backups":[],"deploys":[{"repo":"myrock-stack","branch":"main","commit_sha":"a1b2c3d","commit_message":"fix: optimize payment webhook handler","author":"eljefe06","deployed_at":"2026-05-13T08:15:00-07:00","age_hours":1.75,"status":"ok"}],"docker":null},{"name":"vps-suig","display_name":"VPS-SUIG","status":"ok","provider":"Hetzner","region":"fsn1","specs":{"vcpu":2,"ram_gb":4,"disk_gb":80},"tailscale_ip":null,"agent_reachable":true,"agent_last_seen":"2026-05-13T10:00:00-07:00","stale":false,"metrics":{"cpu_percent":8,"ram_percent":45,"disk_percent":38,"load_1m":0.42,"load_5m":0.38,"load_15m":0.35,"uptime_seconds":2592000,"net_rx_mbps":1.2,"net_tx_mbps":3.8},"services":[{"name":"cedhsinaloa.org.mx","type":"http","criticality":"high","status":"ok","http_status":200,"latency_ms":198,"p95_ms_24h":342,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":"https://cedhsinaloa.org.mx/","extra":{"latency_history":[180,198,210,195,188,202,198,205,192,198,185,201,198,195,200,198,210,195,188,198]}},{"name":"suig.cedhsinaloa","type":"http","criticality":"high","status":"ok","http_status":200,"latency_ms":182,"p95_ms_24h":298,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":"https://suig.cedhsinaloa.org.mx/","extra":{"latency_history":[170,182,175,188,180,178,185,182,176,183,179,182,185,180,175,182,178,183,180,182]}},{"name":"buzon.cedhsinaloa","type":"http","criticality":"high","status":"ok","http_status":200,"latency_ms":92,"p95_ms_24h":145,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":"https://buzon.cedhsinaloa.org.mx/","extra":{"latency_history":[85,92,88,95,90,88,94,91,87,92,89,92,95,90,88,92,91,87,93,92]}},{"name":"cedhs.xyz","type":"http","criticality":"medium","status":"ok","http_status":200,"latency_ms":78,"p95_ms_24h":112,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":"https://cedhs.xyz/","extra":{}}],"ssl":[{"domain":"cedhsinaloa.org.mx","days_left":45,"expires_at":"2026-06-27T00:00:00-07:00","issuer":"Let's Encrypt","status":"ok","checked_externally":true,"last_checked":"2026-05-13T10:00:00-07:00"},{"domain":"suig.cedhsinaloa.org.mx","days_left":45,"expires_at":"2026-06-27T00:00:00-07:00","issuer":"Let's Encrypt","status":"ok","checked_externally":true,"last_checked":"2026-05-13T10:00:00-07:00"},{"domain":"buzon.cedhsinaloa.org.mx","days_left":38,"expires_at":"2026-06-20T00:00:00-07:00","issuer":"Let's Encrypt","status":"ok","checked_externally":true,"last_checked":"2026-05-13T10:00:00-07:00"}],"backups":[],"deploys":[{"repo":"suig","branch":"main","commit_sha":"e4f5g6h","commit_message":"chore: update Node dependencies","author":"eljefe06","deployed_at":"2026-05-12T14:30:00-07:00","age_hours":19.5,"status":"ok"}],"docker":null},{"name":"vps-oic","display_name":"VPS-OIC","status":"ok","provider":"Hetzner","region":"nbg1","specs":{"vcpu":2,"ram_gb":4,"disk_gb":80},"tailscale_ip":null,"agent_reachable":true,"agent_last_seen":"2026-05-13T10:00:00-07:00","stale":false,"metrics":{"cpu_percent":5,"ram_percent":32,"disk_percent":28,"load_1m":0.18,"load_5m":0.22,"load_15m":0.20,"uptime_seconds":3888000,"net_rx_mbps":0.5,"net_tx_mbps":1.2},"services":[{"name":"ser-cedh","type":"http","criticality":"high","status":"ok","http_status":200,"latency_ms":152,"p95_ms_24h":245,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":null,"extra":{"latency_history":[140,152,148,158,150,145,155,152,148,153,150,152,156,150,148,152,151,148,155,152]}},{"name":"declaraciones","type":"http","criticality":"high","status":"ok","http_status":200,"latency_ms":164,"p95_ms_24h":268,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":null,"extra":{"latency_history":[155,164,160,170,162,158,168,164,159,165,162,164,168,162,160,164,163,160,167,164]}},{"name":"denuncias","type":"http","criticality":"high","status":"ok","http_status":200,"latency_ms":138,"p95_ms_24h":225,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":null,"extra":{"latency_history":[128,138,133,142,136,132,140,138,133,139,136,138,141,136,133,138,137,134,141,138]}}],"ssl":[],"backups":[],"deploys":[],"docker":null},{"name":"vps-mail","display_name":"VPS-Mail","status":"ok","provider":"Contabo","region":"eu","specs":{"vcpu":4,"ram_gb":8,"disk_gb":200},"tailscale_ip":null,"agent_reachable":true,"agent_last_seen":"2026-05-13T10:00:00-07:00","stale":false,"metrics":{"cpu_percent":15,"ram_percent":58,"disk_percent":42,"load_1m":0.85,"load_5m":0.78,"load_15m":0.72,"uptime_seconds":5184000,"net_rx_mbps":4.2,"net_tx_mbps":6.8},"services":[{"name":"mailcow.sogo","type":"http","criticality":"high","status":"ok","http_status":200,"latency_ms":248,"p95_ms_24h":398,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":"https://mail.cedhsinaloa.org.mx/SOGo/","extra":{"latency_history":[230,248,242,258,244,240,252,248,242,250,246,248,255,246,242,248,245,242,252,248]}},{"name":"smtp.587","type":"smtp","criticality":"high","status":"ok","http_status":null,"latency_ms":45,"p95_ms_24h":78,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":"mail.cedhsinaloa.org.mx:587","extra":{"starttls":true,"latency_history":[40,45,42,48,44,42,47,45,42,46,44,45,48,44,42,45,44,42,47,45]}},{"name":"imap.993","type":"imap","criticality":"high","status":"ok","http_status":null,"latency_ms":38,"p95_ms_24h":62,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":"mail.cedhsinaloa.org.mx:993","extra":{"tls":true,"latency_history":[34,38,36,40,37,35,39,38,36,38,37,38,40,37,36,38,37,36,39,38]}},{"name":"mailcow.admin","type":"http","criticality":"medium","status":"ok","http_status":200,"latency_ms":312,"p95_ms_24h":480,"last_checked":"2026-05-13T10:00:00-07:00","last_error":null,"url_checked":"https://mail.cedhsinaloa.org.mx/","extra":{}}],"ssl":[{"domain":"mail.cedhsinaloa.org.mx","days_left":18,"expires_at":"2026-05-31T00:00:00-07:00","issuer":"Let's Encrypt","status":"warning","checked_externally":true,"last_checked":"2026-05-13T10:00:00-07:00"}],"backups":[],"deploys":[],"docker":null}],"dns_checks":[{"domain":"cedhsinaloa.org.mx","check_type":"mx","expected":"mail.cedhsinaloa.org.mx","actual":"mail.cedhsinaloa.org.mx","status":"ok","resolver":"1.1.1.1","criticality":"high","last_checked":"2026-05-13T09:00:00-07:00"},{"domain":"cedhsinaloa.org.mx","check_type":"spf","expected":"v=spf1","actual":"v=spf1 include:_spf.google.com ~all","status":"ok","resolver":"1.1.1.1","criticality":"high","last_checked":"2026-05-13T09:00:00-07:00"}],"recent_incidents":[]};

// ── API ───────────────────────────────────────────────────────────────────────

function fetchStatus() {
  return Promise.resolve(MOCKS[activeMock]);
}

// ── Render ────────────────────────────────────────────────────────────────────

function renderDashboard(state) {
  renderHeader(state);
  renderVpsCards(state.servers);
  renderServicesGrid(state.servers);
  renderLogsPanel(state);
  renderSslPanel(state);
  renderDeploysPanel(state);
}

function renderHeader(state) {
  setText('hdr-uptime', 'UP ' + state.uptime.human);

  var incEl = document.getElementById('hdr-incidents');
  if (incEl) {
    incEl.textContent = 'INC ' + state.incidents_open;
    incEl.className = state.incidents_open > 0 ? 'hdr-metric hdr-metric--warn' : 'hdr-metric';
  }

  var main = state.servers.find(function(s) { return s.name === 'vps-myrock'; });
  if (main && main.metrics) {
    setText('hdr-load', 'LOAD ' + main.metrics.load_1m.toFixed(2));
  }

  document.body.dataset.status = state.overall_status;
}

function renderVpsCards(servers) {
  var el = document.getElementById('vps-cards');
  if (!el) return;
  el.innerHTML = servers.map(vpsCardHtml).join('');
}

function vpsCardHtml(server) {
  var color = statusColor(server.status);
  var m = server.metrics;

  return '<div class="vps-card vps-card--' + server.status + '" data-server="' + server.name + '" style="border-left-color:' + color + '">' +
    '<div class="vps-card__header">' +
      '<span class="vps-card__arrow" style="color:' + color + '">▸</span>' +
      '<span class="vps-card__name">' + server.display_name.toUpperCase() + '</span>' +
      '<span class="vps-card__meta">' + server.provider.toUpperCase() + '·' + server.region.toUpperCase() + ' // ' + server.specs.vcpu + 'c/' + server.specs.ram_gb + 'g</span>' +
    '</div>' +
    (server.agent_reachable ? metricsHtml(m) : agentDownHtml()) +
  '</div>';
}

function metricsHtml(m) {
  return '<div class="vps-metrics">' +
    metricRowHtml('CPU',  m.cpu_percent,  70, 90, m.cpu_percent + '%') +
    metricRowHtml('RAM',  m.ram_percent,  75, 90, m.ram_percent + '%') +
    metricRowHtml('DISK', m.disk_percent, 80, 90, m.disk_percent + '%') +
    metricRowHtml('NET',  Math.min(m.net_rx_mbps * 10, 100), 70, 90, fmtNet(m.net_rx_mbps)) +
  '</div>';
}

function metricRowHtml(label, pct, warn, crit, display) {
  var cls = pct >= crit ? 'status-bad' : pct >= warn ? 'status-warn' : 'status-ok';
  return '<div class="vps-metric">' +
    '<span class="vps-metric__label">' + label + '</span>' +
    '<span class="vps-metric__value ' + cls + '">' + display + '</span>' +
    '<div class="vps-bar"><div class="vps-bar__fill ' + cls + '" style="width:' + Math.min(pct, 100) + '%"></div></div>' +
  '</div>';
}

function agentDownHtml() {
  return '<div class="vps-agent-down">AGENTE NO RESPONDE</div>';
}

function fmtNet(mbps) {
  return mbps >= 1 ? mbps.toFixed(1) + 'M' : (mbps * 1000).toFixed(0) + 'K';
}

function renderServicesGrid(servers) {
  var el = document.getElementById('services-grid');
  if (!el) return;

  var high = [];
  servers.forEach(function(s) {
    s.services.forEach(function(svc) {
      if (svc.criticality === 'high') {
        high.push(Object.assign({}, svc, { _server: s.name }));
      }
    });
  });

  el.innerHTML = high.slice(0, 8).map(serviceCardHtml).join('');
}

function serviceCardHtml(svc) {
  var color   = statusColor(svc.status);
  var pill    = statusClass(svc.status);
  var blink   = (svc.status === 'down' || svc.status === 'critical') ? ' svc-pill--blink' : '';
  var history = svc.extra && svc.extra.latency_history;
  var sym     = STATUS_SYMBOL[svc.status] || '';
  var pillTxt = sym + (svc.latency_ms != null ? svc.latency_ms + 'ms' : svc.status.toUpperCase());

  var meta1 = svc.p95_ms_24h != null
    ? '<span class="svc-meta__label">p95</span><span class="svc-meta__value">' + svc.p95_ms_24h + 'ms</span>'
    : '';
  var meta2 = svc.http_status != null
    ? '<span class="svc-meta__label">http</span><span class="svc-meta__value">' + svc.http_status + '</span>'
    : svc.type !== 'http'
    ? '<span class="svc-meta__label">type</span><span class="svc-meta__value">' + svc.type + '</span>'
    : '';

  return '<div class="svc-card svc-card--' + svc.status + '" data-service="' + svc.name + '">' +
    '<div class="svc-card__topbar" style="background:' + color + '; box-shadow:0 0 8px ' + color + '80"></div>' +
    '<div class="svc-card__header">' +
      '<span class="svc-card__name">' + svc.name + '</span>' +
      '<span class="svc-pill ' + pill + blink + '">' + pillTxt + '</span>' +
    '</div>' +
    '<div class="svc-card__meta">' +
      '<div class="svc-meta__row">' + meta1 + '</div>' +
      '<div class="svc-meta__row">' + meta2 + '</div>' +
    '</div>' +
    '<div class="svc-sparkline">' + sparkline(history, color) + '</div>' +
  '</div>';
}

function renderLogsPanel(state) {
  var el = document.getElementById('panel-logs');
  if (!el) return;
  var incidents = state.recent_incidents;
  if (!incidents || !incidents.length) {
    el.innerHTML = emptyHtml('sin actividad reciente');
    return;
  }
  el.innerHTML = incidents.slice(0, 7).map(function(inc) {
    return '<div class="log-line">' +
      '<span class="log-time">' + relTime(inc.started_at) + '</span>' +
      '<span class="log-tag log-tag--' + inc.severity + '">' + inc.severity.toUpperCase() + '</span>' +
      '<span class="log-msg">' + inc.summary + '</span>' +
    '</div>';
  }).join('');
}

function renderSslPanel(state) {
  var el = document.getElementById('panel-ssl');
  if (!el) return;
  var certs = [];
  state.servers.forEach(function(s) {
    (s.ssl || []).forEach(function(c) { certs.push(c); });
  });
  if (!certs.length) {
    el.innerHTML = emptyHtml('sin datos ssl');
    return;
  }
  certs.sort(function(a, b) { return a.days_left - b.days_left; });
  el.innerHTML = certs.slice(0, 7).map(function(cert) {
    return '<div class="ssl-line">' +
      '<span class="ssl-domain">' + cert.domain + '</span>' +
      '<span class="ssl-days ' + statusClass(cert.status) + '">' + cert.days_left + 'd</span>' +
    '</div>';
  }).join('');
}

function renderDeploysPanel(state) {
  var el = document.getElementById('panel-deploys');
  if (!el) return;
  var deploys = [];
  state.servers.forEach(function(s) {
    (s.deploys || []).forEach(function(d) { deploys.push(d); });
  });
  if (!deploys.length) {
    el.innerHTML = emptyHtml('sin deploys recientes');
    return;
  }
  deploys.sort(function(a, b) { return new Date(b.deployed_at) - new Date(a.deployed_at); });
  el.innerHTML = deploys.slice(0, 5).map(function(d) {
    return '<div class="deploy-line">' +
      '<span class="deploy-time">' + relTime(d.deployed_at) + '</span>' +
      '<span class="deploy-repo">' + d.repo + '</span>' +
      '<span class="deploy-sha">' + d.commit_sha.slice(0, 7) + '</span>' +
      '<span class="deploy-msg">' + d.commit_message.slice(0, 32) + '</span>' +
    '</div>';
  }).join('');
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function emptyHtml(msg) {
  return '<div class="panel__empty">─ ' + msg + '</div>';
}

function relTime(iso) {
  var diff = (Date.now() - new Date(iso)) / 1000;
  if (diff < 60)    return Math.floor(diff) + 's';
  if (diff < 3600)  return Math.floor(diff / 60) + 'm';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h';
  return Math.floor(diff / 86400) + 'd';
}

function setText(id, text) {
  var el = document.getElementById(id);
  if (el) el.textContent = text;
}

// ── Mocks adicionales ─────────────────────────────────────────────────────────

// Mock 2: 1 servicio warning, 1 critical
var MOCK_2 = JSON.parse(JSON.stringify(MOCK_DATA));
MOCK_2.overall_status = 'critical';
MOCK_2.incidents_open = 2;
MOCK_2.servers[1].services[0].status = 'warning';   // cedhsinaloa.org.mx warning
MOCK_2.servers[1].services[0].latency_ms = 1850;
MOCK_2.servers[1].services[0].p95_ms_24h = 2300;
MOCK_2.servers[1].services[1].status = 'down';       // suig.cedhsinaloa down
MOCK_2.servers[1].services[1].latency_ms = null;
MOCK_2.servers[1].services[1].http_status = null;
MOCK_2.servers[1].services[1].last_error = 'Connection timeout after 5000ms';
MOCK_2.servers[1].status = 'critical';
MOCK_2.recent_incidents = [
  { id: 'inc-001', started_at: new Date(Date.now() - 4 * 60000).toISOString(), resolved_at: null, status: 'open', severity: 'high', target_type: 'service', target_name: 'suig.cedhsinaloa', summary: 'suig.cedhsinaloa no responde — timeout 5s', first_error: 'Connection timeout' },
  { id: 'inc-002', started_at: new Date(Date.now() - 18 * 60000).toISOString(), resolved_at: null, status: 'open', severity: 'medium', target_type: 'service', target_name: 'cedhsinaloa.org.mx', summary: 'cedhsinaloa.org.mx latencia elevada >1500ms', first_error: null }
];

// Mock 3: 1 servidor agent_unreachable
var MOCK_3 = JSON.parse(JSON.stringify(MOCK_DATA));
MOCK_3.overall_status = 'warning';
MOCK_3.incidents_open = 1;
MOCK_3.servers[2].agent_reachable = false;            // VPS-OIC unreachable
MOCK_3.servers[2].status = 'down';
MOCK_3.servers[2].stale = true;
MOCK_3.servers[2].services.forEach(function(s) { s.status = 'unknown'; s.latency_ms = null; });
MOCK_3.recent_incidents = [
  { id: 'inc-003', started_at: new Date(Date.now() - 12 * 60000).toISOString(), resolved_at: null, status: 'open', severity: 'high', target_type: 'agent', target_name: 'vps-oic', summary: 'Agente SSH vps-oic sin respuesta (2 fallos consecutivos)', first_error: 'ssh: connect timeout' }
];

// Mock 4: certificado SSL crítico (<7d)
var MOCK_4 = JSON.parse(JSON.stringify(MOCK_DATA));
MOCK_4.servers[3].ssl[0].days_left = 4;
MOCK_4.servers[3].ssl[0].status = 'critical';
MOCK_4.servers[3].ssl[0].expires_at = new Date(Date.now() + 4 * 86400000).toISOString();
MOCK_4.recent_incidents = [
  { id: 'inc-004', started_at: new Date(Date.now() - 2 * 3600000).toISOString(), resolved_at: null, status: 'open', severity: 'high', target_type: 'service', target_name: 'mail.cedhsinaloa.org.mx', summary: 'SSL mail.cedhsinaloa.org.mx vence en 4 días — renovar urgente', first_error: null }
];

// Mock 5: incidente activo nuevo + servicio warning
var MOCK_5 = JSON.parse(JSON.stringify(MOCK_DATA));
MOCK_5.overall_status = 'warning';
MOCK_5.incidents_open = 3;
MOCK_5.servers[0].metrics.cpu_percent = 87;           // OpenClaw CPU high
MOCK_5.servers[0].metrics.load_1m = 1.94;
MOCK_5.servers[0].status = 'warning';
MOCK_5.servers[3].services[0].status = 'warning';    // mailcow SOGo warning
MOCK_5.servers[3].services[0].latency_ms = 1200;
MOCK_5.recent_incidents = [
  { id: 'inc-005', started_at: new Date(Date.now() - 45000).toISOString(), resolved_at: null, status: 'open', severity: 'high', target_type: 'server', target_name: 'vps-myrock', summary: 'CPU OpenClaw >85% sostenido — carga anómala', first_error: 'load_1m: 1.94 > 2x cores' },
  { id: 'inc-006', started_at: new Date(Date.now() - 8 * 60000).toISOString(), resolved_at: null, status: 'open', severity: 'medium', target_type: 'service', target_name: 'mailcow.sogo', summary: 'mailcow.sogo latencia >1000ms', first_error: null },
  { id: 'inc-007', started_at: new Date(Date.now() - 25 * 60000).toISOString(), resolved_at: null, status: 'acknowledged', severity: 'low', target_type: 'service', target_name: 'cedhs.xyz', summary: 'cedhs.xyz http 503 — recuperado', first_error: 'HTTP 503' }
];

var MOCKS = [MOCK_DATA, MOCK_2, MOCK_3, MOCK_4, MOCK_5];
var activeMock = 0;

// ── Main loop ─────────────────────────────────────────────────────────────────

var POLL_INTERVAL = 5000;
var errorSince = null;

function tick() {
  fetchStatus()
    .then(function(state) {
      renderDashboard(state);
      document.getElementById('api-error').classList.add('hidden');
      errorSince = null;
    })
    .catch(function() {
      if (!errorSince) errorSince = Date.now();
      var overlay = document.getElementById('api-error');
      var timeEl  = document.getElementById('api-error-time');
      overlay.classList.remove('hidden');
      if (timeEl && errorSince) {
        var s = Math.floor((Date.now() - errorSince) / 1000);
        timeEl.textContent = 'Último estado: hace ' + s + 's';
      }
    });
}

function updateClock() {
  setText('hdr-time', new Date().toLocaleTimeString('es-MX', { hour12: false }));
}

function checkOrientation() {
  var warn = document.getElementById('portrait-warning');
  if (!warn) return;
  if (window.innerWidth < window.innerHeight) {
    warn.classList.remove('hidden');
  } else {
    warn.classList.add('hidden');
  }
}

// Teclas 1-5 para cambiar mock (solo en desarrollo)
document.addEventListener('keydown', function(e) {
  var n = parseInt(e.key);
  if (n >= 1 && n <= 5) {
    activeMock = n - 1;
    tick();
  }
});

checkOrientation();
window.addEventListener('resize', checkOrientation);
updateClock();
setInterval(updateClock, 1000);
tick();
setInterval(tick, POLL_INTERVAL);
