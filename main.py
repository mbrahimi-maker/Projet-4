import webview
import csv
import os
import hashlib
import re
from datetime import datetime
from fonction import fct as ApiFonction
from checkmypass import check as check

conenxion = None
produit = None

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


def enregistrer_commande(lignes, id_user=1):
    """Enregistre les commandes avec le format: id_prod,id_user,quantite,date_commande"""
    fichier_existe = os.path.exists(COMMANDE_CSV)
    date_commande = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(COMMANDE_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not fichier_existe:
            writer.writerow(["id_prod", "id_user", "quantite", "date_commande"])
        
        for ligne in lignes:
            writer.writerow([
                ligne["id_prod"],
                str(id_user),
                str(ligne["quantite"]),
                date_commande
            ])


def mettre_a_jour_stock(panier):
    """Met à jour le stock disponible après validation de commande"""
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
            
            pid = row[0]
            try:
                dispo = float(row[3])
            except Exception:
                dispo = 0
            
            # Chercher si ce produit est dans le panier
            cmd = next((p for p in panier if str(p["id_prod"]) == str(pid)), None)
            if cmd:
                q = cmd["quantite"]
                nouveau_dispo = max(0, dispo - q)
                row[3] = str(int(nouveau_dispo))
            rows.append(row)

    with open(PRODUIT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def lecture_users(csv_file='user.csv'):
    csv_path = os.path.join(os.path.dirname(__file__), 'Data', csv_file)
    users = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                users.append(row)
    return users


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def verify_user(identifiant, password, csv_file='user.csv'):
    users = lecture_users(csv_file)
    hashed_password = hash_password(password)

    for user in users[1:]:
        if len(user) >= 3 and user[1].lower() == identifiant.lower() and user[2] == hashed_password:
            return True
    return False


class Api:
    global connexion, produit
    def __init__(self, csv_file='user.csv', window=None):
        self.csv_file = csv_file
        self.window = window
        self.api_fonction = ApiFonction(csv_file)
        self.id_user = None

    def get_products(self):
        return self.produits

    def valider_commande(self, panier):
        """Valide la commande et met à jour le stock"""
        lignes = []
        for item in panier:
            try:
                id_prod = item["id_prod"]
                quantite = int(item["quantite"])
            except Exception:
                continue
            if quantite <= 0:
                continue
            lignes.append({
                "id_prod": id_prod,
                "quantite": quantite
            })
        
        if lignes:
            enregistrer_commande(lignes, self.id_user)
            mettre_a_jour_stock(lignes)
            return {"success": True, "message": "Commande validée avec succès"}
        
        return {"success": False, "message": "Panier vide"}

    def register(self, identifiant, password, email, user_type):
        try:
            if not identifiant or not password or not email:
                return {'success': False, 'message': 'Tous les champs sont requis'}

            if len(identifiant) < 3:
                return {'success': False, 'message': "L'identifiant doit contenir au moins 3 caractères"}

            if len(password) < 6:
                return {'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}

            if not is_valid_email(email):
                return {'success': False, 'message': 'Email invalide'}

            users = lecture_users(self.csv_file)

            for user in users[1:]:
                if len(user) >= 2 and user[1].lower() == identifiant.lower():
                    return {'success': False, 'message': 'Cet identifiant existe déjà'}

            for user in users[1:]:
                if len(user) >= 4 and user[3].lower() == email.lower():
                    return {'success': False, 'message': 'Cet email est déjà utilisé'}
            hashed_password = hash_password(password)
            chec = check()
            if(chec.main(password)):
                self.api_fonction.add_api(identifiant, hashed_password, email, 'acheteur', 2)
                return {'success': True, 'message': "Inscription réussie ! Vous pouvez maintenant vous connecter."}
            else:
                return {'success': False, 'message': "Erreur mot de passe compromis, choisissez-en un autre."}
        except Exception as e:
            print("Erreur register:", e)
            return {'success': False, 'message': "Erreur lors de l'inscription"}

    def login(self, identifiant, password):
        try:
            if not identifiant or not password:
                return {'success': False, 'message': 'Tous les champs sont requis'}

            users = lecture_users("user.csv")
            hashed_password = hash_password(password)

            for user in users[1:]:
                if len(user) >= 3 and user[1].lower() == identifiant.lower() and user[2] == hashed_password:
                    if user[4] == 'vendeur':
                        pass
                    elif user[4] == 'acheteur':
                        id_user = user[0]
                        self.window.load_html(pagebuy())
                    else:
                        pass   
                    
                    return {'success': True, 'message': 'Connexion réussie !'}
                
            return {'success': False, 'message': 'Identifiant ou mot de passe incorrect'}
        except Exception as e:
            print("Erreur login:", e)
            return {'success': False, 'message': 'Erreur interne lors de la connexion'}

    def show_login(self):
        try:
            if not self.window:
                print("show_login: window est None")
                return False
            self.window.evaluate_js("""
                document.getElementById('loginPage').style.display = 'block';
                document.getElementById('registerPage').style.display = 'none';
                document.getElementById('message').style.display = 'none';
            """)
            return True
        except Exception as e:
            print("Erreur show_login:", e)
            return False

    def show_register(self):
        try:
            if not self.window:
                print("show_register: window est None")
                return False
            self.window.evaluate_js("""
                document.getElementById('loginPage').style.display = 'none';
                document.getElementById('registerPage').style.display = 'block';
                document.getElementById('message').style.display = 'none';
            """)
            return True
        except Exception as e:
            print("Erreur show_register:", e)
            return False



def pagebuy():

    produits = ApiFonction()
    produits = produits.lire_produce('produit.csv')

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
        .btn-remove {
            padding: 2px 8px;
            border-radius: 6px;
            border: none;
            background: var(--danger-soft);
            color: #991b1b;
            font-size: 11px;
            cursor: pointer;
            margin-left: 8px;
            transition: all 0.15s;
        }
        .btn-remove:hover {
            background: #fecaca;
            transform: scale(1.05);
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
        content += '<tr data-id="'{p['id']}'" data-nom="'{p['Nom']}'" data-prix="'{p['Prix']:.2f}'" data-dispo="'{p['Disponible']}'"><td>{p['Nom']}</td>
+'<td>'{p['Prix']:.2f}' €</td>'
+'<td><span class="badge-dispo">'{p['Disponible']}' dispo</span></td>'
+'<td><input type="number" min="1" max="'{p['Disponible']}'" value="1" class="qty-input" '{"disabled" if p['Disponible'] <= 0 else ""}'></td>'
+'<td><button class="btn-line" '{"disabled" if p['Disponible'] <= 0 else ""}'>'{"Épuisé" if p['Disponible'] <= 0 else "Ajouter"}'</button></td>'
+'</tr>'

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
        panier.forEach((item, index) => {
            const li = document.createElement('li');
            const totalLigne = (item.quantite * item.prix);
            totalGlobal += totalLigne;
            li.innerHTML =
                '<div>' +
                '<div class="ligne-nom">' + item.nom + '</div>' +
                '<div class="ligne-qte">Qté ' + item.quantite + ' · ' + item.prix.toFixed(2) + ' €</div>' +
                '</div>' +
                '<div>' +
                '<span class="ligne-total">' + totalLigne.toFixed(2) + ' €</span>' +
                '<button class="btn-remove" onclick="retirerDuPanier(' + index + ')">×</button>' +
                '</div>';
            liste.appendChild(li);
        });

        sousTotalElt.textContent = totalGlobal.toFixed(2) + ' €';
        totalGlobalElt.textContent = totalGlobal.toFixed(2) + ' €';
    }

    function retirerDuPanier(index) {
        panier.splice(index, 1);
        majAffichagePanier();
    }

    document.querySelectorAll('#tbodyProduits tr').forEach(tr => {
        const btn = tr.querySelector('.btn-line');
        const input = tr.querySelector('.qty-input');
        const id = tr.getAttribute('data-id');
        const nom = tr.getAttribute('data-nom');
        const prix = parseFloat(tr.getAttribute('data-prix'));
        const maxDispo = parseInt(tr.getAttribute('data-dispo') || '0', 10);

        if (!btn || maxDispo <= 0) return;

        btn.addEventListener('click', () => {
            const qte = parseInt(input.value || '0', 10);
            if (isNaN(qte) || qte <= 0) return;
            
            // Calculer la quantité déjà dans le panier pour ce produit
            const exist = panier.find(p => p.id_prod === id);
            const qteActuellePanier = exist ? exist.quantite : 0;
            
            if (qteActuellePanier + qte > maxDispo) {
                alert('Quantité totale supérieure au stock disponible (Stock: ' + maxDispo + ', Déjà dans panier: ' + qteActuellePanier + ')');
                return;
            }

            if (exist) {
                exist.quantite += qte;
            } else {
                panier.push({ 
                    id_prod: id, 
                    nom: nom, 
                    quantite: qte, 
                    prix: prix 
                });
            }
            majAffichagePanier();
        });
    });

    document.getElementById('validerBtn').addEventListener('click', () => {
        if (panier.length === 0) {
            alert('Panier vide.');
            return;
        }
        
        const panierPourApi = panier.map(item => ({
            id_prod: item.id_prod,
            quantite: item.quantite
        }));
        
        window.pywebview.api.valider_commande(panierPourApi).then(result => {
            if (result.success) {
                // Mettre à jour l'affichage des stocks
                panier.forEach(item => {
                    const rows = document.querySelectorAll('#tbodyProduits tr');
                    rows.forEach(tr => {
                        const id = tr.getAttribute('data-id');
                        if (id === item.id_prod) {
                            const badge = tr.querySelector('.badge-dispo');
                            const input = tr.querySelector('.qty-input');
                            const btn = tr.querySelector('.btn-line');
                            if (!badge) return;

                            const actuel = parseInt(tr.getAttribute('data-dispo') || '0', 10);
                            const nouveau = Math.max(0, actuel - item.quantite);
                            
                            badge.textContent = nouveau + ' dispo';
                            tr.setAttribute('data-dispo', nouveau);
                            input.max = nouveau;
                            
                            if (nouveau <= 0) {
                                input.disabled = true;
                                btn.disabled = true;
                                btn.textContent = 'Épuisé';
                                input.value = 1;
                            } else if (parseInt(input.value || '0', 10) > nouveau) {
                                input.value = nouveau;
                            }
                        }
                    });
                });

                alert('Commande confirmée avec succès !');
                panier = [];
                majAffichagePanier();
            } else {
                alert('Erreur: ' + result.message);
            }
        }).catch(err => {
            console.error(err);
            alert('Erreur lors de la validation.');
        });
    });
    </script>
    </body>
    </html>"""
    return content


def create_auth_page():
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Connexion / Inscription</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
            .container { background: white; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 100%; max-width: 400px; padding: 40px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
            input[type="text"], input[type="password"], input[type="email"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
            input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 5px rgba(102, 126, 234, 0.5); }
            .radio-group { display: flex; gap: 20px; margin-top: 10px; }
            .radio-group label { margin-bottom: 0; display: flex; align-items: center; }
            .radio-group input[type="radio"] { margin-right: 5px; width: auto; }
            button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin-top: 10px; }
            button:hover { background: #764ba2; }
            .toggle-link { text-align: center; margin-top: 20px; }
            .toggle-link a { color: #667eea; cursor: pointer; text-decoration: none; font-weight: bold; }
            .toggle-link a:hover { text-decoration: underline; }
            .message { padding: 12px; border-radius: 5px; margin-bottom: 20px; display: none; }
            .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            h2 { margin-bottom: 30px; color: #333; }
            #backBtn { width: auto; background: #6c757d; margin-bottom: 20px; }
            #backBtn:hover { background: #5a6268; }
        </style>
    </head>
    <body>
        <div class="container">
            <div id="message" class="message"></div>
            
            <!-- Page de connexion -->
            <div id="loginPage">
                <h2>Connexion</h2>
                <form id="loginFormElement">
                    <div class="form-group">
                        <label for="loginIdentifiant">Identifiant:</label>
                        <input type="text" id="loginIdentifiant" required>
                    </div>
                    <div class="form-group">
                        <label for="loginPassword">Mot de passe:</label>
                        <input type="password" id="loginPassword" required>
                    </div>
                    <button type="submit">Se connecter</button>
                </form>
                <div class="toggle-link">
                    Pas de compte ? <a onclick="window.pywebview.api.show_register()">S'inscrire</a>
                </div>
            </div>
            
            <!-- Page d'inscription -->
            <div id="registerPage" style="display:none;">
                <button id="backBtn" onclick="window.pywebview.api.show_login()">← Retour</button>
                <h2>Inscription</h2>
                <form id="registerFormElement">
                    <div class="form-group">
                        <label for="registerIdentifiant">Identifiant:</label>
                        <input type="text" id="registerIdentifiant" required>
                    </div>
                    <div class="form-group">
                        <label for="registerEmail">Email:</label>
                        <input type="email" id="registerEmail" required>
                    </div>
                    <div class="form-group">
                        <label for="registerPassword">Mot de passe:</label>
                        <input type="password" id="registerPassword" required>
                    </div>
                    <button type="submit">S'inscrire</button>
                </form>
            </div>
        </div>
        
        <script>
        function showMessage(message, type) {
            const msgDiv = document.getElementById('message');
            msgDiv.textContent = message;
            msgDiv.className = 'message ' + type;
            msgDiv.style.display = 'block';
        }

        window.addEventListener('pywebviewready', function() {
            console.log('pywebviewready, api =', window.pywebview && window.pywebview.api);

            // Connexion
            document.getElementById('loginFormElement').addEventListener('submit', function(e) {
                e.preventDefault();
                const identifiant = document.getElementById('loginIdentifiant').value;
                const password = document.getElementById('loginPassword').value;

                window.pywebview.api.login(identifiant, password).then(result => {
                    showMessage(result.message, result.success ? 'success' : 'error');
                    if (result.success) {
                        document.getElementById('loginFormElement').reset();
                    }
                }).catch(err => {
                    console.error('Erreur login JS:', err);
                    showMessage('Erreur de connexion', 'error');
                });
            });

            // Inscription
            document.getElementById('registerFormElement').addEventListener('submit', function(e) {
                e.preventDefault();
                const identifiant = document.getElementById('registerIdentifiant').value;
                const password = document.getElementById('registerPassword').value;
                const email = document.getElementById('registerEmail').value;
                const userTypeRadio = "acheteur";

                if (!userTypeRadio) {
                    showMessage('Veuillez sélectionner un type de compte', 'error');
                    return;
                }

                const userType = userTypeRadio.value;

                window.pywebview.api.register(identifiant, password, email, userType).then(result => {
                    showMessage(result.message, result.success ? 'success' : 'error');
                    if (result.success) {
                        document.getElementById('registerFormElement').reset();
                        document.querySelectorAll('input[name="userType"]').forEach(radio => radio.checked = false);
                        // Retour automatique vers la connexion après 2s
                        setTimeout(() => window.pywebview.api.show_login(), 2000);
                    }
                }).catch(err => {
                    console.error("Erreur inscription JS:", err);
                    showMessage("Erreur lors de l'inscription", 'error');
                });
            });
        });
        </script>
    </body>
    </html>
    """
    return content
def pagevend(self):
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

if __name__ == '__main__':
    html = create_auth_page()
    api = Api('user.csv')
    connexion = webview.create_window('Connexion / Inscription', html=html, js_api=api)
    api.window = connexion
    webview.start(api)
    api.window.load_html(pagebuy())
