function updateDisposalStats(allBerItems) {
  // 1. Calculate Counts
  const totalBer      = allBerItems.length;
  const berFirearms   = allBerItems.filter(i => i.category === 'firearm').length;
  const berMobility   = allBerItems.filter(i => i.category === 'mobility').length;
  const berComms      = allBerItems.filter(i => i.category === 'communication').length;
  const berInvest     = allBerItems.filter(i => i.category === 'investigative').length;

  // 2. Percentage Helper (relative to totalBer)
  const getPct = (value) => {
    if (totalBer === 0) return '0%';
    // Ensures a minimum width of 5% for visual consistency
    return Math.max(5, Math.round((value / totalBer) * 100)) + '%';
  };

  // 3. Update Text Content
  document.getElementById('totalBerCount').textContent    = totalBer;
  document.getElementById('firearmsBerCount').textContent = berFirearms;
  document.getElementById('mobilityBerCount').textContent = berMobility;
  document.getElementById('commsBerCount').textContent    = berComms;
  document.getElementById('investBerCount').textContent   = berInvest;

  // 4. Update Progress Bar Widths
  // The Total bar is always 100% of itself
  document.getElementById('totalBerBar').style.width    = '100%'; 
  document.getElementById('firearmsBerBar').style.width = getPct(berFirearms);
  document.getElementById('mobilityBerBar').style.width = getPct(berMobility);
  document.getElementById('commsBerBar').style.width    = getPct(berComms);
  document.getElementById('investBerBar').style.width   = getPct(berInvest);
}