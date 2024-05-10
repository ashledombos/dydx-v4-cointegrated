from v4_client_py.clients import IndexerClient, ValidatorClient

# Fonction pour fermer toutes les positions ouvertes
def abort_all_positions(indexer_client: IndexerClient, validator_client: ValidatorClient):
    """
    Ferme toutes les positions ouvertes sur le compte. Ceci inclut des positions sur des marchés de produits dérivés perpétuels.
    Prend en paramètre les clients indexer et validator pour effectuer les appels API nécessaires.

    :param indexer_client: Client pour les requêtes d'indexation à l'API dYdX
    :param validator_client: Client pour les requêtes de validation à l'API dYdX
    :return: Résultats des ordres de fermeture
    """
    try:
        # Récupère toutes les positions ouvertes
        positions = indexer_client.account.get_positions()
        results = []
        
        # Boucle pour fermer chaque position
        for position in positions:
            if position['status'] == 'OPEN':
                market = position['market']
                size = -position['size']  # Nécessaire pour fermer la position
                order_result = validator_client.place_order(
                    market=market,
                    size=size,
                    order_type='MARKET',  # Utiliser un ordre de marché pour fermer immédiatement
                    side='SELL' if position['side'] == 'BUY' else 'BUY'  # Inverse la position
                )
                results.append(order_result)
        
        return results
    except Exception as e:
        print(f"Erreur lors de la fermeture des positions : {e}")
        raise
