from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED, PLACE_TRADES, MANAGE_EXITS
from func_connections import connect_dydx_v4
from func_private import abort_all_positions_v4
from func_public import construct_market_prices_v4
from func_cointegration import store_cointegration_results_v4
from func_entry_pairs import open_positions_v4
from func_exit_pairs import manage_trade_exits_v4
from func_messaging import send_message_v4


# MAIN FUNCTION
if __name__ == "__main__":
    # Message on start
    send_message_v4("Bot launch successful")

    # Connect to client
    try:
        print("Connecting to Client...")
        client = connect_dydx_v4()
    except Exception as e:
        print("Error connecting to client: ", e)
        send_message_v4(f"Failed to connect to client {e}")
        exit(1)

    # Abort all open positions
    if ABORT_ALL_POSITIONS:
        try:
            print("Closing all positions...")
            close_orders = abort_all_positions_v4(client)
        except Exception as e:
            print("Error closing all positions: ", e)
            send_message_v4(f"Error closing all positions {e}")
            exit(1)

    # Find Cointegrated Pairs
    if FIND_COINTEGRATED:
        # Construct Market Prices
        try:
            print("Fetching market prices, please allow 3 mins...")
            df_market_prices = construct_market_prices_v4(client)
        except Exception as e:
            print("Error constructing market prices: ", e)
            send_message_v4(f"Error constructing market prices {e}")
            exit(1)

        # Store Cointegrated Pairs
        try:
            print("Storing cointegrated pairs...")
            stores_result = store_cointegration_results_v4(df_market_prices)
            if stores_result != "saved":
                print("Error saving cointegrated pairs")
                exit(1)
        except Exception as e:
            print("Error saving cointegrated pairs: ", e)
            send_message_v4(f"Error saving cointegrated pairs {e}")
            exit(1)

    # Run as always on
    while True:
        # Manage exits
        if MANAGE_EXITS:
            try:
                print("Managing exits...")
                manage_trade_exits_v4(client)
            except Exception as e:
                print("Error managing exiting positions: ", e)
                send_message_v4(f"Error managing exiting positions {e}")
                exit(1)

        # Place trades for opening positions
        if PLACE_TRADES:
            try:
                print("Finding trading opportunities...")
                open_positions_v4(client)
            except Exception as e:
                print("Error trading pairs: ", e)
                send_message_v4(f"Error opening trades {e}")
                exit(1)
