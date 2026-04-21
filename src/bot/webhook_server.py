import os
import requests as _requests
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, make_response
from src.services.dm_service import MetaDMService
from src.utils.logger import log

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("WEBHOOK_VERIFY_TOKEN", "my_verify_token")
KEYWORDS     = [kw.upper() for kw in os.environ.get("TRIGGER_KEYWORDS", "РЕТРИТ,ХОЧУ,INFO").split(",")]

dm_service = MetaDMService()


def _subscribe_to_comments():
    ig_user_id = os.environ.get("IG_USER_ID", "")
    token      = os.environ.get("META_ACCESS_TOKEN", "")
    if not ig_user_id or not token:
        log.warning("Skipping webhook subscription: IG_USER_ID or META_ACCESS_TOKEN missing")
        return
    url = f"https://graph.instagram.com/v25.0/{ig_user_id}/subscribed_apps"
    try:
        r = _requests.post(url, params={"subscribed_fields": "comments", "access_token": token}, timeout=10)
        data = r.json()
        if data.get("success"):
            log.info("Subscribed to Instagram comment webhooks OK")
        else:
            log.warning(f"Webhook subscription response: {data}")
    except Exception as e:
        log.error(f"Webhook subscription error: {e}")

_subscribe_to_comments()


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta вызывает этот endpoint при регистрации webhook."""
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        log.info("Webhook verified successfully")
        return make_response(challenge, 200)
    log.warning("Webhook verification failed")
    return make_response("Forbidden", 403)


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """Обрабатывает входящие события от Meta."""
    body = request.get_json(silent=True)
    if not body or body.get("object") != "instagram":
        return make_response("Not Found", 404)

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


def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    run()
