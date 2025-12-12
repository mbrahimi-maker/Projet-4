import webview
import csv
import os
import sys
from list_product import lecture_produce


class ApiProduit:
    def __init__(self, csv_file='produit.csv'):
        self.csv_file = csv_file

    def get_product_stats(self, nom):
        """Retourne les stats d'un produit pour le diagramme"""
        data_prod = lecture_produce(self.csv_file)
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


def create_product_page(product_name):
    """Crée la page HTML pour afficher un produit avec son diagramme"""
    # Échappe les guillemets dans le nom du produit
    safe_name = product_name.replace("'", "\\'")
    
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Détails produit</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial; margin: 20px; }
            .container { max-width: 600px; margin: auto; }
            #chartWrapper { max-width: 50%; max-height: 50%; margin: 20px auto; }
            #myChart { width: 50% !important; height: 50% !important; }
            button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 id="productTitle">Chargement...</h1>
            <div id="stats"></div>
            <div id="chartWrapper">
                <canvas id="myChart"></canvas>
            </div>
            <br>
            <button onclick="window.pywebview.api.go_back()">Retour</button>
        </div>
        <script>
        window.addEventListener('pywebviewready', function() {
            const productName = '""" + safe_name + """';
            window.pywebview.api.get_product_stats(productName).then(stats => {
                if (!stats) {
                    document.getElementById('productTitle').textContent = 'Produit non trouvé';
                    return;
                }

                document.getElementById('productTitle').textContent = stats.nom;
                document.getElementById('stats').innerHTML = `
                    <p><strong>Prix:</strong> ${stats.prix}€</p>
                    <p><strong>Disponible:</strong> ${stats.disponible} / ${stats.total}</p>
                    <p><strong>Pourcentage disponible:</strong> ${(stats.disponible/stats.total*100).toFixed(2)}%</p>
                `;

                const ctx = document.getElementById('myChart').getContext('2d');
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Disponible', 'Indisponible'],
                        datasets: [{
                            data: [stats.disponible, stats.indisponible],
                            backgroundColor: ['#4CAF50', '#FF6B6B'],
                            borderColor: ['#45a049', '#ff5252'],
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            title: {
                                display: true,
                                text: productName + ' - Stock: ' + stats.disponible + '/' + stats.total
                            },
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }).catch(err => {
                console.error('Erreur:', err);
                document.getElementById('productTitle').textContent = 'Erreur de chargement';
            });
        });
        </script>
    </body>
    </html>
    """
    return content


class ApiProduit:
    def __init__(self, csv_file='produit.csv', window=None):
        self.csv_file = csv_file
        self.window = window

    def get_product_stats(self, nom):
        """Retourne les stats d'un produit pour le diagramme"""
        data_prod = lecture_produce(self.csv_file)
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

    def go_back(self):
        """Ferme la fenêtre et revient à la liste des produits"""
        if self.window:
            self.window.destroy()
        return True


def open_product_page(product_name):
    """Ouvre une nouvelle fenêtre pywebview pour un produit"""
    html = create_product_page(product_name)
    api = ApiProduit('produit.csv')
    window = webview.create_window(f'Produit - {product_name}', html=html, js_api=api)
    api.window = window  # Assigne la fenêtre à l'API
    webview.start()


if __name__ == '__main__':
    # Récupère le nom du produit en argument
    if len(sys.argv) > 1:
        product_name = sys.argv[1]
    else:
        product_name = 'banane'  # Par défaut
    
    open_product_page(product_name)