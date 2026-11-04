# JK Creator Lab — enquiry-to-order playbook

## Customer path
1. Customer opens @JKCreatorLabBot and sends /packages.
2. Customer sends /order followed by package, public video URL (or topic), and requested improvements.
3. Admin receives a private notification with the customer's Telegram chat ID.
4. Reply privately using the bot admin command: `/reply CHAT_ID message`.
5. Confirm the exact deliverables, whether the video is accessible, the delivery slot, revision limit and final price before requesting payment.
6. Share payment instructions only after the customer accepts the written scope.
7. Verify the actual UPI credit in the bank/UPI app. Never accept a screenshot as proof.
8. Deliver manually and record only anonymous order reference and verified amount in the sales ledger.

## Reply templates

### First response
Thanks for contacting JK Creator Lab. I've received your video and package details. I'll review the scope and confirm availability, deliverables and delivery timing before you make any payment.

### ₹299 SEO Quick Fix
For ₹299, the package covers one video: 3 accurate title options, one description, relevant hashtags/tags and an upload checklist. It does not guarantee views, rankings or subscribers. Please confirm that this scope works for you.

### ₹499 Creator Growth Pack
For ₹499, the package covers one video: 5 title options, description, relevant metadata, thumbnail direction, opening-hook suggestions and an upload checklist. No performance guarantees. Please confirm that this scope works for you.

### ₹999 Pro Optimization
For ₹999, the package covers one video: detailed review, 5 title options, description, relevant tags/hashtags, thumbnail direction and text, opening-hook improvements, suitable chapters and one reasonable revision. No performance guarantees. Please confirm that this scope works for you.

### Scope confirmation before payment
Your order scope is: [package and deliverables]. Delivery target: [date/time or agreed window]. Revisions: [agreed limit]. Total: ₹[amount]. Please reply CONFIRM if you accept. Payment instructions will follow after confirmation.

### Payment safety
Thank you. Please pay only the agreed amount using the payment details sent in this private chat. Never share your UPI PIN or OTP. We will begin after the credit appears in our own bank/UPI app; payment screenshots alone are not accepted.

### Delivery
Your order is ready: [delivery link or attachment]. Please review it and send any agreed revision request within [agreed period].

## Admin bot command
Use `/reply CHAT_ID message` in the private bot chat to reply to a customer. Use `/help` for the command reminder.

## Revenue records
- Keep customer names, phone numbers, video links, UPI IDs and chat IDs out of this public repository.
- Record only anonymous order references and amounts in `orders.csv` and `revenue.csv`.
- Mark revenue verified only after checking the actual credit in your bank app.
- Record refunds separately; never count an enquiry or unpaid order as revenue.

## Ethical promotion
Share the channel only where promotion is allowed. Contribute a useful answer before sharing. Do not mass-DM, scrape members, buy engagement, or promise growth outcomes.
