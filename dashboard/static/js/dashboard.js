// ── Dashboard interactions ────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function () {

  const readBtn = document.querySelector('.read-btn');
  if (readBtn) {
    readBtn.addEventListener('click', function () {
      document.querySelectorAll('.dot').forEach(d => d.style.opacity = '0');
      const badge = document.querySelector('.notif-count');
      if (badge) badge.textContent = '0';
    });
  }

  document.querySelectorAll('.view-all').forEach(btn => {
    btn.addEventListener('click', function () {
      alert('Full list coming soon.');
    });
  });

});