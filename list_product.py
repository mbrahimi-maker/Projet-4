import webview
import csv
import os


def set_prod(nom, prix=0, quantit=0, csv_file=None):
    """Modifie un produit existant
    
    Args:
        nom: Nom du produit à modifier
        prix: Nouveau prix (optionnel)
        quantit: Nouvelle quantité (optionnel)
        csv_file: Nom du fichier CSV (ex: 'produit.csv')
    """
    if csv_file is None:
        csv_file = 'produit.csv'
    
    csv_path_arg = os.path.join(os.path.dirname(__file__), 'Data', csv_file)
    data_prod = []
    header = []
    with open(csv_path_arg, 'r', newline='', encoding='utf-8') as csv_prod:
        reader = csv.reader(csv_prod)
        for i, row in enumerate(reader):
            if i == 0:
                header = row
                data_prod.append(row)
            else:
                if len(row) < 5:
                    continue
                id0 = row[0]
                name = row[1]
                try:
                    price = float(row[2])
                except Exception:
                    price = 0.0
                quantity = row[3]
                total = row[4]
                if quantit == 0: 
                    quantit = quantity
                if prix == 0: 
                    prix = price
                if name == nom:
                    price = prix
                    quantity = quantit

                data_prod.append([id0, name, f"{price}", quantity, total])

    with open(csv_path_arg, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data_prod)


def lecture_produce(csv_file=None):
    """Lit un fichier CSV
    
    Args:
        csv_file: Nom du fichier CSV (ex: 'produit.csv')
    """
    if csv_file is None:
        csv_file = 'produit.csv'
    
    csv_path_arg = os.path.join(os.path.dirname(__file__), 'Data', csv_file)
    data_prod = []
    with open(csv_path_arg, 'r', newline='', encoding='utf-8') as csv_prod:
        reader = csv.reader(csv_prod)
        for row in reader:
            data_prod.append(row)
    return data_prod


def add_product(nom, prix, quantit, csv_file=None):
    """Ajoute un nouveau produit
    
    Args:
        nom: Nom du produit
        prix: Prix du produit
        quantit: Quantité du produit
        csv_file: Nom du fichier CSV (ex: 'produit.csv')
    """
    if csv_file is None:
        csv_file = 'produit.csv'
    
    csv_path_arg = os.path.join(os.path.dirname(__file__), 'Data', csv_file)
    # lecture
    data_prod = []
    header = []
    with open(csv_path_arg, 'r', newline='', encoding='utf-8') as csv_prod:
        reader = csv.reader(csv_prod)
        for i, row in enumerate(reader):
            if i == 0:
                header = row
                data_prod.append(row)
            else:
                if len(row) < 5:
                    continue
                id0 = row[0]
                name = row[1]
                try:
                    price = float(row[2])
                except Exception:
                    price = 0.0
                quantity = row[3]
                total = row[4]
                data_prod.append([id0, name, f"{price}", quantity, total])
        
        # Déterminer le prochain ID
        next_id = 1
        if len(data_prod) > 1:
            try:
                last_id = int(data_prod[-1][0])
                next_id = last_id + 1
            except:
                next_id = len(data_prod)
        
        data_prod.append([str(next_id), nom, str(prix), str(quantit), str(quantit)])

    # Réécrire
    with open(csv_path_arg, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data_prod)


class Api:
    def __init__(self, csv_file='produit.csv'):
        self.csv_file = csv_file

    def add_product_api(self, nom, prix, quantit):
        """Récupère les champs du formulaire et appelle add_product"""
        try:
            prix = float(prix)
        except:
            prix = 0.0
        try:
            quantit = int(quantit)
        except:
            quantit = 0
        
        add_product(nom, prix, quantit, self.csv_file)
        return True

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


def hello_world():
    webview.evaluate_js('document.getElementById("message").innerHTML = "Hello, Pywebview!"')


if __name__ == '__main__':
    csv_path = os.path.join(os.path.dirname(__file__), 'Data', 'produit.csv')

    # message initial
    content = """
        <div id="message">
        <h1>Bonjour!</h1>
        </div>
        """


    # génération du tableau HTML à partir des données lues
    content += """
    <div id="mainPage">
    <h2>Ajouter un produit</h2>
    <form id="addForm">
      <label>Nom: <input id="name" required></label>
      <label>Prix: <input id="price" type="number" step="0.01" required></label>
      <label>Quantité: <input id="quantity" type="number" required></label>
      <button type="submit">Ajouter</button>
    </form>
    <hr />
    <style>
        .product-link {
            color: black !important;
            text-decoration: none;
            cursor: pointer;
        }
        .product-link:hover {
            text-decoration: underline;
        }
    </style>
    """

    data_prod = lecture_produce('produit.csv')
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
                f'<td>{row[2]}</td>'
                f'<td>{row[3]}</td>'
                f'<td>{row[4]}</td>'
                '</tr>'
            )

    content += "</tbody></table>"
    content += "</div>"  # Ferme mainPage

    # Div pour afficher les détails du produit
    content += """
    <div id="productDetailPage" style="display:none;">
        <style>
            #productDetailPage { max-width: 600px; margin: auto; padding: 20px; }
            #chartWrapper { max-width: 50%; max-height: 50%; margin: 20px auto; }
            #myChart { width: 75% !important; height: 50% !important; }
            #backBtn { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        </style>
        <button id="backBtn">← Retour</button>
        <h1 id="productTitle"></h1>
        <div id="stats"></div>
        <div id="chartWrapper">
            <canvas id="myChart"></canvas>
        </div>
    </div>
    """

    # JS pour gérer la navigation et les diagrammes
    content += """
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
    let chart = null;

    window.addEventListener('pywebviewready', function() {
        // Gestion du formulaire d'ajout
        document.getElementById('addForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const nom = document.getElementById('name').value;
            const prix = document.getElementById('price').value;
            const quantit = document.getElementById('quantity').value;
            
            window.pywebview.api.add_product_api(nom, prix, quantit).then(() => {
                const tbody = document.getElementById('tbody');
                const tr = document.createElement('tr');
                tr.innerHTML = '<th scope="row"><a href="javascript:void(0)" class="product-link" data-product="' + nom + '">' + nom + '</a></th><td>' + prix + '</td><td>' + quantit + '</td><td>' + quantit + '</td>';
                tbody.appendChild(tr);
                document.getElementById('addForm').reset();
                attachProductLinks();
            }).catch(err => {
                console.error('Erreur :', err);
                alert('Erreur : ' + err.message);
            });
        });

        // Bouton retour
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
                <p><strong>Prix:</strong> ${stats.prix}€</p>
                <p><strong>Disponible:</strong> ${stats.disponible} / ${stats.total}</p>
                <p><strong>Pourcentage disponible:</strong> ${(stats.disponible/stats.total*100).toFixed(2)}%</p>
            `;

            // Attendre que le DOM soit prêt avant de créer le chart
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
            }, 100);
        }).catch(err => {
            console.error('Erreur:', err);
            alert('Erreur de chargement');
        });
    }
    </script>
    """

    api = Api('produit.csv')
    window = webview.create_window('Gestion produits', html=content, js_api=api)
    webview.start(hello_world, window)
