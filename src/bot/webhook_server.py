import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, make_response
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


def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    run()
