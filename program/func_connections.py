import asyncio
from decouple import config
from v4_client_py.clients.constants import Network
from v4_client_py.chain.aerial.wallet import LocalWallet
from v4_client_py.clients.dydx_indexer_client import IndexerClient
from v4_client_py.clients.dydx_subaccount import Subaccount
from v4_client_py.clients.dydx_validator_client import ValidatorClient

def get_network_config():
    network_mode = config('NETWORK_MODE', default='testnet')
    if network_mode == "mainnet":
        return Network.config_network()  # Assurez-vous que cette configuration est correctement définie
    else:
        return Network.config_network()  # Assurez-vous que cette configuration est correctement définie

async def connect_dydx_v4():
    mnemonic = config('MNEMONIC')
    network = get_network_config()
    wallet = LocalWallet.from_mnemonic(mnemonic)
    subaccount = Subaccount(wallet)

    # Création des clients
    indexer_client = IndexerClient(network.indexer_config)
    validator_client = ValidatorClient(network.validator_config)

    # Utiliser `IndexerClient` pour obtenir les informations du compte
    account_info = await indexer_client.account.get_subaccount(wallet.address(), subaccount.subaccount_number)

    # Afficher les informations obtenues
    print("Connection Successful")
    print(f"Account ID: {wallet.address()}")
    print(f"Subaccount ID: {subaccount.subaccount_number}")
    print(f"Account Info: {account_info}")

    return account_info

if __name__ == "__main__":
    asyncio.run(connect_dydx_v4())
