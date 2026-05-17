let sb;

let selectedBERId = null;

function initSupabase() {
  if (!window.supabase) {
    console.error("Supabase JS library not loaded!");
    return null;
  }

  try {
    if (!window.supabaseClient) {
      window.supabaseClient = window.supabase.createClient(
        "https://vamjajitzyspdyfxisac.supabase.co",
        "sb_publishable_mTj-PK3WV3ZPqGOii548Ng_EXvssL54",
      );
    }

    sb = window.supabaseClient;

    console.log("✅ Supabase initialized successfully");

    return sb;
  } catch (e) {
    console.error("❌ Supabase init failed:", e);
    return null;
  }
}

initSupabase();

function todayDate() {
  return new Date().toISOString().split("T")[0];
}

/* =========================================
   MODALS
========================================= */

function toggleModal(id) {
  const modal = document.getElementById(id);

  if (!modal) return;

  modal.classList.toggle("active");

  if (id === "addModal" && modal.classList.contains("active")) {
    setTimeout(populateSubcategories, 100);
  }
}

function prepareRemoval(id) {
  selectedBERId = Number(id);

  const modal = document.getElementById("confirmationModal");

  if (modal) {
    modal.classList.add("active");
  }
}

function closeConfirmationModal() {
  selectedBERId = null;

  const modal = document.getElementById("confirmationModal");

  if (modal) {
    modal.classList.remove("active");
  }
}

async function confirmBerRemoval() {
  if (!selectedBERId) {
    alert("No asset selected.");
    return;
  }

  await moveToBER(selectedBERId);
}

/* =========================================
   SUBCATEGORIES
========================================= */

function populateSubcategories() {
  const subSelect = document.getElementById("subcategorySelect");

  if (!subSelect) return;

  subSelect.innerHTML = '<option value="">Select Subcategory...</option>';

  const technicalSubcategories = [
    "SOCO",
    "DNA",
    "PHOTO",
    "FINGERPRINT (FP)",
    "FIREARMS",
    "CHEMISTRY",
    "MEDICO-LEGAL",
    "Questioned Document",
    "POLYGRAPH",
    "Physical Identification (PI)",
  ];

  technicalSubcategories.forEach((item) => {
    const el = document.createElement("option");

    el.textContent = item;
    el.value = item;

    subSelect.appendChild(el);
  });
}

/* =========================================
   ACTIVITY LOGS
========================================= */

async function addInvestigativeActivityLog({ assetId, action, details }) {
  if (!sb) return;

  const { error } = await sb.from("Investigative_Activity_Log").insert([
    {
      asset_ptr_id: assetId,
      action: action,
      details: details,
    },
  ]);

  if (error) {
    console.error("INVESTIGATIVE ACTIVITY LOG ERROR:", error);
  }
}

/* =========================================
   MOVE TO BER
========================================= */

async function moveToBER(id) {
  id = Number(id);

  if (!sb) {
    alert("Supabase not initialized. Please refresh the page.");
    return;
  }

  try {
    const now = new Date().toISOString();

    /* =========================
       CHECK EXISTING DISPOSAL
    ========================= */

    const { data: existingDisposal, error: checkError } = await sb
      .from("disposal_disposalitems")
      .select("asset_ptr_id")
      .eq("asset_ptr_id", id)
      .maybeSingle();

    if (checkError) {
      console.error("DISPOSAL CHECK ERROR:", checkError);
      alert(checkError.message);
      return;
    }

    /* =========================
       INSERT DISPOSAL RECORD
    ========================= */

    if (!existingDisposal) {
      const { error: disposalError } = await sb
        .from("disposal_disposalitems")
        .insert([
          {
            asset_ptr_id: id,
            days_overdue: 0,
            expiry_date: todayDate(),
            disposal_reason: "Marked as BER from Investigative Equipment",
            disposal_date: now,
            processed_by: null,
            personnel_assigned: null,
            last_sync: now,
          },
        ]);

      if (disposalError) {
        console.error("DISPOSAL INSERT ERROR:", disposalError);

        alert(disposalError.message);
        return;
      }
    }

    /* =========================
       UPDATE ASSET STATUS
    ========================= */

    const { error: assetError } = await sb
      .from("config_asset")
      .update({
        StatusID: 4,
      })
      .eq("id", id);

    if (assetError) {
      console.error("ASSET STATUS UPDATE ERROR:", assetError);

      alert(assetError.message);
      return;
    }

    /* =========================
       DELETE PAR RECORDS
    ========================= */

    const { data: deletedPAR, error: parDeleteError } = await sb
      .from("Investigative_PAR_Record")
      .delete()
      .eq("asset_id", id)
      .select();

    console.log("PAR DELETED:", deletedPAR);

    if (parDeleteError) {
      console.error("PAR DELETE ERROR:", parDeleteError);

      alert(parDeleteError.message);
      return;
    }

    /* =========================
       DELETE ICS RECORDS
    ========================= */

    const { data: deletedICS, error: icsDeleteError } = await sb
      .from("Investigative_ICS_Record")
      .delete()
      .eq("asset_id", id)
      .select();

    console.log("ICS DELETED:", deletedICS);

    if (icsDeleteError) {
      console.error("ICS DELETE ERROR:", icsDeleteError);

      alert(icsDeleteError.message);
      return;
    }

    /* =========================
       ACTIVITY LOG DETAILS
    ========================= */

    const hasDeletedPAR = deletedPAR && deletedPAR.length > 0;

    const hasDeletedICS = deletedICS && deletedICS.length > 0;

    let logDetails = `Investigative Asset ID ${id} has been moved to BER`;

    if (hasDeletedPAR && hasDeletedICS) {
      logDetails += ", and PAR and ICS Records are deleted";
    } else if (hasDeletedPAR) {
      logDetails += ", and PAR Record is deleted";
    } else if (hasDeletedICS) {
      logDetails += ", and ICS Record is deleted";
    }

    await addInvestigativeActivityLog({
      assetId: id,
      action: "Moved to BER",
      details: logDetails,
    });

    closeConfirmationModal();

    alert("✅ Successfully moved to BER!");

    window.location.reload();
  } catch (err) {
    console.error(err);

    alert("Failed to move to BER:\n" + err.message);
  }
}

/* =========================================
   AUTO DISMISS ALERTS
========================================= */

function autoDismissMessages() {
  const messages = document.querySelectorAll(".messages .alert");

  messages.forEach((msg) => {
    if (!msg.querySelector(".close-btn")) {
      const closeBtn = document.createElement("span");

      closeBtn.className = "close-btn";
      closeBtn.innerHTML = "&times;";

      closeBtn.style.cssText =
        "float: right; font-size: 20px; cursor: pointer; margin-left: 15px;";

      closeBtn.onclick = () => msg.remove();

      msg.appendChild(closeBtn);
    }

    setTimeout(() => {
      if (msg && msg.parentNode) {
        msg.style.transition = "opacity 0.5s ease";
        msg.style.opacity = "0";

        setTimeout(() => {
          if (msg && msg.parentNode) {
            msg.remove();
          }
        }, 500);
      }
    }, 5000);
  });
}

/* =========================================
   UPDATE MODAL
========================================= */

function openUpdateModal(id, name, propertyId, category, quantity) {
  console.log("Opening edit modal for ID:", id);

  const updateAssetId = document.getElementById("updateAssetId");

  const updateItemName = document.getElementById("updateItemName");

  const updateQuantity = document.getElementById("updateQuantity");

  if (updateAssetId) updateAssetId.value = id;

  if (updateItemName) updateItemName.value = name || "";

  if (updateQuantity) updateQuantity.value = quantity || 1;

  toggleModal("updateModal");
}

/* =========================================
   DOM LOADED
========================================= */

document.addEventListener("DOMContentLoaded", function () {
  populateSubcategories();

  autoDismissMessages();

  const addForm = document.querySelector("#addModal form");

  if (addForm) {
    addForm.addEventListener("submit", function (e) {
      const propertyInput = document.querySelector("input[name='par_id']");

      const propertyId = propertyInput ? propertyInput.value.trim() : "";

      if (!propertyId) {
        alert("Property ID is required!");

        e.preventDefault();
      }
    });
  }

  /* =========================
       CONFIRM BER FORM
    ========================= */

  const confirmForm = document.getElementById("confirmRemovalForm");

  if (confirmForm) {
    confirmForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      if (!selectedBERId) {
        alert("No asset selected.");
        return;
      }

      await moveToBER(selectedBERId);
    });
  }

  const observer = new MutationObserver(autoDismissMessages);

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
});

/* =========================================
   CLICK OUTSIDE MODAL
========================================= */

window.onclick = function (event) {
  const confirmationModal = document.getElementById("confirmationModal");

  if (event.target === confirmationModal) {
    closeConfirmationModal();
  }
};

/* =========================================
   GLOBAL FUNCTIONS
========================================= */

window.toggleModal = toggleModal;
window.openUpdateModal = openUpdateModal;
window.moveToBER = moveToBER;
window.prepareRemoval = prepareRemoval;
window.confirmBerRemoval = confirmBerRemoval;
window.closeConfirmationModal = closeConfirmationModal;
window.populateSubcategories = populateSubcategories;
