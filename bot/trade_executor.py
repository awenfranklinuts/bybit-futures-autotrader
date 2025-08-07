import os
import time
import hmac
import hashlib
import requests
import json
from dotenv import load_dotenv
from collections import OrderedDict
from urllib.parse import urlencode

# Load credentials
load_dotenv(dotenv_path="config/.env")

USE_TESTNET = os.getenv("BYBIT_USE_TESTNET", "false").lower() == "true"

API_KEY = os.getenv("BYBIT_TESTNET_API_KEY") if USE_TESTNET else os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_TESTNET_API_SECRET") if USE_TESTNET else os.getenv("BYBIT_API_SECRET")
BASE_URL = "https://api-testnet.bybit.com" if USE_TESTNET else "https://api.bybit.com"
RECV_WINDOW = "5000"

# ----------------------------------------
def generate_signature(timestamp: str, api_key: str, recv_window: str, body_or_query: str, secret: str) -> str:
    prehash_string = f"{timestamp}{api_key}{recv_window}{body_or_query}"
    print("Prehash string:", prehash_string)
    return hmac.new(secret.encode("utf-8"), prehash_string.encode("utf-8"), hashlib.sha256).hexdigest()

# ----------------------------------------
def get_balance():
    timestamp = str(int(time.time() * 1000))
    endpoint = "/v5/account/wallet-balance"
    url = BASE_URL + endpoint
    params = {
        "accountType": "UNIFIED"
    }

    query_str = urlencode(params)
    sign = generate_signature(timestamp, API_KEY, RECV_WINDOW, query_str, API_SECRET)

    headers = {
        "Content-Type": "application/json",
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": RECV_WINDOW,
        "X-BAPI-SIGN": sign
    }

    response = requests.get(f"{url}?{query_str}", headers=headers)
    result = response.json()

    if result.get("retCode") != 0:
        print(f"❌ API Error: {result.get('retMsg')}")
        return 0.0

    try:
        usdt_balance = float(result["result"]["list"][0]["totalAvailableBalance"])
        print(f"✅ Available USDT Balance: {usdt_balance}")
        return usdt_balance
    except Exception as e:
        print("⚠️ Failed to parse balance:", e)
        print("Raw response:", json.dumps(result, indent=2))
        return 0.0

# ----------------------------------------
def get_last_price(symbol: str = "BTCUSDT") -> float:
    url = f"{BASE_URL}/v5/market/tickers"
    params = {"category": "linear", "symbol": symbol}
    response = requests.get(url, params=params)
    return float(response.json()["result"]["list"][0]["lastPrice"])

# ----------------------------------------
def place_order(
    symbol: str,
    side: str,
    order_type: str,
    qty: float,
    leverage: int = 10,
    take_profit: float = None,
    stop_loss: float = None
):
    if qty <= 0:
        print("❌ Quantity too low. Aborting order.")
        return

    timestamp = str(int(time.time() * 1000))
    endpoint = "/v5/order/create"
    url = BASE_URL + endpoint

    body = OrderedDict([
        ("category", "linear"),
        ("symbol", symbol),
        ("side", side),
        ("orderType", order_type),
        ("qty", str(qty)),
        ("leverage", str(leverage)),
        ("timeInForce", "GoodTillCancel"),
        ("recvWindow", RECV_WINDOW)
    ])

    if take_profit:
        body["takeProfit"] = str(take_profit)
    if stop_loss:
        body["stopLoss"] = str(stop_loss)

    body_json = json.dumps(body, separators=(', ', ': '), ensure_ascii=False)
    sign = generate_signature(timestamp, API_KEY, RECV_WINDOW, body_json, API_SECRET)

    headers = {
        "Content-Type": "application/json",
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": RECV_WINDOW,
        "X-BAPI-SIGN": sign
    }

    response = requests.post(url, headers=headers, json=body)

    print("Request sent to:", url)
    print("Body:", body)
    print("Signature:", sign)
    print("Status Code:", response.status_code)
    print("Response:", response.json())

    return response.json()

# ----------------------------------------
if __name__ == "__main__":
    # Step 1: Get balance
    balance = get_balance()

    # Step 2: Get live BTC price
    btc_price = get_last_price()
    leverage = 10

    # Step 3: Calculate safe qty using 90% of margin
    usdt_to_use = balance * 0.9
    qty = round((usdt_to_use * leverage) / btc_price, 3)

    print(f"💡 BTC Price: {btc_price}")
    print(f"💡 Using qty={qty} BTC with leverage={leverage}")

    # Step 4: Set TP/SL dynamically
    take_profit = round(btc_price * 1.02, 2)
    stop_loss = round(btc_price * 0.98, 2)

    # Step 5: Place order
    place_order(
        symbol="BTCUSDT",
        side="Buy",
        order_type="Market",
        qty=qty,
        take_profit=take_profit,
        stop_loss=stop_loss
    )
