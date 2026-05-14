const STATUS_CLS = {
  ok:       'ok',
  warning:  'warn',
  critical: 'crit',
  down:     'crit',
  unknown:  '',
};

function statusCls(s) { return STATUS_CLS[s] || ''; }

const SEV_TAG  = { critical: 'CRÍTICO', warning: 'ADVERTENCIA' };
const SEV_CLS  = { critical: 'crit',    warning: 'warn' };
function sevTag(sv) { return SEV_TAG[sv] || sv.toUpperCase(); }
function sevCls(sv) { return SEV_CLS[sv] || 'warn'; }
