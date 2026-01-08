import csv
import os




def add(nom, prix, quantit, total=None ,csv_file=None):
    """Ajoute un nouveau produit
    
    Args:
        nom: Nom du produit
        prix: Prix du produit
        quantit: Quantité du produit
        csv_file: Nom du fichier CSV (ex: 'produit.csv')
    """
    if total is None:
        total = quantit

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
                total_existing = row[4]
                data_prod.append([id0, name, price, quantity, total_existing])
        
        # Déterminer le prochain ID - DÉPLACER CETTE PARTIE
        next_id = 1
        if len(data_prod) > 1:
            try:
                last_id = int(data_prod[-1][0])
                next_id = last_id + 1
            except:
                next_id = len(data_prod)
        
        data_prod.append([str(next_id), nom, str(prix), str(quantit), str(total)])

    # Réécrire
    with open(csv_path_arg, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data_prod)

def add_user(nom, passw, mail , typ, salt, csv_file=None):
    """Ajoute un nouveau produit
    
    Args:
        nom: Nom du produit
        prix: Prix du produit
        quantit: Quantité du produit
        csv_file: Nom du fichier CSV (ex: 'produit.csv')
    """
    if csv_file is None:
        csv_file = 'user.csv'
    
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
                data_prod.append(row)

        # Déterminer le prochain ID - DÉPLACER CETTE PARTIE
        next_id = 1
        if len(data_prod) > 1:
            try:
                last_id = int(data_prod[-1][0])
                next_id = last_id + 1
            except:
                next_id = len(data_prod)
        
        data_prod.append([str(next_id), nom, passw, salt, mail, typ])

    # Réécrire
    with open(csv_path_arg, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data_prod)

class fct:
    def __init__(self, csv_file='produit.csv'):
        self.csv_file = csv_file

    def add_api(self, a, b, c, d=None, e=None, f=None):
        """Récupère les champs du formulaire et appelle add_product"""

        if e is None:
            add(a, b, c, d, self.csv_file)
        elif f != None:
            add_user(a, b, c, e, f, self.csv_file)
        return True

