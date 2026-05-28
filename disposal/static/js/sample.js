/* ---------------- SAFE SUPABASE INIT ---------------- */
// Added a fallback check to prevent crashing if the CDN isn't loaded yet
const supabaseUrl = "https://vamjajitzyspdyfxisac.supabase.co";
const supabaseKey = "sb_publishable_mTj-PK3WV3ZPqGOii548Ng_EXvssL54";

/* ---------------- STATE ---------------- */
let disposal = [];
let filtered = [];

/* ---------------- FETCH DATA ---------------- */
async function fetchData() {
    if (!sb) {
        console.error("Supabase client is not initialized.");
        return;
    }

    const { data, error } = await sb
        .from("disposal_disposalitems")
        .select("*")
        .order("asset_ptr_id", { ascending: false });

    if (error) {
        console.error("FETCH ERROR:", error);
        alert("Failed to load disposal.");
        return;
    }

    // FIX: Make sure to map 'category' or the field containing your category names!
    // Also fixed the typo from 'action_typetype' to 'action_type' if applicable
    disposal = data
        .map((item) => ({
            id: item.asset_ptr_id,
            action_type: item.action_type || item.action_typetype || "",
            category: item.category || "", // <-- CRITICAL: This must exist to filter later
        }))
        .filter((item) => item.id > 0);

    filtered = [...disposal];
    updateStats();
}

/* ---------------- STATS FROM DJANGO CONTEXT ---------------- */
function updateResponsiveBars() {

  const totalEl = document.getElementById('totalBerCount');
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
      const totalBar = document.getElementById('totalBerBar');
      if (totalBar) totalBar.style.width = '100%';

      animateBar('firearmsBerCount', 'firearmsBerBar');
      animateBar('mobilityBerCount', 'mobilityBerBar');
      animateBar('commsBerCount', 'commsBerBar');
      animateBar('investBerCount', 'investBerBar');
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
      }, 350); 
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