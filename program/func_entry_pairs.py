from constants import ZSCORE_THRESH, USD_PER_TRADE, USD_MIN_COLLATERAL
from func_utils import format_number
from func_public import get_candles_recent
from func_cointegration import calculate_zscore
from func_private import is_open_positions
from func_bot_agent import BotAgent
import pandas as pd
import json

from pprint import pprint

def open_positions(client):
    """
    Gérer la recherche de déclencheurs pour l'entrée en position.
    Stocker les trades pour une gestion ultérieure dans la fonction de sortie.
    """
    
    # Charger les paires cointegrées
    df = pd.read_csv("cointegrated_pairs.csv")

    # Obtenir les marchés pour référencer la taille minimale des ordres, la taille des ticks, etc.
    markets = client.public.get_markets().data

    # Initialiser le conteneur pour les résultats de BotAgent
    bot_agents = []

    # Ouvrir le fichier JSON
    try:
        with open("bot_agents.json") as open_positions_file:
            open_positions_dict = json.load(open_positions_file)
            for p in open_positions_dict:
                bot_agents.append(p)
    except FileNotFoundError:
        bot_agents = []
    
    # Trouver les déclencheurs ZScore
    for index, row in df.iterrows():
        # Extraire les variables
        base_market = row["base_market"]
        quote_market = row["quote_market"]
        hedge_ratio = row["hedge_ratio"]
        half_life = row["half_life"]

        # Obtenir les prix
        series_1 = get_candles_recent(client, base_market)
        series_2 = get_candles_recent(client, quote_market)

        # Calculer le ZScore
        if len(series_1) > 0 and len(series_1) == len(series_2):
            spread = series_1 - (hedge_ratio * series_2)
            z_score = calculate_zscore(spread).values.tolist()[-1]

            # Établir si c'est un trade potentiel
            if abs(z_score) >= ZSCORE_THRESH:
                # S'assurer qu'aucune position similaire n'est déjà ouverte (diversifier le trading)
                is_base_open = is_open_positions(client, base_market)
                is_quote_open = is_open_positions(client, quote_market)

                # Placer le trade
                if not is_base_open and not is_quote_open:
                    # Déterminer le côté
                    base_side = "BUY" if z_score < 0 else "SELL"
                    quote_side = "BUY" if z_score > 0 else "SELL"

                    # Obtenir les prix acceptables sous forme de chaîne avec le bon nombre de décimales
                    base_price = series_1[-1]
                    quote_price = series_2[-1]
                    accept_base_price = float(base_price) * 1.01 if z_score < 0 else float(base_price) * 0.99
                    accept_quote_price = float(quote_price) * 1.01 if z_score > 0 else float(quote_price) * 0.99
                    failsafe_base_price = float(base_price) * 0.05 if z_score < 0 else float(base_price) * 1.7
                    base_tick_size = markets["markets"][base_market]["tickSize"]
                    quote_tick_size = markets["markets"][quote_market]["tickSize"]

                    # Formater les prix
                    accept_base_price = format_number(accept_base_price, base_tick_size)
                    accept_quote_price = format_number(accept_quote_price, quote_tick_size)
                    accept_failsafe_base_price = format_number(failsafe_base_price, base_tick_size)

                    # Obtenir la taille
                    base_quantity = 1 / base_price * USD_PER_TRADE
                    quote_quantity = 1 / quote_price * USD_PER_TRADE
                    base_step_size = markets["markets"][base_market]["stepSize"]
                    quote_step_size = markets["markets"][quote_market]["stepSize"]

                    # Formater les tailles
                    base_size = format_number(base_quantity, base_step_size)
                    quote_size = format_number(quote_quantity, quote_step_size)

                    # S'assurer de la taille
                    base_min_order_size = markets["markets"][base_market]["minOrderSize"]
                    quote_min_order_size = markets["markets"][quote_market]["minOrderSize"]
                    check_base = float(base_quantity) > float(base_min_order_size)
                    check_quote = float(quote_quantity) > float(quote_min_order_size)

                    # Si les vérifications sont validées, placer les trades
                    if check_base and check_quote:
                        # Vérifier le solde du compte
                        account = client.private.get_account()
                        free_collateral = float(account.data["account"]["freeCollateral"])
                        print(f"Solde : {free_collateral} et minimum à {USD_MIN_COLLATERAL}")

                        # Vérification : S'assurer du collatéral
                        if free_collateral < USD_MIN_COLLATERAL:
                            break

                        # Créer un BotAgent
                        bot_agent = BotAgent(
                            client,
                            market_1=base_market,
                            market_2=quote_market,
                            base_side=base_side,
                            base_size=base_size,
                            base_price=accept_base_price,
                            quote_side=quote_side,
                            quote_size=quote_size,
                            quote_price=accept_quote_price,
                            accept_failsafe_base_price=accept_failsafe_base_price,
                            z_score=z_score,
                            half_life=half_life,
                            hedge_ratio=hedge_ratio
                        )

                        # Ouvrir les trades
                        bot_open_dict = bot_agent.open_trades()

                        # Vérification : Gérer les échecs
                        if bot_open_dict == "failed":
                            continue

                        # Gérer le succès de l'ouverture des trades
                        if bot_open_dict["pair_status"] == "LIVE":
                            # Ajouter à la liste des agents de bots
                            bot_agents.append(bot_open_dict)
                            del(bot_open_dict)

                            # Confirmer le statut live dans le print
                            print("Statut du trade : Live")
                            print("---")

    # Sauvegarder les agents
    print("Succès : Vérification de la gestion des trades ouverts")
    if len(bot_agents) > 0:
        with open("bot_agents.json", "w") as f:
            json.dump(bot_agents, f)
