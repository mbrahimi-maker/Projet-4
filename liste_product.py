import webview
import csv
import os
import json
from datetime import datetime, timedelta





class Api:
    def __init__(self, csv_file='produit.csv'):
        self.csv_file = csv_file

    def lecture_produce(self, csv_file=None):
        if csv_file is None:
            csv_file = 'produit.csv'

        csv_path_arg = os.path.join(os.path.dirname(__file__), 'Data', csv_file)
        data_prod = []
        with open(csv_path_arg, 'r', newline='', encoding='utf-8') as csv_prod:
            reader = csv.reader(csv_prod)
            for row in reader:
                data_prod.append(row)
        return data_prod


    def get_product_stats(self, nom):
        """Récupère les statistiques d'un produit"""
        data_prod = self.lecture_produce(self.csv_file)
        for row in data_prod[1:]:
            if len(row) >= 5 and row[1] == nom:
                try:
                    disponible = float(row[3])
                    total = float(row[4])
                    indisponible = total - disponible
                    return {
                        'nom': nom,
                        'prix': row[2],
                        'disponible': disponible,
                        'indisponible': indisponible,
                        'total': total
                    }
                except (ValueError, IndexError):
                    return None
        return None



    def page(self):
        content = """
        <html>
        <head>
        <meta charset="utf-8">
        <title>Gestion produits</title>
        <style>
            :root {
                --bg: #f5f7fb;
                --card: #ffffff;
                --primary: #5b8def;
                --primary-soft: #e4edff;
                --accent: #4caf93;
                --accent-soft: #d9f5ea;
                --danger-soft: #ffe3e3;
                --text-main: #1f2933;
                --text-muted: #6b7280;
                --border-soft: #e2e8f0;
            }
            * {
                box-sizing: border-box;
            }
            body {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                margin: 0;
                padding: 24px;
                background: radial-gradient(circle at top left, #fdfcff, #edf2fb);
                color: var(--text-main);
            }
            h1, h2 {
                margin: 0;
                font-weight: 600;
            }
            #shell {
                max-width: 960px;
                margin: 0 auto;
            }
            #mainPage, #productDetailPage {
                background: var(--card);
                padding: 20px 20px 24px;
                border-radius: 14px;
                box-shadow: 0 18px 40px rgba(148,163,184,0.35);
                margin-top: 20px;
                border: 1px solid var(--border-soft);
            }
            #message {
                padding: 8px 4px 0;
            }
            #header-line {
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
                gap: 12px;
            }
            #message h1 {
                font-size: 26px;
            }
            #message h1 span {
                color: var(--primary);
            }
            .form-produit {
                display: flex;
                flex-wrap: wrap;
                gap: 16px;
                align-items: flex-end;
                margin: 16px 0 10px;
            }
            .form-row label {
                font-size: 13px;
                color: var(--text-muted);
            }
            .form-row input {
                width: 160px;
                margin-top: 4px;
                padding: 7px 9px;
                border-radius: 8px;
                border: 1px solid var(--border-soft);
                background: #f9fbff;
                color: var(--text-main);
                outline: none;
                transition: border 0.15s, box-shadow 0.15s, background 0.15s, transform 0.06s;
            }
            .form-row input:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 2px rgba(91,141,239,0.25);
                background: #ffffff;
                transform: translateY(-1px);
            }
            .btn-primary {
                padding: 8px 18px;
                background: linear-gradient(135deg, var(--primary), #7bb3ff);
                color: #ffffff;
                border: none;
                border-radius: 999px;
                cursor: pointer;
                font-weight: 600;
                font-size: 14px;
                letter-spacing: 0.01em;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                box-shadow: 0 10px 24px rgba(91,141,239,0.45);
                transition: transform 0.08s ease-out, box-shadow 0.08s ease-out, filter 0.08s;
            }
            .btn-primary:hover {
                transform: translateY(-1px);
                box-shadow: 0 16px 30px rgba(91,141,239,0.5);
                filter: brightness(1.02);
            }
            .btn-primary:active {
                transform: translateY(0);
                box-shadow: 0 6px 14px rgba(91,141,239,0.4);
            }
            .btn-primary::before {
                content: "+";
                font-size: 18px;
                margin-right: 2px;
            }
            hr {
                border: none;
                border-top: 1px dashed #d4dbe8;
                margin: 10px 0 6px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 4px;
                background: var(--card);
                border-radius: 10px;
                overflow: hidden;
                border: 1px solid var(--border-soft);
            }
            caption {
                caption-side: top;
                font-weight: 600;
                margin-bottom: 6px;
                text-align: left;
                color: var(--text-muted);
                font-size: 13px;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }
            th, td {
                border-bottom: 1px solid #edf2f7;
                padding: 8px 10px;
                text-align: left;
                font-size: 13px;
            }
            thead {
                background: var(--primary-soft);
            }
            thead th {
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #4b5563;
            }
            tbody tr:last-child td,
            tbody tr:last-child th {
                border-bottom: none;
            }
            tbody tr:nth-child(even) {
                background: #f9fafb;
            }
            tbody tr:hover {
                background: #e9f3ff;
            }
            .product-link {
                color: #1f2933 !important;
                text-decoration: none;
                cursor: pointer;
                font-weight: 500;
            }
            .product-link:hover {
                text-decoration: underline;
                color: var(--primary) !important;
            }
            .qty-badge {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                padding: 2px 8px;
                border-radius: 999px;
                background: var(--accent-soft);
                color: #166a57;
                font-size: 12px;
            }
            .qty-dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: var(--accent);
            }
            #productDetailPage {
                max-width: 720px;
                margin: 20px auto 0;
            }
            #productTitle {
                margin-top: 10px;
                margin-bottom: 6px;
                font-size: 22px;
                color: var(--primary);
            }
            #stats p {
                margin: 4px 0;
                font-size: 14px;
                color: var(--text-muted);
            }
            #stats strong {
                color: var(--text-main);
            }
            #chartWrapper {
                max-width: 320px;
                margin: 20px auto 4px;
            }
            #backBtn {
                padding: 6px 14px;
                font-size: 13px;
                cursor: pointer;
                border-radius: 999px;
                border: 1px solid var(--border-soft);
                background: #f3f4ff;
                color: #374151;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                transition: background 0.1s, transform 0.08s;
            }
            #backBtn:hover {
                background: #e0e7ff;
                transform: translateY(-1px);
            }
            #backBtn span {
                font-size: 16px;
            }
            .btn-logout {
                padding: 8px 16px;
                background: linear-gradient(135deg, #ef4444, #dc2626);
                color: #ffffff;
                border: none;
                border-radius: 999px;
                cursor: pointer;
                font-weight: 600;
                font-size: 14px;
                box-shadow: 0 10px 24px rgba(239,68,68,0.45);
                transition: transform 0.08s ease-out, box-shadow 0.08s ease-out, filter 0.08s;
            }
            .btn-logout:hover {
                transform: translateY(-1px);
                box-shadow: 0 16px 30px rgba(239,68,68,0.5);
                filter: brightness(1.02);
            }
            .btn-logout:active {
                transform: translateY(0);
                box-shadow: 0 6px 14px rgba(239,68,68,0.4);
            }
            #chartLegendNote {
                text-align: center;
                font-size: 11px;
                color: var(--text-muted);
                margin-top: 2px;
            }
            .price-input, .stock-input {
                width: 80px;
                padding: 6px;
                border: 1px solid var(--border-soft);
                border-radius: 4px;
                font-size: 12px;
            }
            .btn-update {
                padding: 6px 12px;
                background: linear-gradient(135deg, #4caf93, #5dd9a3);
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 600;
            }
            .btn-update:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(76,175,147,0.3);
            }
            @media (max-width: 720px) {
                body {
                    padding: 16px;
                }
                .form-row input {
                    width: 100%;
                }
                .form-produit {
                    align-items: stretch;
                }
                table {
                    font-size: 12px;
                }
                th, td {
                    padding: 7px 8px;
                }
            }
        </style>
        </head>
        <body>
        <div id="shell">
        <div id="message">
        <div id="header-line">
            <div>
            <h1>Bonjour, <span>inventaire</span></h1>
            </div>
            <button id="logoutBtn" class="btn-logout">Déconnexion</button>
        </div>
        </div>
        """

        content += """
            <div id="mainPage">
            <h2>Ajouter un produit</h2>
            <form id="addForm" class="form-produit">
            <div class="form-row">
                <label>Nom<br><input id="name" required></label>
            </div>
            <div class="form-row">
                <label>Prix<br><input id="price" type="number" step="0.01" required></label>
            </div>
            <div class="form-row">
                <label>Quantité<br><input id="quantity" type="number" required></label>
            </div>
            <button type="submit" class="btn-primary">Ajouter</button>
            </form>
            <hr />
            """

        api_instance = Api()
        data_prod = api_instance.lecture_produce('produit.csv')
        header = data_prod[0]

        if header and len(header) >= 5:
            content += (
                '<table><caption>Liste des produits</caption>'
                '<thead><tr>'
                f'<th scope="col">{header[1]}</th>'
                f'<th scope="col">{header[2]}</th>'
                f'<th scope="col">{header[3]}</th>'
                f'<th scope="col">{header[4]}</th>'
                '<th scope="col">Actions</th>'
                '</tr></thead><tbody id="tbody">'
            )
        else:
            content += '<table><tbody id="tbody">'

        for row in data_prod[1:]:
            if len(row) >= 5 and row[0] != "id":
                content += (
                    '<tr data-product-id="' + row[0] + '" data-product-name="' + row[1] + '">'
                    f'<th scope="row"><a href="javascript:void(0)" class="product-link" data-product="{row[1]}">{row[1]}</a></th>'
                    f'<td><input type="number" step="0.01" class="price-input" value="{row[2]}" data-product-id="{row[0]}"></td>'
                    f'<td><input type="number" class="stock-input" value="{row[3]}" data-product-id="{row[0]}"></td>'
                    f'<td>{row[4]}</td>'
                    f'<td><button class="btn-update" data-product-id="{row[0]}" data-product-name="{row[1]}">Enregistrer</button></td>'
                    '</tr>'
                )

        content += """
            </tbody></table>

            <div style="margin-top:16px;">
                <h2>Répartition des ventes par quantité</h2>
                <canvas id="globalSalesChart"></canvas>
            </div>

            <div style="margin-top:16px;">
                <h2>Répartition des ventes par prix</h2>
                <canvas id="globalPriceChart"></canvas>
            </div>
        </div>
"""

        content += """
            <div id="productDetailPage" style="display:none;">
                <button id="backBtn"><span>←</span><span>Retour</span></button>
                <h1 id="productTitle"></h1>
                <div id="stats"></div>
                <div id="chartWrapper">
                    <canvas id="myChart"></canvas>
                </div>
                <div id="chartLegendNote">Vert = stock disponible, rose = stock déjà utilisé.</div>
                
                <div style="margin-top: 30px;">
                    <h2>Ventes sur la dernière semaine</h2>
                    <div style="max-width: 600px; margin: 0 auto;">
                        <canvas id="weekChart"></canvas>
                    </div>
                </div>
                
                <div style="margin-top: 30px;">
                    <h2>Ventes sur le dernier mois</h2>
                    <div style="max-width: 600px; margin: 0 auto;">
                        <canvas id="monthChart"></canvas>
                    </div>
                </div>
            </div>
            """

        data_prod = Api.lecture_produce('produit.csv')
        header = data_prod[0]

        circle_price = []

        circle_data = []

        for row in data_prod[1:]:
            nom = row[1]
            prix = float(row[2])
            dispo = int(row[3])
            total = int(row[4])

            vendu = max(total - dispo, 0)

            montant = vendu * prix

            circle_data.append({
                "nom": nom,
                "vendu": vendu
            })

            circle_price.append({
                "nom": nom,
                "montant": montant
            })
        




        content += f"""<script>const globalSalesData = {json.dumps(circle_data, ensure_ascii=False)};</script>"""
        content += f"""<script>const globalPriceData = {json.dumps(circle_price, ensure_ascii=False)};</script>"""
        content += """
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>

            let chart = null;
            let globalChart = null;
            let globalPrice = null;
            

            window.addEventListener('pywebviewready', function() {
                document.getElementById('logoutBtn').addEventListener('click', function() {
                    window.pywebview.api.logout();
                });

                document.getElementById('addForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    const nom = document.getElementById('name').value;
                    const prix = document.getElementById('price').value;
                    const quantit = document.getElementById('quantity').value;

                    window.pywebview.api.add_product_api(nom, prix, quantit).then((result) => {
                        const tbody = document.getElementById('tbody');
                        const tr = document.createElement('tr');
                        const productId = result.id;
                        
                        tr.innerHTML =
                        '<th scope="row"><a href="javascript:void(0)" class="product-link" data-product="' + nom + '">' + nom +
                        '</a></th>' +
                        '<td><input type="number" step="0.01" class="price-input" value="' + prix + '" data-product-id="' + productId + '"></td>' +
                        '<td><input type="number" class="stock-input" value="' + quantit + '" data-product-id="' + productId + '"></td>' +
                        '<td>' + quantit + '</td>' +
                        '<td><button class="btn-update" data-product-id="' + productId + '" data-product-name="' + nom + '">Enregistrer</button></td>';
                        
                        tr.setAttribute('data-product-id', productId);
                        tr.setAttribute('data-product-name', nom);
                        tbody.appendChild(tr);
                        document.getElementById('addForm').reset();
                        
                        // Ajouter l'event listener au nouveau bouton
                        const newButton = tr.querySelector('.btn-update');
                        newButton.addEventListener('click', function() {
                            const productId = this.getAttribute('data-product-id');
                            const productName = this.getAttribute('data-product-name');
                            const newPrice = tr.querySelector('.price-input').value;
                            const newStock = tr.querySelector('.stock-input').value;
                            
                            if (!newPrice || !newStock) {
                                alert('Veuillez remplir tous les champs');
                                return;
                            }
                            
                            window.pywebview.api.update_product_price(productName, newPrice).then(priceResult => {
                                window.pywebview.api.add_stock(productName, newStock).then(stockResult => {
                                    if (priceResult.success && stockResult.success) {
                                        alert('Produit modifié avec succès');
                                        showMainPage();
                                    } else {
                                        alert('Erreur lors de la modification');
                                    }
                                }).catch(err => {
                                    console.error('Erreur stock:', err);
                                    alert('Erreur lors de la modification du stock');
                                });
                            }).catch(err => {
                                console.error('Erreur prix:', err);
                                alert('Erreur lors de la modification du prix');
                            });
                        });
                        
                        attachProductLinks();
                    }).catch(err => {
                        console.error('Erreur :', err);
                        alert('Erreur : ' + err.message);
                    });
                });

                document.getElementById('backBtn').addEventListener('click', function() {
                    showMainPage();
                });

                // Event listener pour les boutons Enregistrer
                document.querySelectorAll('.btn-update').forEach(button => {
                    button.addEventListener('click', function() {
                        const productId = this.getAttribute('data-product-id');
                        const productName = this.getAttribute('data-product-name');
                        const newPrice = document.querySelector('.price-input[data-product-id="' + productId + '"]').value;
                        const newStock = document.querySelector('.stock-input[data-product-id="' + productId + '"]').value;
                        
                        if (!newPrice || !newStock) {
                            alert('Veuillez remplir tous les champs');
                            return;
                        }
                        
                        window.pywebview.api.update_product_price(productName, newPrice).then(priceResult => {
                            window.pywebview.api.add_stock(productName, newStock).then(stockResult => {
                                if (priceResult.success && stockResult.success) {
                                    alert('Produit modifié avec succès');
                                    showMainPage();
                                } else {
                                    alert('Erreur lors de la modification');
                                }
                            }).catch(err => {
                                console.error('Erreur stock:', err);
                                alert('Erreur lors de la modification du stock');
                            });
                        }).catch(err => {
                            console.error('Erreur prix:', err);
                            alert('Erreur lors de la modification du prix');
                        });
                    });
                });

                attachProductLinks();

                buildGlobalSalesChart();
                buildGlobalPriceChart();
            });

            function buildGlobalPriceChart(){
                const labels = globalPriceData.map(p => p.nom);
                const values = globalPriceData.map(p => p.montant);
                const ctx = document.getElementById('globalPriceChart').getContext('2d');
                    if (globalPrice) {
                        globalPrice.destroy();
                    }

                globalChart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Part des ventes',
                            data: values,
                            backgroundColor: [
                                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                                '#9966FF', '#FF9F40', '#66BB6A', '#AB47BC',
                                '#29B6F6', '#EC407A', '#FFA726', '#8D6E63'
                            ],
                            borderColor: '#ffffff',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Répartition des ventes (total - disponible)'
                            },
                            legend: {
                                position: 'bottom'
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.parsed;
                                        const total = context.chart._metasets[0].total;
                                        const percent = total > 0
                                            ? (value / total * 100).toFixed(1)
                                            : 0;
                                        return `${label}: ${value} € ventes (${percent}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            function buildGlobalSalesChart() {
                const labels = globalSalesData.map(p => p.nom);
                const values = globalSalesData.map(p => p.vendu);

                const ctx = document.getElementById('globalSalesChart').getContext('2d');

                if (globalChart) {
                    globalChart.destroy();
                }

                globalChart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Part des ventes',
                            data: values,
                            backgroundColor: [
                                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                                '#9966FF', '#FF9F40', '#66BB6A', '#AB47BC',
                                '#29B6F6', '#EC407A', '#FFA726', '#8D6E63'
                            ],
                            borderColor: '#ffffff',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Répartition des ventes (total - disponible)'
                            },
                            legend: {
                                position: 'bottom'
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.parsed;
                                        const total = context.chart._metasets[0].total;
                                        const percent = total > 0
                                            ? (value / total * 100).toFixed(1)
                                            : 0;
                                        return `${label}: ${value} ventes (${percent}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
            }


            function attachProductLinks() {
                document.querySelectorAll('.product-link').forEach(link => {
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        const productName = this.getAttribute('data-product');
                        showProductDetail(productName);
                    });
                });
            }

            function showMainPage() {
                document.getElementById('mainPage').style.display = 'block';
                document.getElementById('productDetailPage').style.display = 'none';
                if (chart) {
                    chart.destroy();
                    chart = null;
                }
            }

            function showProductDetail(productName) {
                window.pywebview.api.get_product_stats(productName).then(stats => {
                    if (!stats) {
                        alert('Produit non trouvé');
                        return;
                    }

                    document.getElementById('mainPage').style.display = 'none';
                    document.getElementById('productDetailPage').style.display = 'block';

                    document.getElementById('productTitle').textContent = stats.nom;
                    document.getElementById('stats').innerHTML = `
                        <p><strong>Prix :</strong> ${stats.prix}€</p>
                        <p><strong>Disponible :</strong> ${stats.disponible} / ${stats.total}</p>
                        <p><strong>Pourcentage disponible :</strong> ${(stats.disponible/stats.total*100).toFixed(2)}%</p>
                    `;

                    setTimeout(() => {
                        const ctx = document.getElementById('myChart').getContext('2d');

                        if (chart) {
                            chart.destroy();
                        }

                        chart = new Chart(ctx, {
                            type: 'doughnut',
                            data: {
                                labels: ['Disponible', 'Indisponible'],
                                datasets: [{
                                    data: [stats.disponible, stats.indisponible],
                                    backgroundColor: ['#9FD9C6', '#FFC9DE'],
                                    borderColor: ['#4caf93', '#FF8CA4'],
                                    borderWidth: 2,
                                    hoverOffset: 5,
                                    cutout: '62%'
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: true,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: productName + ' - Stock: ' + stats.disponible + '/' + stats.total,
                                        color: '#111827',
                                        font: { size: 14, weight: '500' }
                                    },
                                    legend: {
                                        position: 'bottom',
                                        labels: { color: '#4b5563' }
                                    }
                                }
                            }
                        });
                        
                        // Afficher les graphiques de ventes
                        window.pywebview.api.get_sales_week(productName).then(weekData => {
                            buildWeekChart(weekData);
                        });
                        
                        window.pywebview.api.get_sales_month(productName).then(monthData => {
                            buildMonthChart(monthData);
                        });
                    }, 80);
                }).catch(err => {
                    console.error('Erreur:', err);
                    alert('Erreur de chargement');
                });
            }
            
            let weekChartObj = null;
            let monthChartObj = null;
            
            function buildWeekChart(weekData) {
                const labels = Object.keys(weekData).map(date => {
                    const d = new Date(date + 'T00:00:00');
                    return d.toLocaleDateString('fr-FR', { weekday: 'short', month: 'short', day: 'numeric' });
                });
                const values = Object.values(weekData);
                
                const ctx = document.getElementById('weekChart').getContext('2d');
                if (weekChartObj) {
                    weekChartObj.destroy();
                }
                
                weekChartObj = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Ventes (quantité)',
                            data: values,
                            backgroundColor: '#5b8def',
                            borderColor: '#3d5fa3',
                            borderWidth: 1,
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top'
                            },
                            title: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1
                                }
                            }
                        }
                    }
                });
            }
            
            function buildMonthChart(monthData) {
                const labels = Object.keys(monthData).map(date => {
                    const d = new Date(date + 'T00:00:00');
                    return d.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' });
                });
                const values = Object.values(monthData);
                
                const ctx = document.getElementById('monthChart').getContext('2d');
                if (monthChartObj) {
                    monthChartObj.destroy();
                }
                
                monthChartObj = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Ventes (quantité)',
                            data: values,
                            borderColor: '#4caf93',
                            backgroundColor: 'rgba(76, 175, 147, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3,
                            pointBackgroundColor: '#4caf93',
                            pointBorderColor: '#ffffff',
                            pointBorderWidth: 2,
                            pointRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top'
                            },
                            title: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1
                                }
                            }
                        }
                    }
                });
            }
            </script>
        </div>
        </body>
        </html>
            """
        return content

def hello_world():
    pass


if __name__ == '__main__':
    csv_path = os.path.join(os.path.dirname(__file__), 'Data', 'produit.csv')

    content = Api('produit.csv').page()

    api = Api('produit.csv')
    window = webview.create_window('Gestion produits', html=content, js_api=api)
    webview.start(window)