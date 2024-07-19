document.addEventListener('DOMContentLoaded', function() {
    var dailyCtx = document.getElementById('dailyChart').getContext('2d');
    var dailyChart = new Chart(dailyCtx, {
        type: 'bar',
        data: dailyChartData,
        options: {
            scales: {
                x: {
                    type: 'category',
                    labels: dailyChartData.labels,
                    ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            size: 20 // font size on x-axis
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Playing Time (minutes)', // unit on y-axis
                        font: {
                            size: 20 // font size of x-axis label
                        }
                    },
                    ticks: {
                        font: {
                            size: 20 // font size of y-axis label
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: {
                            size: 20 // font size of legend
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            var label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            var hour = context.label;
                            var game_name = context.dataset.label;
                            var times = context.chart.data.tooltipData[hour][game_name];
                            label += times.join(', ');
                            return label;
                        }
                    }
                }
            }
        }
    });

    var weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
    var weeklyChart = new Chart(weeklyCtx, {
        type: 'line',
        data: weeklyChartData,
        options: {
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        font: {
                            size: 20 // font size of x-axis label
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Playing Time (minutes)', // unite on y
                        font: {
                            size: 20 // font size of x-axis label
                        }
                    },
                    ticks: {
                        font: {
                            size: 20 // font size of y-axis label
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: {
                            size: 20 // font size of legend
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 20 // font size of marks
                    }
                }
            }
        }
    });
});



var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});