from decouple import config
from v4_client_py.clients import CompositeClient, Subaccount
from v4_client_py.clients.constants import Network
from v4_client_py.chain.aerial.wallet import LocalWallet
from constants import NETWORK_MODE

def connect_dydx_v4():
    """
    Connects to dYdX V4 using the CompositeClient and fetches account details.
    
    Returns a client object that includes all necessary details like account id,
    balances, and other relevant account information.
    """
    # Charger le mnemonic depuis le fichier .env
    mnemonic = config('MNEMONIC')

    # Configurer le réseau
    if NETWORK_MODE == "mainnet":
        network = Network.mainnet()
    else:
        network = Network.testnet()

    # Créer le portefeuille local
    wallet = LocalWallet.from_mnemonic(mnemonic)

    # Créer le client composite
    client = CompositeClient(network)

    # Créer un subcompte (par exemple, le premier subcompte)
    subaccount = Subaccount(wallet, 0)

    # Récupérer les informations du compte
    account_info = client.get_account_info(subaccount)
    
    # Afficher les informations
    print("Connection Successful")
    print(f"Account ID: {account_info['account_id']}")
    print(f"Quote Balance: {account_info['quote_balance']}")

    return client

# Appel de la fonction si le script est exécuté directement
if __name__ == "__main__":
    client = connect_dydx_v4()
