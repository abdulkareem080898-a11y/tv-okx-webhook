"""
TradingView to OKX Demo Webhook Receiver
Receives JSON alerts from TradingView and places orders on OKX demo account.
"""
import os
import json
import hmac
import hashlib
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Config
OKX_API_KEY    = os.environ.get("OKX_API_KEY", "")
OKX_SECRET     = os.environ.get("OKX_SECRET", "")
OKX_PASSPHRASE = os.environ.get("OKX_PASSPHRASE", "")
OKX_BASE_URL   = "https://www.okx.com"

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "my_secret_123")

# Trading defaults
INST_ID        = os.environ.get("INST_ID", "ETH-USDT-SWAP")
TRADE_SIZE     = os.environ.get("TRADE_SIZE", "2")
LEVERAGE       = os.environ.get("LEVERAGE", "5")

def sign_request(method, path, body=""):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    msg = timestamp + method.upper() + path + body
    sig = hmac.new(OKX_SECRET.encode(), msg.encode(), hashlib.sha256).digest()
    import base64
    sig_b64 = base64.b64encode(sig).decode()
    return {
        "OK-ACCESS-KEY":        OKX_API_KEY,
        "OK-ACCESS-SIGN":       sig_b64,
        "OK-ACCESS-TIMESTAMP":  timestamp,
        "OK-ACCESS-PASSPHRASE": OKX_PASSPHRASE,
        "Content-Type":         "application/json",
        "x-simulated-trading":  "1",
    }

def okx_post(path, body):
    body_str = json.dumps(body)
    headers  = sign_request("POST", path, body_str)
    resp     = requests.post(OKX_BASE_URL + path, headers=headers, data=body_str, timeout=10)
    return resp.json()

def set_leverage():
    return okx_post("/api/v5/account/set-leverage", {
        "instId":  INST_ID,
        "lever":   LEVERAGE,
        "mgnMode": "cross",
    })

def close_position(pos_side):
    okx_post("/api/v5/trade/close-position", {
        "instId":  INST_ID,
        "mgnMode": "cross",
        "posSide": pos_side,
    })

def place_order(side, pos_side):
    return okx_post("/api/v5/trade/order", {
        "instId":  INST_ID,
        "tdMode":  "cross",
        "side":    side,
        "posSide": pos_side,
        "ordType": "market",
        "sz":      TRADE_SIZE,
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_secret = request.args.get("secret", "")
    if incoming_secret != WEBHOOK_SECRET:
        app.logger.warning("Bad secret - rejected")
        return jsonify({"error": "unauthorized"}), 401

    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "bad JSON"}), 400

    signal = str(data.get("signal", "")).upper()
    if signal == "LONG EXIT":
        signal = "CLOSE"
    symbol   = data.get("symbol", INST_ID)
    price    = data.get("price", "market")
    strategy = data.get("strategy", "unknown")

    app.logger.info("Alert received | signal=%s | symbol=%s | price=%s | strategy=%s", signal, symbol, price, strategy)

    if signal not in ("LONG", "SHORT", "CLOSE"):
        return jsonify({"error": "unknown signal: " + signal}), 400

    set_leverage()
    result = {}

    if signal == "LONG":
        close_position("short")
        time.sleep(0.3)
        result = place_order("buy", "long")
        action = "BUY LONG"
    elif signal == "SHORT":
        close_position("long")
        time.sleep(0.3)
        result = place_order("sell", "short")
        action = "SELL SHORT"
    elif signal == "CLOSE":
        close_position("long")
        close_position("short")
        action = "CLOSE ALL"
        result = {"msg": "positions closed"}

    ok = result.get("code") == "0" if isinstance(result, dict) else False
    app.logger.info("%s %s - OKX response: %s", "OK" if ok else "FAIL", action, result)

    return jsonify({
        "received": True,
        "signal":   signal,
        "action":   action,
        "okx":      result,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": time.time()})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
