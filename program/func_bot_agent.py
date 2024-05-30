import asyncio
from decouple import config
from v4_client_py.clients import CompositeClient
from v4_client_py.clients.constants import Network
from v4_client_py.chain.aerial.wallet import LocalWallet
from v4_client_py.clients.dydx_subaccount import Subaccount

def get_network_config():
    # Déterminer si on utilise mainnet ou testnet en se basant sur une variable d'environnement
    network_mode = config('NETWORK_MODE', default='testnet')
    if network_mode == "mainnet":
        return Network.config_network()  # Assurez-vous que cette méthode est configurée pour mainnet
    else:
        return Network.config_network()  # Assurez-vous que cette méthode est configurée pour testnet

async def connect_dydx_v4():
    """
    Connecte à dYdX V4 en utilisant le CompositeClient et récupère les détails du compte de manière asynchrone.
    """
    mnemonic = config('MNEMONIC')
    network = get_network_config()
    wallet = LocalWallet.from_mnemonic(mnemonic)
    subaccount = Subaccount(wallet)

    client = CompositeClient(network)
    indexer_client = client.indexer_client

    # Récupération des informations du subcompte
    account_info = await indexer_client.account.get_subaccount(wallet.address().__str__(), subaccount.subaccount_number)
    
    print("Connection Successful")
    print(f"Account ID: {account_info.data['account']['accountId']}")
    print(f"Quote Balance: {account_info.data['account']['balances']['quote']}")

    return client

if __name__ == "__main__":
    asyncio.run(connect_dydx_v4())
