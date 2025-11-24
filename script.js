// Data contoh untuk grafik pendapatan (mirip seperti di video)
const months = ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb'];
const revenues = [22000, 20000, 25000, 18000, 21000, 15000, 18200, 14678, 8000, 7500, 9000, 6000];

// Mengambil elemen canvas
const ctx = document.getElementById('revenueChart').getContext('2d');

// Konfigurasi dan inisialisasi Chart.js
const revenueChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: months,
        datasets: [{
            label: 'Revenue ($)',
            data: revenues,
            backgroundColor: 'rgba(85, 107, 255, 0.5)', // Warna primary semi-transparan
            borderColor: 'rgba(85, 107, 255, 1)',
            borderWidth: 1,
            borderRadius: 5,
            hoverBackgroundColor: 'rgba(85, 107, 255, 1)', // Warna solid saat hover
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false, // Penting untuk mengontrol tinggi dengan CSS
        scales: {
            y: {
                beginAtZero: true,
                max: 40000,
                ticks: {
                    // Menampilkan dalam ribuan (k)
                    callback: function(value) {
                        return '$' + value / 1000 + 'k';
                    }
                }
            },
            x: {
                grid: {
                    display: false // Menghilangkan garis vertikal di latar belakang
                }
            }
        },
        plugins: {
            legend: {
                display: false // Menghilangkan legend
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            }
        }
    }
});
