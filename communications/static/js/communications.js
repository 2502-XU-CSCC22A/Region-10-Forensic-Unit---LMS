window.supabaseClient = window.supabaseClient || window.supabase.createClient(
  "https://vamjajitzyspdyfxisac.supabase.co",
  "sb_publishable_mTj-PK3WV3ZPqGOii548Ng_EXvssL54"
);

const supabase = window.supabaseClient;

// state
let communications = [];
let filtered = [];
let currentPage = 1;
const pageSize = 5;
let sortKey = null;
let sortDir = 1;
let editingId = null;

/* ---------------- FETCH DATA ---------------- */
async function fetchData() {
  const { data, error } = await supabase
    .from("communications_communication")
    .select("*");

  if (error) {
    console.error(error);
    return;
  }

  communications = data.map((item) => ({
    id: item.asset_ptr_id,
    type: item.type,
    serial: item.imei_serial,
    frequency: item.frequency_range,
    stock: item.stock_level,
  }));

  filtered = [...communications];
  renderTable();
  renderPagination();
}

/* ---------------- TABLE RENDER ---------------- */
function renderTable() {
  const tbody = document.getElementById("tableBody");

  tbody.innerHTML = filtered.map(c => `
    <tr>
      <td>${c.type}</td>
      <td>${c.serial}</td>
      <td>${c.frequency}</td>
      <td>${c.stock}</td>
      <td>
        <button class="edit-btn" data-id="${c.id}">Edit</button>
      </td>
    </tr>
  `).join("");

  // attach event listeners AFTER rendering
  document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      openActionModal(btn.dataset.id);
    });
  });
}

/* ---------------- PAGINATION ---------------- */
function renderPagination() {
  const pages = Math.ceil(filtered.length / pageSize);
  const el = document.getElementById("pagination");

  el.innerHTML = "";

  for (let i = 1; i <= pages; i++) {
    const b = document.createElement("button");
    b.className = "page-btn" + (i === currentPage ? " active" : "");
    b.textContent = i;

    b.onclick = () => {
      currentPage = i;
      renderTable();
    };

    el.appendChild(b);
  }
}

/* ---------------- FILTER ---------------- */
function filterTable() {
  const q = document.getElementById("searchInput").value.toLowerCase();
  const sf = document.getElementById("statusFilter").value;

  filtered = communications.filter((c) => {
    const textMatch =
      (c.type || "").toLowerCase().includes(q) ||
      (c.serial || "").toLowerCase().includes(q) ||
      (c.frequency || "").toLowerCase().includes(q);

    const statusMatch = !sf || c.status === sf;

    return textMatch && statusMatch;
  });

  currentPage = 1;
  renderTable();
  renderPagination();
}

/* ---------------- SORT ---------------- */
function sortTable(key) {
  sortDir = sortKey === key ? sortDir * -1 : 1;
  sortKey = key;

  filtered.sort((a, b) => {
    const av = (a[key] || "").toString().toLowerCase();
    const bv = (b[key] || "").toString().toLowerCase();
    return av < bv ? -sortDir : av > bv ? sortDir : 0;
  });

  renderTable();
}

/* ---------------- MODAL ---------------- */
function inputField(label, id, val = "", type = "text") {
  return `
    <div style="margin-bottom:10px">
      <label for="${id}">${label}</label>
      <input id="${id}" type="${type}" value="${val}"
        style="width:100%;padding:7px 10px;border:1px solid var(--border);
        border-radius:6px;margin-top:3px"/>
    </div>`;
}

function buildForm(c = {}) {
  return (
    inputField("Type", "c_type", c.type || "") +
    inputField("IMEI / Serial", "c_serial", c.serial || "") +
    inputField("Frequency Range", "c_frequency", c.frequency || "") +
    inputField("Stock Level", "c_stock", c.stock || 1, "number")
  );
}

function openActionModal(id) {
  editingId = id;

  const c = communications.find((x) => x.id === id);

  document.getElementById("modalTitle").textContent =
    "Edit Communications Record";

  document.getElementById("modalBody").innerHTML = buildForm(c);

  document.getElementById("modalSaveBtn").textContent = "Save Changes";

  document.getElementById("modalOverlay").classList.add("open");
}

function openAddModal() {
  editingId = null;

  const title = document.getElementById('modalTitle');
  const body = document.getElementById('modalBody');
  const btn = document.getElementById('modalSaveBtn');
  const overlay = document.getElementById('modalOverlay');

  if (!title || !body || !btn || !overlay) {
    console.error("Modal elements missing in HTML");
    return;
  }

  title.textContent = 'Add New Communications Record';
  body.innerHTML = buildForm();
  btn.textContent = 'Add Record';
  overlay.classList.add('open');
}

function closeModal() {
  document.getElementById("modalOverlay").classList.remove("open");
  editingId = null;
}

/* ---------------- SAVE ---------------- */
async function saveRecord() {
  const get = (id) => document.getElementById(id)?.value?.trim() || "";

  const recordData = {
  type: get("c_type"),
  imei_serial: get("c_serial"),
  frequency_range: get("c_frequency"),
  stock_level: parseInt(get("c_stock")) || 0,
};

  if (!recordData.type || !recordData.imei_serial) {
    alert("Type and Serial are required.");
    return;
  }

  if (editingId) {
    const { error } = await supabase
      .from("communications_communication")
      .update(recordData)
      .eq("asset_ptr_id", editingId);

    if (error) {
      console.error(error);
      alert("Update failed");
      return;
    }
  } else {
    const { error } = await supabase
      .from("communications_communication")
      .insert([recordData]);

    if (error) {
      console.error(error);
      alert("Insert failed");
      return;
    }
  }

  await fetchData();
  closeModal();
}

/* ---------------- EXPORT CSV ---------------- */
function exportCSV() {
  const headers = ["TYPE", "SERIAL", "FREQUENCY", "STOCK"];

  const rows = filtered.map((c) =>
    [c.type, c.serial, c.frequency, c.stock]
      .map((v) => `"${v}"`)
      .join(",")
  );

  const csv = [headers.join(","), ...rows].join("\n");

  const a = document.createElement("a");
  a.href = "data:text/csv," + encodeURIComponent(csv);
  a.download = "communications_export.csv";
  a.click();
}

/* ---------------- INIT ---------------- */
document.addEventListener("DOMContentLoaded", () => {
  fetchData();

  const btn = document.getElementById("addRecordBtn");
  if (btn) {
    btn.addEventListener("click", openAddModal);
  }
});

window.openAddModal = openAddModal;
window.openActionModal = openActionModal;
window.closeModal = closeModal;
window.saveRecord = saveRecord;