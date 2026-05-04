/* ---------------- SAFE SUPABASE INIT ---------------- */
window.supabaseClient = window.supabaseClient || window.supabase.createClient(
  "https://vamjajitzyspdyfxisac.supabase.co",
  "sb_publishable_mTj-PK3WV3ZPqGOii548Ng_EXvssL54"
);

const sb = window.supabaseClient;

/* ---------------- STATE ---------------- */
let disposal = [];
let filtered = [];
let currentPage = 1;
const pageSize = 5;
let editingId = null;

/* ---------------- FETCH DATA ---------------- */
async function fetchData() {
  const { data, error } = await sb
    .from("disposal_disposalitems")
    .select("*")
    .order("asset_ptr_id", { ascending: false });

  if (error) {
    console.error("FETCH ERROR:", error);
    alert("Failed to load disposal.");
    return;
  }

  disposal = data
    .map((item) => ({
      id: item.asset_ptr_id,
      action_type: item.action_typetype || "",
    }))
    .filter((item) => item.id > 0);

  filtered = [...disposal];

  updateStats();
}

/* ---------------- STATS ---------------- */
function updateStats() {
  const total = disposal.length;
  
  // Filtering based on the mapped category name (e.g., from your config_category table)
  const firearms = disposal.filter(i => (i.category || '').toLowerCase().includes('firearm')).length;
  const mobility = disposal.filter(i => (i.category || '').toLowerCase().includes('mobility')).length;
  const comms    = disposal.filter(i => (i.category || '').toLowerCase().includes('communication')).length;
  const invest   = disposal.filter(i => (i.category || '').toLowerCase().includes('investigative')).length;

  const pct = v => Math.max(4, Math.round((v / (total || 1)) * 100)) + '%';
  
  // Text Counters
  document.getElementById('totalBerCount').textContent    = total;
  document.getElementById('firearmsBerCount').textContent = firearms;
  document.getElementById('mobilityBerCount').textContent = mobility;
  document.getElementById('commsBerCount').textContent    = comms;
  document.getElementById('investBerCount').textContent   = invest;

  // Animate Bars
  setTimeout(() => {
    if(document.getElementById('totalBerBar'))    document.getElementById('totalBerBar').style.width = '100%';
    if(document.getElementById('firearmsBerBar')) document.getElementById('firearmsBerBar').style.width = pct(firearms);
    if(document.getElementById('mobilityBerBar')) document.getElementById('mobilityBerBar').style.width = pct(mobility);
    if(document.getElementById('commsBerBar'))    document.getElementById('commsBerBar').style.width = pct(comms);
    if(document.getElementById('investBerBar'))   document.getElementById('investBerBar').style.width = pct(invest);
  }, 100);
}