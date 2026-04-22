import os
import requests
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, make_response, jsonify
from src.services.dm_service import MetaDMService
from src.utils.logger import log

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("WEBHOOK_VERIFY_TOKEN", "my_verify_token")
KEYWORDS     = [kw.upper() for kw in os.environ.get("TRIGGER_KEYWORDS", "РЕТРИТ,ХОЧУ,INFO").split(",")]

dm_service = MetaDMService()




@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta вызывает этот endpoint при регистрации webhook."""
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        log.info("Webhook verified successfully")
        return make_response(challenge, 200)
    log.warning(f"Webhook verification failed: mode={mode} token={token} expected={VERIFY_TOKEN}")
    return make_response("Forbidden", 403)


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """Обрабатывает входящие события от Meta."""
    body = request.get_json(silent=True)
    log.info(f"Webhook POST received: object={body.get('object') if body else 'NO_BODY'}, body={body}")
    if not body:
        log.warning("Rejected webhook: empty body")
        return make_response("Not Found", 404)
    if body.get("object") not in ("instagram", "page"):
        log.warning(f"Unknown object type: {body.get('object')}")
        return make_response("EVENT_RECEIVED", 200)

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            field = change.get("field")
            value = change.get("value", {})

            if field == "comments":
                _handle_comment(value)

    return make_response("EVENT_RECEIVED", 200)


def _handle_comment(value: dict):
    text     = value.get("text", "").upper()
    user_id  = value.get("from", {}).get("id")
    username = value.get("from", {}).get("username", "")
    media_id = value.get("media", {}).get("id", "")

    if not user_id:
        return

    if any(kw in text for kw in KEYWORDS):
        log.info(f"Trigger keyword found in comment by @{username}")
        dm_service.send_dm(igsid=user_id, username=username)


@app.route("/setup")
def setup_subscription():
    """Обменивает токен на долгосрочный (60 дней) и подписывает аккаунт на webhook events."""
    token      = request.args.get("token") or os.environ.get("META_ACCESS_TOKEN", "")
    ig_user    = os.environ.get("IG_USER_ID", "")
    app_id     = os.environ.get("APP_ID", "960470996353710")
    app_secret = os.environ.get("APP_SECRET", "")
    api_ver    = "v25.0"

    if not token or not ig_user:
        return jsonify({"error": "META_ACCESS_TOKEN or IG_USER_ID not set"}), 500

    long_token = token
    if app_secret:
        ex = requests.get(f"https://graph.facebook.com/{api_ver}/oauth/access_token", params={
            "grant_type":        "fb_exchange_token",
            "client_id":         app_id,
            "client_secret":     app_secret,
            "fb_exchange_token": token,
        }, timeout=10)
        ex_data = ex.json()
        if "access_token" in ex_data:
            long_token = ex_data["access_token"]
            expires_in = ex_data.get("expires_in", "unknown")
            log.info(f"Token exchanged for long-lived, expires_in={expires_in}s")
            log.info(f"LONG_LIVED_TOKEN={long_token}")
        else:
            log.warning(f"Token exchange failed: {ex_data}")

    url = f"https://graph.facebook.com/{api_ver}/{ig_user}/subscribed_apps"
    r = requests.post(url, params={
        "subscribed_fields": "comments",
        "access_token": long_token,
    }, timeout=10)

    data = r.json()
    log.info(f"subscribed_apps response [{r.status_code}]: {data}")
    return jsonify({
        "subscribed": data,
        "long_lived_token": long_token if app_secret else "APP_SECRET not set — token not exchanged",
        "note": "Copy long_lived_token to Railway META_ACCESS_TOKEN — valid 60 days"
    })


@app.route("/status")
def status():
    """Проверить текущую подписку IG аккаунта."""
    token   = os.environ.get("META_ACCESS_TOKEN", "")
    ig_user = os.environ.get("IG_USER_ID", "")
    api_ver = "v25.0"

    if not token or not ig_user:
        return jsonify({"error": "META_ACCESS_TOKEN or IG_USER_ID not set"}), 500

    url = f"https://graph.facebook.com/{api_ver}/{ig_user}/subscribed_apps"
    r = requests.get(url, params={"access_token": token}, timeout=10)
    data = r.json()
    log.info(f"subscribed_apps GET [{r.status_code}]: {data}")
    return jsonify({"status": r.status_code, "response": data})


def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    run()
