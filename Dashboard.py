<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard CRM Sederhana</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="styles.css">
    <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
</head>
<body>
    <div class="dashboard-container">
        <aside class="sidebar">
            <div class="logo">Pivora <span>CRM Platform</span></div>
            <nav>
                <ul>
                    <li><a href="#" class="active"><i class='bx bxs-dashboard'></i> Dashboard</a></li>
                    <li><a href="#"><i class='bx bx-notepad'></i> Deals</a></li>
                    <li><a href="#"><i class='bx bx-calendar'></i> Notes</a></li>
                    <li><a href="#"><i class='bx bx-file'></i> Reports</a></li>
                    </ul>
            </nav>
        </aside>

        <main class="main-content">
            <header class="header">
                <h2>Dashboard</h2>
                <div class="header-actions">
                    <button class="btn-export">Export <i class='bx bx-download'></i></button>
                </div>
            </header>

            <section class="stats-cards">
                <div class="card">
                    <div class="card-title">Leads</div>
                    <div class="card-value">129</div>
                    <div class="card-change up">↑ 2% vs last week</div>
                </div>
                <div class="card">
                    <div class="card-title">CLV</div>
                    <div class="card-value">14d</div>
                    <div class="card-change down">↓ 4% vs last week</div>
                </div>
                </section>

            <section class="revenue-chart-area">
                <h3>Revenue <small>$32.209 +22% vs last month</small></h3>
                <div class="chart-container">
                    <canvas id="revenueChart"></canvas>
                </div>
            </section>
            
            <section class="bottom-area">
                </section>

        </main>
    </div>

    <script src="script.js"></script>
</body>
</html>
