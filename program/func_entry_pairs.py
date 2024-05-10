from v4_client_py.clients import CompositeClient, Subaccount
from v4_client_py.clients.constants import Network, BECH32_PREFIX
from v4_client_py.clients.helpers.chain_helpers import OrderType, OrderSide, OrderTimeInForce

async def open_positions(client, pairs_to_trade):
    """
    Ouvre des positions pour les paires de trading sélectionnées en utilisant l'API dYdX V4.

    :param client: Instance de CompositeClient pour interagir avec l'API dYdX V4.
    :param pairs_to_trade: Liste des paires à trader.
    """
    wallet = client.wallet
    subaccount = Subaccount(wallet, 0)  # Utilise le subaccount principal par défaut
    for pair in pairs_to_trade:
        try:
            # Prépare les paramètres de l'ordre
            order_params = {
                'market': pair['market'],
                'type': OrderType.LIMIT,
                'side': OrderSide.BUY if pair['side'] == 'long' else OrderSide.SELL,
                'price': pair['entry_price'],
                'size': pair['size'],
                'time_in_force': OrderTimeInForce.GTT,
                'post_only': True
            }
            
            # Place l'ordre
            tx = await client.place_order(subaccount, **order_params)
            print(f"Order placed for {pair['market']} at price {pair['entry_price']}, transaction hash: {tx.tx_hash}")
        except Exception as error:
            print(f"Failed to place order for {pair['market']}: {error}")

