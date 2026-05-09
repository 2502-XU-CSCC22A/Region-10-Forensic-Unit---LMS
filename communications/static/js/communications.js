console.log("COMM JS LOADED");

window.supabaseClient = window.supabaseClient || window.supabase.createClient(
  "https://vamjajitzyspdyfxisac.supabase.co",
  "sb_publishable_mTj-PK3WV3ZPqGOii548Ng_EXvssL54"
);

const sb = window.supabaseClient;

let communications = [];
let filtered = [];
let currentPage = 1;
const pageSize = 5;
let editingId = null;

function getValue(id) {
  return document.getElementById(id)?.value?.trim() || "";
}

function todayDate() {
  return new Date().toISOString().split("T")[0];
}

function generatePropertyNo() {
  return "PN-" + Date.now();
}

function statusBadge(status) {
  if (status === "SERVICEABLE") {
    return `<span class="badge badge-green">SERVICEABLE</span>`;
  }

  if (status === "UNSERVICEABLE") {
    return `<span class="badge badge-red">UNSERVICEABLE</span>`;
  }

  return `<span class="badge badge-orange">${status || "N/A"}</span>`;
}

function remarksBadge(remarks) {
  if (remarks === "VALIDATED") {
    return `<span class="badge badge-green">VALIDATED</span>`;
  }

  return `<span class="badge badge-red">${remarks || "N/A"}</span>`;
}

async function addActivityLog({ communicationId, action, details }) {
  const { error } = await sb
    .from("communications_activitylog")
    .insert([{
      communication_id: communicationId,
      action: action,
      details: details,
      old_stock: null,
      new_stock: null
    }]);

  if (error) {
    console.error("ACTIVITY LOG ERROR:", error);
  }
}

async function fetchData() {
  const { data: commData, error: commError } = await sb
    .from("communications_communication")
    .select("*")
    .order("asset_ptr_id", { ascending: false });

  if (commError) {
    console.error("FETCH COMM ERROR:", commError);
    alert("Failed to load communications.");
    return;
  }

  const communicationIds = commData.map(item => item.asset_ptr_id);

  let parMap = {};

  if (communicationIds.length > 0) {
    const { data: parData, error: parError } = await sb
      .from("communications_parrecord")
      .select("communication_id, par_number, created_at")
      .in("communication_id", communicationIds)
      .order("created_at", { ascending: false });

    if (parError) {
      console.error("FETCH PAR ERROR:", parError);
    }

    if (parData) {
      parData.forEach(par => {
        const commId = Number(par.communication_id);

        if (!parMap[commId]) {
          parMap[commId] = par.par_number;
        }
      });
    }
  }

  communications = commData
    .filter(item => item.is_deleted !== true)
    .map((item) => ({
      id: item.asset_ptr_id,
      type: item.type || "",
      serial: item.imei_serial || "",
      parNo: parMap[Number(item.asset_ptr_id)] || "N/A",
      radioId: item.radio_id || "",
      status: item.status || "SERVICEABLE",
      remarks: item.remarks || "VALIDATED",
    }));

  filtered = [...communications];
  currentPage = 1;

  renderTable();
  renderPagination();
  updateStats();
}

function renderTable() {
  const tbody = document.getElementById("tableBody");

  const start = (currentPage - 1) * pageSize;
  const pageItems = filtered.slice(start, start + pageSize);

  if (pageItems.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center;">
          No records found
        </td>
      </tr>
    `;

    document.getElementById("rowInfo").textContent = "No records";
    return;
  }

  tbody.innerHTML = pageItems.map(c => `
    <tr>
      <td>${c.type}</td>
      <td>${c.serial}</td>
      <td>${c.parNo}</td>
      <td>${c.radioId}</td>
      <td>${statusBadge(c.status)}</td>
      <td>${remarksBadge(c.remarks)}</td>
      <td>
        <div style="display:flex; gap:8px; align-items:center;">
          <button
            class="action-btn"
            onclick="openActionModal('${c.id}')"
          >
            Edit ▸
          </button>

          <button
            class="delete-btn"
            onclick="moveToBER('${c.id}')"
          >
            BER
          </button>
        </div>
      </td>
    </tr>
  `).join("");

  document.getElementById("rowInfo").textContent =
    `Showing ${start + 1}-${Math.min(start + pageSize, filtered.length)} of ${filtered.length}`;
}

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

function updateStats() {
  const total = communications.length;

  const serviceable = communications.filter(
    c => c.status === "SERVICEABLE"
  ).length;

  const validated = communications.filter(
    c => c.remarks === "VALIDATED"
  ).length;

  document.getElementById("totalCount").textContent = total;
  document.getElementById("issuedCount").textContent = serviceable;
  document.getElementById("parCount").textContent = validated;
  document.getElementById("totalBar").style.width =
    total > 0 ? "100%" : "0%";

  document.getElementById("issuedBar").style.width =
    total > 0
      ? Math.max(5, Math.round((serviceable / total) * 100)) + "%"
      : "0%";

  document.getElementById("parBar").style.width =
    total > 0
      ? Math.max(5, Math.round((validated / total) * 100)) + "%"
      : "0%";
}

function filterTable() {
  const q = document.getElementById("searchInput")
    .value
    .toLowerCase();

  const statusFilter =
    document.getElementById("statusFilter").value;

  filtered = communications.filter((c) => {
    const searchMatch =
      c.type.toLowerCase().includes(q) ||
      c.serial.toLowerCase().includes(q) ||
      c.parNo.toLowerCase().includes(q) ||
      c.radioId.toLowerCase().includes(q) ||
      c.status.toLowerCase().includes(q) ||
      c.remarks.toLowerCase().includes(q);

    const statusMatch =
      !statusFilter ||
      c.status === statusFilter;

    return searchMatch && statusMatch;
  });

  currentPage = 1;

  renderTable();
  renderPagination();
}

function inputField(label, id, val = "", type = "text") {
  return `
    <div style="margin-bottom:10px">
      <label>${label}</label>

      <input
        id="${id}"
        type="${type}"
        value="${val}"
        style="
          width:100%;
          padding:7px;
          border:1px solid #ccc;
          border-radius:6px;
          margin-top:3px
        "
      />
    </div>
  `;
}

function selectField(label, id, options, selected = "") {
  return `
    <div style="margin-bottom:10px">
      <label>${label}</label>

      <select
        id="${id}"
        style="
          width:100%;
          padding:7px;
          border:1px solid #ccc;
          border-radius:6px;
          margin-top:3px
        "
      >
        ${options.map(option => `
          <option
            value="${option}"
            ${option === selected ? "selected" : ""}
          >
            ${option}
          </option>
        `).join("")}
      </select>
    </div>
  `;
}

function buildForm(c = {}) {
  return (
    inputField("Type", "c_type", c.type || "") +
    inputField("IMEI / Serial", "c_serial", c.serial || "") +
    inputField("Radio ID", "c_radioId", c.radioId || "") +
    selectField(
      "Status",
      "c_status",
      ["SERVICEABLE", "UNSERVICEABLE"],
      c.status || "SERVICEABLE"
    ) +
    selectField(
      "Remarks",
      "c_remarks",
      ["VALIDATED", "EXPIRED/FOR RENEWAL"],
      c.remarks || "VALIDATED"
    )
  );
}

function openActionModal(id) {
  editingId = id;

  const c = communications.find(x => x.id == id);

  document.getElementById("modalTitle").textContent =
    "Edit Record";

  document.getElementById("modalBody").innerHTML =
    buildForm(c);

  document.getElementById("modalSaveBtn").textContent =
    "Save";

  document
    .getElementById("modalOverlay")
    .classList.add("open");
}

function openAddModal() {
  editingId = null;

  document.getElementById("modalTitle").textContent =
    "Add Record";

  document.getElementById("modalBody").innerHTML =
    buildForm();

  document.getElementById("modalSaveBtn").textContent =
    "Add";

  document
    .getElementById("modalOverlay")
    .classList.add("open");
}

function closeModal() {
  document
    .getElementById("modalOverlay")
    .classList.remove("open");
}

async function saveRecord() {
  const type = getValue("c_type");
  const serial = getValue("c_serial");
  const radioId = getValue("c_radioId");
  const status = getValue("c_status");
  const remarks = getValue("c_remarks");

  if (!type || !serial) {
    alert("Type and IMEI / Serial are required.");
    return;
  }

  if (editingId) {
    const oldRecord = communications.find(c => c.id == editingId);

    const changes = [];

    if (oldRecord.type !== type) {
      changes.push(`Type changed from "${oldRecord.type}" to "${type}"`);
    }

    if (oldRecord.serial !== serial) {
      changes.push(`Serial changed from "${oldRecord.serial}" to "${serial}"`);
    }

    if (oldRecord.radioId !== radioId) {
      changes.push(`Radio ID changed from "${oldRecord.radioId}" to "${radioId}"`);
    }

    if (oldRecord.status !== status) {
      changes.push(`Status changed from "${oldRecord.status}" to "${status}"`);
    }

    if (oldRecord.remarks !== remarks) {
      changes.push(`Remarks changed from "${oldRecord.remarks}" to "${remarks}"`);
    }

    const { error } = await sb
      .from("communications_communication")
      .update({
        type: type,
        imei_serial: serial,
        radio_id: radioId,
        status: status,
        remarks: remarks,
      })
      .eq("asset_ptr_id", editingId);

    if (error) {
      console.error("UPDATE ERROR:", error);
      alert(error.message);
      return;
    }

    if (changes.length > 0) {
      await addActivityLog({
        communicationId: editingId,
        action: "Communication Updated",
        details: changes.join("; ")
      });
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
        radio_id: radioId,
        status: status,
        remarks: remarks,
        is_deleted: false,
      }]);

    if (childError) {
      console.error("CHILD SAVE ERROR:", childError);
      alert(childError.message);
      return;
    }

    await addActivityLog({
      communicationId: parentData.id,
      action: "Communication Created",
      details: `Added ${type} with Serial ${serial}`
    });
  }

  await fetchData();

  closeModal();
}

async function moveToBER(id) {
  const confirmed = confirm(
    "Move this communication asset to BER & Disposal?"
  );

  if (!confirmed) return;

  const c = communications.find(item => item.id == id);

  if (!c) {
    alert("Communication record not found.");
    return;
  }

  const { error: disposalError } = await sb
    .from("disposal_disposalitems")
    .insert([{
      asset_ptr_id: id,
      days_overdue: 0,
      expiry_date: todayDate(),
      disposal_reason: "Marked as BER from Communications",
      disposal_date: new Date().toISOString(),
      processed_by: null,
      personnel_assigned: null,
      last_sync: new Date().toISOString()
    }]);

  if (disposalError) {
    console.error("DISPOSAL INSERT ERROR:", disposalError);
    alert(disposalError.message);
    return;
  }

  // UPDATE COMMUNICATION TABLE
  const { error: commError } = await sb
    .from("communications_communication")
    .update({
      is_deleted: true,
      status: "UNSERVICEABLE"
    })
    .eq("asset_ptr_id", id);

  if (commError) {
    console.error("COMMUNICATION UPDATE ERROR:", commError);
    alert(commError.message);
    return;
  }

  // UPDATE ASSET STATUSID TO BER (4)
  const { error: assetError } = await sb
    .from("config_asset")
    .update({
      StatusID: 4
    })
    .eq("id", id);

  if (assetError) {
    console.error("ASSET STATUS UPDATE ERROR:", assetError);
    alert(assetError.message);
    return;
  }

  await addActivityLog({
    communicationId: id,
    action: "Moved to BER",
    details: `${c.type} with Serial ${c.serial} was moved to BER & Disposal`
  });

  await fetchData();
}

function exportCSV() {
  const headers = [
    "TYPE",
    "SERIAL NO.",
    "PAR NO.",
    "RADIO ID",
    "STATUS",
    "REMARKS"
  ];

  const rows = filtered.map((c) =>
    [
      c.type,
      c.serial,
      c.parNo,
      c.radioId,
      c.status,
      c.remarks
    ]
      .map((v) => `"${v || ""}"`)
      .join(",")
  );

  const csv =
    [headers.join(","), ...rows].join("\n");

  const a =
    document.createElement("a");

  a.href =
    "data:text/csv," +
    encodeURIComponent(csv);

  a.download =
    "communications_export.csv";

  a.click();
}

document.addEventListener(
  "DOMContentLoaded",
  () => {

    fetchData();

    document
      .getElementById("addRecordBtn")
      ?.addEventListener(
        "click",
        openAddModal
      );

    document
      .getElementById("modalSaveBtn")
      ?.addEventListener(
        "click",
        saveRecord
      );

    document
      .getElementById("closeModalBtn")
      ?.addEventListener(
        "click",
        closeModal
      );

    document
      .getElementById("closeModalBtn2")
      ?.addEventListener(
        "click",
        closeModal
      );
  }
);

window.openAddModal = openAddModal;
window.openActionModal = openActionModal;
window.closeModal = closeModal;
window.saveRecord = saveRecord;
window.moveToBER = moveToBER;
window.filterTable = filterTable;
window.exportCSV = exportCSV;