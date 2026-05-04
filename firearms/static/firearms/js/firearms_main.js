const API = {
  list:   '/firearms/api/list/',
  create: '/firearms/api/create/',
  update: (id) => `/firearms/api/update/${id}/`,
  delete: (id) => `/firearms/api/delete/${id}/`,
};

let allFirearms = [];
let filtered    = [];
let currentPage = 1;
const pageSize  = 5;
let sortKey     = null;
let sortDir     = 1;
let editingId   = null;

function getCookie(name) {
  const val   = `; ${document.cookie}`;
  const parts = val.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

async function apiPost(url, data) {
  const res = await fetch(url, {
    method:  'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken':  getCookie('csrftoken'),
    },
    body: JSON.stringify(data),
  });
  return res.json();
}

async function loadFirearms() {
  try {
    const res  = await fetch(API.list);
    const data = await res.json();
    allFirearms = data.firearms || [];
    filterTable();
  } catch (err) {
    console.error('Failed to load firearms:', err);
    document.getElementById('tableBody').innerHTML =
      `<tr><td colspan="11" style="text-align:center;padding:30px;color:var(--red)">
         Failed to load data. Check your connection.
       </td></tr>`;
  }
}

function updateStats() {
  const total     = allFirearms.length;
  const validated = allFirearms.filter(f => f.validated === 'VALIDATED').length;
  const pending   = allFirearms.filter(f => f.validated === 'PENDING').length;
  const pct       = v => Math.max(4, Math.round((v / (total || 1)) * 100)) + '%';
  
  document.getElementById('totalCount').textContent  = total;
  document.getElementById('issuedCount').textContent = validated;
  document.getElementById('pendingCount').textContent= pending;

  document.getElementById('totalBar').style.width    = '100%';
  document.getElementById('issuedBar').style.width   = pct(validated);
  document.getElementById('pendingBar').style.width  = pct(pending);
}

function statusBadge(s) {
  if (s === 'Serviceable')   return `<span class="badge badge-green">${s}</span>`;
  if (s === 'Unserviceable') return `<span class="badge badge-red">${s}</span>`;
  if (s === 'Lost')          return `<span class="badge badge-orange">${s}</span>`;
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
          <td>
            <button class="action-btn" onclick="openActionModal(${f.id})">Edit ▸</button>
            <button class="action-btn" style="background:#ef4444;margin-left:4px"
                    onclick="deleteRecord(${f.id})">Del</button>
          </td>
        </tr>`).join('')
    : `<tr><td colspan="11" style="text-align:center;padding:30px;color:var(--muted)">No records found.</td></tr>`;

  document.getElementById('rowInfo').textContent =
    `Showing ${filtered.length ? start + 1 : 0}–${Math.min(start + pageSize, filtered.length)} of ${filtered.length}`;

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

  filtered = allFirearms.filter(f => {
    const textMatch   = [f.name, f.serialNo, f.station, f.faid, f.makeModel, f.subunit]
                          .some(v => (v || '').toLowerCase().includes(q));
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

function inputField(label, id, val = '') {
  return `
    <div style="margin-bottom:10px">
      <label class="modal-label" for="${id}">${label}</label>
      <input id="${id}" type="text" value="${val}"
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
    inputField('Name (Assigned To)',            'f_name',        f.name        || '') +
    inputField('Unit',                          'f_unit',        f.unit        !== 'N/A' ? f.unit        || 'PNP FG' : 'PNP FG') +
    inputField('Subunit',                       'f_subunit',     f.subunit     !== 'N/A' ? f.subunit     || '' : '') +
    inputField('Station',                       'f_station',     f.station     !== 'N/A' ? f.station     || '' : '') +
    inputField('Issuing Unit',                  'f_issuingUnit', f.issuingUnit !== 'N/A' ? f.issuingUnit || 'PNP FG' : 'PNP FG') +
    inputField('FAID / Serial',                 'f_faid',        f.faid        !== 'N/A' ? f.faid        || '' : '') +
    inputField('Serial No.',                    'f_serialNo',    f.serialNo    !== 'N/A' ? f.serialNo    || '' : '') +
    inputField('Make / Model / Kind / Caliber', 'f_makeModel',   f.makeModel   !== 'N/A' ? f.makeModel   || '' : '') +
    selectField('Status',    'f_status',    ['Serviceable', 'Unserviceable', 'Lost'], f.status    || 'SERVICEABLE') +
    selectField('Validated', 'f_validated', ['VALIDATED', 'PENDING'],                 f.validated || 'PENDING')
  );
}

function openActionModal(id) {
  editingId = id;
  const f   = allFirearms.find(x => x.id === id);
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

async function saveRecord() {
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

  if (!data.name) { alert('Name is required.'); return; }

  const btn       = document.getElementById('modalSaveBtn');
  btn.disabled    = true;
  btn.textContent = 'Saving…';

  try {
    const url    = editingId ? API.update(editingId) : API.create;
    const result = await apiPost(url, data);

    if (result.success) {
      closeModal();
      await loadFirearms();
    } else {
      alert('Error: ' + result.error);
    }
  } catch (err) {
    alert('Network error. Please try again.');
    console.error(err);
  } finally {
    btn.disabled    = false;
    btn.textContent = editingId ? 'Save Changes' : 'Add Record';
  }
}

async function deleteRecord(id) {
  if (!confirm('Delete this firearm record? This cannot be undone.')) return;
  try {
    const result = await apiPost(API.delete(id), {});
    if (result.success) {
      await loadFirearms();
    } else {
      alert('Error: ' + result.error);
    }
  } catch (err) {
    alert('Network error.');
  }
}

function exportCSV() {
  const headers = ['NAME','UNIT','SUBUNIT','STATION','ISSUING UNIT','FAID','SERIAL NO.','MAKE/MODEL','STATUS','VALIDATED'];
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
  loadFirearms();
});