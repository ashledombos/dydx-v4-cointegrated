from constants import RESOLUTION
from func_utils import get_ISO_times
import pandas as pd
import numpy as np
import time

# Get relevant time periods for ISO from and to
ISO_TIMES = get_ISO_times()

def get_candles_recent(client, market):
    """
    Récupérer les données récentes de bougies pour un marché donné.

    Parameters:
    client (obj): Client de l'API.
    market (str): Le marché pour lequel les données de bougies sont récupérées.

    Returns:
    np.array: Un tableau contenant les prix de clôture des bougies récentes.
    """
    
    close_prices = []

    # Protéger les limites de l'API
    time.sleep(0.2)

    try:
        # Récupérer les données
        candles = client.public.get_candles(
            market=market,
            resolution=RESOLUTION,
            limit=100
        )
        # Structurer les données
        for candle in candles.data["candles"]:
            close_prices.append(candle["close"])
    except Exception as e:
        print(f"Erreur lors de la récupération des bougies récentes pour {market} : {e}")
        return np.array([])  # Retourner un tableau vide en cas d'erreur

    # Construire et retourner la série de prix de clôture
    close_prices.reverse()
    prices_result = np.array(close_prices).astype(np.float64)
    return prices_result


def get_candles_historical(client, market):
    """
    Récupérer les données historiques de bougies pour un marché donné.

    Parameters:
    client (obj): Client de l'API.
    market (str): Le marché pour lequel les données de bougies sont récupérées.

    Returns:
    list: Une liste de dictionnaires contenant les prix de clôture historiques et leurs dates.
    """
    
    close_prices = []

    for timeframe in ISO_TIMES.keys():
        tf_obj = ISO_TIMES[timeframe]
        from_iso = tf_obj["from_iso"]
        to_iso = tf_obj["to_iso"]

        # Protéger les limites de l'API
        time.sleep(0.2)

        try:
            # Récupérer les données
            candles = client.public.get_candles(
                market=market,
                resolution=RESOLUTION,
                from_iso=from_iso,
                to_iso=to_iso,
                limit=100
            )
            # Structurer les données
            for candle in candles.data["candles"]:
                close_prices.append({"datetime": candle["startedAt"], market: candle["close"] })
        except Exception as e:
            print(f"Erreur lors de la récupération des bougies historiques pour {market} dans la période {timeframe} : {e}")
            continue  # Passer à la période suivante en cas d'erreur

    # Construire et retourner la liste des prix de clôture
    close_prices.reverse()
    return close_prices


def construct_market_prices(client):
    """
    Construire les prix du marché pour tous les marchés disponibles et en ligne.

    Parameters:
    client (obj): Client de l'API.

    Returns:
    pd.DataFrame: Un DataFrame contenant les prix de clôture pour tous les marchés disponibles.
    """
    
    tradeable_markets = []

    try:
        markets = client.public.get_markets()
    except Exception as e:
        print(f"Erreur lors de la récupération des données de marché : {e}")
        return pd.DataFrame()  # Retourner un DataFrame vide en cas d'erreur

    # Trouver les paires échangeables
    for market in markets.data["markets"].keys():
        market_info = markets.data["markets"][market]
        if market_info["status"] == "ONLINE" and market_info["type"] == "PERPETUAL":
            tradeable_markets.append(market)

    # Initialiser le DataFrame avec le premier marché
    close_prices = get_candles_historical(client, tradeable_markets[0])
    df = pd.DataFrame(close_prices)
    df.set_index("datetime", inplace=True)

    # Ajouter les prix des autres marchés au DataFrame
    for market in tradeable_markets[1:]:
        close_prices_add = get_candles_historical(client, market)
        df_add = pd.DataFrame(close_prices_add)
        df_add.set_index("datetime", inplace=True)
        df = pd.merge(df, df_add, how="outer", on="datetime", copy=False)
        del df_add

    # Vérifier les colonnes contenant des NaNs
    nans = df.columns[df.isna().any()].tolist()
    if nans:
        print("Suppression des colonnes : ")
        print(nans)
        df.drop(columns=nans, inplace=True)

    return df
