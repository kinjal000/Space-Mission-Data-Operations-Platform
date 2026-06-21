document.addEventListener("DOMContentLoaded", function() {
  const satContainer = document.getElementById("satellite-chart-container");
  const missionContainer = document.getElementById("mission-chart-container");
  
  let satelliteChart = null;
  let missionChart = null;

  // Retrieve current color styles from CSS Variables
  function getThemeColors() {
    const style = getComputedStyle(document.documentElement);
    return {
      text: style.getPropertyValue('--text-main').trim() || '#394462',
      muted: style.getPropertyValue('--text-muted').trim() || '#685A87',
      border: style.getPropertyValue('--border-color').trim() || 'rgba(104, 90, 135, 0.15)',
      primary: style.getPropertyValue('--palette-685a87').trim() || '#685A87',
      secondary: style.getPropertyValue('--palette-b391b9').trim() || '#B391B9',
      highlight: style.getPropertyValue('--palette-98a9d0').trim() || '#98A9D0',
      darkNavy: style.getPropertyValue('--palette-394462').trim() || '#394462'
    };
  }

  function initCharts() {
    const colors = getThemeColors();

    // 1. Satellite Status Chart (Doughnut)
    if (satContainer) {
      const labels = JSON.parse(satContainer.getAttribute("data-labels") || "[]");
      const values = JSON.parse(satContainer.getAttribute("data-values") || "[]");
      const ctx = document.getElementById('satelliteStatusChart').getContext('2d');
      
      satelliteChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: values,
            backgroundColor: [colors.primary, colors.secondary],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: colors.text,
                font: {
                  family: 'Outfit',
                  size: 13,
                  weight: '500'
                }
              }
            }
          }
        }
      });
    }

    // 2. Mission Status Chart (Bar)
    if (missionContainer) {
      const labels = JSON.parse(missionContainer.getAttribute("data-labels") || "[]");
      const values = JSON.parse(missionContainer.getAttribute("data-values") || "[]");
      const ctx = document.getElementById('missionStatusChart').getContext('2d');
      
      missionChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Missions Count',
            data: values,
            backgroundColor: colors.primary,
            borderRadius: 6,
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
                color: colors.muted,
                font: {
                  family: 'Outfit'
                }
              },
              grid: {
                color: colors.border
              }
            },
            x: {
              ticks: {
                color: colors.muted,
                font: {
                  family: 'Outfit'
                }
              },
              grid: {
                display: false
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    }
  }

  // Update chart configs on theme change
  function updateChartsTheme() {
    const colors = getThemeColors();

    if (satelliteChart) {
      satelliteChart.options.plugins.legend.labels.color = colors.text;
      satelliteChart.data.datasets[0].backgroundColor = [colors.primary, colors.secondary];
      satelliteChart.update();
    }

    if (missionChart) {
      missionChart.options.scales.y.ticks.color = colors.muted;
      missionChart.options.scales.y.grid.color = colors.border;
      missionChart.options.scales.x.ticks.color = colors.muted;
      missionChart.data.datasets[0].backgroundColor = colors.primary;
      missionChart.update();
    }
  }

  // Run initialization
  initCharts();

  // Listen to the theme switcher toggle
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('change', function() {
      // Small timeout to allow CSS variables to transition / change values
      setTimeout(updateChartsTheme, 80);
    });
  }
});
