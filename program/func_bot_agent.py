from func_private import place_market_order, check_order_status
from datetime import datetime, timedelta
from func_messaging import send_message
import time
from pprint import pprint

class BotAgent:
    """
    Classe principale pour gérer l'ouverture et le suivi des ordres
    """

    def __init__(
        self,
        client,
        market_1,
        market_2,
        base_side,
        base_size,
        base_price,
        quote_side,
        quote_size,
        quote_price,
        accept_failsafe_base_price,
        z_score,
        half_life,
        hedge_ratio,
    ):
        """
        Initialise les variables de classe

        Args:
            client: Client d'API dYdX
            market_1: Premier marché
            market_2: Deuxième marché
            base_side: Côté de l'ordre de base (achat/vente)
            base_size: Taille de l'ordre de base
            base_price: Prix de l'ordre de base
            quote_side: Côté de l'ordre de contrepartie (achat/vente)
            quote_size: Taille de l'ordre de contrepartie
            quote_price: Prix de l'ordre de contrepartie
            accept_failsafe_base_price: Prix de sécurité pour annulation d'ordre
            z_score: Score Z pour la stratégie de trading
            half_life: Demi-vie de la stratégie de trading
            hedge_ratio: Ratio de couverture
        """
        self.client = client
        self.market_1 = market_1
        self.market_2 = market_2
        self.base_side = base_side
        self.base_size = base_size
        self.base_price = base_price
        self.quote_side = quote_side
        self.quote_size = quote_size
        self.quote_price = quote_price
        self.accept_failsafe_base_price = accept_failsafe_base_price
        self.z_score = z_score
        self.half_life = half_life
        self.hedge_ratio = hedge_ratio

        # Statut initial des ordres
        self.order_dict = {
            "market_1": market_1,
            "market_2": market_2,
            "hedge_ratio": hedge_ratio,
            "z_score": z_score,
            "half_life": half_life,
            "order_id_m1": "",
            "order_m1_size": base_size,
            "order_m1_side": base_side,
            "order_time_m1": "",
            "order_id_m2": "",
            "order_m2_size": quote_size,
            "order_m2_side": quote_side,
            "order_time_m2": "",
            "pair_status": "",
            "comments": "",
        }

    def check_order_status_by_id(self, order_id):
        """
        Vérifie le statut d'un ordre par son ID

        Args:
            order_id: ID de l'ordre à vérifier

        Returns:
            str: Statut de l'ordre ('failed', 'live', 'error')
        """
        try:
            time.sleep(2)
            order_status = check_order_status(self.client, order_id)

            if order_status == "CANCELED":
                print(f"{self.market_1} vs {self.market_2} - Ordre annulé…")
                self.order_dict["pair_status"] = "FAILED"
                return "failed"

            if order_status != "FILLED":
                time.sleep(15)
                order_status = check_order_status(self.client, order_id)
                if order_status == "CANCELED":
                    print(f"{self.market_1} vs {self.market_2} - Ordre annulé…")
                    self.order_dict["pair_status"] = "FAILED"
                    return "failed"
                if order_status != "FILLED":
                    self.client.private.cancel_order(order_id=order_id)
                    self.order_dict["pair_status"] = "ERROR"
                    print(f"{self.market_1} vs {self.market_2} - Erreur d'ordre…")
                    return "error"
            return "live"
        except Exception as e:
            self.order_dict["pair_status"] = "ERROR"
            self.order_dict["comments"] = str(e)
            return "error"

    def open_trades(self):
        """
        Ouvre des trades sur les marchés définis

        Returns:
            dict: Statut des ordres et commentaires
        """
        print("---")
        print(f"{self.market_1}: Placement du premier ordre…")
        print(f"Side: {self.base_side}, Size: {self.base_size}, Price: {self.base_price}")
        print("---")

        try:
            base_order = place_market_order(
                self.client,
                market=self.market_1,
                side=self.base_side,
                size=self.base_size,
                price=self.base_price,
                reduce_only=False
            )
            self.order_dict["order_id_m1"] = base_order["order"]["id"]
            self.order_dict["order_time_m1"] = datetime.now().isoformat()
        except Exception as e:
            self.order_dict["pair_status"] = "ERROR"
            self.order_dict["comments"] = f"Market 1 {self.market_1}: {e}"
            return self.order_dict

        order_status_m1 = self.check_order_status_by_id(self.order_dict["order_id_m1"])
        if order_status_m1 != "live":
            self.order_dict["pair_status"] = "ERROR"
            self.order_dict["comments"] = f"{self.market_1} failed to fill"
            return self.order_dict

        print("---")
        print(f"{self.market_2}: Placement du second ordre…")
        print(f"Side: {self.quote_side}, Size: {self.quote_size}, Price: {self.quote_price}")
        print("---")

        try:
            quote_order = place_market_order(
                self.client,
                market=self.market_2,
                side=self.quote_side,
                size=self.quote_size,
                price=self.quote_price,
                reduce_only=False
            )
            self.order_dict["order_id_m2"] = quote_order["order"]["id"]
            self.order_dict["order_time_m2"] = datetime.now().isoformat()
        except Exception as e:
            self.order_dict["pair_status"] = "ERROR"
            self.order_dict["comments"] = f"Market 2 {self.market_2}: {e}"
            return self.order_dict

        order_status_m2 = self.check_order_status_by_id(self.order_dict["order_id_m2"])
        if order_status_m2 != "live":
            self.order_dict["pair_status"] = "ERROR"
            self.order_dict["comments"] = f"{self.market_1} failed to fill"

            try:
                close_order = place_market_order(
                    self.client,
                    market=self.market_1,
                    side=self.quote_side,
                    size=self.base_size,
                    price=self.accept_failsafe_base_price,
                    reduce_only=True
                )

                time.sleep(2)
                order_status_close_order = check_order_status(self.client, close_order["order"]["id"])
                if order_status_close_order != "FILLED":
                    print("ABORT PROGRAM")
                    print("Unexpected Error")
                    print(order_status_close_order)

                    send_message("Failed to execute. Code red. Error code: 100")
                    exit(1)
            except Exception as e:
                self.order_dict["pair_status"] = "ERROR"
                self.order_dict["comments"] = f"Close Market 1 {self.market_1}: {e}"
                print("ABORT PROGRAM")
                print("Unexpected Error")
                print(order_status_close_order)

                send_message("Failed to execute. Code red. Error code: 101")
                exit(1)

        else:
            self.order_dict["pair_status"] = "LIVE"
            return self.order_dict
