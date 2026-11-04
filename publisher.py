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


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "@JKCreatorLab").strip()
    if not token:
        fail("Missing TELEGRAM_BOT_TOKEN secret. Add it in GitHub repository Actions secrets.")

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

    index = int(state.get("next_post_index", 0)) % len(posts)
    post = posts[index]
    if not isinstance(post, dict) or not post.get("text"):
        fail(f"Post at index {index} is missing its text.")

    text = str(post["text"]).strip()
    if len(text) > 4096:
        fail("Telegram message exceeds the 4096-character limit.")

    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        fail(f"Telegram API returned HTTP {exc.code}: {detail}")
    except (urllib.error.URLError, TimeoutError) as exc:
        fail(f"Could not reach Telegram: {exc}")

    if not result.get("ok"):
        fail(f"Telegram rejected the message: {result}")

    message_id = result.get("result", {}).get("message_id")
    new_state = {
        "last_published_date": today,
        "last_message_id": message_id,
        "next_post_index": (index + 1) % len(posts),
    }
    STATE_PATH.write_text(
        json.dumps(new_state, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Published post {index + 1}/{len(posts)} to {chat_id}; message_id={message_id}")


if __name__ == "__main__":
    main()
