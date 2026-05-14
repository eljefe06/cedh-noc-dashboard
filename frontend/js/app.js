// ── Mock data ─────────────────────────────────────────────────────────────────

const NOW_ISO = new Date().toISOString();

function _mkServer(name, displayName, status, cpu, ram, disk, svcs, ssl, deploys) {
  return {
    name, display_name: displayName, status,
    agent_reachable: status !== 'down',
    agent_last_seen: NOW_ISO, stale: false,
    metrics: status !== 'down'
      ? { cpu_percent: cpu, ram_percent: ram, disk_percent: disk,
          load_1m: (cpu / 100).toFixed(2), uptime_seconds: 1209600 }
      : null,
    services: svcs, ssl: ssl || [], deploys: deploys || [], backups: [],
  };
}

function _mkSvc(name, type, crit, status, latency, code, err) {
  return {
    name, type: type || 'http', criticality: crit || 'high',
    status, http_status: code || null, latency_ms: latency || null,
    last_checked: NOW_ISO, last_error: err || null,
    url_checked: null, extra: {},
  };
}

function _mkInc(id, sev, name, title, desc, diag, impact, startedMinsAgo) {
  const started = new Date(Date.now() - startedMinsAgo * 60000).toISOString();
  return {
    id, severity: sev, target_type: 'service', target_name: name,
    title, description: desc, diagnosis: diag, impact_label: impact,
    started_at: started, resolved_at: null,
    duration_seconds: startedMinsAgo * 60, duration_human: formatDuration(startedMinsAgo * 60),
  };
}

const BASE_SERVERS = [
  _mkServer('vps-myrock', 'OpenClaw', 'ok', 12, 36, 34,
    [_mkSvc('pagokids.com.mx', 'http', 'high', 'ok', 112, 200),
     _mkSvc('myrock.com.mx',   'http', 'medium', 'ok', 89, 200),
     _mkSvc('n8n',             'http', 'medium', 'ok', 204, 200)],
    [{domain:'myrock.com.mx', days_left:62, status:'ok'},
     {domain:'pagokids.com.mx', days_left:55, status:'ok'}],
    [{repo:'myrock-stack', branch:'main', commit_sha:'a1b2c3d',
      commit_message:'fix: payment webhook', author:'eljefe06',
      deployed_at: new Date(Date.now() - 5400000).toISOString(), status:'ok'}]),

  _mkServer('vps-suig', 'VPS-SUIG', 'ok', 8, 45, 38,
    [_mkSvc('cedhsinaloa.org.mx',   'http', 'high', 'ok', 198, 200),
     _mkSvc('suig.cedhsinaloa',     'http', 'high', 'ok', 182, 200),
     _mkSvc('buzon.cedhsinaloa',    'http', 'high', 'ok', 92, 200),
     _mkSvc('cedhs.xyz',            'http', 'medium', 'ok', 78, 200)],
    [{domain:'cedhsinaloa.org.mx', days_left:45, status:'ok'},
     {domain:'suig.cedhsinaloa.org.mx', days_left:45, status:'ok'},
     {domain:'buzon.cedhsinaloa.org.mx', days_left:38, status:'ok'}],
    [{repo:'suig', branch:'main', commit_sha:'e4f5g6h',
      commit_message:'chore: deps', author:'eljefe06',
      deployed_at: new Date(Date.now() - 70200000).toISOString(), status:'ok'}]),

  _mkServer('vps-oic', 'VPS-OIC', 'ok', 5, 32, 28,
    [_mkSvc('ser-cedh',      'http', 'high', 'ok', 152, 200),
     _mkSvc('declaraciones', 'http', 'high', 'ok', 164, 200),
     _mkSvc('denuncias',     'http', 'high', 'ok', 138, 200)],
    [], []),

  _mkServer('vps-mail', 'VPS-Mail', 'ok', 15, 58, 42,
    [_mkSvc('mailcow.sogo', 'http', 'high', 'ok', 248, 200),
     _mkSvc('smtp.587',     'smtp', 'high', 'ok', 45, null),
     _mkSvc('imap.993',     'imap', 'high', 'ok', 38, null),
     _mkSvc('mailcow.admin','http', 'medium', 'ok', 312, 200)],
    [{domain:'mail.cedhsinaloa.org.mx', days_left:18, status:'warning'}],
    []),
];

const MOCKS = [
  // Mock 1: todo OK
  {
    generated_at: NOW_ISO, schema_version: '1.0', overall_status: 'ok',
    incidents_open: 0, uptime: { since: NOW_ISO, seconds: 1209682, human: '14d 06h' },
    servers: BASE_SERVERS, dns_checks: [], recent_incidents: [],
  },

  // Mock 2: 1 crítico + 1 advertencia
  {
    generated_at: NOW_ISO, schema_version: '1.0', overall_status: 'critical',
    incidents_open: 2, uptime: { since: NOW_ISO, seconds: 1209682, human: '14d 06h' },
    servers: BASE_SERVERS.map((s, i) => {
      if (i !== 0) return s;
      return { ...s, status: 'critical', services: s.services.map((sv, j) =>
        j === 0
          ? { ...sv, status: 'critical', http_status: 520, latency_ms: null,
              last_error: 'Cloudflare 520 — connection refused at origin' }
          : sv
      )};
    }),
    dns_checks: [], recent_incidents: [
      _mkInc('inc-001', 'critical', 'pagokids.com.mx',
        'PagoKids no responde correctamente',
        'Cloudflare devuelve 520. VPS MyRock está vivo; otros servicios responden normal.',
        'Probable problema entre Cloudflare y el origen. Revisar nginx del contenedor pagokids-web y logs.',
        'Afecta usuarios públicos', 14),
      _mkInc('inc-002', 'warning', 'mailcow.sogo',
        'Mailcow webmail redirige 301',
        'SOGo responde con redirect en lugar de 200. Servicio sigue funcional pero con comportamiento inesperado.',
        'Verificar si fue cambio intencional reciente. Revisar config nginx-mailcow.',
        'Sin impacto operativo', 138),
    ],
  },

  // Mock 3: servidor down (agent_unreachable)
  {
    generated_at: NOW_ISO, schema_version: '1.0', overall_status: 'critical',
    incidents_open: 1, uptime: { since: NOW_ISO, seconds: 1209682, human: '14d 06h' },
    servers: BASE_SERVERS.map((s, i) => i === 1
      ? { ...s, status: 'down', agent_reachable: false, metrics: null,
          services: s.services.map(sv => ({ ...sv, status: 'unknown' })) }
      : s),
    dns_checks: [], recent_incidents: [
      _mkInc('inc-003', 'critical', 'vps-suig',
        'VPS-SUIG sin respuesta',
        'El agente SSH no responde. SUIG, buzón y cedhsinaloa.org.mx posiblemente caídos.',
        'Verificar estado del VPS en panel Hetzner. Si está corriendo, revisar sshd y firewall.',
        'Afecta usuarios públicos', 22),
    ],
  },

  // Mock 4: SSL crítico (<7d)
  {
    generated_at: NOW_ISO, schema_version: '1.0', overall_status: 'critical',
    incidents_open: 1, uptime: { since: NOW_ISO, seconds: 1209682, human: '14d 06h' },
    servers: BASE_SERVERS.map((s, i) => i === 3
      ? { ...s, ssl: [{ domain:'mail.cedhsinaloa.org.mx', days_left: 3, status:'critical' }] }
      : s),
    dns_checks: [], recent_incidents: [
      _mkInc('inc-004', 'critical', 'mail.cedhsinaloa.org.mx',
        'SSL mail.cedhsinaloa.org.mx vence en 3 días',
        'Certificado Let\'s Encrypt expira 2026-05-16. Mailcow dejará de funcionar con TLS.',
        'Ejecutar renovación Certbot desde el VPS-Mail. Si falla, revisar DNS y puertos 80/443.',
        'Afecta operación interna', 180),
    ],
  },

  // Mock 5: RAM alta en MyRock
  {
    generated_at: NOW_ISO, schema_version: '1.0', overall_status: 'warning',
    incidents_open: 1, uptime: { since: NOW_ISO, seconds: 1209682, human: '14d 06h' },
    servers: BASE_SERVERS.map((s, i) => i === 0
      ? { ...s, status: 'warning',
          metrics: { ...s.metrics, cpu_percent: 88, ram_percent: 91, disk_percent: 34 } }
      : s),
    dns_checks: [], recent_incidents: [
      _mkInc('inc-005', 'warning', 'vps-myrock',
        'OpenClaw — RAM crítica 91%',
        'RAM de MyRock supera 90%. CPU también elevada. Riesgo de OOM killer.',
        'Revisar containers con alto consumo: docker stats. Posible memory leak en n8n o Evolution.',
        'Afecta operación interna', 8),
    ],
  },
];

let activeMock = 0;

// ── Fetch ─────────────────────────────────────────────────────────────────────

async function fetchStatus() {
  if (location.protocol === 'file:') {
    return MOCKS[activeMock];
  }
  const resp = await fetch('/api/v1/status', { cache: 'no-store' });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

// ── Counters ──────────────────────────────────────────────────────────────────

function buildCounters(data) {
  let crit = 0, warn = 0, ok = 0;
  for (const srv of (data.servers || [])) {
    for (const svc of (srv.services || [])) {
      if (svc.status === 'critical' || svc.status === 'down') crit++;
      else if (svc.status === 'warning') warn++;
      else if (svc.status === 'ok') ok++;
    }
    for (const s of (srv.ssl || [])) {
      if (s.status === 'critical') crit++;
      else if (s.status === 'warning') warn++;
    }
    if (!srv.agent_reachable) crit++;
  }
  return { crit, warn, ok };
}

// ── Render orchestrator ───────────────────────────────────────────────────────

let lastData = null;

function renderDashboard(data) {
  lastData = data;

  const { crit, warn, ok } = buildCounters(data);

  document.querySelector('.sb-num-crit').textContent = crit;
  document.querySelector('.sb-num-warn').textContent = warn;
  document.querySelector('.sb-num-ok').textContent   = ok;

  const critEl = document.querySelector('.sb-crit');
  if (crit > 0) critEl.classList.add('active');
  else          critEl.classList.remove('active');

  if (data.uptime) {
    document.querySelector('.sb-uptime').textContent = data.uptime.human || '';
  }

  const openInc = (data.recent_incidents || []).filter(i => !i.resolved_at);
  renderIncidents(document.getElementById('incidents-block'), openInc);
  renderServices(document.getElementById('services-strip'), data.servers || []);
  renderInfra(document.getElementById('infra-row'), data.servers || []);
  renderPanels(
    document.getElementById('panel-changes'),
    document.getElementById('panel-certs'),
    document.getElementById('panel-pending'),
    data
  );

  document.querySelector('.footer-ts').textContent = 'ONLINE';

  // Mock label (dev only)
  if (location.protocol === 'file:') {
    const ml = document.querySelector('.footer-mock');
    if (ml) ml.textContent = `mock ${activeMock + 1}/5 · tecla 1-5`;
  }
}

// ── Clock + live duration ─────────────────────────────────────────────────────

function updateClock() {
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  document.querySelector('.sb-time').textContent =
    `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;

  document.querySelectorAll('.inc-duration[data-started-at]').forEach(el => {
    const secs = Math.floor((Date.now() - new Date(el.dataset.startedAt)) / 1000);
    el.textContent = formatDuration(secs);
  });
}

// ── Error overlay ─────────────────────────────────────────────────────────────

function showError(msg) {
  const el = document.querySelector('.api-error');
  el.querySelector('.api-error__sub').textContent = msg;
  el.classList.remove('hidden');
}

function hideError() {
  document.querySelector('.api-error').classList.add('hidden');
}

// ── Main loop ─────────────────────────────────────────────────────────────────

async function tick() {
  try {
    const data = await fetchStatus();
    hideError();
    renderDashboard(data);
  } catch (e) {
    showError(e.message);
  }
}

// ── Boot ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  tick();
  setInterval(tick, 5000);
  setInterval(updateClock, 1000);

  // Mock rotation (dev, file: protocol only)
  if (location.protocol === 'file:') {
    document.addEventListener('keydown', e => {
      const n = parseInt(e.key, 10);
      if (n >= 1 && n <= MOCKS.length) {
        activeMock = n - 1;
        tick();
      }
    });
  }

  // Orientation
  const warn = document.querySelector('.portrait-warning');
  function checkOrientation() {
    if (warn) {
      warn.style.display = window.innerHeight > window.innerWidth ? 'flex' : 'none';
    }
  }
  window.addEventListener('resize', checkOrientation);
  checkOrientation();
});
