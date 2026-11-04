import hashlib
import hmac
import json
import os
import urllib.parse
import urllib.request
from flask import Flask, request, jsonify

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ADMIN = os.environ.get("JK_ADMIN_CHAT_ID", "").strip()
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
PUBLIC_URL = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
API = f"https://api.telegram.org/bot{TOKEN}/" if TOKEN else ""
app = Flask(__name__)

def telegram(method, data):
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    req = urllib.request.Request(API + method, data=urllib.parse.urlencode(data).encode())
    with urllib.request.urlopen(req, timeout=20) as response:
        result = json.loads(response.read().decode())
    if not result.get("ok"):
        raise RuntimeError(result.get("description", "Telegram API error"))
    return result.get("result")

def send(chat_id, text):
    telegram("sendMessage", {"chat_id": chat_id, "text": text})

def process_message(message):
    chat = message.get("chat") or {}
    if chat.get("type") != "private":
        return
    chat_id = str(chat.get("id"))
    text = (message.get("text") or "").strip()
    if not text:
        return
    command = text.split(maxsplit=1)[0].split("@", 1)[0].lower() if text.startswith("/") else ""
    is_admin = bool(ADMIN and chat_id == ADMIN)

    if is_admin and command == "/reply":
        parts = text.split(" ", 2)
        if len(parts) == 3 and parts[1].isdigit() and parts[2].strip():
            send(parts[1], parts[2].strip())
            send(chat_id, "Reply sent to customer.")
        else:
            send(chat_id, "Usage: /reply CHAT_ID your message")
    elif is_admin and command == "/help":
        send(chat_id, "Admin tools:\n/reply CHAT_ID message — reply privately to a customer.\nVerify payments in your bank app; record verified sales manually. Never rely on screenshots.")
    elif command == "/start":
        send(chat_id, "Welcome to JK Creator Lab!\n\n/packages — view services\n/order — submit a private enquiry\n/help — ordering steps\n\nNever send passwords, OTPs or UPI PINs.")
    elif command == "/packages":
        send(chat_id, "JK Creator Lab packages (one video):\n\n₹299 SEO Quick Fix — 3 accurate title options, description, relevant hashtags/tags and upload checklist.\n\n₹499 Creator Growth Pack — 5 title options, description, metadata, thumbnail direction, hooks and checklist.\n\n₹999 Pro Optimization — detailed review, metadata, thumbnail direction, opening hook improvements, suitable chapters and one revision.\n\nManual delivery target: within 48 hours after scope, slot and payment confirmation. No views/rankings/subscriber guarantees. Use /order.")
    elif command == "/order":
        send(chat_id, "Send one message with: package (299/499/999), public YouTube video URL (or topic if not uploaded), and what you want improved. We confirm scope and availability before payment. Never send passwords, OTPs, UPI PINs or payment screenshots.")
    elif command == "/help":
        send(chat_id, "Ordering steps:\n1. Send /order and your package/video details.\n2. We confirm scope and availability.\n3. Payment instructions are provided only after confirmation.\n4. Payment is verified in our bank app.\n5. Delivery is manual. No guaranteed views, rankings or subscribers.")
    elif is_admin:
        send(chat_id, "Admin tools: send /help for commands.")
    elif ADMIN:
        send(ADMIN, "NEW PRIVATE JK CREATOR LAB ENQUIRY\nCustomer chat ID: " + chat_id + "\n\n" + text[:1800] + "\n\nReply with: /reply " + chat_id + " your message")
        send(chat_id, "Thanks! Your enquiry has been sent privately. We'll confirm scope and availability before payment. Do not pay yet.")
    else:
        send(chat_id, "Thanks for contacting JK Creator Lab. Admin notifications are not configured yet. Please do not pay until an admin confirms your order.")

# Register or refresh the webhook automatically when the hosted service starts.
if TOKEN and WEBHOOK_SECRET and PUBLIC_URL:
    try:
        telegram("setWebhook", {
            "url": PUBLIC_URL + "/telegram/webhook",
            "secret_token": WEBHOOK_SECRET,
            "allowed_updates": json.dumps(["message"])
        })
        app.logger.info("Telegram webhook registered.")
    except Exception:
        app.logger.exception("Could not register Telegram webhook; check hosting environment variables.")

@app.get("/")
def health():
    return jsonify({"service": "JK Creator Lab Telegram webhook", "status": "ok"})

@app.post("/telegram/webhook")
def webhook():
    if not WEBHOOK_SECRET:
        return jsonify({"error": "Webhook secret is not configured"}), 503
    supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not hmac.compare_digest(supplied, WEBHOOK_SECRET):
        return jsonify({"error": "unauthorized"}), 403
    update = request.get_json(silent=True) or {}
    message = update.get("message")
    if message:
        try:
            process_message(message)
        except Exception:
            app.logger.exception("Failed to process Telegram update")
            return jsonify({"ok": False}), 500
    return jsonify({"ok": True})

@app.get("/setup")
def setup_status():
    # Does not expose credentials or customer data.
    return jsonify({
        "token_configured": bool(TOKEN),
        "admin_chat_configured": bool(ADMIN),
        "webhook_secret_configured": bool(WEBHOOK_SECRET),
        "public_url_detected": bool(PUBLIC_URL),
        "instructions": "Set TELEGRAM_BOT_TOKEN, JK_ADMIN_CHAT_ID and TELEGRAM_WEBHOOK_SECRET in the hosting dashboard. Then register the webhook URL using the Telegram Bot API."
    })

