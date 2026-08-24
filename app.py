"""
TradingView → OKX Demo Webhook Receiver
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

# ── Config ──────────────────────────────────────────────────────────────────
OKX_API_KEY    = os.environ.get("OKX_API_KEY", "")
OKX_SECRET     = os.environ.get("OKX_SECRET", "")
OKX_PASSPHRASE = os.environ.get("OKX_PASSPHRASE", "")
OKX_BASE_URL   = "https://www.okx.com"          # use demo: x-simulated-trading: 1

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "my_secret_123")  # set this in Render env vars

# Trading defaults (override per-alert if you want)
INST_ID        = os.environ.get("INST_ID", "ETH-USDT-SWAP")  # ETH perp swap on demo
TRADE_SIZE     = os.environ.get("TRADE_SIZE", "2")            # 2 contracts ≈ 0.02 ETH ≈ $50 notional
LEVERAGE       = os.environ.get("LEVERAGE", "5")

# ── OKX REST helper ──────────────────────────────────────────────────────────
def sign_request(method: str, path: str, body: str = "") -> dict:
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
            "x-simulated-trading":  "1",          # DEMO account flag
        }

def okx_post(path: str, body: dict) -> dict:
        body_str = json.dumps(body)
        headers  = sign_request("POST", path, body_str)
        resp     = requests.post(OKX_BASE_URL + path, headers=headers, data=body_str, timeout=10)
        return resp.json()

def set_leverage():
        """Set leverage once before trading."""
        return okx_post("/api/v5/account/set-leverage", {
            "instId":  INST_ID,
            "lever":   LEVERAGE,
            "mgnMode": "cross",
        })

def close_position(pos_side: str):
        """Close any open position before entering opposite side."""
        okx_post("/api/v5/trade/close-position", {
            "instId":  INST_ID,
            "mgnMode": "cross",
            "posSide": pos_side,
        })

def place_order(side: str, pos_side: str) -> dict:
        """Place a market order on OKX demo."""
        return okx_post("/api/v5/trade/order", {
            "instId":  INST_ID,
            "tdMode":  "cross",
            "side":    side,       # "buy" or "sell"
            "posSide": pos_side,   # "long" or "short"
            "ordType": "market",
            "sz":      TRADE_SIZE,
        })

# ── Webhook endpoint ──────────────────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
        # 1. Verify secret
        incoming_secret = request.args.get("secret", "")
        if incoming_secret != WEBHOOK_SECRET:
                    app.logger.warning("❌ Bad secret — rejected")
                    return jsonify({"error": "unauthorized"}), 401

        # 2. Parse alert payload
        try:
                    data = request.get_json(force=True) or {}
except Exception:
        return jsonify({"error": "bad JSON"}), 400

    signal   = str(data.get("signal", "")).upper()   # "LONG", "SHORT", "CLOSE", or "LONG EXIT"
    # Normalise "LONG EXIT" (from strategy.order.id) → "CLOSE"
    if signal == "LONG EXIT":
                signal = "CLOSE"
            symbol   = data.get("symbol", INST_ID)
    price    = data.get("price", "market")
    strategy = data.get("strategy", "unknown")

    app.logger.info(f"📡 Alert received | signal={signal} | symbol={symbol} | price={price} | strategy={strategy}")

    if signal not in ("LONG", "SHORT", "CLOSE"):
                return jsonify({"error": f"unknown signal: {signal}"}), 400

    # 3. Set leverage (idempotent)
    set_leverage()

    result = {}

    if signal == "LONG":
                # Close any short first
                close_position("short")
                time.sleep(0.3)
                result = place_order("buy", "long")
                action = "BUY LONG"

elif signal == "SHORT":
            # Close any long first
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
    app.logger.info(f"{'✅' if ok else '❌'} {action} — OKX response: {result}")

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
    
