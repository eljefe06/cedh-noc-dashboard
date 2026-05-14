function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function renderIncidents(container, incidents) {
  if (!incidents || incidents.length === 0) {
    container.innerHTML = '<div class="inc-empty">✓ Sin incidentes activos</div>';
    return;
  }

  container.innerHTML = incidents.map(inc => {
    const cls  = sevCls(inc.severity);
    const tag  = sevTag(inc.severity);
    const secs = inc.started_at
      ? Math.floor((Date.now() - new Date(inc.started_at)) / 1000)
      : (inc.duration_seconds || 0);
    const dur  = formatDuration(secs);

    const diagHtml   = inc.diagnosis
      ? `<p class="inc-diag">${esc(inc.diagnosis)}</p>` : '';
    const descHtml   = inc.description
      ? `<p class="inc-desc">${esc(inc.description)}</p>` : '';
    const impactHtml = inc.impact_label
      ? `<span class="inc-impact">${esc(inc.impact_label)}</span>` : '';
    const startedAt  = inc.started_at ? ` data-started-at="${esc(inc.started_at)}"` : '';

    return `<div class="incident ${cls}" data-inc-id="${esc(inc.id)}">
  <div class="inc-left">
    <span class="inc-tag">${tag}</span>
    <p class="inc-title">${esc(inc.title || inc.target_name)}</p>
    ${descHtml}
    ${diagHtml}
  </div>
  <div class="inc-right">
    <span class="inc-since">caído desde</span>
    <span class="inc-duration"${startedAt}>${esc(dur)}</span>
    ${impactHtml}
  </div>
</div>`;
  }).join('');
}
