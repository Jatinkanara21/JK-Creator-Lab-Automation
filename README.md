# JK Creator Lab Automation

A zero-paid-AI daily Telegram publisher for **@JK_Creator_Lab_21**. It uses a prepared content library and GitHub Actions.

## What it does

- Publishes one original creator-growth post per India calendar day.
- Runs daily at **9:00 AM Asia/Kolkata** (03:30 UTC).
- Rotates through `content/posts.json`.
- Records the last successful publication in `state.json` to avoid duplicate posts on reruns that day.
- Uses Python's standard library only; no OpenAI API, Make.com, or third-party Python packages.

## One-time setup

1. Open the Telegram bot chat and send `/start` if you have not already.
2. Add **@JKCreatorLabBot** to **@JK_Creator_Lab_21** as an administrator with permission to post messages.
3. In this GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret**.
4. Create a secret named `TELEGRAM_BOT_TOKEN` and paste the bot token from BotFather. Never put the token in source code, commits, screenshots, or chat messages.
5. Open **Actions → JK Creator Lab — Daily Telegram Publisher → Run workflow** to test the first post.

The workflow already targets `@JK_Creator_Lab_21`. To change the channel, edit the `TELEGRAM_CHAT_ID` value in `.github/workflows/daily-publish.yml`.

## Edit the content

Add or edit objects in `content/posts.json`. Each object must have a `text` field. Telegram messages must be no longer than 4096 characters. Keep posts accurate, original, useful, and non-spammy.

## Check status

- GitHub → **Actions** shows each run and its logs.
- A successful run prints the Telegram message ID and updates `state.json`.
- A failed run displays the Telegram API error in the workflow log.
- If a post has already been recorded for the current India date, a rerun safely skips it.

## Important

GitHub Actions usage is subject to GitHub account and repository limits. Scheduled jobs can be delayed by GitHub. This project does not guarantee audience growth or income. Review content and comply with Telegram and YouTube rules.


## Monetization v2.0 (free tools, manual approval)

### What was added
- `content/promotions.json`: product/service offers. All starter offers are `draft` and cannot be published until explicitly changed to `approved`.
- `content/affiliate-posts.json`: affiliate copy template with a mandatory disclosure field and an empty URL placeholder. Never publish until the URL is a real, verified affiliate link and the disclosure is visible.
- `publish_promotion.py` and `.github/workflows/publish-approved-promotion.yml`: separate, manually triggered promotion publisher. It only publishes an exact promotion ID whose status is `approved`, requires the UPI secret, and blocks duplicate IDs.
- `sales/`: blank CSV templates for leads, orders and verified revenue, plus publication records.

### Safe setup before any paid offer
1. Add a repository Actions secret named `JK_UPI_ID` containing the business UPI ID you have verified. Do not add a UPI PIN, OTP, bank password or QR login credential. The UPI ID will be visible in the public Telegram promotion when the workflow publishes.
2. Review the price, scope, delivery time, revision/refund terms and claims in `content/promotions.json`. Change only the chosen offer's `status` from `draft` to `approved` after review.
3. Open Actions → **JK Creator Lab — Approved Promotion Publisher** → Run workflow. Enter the exact promotion ID, for example `seo-starter-001`. The action fails closed if the item is still a draft, the UPI secret is missing, or that ID was already published.
4. The ordinary daily educational publisher remains separate and keeps its 09:00 Asia/Kolkata schedule. Promotional posts are never included in that automatic rotation.

### Affiliate disclosure
Use `content/affiliate-posts.json` as a drafting template. Before sharing an affiliate recommendation, add a genuine tracked URL and a clear disclosure near the link, such as: "Affiliate link: JK Creator Lab may earn a commission if you purchase through this link, at no extra cost to you." Check the program's current terms and applicable advertising disclosure rules. Do not imply personal testing unless you actually tested the product. Affiliate templates are drafts; they are not automatically published.

### Channel-only customer contact and payment handling
- This setup does not create a private customer inbox or payment gateway. The channel is the only public contact surface.
- Telegram channel comments require a linked discussion group. If comments are not enabled, customers cannot privately place an order through the channel alone; do not claim that they can. Consider enabling channel comments or publishing a clear order-instructions post.
- A UPI ID is a payment destination, not an order-management system. Confirm every payment in your own bank/UPI app before marking an order paid or delivering anything.
- Do not ask customers to send UPI PINs, OTPs, passwords or full payment credentials. Do not treat a payment screenshot as proof of receipt.
- Keep customer names, phone numbers, UPI IDs and addresses out of this public repository. Use anonymous order references in the CSVs. Do not commit identifiable customer records to a public repo.
- Publish clear delivery, revision, cancellation and refund terms before accepting payment.

### Manual sales tracking
Use the blank CSV headers in `sales/leads.csv`, `sales/orders.csv` and `sales/revenue.csv` as schemas. Keep actual customer-level records in a private local spreadsheet, not this public repository. Record revenue only after payment is independently verified; subtract actual fees and refunds when calculating net revenue.

### Important limitations
This is a lightweight publishing and recordkeeping starter, not an automated storefront. It does not accept payments, verify UPI transfers, deliver files, manage customer support, or guarantee sales/income. GitHub Actions schedules may be delayed and are subject to GitHub usage limits.
