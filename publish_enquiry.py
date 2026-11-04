#!/usr/bin/env python3
"""Publish an enquiry-only post. This does not request or accept payment."""
import json, os, sys, urllib.parse, urllib.request, urllib.error

token=os.environ.get("TELEGRAM_BOT_TOKEN","").strip()
chat=os.environ.get("TELEGRAM_CHAT_ID","@JK_Creator_Lab_21").strip()
if not token:
    raise SystemExit("Missing TELEGRAM_BOT_TOKEN")
message = """🚀 JK CREATOR LAB — YOUTUBE SEO QUICK FIX

Need help preparing your next YouTube upload?

₹299 — YouTube Video SEO Quick Fix
• 3 accurate title options
• One optimized description
• Relevant hashtags and tags
• Short upload checklist

We review the actual video/topic before preparing the recommendations. Manual delivery target: within 48 hours after the scope and delivery slot are confirmed.

HOW TO ENQUIRE
Comment ORDER below this post. An admin will reply to confirm availability and explain the next steps.

IMPORTANT
• This is an enquiry post, not a payment request.
• Do not send money until the order scope, delivery slot and private delivery method are confirmed.
• Never post phone numbers, UPI IDs, transaction IDs, screenshots, passwords, PINs or OTPs in public comments.
• No views, rankings or subscriber results are guaranteed.

— JK Creator Lab"""
data=urllib.parse.urlencode({"chat_id":chat,"text":message,"disable_web_page_preview":"true"}).encode()
req=urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",data=data,method="POST")
try:
    with urllib.request.urlopen(req,timeout=25) as r:
        result=json.loads(r.read().decode())
except urllib.error.HTTPError as e:
    raise SystemExit(f"Telegram HTTP {e.code}: {e.read().decode(errors='replace')}")
if not result.get("ok"):
    raise SystemExit(f"Telegram API error: {result}")
print("Enquiry-only post published. message_id="+str(result["result"]["message_id"]))
