function renderPanels(changeEl, certEl, pendingEl, data) {
  _renderChanges(changeEl, data);
  _renderCerts(certEl, data);
  _renderPending(pendingEl, data);
}

function _renderChanges(el, data) {
  const deploys = [];
  for (const srv of (data.servers || [])) {
    for (const d of (srv.deploys || [])) {
      deploys.push(d);
    }
  }
  deploys.sort((a, b) => new Date(b.deployed_at) - new Date(a.deployed_at));

  if (deploys.length === 0) {
    el.innerHTML = '<div class="panel-empty">sin cambios recientes</div>';
    return;
  }

  el.innerHTML = deploys.slice(0, 6).map(d => {
    const t = new Date(d.deployed_at).toLocaleTimeString('es-MX', {
      hour: '2-digit', minute: '2-digit', hour12: false
    });
    const sha = (d.commit_sha || '').slice(0, 7);
    return `<div class="panel-line">
  <span class="panel-time">${esc(t)}</span>
  <span class="panel-tag info">deploy</span>
  <span class="panel-msg">${esc(d.repo)} · ${esc(sha)}</span>
</div>`;
  }).join('');
}

function _renderCerts(el, data) {
  const certs = [];
  for (const srv of (data.servers || [])) {
    for (const s of (srv.ssl || [])) {
      certs.push(s);
    }
  }
  certs.sort((a, b) => a.days_left - b.days_left);

  if (certs.length === 0) {
    el.innerHTML = '<div class="panel-empty">sin datos SSL</div>';
    return;
  }

  el.innerHTML = certs.slice(0, 7).map(c => {
    const cls = c.days_left < 7 ? 'crit' : c.days_left < 30 ? 'warn' : 'ok';
    const short = c.domain
      .replace(/\.org\.mx$/, '')
      .replace(/\.com\.mx$/, '');
    return `<div class="panel-line">
  <span class="panel-key">${esc(short)}</span>
  <span class="panel-val ${cls}">${c.days_left}d</span>
</div>`;
  }).join('');
}

function _renderPending(el, data) {
  const items = [];

  for (const inc of (data.recent_incidents || [])) {
    if (inc.resolved_at) continue;
    const secs = inc.started_at
      ? Math.floor((Date.now() - new Date(inc.started_at)) / 1000)
      : (inc.duration_seconds || 0);
    const cls = sevCls(inc.severity);
    items.push({
      key: inc.title || inc.target_name,
      val: formatDuration(secs),
      cls,
    });
  }

  // Expiring certs not already covered by incidents
  const incTargets = new Set((data.recent_incidents || [])
    .filter(i => !i.resolved_at && i.target_type === 'ssl')
    .map(i => i.target_name));

  for (const srv of (data.servers || [])) {
    for (const c of (srv.ssl || [])) {
      if (c.days_left <= 30 && !incTargets.has(c.domain)) {
        const cls = c.days_left < 7 ? 'crit' : 'warn';
        items.push({
          key: `renovar SSL ${c.domain.split('.')[0]}`,
          val: `vence ${c.days_left}d`,
          cls,
        });
      }
    }
  }

  if (items.length === 0) {
    el.innerHTML = '<div class="panel-empty ok">✓ Sin pendientes urgentes</div>';
    return;
  }

  el.innerHTML = items.slice(0, 6).map(p => `<div class="panel-line">
  <span class="panel-key">${esc(p.key)}</span>
  <span class="panel-val ${p.cls}">${esc(p.val)}</span>
</div>`).join('');
}
