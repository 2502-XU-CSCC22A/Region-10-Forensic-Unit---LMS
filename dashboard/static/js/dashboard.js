// ── Dashboard interactions ────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function () {

    // Mark all notifications read on button click
    const readBtn = document.querySelector('.read-btn');
    if (readBtn) {
      readBtn.addEventListener('click', function () {
        document.querySelectorAll('.dot').forEach(d => d.style.opacity = '0');
        const badge = document.querySelector('.notif-count');
        if (badge) badge.textContent = '0';
      });
    }
  
    // View-all placeholders
    document.querySelectorAll('.view-all').forEach(btn => {
      btn.addEventListener('click', function () {
        alert('Full list coming soon.');
      });
    });
  
  });