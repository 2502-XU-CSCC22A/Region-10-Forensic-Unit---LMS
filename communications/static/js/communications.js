console.log("COMM JS LOADED");

/* ---------------- SAFE SUPABASE INIT ---------------- */
window.supabaseClient = window.supabaseClient || window.supabase.createClient(
  "https://vamjajitzyspdyfxisac.supabase.co",
  "sb_publishable_mTj-PK3WV3ZPqGOii548Ng_EXvssL54"
);

const sb = window.supabaseClient;

/* ---------------- STATE ---------------- */
let communications = [];
let filtered = [];
let currentPage = 1;
const pageSize = 5;
let editingId = null;

/* ---------------- HELPERS ---------------- */
function getValue(id) {
  return document.getElementById(id)?.value?.trim() || "";
}

function todayDate() {
  return new Date().toISOString().split("T")[0];
}

function generatePropertyNo() {
  return "PN-" + Date.now();
}

/* ---------------- FETCH DATA ---------------- */
async function fetchData() {
  const { data, error } = await sb
    .from("communications_communication")
    .select("*")
    .order("asset_ptr_id", { ascending: false });

  if (error) {
    console.error("FETCH ERROR:", error);
    alert("Failed to load communications.");
    return;
  }

  communications = data
    .map((item) => ({
      id: item.asset_ptr_id,
      type: item.type || "",
      serial: item.imei_serial || "",
      frequency: item.frequency_range || "",
      stock: item.stock_level || 0,
    }))
    .filter((item) => item.stock > 0);

  filtered = [...communications];
  currentPage = 1;

  renderTable();
  renderPagination();
  updateStats();
}

/* ---------------- TABLE ---------------- */
function renderTable() {
  const tbody = document.getElementById("tableBody");

  const start = (currentPage - 1) * pageSize;
  const pageItems = filtered.slice(start, start + pageSize);

  if (pageItems.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align:center;">No records found</td>
      </tr>
    `;
    document.getElementById("rowInfo").textContent = "No records";
    return;
  }

  tbody.innerHTML = pageItems.map(c => `
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

  document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      openActionModal(btn.dataset.id);
    });
  });

  document.getElementById("rowInfo").textContent =
    `Showing ${start + 1}-${Math.min(start + pageSize, filtered.length)} of ${filtered.length}`;
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
      renderPagination();
    };

    el.appendChild(b);
  }
}

/* ---------------- STATS ---------------- */
function updateStats() {
  document.getElementById("totalCount").textContent = communications.length;
  document.getElementById("issuedCount").textContent = communications.length;
  document.getElementById("parCount").textContent = 0;

  document.getElementById("totalBar").style.width = "100%";
  document.getElementById("issuedBar").style.width = "100%";
  document.getElementById("parBar").style.width = "0%";
}

/* ---------------- FILTER ---------------- */
function filterTable() {
  const q = document.getElementById("searchInput").value.toLowerCase();

  filtered = communications.filter((c) =>
    c.type.toLowerCase().includes(q) ||
    c.serial.toLowerCase().includes(q) ||
    c.frequency.toLowerCase().includes(q)
  );

  currentPage = 1;
  renderTable();
  renderPagination();
}

/* ---------------- MODAL ---------------- */
function inputField(label, id, val = "", type = "text") {
  return `
    <div style="margin-bottom:10px">
      <label>${label}</label>
      <input id="${id}" type="${type}" value="${val}"
        style="width:100%;padding:7px;border:1px solid #ccc;border-radius:6px;margin-top:3px"/>
    </div>
  `;
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
  const c = communications.find(x => x.id == id);

  document.getElementById("modalTitle").textContent = "Edit Record";
  document.getElementById("modalBody").innerHTML = buildForm(c);
  document.getElementById("modalSaveBtn").textContent = "Save";

  document.getElementById("modalOverlay").classList.add("open");
}

function openAddModal() {
  editingId = null;

  document.getElementById("modalTitle").textContent = "Add Record";
  document.getElementById("modalBody").innerHTML = buildForm();
  document.getElementById("modalSaveBtn").textContent = "Add";

  document.getElementById("modalOverlay").classList.add("open");
}

function closeModal() {
  document.getElementById("modalOverlay").classList.remove("open");
}

/* ---------------- SAVE ---------------- */
async function saveRecord() {
  const type = getValue("c_type");
  const serial = getValue("c_serial");
  const frequency = getValue("c_frequency");
  const stock = parseInt(getValue("c_stock")) || 0;

  console.log("TYPE:", type);
  console.log("SERIAL:", serial);

  if (!type || !serial) {
    alert("Type and IMEI / Serial are required.");
    return;
  }

  if (editingId) {
    const oldRecord = communications.find(c => c.id == editingId);
    const oldStock = oldRecord ? oldRecord.stock : null;

    const { error } = await sb
      .from("communications_communication")
      .update({
        type: type,
        imei_serial: serial,
        frequency_range: frequency,
        stock_level: stock,
      })
      .eq("asset_ptr_id", editingId);

    if (error) {
      console.error("UPDATE ERROR:", error);
      alert(error.message);
      return;
    }

    // Save to activity log only if stock changed
    if (oldStock !== stock) {
      const { error: logError } = await sb
        .from("communications_activitylog")
        .insert([{
          communication_id: editingId,
          action: "Stock Updated",
          old_stock: oldStock,
          new_stock: stock,
          details: `${type} stock changed from ${oldStock} to ${stock}`
        }]);

      if (logError) {
        console.error("ACTIVITY LOG ERROR:", logError);
        alert("Stock updated, but activity log failed: " + logError.message);
        return;
      }
    }

  } else {
    const { data: parentData, error: parentError } = await sb
      .from("config_asset")
      .insert([{
        date_acquired: todayDate(),
        property_no: generatePropertyNo(),
        serial_no: serial,
        model: type,
        category_id: 2,
        "StatusID": 1
      }])
      .select("id")
      .single();

    if (parentError) {
      console.error("PARENT SAVE ERROR:", parentError);
      alert(parentError.message);
      return;
    }

    const { error: childError } = await sb
      .from("communications_communication")
      .insert([{
        asset_ptr_id: parentData.id,
        type: type,
        imei_serial: serial,
        frequency_range: frequency,
        stock_level: stock
      }]);

    if (childError) {
      console.error("CHILD SAVE ERROR:", childError);
      alert(childError.message);
      return;
    }
  }

  const { error: disposalError } = await sb
  .from("disposal_disposalitems")
  .insert([{
    asset_ptr_id: editingId,
    disposal_reason: "Stock reached zero",
    disposal_date: new Date().toISOString(),
    last_sync: new Date().toISOString()
  }]);

  await fetchData();
  closeModal();
}

/* ---------------- EXPORT ---------------- */
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

  document.getElementById("addRecordBtn")?.addEventListener("click", openAddModal);
  document.getElementById("modalSaveBtn")?.addEventListener("click", saveRecord);
  document.getElementById("closeModalBtn")?.addEventListener("click", closeModal);
  document.getElementById("closeModalBtn2")?.addEventListener("click", closeModal);
});

/* ---------------- GLOBAL ---------------- */
window.openAddModal = openAddModal;
window.openActionModal = openActionModal;
window.closeModal = closeModal;
window.saveRecord = saveRecord;
window.filterTable = filterTable;
window.exportCSV = exportCSV;