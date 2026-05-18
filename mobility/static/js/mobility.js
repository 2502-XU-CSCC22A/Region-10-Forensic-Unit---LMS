/* ---------------- MOBILITY STATS FROM DJANGO CONTEXT ---------------- */
function updateResponsiveBars() {

    const totalEl = document.getElementById('totalVehiclesCount');
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
        const totalBar = document.getElementById('totalVehiclesBar');
        if (totalBar) totalBar.style.width = '100%';
  
        animateBar('serviceableVehiclesCount', 'serviceableVehiclesBar');
        animateBar('validatedParCount', 'validatedParBar');
        animateBar('expiringParCount', 'expiringParBar');
    });
  }
  
  document.addEventListener("DOMContentLoaded", () => {
    updateResponsiveBars();
  });