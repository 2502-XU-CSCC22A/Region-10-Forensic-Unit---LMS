let firearms = [];

let nextId      = 9;
let filtered    = [...firearms];
let currentPage = 1;
const pageSize  = 5;
let sortKey     = null;
let sortDir     = 1;
let editingId   = null;

function updateStats() {
  const total     = firearms.length;
  const validated = firearms.filter(f => f.validated === 'VALIDATED').length;
  const pending   = firearms.filter(f => f.validated === 'PENDING').length;
  const pct       = v => Math.max(4, Math.round((v / total) * 100)) + '%';

  document.getElementById('totalCount').textContent   = total;
  document.getElementById('issuedCount').textContent  = validated;
  document.getElementById('pendingCount').textContent = pending;

  document.getElementById('totalBar').style.width   = '100%';
  document.getElementById('issuedBar').style.width  = pct(validated);
  document.getElementById('pendingBar').style.width = pct(pending);
}

function statusBadge(s) {
  if (s === 'SERVICEABLE')   return `<span class="badge badge-green">${s}</span>`;
  if (s === 'UNSERVICEABLE') return `<span class="badge badge-red">${s}</span>`;
  return `<span class="badge badge-orange">${s}</span>`;
}

function validatedBadge(v) {
  return v === 'VALIDATED'
    ? `<span class="badge badge-blue">${v}</span>`
    : `<span class="badge badge-orange">${v}</span>`;
}

function renderTable() {
  const tbody = document.getElementById('tableBody');
  const start = (currentPage - 1) * pageSize;
  const page  = filtered.slice(start, start + pageSize);

  tbody.innerHTML = page.length
    ? page.map(f => `
        <tr>
          <td><strong>${f.name}</strong></td>
          <td>${f.unit}</td>
          <td>${f.subunit}</td>
          <td>${f.station}</td>
          <td>${f.issuingUnit}</td>
          <td style="font-family:monospace;font-size:12px">${f.faid}</td>
          <td><strong>${f.serialNo}</strong></td>
          <td>${f.makeModel}</td>
          <td>${statusBadge(f.status)}</td>
          <td>${validatedBadge(f.validated)}</td>
          <td><button class="action-btn" onclick="openActionModal(${f.id})">Action ▸</button></td>
        </tr>`).join('')
    : `<tr><td colspan="11" style="text-align:center;padding:30px;color:var(--muted)">No records found.</td></tr>`;

  document.getElementById('rowInfo').textContent =
    `Showing ${Math.min(start + 1, filtered.length)}–${Math.min(start + pageSize, filtered.length)} of ${filtered.length}`;

  renderPagination();
  updateStats();
}

function renderPagination() {
  const pages = Math.ceil(filtered.length / pageSize);
  const el    = document.getElementById('pagination');
  el.innerHTML = '';

  for (let i = 1; i <= pages; i++) {
    const b       = document.createElement('button');
    b.className   = 'page-btn' + (i === currentPage ? ' active' : '');
    b.textContent = i;
    b.onclick     = () => { currentPage = i; renderTable(); };
    el.appendChild(b);
  }
}

function filterTable() {
  const q  = document.getElementById('searchInput').value.toLowerCase();
  const sf = document.getElementById('statusFilter').value;

  filtered = firearms.filter(f => {
    const textMatch   = [f.name, f.serialNo, f.station, f.faid, f.makeModel, f.subunit]
                          .some(v => v.toLowerCase().includes(q));
    const statusMatch = !sf || f.status === sf;
    return textMatch && statusMatch;
  });

  if (sortKey) applySortFiltered();
  currentPage = 1;
  renderTable();
}

function sortTable(key) {
  sortDir = sortKey === key ? sortDir * -1 : 1;
  sortKey = key;
  applySortFiltered();
  renderTable();
}

function applySortFiltered() {
  filtered.sort((a, b) => {
    const av = (a[sortKey] || '').toString().toLowerCase();
    const bv = (b[sortKey] || '').toString().toLowerCase();
    return av < bv ? -sortDir : av > bv ? sortDir : 0;
  });
}

function inputField(label, id, val = '', type = 'text') {
  return `
    <div style="margin-bottom:10px">
      <label class="modal-label" for="${id}">${label}</label>
      <input id="${id}" type="${type}" value="${val}"
        style="width:100%;padding:7px 10px;border:1px solid var(--border);
               border-radius:6px;font-size:13px;font-family:inherit;margin-top:3px"/>
    </div>`;
}

function selectField(label, id, options, val = '') {
  const opts = options.map(o =>
    `<option value="${o}" ${o === val ? 'selected' : ''}>${o}</option>`
  ).join('');
  return `
    <div style="margin-bottom:10px">
      <label class="modal-label" for="${id}">${label}</label>
      <select id="${id}"
        style="width:100%;padding:7px 10px;border:1px solid var(--border);
               border-radius:6px;font-size:13px;font-family:inherit;margin-top:3px">
        ${opts}
      </select>
    </div>`;
}

function buildForm(f = {}) {
  return (
    inputField('Name',                    'f_name',        f.name        || '')       +
    inputField('Unit',                    'f_unit',        f.unit        || 'PNP FG') +
    inputField('Subunit',                 'f_subunit',     f.subunit     || '')       +
    inputField('Station',                 'f_station',     f.station     || '')       +
    inputField('Issuing Unit',            'f_issuingUnit', f.issuingUnit || 'PNP FG') +
    inputField('FAID',                    'f_faid',        f.faid        || '')       +
    inputField('Serial No.',              'f_serialNo',    f.serialNo    || '')       +
    inputField('Make / Model / Kind / Caliber', 'f_makeModel', f.makeModel || '')    +
    selectField('Status',    'f_status',    ['SERVICEABLE', 'UNSERVICEABLE', 'LOST'], f.status    || 'SERVICEABLE') +
    selectField('Validated', 'f_validated', ['VALIDATED', 'PENDING'],                 f.validated || 'PENDING')
  );
}

function openActionModal(id) {
  editingId = id;
  const f   = firearms.find(x => x.id === id);
  document.getElementById('modalTitle').textContent   = 'Edit Firearm Record';
  document.getElementById('modalBody').innerHTML      = buildForm(f);
  document.getElementById('modalSaveBtn').textContent = 'Save Changes';
  document.getElementById('modalOverlay').classList.add('open');
}

function openAddModal() {
  editingId = null;
  document.getElementById('modalTitle').textContent   = 'Add New Firearm Record';
  document.getElementById('modalBody').innerHTML      = buildForm();
  document.getElementById('modalSaveBtn').textContent = 'Add Record';
  document.getElementById('modalOverlay').classList.add('open');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
  editingId = null;
}

function saveRecord() {
  const get  = id => document.getElementById(id)?.value?.trim() || '';
  const data = {
    name:        get('f_name'),
    unit:        get('f_unit'),
    subunit:     get('f_subunit'),
    station:     get('f_station'),
    issuingUnit: get('f_issuingUnit'),
    faid:        get('f_faid'),
    serialNo:    get('f_serialNo'),
    makeModel:   get('f_makeModel'),
    status:      get('f_status'),
    validated:   get('f_validated'),
  };

  if (!data.name || !data.serialNo) {
    alert('Name and Serial No. are required.');
    return;
  }

  if (editingId) {
    const idx     = firearms.findIndex(f => f.id === editingId);
    firearms[idx] = { ...firearms[idx], ...data };
  } else {
    firearms.push({ id: nextId++, ...data });
  }

  filterTable();
  closeModal();
}

function exportCSV() {
  const headers = ['NAME','UNIT','SUBUNIT','STATION','ISSUING UNIT','FAID','SERIAL NO.','MAKE/MODEL/KIND/CALIBER','STATUS','VALIDATED'];
  const rows    = filtered.map(f =>
    [f.name, f.unit, f.subunit, f.station, f.issuingUnit,
     f.faid, f.serialNo, f.makeModel, f.status, f.validated]
    .map(v => `"${v}"`).join(',')
  );
  const csv = [headers.join(','), ...rows].join('\n');
  const a   = document.createElement('a');
  a.href    = 'data:text/csv,' + encodeURIComponent(csv);
  a.download = 'firearms_issuances.csv';
  a.click();
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('modalOverlay').addEventListener('click', e => {
    if (e.target === document.getElementById('modalOverlay')) closeModal();
  });
  filterTable();
});