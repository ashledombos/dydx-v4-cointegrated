import asyncio
from decouple import config
from v4_client_py.clients import CompositeClient, Subaccount
from v4_client_py.clients.constants import Network, ValidatorConfig, IndexerConfig
from v4_client_py.chain.aerial.wallet import LocalWallet

def get_network_config():
    """
    Configure and return the network settings using the custom configuration method.
    """
    # Create validator and indexer configurations based on predefined settings
    validator_config = ValidatorConfig(
        grpc_endpoint='{get from deployer}',
        chain_id='{get from deployer}',
        ssl_enabled=True,
        url_prefix='{get from deployer}',
        aerial_url='{get from deployer}'
    )
    indexer_config = IndexerConfig(
        rest_endpoint='{get from deployer}',
        websocket_endpoint='{get from deployer}'
    )

    # Return a new network configuration instance
    return Network(
        env='{get from deployer}',
        validator_config=validator_config,
        indexer_config=indexer_config,
        faucet_endpoint=None  # or your specific faucet endpoint if applicable
    )

async def connect_dydx_v4():
    """
    Connects to dYdX V4 using the CompositeClient and fetches account details asynchronously.
    """
    # Load the mnemonic from environment variables
    mnemonic = config('MNEMONIC')

    # Fetch network configuration
    network = get_network_config()

    # Create a local wallet from the mnemonic
    wallet = LocalWallet.from_mnemonic(mnemonic)

    # Initialize the CompositeClient with the network configuration
    client = CompositeClient(network)

    # Create a subaccount using the wallet, specifying subaccount index 0
    subaccount = Subaccount(wallet, 0)

    # Fetch and print account info asynchronously
    account_info = await client.get_account_info(subaccount)

    print("Connection Successful")
    print(f"Account ID: {account_info['account_id']}")
    print(f"Quote Balance: {account_info['quote_balance']}")

    return client

if __name__ == "__main__":
    asyncio.run(connect_dydx_v4())

    client = connect_dydx_v4()
