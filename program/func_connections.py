from v4_client_py.clients import IndexerClient, ValidatorClient
from v4_client_py.clients.constants import Network
from constants import DYDX_TEST_MNEMONIC

# Connect to DYDX v4 API
def connect_dydx():
    """
    Crée et retourne un client dYdX connecté à l'aide de la v4 API.
    Utilise la configuration du réseau spécifiée pour se connecter aux endpoints nécessaires.
    """

    # Configuration du réseau
    network_config = Network.config_network()
    indexer_client = IndexerClient(
        config=network_config.indexer_config,
    )
    validator_client = ValidatorClient(
        config=network_config.validator_config,
    )

    # Vérification de la connexion
    try:
        # Pour des vérifications supplémentaires, on pourrait implémenter des appels à des endpoints spécifiques,
        # par exemple, vérifier le statut de l'API ou des informations de compte spécifiques.
        print("Connection Successful to Indexer and Validator Clients")
        
        # Retourne les clients connectés
        return indexer_client, validator_client
    except Exception as e:
        print("Failed to connect to dYdX v4 clients:", e)
        raise

