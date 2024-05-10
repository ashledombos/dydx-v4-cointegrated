from v4_client_py.clients import IndexerClient

def construct_market_prices(indexer_client: IndexerClient):
    """
    Construit et retourne les prix actuels du marché en utilisant l'API publique dYdX V4.
    Prend en paramètre le client indexer pour effectuer les requêtes API nécessaires.

    :param indexer_client: Client pour les requêtes d'indexation à l'API dYdX
    :return: DataFrame contenant les prix de marché
    """
    try:
        # Récupère les informations de marché pour tous les produits dérivés perpétuels
        markets_info = indexer_client.markets.get_perpetual_markets()
        market_data = []

        # Extrait les données pertinentes pour chaque marché
        for market in markets_info['markets']:
            market_data.append({
                'market': market['id'],
                'price': market['price'],
                'volume': market['volume24h']
            })

        # Convertit les données du marché en DataFrame pour une manipulation ultérieure
        import pandas as pd
        df_market_prices = pd.DataFrame(market_data)
        return df_market_prices
    except Exception as e:
        print(f"Erreur lors de la construction des prix de marché : {e}")
        raise
