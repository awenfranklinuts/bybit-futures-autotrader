# close_executor.py

import os
import time
import hmac
import hashlib
import requests
import json
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load credentials
load_dotenv(dotenv_path="config/.env")

USE_TESTNET = os.getenv("BYBIT_USE_TESTNET", "false").lower() == "true"
API_KEY = os.getenv("BYBIT_TESTNET_API_KEY") if USE_TESTNET else os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_TESTNET_API_SECRET") if USE_TESTNET else os.getenv("BYBIT_API_SECRET")
BASE_URL = "https://api-testnet.bybit.com" if USE_TESTNET else "https://api.bybit.com"
RECV_WINDOW = "5000"

def generate_signature(timestamp: str, api_key: str, recv_window: str, query_string: str, secret: str) -> str:
    prehash_string = f"{timestamp}{api_key}{recv_window}{query_string}"
    return hmac.new(secret.encode("utf-8"), prehash_string.encode("utf-8"), hashlib.sha256).hexdigest()

def close_position(symbol: str):
    timestamp = str(int(time.time() * 1000))
    endpoint = "/v5/position/close-pnL"
    url = BASE_URL + endpoint

    body = {
        "category": "linear",
        "symbol": symbol,
        "qty": "auto"  # Let Bybit close full position automatically
    }

    body_json = json.dumps(body, separators=(',', ':'), ensure_ascii=False)
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
