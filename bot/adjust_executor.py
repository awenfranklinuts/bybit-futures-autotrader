from .trade_executor import get_last_price, place_order


def adjust_position(symbol: str, action: str, new_value: float = None, side: str = "Buy"):
    """
    Adjusts an open position based on the action:
    - move_sl_to_entry: Moves stop loss to the entry price
    - update_sl: Updates stop loss to a new price
    - update_tp: Updates take profit to a new price
    - partial_close: Closes part of the position

    Parameters:
        symbol (str): The symbol to adjust (e.g., 'BTCUSDT')
        action (str): The adjustment type
        new_value (float): The value used for SL/TP updates or partial close qty
        side (str): Trade direction ("Buy" or "Sell")
    """
    print(f"🔧 Adjusting {symbol} | Action: {action} | Value: {new_value}")

    if action == "move_sl_to_entry":
        entry_price = get_last_price(symbol)
        place_order(
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=0.001,  # Replace with actual size
            leverage=10,
            stop_loss=entry_price,
            take_profit=None
        )

    elif action == "update_sl":
        if new_value is None:
            print("❌ No new SL value provided.")
            return
        place_order(
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=0.001,
            leverage=10,
            stop_loss=new_value
        )

    elif action == "update_tp":
        if new_value is None:
            print("❌ No new TP value provided.")
            return
        place_order(
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=0.001,
            leverage=10,
            take_profit=new_value
        )

    elif action == "partial_close":
        if new_value is None or new_value <= 0:
            print("❌ Invalid partial close quantity.")
            return
        place_order(
            symbol=symbol,
            side="Sell" if side == "Buy" else "Buy",
            order_type="Market",
            qty=new_value,
            leverage=10
        )

    else:
        print(f"⚠️ Unsupported adjustment action: {action}")
