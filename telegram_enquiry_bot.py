import json, os, sys, urllib.parse, urllib.request, urllib.error
from pathlib import Path

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
ADMIN = os.environ.get("JK_ADMIN_CHAT_ID", "").strip()
if not TOKEN:
    raise SystemExit("ERROR: TELEGRAM_BOT_TOKEN is missing. Check GitHub Actions repository secrets.")

API = f"https://api.telegram.org/bot{TOKEN}/"
STATE = Path("bot_state.json")

try:
    offset = int(json.loads(STATE.read_text()).get("offset", 0))
except (OSError, ValueError, TypeError, json.JSONDecodeError):
    offset = 0

def call(method, data=None):
    req = urllib.request.Request(
        API + method,
        data=urllib.parse.urlencode(data or {}).encode() if data is not None else None
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            payload = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        raise RuntimeError(f"Telegram API HTTP {exc.code} in {method}: {detail}") from exc
    except Exception as exc:
        raise RuntimeError(f"Telegram API connection failed in {method}: {exc}") from exc
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API {method} failed: {payload.get('description', 'unknown error')}")
    return payload.get("result")

def send(chat, message):
    call("sendMessage", {"chat_id": chat, "text": message})

# Validate credentials and detect webhook conflicts before polling.
bot = call("getMe")
webhook = call("getWebhookInfo") or {}
if webhook.get("url"):
    print("Telegram webhook is active; scheduled polling safely skipped.")
    raise SystemExit(0)

updates = call("getUpdates", {
    "offset": offset,
    "timeout": 20,
    "allowed_updates": json.dumps(["message"])
}) or []

processed = 0
for update in updates:
    msg = update.get("message") or {}
    chat = msg.get("chat") or {}
    if chat.get("type") != "private":
        offset = max(offset, int(update["update_id"]) + 1)
        continue

    cid = str(chat.get("id"))
    txt = (msg.get("text") or "").strip()
    command = txt.split(maxsplit=1)[0].split("@", 1)[0].lower() if txt.startswith("/") else ""
    is_admin = bool(ADMIN and cid == ADMIN)

    if is_admin and command == "/reply":
        parts = txt.split(" ", 2)
        if len(parts) == 3 and parts[1].isdigit() and parts[2].strip():
            send(parts[1], parts[2].strip())
            send(cid, "Reply sent to customer.")
        else:
            send(cid, "Usage: /reply CHAT_ID your message")
    elif is_admin and command == "/help":
        send(cid, "Admin tools:\n/reply CHAT_ID message — reply privately to a customer.\nUse your bank app to verify payments; update sales/revenue.csv manually. Never rely on screenshots.")
    elif command == "/start":
        send(cid, "Welcome to JK Creator Lab!\n\n/packages — view services\n/order — submit a private enquiry\n/help — ordering steps\n\nNever send passwords, OTPs or UPI PINs.")
    elif command == "/packages":
        send(cid, "JK Creator Lab packages (one video):\n\n₹299 SEO Quick Fix — 3 accurate title options, description, relevant hashtags/tags and upload checklist.\n\n₹499 Creator Growth Pack — 5 title options, description, metadata, thumbnail direction, hooks and checklist.\n\n₹999 Pro Optimization — detailed review, metadata, thumbnail direction, opening hook improvements, suitable chapters and one revision.\n\nManual delivery target: within 48 hours after scope, slot and payment confirmation. No views/rankings/subscriber guarantees. Use /order.")
    elif command == "/order":
        send(cid, "Send one message with: package (299/499/999), public YouTube video URL (or topic if not uploaded), and what you want improved. We confirm scope and availability before payment. Never send passwords, OTPs, UPI PINs or payment screenshots.")
    elif command == "/help":
        send(cid, "Ordering steps:\n1. Send /order and your package/video details.\n2. We confirm scope and availability.\n3. Payment instructions are provided only after confirmation.\n4. Payment is verified in our bank app.\n5. Delivery is manual. No guaranteed views, rankings or subscribers.")
    elif is_admin:
        send(cid, "Admin tools: send /help for commands.")
    elif txt and ADMIN:
        send(ADMIN, "NEW PRIVATE JK CREATOR LAB ENQUIRY\nCustomer chat ID: " + cid + "\n\n" + txt[:1800] + "\n\nReply with: /reply " + cid + " your message")
        send(cid, "Thanks! Your enquiry has been sent privately. We'll confirm scope and availability before payment. Do not pay yet.")
    elif txt:
        send(cid, "Thanks for contacting JK Creator Lab. Admin notifications are not configured yet. Please do not pay until an admin confirms your order.")

    offset = max(offset, int(update["update_id"]) + 1)
    processed += 1

STATE.write_text(json.dumps({"offset": offset}, indent=2) + "\n")
print(f"Bot @{bot.get('username', 'unknown')} processed {processed} private update(s). Offset saved: {offset}.")
