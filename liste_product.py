import webview
import csv
import os





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
            #chartLegendNote {
                text-align: center;
                font-size: 11px;
                color: var(--text-muted);
                margin-top: 2px;
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

        data_prod = Api.lecture_produce('produit.csv')
        header = data_prod[0]

        if header and len(header) >= 5:
            content += (
                '<table><caption>Liste des produits</caption>'
                '<thead><tr>'
                f'<th scope="col">{header[1]}</th>'
                f'<th scope="col">{header[2]}</th>'
                f'<th scope="col">{header[3]}</th>'
                f'<th scope="col">{header[4]}</th>'
                '</tr></thead><tbody id="tbody">'
            )
        else:
            content += '<table><tbody id="tbody">'

        for row in data_prod[1:]:
            if len(row) >= 5 and row[0] != "id":
                content += (
                    '<tr>'
                    f'<th scope="row"><a href="javascript:void(0)" class="product-link" data-product="{row[1]}">{row[1]}</a></th>'
                    f'<td>{row[2]} €</td>'
                    f'<td><span class="qty-badge"><span class="qty-dot"></span>{row[3]}</span></td>'
                    f'<td>{row[4]}</td>'
                    '</tr>'
                )

        content += "</tbody></table>"
        content += "</div>"

        content += """
            <div id="productDetailPage" style="display:none;">
                <button id="backBtn"><span>←</span><span>Retour</span></button>
                <h1 id="productTitle"></h1>
                <div id="stats"></div>
                <div id="chartWrapper">
                    <canvas id="myChart"></canvas>
                </div>
                <div id="chartLegendNote">Vert = stock disponible, rose = stock déjà utilisé.</div>
            </div>
            """

        content += """
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>
            let chart = null;

            window.addEventListener('pywebviewready', function() {
                document.getElementById('addForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    const nom = document.getElementById('name').value;
                    const prix = document.getElementById('price').value;
                    const quantit = document.getElementById('quantity').value;

                    window.pywebview.api.add_product_api(nom, prix, quantit).then(() => {
                        const tbody = document.getElementById('tbody');
                        const tr = document.createElement('tr');
                        tr.innerHTML =
                        '<th scope="row"><a href="javascript:void(0)" class="product-link" data-product="' + nom + '">' + nom +
                        '</a></th><td>' + prix + ' €</td>' +
                        '<td><span class="qty-badge"><span class="qty-dot"></span>' + quantit +
                        '</span></td><td>' + quantit + '</td>';
                        tbody.appendChild(tr);
                        document.getElementById('addForm').reset();
                        attachProductLinks();
                    }).catch(err => {
                        console.error('Erreur :', err);
                        alert('Erreur : ' + err.message);
                    });
                });

                document.getElementById('backBtn').addEventListener('click', function() {
                    showMainPage();
                });

                attachProductLinks();
            });

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
                    }, 80);
                }).catch(err => {
                    console.error('Erreur:', err);
                    alert('Erreur de chargement');
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