from datetime import datetime, timedelta
from func_utils import format_number
import time
import json
from pprint import pprint

def is_open_positions(client, market):
    """
    Check if there are any open positions for the specified market.
    
    Args:
        client: The dYdX client object.
        market: The market to check for open positions.
    
    Returns:
        bool: True if there are open positions, False otherwise.
    """
    try:
        # Protect API
        time.sleep(0.2)
        
        # Get positions
        all_positions = client.private.get_positions(market=market, status="OPEN")
        
        # Determine if open
        return len(all_positions.data["positions"]) > 0
    except Exception as e:
        print(f"Error checking open positions: {e}")
        return False

def check_order_status(client, order_id):
    """
    Check the status of a specific order by its ID.
    
    Args:
        client: The dYdX client object.
        order_id: The ID of the order to check.
    
    Returns:
        str: The status of the order.
    """
    try:
        order = client.private.get_order_by_id(order_id)
        if order.data:
            if "order" in order.data.keys():
                return order.data["order"]["status"]
        return "FAILED"
    except Exception as e:
        print(f"Error checking order status: {e}")
        return "FAILED"

def place_market_order(client, market, side, size, price, reduce_only):
    """
    Place a market order on the specified market.
    
    Args:
        client: The dYdX client object.
        market: The market to place the order on.
        side: The side of the order ('BUY' or 'SELL').
        size: The size of the order.
        price: The price of the order.
        reduce_only: Whether the order is reduce-only.
    
    Returns:
        dict: The placed order data.
    """
    try:
        # Get Position Id
        account_response = client.private.get_account()
        position_id = account_response.data["account"]["positionId"]
        
        # Get expiration time
        server_time = client.public.get_time()
        expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", "")) + timedelta(seconds=70)
        
        # Place an order
        placed_order = client.private.create_order(
            position_id=position_id,  # required for creating the order signature
            market=market,
            side=side,
            order_type="MARKET",
            post_only=False,
            size=size,
            price=price,
            limit_fee='0.015',
            expiration_epoch_seconds=expiration.timestamp(),
            time_in_force="FOK",
            reduce_only=reduce_only
        )
        
        return placed_order.data
    except Exception as e:
        print(f"Error placing market order: {e}")
        return None

def abort_all_positions(client):
    """
    Abort all open positions by cancelling all orders and closing open positions.
    
    Args:
        client: The dYdX client object.
    
    Returns:
        list: A list of closed orders.
    """
    try:
        # Cancel all orders
        client.private.cancel_all_orders()
        
        # Protect API
        time.sleep(0.5)
        
        # Get markets for reference of tick size
        markets = client.public.get_markets().data
        
        # Protect API
        time.sleep(0.5)
        
        # Get all open positions
        positions = client.private.get_positions(status="OPEN")
        all_positions = positions.data["positions"]
        
        # Handle open positions
        close_orders = []
        if len(all_positions) > 0:
            for position in all_positions:
                # Determine Market
                market = position["market"]
                
                # Determine Side
                side = "BUY" if position["side"] == "SHORT" else "SELL"
                
                # Get Price
                price = float(position["entryPrice"])
                accept_price = price * 1.7 if side == "BUY" else price * 0.3
                tick_size = float(markets["markets"][market]["tickSize"])
                accept_price = format_number(accept_price, tick_size)
                
                # Place order to close
                order = place_market_order(
                    client,
                    market,
                    side,
                    position["size"],
                    accept_price,
                    True
                )
                
                # Append the result
                close_orders.append(order)
                
                # Protect API
                time.sleep(0.2)
            
            # Override json file with empty list
            bot_agents = []
            with open("bot_agents.json", "w") as f:
                json.dump(bot_agents, f)
            
        return close_orders
    except Exception as e:
        print(f"Error aborting all positions: {e}")
        return []

