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