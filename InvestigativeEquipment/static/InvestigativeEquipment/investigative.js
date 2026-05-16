// ==================== FIXED VERSION ====================
let sb;

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

document.addEventListener("DOMContentLoaded", function () {
  populateSubcategories();
});

function toggleModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;

  modal.classList.toggle("active");

  if (id === "addModal" && modal.classList.contains("active")) {
    setTimeout(populateSubcategories, 100);
  }
}

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
    let el = document.createElement("option");
    el.textContent = item;
    el.value = item;
    subSelect.appendChild(el);
  });
}

async function moveToBER(id) {
  id = Number(id);

  if (!confirm("Move this investigative asset to BER & Disposal?")) {
    return;
  }

  if (!sb) {
    alert("Supabase not initialized. Please refresh the page.");
    return;
  }

  try {
    const now = new Date().toISOString();

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

    alert("✅ Successfully moved to BER!");

    window.location.reload();
  } catch (err) {
    console.error(err);
    alert("Failed to move to BER:\n" + err.message);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const addForm = document.querySelector("#addModal form");
  if (addForm) {
    addForm.addEventListener("submit", function (e) {
      const propertyId = document
        .querySelector("input[name='par_id']")
        .value.trim();
      if (!propertyId) {
        alert("Property ID is required!");
        e.preventDefault();
      }
    });
  }
});

function autoDismissMessages() {
  const messages = document.querySelectorAll(".messages .alert");
  messages.forEach((msg, index) => {
    // Add close button (optional but nice)
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
          if (msg && msg.parentNode) msg.remove();
        }, 500);
      }
    }, 5000); // 5 seconds
  });
}

document.addEventListener("DOMContentLoaded", function () {
  populateSubcategories();
  autoDismissMessages();

  const observer = new MutationObserver(autoDismissMessages);
  observer.observe(document.body, { childList: true, subtree: true });
});

function openUpdateModal(id, name, propertyId, category, quantity) {
  console.log("Opening edit modal for ID:", id); // Debug

  document.getElementById("updateAssetId").value = id;
  document.getElementById("updateItemName").value = name || "";
  document.getElementById("updateQuantity").value = quantity || 1;

  toggleModal("updateModal");
}