from decouple import config
from dydx4 import Client  # Assurez-vous d'utiliser la bibliothèque dydx4
from constants import (
    HOST,
    DYDX_API_KEY,
    DYDX_API_SECRET,
    DYDX_API_PASSPHRASE,
)

def connect_dydx():
    """
    Connexion à DYDX et retour du client.

    Crée une connexion client à l'API DYDX en utilisant les informations d'identification fournies. 
    Affiche et renvoie les informations du compte DYDX si la connexion est réussie.

    Returns:
        client (Client): Instance du client DYDX connecté.
    """

    try:
        # Création de la connexion client
        client = Client(
            host=HOST,
            api_key_credentials={
                "key": DYDX_API_KEY,
                "secret": DYDX_API_SECRET,
                "passphrase": DYDX_API_PASSPHRASE,
            }
        )

        # Confirmation de la connexion du client
        account = client.private.get_account()
        account_id = account['account']['id']
        balance = account['account']['balance']

        print("Connexion réussie")
        print("ID du compte : ", account_id)
        print("Solde du compte : ", balance)

        # Retourne le client connecté
        return client

    except Exception as e:
        print(f"Erreur lors de la connexion à DYDX : {e}")
        return None

# Appel de la fonction de connexion pour tester
if __name__ == "__main__":
    connect_dydx()
