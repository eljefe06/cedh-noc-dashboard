export const STATUS_CLASS = {
  ok:       'status-ok',
  warning:  'status-warn',
  critical: 'status-bad',
  down:     'status-bad',
  unknown:  'status-unknown',
};

export const STATUS_COLOR = {
  ok:       'var(--neon-lime)',
  warning:  'var(--neon-orange)',
  critical: 'var(--neon-magenta)',
  down:     'var(--neon-magenta)',
  unknown:  'var(--text-tertiary)',
};

export function statusClass(status) {
  return STATUS_CLASS[status] ?? 'status-unknown';
}

export function statusColor(status) {
  return STATUS_COLOR[status] ?? 'var(--text-tertiary)';
}
