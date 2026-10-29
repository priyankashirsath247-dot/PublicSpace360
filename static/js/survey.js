// =============================================================================
// PublicSpace360 - Survey Form Handler & Rating Widget Logic
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
  const surveyForm = document.getElementById('cepSurveyForm');
  if (!surveyForm) return;

  // Handle Scale Rating Buttons (1 to 5)
  const ratingGroups = document.querySelectorAll('.rating-scale-group');
  ratingGroups.forEach(group => {
    const targetInputId = group.getAttribute('data-target');
    const targetInput = document.getElementById(targetInputId);
    const badgeSpan = document.getElementById('val_' + targetInputId.replace('_rating', ''));
    const buttons = group.querySelectorAll('.scale-btn');

    buttons.forEach(btn => {
      btn.addEventListener('click', function () {
        buttons.forEach(b => b.classList.remove('selected'));
        this.classList.add('selected');
        const val = this.getAttribute('data-value');
        if (targetInput) targetInput.value = val;
        if (badgeSpan) badgeSpan.textContent = `${val} / 5`;
      });
    });
  });

  // Handle Survey Submission via REST API
  surveyForm.addEventListener('submit', function (e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submitSurveyBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Submitting Survey...';

    const formData = new FormData(surveyForm);
    const payload = {
      space_id: formData.get('space_id'),
      visit_frequency: formData.get('visit_frequency'),
      purpose: formData.get('purpose'),
      age_group: formData.get('age_group'),
      safety_rating: formData.get('safety_rating'),
      cleanliness_rating: formData.get('cleanliness_rating'),
      lighting_rating: formData.get('lighting_rating'),
      seating_rating: formData.get('seating_rating'),
      water_rating: formData.get('water_rating'),
      accessibility_rating: formData.get('accessibility_rating'),
      improvement: formData.get('improvement'),
      suggestion: formData.get('suggestion')
    };

    fetch('/api/surveys', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(res => {
        if (res.success) {
          showToast(res.message, 'success');
          setTimeout(() => {
            window.location.href = '/results';
          }, 1500);
        } else {
          showToast(res.error || 'Failed to submit survey.', 'danger');
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane me-2"></i> Submit Survey Response';
        }
      })
      .catch(err => {
        console.error('Survey submit error:', err);
        showToast('A network error occurred while submitting.', 'danger');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane me-2"></i> Submit Survey Response';
      });
  });
});
