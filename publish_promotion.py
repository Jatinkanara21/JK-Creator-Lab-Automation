#!/usr/bin/env python3
"""Publish one manually approved promotion. Never publishes drafts."""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROMOTIONS = ROOT / "content" / "promotions.json"
PUBLISHED = ROOT / "sales" / "published_promotions.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def telegram_call(token: str, method: str, values: dict) -> dict:
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=urllib.parse.urlencode(values).encode("utf-8"),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        fail(f"Telegram HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}")
    except (urllib.error.URLError, TimeoutError) as exc:
        fail(f"Telegram connection failed: {exc}")
    if not result.get("ok"):
        fail(f"Telegram rejected request: {result}")
    return result


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "@JK_Creator_Lab_21").strip()
    promotion_id = os.environ.get("PROMOTION_ID", "").strip()
    upi_id = os.environ.get("JK_UPI_ID", "").strip()
    if not token or not promotion_id:
        fail("Missing TELEGRAM_BOT_TOKEN or PROMOTION_ID.")
    if not upi_id:
        fail("Missing JK_UPI_ID secret. Add your verified UPI ID to repository Actions secrets before publishing a paid offer.")

    try:
        promotions = json.loads(PROMOTIONS.read_text(encoding="utf-8"))
        published = json.loads(PUBLISHED.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Cannot read promotion data: {exc}")

    matches = [p for p in promotions if p.get("id") == promotion_id]
    if len(matches) != 1:
        fail(f"Promotion ID {promotion_id!r} was not found uniquely.")
    promotion = matches[0]
    if promotion.get("status") != "approved":
        fail("Promotion is not approved. Change its status to 'approved' in content/promotions.json only after reviewing its claims, price, delivery and terms.")
    published_ids = published.setdefault("published_ids", [])
    if promotion_id in published_ids:
        fail("This promotion ID has already been published. Use a new ID for a new campaign.")

    price = promotion.get("price_inr")
    if not isinstance(price, int) or price <= 0:
        fail("Promotion must have a positive integer price_inr.")
    title = str(promotion.get("title", "")).strip()
    description = str(promotion.get("description", "")).strip()
    delivery = str(promotion.get("delivery", "")).strip()
    disclosure = str(promotion.get("disclosure", "")).strip()
    if not all((title, description, delivery, disclosure)):
        fail("Promotion needs title, description, delivery and disclosure text.")

    message = (
        f"📣 JK CREATOR LAB — OFFER\n\n{title}\n\n{description}\n\n"
        f"Price: ₹{price}\nUPI ID: {upi_id}\n\n"
        f"Payment note: Add your order ID in the UPI note if provided after placing your order. "
        f"Please do not share your UPI PIN or OTP. Payment is confirmed only after we verify the credit.\n\n"
        f"Delivery: {delivery}\n\n{disclosure}\n\n"
        "For order instructions, follow the pinned instructions in this channel."
    )
    if len(message) > 4096:
        fail("Promotion message exceeds Telegram's 4096-character limit.")

    result = telegram_call(token, "sendMessage", {
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": "true",
    })
    message_id = result.get("result", {}).get("message_id")
    published_ids.append(promotion_id)
    PUBLISHED.write_text(json.dumps(published, indent=2) + "\n", encoding="utf-8")
    print(f"Published approved promotion {promotion_id}; message_id={message_id}")


if __name__ == "__main__":
    main()
