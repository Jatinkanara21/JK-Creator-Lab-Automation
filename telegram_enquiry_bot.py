import json, os, urllib.parse, urllib.request
from pathlib import Path

TOKEN=os.environ["TELEGRAM_BOT_TOKEN"]
ADMIN=os.environ.get("JK_ADMIN_CHAT_ID","").strip()
API=f"https://api.telegram.org/bot{TOKEN}/"
STATE=Path("bot_state.json")
try: offset=int(json.loads(STATE.read_text()).get("offset",0))
except Exception: offset=0

def call(method,data=None):
    req=urllib.request.Request(API+method,data=urllib.parse.urlencode(data or {}).encode() if data is not None else None)
    with urllib.request.urlopen(req,timeout=30) as response: result=json.loads(response.read().decode())
    if not result.get("ok"): raise RuntimeError("Telegram API request failed")
    return result.get("result")

def send(chat,text): call("sendMessage",{"chat_id":chat,"text":text})

updates=call("getUpdates",{"offset":offset,"timeout":20,"allowed_updates":json.dumps(["message"])}) or []
for update in updates:
    offset=max(offset,int(update["update_id"])+1)
    msg=update.get("message") or {}; chat=msg.get("chat") or {}
    if chat.get("type")!="private": continue
    cid=str(chat.get("id")); txt=(msg.get("text") or "").strip()
    admin=bool(ADMIN and cid==ADMIN)
    if admin and txt.startswith("/reply "):
        parts=txt.split(" ",2)
        if len(parts)==3:
            send(parts[1],parts[2]); send(cid,"Reply sent to customer.")
        else: send(cid,"Usage: /reply CHAT_ID your message")
    elif admin and txt=="/help":
        send(cid,"Admin tools:\n/reply CHAT_ID message — reply privately to a customer.\nUse your bank app to verify payments; update sales/revenue.csv manually. Never rely on screenshots.")
    elif txt.startswith("/start"):
        send(cid,"Welcome to JK Creator Lab!\n\n/packages — view services\n/order — submit a private enquiry\n/help — ordering steps\n\nNever send passwords, OTPs or UPI PINs.")
    elif txt.startswith("/packages"):
        send(cid,"JK Creator Lab packages (one video):\n\n₹299 SEO Quick Fix — 3 accurate title options, description, relevant hashtags/tags and upload checklist.\n\n₹499 Creator Growth Pack — 5 title options, description, metadata, thumbnail direction, hooks and checklist.\n\n₹999 Pro Optimization — detailed review, metadata, thumbnail direction, opening hook improvements, suitable chapters and one revision.\n\nManual delivery target: within 48 hours after scope, slot and payment confirmation. No views/rankings/subscriber guarantees. Use /order.")
    elif txt.startswith("/order"):
        send(cid,"Send one message with: package (299/499/999), public YouTube video URL (or topic if not uploaded), and what you want improved. We confirm scope and availability before payment. Never send passwords, OTPs, UPI PINs or payment screenshots.")
    elif txt.startswith("/help"):
        send(cid,"Ordering steps:\n1. Send /order and your package/video details.\n2. We confirm scope and availability.\n3. Payment instructions are provided only after confirmation.\n4. Payment is verified in our bank app.\n5. Delivery is manual. No guaranteed views, rankings or subscribers.")
    elif admin:
        send(cid,"Admin tools: send /help for commands.")
    elif txt and ADMIN:
        send(ADMIN,"NEW PRIVATE JK CREATOR LAB ENQUIRY\nCustomer chat ID: "+cid+"\n\n"+txt[:1800]+"\n\nReply with: /reply "+cid+" your message")
        send(cid,"Thanks! Your enquiry has been sent privately to JK Creator Lab. We'll confirm scope and availability before payment. Do not pay yet.")
    elif txt:
        send(cid,"Thanks for contacting JK Creator Lab. Admin notifications are not configured yet. Please do not pay until an admin confirms your order.")
STATE.write_text(json.dumps({"offset":offset},indent=2)+"\n")
print("Private enquiry bot processed updates.")
