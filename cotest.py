import webview
import csv
import os
import hashlib
import re
import subprocess
import sys
from fonction import fct as ApiFonction
from checkmypass import main


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

    def register(self, identifiant, password, email, user_type):
        try:
            if not identifiant or not password or not email or not user_type:
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

            if(main(password)):
                self.api_fonction.add_api(identifiant, hashed_password, email, user_type)
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

            if verify_user(identifiant, password, self.csv_file):
                # Connexion réussie - lancer liste produit.py
                self.launch_product_list()
                return {'success': True, 'message': 'Connexion réussie ! Redirection...'}
            else:
                return {'success': False, 'message': 'Identifiant ou mot de passe incorrect'}
        except Exception as e:
            print("Erreur login:", e)
            return {'success': False, 'message': 'Erreur interne lors de la connexion'}

    def launch_product_list(self):
        """Lance liste produit.py et ferme la fenêtre de connexion"""
        try:
            # Chemin vers liste produit.py
            product_list_path = os.path.join(os.path.dirname(__file__), 'liste produit.py')
            
            # Lancer le fichier dans un nouveau processus
            if sys.platform == 'win32':
                subprocess.Popen([sys.executable, product_list_path], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, product_list_path])
            
            # Fermer la fenêtre de connexion après un court délai
            if self.window:
                import threading
                def close_window():
                    import time
                    time.sleep(1)  # Attendre 1 seconde pour que l'utilisateur voie le message
                    self.window.destroy()
                
                threading.Thread(target=close_window, daemon=True).start()
        except Exception as e:
            print(f"Erreur lors du lancement de liste produit.py: {e}")

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
            button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin-top: 10px; transition: background 0.3s; }
            button:hover { background: #764ba2; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .toggle-link { text-align: center; margin-top: 20px; }
            .toggle-link a { color: #667eea; cursor: pointer; text-decoration: none; font-weight: bold; }
            .toggle-link a:hover { text-decoration: underline; }
            .message { padding: 12px; border-radius: 5px; margin-bottom: 20px; display: none; }
            .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            h2 { margin-bottom: 30px; color: #333; }
            #backBtn { width: auto; background: #6c757d; margin-bottom: 20px; }
            #backBtn:hover { background: #5a6268; }
            .loading-spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid #fff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 0.6s linear infinite; margin-left: 8px; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
                    <button type="submit" id="loginBtn">Se connecter</button>
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
                    <div class="form-group">
                        <label>Type de compte:</label>
                        <div class="radio-group">
                            <label>
                                <input type="radio" name="userType" value="vendeur" required>
                                Vendeur
                            </label>
                            <label>
                                <input type="radio" name="userType" value="acheteur" required>
                                Acheteur
                            </label>
                        </div>
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
                const loginBtn = document.getElementById('loginBtn');

                // Désactiver le bouton et afficher un spinner
                loginBtn.disabled = true;
                loginBtn.innerHTML = 'Connexion en cours<span class="loading-spinner"></span>';

                window.pywebview.api.login(identifiant, password).then(result => {
                    showMessage(result.message, result.success ? 'success' : 'error');
                    if (result.success) {
                        document.getElementById('loginFormElement').reset();
                        // La fenêtre se fermera automatiquement après 1 seconde
                    } else {
                        // Réactiver le bouton en cas d'échec
                        loginBtn.disabled = false;
                        loginBtn.innerHTML = 'Se connecter';
                    }
                }).catch(err => {
                    console.error('Erreur login JS:', err);
                    showMessage('Erreur de connexion', 'error');
                    loginBtn.disabled = false;
                    loginBtn.innerHTML = 'Se connecter';
                });
            });

            // Inscription
            document.getElementById('registerFormElement').addEventListener('submit', function(e) {
                e.preventDefault();
                const identifiant = document.getElementById('registerIdentifiant').value;
                const password = document.getElementById('registerPassword').value;
                const email = document.getElementById('registerEmail').value;
                const userTypeRadio = document.querySelector('input[name="userType"]:checked');

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


if __name__ == '__main__':
    html = create_auth_page()
    api = Api('user.csv')
    window = webview.create_window('Connexion / Inscription', html=html, js_api=api)
    api.window = window
    webview.start(debug=True)