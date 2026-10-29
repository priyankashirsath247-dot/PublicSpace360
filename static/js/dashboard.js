// =============================================================================
// PublicSpace360 - User Dashboard Controller
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
  // Initialize tooltips if Bootstrap is available
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }

  // Quick report filter (All, Active, Resolved)
  const reportFilter = document.getElementById('reportStatusFilter');
  if (reportFilter) {
    reportFilter.addEventListener('change', function (e) {
      const selectedStatus = e.target.value.toLowerCase();
      const rows = document.querySelectorAll('#userReportsTable tbody tr');

      rows.forEach(row => {
        const statusBadge = row.querySelector('.badge');
        if (!statusBadge) return;
        const status = statusBadge.textContent.trim().toLowerCase();

        if (selectedStatus === 'all' || status === selectedStatus) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }

  // Quick survey table search
  const surveySearch = document.getElementById('userSurveySearch');
  if (surveySearch) {
    surveySearch.addEventListener('input', function (e) {
      const query = e.target.value.toLowerCase();
      const rows = document.querySelectorAll('#userSurveysTable tbody tr');

      rows.forEach(row => {
        const spaceName = row.querySelector('.space-name')?.textContent.toLowerCase() || '';
        const purpose = row.querySelector('.survey-purpose')?.textContent.toLowerCase() || '';

        if (spaceName.includes(query) || purpose.includes(query)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }
});
