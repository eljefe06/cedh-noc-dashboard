function renderServices(container, servers) {
  const all = [];
  for (const srv of servers) {
    for (const svc of (srv.services || [])) {
      if (svc.type === 'http') all.push(svc);
    }
  }

  // Sort: high criticality first, then by status severity (crit/down before warn before ok)
  const sevOrder = { critical: 0, down: 1, warning: 2, ok: 3, unknown: 4 };
  const critOrder = { high: 0, medium: 1, low: 2 };
  all.sort((a, b) => {
    const co = (critOrder[a.criticality] || 1) - (critOrder[b.criticality] || 1);
    if (co !== 0) return co;
    return (sevOrder[a.status] || 3) - (sevOrder[b.status] || 3);
  });

  const shown = all.slice(0, 8);

  container.innerHTML = shown.map(svc => {
    const cls = statusCls(svc.status);
    let meta;
    if (svc.latency_ms != null && svc.http_status != null) {
      meta = `${svc.latency_ms}ms · ${svc.http_status}`;
    } else if (svc.latency_ms != null) {
      meta = `${svc.latency_ms}ms`;
    } else if (svc.status !== 'ok') {
      meta = svc.last_error || svc.status.toUpperCase();
    } else {
      meta = 'OK';
    }
    const name = svc.name
      .replace(/\.cedhsinaloa\.org\.mx$/, '')
      .replace(/\.cedhsinaloa$/, '')
      .replace(/\.com\.mx$/, '')
      .replace(/\.org\.mx$/, '')
      .replace(/mailcow\./, '');

    return `<div class="svc-chip ${cls}">
  <div class="svc-chip-name">${esc(name)}</div>
  <div class="svc-chip-meta">${esc(meta)}</div>
</div>`;
  }).join('');
}
