import pandas as pd
from statsmodels.tsa.stattools import coint

def store_cointegration_results(df_market_prices):
    """
    Analyse la cointégration des paires de marchés à partir des prix récupérés et stocke les résultats.
    La cointégration est utilisée pour identifier les paires de marchés qui peuvent être utilisées pour des stratégies de trading à long terme.

    :param df_market_prices: DataFrame contenant les prix de marché
    :return: Résultat de l'opération de sauvegarde ou une indication d'échec
    """
    try:
        # Analyse de la cointégration sur toutes les combinaisons possibles de marchés
        n = len(df_market_prices)
        p_values = pd.DataFrame(index=df_market_prices['market'], columns=df_market_prices['market'])
        for i in range(n):
            for j in range(i+1, n):
                result = coint(df_market_prices.iloc[i]['price'], df_market_prices.iloc[j]['price'])
                p_values.iloc[i, j] = result[1]

        # Filtre les paires avec une p-value inférieure à un seuil, e.g., 0.05
        pairs_to_trade = p_values.where(lambda x: x < 0.05).stack().index.tolist()

        # Sauvegarde des résultats (simulé ici comme un simple print ou retour de valeur)
        print("Paires cointégrées trouvées et sauvegardées :", pairs_to_trade)
        return "saved"
    except Exception as e:
        print(f"Erreur lors de l'enregistrement des résultats de cointégration : {e}")
        return "failed"
