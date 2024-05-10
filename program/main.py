import asyncio
from v4_client_py.clients import CompositeClient, Network, Subaccount
from examples.utils import loadJson, OrderExecutionToTimeInForce
from func_bot_agent import place_order, manage_positions
from tests.constants import DYDX_TEST_MNEMONIC

async def main():
    """
    Fonction principale pour démarrer le bot de trading.
    """
    network_config = Network.config_network()
    wallet = Subaccount.from_mnemonic(DYDX_TEST_MNEMONIC)
    client = CompositeClient(network_config)

    # Chargement des paramètres de trading à partir d'un fichier JSON.
    trading_params = loadJson('trading_parameters.json')

    # Boucle principale de trading.
    while True:
        try:
            # Vérification des opportunités de trading et placement des ordres.
            for param in trading_params:
                market = param['market']
                order_type = OrderType[param['type']]
                side = OrderSide[param['side']]
                price = param['price']
                amount = param['amount']
                time_in_force = OrderExecutionToTimeInForce(param['timeInForce'])

                print(f"Placing order on {market} at price {price} for {amount}")
                order_result = await place_order(client, market, order_type, side, amount, price)
                print(f"Order placed: {order_result}")

            # Gestion des positions existantes.
            await manage_positions(client, threshold=0.1, market='BTC-USD')

            # Attente avant le prochain cycle de trading.
            await asyncio.sleep(60)

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    asyncio.run(main())
