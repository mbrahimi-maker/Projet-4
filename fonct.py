import csv
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "Data")
PRODUIT_CSV = os.path.join(DATA_DIR, "produit.csv")
COMMANDE_CSV = os.path.join(DATA_DIR, "commande.csv")

def lire_produits_detail():
    produits = []
    with open(PRODUIT_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 5:
                continue
            pid = row[0]
            nom = row[1]
            try:
                prix = float(row[2])
            except Exception:
                prix = 0.0
            try:
                dispo = int(float(row[3]))
            except Exception:
                dispo = 0
            produits.append({
                "id": pid,
                "nom": nom,
                "prix": prix,
                "disponible": dispo
            })
    return produits

def lecture_produce(csv_file=None):
    if csv_file is None:
        csv_file = 'produit.csv'

    csv_path_arg = os.path.join(os.path.dirname(__file__), 'Data', csv_file)
    data_prod = []
    with open(csv_path_arg, 'r', newline='', encoding='utf-8') as csv_prod:
        reader = csv.reader(csv_prod)
        for row in reader:
            data_prod.append(row)
    return data_prod