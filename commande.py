import webview
import csv
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "Data")
PRODUIT_CSV = os.path.join(DATA_DIR, "produit.csv")
COMMANDE_CSV = os.path.join(DATA_DIR, "commande.csv")


def lire_produits():
    produits = []
    with open(PRODUIT_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
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


def enregistrer_commande(lignes):
    fichier_existe = os.path.exists(COMMANDE_CSV)
    next_id = 1
    if fichier_existe:
        with open(COMMANDE_CSV, "r", newline="", encoding="utf-8") as fr:
            r = csv.reader(fr)
            next(r, None)
            for last in r:
                if last and last[0].isdigit():
                    next_id = int(last[0]) + 1

    with open(COMMANDE_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not fichier_existe:
            writer.writerow(["id_commande", "nom_produit", "quantite", "prix_unitaire", "total_ligne"])
        for ligne in lignes:
            writer.writerow([
                str(next_id),
                ligne["nom"],
                str(ligne["quantite"]),
                f"{ligne['prix']:.2f}",
                f"{ligne['total']:.2f}"
            ])
            next_id += 1


def mettre_a_jour_stock(panier):
    rows = []
    with open(PRODUIT_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header:
            rows.append(header)
        for row in reader:
            if len(row) < 5:
                rows.append(row)
                continue
            nom = row[1]
            try:
                dispo = float(row[3])
            except Exception:
                dispo = 0
            cmd = next((p for p in panier if p["nom"] == nom), None)
            if cmd:
                q = cmd["quantite"]
                nouveau_dispo = max(0, dispo - q)
                row[3] = str(nouveau_dispo)
            rows.append(row)

    with open(PRODUIT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


class ApiCommande:
    def __init__(self):
        self.produits = lire_produits()

    def get_products(self):
        return self.produits

    def valider_commande(self, panier):
        lignes = []
        for item in panier:
            try:
                nom = item["nom"]
                quantite = int(item["quantite"])
                prix = float(item["prix"])
            except Exception:
                continue
            if quantite <= 0:
                continue
            total = prix * quantite
            lignes.append({"nom": nom, "quantite": quantite, "prix": prix, "total": total})
        if lignes:
            enregistrer_commande(lignes)
            mettre_a_jour_stock(lignes)
        return True
    
    def page(self):
        produits = lire_produits()

        content = """
    <html>
    <head>
    <meta charset="utf-8">
    <title>Validation de commande</title>
    <style>
        :root {
            --bg: #f2f4ff;
            --card: #ffffff;
            --primary: #6366f1;
            --primary-soft: #e0e7ff;
            --accent: #0ea5e9;
            --accent-soft: #cffafe;
            --text-main: #0f172a;
            --text-muted: #6b7280;
            --border-soft: #e2e8f0;
            --danger-soft: #fee2e2;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: radial-gradient(circle at top left, #eef2ff, #e0f2fe);
            color: var(--text-main);
            padding: 24px;
        }
        #shell {
            max-width: 1120px;
            margin: 0 auto;
        }
        #header {
            margin-bottom: 18px;
        }
        #header h1 {
            font-size: 26px;
            font-weight: 650;
        }
        #header h1 span {
            color: var(--primary);
        }
        #subtitle {
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 4px;
        }
        #layout {
            display: grid;
            grid-template-columns: 3fr 2fr;
            gap: 20px;
            align-items: flex-start;
        }
        .card {
            background: var(--card);
            border-radius: 16px;
            border: 1px solid var(--border-soft);
            box-shadow: 0 16px 40px rgba(148,163,184,0.35);
            padding: 18px 18px 20px;
        }
        .card h2 {
            font-size: 18px;
            margin-bottom: 6px;
        }
        .card small {
            font-size: 12px;
            color: var(--text-muted);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-top: 10px;
        }
        thead {
            background: var(--primary-soft);
        }
        th, td {
            padding: 7px 8px;
            border-bottom: 1px solid #edf2f7;
            text-align: left;
        }
        thead th {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #4b5563;
        }
        tbody tr:last-child td { border-bottom: none; }
        tbody tr:nth-child(even) { background: #f9fafb; }
        tbody tr:hover { background: #eef2ff; }
        .qty-input {
            width: 60px;
            padding: 4px 6px;
            border-radius: 8px;
            border: 1px solid var(--border-soft);
            background: #f9fbff;
            text-align: right;
            font-size: 13px;
        }
        .btn-line {
            padding: 4px 10px;
            border-radius: 999px;
            border: 1px solid var(--accent);
            background: #ecfeff;
            color: #0369a1;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.1s, color 0.1s, transform 0.05s, box-shadow 0.05s;
        }
        .btn-line:hover {
            background: var(--accent);
            color: #ffffff;
            transform: translateY(-1px);
            box-shadow: 0 6px 14px rgba(56,189,248,0.4);
        }
        .badge-dispo {
            font-size: 11px;
            padding: 2px 7px;
            border-radius: 999px;
            background: var(--accent-soft);
            color: #0369a1;
        }
        #summaryHeader {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        #summaryHeader span {
            font-size: 12px;
            color: var(--text-muted);
        }
        #panierListe {
            list-style: none;
            margin-top: 6px;
            max-height: 260px;
            overflow-y: auto;
        }
        #panierListe li {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 8px;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px dashed #d7dde8;
            font-size: 13px;
        }
        #panierListe li:last-child { border-bottom: none; }
        .ligne-nom {
            font-weight: 500;
        }
        .ligne-qte {
            font-size: 12px;
            color: var(--text-muted);
        }
        .ligne-total {
            font-weight: 600;
        }
        #emptyMsg {
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 4px;
        }
        #totalBloc {
            margin-top: 12px;
            border-top: 1px solid #e5e7eb;
            padding-top: 10px;
            font-size: 14px;
        }
        #totalLignes {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
        }
        #frais {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-muted);
        }
        #totalGlobal {
            margin-top: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 15px;
            font-weight: 650;
            color: var(--primary);
        }
        #totalGlobal span:last-child {
            font-size: 18px;
        }
        .badge-free {
            font-size: 11px;
            padding: 2px 7px;
            border-radius: 999px;
            background: #dcfce7;
            color: #15803d;
        }
        .btn-primary {
            margin-top: 12px;
            width: 100%;
            padding: 10px 14px;
            border-radius: 999px;
            border: none;
            cursor: pointer;
            background: linear-gradient(135deg, var(--primary), #a855f7);
            color: #ffffff;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 14px 32px rgba(129,140,248,0.6);
            transition: transform 0.08s, box-shadow 0.08s;
        }
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 18px 40px rgba(129,140,248,0.7);
        }
        .btn-primary:active {
            transform: translateY(0);
            box-shadow: 0 8px 18px rgba(129,140,248,0.6);
        }
        @media (max-width: 900px) {
            #layout { grid-template-columns: 1fr; }
        }
    </style>
    </head>
    <body>
    <div id="shell">
    <div id="header">
        <h1>Valider votre <span>commande</span></h1>
        <p id="subtitle">Ajoutez les produits au récapitulatif, vérifiez le total puis confirmez.</p>
    </div>

    <div id="layout">
        <div class="card">
        <h2>Catalogue</h2>
        <small>Choisissez les quantités à ajouter au panier.</small>
        <table>
            <thead>
            <tr>
                <th>Produit</th>
                <th>Prix</th>
                <th>Stock</th>
                <th>Qté</th>
                <th></th>
            </tr>
            </thead>
            <tbody id="tbodyProduits">
    """

        for p in produits:
            content += f"""
            <tr data-nom="{p['nom']}" data-prix="{p['prix']:.2f}">
                <td>{p['nom']}</td>
                <td>{p['prix']:.2f} €</td>
                <td><span class="badge-dispo">{p['disponible']} dispo</span></td>
                <td><input type="number" min="1" max="{p['disponible']}" value="1" class="qty-input"></td>
                <td><button class="btn-line">Ajouter</button></td>
            </tr>
    """

        content += """
            </tbody>
        </table>
        </div>

        <div class="card">
        <div id="summaryHeader">
            <div>
            <h2>Récapitulatif</h2>
            <span id="emptyMsg">Aucun article dans le panier.</span>
            </div>
            <span>Commande locale</span>
        </div>

        <ul id="panierListe"></ul>

        <div id="totalBloc">
            <div id="totalLignes">
            <span>Sous-total</span>
            <span id="sousTotal">0.00 €</span>
            </div>
            <div id="frais">
            <span>Frais de préparation</span>
            <span><span class="badge-free">Offerts</span></span>
            </div>
            <div id="totalGlobal">
            <span>Total à payer</span>
            <span id="totalGlobalValeur">0.00 €</span>
            </div>
        </div>

        <button id="validerBtn" class="btn-primary">Confirmer la commande</button>
        </div>
    </div>
    </div>

    <script>
    let panier = [];

    function majAffichagePanier() {
        const liste = document.getElementById('panierListe');
        const empty = document.getElementById('emptyMsg');
        const sousTotalElt = document.getElementById('sousTotal');
        const totalGlobalElt = document.getElementById('totalGlobalValeur');

        liste.innerHTML = '';

        if (panier.length === 0) {
            empty.style.display = 'inline';
            sousTotalElt.textContent = '0.00 €';
            totalGlobalElt.textContent = '0.00 €';
            return;
        }

        empty.style.display = 'none';

        let totalGlobal = 0;
        panier.forEach(item => {
            const li = document.createElement('li');
            const totalLigne = (item.quantite * item.prix);
            totalGlobal += totalLigne;
            li.innerHTML =
                '<div>' +
                '<div class="ligne-nom">' + item.nom + '</div>' +
                '<div class="ligne-qte">Qté ' + item.quantite + ' · ' + item.prix.toFixed(2) + ' €</div>' +
                '</div>' +
                '<div class="ligne-total">' + totalLigne.toFixed(2) + ' €</div>';
            liste.appendChild(li);
        });

        sousTotalElt.textContent = totalGlobal.toFixed(2) + ' €';
        totalGlobalElt.textContent = totalGlobal.toFixed(2) + ' €';
    }

    document.querySelectorAll('#tbodyProduits tr').forEach(tr => {
        const btn = tr.querySelector('.btn-line');
        const input = tr.querySelector('.qty-input');
        const nom = tr.getAttribute('data-nom');
        const prix = parseFloat(tr.getAttribute('data-prix'));

        btn.addEventListener('click', () => {
            const qte = parseInt(input.value || '0', 10);
            const max = parseInt(input.max || '0', 10);
            if (isNaN(qte) || qte <= 0) return;
            if (max > 0 && qte > max) {
                alert('Quantité supérieure au stock disponible.');
                return;
            }

            const exist = panier.find(p => p.nom === nom);
            if (exist) {
                if (exist.quantite + qte > max) {
                    alert('Quantité totale supérieure au stock disponible.');
                    return;
                }
                exist.quantite += qte;
            } else {
                panier.push({ nom: nom, quantite: qte, prix: prix });
            }
            majAffichagePanier();
        });
    });

    document.getElementById('validerBtn').addEventListener('click', () => {
        if (panier.length === 0) {
            alert('Panier vide.');
            return;
        }
        window.pywebview.api.valider_commande(panier).then(() => {
            panier.forEach(item => {
                const rows = document.querySelectorAll('#tbodyProduits tr');
                rows.forEach(tr => {
                    const nom = tr.getAttribute('data-nom');
                    if (nom === item.nom) {
                        const badge = tr.querySelector('.badge-dispo');
                        const input = tr.querySelector('.qty-input');
                        if (!badge) return;

                        const parts = badge.textContent.split(' ');
                        let actuel = parseInt(parts[0] || '0', 10);
                        if (isNaN(actuel)) actuel = 0;

                        const nouveau = Math.max(0, actuel - item.quantite);
                        badge.textContent = nouveau + ' dispo';
                        input.max = nouveau;
                        if (parseInt(input.value || '0', 10) > nouveau) {
                            input.value = nouveau > 0 ? nouveau : 1;
                        }
                    }
                });
            });

            alert('Commande confirmée.');
            panier = [];
            majAffichagePanier();
        }).catch(err => {
            console.error(err);
            alert('Erreur lors de la validation.');
        });
    });
    </script>
    </body>
    </html>
    """
        return content


if __name__ == "__main__":
    

    api = ApiCommande()
    content = ApiCommande.page()
    window = webview.create_window("Validation de commande", html=content, js_api=api)
    webview.start()
