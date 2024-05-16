from constants import CLOSE_AT_ZSCORE_CROSS
from func_utils import format_number
from func_public import get_candles_recent
from func_cointegration import calculate_zscore
from func_private import place_market_order
import json
import time
from pprint import pprint

def manage_trade_exits(client):
    """
    Gérer les sorties de positions ouvertes selon les critères définis dans constants.
    """
    
    # Initialiser la sauvegarde de la sortie
    save_output = []

    try:
        # Ouvrir le fichier JSON des positions ouvertes
        with open("bot_agents.json") as open_positions_file:
            open_positions_dict = json.load(open_positions_file)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du fichier bot_agents.json : {e}")
        return "complete"

    # Garder: Sortir s'il n'y a pas de positions ouvertes dans le fichier
    if len(open_positions_dict) < 1:
        return "complete"

    try:
        # Obtenir toutes les positions ouvertes par plateforme de trading
        exchange_pos = client.private.get_positions(status="OPEN")
        all_exc_pos = exchange_pos.data["positions"]
        markets_live = [p["market"] for p in all_exc_pos]
    except Exception as e:
        print(f"Erreur lors de la récupération des positions ouvertes : {e}")
        return "complete"

    # Protéger l'API
    time.sleep(0.5)

    # Vérifier que toutes les positions enregistrées correspondent à l'ordre enregistré
    # Sortir de la position selon les règles de sortie
    for position in open_positions_dict:
        is_close = False

        # Extraire les informations de correspondance de la position du fichier - marché 1
        position_market_m1 = position["market_1"]
        position_size_m1 = position["order_m1_size"]
        position_side_m1 = position["order_m1_side"]

        # Extraire les informations de correspondance de la position du fichier - marché 2
        position_market_m2 = position["market_2"]
        position_size_m2 = position["order_m2_size"]
        position_side_m2 = position["order_m2_side"]

        # Protéger l'API
        time.sleep(0.5)

        try:
            # Obtenir les infos de l'ordre m1 par exchange
            order_m1 = client.private.get_order_by_id(position["order_id_m1"])
            order_market_m1 = order_m1.data["order"]["market"]
            order_size_m1 = order_m1.data["order"]["size"]
            order_side_m1 = order_m1.data["order"]["side"]
        except Exception as e:
            print(f"Erreur lors de la récupération de l'ordre pour {position_market_m1} : {e}")
            continue

        # Protéger l'API
        time.sleep(0.5)

        try:
            # Obtenir les infos de l'ordre m2 par exchange
            order_m2 = client.private.get_order_by_id(position["order_id_m2"])
            order_market_m2 = order_m2.data["order"]["market"]
            order_size_m2 = order_m2.data["order"]["size"]
            order_side_m2 = order_m2.data["order"]["side"]
        except Exception as e:
            print(f"Erreur lors de la récupération de l'ordre pour {position_market_m2} : {e}")
            continue

        # Effectuer les vérifications de correspondance
        check_m1 = position_market_m1 == order_market_m1 and position_size_m1 == order_size_m1 and position_side_m1 == order_side_m1
        check_m2 = position_market_m2 == order_market_m2 and position_size_m2 == order_size_m2 and position_side_m2 == order_side_m2
        check_live = position_market_m1 in markets_live and position_market_m2 in markets_live

        # Garder: Si tous ne correspondent pas, sortir avec une erreur
        if not check_m1 or not check_m2 or not check_live:
            print(f"Warning: Not all open positions match exchange records for {position_market_m1} and {position_market_m2}")
            continue

        try:
            # Obtenir les prix
            series_1 = get_candles_recent(client, position_market_m1)
            time.sleep(0.2)
            series_2 = get_candles_recent(client, position_market_m2)
            time.sleep(0.2)

            # Obtenir les marchés pour référence de la taille de tick
            markets = client.public.get_markets().data
            time.sleep(0.2)
        except Exception as e:
            print(f"Erreur lors de la récupération des données de marché : {e}")
            continue

        if CLOSE_AT_ZSCORE_CROSS:
            try:
                # Initialiser les z_scores
                hedge_ratio = position["hedge_ratio"]
                z_score_traded = position["z_score"]
                if len(series_1) > 0 and len(series_1) == len(series_2):
                    spread = series_1 - (hedge_ratio * series_2)
                    z_score_current = calculate_zscore(spread).values.tolist()[-1]

                # Déterminer le déclencheur
                z_score_level_check = abs(z_score_current) >= abs(z_score_traded)
                z_score_cross_check = (z_score_current < 0 and z_score_traded > 0) or (z_score_current > 0 and z_score_traded < 0)

                # Fermer la position
                if z_score_level_check and z_score_cross_check:
                    is_close = True
            except Exception as e:
                print(f"Erreur lors du calcul du Z-Score : {e}")
                continue

        # Ajouter toute autre logique de fermeture ici

        if is_close:
            try:
                # Déterminer le côté - m1
                side_m1 = "SELL" if position_side_m1 == "BUY" else "BUY"

                # Déterminer le côté - m2
                side_m2 = "SELL" if position_side_m2 == "BUY" else "BUY"

                # Obtenir et formater le prix
                price_m1 = float(series_1[-1])
                price_m2 = float(series_2[-1])
                accept_price_m1 = price_m1 * 1.05 if side_m1 == "BUY" else price_m1 * 0.95
                accept_price_m2 = price_m2 * 1.05 if side_m2 == "BUY" else price_m2 * 0.95
                tick_size_m1 = markets["markets"][position_market_m1]["tickSize"]
                tick_size_m2 = markets["markets"][position_market_m2]["tickSize"]
                accept_price_m1 = format_number(accept_price_m1, tick_size_m1)
                accept_price_m2 = format_number(accept_price_m2, tick_size_m2)

                # Fermer les positions pour le marché 1
                print(">>> Fermeture du marché 1 <<<")
                print(f"Fermeture de la position pour {position_market_m1}")
                close_order_m1 = place_market_order(
                    client,
                    market=position_market_m1,
                    side=side_m1,
                    size=position_size_m1,
                    price=accept_price_m1,
                    reduce_only=True,
                )
                print(close_order_m1["order"]["id"])
                print(">>> Fermeture <<<")

                time.sleep(1)

                # Fermer les positions pour le marché 2
                print(">>> Fermeture du marché 2 <<<")
                print(f"Fermeture de la position pour {position_market_m2}")
                close_order_m2 = place_market_order(
                    client,
                    market=position_market_m2,
                    side=side_m2,
                    size=position_size_m2,
                    price=accept_price_m2,
                    reduce_only=True,
                )
                print(close_order_m2["order"]["id"])
                print(">>> Fermeture <<<")
            except Exception as e:
                print(f"Échec de la sortie pour {position_market_m1} et {position_market_m2} : {e}")
                save_output.append(position)
        else:
            save_output.append(position)

    # Sauvegarder les éléments restants
    print(f"{len(save_output)} éléments restants. Sauvegarde du fichier...")
    with open("bot_agents.json", "w") as f:
        json.dump(save_output, f)

# Améliorations et clarifications ajoutées:
# - Gestion des erreurs avec try-except
# - Docstrings pour les fonctions
# - Clarification des commentaires
# - Correction des erreurs potentielles liées aux appels API et à la version de dydx utilisée
