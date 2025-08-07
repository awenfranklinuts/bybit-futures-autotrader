import re
import openai

def is_new_trade_signal(message: str) -> bool:
    keywords = ["new position", "entry", "target", "stop loss"]
    return all(kw in message.lower() for kw in keywords)

def parse_signal(message: str) -> dict:
    """
    Parses a new trade signal from a message string.
    Returns a dictionary with extracted values.
    """
    if not is_new_trade_signal(message):
        return None

    try:
        # Coin
        coin_match = re.search(r"coin:\s*(\w+)", message, re.IGNORECASE)
        coin = coin_match.group(1).upper() if coin_match else None

        # Side + Leverage
        side_lev = re.search(r"(long|short).*?(\d+)\s*leverage", message, re.IGNORECASE)
        side = side_lev.group(1).capitalize() if side_lev else None
        leverage = int(side_lev.group(2)) if side_lev else None

        # Entry range
        entry_match = re.search(r"entry:\s*([\d.]+)\s*-\s*([\d.]+)", message, re.IGNORECASE)
        entry_from, entry_to = entry_match.groups() if entry_match else (None, None)
        entry_avg = round((float(entry_from) + float(entry_to)) / 2, 6) if entry_from and entry_to else None

        # Targets
        targets = re.findall(r"Target \d:\s*([\d.]+)", message)
        take_profit = float(targets[0]) if targets else None  # Use TP1

        # Stop Loss
        sl_match = re.search(r"stop loss.*?(above|below)?\s*([\d.]+)", message, re.IGNORECASE)
        stop_loss = float(sl_match.group(2)) if sl_match else None

        return {
            "coin": coin,
            "side": side,
            "leverage": leverage,
            "entry": entry_avg,
            "take_profit": take_profit,
            "stop_loss": stop_loss
        }

    except Exception as e:
        print("Failed to parse:", e)
        return None
