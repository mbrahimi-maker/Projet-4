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

    def get_product_stats(self, nom):
        """Retourne les stats d'un produit pour le diagramme"""
        data_prod = self.lire_produce(self.csv_file)
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
    
    def lire_produce(self, csv_file=None):
        if csv_file is None:
            csv_file = 'produit.csv'
        csv_path_arg = os.path.join(os.path.dirname(__file__), 'Data', csv_file)
        data_prod = []
        with open(csv_path_arg, 'r', newline='', encoding='utf-8') as csv_prod:
            reader = csv.DictReader(csv_prod)
            for row in reader:
                data_prod.append(row)
        return data_prod

