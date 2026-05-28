// ── Dashboard interactions

document.addEventListener("DOMContentLoaded", function () {
  const readAllBtn = document.getElementById("read-all-btn");
  if (readAllBtn) {
    readAllBtn.addEventListener("click", function () {
      // Get CSRF token from cookie
      function getCookie(name) {
        var v = document.cookie.match("(^|;) ?" + name + "=([^;]*)(;|$)");
        return v ? decodeURIComponent(v[2]) : null;
      }

      fetch("/dashboard/mark-all-read/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json",
        },
      })
        .then(function (res) {
          return res.json();
        })
        .then(function (data) {
          if (data.status === "ok") {
            document
              .querySelectorAll("#widget-notifications .dot")
              .forEach(function (dot) {
                dot.remove();
              });
            const badge = document.getElementById("notif-badge");
            if (badge) {
              badge.textContent = "0";
              badge.style.background = "#94a3b8";
            }
          }
        })
        .catch(function (err) {
          console.error("mark-all-read failed:", err);
        });
    });
  }

  const PREVIEW_COUNT = 5;

  document.querySelectorAll(".view-all").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const target = btn.getAttribute("data-target");
      const list = document.getElementById("list-" + target);
      if (!list) return;

      const items = list.querySelectorAll(".activity-item");
      const expanded = btn.getAttribute("data-expanded") === "true";

      if (expanded) {
        items.forEach(function (item, i) {
          item.style.display = i < PREVIEW_COUNT ? "" : "none";
        });
        btn.textContent = "View all";
        btn.setAttribute("data-expanded", "false");
      } else {
        items.forEach(function (item) {
          item.style.display = "";
        });
        btn.textContent = "Show less";
        btn.setAttribute("data-expanded", "true");
      }
    });

    const target = btn.getAttribute("data-target");
    const list = document.getElementById("list-" + target);
    if (list) {
      const items = list.querySelectorAll(".activity-item");
      items.forEach(function (item, i) {
        if (i >= PREVIEW_COUNT) item.style.display = "none";
      });
      btn.setAttribute("data-expanded", "false");
    }
  });

  document.querySelectorAll(".js-refresh").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const icon = btn.querySelector("i");
      if (icon) {
        icon.style.transition = "transform 0.5s";
        icon.style.transform = "rotate(360deg)";
        setTimeout(function () {
          icon.style.transform = "";
        }, 500);
      }
      window.location.reload();
    });
  });

  document.querySelectorAll(".js-filter").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const target = btn.getAttribute("data-target");
      alert('Filter for "' + target + '" coming soon.');
    });
  });

  document.querySelectorAll(".js-export").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const target = btn.getAttribute("data-target");
      const list = document.getElementById("list-" + target);
      if (!list) return;

      const rows = [["Actor", "Action", "Item", "Timestamp"]];
      list.querySelectorAll(".activity-item").forEach(function (item) {
        const text = item.querySelector(".activity-text");
        const meta = item.querySelector(".activity-meta");
        const strongs = text ? text.querySelectorAll("strong") : [];
        const actor = strongs[0] ? strongs[0].textContent.trim() : "";
        const itemLabel = strongs[1] ? strongs[1].textContent.trim() : "";
        const actionRaw = text
          ? text.textContent.replace(actor, "").replace(itemLabel, "").trim()
          : "";
        const timestamp = meta ? meta.textContent.trim() : "";
        rows.push([actor, actionRaw, itemLabel, timestamp]);
      });

      const csv = rows
        .map(function (r) {
          return r
            .map(function (c) {
              return '"' + c.replace(/"/g, '""') + '"';
            })
            .join(",");
        })
        .join("\n");

      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = target + "_export.csv";
      a.click();
      URL.revokeObjectURL(url);
    });
  });
});

/* ---------------- STATS FROM DJANGO CONTEXT ---------------- */
function updateResponsiveBars() {

  const totalEl = document.getElementById('totalAssetCount');
  const total = totalEl ? parseInt(totalEl.textContent, 10) || 0 : 0;

  const calculatePct = (count) => {
      if (total === 0) return '0%';
      return Math.max(4, Math.round((count / total) * 100)) + '%';
  };

  const animateBar = (countId, barId) => {
      const countEl = document.getElementById(countId);
      const barEl = document.getElementById(barId);
      
      if (countEl && barEl) {
          const countValue = parseInt(countEl.textContent, 10) || 0;
          barEl.style.width = calculatePct(countValue);
      }
  };

  requestAnimationFrame(() => {
      const totalBar = document.getElementById('totalAssetBar');
      if (totalBar) totalBar.style.width = '100%';

      animateBar('firearmsCount', 'firearmsBar');
      animateBar('mobilityCount', 'mobilityBar');
      animateBar('commsCount', 'commsBar');
      animateBar('investCount', 'investBar');
  });
}

document.addEventListener("DOMContentLoaded", () => {
  updateResponsiveBars();
});


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

document.addEventListener("DOMContentLoaded", function () {
  // State Tracking variables 
  let currentPage = 1;
  const dateInput = document.getElementById("modal-filter-date");
  const roleSelect = document.getElementById("modal-filter-role");
  const resetButton = document.getElementById("modal-filter-reset");
  const container = document.getElementById("modal-activities-container");
  
  const prevBtn = document.getElementById("modal-btn-prev");
  const nextBtn = document.getElementById("modal-btn-next");
  const pagInfo = document.getElementById("modal-pagination-info");

  // Endpoint Configuration Target URL 
  const apiEndpoint = window.RECENT_ACTIVITIES_API_URL || "/dashboard/api/recent-activities/";

  function fetchModalActivities(page = 1) {
      currentPage = page;
      
      // Form URL tracking query parameters 
      let url = `${apiEndpoint}?page=${page}`;
      if (dateInput.value) url += `&date=${dateInput.value}`;
      if (roleSelect.value) url += `&role=${encodeURIComponent(roleSelect.value)}`;

      // Render Loading Indicator
      container.innerHTML = `<div class="text-center my-4 text-muted"><i class="fas fa-spinner fa-spin mr-2"></i>Loading history logs...</div>`;

      fetch(url)
          .then(response => response.json())
          .then(data => {
              renderLogs(data.results);
              setupPaginationControls(data);
          })
          .catch(err => {
              console.error("Error loading activity updates:", err);
              container.innerHTML = `<p class="text-center text-danger my-3">Failed to load access logs history data records.</p>`;
          });
  }

  function renderLogs(logs) {
      if (!logs || logs.length === 0) {
          container.innerHTML = `<p class="text-center text-muted my-4">No matching access logs matching your selection parameters.</p>`;
          return;
      }

      container.innerHTML = logs.map(act => {
          const iconClass = act.is_logout ? "fa-sign-out-alt text-danger" : "fa-sign-in-alt text-success";
          return `
              <div class="activity-item d-flex align-items-start border-bottom py-2 my-1">
                  <div class="av-sm mr-3 bg-light rounded-circle p-2 text-center" style="width: 38px; height: 38px;">
                      <i class="fas ${iconClass}"></i>
                  </div>
                  <div class="activity-body flex-grow-1">
                      <div class="activity-text text-dark" style="font-size: 0.9rem;">
                          <strong>${act.actor}</strong> successfully <strong>${act.action}</strong>
                      </div>
                      <div class="activity-meta text-muted small mt-1">${act.timestamp}</div>
                  </div>
              </div>
          `;
      }).join("");
  }

  function setupPaginationControls(meta) {
      pagInfo.textContent = `Showing page ${meta.number} of ${meta.num_pages || 1}`;

      // Previous Page Button Management
      if (meta.has_previous) {
          prevBtn.classList.remove("disabled");
          prevBtn.onclick = (e) => { e.preventDefault(); fetchModalActivities(meta.number - 1); };
      } else {
          prevBtn.classList.add("disabled");
          prevBtn.onclick = null;
      }

      // Next Page Button Management
      if (meta.has_next) {
          nextBtn.classList.remove("disabled");
          nextBtn.onclick = (e) => { e.preventDefault(); fetchModalActivities(meta.number + 1); };
      } else {
          nextBtn.classList.add("disabled");
          nextBtn.onclick = null;
      }
  }

  // --- Dynamic Filters Listeners ---
  dateInput.addEventListener("change", () => fetchModalActivities(1));
  roleSelect.addEventListener("change", () => fetchModalActivities(1));
  
  resetButton.addEventListener("click", () => {
      dateInput.value = "";
      roleSelect.value = "";
      fetchModalActivities(1);
  });

  // Trigger loading logic immediately upon showing the view-all modal interface
  document.getElementById("open-recent-modal-btn").addEventListener("click", function() {
      fetchModalActivities(1);
  });
});

// --- ASSETS MODAL MANAGER SYSTEM ---
const assetEndpoint = window.ASSET_ACTIVITIES_API_URL || "/dashboard/api/assets-log/";
const aDate = document.getElementById("asset-filter-date");
const aAction = document.getElementById("asset-filter-action");
const aRole = document.getElementById("asset-filter-role");
const aContainer = document.getElementById("asset-activities-container");

function fetchAssetActivities(page = 1) {
    let url = `${assetEndpoint}?page=${page}`;
    if (aDate.value) url += `&date=${aDate.value}`;
    if (aAction.value) url += `&action=${encodeURIComponent(aAction.value)}`;
    if (aRole.value) url += `&role=${encodeURIComponent(aRole.value)}`;

    aContainer.innerHTML = `<div class="text-center my-3 text-muted"><i class="fas fa-spinner fa-spin mr-2"></i>Parsing status logs...</div>`;
    fetch(url).then(res => res.json()).then(data => {
        if(!data.results.length) {
            aContainer.innerHTML = `<p class="text-center text-muted my-3">No matching modification footprints found.</p>`;
            return;
        }
        aContainer.innerHTML = data.results.map(act => `
            <div class="activity-item d-flex border-bottom py-2">
                <div class="av-sm mr-3 bg-light rounded p-2 text-info"><i class="fas fa-pen-nib"></i></div>
                <div>
                    <div class="text-dark"><strong>${act.actor}</strong> explicitly <strong>${act.action}</strong> asset item: <strong>${act.item}</strong></div>
                    <div class="small text-muted mt-1">${act.timestamp}</div>
                </div>
            </div>
        `).join("");
        handleModalPagination(data, "asset", fetchAssetActivities);
    });
}
document.getElementById("open-assets-modal-btn").addEventListener("click", () => fetchAssetActivities(1));
aDate.addEventListener("change", () => fetchAssetActivities(1));
aAction.addEventListener("change", () => fetchAssetActivities(1));
aRole.addEventListener("change", () => fetchAssetActivities(1));


// --- NOTIFICATIONS EXPIRY MODAL SYSTEM ---
const notifEndpoint = window.NOTIFICATIONS_API_URL || "/dashboard/api/notifications-log/";
const nCategory = document.getElementById("notif-filter-category");
const nContainer = document.getElementById("notif-activities-container");

function fetchNotificationsHistory(page = 1) {
    let url = `${notifEndpoint}?page=${page}`;
    if (nCategory.value) url += `&category=${nCategory.value}`;

    nContainer.innerHTML = `<div class="text-center my-3 text-muted"><i class="fas fa-spinner fa-spin mr-2"></i>Checking lifecycle logs...</div>`;
    fetch(url).then(res => res.json()).then(data => {
        if(!data.results.length) {
            nContainer.innerHTML = `<p class="text-center text-muted my-3">No immediate asset expirations discovered inside this category segment.</p>`;
            return;
        }
        nContainer.innerHTML = data.results.map(alert => `
            <div class="activity-item d-flex border-bottom py-2 bg-light-red mb-1 rounded p-2">
                <div class="av-sm mr-3 text-danger pt-1"><i class="fas fa-exclamation-triangle"></i></div>
                <div>
                    <div class="text-dark">[<strong>${alert.category}</strong>] Asset: <strong>${alert.asset_name}</strong> (S/N: ${alert.serial_number}) has an active tracking structure nearing expiry.</div>
                    <div class="small text-danger font-weight-bold mt-1">Expires on: ${alert.expiry_date}</div>
                </div>
            </div>
        `).join("");
        handleModalPagination(data, "notif", fetchNotificationsHistory);
    });
}
document.getElementById("open-notifications-modal-btn").addEventListener("click", () => fetchNotificationsHistory(1));
nCategory.addEventListener("change", () => fetchNotificationsHistory(1));


// Generic Modal Pagination Helper Component
function handleModalPagination(meta, prefix, callback) {
    document.getElementById(`${prefix}-pagination-info`).textContent = `Showing page ${meta.number} of ${meta.num_pages || 1}`;
    const prev = document.getElementById(`${prefix}-btn-prev`);
    const next = document.getElementById(`${prefix}-btn-next`);
    
    if (meta.has_previous) {
        prev.classList.remove("disabled"); prev.onclick = (e) => { e.preventDefault(); callback(meta.number - 1); };
    } else { prev.classList.add("disabled"); prev.onclick = null; }

    if (meta.has_next) {
        next.classList.remove("disabled"); next.onclick = (e) => { e.preventDefault(); callback(meta.number + 1); };
    } else { next.classList.add("disabled"); next.onclick = null; }
}