from bot.signal_parser import parse_signal
from bot.trade_executor import place_order, get_balance
from bot.adjust_executor import adjust_position
from bot.close_executor import close_position  # Handles close logic

# Example WhatsApp message
whatsapp_message = """
🔥 VIP SIGNAL

🧪 New position  
🪙 Coin: BRETTUSDT LONG (20 leverage cross)  
💳 Entry: 0.064 - 0.066  
🎯 Target 1: 0.070  
🎯 Target 2: 0.074  
🎯 Target 3: 0.078  
🎯 Target 4: 0.083  
🎯 Target 5: 0.089  
🎯 Target 6: runners  
🛑 Stop loss: 1 day candle close below 0.058  
📝 Notes: DCA point: 0.062 – leave space to DCA  
🔒 1% for entries (0.5% entry 1, 0.5% entry 2), 2% for DCA point  
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
        leverage = int(''.join(filter(str.isdigit, leverage_raw)))  # Remove 'x'

        entry_raw = signal.get("entry")
        stop_loss_raw = signal.get("stop_loss")
        targets_raw = signal.get("targets")

        def clean_price(val):
            if not val:
                return None
            val = val.replace(",", "").strip()
            try:
                return float(val)
            except:
                return None

        # Handle range like "0.161 - 0.163"
        entry_price = None
        if entry_raw and "-" in entry_raw:
            entry_parts = entry_raw.split("-")
            entry_price = clean_price(entry_parts[0])  # use lower bound for calculation
        else:
            entry_price = clean_price(entry_raw)

        stop_loss = clean_price(stop_loss_raw.split()[-1]) if stop_loss_raw else None
        targets = [clean_price(t) for t in targets_raw if clean_price(t)] if targets_raw else []
        take_profit = targets[0] if targets else None

        # ✅ Calculate qty using 1% of actual balance (NOT leverage-adjusted)
        balance = get_balance()
        risk_percent = 0.01
        usdt_to_risk = balance * risk_percent
        qty = round(usdt_to_risk / entry_price, 0) if entry_price else 0.001

        order_type = "Limit" if entry_price else "Market"

        place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            qty=qty,
            leverage=leverage,
            take_profit=take_profit,
            stop_loss=stop_loss,
            price=entry_price if order_type == "Limit" else None
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
