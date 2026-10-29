// =============================================================================
// PublicSpace360 - Dynamic Chart.js Analytics Engine (CEP Research Telemetry)
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
  fetch('/api/analytics')
    .then(res => res.json())
    .then(data => {
      // 1. Update metric cards
      const totalResponsesEl = document.getElementById('analyticsTotalResponses');
      if (totalResponsesEl) totalResponsesEl.textContent = data.total_responses || '0';

      const topSpaceEl = document.getElementById('analyticsTopSpace');
      if (topSpaceEl) topSpaceEl.textContent = data.most_used_space || 'Central Botanical Park';

      if (data.activities && data.activities.labels && data.activities.labels.length > 0) {
        const topActEl = document.getElementById('analyticsTopActivity');
        if (topActEl) topActEl.textContent = data.activities.labels[0];
      }

      if (data.facility_ratings && data.facility_ratings.scores) {
        const avgSafetyEl = document.getElementById('analyticsAvgSafety');
        if (avgSafetyEl) avgSafetyEl.textContent = `${data.facility_ratings.scores[0]} / 5.0`;
      }

      // Chart Colors Palette
      const palette = {
        emerald: '#10b981',
        orange: '#f97316',
        purple: '#8b5cf6',
        blue: '#3b82f6',
        cyan: '#06b6d4',
        rose: '#f43f5e',
        amber: '#f59e0b'
      };

      // 2. Public Space Usage Pie Chart
      const pieCtx = document.getElementById('usagePieChart');
      if (pieCtx && data.usage_by_type) {
        const pieColors = [palette.emerald, palette.orange, palette.purple, palette.blue, palette.cyan];
        new Chart(pieCtx, {
          type: 'pie',
          data: {
            labels: data.usage_by_type.labels,
            datasets: [{
              data: data.usage_by_type.counts,
              backgroundColor: pieColors,
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom' },
              tooltip: {
                callbacks: {
                  label: function (ctx) {
                    const label = ctx.label || '';
                    const value = ctx.raw || 0;
                    const total = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                    const percentage = Math.round((value / total) * 100);
                    return ` ${label}: ${value} (${percentage}%)`;
                  }
                }
              }
            }
          }
        });

        // Populate percentage legend pills
        const legendContainer = document.getElementById('usagePercentageLegend');
        if (legendContainer && data.usage_by_type.labels) {
          legendContainer.innerHTML = '';
          data.usage_by_type.labels.forEach((lbl, idx) => {
            const pct = data.usage_by_type.percentages[idx] || 0;
            const badge = document.createElement('span');
            badge.className = 'badge bg-light text-dark border px-2 py-1';
            badge.innerHTML = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${pieColors[idx % pieColors.length]};margin-right:4px;"></span> ${lbl}: <b>${pct}%</b>`;
            legendContainer.appendChild(badge);
          });
        }
      }

      // 3. Main Activities Bar Chart
      const actCtx = document.getElementById('activitiesBarChart');
      if (actCtx && data.activities) {
        new Chart(actCtx, {
          type: 'bar',
          data: {
            labels: data.activities.labels,
            datasets: [{
              label: 'Participants',
              data: data.activities.counts,
              backgroundColor: 'rgba(0, 173, 181, 0.75)',
              borderColor: '#00adb5',
              borderWidth: 1.5,
              borderRadius: 8
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                ticks: { stepSize: 1 }
              },
              x: {
                grid: { display: false }
              }
            },
            plugins: {
              legend: { display: false }
            }
          }
        });
      }

      // 4. Age Groups Doughnut Chart
      const ageCtx = document.getElementById('ageDoughnutChart');
      if (ageCtx && data.age_groups) {
        new Chart(ageCtx, {
          type: 'doughnut',
          data: {
            labels: data.age_groups.labels,
            datasets: [{
              data: data.age_groups.counts,
              backgroundColor: [palette.cyan, palette.emerald, palette.purple, palette.orange, palette.blue],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom' }
            }
          }
        });
      }

      // 5. Facility Ratings Bar Chart (1 to 5 scale)
      const facCtx = document.getElementById('facilityRatingsChart');
      if (facCtx && data.facility_ratings) {
        new Chart(facCtx, {
          type: 'bar',
          data: {
            labels: data.facility_ratings.labels,
            datasets: [{
              label: 'Average Citizen Score (out of 5)',
              data: data.facility_ratings.scores,
              backgroundColor: [
                'rgba(16, 185, 129, 0.75)',
                'rgba(59, 130, 246, 0.75)',
                'rgba(245, 158, 11, 0.75)',
                'rgba(6, 182, 212, 0.75)',
                'rgba(139, 92, 246, 0.75)',
                'rgba(244, 63, 94, 0.75)'
              ],
              borderColor: [
                palette.emerald,
                palette.blue,
                palette.amber,
                palette.cyan,
                palette.purple,
                palette.rose
              ],
              borderWidth: 1.5,
              borderRadius: 8
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                min: 0,
                max: 5,
                ticks: { stepSize: 1 }
              },
              x: {
                grid: { display: false }
              }
            },
            plugins: {
              legend: { display: false }
            }
          }
        });
      }

      // 6. Improvements Chart
      const impCtx = document.getElementById('improvementsChart');
      if (impCtx && data.improvement_needs) {
        new Chart(impCtx, {
          type: 'bar',
          data: {
            labels: data.improvement_needs.labels,
            datasets: [{
              label: 'Requested Interventions',
              data: data.improvement_needs.counts,
              backgroundColor: 'rgba(239, 68, 68, 0.7)',
              borderColor: '#ef4444',
              borderRadius: 6
            }]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              x: { beginAtZero: true, ticks: { stepSize: 1 } }
            },
            plugins: { legend: { display: false } }
          }
        });
      }

      // 7. Visitation Frequency Chart
      const freqCtx = document.getElementById('frequencyChart');
      if (freqCtx && data.visit_frequencies) {
        new Chart(freqCtx, {
          type: 'bar',
          data: {
            labels: data.visit_frequencies.labels,
            datasets: [{
              label: 'Visits',
              data: data.visit_frequencies.counts,
              backgroundColor: 'rgba(139, 92, 246, 0.75)',
              borderColor: '#8b5cf6',
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: { beginAtZero: true, ticks: { stepSize: 1 } }
            },
            plugins: { legend: { display: false } }
          }
        });
      }
    })
    .catch(err => console.error("Error loading analytics data:", err));
});
