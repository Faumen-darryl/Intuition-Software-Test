from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import requests
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from bson import ObjectId




app = Flask(__name__)
app.secret_key = "your_secret_key"

# Connexion à la base de données MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['crypto_app']
users_collection = db['users']
# Initialisation de la collection alerts_collection
alerts_collection = db['alerts_collection']

# Clé API CoinAPI
coinapi_key = "12C0883C-8FC5-4153-AF3F-448D32023FA7"


# Page d'inscription
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Vérifier si l'utilisateur existe déjà
        if users_collection.find_one({'username': username}):
            return "Cet utilisateur existe déjà !"
        else:
            # Insérer l'utilisateur dans la base de données
            users_collection.insert_one({'username': username, 'password': password})
            session['username'] = username
            return redirect(url_for('index'))
    return render_template('signup.html')

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Vérifier les informations de connexion
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Nom d'utilisateur ou mot de passe incorrect !"
    return render_template('login.html')

# Page d'accueil
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))  # Rediriger vers la page de connexion

# Page de bienvenue
@app.route('/welcome')
def welcome():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    return redirect(url_for('login'))

# Déconnexion
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

previous_btc_value = None

def generate_alerts():
    global previous_btc_value
    threshold = 62200  # Seuil pour l'alerte en USD
    # Récupérer le prix actuel du BTC en USD depuis l'API CoinAPI
    response = requests.get(f"https://rest.coinapi.io/v1/exchangerate/BTC/USD?apikey={coinapi_key}")
    data = response.json()
    current_price = data['rate']
    
    # Vérifier si nous avons une valeur précédente du BTC
    if previous_btc_value is not None:
        # Comparer avec la valeur précédente pour déterminer si le prix a augmenté ou diminué
        difference = current_price - previous_btc_value
        if difference >= 0:
            alert_message = f"Le prix du Bitcoin a augmenté de {difference:.2f} USD (Ancien prix: {previous_btc_value:.2f} USD, Nouveau prix: {current_price:.2f} USD) à {datetime.datetime.now()}"
        else:
            alert_message = f"Le prix du Bitcoin a diminué de {abs(difference):.2f} USD (Ancien prix: {previous_btc_value:.2f} USD, Nouveau prix: {current_price:.2f} USD) à {datetime.datetime.now()}"
        # Stocker l'alerte dans la base de données
        alerts_collection.insert_one({'message': alert_message})
    
    # Mettre à jour la valeur précédente du BTC
    previous_btc_value = current_price

# Planifier la génération des alertes toutes les minutes
scheduler = BackgroundScheduler()
scheduler.add_job(generate_alerts, 'interval', minutes=1)
scheduler.start()


# Routes pour les services de notification de crypto-monnaie
@app.route('/create_alert_usd', methods=['GET', 'POST'])
def create_alert_usd():
    if request.method == 'POST':
        threshold = float(request.form['threshold'])
        # Récupérer le prix actuel du BTC en USD depuis l'API CoinAPI
        response = requests.get(f"https://rest.coinapi.io/v1/exchangerate/BTC/USD?apikey={coinapi_key}")
        data = response.json()
        current_price = data['rate']
        # Vérifier si le prix actuel est au-dessus ou en dessous du seuil de l'alerte
        difference = current_price - previous_btc_value
        if difference >= threshold:
            alert_message = f"Le prix du Bitcoin a augmenté de {difference:.2f} USD (Ancien prix: {previous_btc_value:.2f} USD, Nouveau prix: {current_price:.2f} USD) à {datetime.datetime.now()}"
        else:
            alert_message = f"Le prix du Bitcoin a diminué de {abs(difference):.2f} USD (Ancien prix: {previous_btc_value:.2f} USD, Nouveau prix: {current_price:.2f} USD) à {datetime.datetime.now()}"
            # Stocker l'alerte dans la base de données
            alerts_collection.insert_one({'message': alert_message})
        # Rediriger vers la page de création d'alerte avec les alertes mises à jour
        alerts = alerts_collection.find()
        return render_template('create_alert_usd.html', alerts=alerts)
    else:
        # Afficher la page de création d'alerte avec les alertes existantes
        alerts = alerts_collection.find()
        return render_template('create_alert_usd.html', alerts=alerts)


@app.route('/alert_eur')
def alert_eur():
    # Votre code ici
    pass

@app.route('/all_alerts')
def all_alerts():
    alerts = list(alerts_collection.find())
    return render_template('all_alerts.html', alerts=alerts)


@app.route('/modify_alerts')
def modify_alerts():
    # Votre code ici
    pass

@app.route('/delete_alerts', methods=['GET', 'POST'])
def delete_alerts():
    if request.method == 'POST':
        # Récupérer l'ID de l'alerte à supprimer depuis le formulaire
        alert_id = request.form['alert_id']
        # Supprimer l'alerte de la base de données
        alerts_collection.delete_one({'_id': ObjectId(alert_id)})
        # Rediriger vers la page des alertes
        return redirect(url_for('all_alerts'))
    else:
        # Récupérer toutes les alertes de la base de données
        alerts = list(alerts_collection.find())
        return render_template('delete_alerts.html', alerts=alerts)


if __name__ == '__main__':
    app.run(debug=True)
