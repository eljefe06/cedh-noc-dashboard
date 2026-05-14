function renderInfra(container, servers) {
  container.innerHTML = servers.map(srv => {
    const dotCls = !srv.agent_reachable ? 'crit' : statusCls(srv.status);
    const m = srv.metrics;

    let statsHtml;
    if (!srv.agent_reachable) {
      statsHtml = `<div class="vps-stats"><span class="crit">AGENT DOWN</span></div>`;
    } else if (m) {
      const cpuCls = m.cpu_percent > 90 ? 'crit' : m.cpu_percent > 75 ? 'warn' : '';
      const ramCls = m.ram_percent > 90 ? 'crit' : m.ram_percent > 75 ? 'warn' : '';
      const dskCls = m.disk_percent > 90 ? 'crit' : m.disk_percent > 75 ? 'warn' : '';
      statsHtml = `<div class="vps-stats">
  <span class="${cpuCls}">cpu ${Math.round(m.cpu_percent)}</span>
  <span class="${ramCls}">ram ${Math.round(m.ram_percent)}</span>
  <span class="${dskCls}">dsk ${Math.round(m.disk_percent)}</span>
</div>`;
    } else {
      statsHtml = `<div class="vps-stats"><span class="">sin métricas</span></div>`;
    }

    return `<div class="vps-card">
  <span class="vps-dot ${dotCls}"></span>
  <div class="vps-info">
    <div class="vps-name">${esc(srv.display_name)}</div>
    ${statsHtml}
  </div>
</div>`;
  }).join('');
}
