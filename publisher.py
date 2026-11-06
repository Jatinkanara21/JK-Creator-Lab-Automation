#!/usr/bin/env python3
"""Publish one prepared JK Creator Lab post per India calendar day."""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "state.json"
POSTS_PATH = ROOT / "content" / "posts.json"
TIMEZONE = ZoneInfo("Asia/Kolkata")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def telegram_call(token: str, method: str, values: dict | None = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(values).encode("utf-8") if values else None
    request = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        fail(f"Telegram API returned HTTP {exc.code}: {detail}")
    except (urllib.error.URLError, TimeoutError) as exc:
        fail(f"Could not reach Telegram: {exc}")
    if not result.get("ok"):
        fail(f"Telegram {method} failed: {result}")
    return result



def post_ready_for_today(post: object, chat_id: str, today: str) -> tuple[bool, str]:
    """Fail closed: publish only explicitly approved, complete, non-promotional Telegram text."""
    if not isinstance(post, dict):
        return False, "not a post object"
    if post.get("status") not in {"approved", "ready"}:
        return False, "status is not explicitly approved/ready"
    if post.get("content_type") not in {"educational", "creator_tip"}:
        return False, "content_type is not educational/creator_tip"
    if post.get("destination") != chat_id:
        return False, "destination is missing or does not match this channel"
    if post.get("is_promotional") is not False:
        return False, "is_promotional must be explicitly false"
    if post.get("rights_status") not in {"original", "licensed", "public_domain", "cleared"}:
        return False, "rights_status is missing or not cleared"
    if post.get("synthetic_media") is not False:
        return False, "synthetic_media must be explicitly false for this text-only workflow"
    if post.get("media") not in (None, []):
        return False, "this workflow accepts text-only Telegram posts"
    publish_at = post.get("publish_at")
    if not isinstance(publish_at, str) or not publish_at.strip():
        return False, "publish_at is missing"
    try:
        scheduled = datetime.fromisoformat(publish_at.strip().replace("Z", "+00:00"))
    except ValueError:
        return False, "publish_at is not a valid ISO-8601 timestamp"
    if scheduled.tzinfo is None:
        return False, "publish_at must include a timezone offset"
    local_time = scheduled.astimezone(TIMEZONE)
    if local_time.date().isoformat() != today or (local_time.hour, local_time.minute) != (9, 0):
        return False, "publish_at must be today's 09:00 Asia/Kolkata slot"
    if not isinstance(post.get("text"), str) or not post["text"].strip():
        return False, "text is missing"
    text_lower = post["text"].lower()
    sales_markers = (
        "₹",
        "seo quick fix",
        "creator growth pack",
        "pro optimization",
        "need help with one youtube video",
        "?start=order",
    )
    if any(marker in text_lower for marker in sales_markers):
        return False, "contains a price, sales offer or order CTA"
    return True, ""


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "@JK_Creator_Lab_21").strip()
    if not token:
        fail("Missing TELEGRAM_BOT_TOKEN secret. Add it in GitHub repository Actions secrets.")

    # Identify the bot represented by the saved secret without exposing its token.
    bot = telegram_call(token, "getMe").get("result", {})
    bot_username = bot.get("username", "unknown")
    print(f"Authenticated Telegram bot: @{bot_username}")
    if bot_username.lower() != "jkcreatorlabbot":
        fail("The TELEGRAM_BOT_TOKEN secret belongs to a different bot. Update it with the token for @JKCreatorLabBot.")

    # Diagnose the exact target and the bot's membership before attempting to post.
    chat = telegram_call(token, "getChat", {"chat_id": chat_id}).get("result", {})
    print(f"Resolved destination: title={chat.get('title', 'unknown')!r}, username=@{chat.get('username', 'unknown')}, type={chat.get('type', 'unknown')}")
    membership = telegram_call(token, "getChatMember", {
        "chat_id": chat_id,
        "user_id": bot.get("id"),
    }).get("result", {})
    status = membership.get("status", "unknown")
    print(f"Bot channel membership status: {status}")
    if status not in ("administrator", "creator"):
        fail(f"Bot @{bot_username} is not an administrator of {chat_id}; Telegram reports status={status!r}. Add this exact bot to the resolved channel and grant Post Messages.")

    today = datetime.now(TIMEZONE).date().isoformat()
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        posts = json.loads(POSTS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Could not read content/state files: {exc}")

    if state.get("last_published_date") == today:
        print(f"A post is already recorded for {today} (India time). Skipping duplicate.")
        return
    if not isinstance(posts, list) or not posts:
        fail("content/posts.json must contain a non-empty list of posts.")

    start_index = int(state.get("next_post_index", 0)) % len(posts)
    selected = None
    for step in range(len(posts)):
        candidate_index = (start_index + step) % len(posts)
        candidate = posts[candidate_index]
        ready, reason = post_ready_for_today(candidate, chat_id, today)
        if ready:
            selected = (candidate_index, candidate)
            break
        print(f"Skipping post {candidate_index + 1}/{len(posts)}: {reason}.")

    if selected is None:
        print("No explicitly approved, complete, non-promotional Telegram text post is ready for today's 09:00 Asia/Kolkata slot. Nothing was published.")
        return

    index, post = selected
    message = str(post["text"]).strip()
    if len(message) > 4096:
        fail("Telegram message exceeds the 4096-character limit.")

    result = telegram_call(token, "sendMessage", {
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": "true",
    })
    message_id = result.get("result", {}).get("message_id")
    new_state = {
        "last_published_date": today,
        "last_message_id": message_id,
        "next_post_index": (index + 1) % len(posts),
    }
    STATE_PATH.write_text(json.dumps(new_state, indent=2) + "\n", encoding="utf-8")
    print(f"Published post {index + 1}/{len(posts)} to {chat_id}; message_id={message_id}")


if __name__ == "__main__":
    main()
