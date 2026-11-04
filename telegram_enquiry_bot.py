import json, os, urllib.parse, urllib.request
from pathlib import Path

token=os.environ["TELEGRAM_BOT_TOKEN"]
admin=os.environ.get("JK_ADMIN_CHAT_ID","").strip()
api="https://api.telegram.org/bot"+token+"/"
state_file=Path("bot_state.json")
try: offset=int(json.loads(state_file.read_text()).get("offset",0))
except Exception: offset=0

def api_call(method, data=None):
    req=urllib.request.Request(api+method, data=urllib.parse.urlencode(data or {}).encode() if data is not None else None)
    with urllib.request.urlopen(req,timeout=30) as response:
        result=json.loads(response.read().decode())
    if not result.get("ok"): raise RuntimeError("Telegram API returned an error")
    return result.get("result")

def send(chat,text):
    api_call("sendMessage",{"chat_id":chat,"text":text})

updates=api_call("getUpdates",{"offset":offset,"timeout":20,"allowed_updates":json.dumps(["message"])}) or []
for update in updates:
    offset=max(offset,int(update["update_id"])+1)
    msg=update.get("message",{})
    chat=msg.get("chat",{})
    if chat.get("type")!="private": continue
    chat_id=str(chat.get("id"))
    text=(msg.get("text") or "").strip()
    if text.startswith("/start"):
        send(chat_id,"Welcome to JK Creator Lab!\n\n/packages — view services\n/order — submit a private enquiry\n/myid — show your Telegram chat ID for owner setup\n\nNever send passwords, OTPs or UPI PINs.")
    elif text.startswith("/myid"):
        send(chat_id,"Your Telegram chat ID: "+chat_id+"\nKeep it private. The owner can add it as GitHub Actions secret JK_ADMIN_CHAT_ID.")
    elif text.startswith("/packages"):
        send(chat_id,"JK Creator Lab packages:\n\n₹299 SEO Quick Fix — 3 title options, description, relevant hashtags/tags and upload checklist.\n\n₹499 Creator Growth Pack — metadata, thumbnail direction, hooks and checklist.\n\n₹999 Pro Optimization — detailed review, metadata, thumbnail direction and one revision.\n\nManual delivery target: within 48 hours after scope and slot confirmation. No views or ranking guarantees. Use /order to enquire. Do not pay until confirmed.")
    elif text.startswith("/order"):
        send(chat_id,"Reply here with your package (299/499/999), YouTube video URL, and what you want improved. Do not send passwords, OTPs, UPI PINs or payment screenshots.")
    elif admin:
        send(admin,"NEW PRIVATE JK CREATOR LAB ENQUIRY\nCustomer chat ID: "+chat_id+"\nUsername: @"+str(msg.get("from",{}).get("username","not_set"))+"\n\n"+text[:2000])
        send(chat_id,"Thanks. Your enquiry has been forwarded privately. Please wait for confirmation before paying.")
    else:
        send(chat_id,"Thanks for contacting JK Creator Lab. Private order notifications are not configured yet. Please do not pay until an admin confirms your order.")
state_file.write_text(json.dumps({"offset":offset},indent=2)+"\n")
print("Telegram enquiry polling completed.")
