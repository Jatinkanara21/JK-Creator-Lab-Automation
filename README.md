# JK Creator Lab Automation

A zero-paid-AI daily Telegram publisher for **@JKCreatorLab**. It uses a prepared content library and GitHub Actions.

## What it does

- Publishes one original creator-growth post per India calendar day.
- Runs daily at **9:00 AM Asia/Kolkata** (03:30 UTC).
- Rotates through `content/posts.json`.
- Records the last successful publication in `state.json` to avoid duplicate posts on reruns that day.
- Uses Python's standard library only; no OpenAI API, Make.com, or third-party Python packages.

## One-time setup

1. Open the Telegram bot chat and send `/start` if you have not already.
2. Add your bot to **@JKCreatorLab** as an administrator with permission to post messages.
3. In this GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret**.
4. Create a secret named `TELEGRAM_BOT_TOKEN` and paste the bot token from BotFather. Never put the token in source code, commits, screenshots, or chat messages.
5. Open **Actions → JK Creator Lab — Daily Telegram Publisher → Run workflow** to test the first post.

The workflow already targets `@JKCreatorLab`. To change the channel, edit the `TELEGRAM_CHAT_ID` value in `.github/workflows/daily-publish.yml`.

## Edit the content

Add or edit objects in `content/posts.json`. Each object must have a `text` field. Telegram messages must be no longer than 4096 characters. Keep posts accurate, original, useful, and non-spammy.

## Check status

- GitHub → **Actions** shows each run and its logs.
- A successful run prints the Telegram message ID and updates `state.json`.
- A failed run displays the Telegram API error in the workflow log.
- If a post has already been recorded for the current India date, a rerun safely skips it.

## Important

GitHub Actions usage is subject to GitHub account and repository limits. Scheduled jobs can be delayed by GitHub. This project does not guarantee audience growth or income. Review content and comply with Telegram and YouTube rules.
