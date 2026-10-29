// =============================================================================
// PublicSpace360 - Global Utilities & Micro-Interactions
// =============================================================================

// Toast Notification Helper
function showToast(message, type = 'info') {
  const toastEl = document.getElementById('appToast');
  const toastMsg = document.getElementById('toastMessage');
  if (!toastEl || !toastMsg) return;

  const iconMap = {
    'success': '<i class="fa-solid fa-circle-check text-success fs-5"></i>',
    'danger': '<i class="fa-solid fa-circle-xmark text-danger fs-5"></i>',
    'warning': '<i class="fa-solid fa-triangle-exclamation text-warning fs-5"></i>',
    'info': '<i class="fa-solid fa-circle-info text-info fs-5"></i>'
  };

  toastMsg.innerHTML = `${iconMap[type] || iconMap['info']} <div>${message}</div>`;
  const toast = new bootstrap.Toast(toastEl, { delay: 4500 });
  toast.show();
}

// Smooth Number Counter Animation
function animateCounter(element, target, duration = 1500) {
  if (!element) return;
  const start = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // Ease-out cubic
    const easeOut = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(start + (target - start) * easeOut);
    element.textContent = current.toLocaleString();

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      element.textContent = target.toLocaleString();
    }
  }

  requestAnimationFrame(update);
}

document.addEventListener('DOMContentLoaded', function () {
  // Fetch and animate floating stats strip if elements exist
  const statSpacesEl = document.getElementById('stat-spaces');
  const statResponsesEl = document.getElementById('stat-responses');
  const statParksEl = document.getElementById('stat-parks');
  const statPlaygroundsEl = document.getElementById('stat-playgrounds');
  const statPromenadesEl = document.getElementById('stat-promenades');

  if (statSpacesEl || statResponsesEl) {
    fetch('/api/statistics')
      .then(res => res.json())
      .then(stats => {
        if (statSpacesEl) animateCounter(statSpacesEl, (stats.spaces !== undefined ? stats.spaces : stats.total_spaces) || 10);
        if (statResponsesEl) animateCounter(statResponsesEl, (stats.responses !== undefined ? stats.responses : stats.total_surveys) || 30);
        if (statParksEl) animateCounter(statParksEl, (stats.parks !== undefined ? stats.parks : stats.parks_count) || 3);
        if (statPlaygroundsEl) animateCounter(statPlaygroundsEl, (stats.playgrounds !== undefined ? stats.playgrounds : stats.playgrounds_count) || 2);
        if (statPromenadesEl) animateCounter(statPromenadesEl, (stats.promenades !== undefined ? stats.promenades : stats.promenades_count) || 2);
      })
      .catch(err => console.error("Error fetching stats:", err));
  }

  // Sticky Navbar Blur and Shadow on scroll
  const nav = document.querySelector('.navbar-custom');
  if (nav) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 40) {
        nav.classList.add('shadow-lg');
      } else {
        nav.classList.remove('shadow-lg');
      }
    });
  }
});
