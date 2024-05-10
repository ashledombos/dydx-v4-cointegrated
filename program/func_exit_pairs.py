from v4_client_py.clients import CompositeClient, Subaccount
from v4_client_py.clients.constants import Network, BECH32_PREFIX
from v4_client_py.clients.helpers.chain_helpers import OrderType, OrderSide, OrderTimeInForce

async def manage_trade_exits(client, positions_to_exit):
    """
    Gère la fermeture des positions ouvertes selon les conditions définies.

    :param client: Instance de CompositeClient pour interagir avec l'API dYdX V4.
    :param positions_to_exit: Liste des positions à fermer.
    """
    wallet = client.wallet
    subaccount = Subaccount(wallet, 0)  # Utilise le subaccount principal par défaut
    for position in positions_to_exit:
        try:
            # Prépare les paramètres de l'ordre pour fermer la position
            order_params = {
                'market': position['market'],
                'type': OrderType.MARKET,
                'side': OrderSide.SELL if position['side'] == 'long' else OrderSide.BUY,  # Inverse la position
                'size': position['size'],  # Assurez-vous que la taille de l'ordre correspond à la position
                'time_in_force': OrderTimeInForce.IOC  # Utilise Immediate-Or-Cancel pour une fermeture rapide
            }
            
            # Place l'ordre de fermeture
            tx = await client.place_order(subaccount, **order_params)
            print(f"Order to exit {position['market']} placed, transaction hash: {tx.tx_hash}")
        except Exception as error:
            print(f"Failed to exit position for {position['market']}: {error}")

