const API = {
  list: '/firearms/api/list/',
  create: '/firearms/api/create/',
  update: (id) => `/firearms/api/update/${id}/`,
  delete: (id) => `/firearms/api/delete/${id}/`,
  ber: (id) => `/firearms/api/ber/${id}/`,
};

const PAR_API = {
  list: '/firearms/api/par/list/',
};

let allFirearms = [];
let filtered = [];
let currentPage = 1;
const pageSize = 5;
let sortKey = null;
let sortDir = 1;
let editingId = null;

let selectedBERId = null;

function getCookie(name) {
  const val = `; ${document.cookie}`;
  const parts = val.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}


async function apiPost(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify(data),
  });
  return res.json();
}

function prepareRemoval(id) {
  selectedBERId = id;
  const modal = document.getElementById('confirmationModal');
  if (modal) {
    modal.classList.add('open');
  }
}

function closeConfirmationModal() {
  selectedBERId = null;
  const modal = document.getElementById('confirmationModal');
  if (modal) {
    modal.classList.remove('open');
  }
}

async function moveToBER(id) {
  const firearm = allFirearms.find((item) => item.id == id);

  if (!firearm) {
    alert('Firearm record not found.');
    return;
  }

  const submitBtn = document.querySelector('#confirmRemovalForm button[type="submit"]');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
  }

  try {
    const berResponse = await fetch(API.ber(id), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({}),
    });

    const berResult = await berResponse.json();

    if (!berResult.success) {
      console.error('FIREARM STATUS UPDATE ERROR:', berResult.error);
      alert('Failed to update firearm status: ' + berResult.error);
      return;
    }

    closeConfirmationModal();
    await loadFirearms();

  } catch (err) {
    console.error('BER WORKFLOW ERROR:', err);
    alert('Network error: ' + err.message);
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Confirm';
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {

  document.getElementById('modalOverlay').addEventListener('click', e => {
    if (e.target === document.getElementById('modalOverlay')) closeModal();
  });

  document.getElementById('confirmRemovalForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    if (!selectedBERId) {
      alert('No firearm selected.');
      return;
    }

    await moveToBER(selectedBERId);
  });

  loadFirearms();
  loadPARStats();
});

async function loadFirearms() {
  try {
    const [firearmsRes, parRes] = await Promise.all([
      fetch(API.list),
      fetch(PAR_API.list)
    ]);

    const firearmsData = await firearmsRes.json();
    const parData = await parRes.json();

    const parMap = {};
    (parData.pars || []).forEach(p => {
      if (!parMap[p.firearm_id]) {
        parMap[p.firearm_id] = p.par_number;
      }
    });

    allFirearms = (firearmsData.firearms || []).map(f => ({
      ...f,
      parNumber: parMap[f.id] || 'N/A',
    }));

    filterTable();
  } catch (err) {
    console.error('Failed to load firearms:', err);
    document.getElementById('tableBody').innerHTML =
      `<tr><td colspan="11" style="text-align:center;padding:30px;color:var(--red)">
         Failed to load data. Check your connection.
       </td></tr>`;
  }
}

function updatePARStatsFromFallback() {
  const el = document.getElementById('par-initial-data');
  if (!el) return false;
  try {
    const data = JSON.parse(el.textContent);
    const count = data.validated || data.count || 0;
    document.getElementById('parCount').textContent = count;
    document.getElementById('parBar').style.width = count > 0 ? '100%' : '0%';
    return true;
  } catch (e) {
    return false;
  }
}

async function loadPARStats() {
  try {
    const res = await fetch(PAR_API.list);
    if (!res.ok) throw new Error('PAR API not available');

    const data = await res.json();
    const pars = data.pars || [];

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    let validatedPAR = 0;
    let expiringSoonPAR = 0;

    pars.forEach(p => {
      if (!p.expiry_date) {
        validatedPAR++;
        return;
      }

      const expiryDate = new Date(p.expiry_date);
      expiryDate.setHours(0, 0, 0, 0);

      const daysUntilExpiry = Math.ceil(
        (expiryDate - today) / (1000 * 60 * 60 * 24)
      );

      if (daysUntilExpiry > 0 && daysUntilExpiry <= 30) {
        expiringSoonPAR++;
      }

      if (daysUntilExpiry >= 0) {
        validatedPAR++;
      }
    });

    document.getElementById('parCount').textContent = validatedPAR;
    document.getElementById('parBar').style.width = validatedPAR > 0 ? '100%' : '0%';

    document.getElementById('expiringParCount').textContent = expiringSoonPAR;
    document.getElementById('expiringParBar').style.width =
      expiringSoonPAR > 0 ? '100%' : '0%';

  } catch (err) {
    console.error('Failed to load PAR stats:', err);

    if (!updatePARStatsFromFallback()) {
      document.getElementById('parCount').textContent = '—';
      document.getElementById('parBar').style.width = '0%';
    }

    document.getElementById('expiringParCount').textContent = '—';
    document.getElementById('expiringParBar').style.width = '0%';
  }
}


function updateStats() {
  const total = allFirearms.length;
  const validated = allFirearms.filter(f => f.validated === 'VALIDATED').length;

  document.getElementById('totalCount').textContent = total;
  document.getElementById('issuedCount').textContent = validated;
  document.getElementById('totalBar').style.width = '100%';
  document.getElementById('issuedBar').style.width = Math.max(4, Math.round((validated / (total || 1)) * 100)) + '%';
}

function statusBadge(s) {
  if (s === 'Serviceable') return `<span class="badge badge-green">SERVICEABLE</span>`;
  if (s === 'Unserviceable') return `<span class="badge badge-red">UNSERVICEABLE</span>`;
  if (s === 'BER') return `<span class="badge badge-red">UNSERVICEABLE</span>`;
  return `<span class="badge badge-orange">${s.toUpperCase()}</span>`;
}

function validatedBadge(v) {
  return v === 'VALIDATED'
    ? `<span class="badge badge-green">${v}</span>`
    : `<span class="badge badge-red">${v}</span>`;
}

function renderTable() {
  const tbody = document.getElementById('tableBody');
  const start = (currentPage - 1) * pageSize;
  const page = filtered.slice(start, start + pageSize);

  tbody.innerHTML = page.length
    ? page.map(f => `
        <tr>
          <td><strong>${f.name || 'N/A'}</strong></td>
          <td>${f.subunit || 'N/A'}</td>
          <td>${f.station || 'N/A'}</td>
          <td>${f.issuingUnit || 'N/A'}</td>
          <td style="font-family:monospace;font-size:12px">${f.faid || 'N/A'}</td>   
          <td><strong>${f.parNumber || 'N/A'}</strong></td>                           
          <td>${f.makeModel}</td>
          <td>${statusBadge(f.status)}</td>
          <td>${validatedBadge(f.validated)}</td>
          <td>
            <button class="action-btn" onclick="openActionModal(${f.id})">Edit ▸</button>
            <button class="action-btn" style="background:#ef4444;margin-left:4px"
                    onclick="prepareRemoval(${f.id})">BER</button>
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
  const el = document.getElementById('pagination');
  el.innerHTML = '';
  for (let i = 1; i <= pages; i++) {
    const b = document.createElement('button');
    b.className = 'page-btn' + (i === currentPage ? ' active' : '');
    b.textContent = i;
    b.onclick = () => { currentPage = i; renderTable(); };
    el.appendChild(b);
  }
}

function filterTable() {
  const q = document.getElementById('searchInput').value.toLowerCase();
  const sf = document.getElementById('statusFilter').value;

  filtered = allFirearms.filter(f => {
    const textMatch = [f.name, f.serialNo, f.station, f.faid, f.makeModel, f.subunit]
      .some(v => (v || '').toLowerCase().includes(q));
    const effectiveStatus = (f.status === 'BER' || f.status?.toLowerCase() === 'unserviceable')
      ? 'Unserviceable'
      : f.status;
    const statusMatch = !sf || effectiveStatus === sf;
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
    inputField('Name (Issued To)', 'f_name', f.name || '') +
    inputField('Subunit', 'f_subunit', f.subunit || '') +
    inputField('Station', 'f_station', f.station || '') +
    inputField('Issuing Unit', 'f_issuingUnit', f.issuingUnit || 'PNP FG') +
    inputField('FA ID / Serial No.', 'f_faid', f.faid || '') +
    inputField('PAR No.', 'f_parNumber', f.parNumber || '') +
    inputField('Item Description', 'f_makeModel', f.makeModel !== 'N/A' ? f.makeModel || '' : '') +
    selectField('Status', 'f_status', ['Serviceable', 'Unserviceable'], f.status || 'SERVICEABLE') +
    selectField('Remarks', 'f_validated', ['Validated', 'Expired/For Renewal'], f.validated || 'VALIDATED')
  );
}


function openActionModal(id) {
  editingId = id;
  const f = allFirearms.find(x => x.id === id);
  document.getElementById('modalTitle').textContent = 'Edit Firearm Record';
  document.getElementById('modalBody').innerHTML = buildForm(f);
  document.getElementById('modalSaveBtn').textContent = 'Save Changes';
  document.getElementById('modalOverlay').classList.add('open');
}

function openAddModal() {
  editingId = null;
  document.getElementById('modalTitle').textContent = 'Add New Firearm Record';
  document.getElementById('modalBody').innerHTML = buildForm();
  document.getElementById('modalSaveBtn').textContent = 'Add Record';
  document.getElementById('modalOverlay').classList.add('open');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
  editingId = null;
}

async function saveRecord() {
  const get = id => document.getElementById(id)?.value?.trim() || '';
  const data = {
    name: get('f_name'),
    subunit: get('f_subunit'),
    station: get('f_station'),
    issuingUnit: get('f_issuingUnit'),
    faid: get('f_faid'),
    makeModel: get('f_makeModel'),
    status: get('f_status'),
    validated: get('f_validated').toUpperCase(),
  };

  if (!data.name) { alert('Name is required.'); return; }

  const btn = document.getElementById('modalSaveBtn');
  btn.disabled = true;
  btn.textContent = 'Saving…';

  try {
    const url = editingId ? API.update(editingId) : API.create;
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
    btn.disabled = false;
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
  const headers = ['NAME', 'UNIT', 'SUBUNIT', 'STATION', 'ISSUING UNIT', 'FAID', 'SERIAL NO.', 'MAKE/MODEL', 'STATUS', 'VALIDATED'];
  const rows = filtered.map(f =>
    [f.name, f.unit, f.subunit, f.station, f.issuingUnit,
    f.faid, f.serialNo, f.makeModel, f.status, f.validated]
      .map(v => `"${v}"`).join(',')
  );
  const csv = [headers.join(','), ...rows].join('\n');
  const a = document.createElement('a');
  a.href = 'data:text/csv,' + encodeURIComponent(csv);
  a.download = 'firearms_issuances.csv';
  a.click();
}


window.openAddModal = openAddModal;
window.openActionModal = openActionModal;
window.closeModal = closeModal;
window.saveRecord = saveRecord;
window.deleteRecord = deleteRecord;
window.prepareRemoval = prepareRemoval;
window.filterTable = filterTable;
window.sortTable = sortTable;
window.exportCSV = exportCSV;
window.closeConfirmationModal = closeConfirmationModal;