// =============================================================================
// PublicSpace360 - Admin Operations Controller (Smart City Dashboard)
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
  // Initialize Mini Pie on Overview
  const miniPieCtx = document.getElementById('adminMiniPie');
  if (miniPieCtx) {
    fetch('/api/analytics')
      .then(res => res.json())
      .then(data => {
        if (data.usage_by_type) {
          new Chart(miniPieCtx, {
            type: 'doughnut',
            data: {
              labels: data.usage_by_type.labels,
              datasets: [{
                data: data.usage_by_type.counts,
                backgroundColor: ['#10b981', '#f97316', '#8b5cf6', '#3b82f6', '#06b6d4'],
                borderWidth: 1.5,
                borderColor: '#ffffff'
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: { legend: { position: 'right' } }
            }
          });
        }
      })
      .catch(e => console.error("Error loading admin mini chart:", e));
  }

  // Handle Add Space Form Submission
  const addSpaceForm = document.getElementById('addSpaceForm');
  if (addSpaceForm) {
    addSpaceForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const fd = new FormData(addSpaceForm);
      const payload = Object.fromEntries(fd.entries());

      fetch('/api/spaces', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(res => res.json())
        .then(res => {
          if (res.success) {
            showToast(res.message, 'success');
            const modalEl = document.getElementById('addSpaceModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            setTimeout(() => location.reload(), 1000);
          } else {
            showToast(res.error || 'Failed to add space', 'danger');
          }
        })
        .catch(err => {
          console.error(err);
          showToast('Network error while saving public space.', 'danger');
        });
    });
  }

  // Handle Edit Space Form Submission
  const editSpaceForm = document.getElementById('editSpaceForm');
  if (editSpaceForm) {
    editSpaceForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const fd = new FormData(editSpaceForm);
      const payload = Object.fromEntries(fd.entries());
      const spaceId = payload.id;

      fetch(`/api/spaces/${spaceId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(res => res.json())
        .then(res => {
          if (res.success) {
            showToast(res.message, 'success');
            const modalEl = document.getElementById('editSpaceModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            setTimeout(() => location.reload(), 1000);
          } else {
            showToast(res.error || 'Failed to update space', 'danger');
          }
        })
        .catch(err => {
          console.error(err);
          showToast('Network error while updating public space.', 'danger');
        });
    });
  }

  // Survey table live search filter
  const searchInput = document.getElementById('surveyTableSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function (e) {
      const q = e.target.value.toLowerCase();
      const rows = document.querySelectorAll('#surveysDataTable tbody tr');
      rows.forEach(r => {
        const text = r.textContent.toLowerCase();
        r.style.display = text.includes(q) ? '' : 'none';
      });
    });
  }
});

// Populate Edit Space Modal
function openEditSpaceModal(space) {
  document.getElementById('edit_space_id').value = space.id;
  document.getElementById('edit_space_name').value = space.name || '';
  document.getElementById('edit_space_type').value = space.type || 'Gardens';
  if (document.getElementById('edit_space_area')) {
    document.getElementById('edit_space_area').value = space.area || 'New Panvel';
  }
  document.getElementById('edit_space_address').value = space.address || '';
  document.getElementById('edit_space_latitude').value = space.latitude || '';
  document.getElementById('edit_space_longitude').value = space.longitude || '';
  document.getElementById('edit_space_description').value = space.description || '';
  document.getElementById('edit_space_facilities').value = space.facilities || '';
  document.getElementById('edit_space_opening_time').value = space.opening_time || '05:00 AM';
  document.getElementById('edit_space_closing_time').value = space.closing_time || '10:00 PM';
  document.getElementById('edit_space_average_visitors').value = space.average_visitors || 500;
  document.getElementById('edit_space_condition').value = space.condition || 'Good';
  document.getElementById('edit_space_image').value = space.image || '';

  const modal = new bootstrap.Modal(document.getElementById('editSpaceModal'));
  modal.show();
}

// Delete Public Space
function deleteSpace(spaceId) {
  if (!confirm(`Are you sure you want to delete this public space (#${spaceId})? All related surveys and reports will also be deleted.`)) return;

  fetch(`/api/spaces/${spaceId}`, {
    method: 'DELETE'
  })
    .then(res => res.json())
    .then(res => {
      if (res.success) {
        showToast(res.message, 'success');
        const row = document.getElementById(`space-row-${spaceId}`);
        if (row) row.remove();
      } else {
        showToast(res.error || 'Failed to delete space', 'danger');
      }
    })
    .catch(() => showToast('Network error while deleting space', 'danger'));
}

// Update Report Status
function updateReportStatus(reportId, newStatus) {
  fetch(`/api/reports/${reportId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus })
  })
    .then(res => res.json())
    .then(res => {
      if (res.success) {
        showToast(`Report #${reportId} updated to '${newStatus}'`, 'success');
      } else {
        showToast(res.error || 'Failed to update report status', 'danger');
      }
    })
    .catch(() => showToast('Network error updating report', 'danger'));
}

// Delete Survey Entry
function deleteSurvey(surveyId) {
  if (!confirm(`Are you sure you want to remove survey response #${surveyId}?`)) return;

  fetch(`/api/surveys/${surveyId}`, {
    method: 'DELETE'
  })
    .then(res => res.json())
    .then(res => {
      if (res.success) {
        showToast('Survey record deleted', 'info');
        const row = document.getElementById(`survey-row-${surveyId}`);
        if (row) row.remove();
      } else {
        showToast(res.error || 'Failed to delete survey', 'danger');
      }
    })
    .catch(() => showToast('Network error deleting survey', 'danger'));
}

// Export Survey Data to CSV File
function exportSurveysToCSV() {
  fetch('/api/surveys')
    .then(res => res.json())
    .then(surveys => {
      if (!surveys || surveys.length === 0) {
        alert('No survey responses to export.');
        return;
      }

      const headers = ['ID', 'User', 'Space Name', 'Space Type', 'Frequency', 'Purpose', 'Age Group', 'Safety', 'Cleanliness', 'Lighting', 'Seating', 'Water', 'Accessibility', 'Improvement', 'Date'];
      const rows = surveys.map(s => [
        s.id,
        `"${(s.user_name || '').replace(/"/g, '""')}"`,
        `"${(s.space_name || '').replace(/"/g, '""')}"`,
        `"${(s.space_type || '').replace(/"/g, '""')}"`,
        `"${(s.visit_frequency || '').replace(/"/g, '""')}"`,
        `"${(s.purpose || '').replace(/"/g, '""')}"`,
        `"${(s.age_group || '').replace(/"/g, '""')}"`,
        s.safety_rating,
        s.cleanliness_rating,
        s.lighting_rating,
        s.seating_rating,
        s.water_rating,
        s.accessibility_rating,
        `"${(s.improvement || '').replace(/"/g, '""')}"`,
        `"${s.created_at}"`
      ]);

      const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', `PublicSpace360_CEP_Surveys_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    })
    .catch(err => console.error("Error exporting CSV:", err));
}

// -----------------------------------------------------------------------------
// Admin Image Management (Requirement 18)
// -----------------------------------------------------------------------------

function deleteSpaceImage(imageId) {
  if (!confirm('Are you sure you want to delete this photograph?')) return;
  fetch(`/api/spaces/images/${imageId}`, { method: 'DELETE' })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast(data.message, 'success');
        const row = document.getElementById(`img-row-${imageId}`);
        if (row) row.remove();
        setTimeout(() => location.reload(), 800);
      } else {
        showToast(data.error || 'Failed to delete image', 'danger');
      }
    })
    .catch(() => showToast('Network error while deleting image.', 'danger'));
}

function setPrimaryImage(imageId) {
  fetch(`/api/spaces/images/${imageId}/primary`, { method: 'PUT' })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast(data.message, 'success');
        setTimeout(() => location.reload(), 800);
      } else {
        showToast(data.error || 'Failed to set primary image', 'danger');
      }
    })
    .catch(() => showToast('Network error while setting primary image.', 'danger'));
}

function openSpaceGalleryModal(spaceId, spaceName) {
  const modalEl = document.getElementById('uploadImageModal');
  if (!modalEl) return;
  const selectEl = document.getElementById('upload_image_space_id');
  if (selectEl) selectEl.value = spaceId;
  const modalTitle = document.getElementById('uploadImageModalTitle');
  if (modalTitle) modalTitle.textContent = `Upload Photo for ${spaceName}`;
  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

// Handle Photo Upload Form Submission
document.addEventListener('DOMContentLoaded', function () {
  const uploadForm = document.getElementById('uploadPhotoForm');
  if (uploadForm) {
    uploadForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const spaceId = uploadForm.space_id.value;
      if (!spaceId) {
        showToast('Please select a public space.', 'warning');
        return;
      }

      const fd = new FormData(uploadForm);
      fetch(`/api/spaces/${spaceId}/images`, {
        method: 'POST',
        body: fd
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showToast(data.message, 'success');
          const modalEl = document.getElementById('uploadImageModal');
          if (modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
          }
          setTimeout(() => location.reload(), 1000);
        } else {
          showToast(data.error || 'Failed to upload photo.', 'danger');
        }
      })
      .catch(() => showToast('Network error while uploading photograph.', 'danger'));
    });
  }
});

// -----------------------------------------------------------------------------
// Admin Comment Moderation (Requirement 10)
// -----------------------------------------------------------------------------

function updateFeedbackStatus(feedbackId, status) {
  fetch(`/api/feedback/${feedbackId}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: status })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.message, 'success');
      const badge = document.getElementById(`fb-status-${feedbackId}`);
      if (badge) {
        badge.textContent = status;
        badge.className = `badge ${status === 'Approved' ? 'bg-success' : 'bg-danger'}`;
      }
    } else {
      showToast(data.error || 'Failed to update status', 'danger');
    }
  })
  .catch(() => showToast('Network error updating comment status.', 'danger'));
}

function deleteFeedback(feedbackId) {
  if (!confirm('Are you sure you want to permanently delete this comment?')) return;
  fetch(`/api/feedback/${feedbackId}`, { method: 'DELETE' })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast(data.message, 'success');
        const row = document.getElementById(`fb-row-${feedbackId}`);
        if (row) row.remove();
      } else {
        showToast(data.error || 'Failed to delete comment', 'danger');
      }
    })
    .catch(() => showToast('Network error deleting comment.', 'danger'));
}

