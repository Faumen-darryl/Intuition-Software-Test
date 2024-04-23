import requests
import time
from datetime import datetime

class BitcoinPriceService:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_price(self, currency):
        url = f"https://rest.coinapi.io/v1/exchangerate/BTC/{currency}"
        headers = {"X-CoinAPI-Key": self.api_key}
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['rate']

class AlertStorage:
    def __init__(self, filename):
        self.filename = filename

    def save_alert(self, alert):
        with open(self.filename, "a") as file:
            file.write(alert + '\n')

    def delete_alert(self, alert_index):
        with open(self.filename, "r") as file:
            alerts = file.readlines()
        del alerts[alert_index]
        with open(self.filename, "w") as file:
            file.writelines(alerts)

    def display_alerts(self):
        try:
            with open(self.filename, "r") as file:
                alerts = file.readlines()
                for index, alert in enumerate(alerts):
                    print(f"{index + 1}: {alert.strip()}")
        except FileNotFoundError:
            print("Aucune alerte n'a été enregistrée.")

class AlertService:
    def __init__(self, bitcoin_price_service, alert_storage):
        self.bitcoin_price_service = bitcoin_price_service
        self.alert_storage = alert_storage

    def create_alert(self, currency, value_change):
        previous_price = self.bitcoin_price_service.get_price(currency)
        while True:
            try:
                bitcoin_price = self.bitcoin_price_service.get_price(currency)
                price_change = bitcoin_price - previous_price
                if price_change >= value_change:
                    alert_message = f"Alerte : Le prix du Bitcoin a augmenté de {price_change:.2f} {currency} (Ancien prix: {previous_price:.2f} {currency}, Nouveau prix: {bitcoin_price:.2f} {currency}) à {datetime.now()}"
                    print(alert_message)
                    self.alert_storage.save_alert(alert_message)
                    previous_price = bitcoin_price
                elif price_change <= -value_change:
                    alert_message = f"Alerte : Le prix du Bitcoin a diminué de {-price_change:.2f} {currency} (Ancien prix: {previous_price:.2f} {currency}, Nouveau prix: {bitcoin_price:.2f} {currency}) à {datetime.now()}"
                    print(alert_message)
                    self.alert_storage.save_alert(alert_message)
                    previous_price = bitcoin_price
                time.sleep(60)
            except Exception as e:
                print("Une erreur s'est produite :", e)

class AlertManagement:
    def __init__(self, alert_storage):
        self.alert_storage = alert_storage

    def modify_value(self):
        try:
            new_value = float(input("Entrez la nouvelle valeur en USD pour laquelle vous souhaitez être alerté lors de l'augmentation/diminution du BTC : "))
            print("Nouvelles alertes générées avec succès avec la nouvelle valeur.")
            return new_value
        except ValueError:
            print("Veuillez entrer une valeur valide.")

    def delete_alert(self):
        try:
            self.alert_storage.display_alerts()
            alert_index = int(input("Entrez le numéro de l'alerte que vous souhaitez supprimer : ")) - 1
            self.alert_storage.delete_alert(alert_index)
            print("L'alerte a été supprimée avec succès.")
        except (IndexError, ValueError):
            print("Veuillez entrer un numéro d'alerte valide.")

if __name__ == "__main__":
    bitcoin_price_service = BitcoinPriceService("12C0883C-8FC5-4153-AF3F-448D32023FA7")
    alert_storage = AlertStorage("mes_alertes.txt")
    alert_service = AlertService(bitcoin_price_service, alert_storage)
    alert_management = AlertManagement(alert_storage)
    
    while True:
        print("Saisir 1 pour créer une alerte (USD)")
        print("Saisir 2 pour afficher toutes les alertes") 
        print("Saisir 3 pour modifier la valeur des alertes (USD)") 
        print("Saisir 4 pour supprimer une alerte") 
        print("Saisir 5 pour créer une alerte (EUR)")
        print("Saisir q pour quitter")
        choice = input("Veuillez saisir votre choix : ")

        if choice == "1":
            value_usd = float(input("Entrez la valeur en USD pour laquelle vous souhaitez être alerté lors de l'augmentation/diminution du BTC: "))
            print("Attendez que les alertes se déclenchent ...")
            alert_service.create_alert("USD", value_usd)
        elif choice == "2":
            alert_storage.display_alerts()
        elif choice == "3":
            value_usd = alert_management.modify_value()
            print("Attendez que les alertes se déclenchent ...")
            alert_service.create_alert("USD", value_usd)  
        elif choice == "4":
            alert_management.delete_alert()
        elif choice == "5":
            value_eur = float(input("Entrez la valeur en EUR pour laquelle vous souhaitez être alerté lors de l'augmentation/diminution du BTC : "))
            print("Attendez que les alertes se déclenchent ...")
            alert_service.create_alert("EUR", value_eur)
        elif choice.lower() == "q":
            break
        else:
            print("Choix invalide. Veuillez Saisir 1, 2, 3, 4, 5 ou q.")
