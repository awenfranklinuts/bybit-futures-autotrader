from bot.signal_parser import parse_signal
from bot.trade_executor import place_order
from bot.adjust_executor import adjust_position
from bot.close_executor import close_position  # Handles close logic

# Example WhatsApp message
whatsapp_message = """
🧪 New Position
🪙 Coin: BTCUSDT LONG (20x leverage cross)
💳 Entry: 111,630
🎯 Target 1: 112,500
🎯 Target 2: 114,000
🎯 Target 3: 115,500
🛑 Stop loss: 109,000
📝 Notes: Use 1% of capital, Cross margin, execute at market.
"""

# Step 1: Parse the message
signal = parse_signal(whatsapp_message)
print("\nParsed Signal:", signal)

# Step 2: Determine mode
mode = signal.get("mode")

if mode == "open":
    print("\n✅ Detected trade signal: OPEN")
    try:
        symbol = signal["symbol"]
        side_raw = signal["side"].upper()
        side = "Buy" if side_raw in ["LONG", "BUY"] else "Sell"

        leverage_raw = str(signal.get("leverage", 10))
        leverage = ''.join(filter(str.isdigit, leverage_raw))  # Remove 'x'

        entry_raw = signal.get("entry")
        stop_loss_raw = signal.get("stop_loss")
        targets_raw = signal.get("targets")

        # --- Clean and normalize numeric values ---
        def clean_number(val):
            if isinstance(val, str):
                val = val.replace(",", "").strip()
            try:
                return round(float(val), 2)
            except:
                return None


        entry = clean_number(entry_raw)
        stop_loss = clean_number(stop_loss_raw)
        targets = [clean_number(t) for t in targets_raw] if targets_raw else []
        take_profit = targets[0] if targets else None

        qty = 0.005  # Default test quantity

        place_order(
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=qty,
            leverage=leverage,
            take_profit=take_profit,
            stop_loss=stop_loss
        )

    except Exception as e:
        print("❌ Failed to execute open trade:", e)

elif mode == "adjust":
    print("\n⚠️ Detected trade adjustment signal")
    try:
        symbol = signal.get("symbol")
        action = signal.get("action")
        new_value = signal.get("new_value")

        if symbol and action:
            adjust_position(symbol=symbol, action=action, new_value=new_value)
        else:
            print("⚠️ Missing required fields for adjustment.")
    except Exception as e:
        print("❌ Failed to adjust position:", e)

elif mode == "close":
    print("\n❌ Detected trade CLOSE signal")
    try:
        symbol = signal.get("symbol")
        if symbol:
            close_position(symbol)
        else:
            print("⚠️ Symbol not provided for closing.")
    except Exception as e:
        print("❌ Failed to close position:", e)

elif mode == "commentary":
    print("\n💬 Commentary detected. No action taken.")
    print("Note:", signal.get("note", "No further details."))

else:
    print("\n❓ Unknown signal mode:", mode)
