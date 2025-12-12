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
    <h2>Ajouter un produit</h2>
    <form id="addForm">
      <label>Nom: <input id="name" required></label>
      <label>Prix: <input id="price" type="number" step="0.01" required></label>
      <label>Quantité: <input id="quantity" type="number" required></label>
      <button type="submit">Ajouter</button>
    </form>
    <hr />
    """

    data_prod = lecture_produce()
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
                f'<th scope="row">{row[1]}</th>'
                f'<td>{row[2]}</td>'
                f'<td>{row[3]}</td>'
                f'<td>{row[4]}</td>'
                '</tr>'
            )

    content += "</tbody></table>"

    # JS pour récupérer le formulaire et appeler l'API Python
    content += """
    <script>
    window.addEventListener('pywebviewready', function() {
        document.getElementById('addForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const nom = document.getElementById('name').value;
            const prix = document.getElementById('price').value;
            const quantit = document.getElementById('quantity').value;
            
            console.log('Envoi vers Python :', {nom, prix, quantit});
            
            window.pywebview.api.add_product_api(nom, prix, quantit).then(() => {
                console.log('✓ Succès');
                const tbody = document.getElementById('tbody');
                const tr = document.createElement('tr');
                tr.innerHTML = '<th scope="row">' + nom + '</th><td>' + prix + '</td><td>' + quantit + '</td><td>' + quantit + '</td>';
                tbody.appendChild(tr);
                document.getElementById('addForm').reset();
            }).catch(err => {
                console.error('✗ Erreur :', err);
                alert('Erreur : ' + err.message);
            });
        });
    });
    </script>
    """

    api = Api(csv_path)
    window = webview.create_window('Hello Pywebview', html=content, js_api=api)
    webview.start(hello_world, window)
