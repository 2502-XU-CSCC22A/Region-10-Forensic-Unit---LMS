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
      created_at: new Date().toISOString(),
    },
  ]);

  if (error) {
    console.error("INVESTIGATIVE ACTIVITY LOG ERROR:", error);
    alert("Activity log failed: " + error.message);
    throw error;
  }
}

/* =========================================
   MOVE TO BER
========================================= */

async function confirmBerRemoval() {
  if (!selectedBERId) {
    alert("No asset selected.");
    return;
  }

  await moveToBER(selectedBERId);
}

async function moveToBER(id) {
  id = Number(id);

  if (!sb) {
    alert("Supabase not initialized. Please refresh the page.");
    return;
  }

  try {
    const now = new Date().toISOString();

    const { error: disposalError } = await sb
      .from("disposal_disposalitems")
      .upsert(
        [
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
        ],
        {
          onConflict: "asset_ptr_id",
        },
      );

    if (disposalError) {
      console.error("DISPOSAL UPSERT ERROR:", disposalError);
      alert(disposalError.message);
      return;
    }

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

    const { data: deletedPAR, error: parDeleteError } = await sb
      .from("Investigative_PAR_Record")
      .delete()
      .eq("asset_id", id)
      .select();

    if (parDeleteError) {
      console.error("PAR DELETE ERROR:", parDeleteError);
      alert(parDeleteError.message);
      return;
    }

    const { data: deletedICS, error: icsDeleteError } = await sb
      .from("Investigative_ICS_Record")
      .delete()
      .eq("asset_id", id)
      .select();

    if (icsDeleteError) {
      console.error("ICS DELETE ERROR:", icsDeleteError);
      alert(icsDeleteError.message);
      return;
    }

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

    const { error: detailsDeleteError } = await sb
      .from("Investigative_Details")
      .delete()
      .eq("asset_ptr_id", id);

    if (detailsDeleteError) {
      console.error("INVESTIGATIVE DETAILS DELETE ERROR:", detailsDeleteError);
      alert(detailsDeleteError.message);
      return;
    }

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

  const confirmForm = document.getElementById("confirmRemovalForm");

  if (confirmForm) {
    confirmForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      await confirmBerRemoval();
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


(function () {
  const cssStyles = `
    /* Full-screen backdrop wrapper */
    .loading-screen-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: #f1f5f9; /* Matches dashboard backdrop light canvas */
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 99999; /* Forces layer over all sidebars, navbars, and modulations */
      transition: opacity 0.3s ease, visibility 0.3s ease;
      opacity: 1;
      visibility: visible;
    }

    /* Dismissed hidden state class wrapper */
    .loading-screen-overlay.fade-out {
      opacity: 0;
      visibility: hidden;
    }

    /* Central Layout Container */
    .loading-container {
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      max-width: 450px;
      padding: 20px;
      font-family: 'Inter', sans-serif;
    }

    /* Brand Logo styling */
    .loading-container .logo {
      width: 100px;
      height: auto;
      margin-bottom: 20px;
      filter: drop-shadow(0 4px 10px rgba(13, 33, 85, 0.15));
    }

    /* Core System Title Header */
    .loading-container .title {
      font-size: 28px;
      font-weight: 800;
      color: #1a2b6d; /* Exact theme navy color */
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    /* Unit Subtitles description metadata */
    .loading-container .subtitle {
      font-size: 12px;
      font-weight: 600;
      color: #64748b; /* Slate gray styling */
      text-transform: uppercase;
      line-height: 1.5;
      letter-spacing: 0.5px;
      margin-bottom: 30px;
    }

    /* Infinite progress bar frame track */
    .loading-container .progress-container {
      width: 220px;
      height: 5px;
      background-color: #e2e8f0;
      border-radius: 10px;
      overflow: hidden;
      margin-bottom: 15px;
    }

    /* Moving progress bar component track */
    .loading-container .progress-bar {
      width: 50%;
      height: 100%;
      background-color: #1a2b6d; /* Accent primary navy */
      border-radius: 10px;
      animation: progressMove 1.4s ease-in-out infinite;
    }

    /* Loading Context Subtexts */
    .loading-container .loading-text {
      font-size: 13px;
      font-weight: 500;
      color: #475569;
      margin-bottom: 25px;
    }

    /* System Taglines elements indicators */
    .loading-container .tagline {
      font-size: 12px;
      font-weight: 700;
      color: #1a2b6d;
      background: #e2e8f0;
      padding: 6px 14px;
      border-radius: 20px;
      letter-spacing: 0.5px;
    }

    /* Smooth Progress Bar Loop Keyframe */
    @keyframes progressMove {
      0% { transform: translateX(-100%); }
      50% { transform: translateX(100%); }
      100% { transform: translateX(200%); }
    }
  `;

  const styleSheet = document.createElement("style");
  styleSheet.innerText = cssStyles;
  document.head.appendChild(styleSheet);

  const htmlContent = `
    <div class="loading-container">
      <img src="/static/img/RFU10%20Logo.png" alt="PNP Logo" class="logo" onerror="this.src='/static/firearms/img/RFU10%20Logo.png'">
      <div class="title">RFU10-LMS</div>
      <div class="subtitle">
        PNP REGION 10 FORENSIC UNIT <br>
        LOGISTICS MANAGEMENT SYSTEM
      </div>
      <div class="progress-container">
        <div class="progress-bar"></div>
      </div>
      <div class="loading-text">Initializing Logistics Management System...</div>
      <div class="tagline">🔒 Secure. Monitor. Manage.</div>
    </div>
  `;

  const overlayElement = document.createElement("div");
  overlayElement.id = "globalSystemPageLoader";
  overlayElement.className = "loading-screen-overlay";
  overlayElement.innerHTML = htmlContent;

  if (document.body) {
    document.body.insertBefore(overlayElement, document.body.firstChild);
  } else {
    document.addEventListener("DOMContentLoaded", () => {
      document.body.insertBefore(overlayElement, document.body.firstChild);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
      overlayElement.classList.add("fade-out");
    }, 250); 
  });

  document.addEventListener("click", (event) => {
    const anchor = event.target.closest("a");

    if (anchor) {
      const href = anchor.getAttribute("href");
      const target = anchor.getAttribute("target");

      if (
        !href || 
        href.startsWith("#") || 
        href.startsWith("javascript:") || 
        target === "_blank" || 
        event.ctrlKey || 
        event.metaKey
      ) {
        return;
      }

      overlayElement.classList.remove("fade-out");
    }
  });

  document.addEventListener("submit", (event) => {

    if (event.target.checkValidity && !event.target.checkValidity()) {
      return;
    }
    overlayElement.classList.remove("fade-out");
  });

  window.addEventListener("pageshow", (event) => {
    if (event.persisted) {
      overlayElement.classList.add("fade-out");
    }
  });
})();

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
