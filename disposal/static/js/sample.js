/* ---------------- SAFE SUPABASE INIT ---------------- */
// Added a fallback check to prevent crashing if the CDN isn't loaded yet
const supabaseUrl = "https://vamjajitzyspdyfxisac.supabase.co";
const supabaseKey = "sb_publishable_mTj-PK3WV3ZPqGOii548Ng_EXvssL54";

let sb = null;
if (window.supabaseClient) {
    sb = window.supabaseClient;
} else if (window.supabase && typeof window.supabase.createClient === 'function') {
    window.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);
    sb = window.supabaseClient;
} else {
    console.warn("Supabase CDN not detected yet. Retrying configuration...");
}

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