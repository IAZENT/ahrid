"""Seed ~500 AHRID training scenarios for non-technical SME employees.

Design rules:
  1. Each scenario is a complete workplace mini-story ending with
     "What should you do?"
  2. All 4 answer options are LENGTH-BALANCED (max 12-char spread)
     so users cannot guess by picking the longest answer.
  3. Nepal/Kathmandu Valley context throughout (eSewa, Ncell, Khalti,
     Pathao, Daraz, WorldLink, NTC, IRD, etc.).
  4. Themed groups per category. options match the situations they
     are paired with.

Usage:
    python seed_scenarios.py
"""
from __future__ import annotations

import random

from app import create_app
from app.extensions import db
from app.models.attempt import Attempt
from app.models.scenario import Scenario

random.seed(42)
LETTERS = ["A", "B", "C", "D"]
MAX_SPREAD = 12  # max char difference between longest and shortest option


def _make(title, content, options, correct_idx,
          explanation, red_flags, tip,
          category, difficulty, role="all"):
    """Build a Scenario dict. Skips if option lengths are too unbalanced."""
    lengths = [len(o) for o in options]
    spread = max(lengths) - min(lengths)
    if spread > MAX_SPREAD:
        return None

    placement = hash(content + title) % 4
    correct_text = options[correct_idx]
    distractors = [o for i, o in enumerate(options) if i != correct_idx]
    random.shuffle(distractors)
    final = list(distractors)
    final.insert(placement, correct_text)
    return dict(
        title=title[:200], content=content, question_type="mcq",
        category=category, difficulty=difficulty, target_roles=role,
        correct_answer=LETTERS[placement],
        option_a=final[0], option_b=final[1], option_c=final[2], option_d=final[3],
        explanation=explanation, red_flags=red_flags, learning_tip=tip,
        source="manual", is_active=True,
    )


def _add(s):
    if s is not None:
        SCENARIOS.append(s)


SCENARIOS: list[dict] = []


# ════════════════════════════════════════════════════════════════════════════
# 1. PHISHING EMAIL. ~65 scenarios
# ════════════════════════════════════════════════════════════════════════════

def _phishing():
    C = "phishing_email"

    # --- D1: Obvious phishing with clear red flags ---
    items_d1 = [
        ("Ncell Bill Overdue Email",
         "You get an email saying your Ncell bill is overdue and your number will be cut off in 2 hours. There is a big red 'Pay Now' button. You were not expecting any bill.\n\nWhat should you do?",
         ["Ignore it and check via the Ncell app", "Click 'Pay Now' to fix it right away",
          "Reply asking if the email is legit", "Forward the email to all contacts"],
         0, "Ncell will not threaten disconnection by email. Check via the official app.",
         "Urgency, unknown sender, unexpected bill", "Unexpected + urgent = suspicious. Check the app.", "all"),

        ("Free Daraz Gift Card Email",
         "An email says you won a Rs. 5,000 Daraz gift card. Click a link and enter your phone number to claim it. You never entered any contest.\n\nWhat should you do?",
         ["Delete it. you entered no contest", "Click the link to claim your prize",
          "Enter your phone number to check", "Share the link with your friends"],
         0, "No contest entry = no real prize. This is a data harvesting scam.",
         "Free prize, no contest entered, claim link", "No entry = no prize. Just delete it.", "all"),

        ("Password Expiry Warning",
         "An email from 'IT Support' says your email password expires tonight. Click here to update. But your IT team usually helps in person.\n\nWhat should you do?",
         ["Walk to IT and ask if they sent it", "Click the link and update the password",
          "Reply with your current password", "Ignore it and hope for the best"],
         0, "Real IT teams do not send generic password links. Verify in person.",
         "Password urgency, generic greeting, link", "When in doubt, verify in person.", "all"),

        ("Aramex Package Fee Email",
         "An email from 'Aramex Nepal' says your package needs a Rs. 500 customs fee paid online. You are not expecting any package at all.\n\nWhat should you do?",
         ["Delete it. you expect no delivery", "Pay Rs. 500 since it is small",
          "Click the link to see the package", "Call the number in the email"],
         0, "No expected package = no real delivery email. Just delete it.",
         "Unexpected delivery, small fee trick", "Not expecting a package? It is a scam.", "all"),

        ("Netflix Account Suspended",
         "An email says your Netflix account is suspended. Update your card details by clicking the link. You do have a Netflix account.\n\nWhat should you do?",
         ["Open Netflix directly from your app", "Click the email link to fix it now",
          "Reply with your card information", "Wait to see if Netflix stops working"],
         0, "Always go directly to the app or website, never via email links.",
         "Account suspension, payment urgency", "Go to the website yourself, not via emails.", "all"),

        ("Lottery Win Notification",
         "You receive an email saying you won a UK lottery worth $50,000. Send your bank details to receive the funds. You never bought a UK lottery ticket.\n\nWhat should you do?",
         ["Delete it. you never entered this", "Send bank details to claim it now",
          "Reply asking for more information", "Forward it to your bank to verify"],
         0, "You cannot win a lottery you never entered. This steals bank info.",
         "Foreign lottery, bank details request", "No entry = no win. Always true.", "all"),

        ("Voice Message Notification",
         "An email says you have an unread voice message. Click the link to listen. Your company does not use email-based voicemail.\n\nWhat should you do?",
         ["Delete it. your company has no such system", "Click the link to hear the message",
          "Forward it to IT asking about the system", "Reply asking who left the message"],
         0, "If your company does not use this system, the email is fake.",
         "Unknown service, link to 'listen'", "Know your company tools. Unknown ones = fake.", "all"),

        ("Leave Balance Review Email",
         "An email says your yearly leave balance is incorrect and needs immediate review via a link. HR usually sends leave info through the internal portal.\n\nWhat should you do?",
         ["Check the leave balance on your portal", "Click the link to review your balance",
          "Reply to the email with your staff ID", "Ask a coworker if they got it too"],
         0, "HR uses the internal portal for leave data, not random email links.",
         "Different channel than usual, urgency", "Use the channel HR always uses.", "all"),

        ("Microsoft Storage Full Warning",
         "An email warns your Microsoft 365 storage is full. You will lose files in 24 hours unless you click 'Expand Storage' now.\n\nWhat should you do?",
         ["Check storage in Microsoft settings", "Click 'Expand Storage' before files go",
          "Reply asking how much it will cost", "Forward the email to your IT team"],
         0, "Microsoft does not threaten file deletion in 24 hours. Check directly.",
         "24-hour deadline, file loss threat", "Check your account directly. No 24-hour threats.", "all"),

        ("Pathao Ride Confirmation Email",
         "An email says you booked a Pathao ride and will be charged Rs. 2,000. You did not book any ride. Click to cancel.\n\nWhat should you do?",
         ["Ignore it. you did not book a ride", "Click 'Cancel' to stop the charge",
          "Reply saying you did not book this", "Call the number listed in the email"],
         0, "Pathao sends confirmations in the app. Fake cancellation links steal info.",
         "Fake booking, urgency to cancel", "Pathao uses its own app, not random emails.", "all"),
    ]

    for t, c, o, ci, e, rf, tip, role in items_d1:
        _add(_make(t, c, o, ci, e, rf, tip, C, 1, role))

    # --- D1: Role-specific ---
    role_d1 = [
        ("Tax Email to Finance",
         "An email from 'IRD Nepal' asks the finance team to verify company tax records by clicking a link. The IRD usually sends official paper notices.\n\nWhat should you do?",
         ["Ignore the link and call IRD directly", "Click the link to check your tax records",
          "Forward it to your accountant to open", "Reply with your company PAN number"],
         0, "IRD sends official notices by post. They do not email clickable links.",
         "Government impersonation, link to verify", "Government uses paper. Email links are fake.", "finance"),

        ("HR Portal Update Email",
         "An email from 'HR Department' says update personal details on a new portal. The link goes to 'hr-update-portal.com' not your company domain.\n\nWhat should you do?",
         ["Report the email to IT immediately", "Click the link and update your details",
          "Reply asking if the email is genuine", "Update details with a fake bank number"],
         0, "Your company uses its own domain. A different domain is a red flag.",
         "Wrong domain, bank details request", "Check the website address. Wrong domain = fake.", "hr"),

        ("Package Delivery Link for Reception",
         "An email says a DHL package is waiting. Click a link to confirm delivery. You are the receptionist and packages come every day.\n\nWhat should you do?",
         ["Check with DHL directly by phone", "Click the link since packages are normal",
          "Forward the email to your manager", "Reply with the office street address"],
         0, "Even if you handle packages daily, verify through official channels.",
         "Familiar scenario used as bait", "Familiar does not mean safe. Always verify.", "receptionist"),

        ("Competitor Secret Strategy Email",
         "An email with a subject line 'Leaked: Competitor Strategy 2026' has an attachment. You are curious about the competitor's plans.\n\nWhat should you do?",
         ["Delete it. it is likely bait malware", "Open the attachment out of curiosity",
          "Forward it to your sales manager first", "Save it to your desktop for later"],
         0, "Attackers use curiosity-bait subjects. Leaked competitor info = classic trap.",
         "Curiosity bait, unsolicited attachment", "Curiosity is the hacker's best friend.", "sales"),

        ("Server Alert Email for IT",
         "An email from 'Microsoft Security' says your server has a critical issue. Download a patch immediately. Microsoft sends patches via Windows Update.\n\nWhat should you do?",
         ["Ignore it and check Windows Update", "Download and install the patch urgently",
          "Forward the patch to all IT staff", "Reply asking Microsoft for more details"],
         0, "Microsoft does not email patches to individual staff.",
         "Microsoft impersonation, download link", "Patches come via official update tools.", "it"),
    ]

    for t, c, o, ci, e, rf, tip, role in role_d1:
        _add(_make(t, c, o, ci, e, rf, tip, C, 1, role))

    # --- D2: Intermediate. requires noticing subtle clues ---
    items_d2 = [
        ("Vendor Bank Account Change",
         "A regular supplier emails saying they changed their bank account. Send the next payment to new details. The email address has one extra letter.\n\nWhat should you do?",
         ["Call the supplier on their known number", "Update the bank details as requested",
          "Reply to the email asking to confirm", "Forward it to finance without checking"],
         0, "Scammers imitate supplier emails to redirect payments. Call to verify.",
         "Bank detail change, slight email difference", "Verify bank changes by phone. Always.", "finance"),

        ("Client Contract Download Link",
         "A potential client emails a link to download their requirements. You have been talking to them, but this email is from a slightly different address.\n\nWhat should you do?",
         ["Call the client to confirm they sent it", "Download the document since you expect it",
          "Open the link on your phone instead", "Ask a coworker to open it for you"],
         0, "Attackers research your relationships. A slight email change is a major clue.",
         "Slight email mismatch, expected context", "Even slightly wrong emails = verify by phone.", "sales"),

        ("Invoice Payment Urgency",
         "A supplier you know sends a new invoice with payment due in 2 hours or service will stop. They usually give 30-day payment terms.\n\nWhat should you do?",
         ["Call the supplier about the deadline", "Pay immediately to keep the service",
          "Forward the invoice to your manager", "Reply asking for a payment extension"],
         0, "Sudden deadline changes from known suppliers should trigger verification.",
         "Unusual urgency, changed payment terms", "If terms changed suddenly, call to verify.", "finance"),

        ("Shared Drive Access Request",
         "An email asks you to click a link to 'renew your shared drive access before it expires'. The link looks like a Google login page but the URL is slightly different.\n\nWhat should you do?",
         ["Go to your drive directly, not via link", "Click the link to keep your access safe",
          "Enter your details on the login page", "Ask your coworker if they got it too"],
         0, "Fake login pages steal your credentials. Always go directly to the real site.",
         "Fake login page, slightly wrong URL", "Type the URL yourself. Never click email links.", "all"),

        ("Calendar Invite with Link",
         "You receive a calendar invite for a meeting you do not remember being told about. There is a link to 'join the meeting room'. No one you know sent it.\n\nWhat should you do?",
         ["Decline and ask your manager about it", "Click to join in case it is important",
          "Accept the invite but do not click yet", "Forward the invite to all your team"],
         0, "Fake calendar invites with links are a newer phishing method.",
         "Unknown meeting, unknown sender, join link", "Unknown meeting invite = do not click links.", "all"),

        ("IT Account Verification Email",
         "An email from 'IT Security' asks you to verify your account by entering your username and password on a form. The form is on an external website.\n\nWhat should you do?",
         ["Report the email to your real IT team", "Fill in the form to verify your account",
          "Enter a fake password on the form first", "Reply asking if it is really from IT"],
         0, "IT never asks for passwords via forms. This is credential harvesting.",
         "External form, password request, IT impersonation", "IT never needs your password on a form.", "all"),

        ("Salary Revision Notification",
         "An email says your salary has been revised. Click to view the new amount. HR usually announces salary changes through official letters.\n\nWhat should you do?",
         ["Ask HR directly about any revisions", "Click to see your new salary amount",
          "Reply to the email with your staff ID", "Forward it to HR asking if it is real"],
         0, "Salary notifications come through official HR channels, not random emails.",
         "Salary bait, different channel than usual", "Salary info comes from HR, not email links.", "all"),

        ("Cloud Storage Expiry Email",
         "An email warns your company cloud storage subscription expires tomorrow. Click to renew. Your IT team handles all subscriptions centrally.\n\nWhat should you do?",
         ["Let IT know about the subscription email", "Click to renew before storage is lost",
          "Reply asking which cloud service it is", "Forward the email to all department heads"],
         0, "IT manages subscriptions centrally. You should not renew services via email.",
         "Subscription urgency, centralised IT ignored", "IT handles subscriptions. Not your job.", "all"),

        ("Candidate CV Attachment",
         "You receive a job application with a CV as a .doc file. It references your exact job posting. Your antivirus did not flag it.\n\nWhat should you do?",
         ["Ask IT to scan it before you open it", "Open it since antivirus said it is safe",
          "Forward the CV to HR without opening it", "Reply asking for a PDF version instead"],
         0, "Targeted attackers reference real job posts. Antivirus misses new threats.",
         "Targeted to real posting, .doc attachment", "Antivirus is not perfect. Let IT scan first.", "hr"),

        ("Printer Error Notification",
         "An email says the shared printer has an error and you need to install a driver update from an attached file. Your IT team manages printers remotely.\n\nWhat should you do?",
         ["Report the printer issue to IT directly", "Install the driver from the attachment",
          "Forward the email to the IT department", "Try printing first to see if it works"],
         0, "IT manages printer drivers remotely. Never install software from email attachments.",
         "Printer bait, driver attachment, IT bypassed", "IT manages hardware. Report issues to them.", "all"),
    ]

    for t, c, o, ci, e, rf, tip, role in items_d2:
        _add(_make(t, c, o, ci, e, rf, tip, C, 2, role))

    # --- D3: Advanced. convincing, targeted attacks ---
    items_d3 = [
        ("CEO Wire Transfer Request",
         "Your CEO emails asking you to urgently wire Rs. 2,00,000 to a new vendor. They say 'Do not call me, I am in a meeting. Just do it now.'\n\nWhat should you do?",
         ["Call the CEO anyway to verify the wire", "Wire the money as the CEO requested",
          "Wire only half the amount to be safe", "Ask a coworker for a second opinion"],
         0, "'Do not call me' is the biggest red flag. Real CEOs welcome verification.",
         "'Do not call' instruction, large payment", "Any 'do not verify' request = scam.", "finance"),

        ("Spoofed Manager Gift Card",
         "Your manager emails at 10 PM asking you to buy 5 Daraz gift cards worth Rs. 10,000 each for a 'surprise staff event'. This has never happened before.\n\nWhat should you do?",
         ["Wait and ask your manager in person", "Buy the gift cards as the boss asked",
          "Buy them but save all the receipts", "Reply asking which gift cards to buy"],
         0, "Gift card requests by email are extremely common scams worldwide.",
         "Late night, gift cards, unusual request", "Gift cards + email = scam. Verify in person.", "all"),

        ("Colleague Account Recovery",
         "A trusted coworker messages on Viber saying they are locked out. They need you to log in for them and forward a file via a link they sent.\n\nWhat should you do?",
         ["Tell them to contact IT for help", "Help them since you trust this person",
          "Log in but do not forward any files", "Ask them to try from their own phone"],
         0, "Their Viber may be hacked. IT handles lockouts, not coworkers.",
         "Personal app, login request, urgency", "Account problems = IT department. Always.", "all"),

        ("Board Meeting Document Leak",
         "You receive an email with 'Confidential: Board Meeting Minutes' from an address that looks like your company's. The minutes discuss upcoming layoffs.\n\nWhat should you do?",
         ["Report the email to IT security team", "Open it to check if your job is at risk",
          "Forward it to coworkers for awareness", "Save the document to read it at home"],
         0, "Emotional bait (job fear) is the most effective phishing technique.",
         "Emotional manipulation, confidential label", "Fear-bait is the most dangerous phishing.", "all"),

        ("Multi-Factor Authentication Request",
         "An email from 'IT Security' says your MFA settings need updating. It provides a page to enter your current MFA code. The page looks exactly like your company portal.\n\nWhat should you do?",
         ["Go to the real portal directly instead", "Enter your MFA code on the page shown",
          "Enter an old code that has already expired", "Reply to IT asking if this is real"],
         0, "MFA phishing pages capture your code in real-time. Always go directly to the portal.",
         "Pixel-perfect fake page, MFA code request", "Type the portal URL yourself. Never via email.", "all"),

        ("Invoice from Supply Chain Partner",
         "An email from your regular supplier says they changed banks due to an 'audit requirement'. They provide a new account and ask for payment within 48 hours.\n\nWhat should you do?",
         ["Call the supplier using your saved number", "Update the payment details as asked",
          "Ask them for the bank change letter", "Pay to the old account just to be safe"],
         0, "Bank changes with audit excuses are a textbook Business Email Compromise.",
         "Audit excuse, bank change, tight deadline", "Bank changes = call supplier. Every time.", "finance"),

        ("HR Disciplinary Notice Received",
         "An email from HR says you have a disciplinary hearing next Monday. Click a link for details. You have had no issues at work.\n\nWhat should you do?",
         ["Walk to HR and ask about the hearing", "Click the link to see the complaint",
          "Reply asking what the complaint is about", "Forward it to your direct manager first"],
         0, "Fear and stress make people click. HR delivers disciplinary notices in person.",
         "Fear trigger, HR impersonation, link", "HR talks to you face-to-face about issues.", "all"),

        ("Deepfake CEO Video Email",
         "An email contains a video of your CEO asking all staff to register on a new 'employee benefits portal' via a link. The video looks and sounds authentic.\n\nWhat should you do?",
         ["Verify through official company channels", "Register since the CEO said to do it",
          "Register but use a different password", "Ask your coworker if they registered too"],
         0, "AI deepfake videos can clone anyone. Always verify via official channels.",
         "Deepfake video, new portal, bulk request", "Deepfakes exist. Verify announcements officially.", "all"),

        ("Tax Refund Email to Accountant",
         "An email from 'IRD Nepal' says your company is eligible for a tax refund. Enter company PAN and bank details on a form. The IRD usually sends paper notices.\n\nWhat should you do?",
         ["Contact IRD through their official office", "Fill in the form to get the refund",
          "Forward the form to the CEO for approval", "Enter details but use a different bank"],
         0, "IRD does not process refunds via email forms. Official notices come by post.",
         "Tax refund bait, government impersonation", "Government forms come on paper, not email.", "finance"),

        ("Contact Request via Social Media",
         "An email mentions your recent LinkedIn post by name and asks you to review a 'partnership proposal' via a link. The sender seems to know your work.\n\nWhat should you do?",
         ["Verify the sender through LinkedIn first", "Click the link since they know your work",
          "Reply with your phone number to discuss", "Download the proposal to review later"],
         0, "Spear phishing uses your public social media data to seem legitimate.",
         "Personal details from social media, targeted", "Public info makes phishing look real.", "all"),
    ]

    for t, c, o, ci, e, rf, tip, role in items_d3:
        _add(_make(t, c, o, ci, e, rf, tip, C, 3, role))

_phishing()


# ════════════════════════════════════════════════════════════════════════════
# 2. SMISHING. ~65 scenarios
# ════════════════════════════════════════════════════════════════════════════

def _smishing():
    C = "smishing"

    d1 = [
        ("eSewa Account Locked SMS",
         "An SMS says your eSewa account is locked due to suspicious activity. Click a link to verify your identity. You do use eSewa.\n\nWhat should you do?",
         ["Open the eSewa app directly yourself", "Click the link to unlock your account",
          "Reply to the SMS with your eSewa PIN", "Forward the SMS to friends who use it"],
         0, "eSewa never sends unlock links by SMS. Use the app directly.",
         "SMS lock alert, verification link", "Payment apps never send unlock links by SMS.", "all"),

        ("Free NTC Balance Offer",
         "A text says you won Rs. 5,000 NTC balance. Click to claim before midnight. You never entered any NTC promotion.\n\nWhat should you do?",
         ["Delete the message. no contest entered", "Click the link since free balance is nice",
          "Call the number to ask about the offer", "Share it so your friends can also claim"],
         0, "NTC does not give free balance through random SMS links.",
         "Unexpected prize, midnight deadline", "No entry = no prize. Delete and move on.", "all"),

        ("Pathao Verification Link SMS",
         "A WhatsApp message from an unknown number says a Pathao driver needs you to verify your location via a link. You did not book any ride.\n\nWhat should you do?",
         ["Ignore it. you did not book a ride", "Click the link to check what it is",
          "Reply saying you did not book Pathao", "Send your location to help the driver"],
         0, "Pathao drivers use the Pathao app, not WhatsApp.",
         "Unknown number, WhatsApp not official app", "Pathao communicates through its own app.", "all"),

        ("Internet Bill Overdue SMS",
         "A text from an unknown number says your WorldLink internet will be disconnected today. Click to pay the overdue bill immediately.\n\nWhat should you do?",
         ["Log into your WorldLink account directly", "Click the link to pay before cutoff",
          "Reply asking for the bill amount due", "Call the number in the SMS for details"],
         0, "WorldLink sends bills through their portal. Random SMS links are fake.",
         "Urgency, unknown number, payment link", "Check your internet portal directly.", "all"),

        ("Foodmandu Order Address SMS",
         "An SMS says your Foodmandu order is on the way but needs address confirmation via a link. You did not order any food today.\n\nWhat should you do?",
         ["Ignore it. you did not order food", "Click the link to see the order details",
          "Reply with your correct home address", "Call Foodmandu to ask about the order"],
         0, "No order placed = fake delivery message. Do not click any links.",
         "Fake delivery, address confirmation bait", "No order = no real delivery message.", "all"),

        ("Khalti Wallet Deposit SMS",
         "A text says someone deposited Rs. 10,000 in your Khalti by mistake. Click a link to return it. Your Khalti shows no new deposit.\n\nWhat should you do?",
         ["Ignore it. your wallet shows no deposit", "Click the link to return the money",
          "Reply saying you will return it soon", "Transfer money from Khalti to be fair"],
         0, "If your wallet shows no deposit, nothing was sent. The link steals credentials.",
         "Guilt manipulation, fake deposit claim", "Check your wallet. No deposit = no scam debt.", "all"),

        ("Lottery SMS From Unknown Number",
         "An SMS from an international number says you won a cash prize. Send your bank details to claim. You never entered any foreign lottery.\n\nWhat should you do?",
         ["Delete the SMS. it is a common scam", "Send bank details to claim the prize",
          "Reply asking how much you won exactly", "Forward it to your bank for checking"],
         0, "Foreign lottery SMS scams are extremely common. Never respond.",
         "International number, bank details request", "Foreign lottery = scam. Every single time.", "all"),

        ("Free WiFi Voucher SMS",
         "A text offers a free 3-month WiFi voucher from Nepal Telecom. Click a link to activate. You never signed up for any promotion.\n\nWhat should you do?",
         ["Delete it since you did not sign up", "Click the link to get free internet",
          "Reply STOP to the SMS to opt out", "Forward it to friends who need WiFi"],
         0, "Nepal Telecom does not give free vouchers via random SMS links.",
         "Free service offer, claim link, no signup", "Free offers from random SMS = always fake.", "all"),
    ]

    d2 = [
        ("Bank OTP Request Call + SMS",
         "Someone calls saying they are from your bank, then sends an SMS code. They ask you to read the code back for a 'security check'.\n\nWhat should you do?",
         ["Hang up and call your bank directly", "Read the code for security verification",
          "Read only half of the code to be safe", "Ask them to call back another day"],
         0, "Banks never ask you to read codes back. The code protects YOUR account.",
         "Phone + SMS combo, OTP forwarding", "OTP codes are like keys. Never share them.", "all"),

        ("Tax Filing SMS Alert",
         "An SMS from 'IRD Nepal' says you have unpaid taxes. Click to pay or face legal action immediately.\n\nWhat should you do?",
         ["Contact IRD through their office or site", "Click the link to check your tax status",
          "Call the number in the SMS to discuss", "Pay immediately to avoid legal trouble"],
         0, "IRD does not collect taxes through SMS links. Use official channels.",
         "Government impersonation, legal threat", "Government uses official channels, not SMS.", "finance"),

        ("Courier Custom Fee SMS",
         "A text says your courier package needs Rs. 200 customs payment via a link. You are actually expecting a package from abroad.\n\nWhat should you do?",
         ["Call the courier from their real website", "Pay Rs. 200 since you expect a package",
          "Click the link to track your shipment", "Reply asking what is in the package"],
         0, "Real couriers do not collect customs via SMS links. Call them directly.",
         "Real expectation exploited, small amount", "Expecting a delivery? Call the courier directly.", "receptionist"),

        ("HR Document WhatsApp Link",
         "A job candidate sends their CV via WhatsApp as a link to a file-sharing site. They say the file was too large to attach.\n\nWhat should you do?",
         ["Ask them to email it to your work email", "Click the link since you need the CV",
          "Open the link on your phone for safety", "Ask a coworker to check the link first"],
         0, "CVs are small files. File-sharing links from unknown people can contain malware.",
         "External link, file size excuse", "Receive documents through company email only.", "hr"),

        ("Software License Renewal SMS",
         "A text says your company software license expires today. Click to renew or lose access. Your IT team manages all licenses centrally.\n\nWhat should you do?",
         ["Forward it to your IT team to handle", "Click to renew before access is lost",
          "Reply asking which software is expiring", "Call the number in the SMS for details"],
         0, "IT handles software licenses. You should not renew things via SMS.",
         "Urgency, bypassing IT department", "IT manages licenses. Not your responsibility.", "all"),

        ("Viber Money Transfer Request",
         "A Viber message from a 'bank officer' asks you to confirm a large transfer from your account by clicking a link. No transfer was initiated by you.\n\nWhat should you do?",
         ["Ignore it and check your bank app now", "Click the link to cancel the transfer",
          "Reply asking for the transfer details", "Call the number in the Viber message"],
         0, "Banks do not use Viber for transaction confirmations.",
         "Bank impersonation via personal app", "Banks use their own apps, not Viber.", "all"),

        ("WhatsApp Group Chain Message",
         "A WhatsApp message shared in your office group says Nepal Rastra Bank is giving free Rs. 25,000 to all citizens. Click to claim.\n\nWhat should you do?",
         ["Ignore it. NRB does not give free money", "Click the link since many shared it",
          "Share it in other groups to help people", "Reply in the group saying it might be real"],
         0, "Chain messages with free money offers are always scams, even in office groups.",
         "Chain message, too good to be true, group trust", "If it sounds too good to be true, it is.", "all"),

        ("Medical Insurance SMS",
         "A text says your company medical insurance needs renewal via an SMS link. Your HR team handles all insurance matters.\n\nWhat should you do?",
         ["Check with HR about insurance renewal", "Click the link to renew your insurance",
          "Reply with your insurance policy number", "Forward the SMS to your team manager"],
         0, "HR handles insurance, not SMS links from unknown numbers.",
         "Insurance urgency, bypassing HR", "HR manages insurance. Check with them.", "hr"),
    ]

    d3 = [
        ("OTP Forwarding From Friend",
         "A friend messages on Viber saying they sent a code to your number by mistake. Seconds later your bank sends a 6-digit OTP.\n\nWhat should you do?",
         ["Never share the code. it is for you", "Send the code since your friend asked",
          "Send only the first three digits safely", "Ask what the code is actually for"],
         0, "This is an OTP forwarding attack. The code is for YOUR bank account.",
         "Friend's account may be hacked, bank OTP", "Any code on YOUR phone = YOUR account.", "all"),

        ("SIM Swap Warning SMS",
         "A text says your number is being transferred to a new SIM. Click here to stop it now. You did not request any SIM swap.\n\nWhat should you do?",
         ["Call your carrier from a different phone", "Click the link to stop the SIM swap",
          "Reply STOP to cancel the SIM transfer", "Ignore it since you still have signal"],
         0, "SIM swap scams are real but carriers do not send cancellation links.",
         "Real fear exploited, cancellation link", "Real threats need real calls, not SMS links.", "all"),

        ("WhatsApp Business Verification",
         "A message from 'WhatsApp Support' says your business account will be suspended. Enter your 2FA code on a link to verify.\n\nWhat should you do?",
         ["Ignore it. WhatsApp does not do this", "Enter 2FA code to save your account",
          "Click the link just to check the page", "Reply asking them to prove identity"],
         0, "WhatsApp does not message you asking for 2FA codes. This steals your account.",
         "Platform impersonation, 2FA code request", "WhatsApp never asks for codes. Never.", "all"),

        ("QR Code Payment Request SMS",
         "An SMS asks you to scan a QR code to receive a refund of Rs. 5,000 from a cancelled order. You did cancel an order recently.\n\nWhat should you do?",
         ["Check the refund in the original app", "Scan the QR code to get your refund now",
          "Reply asking for the order reference ID", "Forward the SMS to customer support"],
         0, "QR codes for receiving money is a scam. QR codes are used for PAYING, not receiving.",
         "QR code reversal trick, real cancelled order", "You never scan QR codes to RECEIVE money.", "all"),

        ("CEO WhatsApp Urgent Request",
         "A WhatsApp message from a number claiming to be your CEO asks you to buy Rs. 50,000 in recharge cards. They say their regular phone is broken.\n\nWhat should you do?",
         ["Call the CEO on their regular number", "Buy the cards since the CEO is asking",
          "Buy them and send photos of the codes", "Ask which recharge cards to purchase"],
         0, "CEOs do not buy recharge cards through employee WhatsApp messages.",
         "CEO impersonation, recharge card purchase", "Recharge card requests = scam. Call to verify.", "all"),

        ("Bank App Update Notification",
         "An SMS says your banking app needs an urgent security update. Download from a link. not from the official app store.\n\nWhat should you do?",
         ["Update only from your official app store", "Download from the link for the update",
          "Click the link to read about the update", "Wait a few days then update from store"],
         0, "App updates only come through official stores. External links install malware.",
         "App update outside official store", "Apps update from app stores only. Always.", "all"),

        ("Cryptocurrency Airdrop SMS",
         "A text promises free cryptocurrency worth $500 if you click a link and enter your wallet details. You do not own any cryptocurrency.\n\nWhat should you do?",
         ["Delete it. you have no crypto wallet", "Click to see what cryptocurrency is free",
          "Enter details since $500 is a lot of money", "Forward it to a friend who has crypto"],
         0, "Crypto airdrops to random numbers are always scams to steal credentials.",
         "Free money, crypto bait, wallet details", "Random crypto offers via SMS are scams.", "all"),

        ("Two-Step Vishing + Smishing Attack",
         "Someone calls saying your bank account was hacked. They say the bank will text a code and you must read it to them to 'secure your account'.\n\nWhat should you do?",
         ["Hang up and visit your bank in person", "Wait for the code and read it to them",
          "Hang up and call the bank back yourself", "Ask them to prove they are from the bank"],
         0, "This is a coordinated attack. The caller triggers a real OTP and steals it from you.",
         "Phone + SMS combo, coordinated attack", "Bank staff never ask you to read codes back.", "all"),
    ]

    for t, c, o, ci, e, rf, tip, role in d1:
        _add(_make(t, c, o, ci, e, rf, tip, C, 1, role))
    for t, c, o, ci, e, rf, tip, role in d2:
        _add(_make(t, c, o, ci, e, rf, tip, C, 2, role))
    for t, c, o, ci, e, rf, tip, role in d3:
        _add(_make(t, c, o, ci, e, rf, tip, C, 3, role))

_smishing()


# ════════════════════════════════════════════════════════════════════════════
# 3. VISHING. ~60 scenarios
# ════════════════════════════════════════════════════════════════════════════

def _vishing():
    C = "vishing"

    d1 = [
        ("IT Support Password Call",
         "Someone calls your phone saying they are from IT. Your computer has a virus and they need your password to fix it remotely right now.\n\nWhat should you do?",
         ["Hang up and ask IT in person at desk", "Give your password to fix the virus",
          "Give an old password you do not use now", "Ask them what the virus alert says"],
         0, "Real IT staff never ask for passwords. They fix things without needing yours.",
         "Password request, urgency, IT impersonation", "IT never needs your password. Ever.", "all"),

        ("Security Alert Call from Bank",
         "A caller says they are from your bank. Someone is stealing your money right now. They need your card number and PIN to 'block it'.\n\nWhat should you do?",
         ["Hang up and call your bank card number", "Give card details to stop the theft",
          "Give only the card number, not the PIN", "Stay on the line for investigation"],
         0, "Banks can block accounts without your PIN. They never call asking for it.",
         "Card and PIN request, bank impersonation", "Your bank never asks for your PIN by phone.", "all"),

        ("Police Warrant Robocall",
         "An automated voice says there is a police warrant for you for unpaid taxes. Press 1 to speak to an officer or be arrested today.\n\nWhat should you do?",
         ["Hang up. police do not use robocalls", "Press 1 to speak to the officer now",
          "Stay on the line to find out details", "Give your details to clear your name"],
         0, "Police never use automated calls for warrants. They serve notices in person.",
         "Automated voice, arrest threat, press 1", "Police do not call with robots. Hang up.", "all"),

        ("Lottery Prize Phone Call",
         "Someone calls saying you won a Rs. 1,00,000 prize. Just pay Rs. 2,000 processing fee to receive it. You never entered any lottery.\n\nWhat should you do?",
         ["Hang up. real prizes have no upfront fee", "Pay Rs. 2,000 to get Rs. 1,00,000",
          "Ask them for their office address first", "Ask them to deduct the fee from winnings"],
         0, "Legitimate prizes never require upfront payment. This is advance fee fraud.",
         "Upfront fee for prize, no entry history", "If you must pay to win, it is not a prize.", "all"),

        ("Nepal Telecom Upgrade Call",
         "A caller from 'NTC' says they are upgrading your line and need your personal details to complete the process for free.\n\nWhat should you do?",
         ["Hang up and visit the NTC service center", "Give your details for the free upgrade",
          "Give only your name, not other details", "Ask them to call back in the morning"],
         0, "NTC does not call for upgrades. They handle this in their service centers.",
         "Free upgrade bait, personal details request", "Telecom upgrades happen at service centers.", "all"),

        ("Market Researcher Birth Date",
         "A caller says they are a market researcher and asks for your full name, birth date, and home address for a survey. They sound professional.\n\nWhat should you do?",
         ["Refuse and hang up the phone call now", "Give the details since it is just a survey",
          "Give only your name but not the address", "Ask them to send the survey by email"],
         0, "Name + birth date + address = identity theft starter pack.",
         "Personal data harvesting, professional tone", "Never give personal details to unknown callers.", "all"),

        ("Delivery Location Call",
         "A caller says they are a delivery driver and urgently need your home address and a convenient time when someone will be home.\n\nWhat should you do?",
         ["Ask which company and verify by calling", "Give your address since you expect a parcel",
          "Give only the street name, not the number", "Tell them to check with the sender"],
         0, "Real delivery drivers have your address already. They do not call asking for it.",
         "Address request, urgency, personal info", "Real drivers already have your address.", "all"),
    ]

    d2 = [
        ("ISP Router Password Call",
         "Someone from 'WorldLink' calls saying they need your router admin password to upgrade your speed remotely. The upgrade is free.\n\nWhat should you do?",
         ["Refuse and call WorldLink's real number", "Give the password for faster internet",
          "Give it but change it right after the call", "Ask them to come to the office instead"],
         0, "ISPs manage speed from their end. They never need your router password.",
         "Free upgrade bait, admin credential request", "ISPs never need your router password.", "it"),

        ("Staff Directory Request Call",
         "A caller says they are from your head office. They need the full staff directory with phone numbers for an annual event invitation.\n\nWhat should you do?",
         ["Ask them to request through HR officially", "Email the directory since it is head office",
          "Give only email addresses, not phone numbers", "Read names one by one over the phone"],
         0, "Staff directories are confidential. Official requests go through HR channels.",
         "Authority claim, bulk data request", "Staff directories go through HR. Always.", "receptionist"),

        ("Vendor Warranty Call",
         "A caller says your server warranty is about to expire. They need the serial number and admin access to process the renewal before it is too late.\n\nWhat should you do?",
         ["Hang up and check warranty with vendor", "Give the serial number to renew quickly",
          "Give only the serial, not admin access", "Ask them to send a renewal email first"],
         0, "Real vendors send renewal notices in writing, not unsolicited phone calls.",
         "Warranty urgency, serial + admin request", "Warranty renewals come in writing.", "it"),

        ("Angry Customer CEO Address",
         "An extremely angry customer calls demanding the home address of your CEO. They threaten to sue if you do not provide it right now.\n\nWhat should you do?",
         ["Stay calm and offer the complaints channel", "Give the address to avoid a lawsuit",
          "Give a fake address to calm them down", "Hang up because they are too aggressive"],
         0, "Emotional pressure is a social engineering weapon. Redirect to complaints.",
         "Emotional manipulation, personal data of exec", "Anger is a weapon. Follow procedure calmly.", "receptionist"),

        ("Government Employee Data Call",
         "A caller says they are from a government office and need home addresses of all your employees for a new labour law. They threaten a fine.\n\nWhat should you do?",
         ["Ask for an official letter via post first", "Provide addresses to avoid the fine",
          "Provide names only without the addresses", "Ask them to call back when HR is free"],
         0, "Government requests come through official letters, not phone calls with threats.",
         "Government impersonation, bulk data, fine threat", "Government requests come on paper.", "hr"),

        ("Recruitment Agency Portal Login",
         "A recruitment agency calls saying they need your HR portal login to upload candidate CVs faster. They sound impatient.\n\nWhat should you do?",
         ["Refuse and offer to upload CVs yourself", "Give the login since it saves time",
          "Create a temporary login for their use", "Ask them to email the CVs instead"],
         0, "Third parties should never have access to your internal HR systems.",
         "Impatience pressure, internal system access", "Internal portals are for internal staff only.", "hr"),

        ("ISP Domain Expiry Call",
         "Your domain registrar calls saying your company website domain expires tomorrow. Pay now over the phone or lose your website.\n\nWhat should you do?",
         ["Log into your registrar account to check", "Pay over the phone to save the website",
          "Ask them to send an invoice by email first", "Give your credit card details right away"],
         0, "Domain registrars send renewal emails weeks in advance. Same-day phone calls are scams.",
         "Urgency, domain loss threat, phone payment", "Check your registrar account directly.", "it"),

        ("CEO Urgent Wire Call",
         "Your CEO calls asking you to wire Rs. 5,00,000 to a new account. The voice sounds right. They say keep it confidential.\n\nWhat should you do?",
         ["Follow standard payment approval process", "Wire the money since the voice is real",
          "Wire half the amount as a compromise", "Ask a coworker but still process the wire"],
         0, "AI deepfakes can clone voices. Always follow standard payment procedures.",
         "'Keep confidential', skip approval process", "Always follow standard approval processes.", "finance"),
    ]

    d3 = [
        ("Deepfake Voice Finance Request",
         "A call that sounds exactly like your finance coworker asks for quarterly sales numbers because they 'lost the file'. They usually request this by email.\n\nWhat should you do?",
         ["Send it through the usual email process", "Share numbers since the voice is right",
          "Share only partial data to be cautious", "Ask a personal question to verify them"],
         0, "AI voice cloning can replicate anyone. Stick to standard data sharing processes.",
         "Voice sounds real, unusual channel", "Stick to standard procedures for data.", "all"),

        ("Multi-Stage Social Engineering Call",
         "Someone calls pretending to be a new employee. They chat casually, then ask what software your company uses and who manages the admin passwords.\n\nWhat should you do?",
         ["Politely end the call and report to IT", "Answer since they seem like a new hire",
          "Share software names but not admin info", "Transfer them to the IT department head"],
         0, "Attackers build trust through casual conversation before extracting sensitive info.",
         "Casual approach, gradually sensitive questions", "Gradual questioning is a manipulation tactic.", "all"),

        ("Unscheduled Fire Inspection Visit",
         "A caller says they are from the fire department and need to schedule an immediate inspection. They ask for floor plans, entry codes, and security schedules.\n\nWhat should you do?",
         ["Ask them to send official notice by post", "Provide the info for safety compliance",
          "Give only floor plans, not security info", "Schedule the inspection for next week"],
         0, "Real fire inspectors coordinate through management. They do not cold-call for codes.",
         "Authority impersonation, security data request", "Official inspectors coordinate through management.", "all"),

        ("Vishing With Callback Number",
         "A caller claims to be from your bank and asks you to call back on a number they provide to 'verify your identity'. The number is not on your bank card.\n\nWhat should you do?",
         ["Call only the number on your bank card", "Call the number they provided for safety",
          "Call but do not share any personal data", "Text the number first to check if it is real"],
         0, "Callback numbers can be fake bank lines. Only use the number on your card or statement.",
         "Fake callback number, bank impersonation", "Only use phone numbers from your bank card.", "all"),

        ("Pressure Tactics Vendor Call",
         "A vendor calls yelling that their invoice is 3 months overdue and they will take legal action if payment is not made by end of day. You have no record of this invoice.\n\nWhat should you do?",
         ["Calmly say you will check and call back", "Pay quickly to avoid legal problems now",
          "Ask them to email the overdue invoice", "Transfer them to your manager right away"],
         0, "High-pressure calls are designed to bypass your critical thinking. Stay calm.",
         "Emotional pressure, legal threat, no records", "Pressure = manipulation. Stay calm and verify.", "finance"),

        ("Incoming Tech Support Call",
         "A caller says your company was overcharged for a software subscription. They will process a refund if you provide bank details and remote computer access.\n\nWhat should you do?",
         ["Hang up and check with the actual vendor", "Provide details to receive the refund",
          "Give bank details but not remote access", "Ask them which software subscription it is"],
         0, "Refund scams trick you into giving access. No legitimate company needs remote access for refunds.",
         "Refund bait, remote access request", "Refunds never need your remote computer access.", "all"),

        ("Call from Insurance Auditor",
         "Someone calls claiming to be an insurance auditor. They need the medical records and salary details of all your staff for a 'compliance audit'.\n\nWhat should you do?",
         ["Tell them to submit a formal request to HR", "Provide the data for audit compliance",
          "Give salary data but not medical records", "Ask them to send identification by email"],
         0, "Insurance auditors schedule visits through HR. They never cold-call for bulk records.",
         "Compliance pressure, bulk sensitive data", "Auditors follow formal processes through HR.", "hr"),
    ]

    for t, c, o, ci, e, rf, tip, role in d1:
        _add(_make(t, c, o, ci, e, rf, tip, C, 1, role))
    for t, c, o, ci, e, rf, tip, role in d2:
        _add(_make(t, c, o, ci, e, rf, tip, C, 2, role))
    for t, c, o, ci, e, rf, tip, role in d3:
        _add(_make(t, c, o, ci, e, rf, tip, C, 3, role))

_vishing()


# ════════════════════════════════════════════════════════════════════════════
# 4. PHYSICAL SECURITY. ~60 scenarios
# ════════════════════════════════════════════════════════════════════════════

def _physical():
    C = "physical_security"

    d1 = [
        ("Stranger Tailgating at Door",
         "You swipe your ID to enter the office. A person you have never seen walks behind you and says 'Thanks, I forgot my badge today.'\n\nWhat should you do?",
         ["Ask them to wait and check at reception", "Let them in since they look professional",
          "Let them in but watch where they walk", "Hold the door because it is very polite"],
         0, "Tailgating is one of the easiest ways to enter an office. Always check.",
         "Unknown person, forgot badge excuse", "Send unknown people to reception. Always.", "all"),

        ("Unlocked Laptop in Canteen",
         "You go to the canteen and see a coworker's laptop open and logged in. Nobody is sitting nearby at all.\n\nWhat should you do?",
         ["Lock the screen and tell the coworker", "Leave it alone. not your responsibility",
          "Take the laptop to your own desk now", "Check what they were working on today"],
         0, "Unlocked laptops are open doors to company data. Lock them immediately.",
         "Unattended device, unlocked screen", "Win+L locks your screen in one second.", "all"),

        ("Password on Sticky Note",
         "You notice a coworker has their login password written on a sticky note attached to their computer monitor.\n\nWhat should you do?",
         ["Privately tell them it is a security risk", "Peel it off and throw it in the trash",
          "Take a photo of the note for your records", "Ignore it since everyone does that"],
         0, "Sticky note passwords can be read by visitors, cleaners, and cameras.",
         "Password visible in public space", "Passwords belong in your head or a manager app.", "all"),

        ("Propped Open Back Door",
         "You find the back door of your office propped open with a rock. A sign says 'Emergency Exit. Keep Closed at All Times'.\n\nWhat should you do?",
         ["Remove the rock and close the door now", "Leave it open since someone put it there",
          "Prop it open more since it is very hot", "Put a different rock to hold it better"],
         0, "Open doors bypass all access controls. Close them and report.",
         "Emergency exit propped open, bypass access", "Close it and report it immediately.", "all"),

        ("Phone Left Unlocked on Sofa",
         "A coworker left their unlocked phone on the office sofa. You can see their emails and WhatsApp messages on the screen.\n\nWhat should you do?",
         ["Lock the phone and tell the coworker now", "Leave it alone since it is not yours",
          "Read the messages out of simple curiosity", "Put it in your desk drawer for safety"],
         0, "Unlocked phones expose emails, messages, and company apps. Lock and return.",
         "Unlocked phone, visible messages", "Lock it, return it, tell the owner.", "all"),

        ("Open Notebook With Passwords",
         "In the meeting room you find a notebook left open with a list of system passwords written inside. Nobody is in the room.\n\nWhat should you do?",
         ["Close the book and give it to IT or owner", "Read the passwords for your own reference",
          "Leave it open since someone will come back", "Take a photo for safekeeping purposes"],
         0, "Written passwords in shared spaces are a major security breach.",
         "Passwords in shared room, no owner present", "Close it, return it, tell IT.", "all"),

        ("Guest Without Escort",
         "A visitor is walking through the office without an escort or visitor badge. They seem to know where they are going.\n\nWhat should you do?",
         ["Politely ask if they need help finding someone", "Let them go since they seem confident",
          "Follow them quietly around the office", "Assume a coworker is meeting them soon"],
         0, "Confidence does not equal authorization. All visitors need badges and escorts.",
         "No badge, no escort, confident movement", "All visitors need a badge and an escort.", "all"),
    ]

    d2 = [
        ("Salary Sheets on Printer",
         "You find printed salary sheets with employee names and amounts left on the shared printer. Nobody is around to collect them.\n\nWhat should you do?",
         ["Take the papers directly to HR right now", "Leave them for the owner to collect later",
          "Read them to check if your pay is right", "Throw them in the regular dustbin nearby"],
         0, "Salary data is confidential. Return it to HR for proper handling.",
         "Confidential data in public area", "Found confidential documents go to HR.", "all"),

        ("Delivery Person Near Server Room",
         "A delivery person is standing right outside the server room. The door is slightly open and nobody from IT is around.\n\nWhat should you do?",
         ["Close the server room and escort to front", "Sign for the package so they can leave",
          "Tell them to wait right there for someone", "Ignore them since it is not your problem"],
         0, "Server rooms are critical infrastructure. Secure the door first.",
         "Unauthorized person near server room", "Secure sensitive areas before anything else.", "receptionist"),

        ("Open Finance Cabinet After Hours",
         "After hours you see the finance filing cabinet wide open with keys in the lock. Chequebooks and records are visible.\n\nWhat should you do?",
         ["Lock the cabinet and tell finance team", "Leave it since it is not your department",
          "Take the keys to your desk for safe keeping", "Close cabinet but leave keys in the lock"],
         0, "Unsecured financial documents are a major risk. Lock and notify.",
         "Unsecured financials, keys left in lock", "See something unsecured? Secure it. Tell owner.", "finance"),

        ("Visitor Lost Badge Request",
         "A visitor at reception says they lost their guest badge and need a replacement. They claim they were meeting someone on the third floor.\n\nWhat should you do?",
         ["Verify with the person on the third floor", "Give a new badge since they seem genuine",
          "Let them go up without a badge this time", "Ask them to describe the person they met"],
         0, "Always verify lost badge claims. Never issue replacements without confirmation.",
         "Lost badge claim, plausible story", "Verify every badge claim, no exceptions.", "receptionist"),

        ("Cleaning Staff in Finance Area",
         "You see cleaning staff opening drawers in the finance area while cleaning. They are looking inside the drawers, not just dusting.\n\nWhat should you do?",
         ["Politely ask them to only clean surfaces", "Let them clean since that is their job",
          "Report it to your manager immediately", "Lock the drawers and give them the key"],
         0, "Cleaning staff should only clean surfaces. Opening drawers is not standard cleaning.",
         "Unusual behaviour during cleaning", "If cleaning looks unusual, say something.", "finance"),

        ("Visitor Taking Photos in Office",
         "You notice someone in the hallway taking photos of the office layout, desks, and computer screens with their phone.\n\nWhat should you do?",
         ["Ask who they are and report to security", "Ignore them since they might be new staff",
          "Take photos of them taking photos back", "Block their view with your body politely"],
         0, "Photography of office layouts and screens is a reconnaissance technique.",
         "Unknown person, photographing office layout", "Photos of office layout = potential recon.", "all"),

        ("Server Room Door Held For Cleaning",
         "The cleaning staff asks you to prop the server room door open so they can vacuum inside. They clean every night.\n\nWhat should you do?",
         ["Tell them the server room is off-limits", "Prop it open since they clean here daily",
          "Let them in but stay to watch them clean", "Prop it open but close it when you leave"],
         0, "Server rooms are restricted. Vacuuming can damage equipment with static.",
         "Regular staff, unusual request, server access", "Server rooms are restricted. No exceptions.", "all"),

        ("Bag of Hard Drives by Trash",
         "You see a bag of old hard drives sitting next to the trash bin near the exit. They are labelled with department names.\n\nWhat should you do?",
         ["Take them to IT for secure destruction", "Throw them in the dumpster outside now",
          "Leave them since someone will handle them", "Take one home to use for personal files"],
         0, "Hard drives contain recoverable data even when formatted. IT must destroy them.",
         "Data-bearing devices near trash, labelled", "Hard drives go to IT, never to the trash.", "it"),
    ]

    d3 = [
        ("Confident Visitor Name-Dropping",
         "A well-dressed person walks in confidently saying they are meeting the CEO and she knows they are coming. They have no visitor badge.\n\nWhat should you do?",
         ["Escort them to reception for a badge first", "Let them through since the CEO knows them",
          "Email the CEO's assistant to verify them", "Follow them around the office quietly"],
         0, "Name-dropping and confidence are social engineering tactics. Always badge first.",
         "Name-dropping, confidence, no badge", "Everyone gets a badge. No exceptions. Ever.", "all"),

        ("USB Device Plugged Into Server",
         "In the server room you notice a small unfamiliar USB device plugged into the back of a server. Your team does not use wireless peripherals.\n\nWhat should you do?",
         ["Photograph it and notify IT security now", "Unplug it since it does not belong there",
          "Leave it. maybe IT installed it recently", "Plug it into your laptop to check it"],
         0, "This could be a hardware keylogger or attack device. Do not touch. let IT investigate.",
         "Unknown device on server, potential attack", "Unknown hardware on servers = alert IT.", "it"),

        ("Maintenance Worker No Notice",
         "A person in a maintenance uniform is in the server room fixing AC. Nobody told you or your team about any maintenance visit today.\n\nWhat should you do?",
         ["Ask them to stop and verify with manager", "Let them work since they are in uniform",
          "Watch them until they are done working", "Check their ID and let them continue"],
         0, "Uniforms are easy to fake. No notification = no authorization.",
         "Unannounced maintenance, uniform as trust signal", "No notification = no access.", "all"),

        ("Tailgating With Heavy Boxes",
         "A delivery person carrying heavy boxes asks you to hold the secure door open. They say they cannot reach their badge.\n\nWhat should you do?",
         ["Offer to badge them in after confirming", "Hold the door since they are struggling",
          "Take one box and let them badge through", "Tell them to put boxes down and badge in"],
         0, "Carrying heavy items is a classic tailgating technique to exploit helpfulness.",
         "Heavy boxes tactic, helpfulness exploit", "Helpfulness is good but security comes first.", "all"),

        ("Unscheduled Fire Drill",
         "Someone you do not recognize pulls the fire alarm during lunch. While everyone evacuates, you see them going towards the server room.\n\nWhat should you do?",
         ["Alert security about the person right away", "Evacuate since fire safety comes first",
          "Follow the person to see what they are doing", "Go back in and lock the server room door"],
         0, "Fake fire alarms are used to create chaos while the attacker accesses restricted areas.",
         "Distraction technique, targeting server room", "Fire alarm during unusual time = stay alert.", "all"),

        ("Social Engineer Posing as Auditor",
         "A person with a clipboard walks around the office asking employees about their daily routines, when security guards leave, and which doors stay unlocked.\n\nWhat should you do?",
         ["Report them to your manager or security", "Answer their questions since they are polite",
          "Answer some questions but not security ones", "Tell them to come back when the boss is in"],
         0, "Asking about security routines is reconnaissance. Report to management immediately.",
         "Systematic questioning, security schedule interest", "Questions about security = report immediately.", "all"),

        ("Piggyback Through Turnstile",
         "At the turnstile entrance, a person in formal clothes waits for you to badge in and tries to squeeze through with you before it closes.\n\nWhat should you do?",
         ["Block them and point to the badge reader", "Let them through since they look official",
          "Ask to see their badge before letting in", "Report them but still let them enter"],
         0, "Turnstiles exist for a reason. One badge = one person.",
         "Formal appearance as trust signal, turnstile bypass", "One badge = one person. Every time.", "all"),
    ]

    for t, c, o, ci, e, rf, tip, role in d1:
        _add(_make(t, c, o, ci, e, rf, tip, C, 1, role))
    for t, c, o, ci, e, rf, tip, role in d2:
        _add(_make(t, c, o, ci, e, rf, tip, C, 2, role))
    for t, c, o, ci, e, rf, tip, role in d3:
        _add(_make(t, c, o, ci, e, rf, tip, C, 3, role))

_physical()


# ════════════════════════════════════════════════════════════════════════════
# 5. PASSWORD HYGIENE. ~60 scenarios
# ════════════════════════════════════════════════════════════════════════════

def _password():
    C = "password_hygiene"

    d1 = [
        ("Friend Wants Your Password",
         "A coworker and good friend asks to borrow your email password. Their account is not working and they need to send an urgent email.\n\nWhat should you do?",
         ["Refuse but offer to send it for them", "Share it since they are a trusted friend",
          "Share it and ask them to change it later", "Write the password on paper for them"],
         0, "Never share passwords. Help them another way or tell them to contact IT.",
         "Trusted friend, urgent excuse", "Help the person, not the password.", "all"),

        ("Same Password for Everything",
         "You use the same password for Facebook, your office email, and online banking. A friend says Facebook had a data leak last month.\n\nWhat should you do?",
         ["Change all three passwords right now", "Change only your Facebook password now",
          "Keep them since nobody would target you", "Add a number to make each one different"],
         0, "Same password everywhere = one breach affects all your accounts.",
         "Same password reused, data leak on one", "One password per account. Use a manager.", "all"),

        ("Browser Save on Shared PC",
         "You log into email on the shared meeting room computer. The browser asks 'Save password?' for faster login next time.\n\nWhat should you do?",
         ["Click 'Never' and always log out after", "Click 'Save' since it is more convenient",
          "Save it but delete it from browser later", "Save it since the PC has antivirus now"],
         0, "Saved passwords on shared computers let anyone access your accounts.",
         "Shared computer, browser save prompt", "Shared PC = never save. Log out every time.", "all"),

        ("Simple Password Choice",
         "You are creating a password for your work email. You think of using 'nepal123' because it is very easy to remember.\n\nWhat should you do?",
         ["Create a long passphrase with numbers", "Use 'nepal123' since you will remember it",
          "Use 'Nepal@123' to add a capital letter", "Use your birthday since no one guesses it"],
         0, "Short passwords with common words are cracked in seconds. Use a passphrase.",
         "Common word + simple numbers, too short", "Length beats complexity. Use a passphrase.", "all"),

        ("PIN on Back of ID Card",
         "You write your computer login PIN on the back of your staff ID card so you never forget it. You carry the card everywhere.\n\nWhat should you do?",
         ["Remove the PIN and memorize it instead", "Keep it since the card is always with you",
          "Cover the PIN with a piece of tape now", "Write it on a different card for backup"],
         0, "If you lose your ID card, whoever finds it has your PIN and building access.",
         "PIN on portable item, loss risk", "Memorize PINs. Written ones can be found.", "all"),

        ("Sharing WiFi Password Publicly",
         "You write the office WiFi password on a whiteboard in the reception area so visitors can connect easily.\n\nWhat should you do?",
         ["Set up a separate guest WiFi network", "Keep it visible since visitors need WiFi",
          "Write it smaller so it is harder to see", "Change the password every single month"],
         0, "The office WiFi password should never be public. Use a separate guest network.",
         "Staff WiFi visible publicly, no guest network", "Guest WiFi = separate from staff WiFi.", "all"),

        ("Telling Password to IT on Phone",
         "Someone calls saying they are from your IT department. They need your password to fix your email settings. Your real IT sits upstairs.\n\nWhat should you do?",
         ["Refuse and go ask IT upstairs in person", "Give the password since IT sometimes calls",
          "Give an old password you changed before", "Ask them to email you before sharing it"],
         0, "IT never needs your password for any reason. They have admin access.",
         "IT impersonation, phone password request", "IT has admin access. They never need yours.", "all"),

        ("Using Dog Name as Password",
         "Your office password is your dog's name 'Buddy' because it is easy to remember. Your Facebook profile shows photos with your dog named Buddy.\n\nWhat should you do?",
         ["Change it to something not on social media", "Keep it since nobody checks your Facebook",
          "Add '123' after the name to make it strong", "Change the dog's name on Facebook instead"],
         0, "Attackers check social media for pet names, birthdays, etc. Use unrelated passwords.",
         "Password from public social media info", "Never use info from your social media.", "all"),
    ]

    d2 = [
        ("Ignoring Password Update Prompt",
         "Your system asks you to change your password because it is 90 days old. You ignore the prompt because your current password is really easy to remember.\n\nWhat should you do?",
         ["Change it now using a new strong password", "Keep ignoring it since your password works",
          "Change it to the same password with a '2'", "Ask IT to remove the password expiry rule"],
         0, "Regular password changes limit damage from undetected breaches.",
         "Ignoring security prompt, convenience priority", "When the system says change, change it.", "all"),

        ("Password Manager Suggestion",
         "A coworker suggests using a password manager. You are worried it puts all your passwords in one place.\n\nWhat should you do?",
         ["Start using one. it is safer than reuse", "Avoid it since it is a single failure point",
          "Keep using the same strong password everywhere", "Write passwords in a locked notebook at home"],
         0, "Password managers encrypt all passwords with one master key. This is far safer than reusing passwords or writing them down.",
         "Concern about single point of failure", "Password managers are safer than reuse.", "all"),

        ("Sharing HR Portal Password",
         "Your manager asks you to share the HR portal password with a new intern so they can access employee records for a project.\n\nWhat should you do?",
         ["Ask IT to create a new account for them", "Share it since the manager is asking you",
          "Share it but change it next week sometime", "Write it on paper and hand it to the intern"],
         0, "Each person needs their own account for audit trail. Never share credentials.",
         "Manager request, new intern, shared login", "Everyone gets their own account. No sharing.", "hr"),

        ("Default Router Password",
         "Your office router still uses the default password 'admin/admin' because it is easy and nobody has changed it since installation.\n\nWhat should you do?",
         ["Change it to a strong unique password now", "Keep it since only IT accesses the router",
          "Add '123' to the default to make it better", "Write down the default in case you forget"],
         0, "Default passwords are the first thing attackers try. Change them immediately.",
         "Default credentials, publicly known password", "Default passwords = no password at all.", "it"),

        ("Two-Factor On Personal Phone",
         "Your company enables 2FA for email. You are annoyed because it adds 10 seconds to every login and you log in many times daily.\n\nWhat should you do?",
         ["Keep 2FA. 10 seconds prevents hacking", "Ask IT to disable it for your account",
          "Use 2FA only on Monday mornings for safety", "Find a way to bypass it to save time"],
         0, "2FA is one of the most effective protections. 10 seconds is a small price.",
         "Convenience vs security, 2FA resistance", "2FA is not optional. 10 seconds saves accounts.", "all"),

        ("Reusing Work Password for Personal",
         "You use your work email password for your personal Netflix account too. It is a strong password and you do not want to remember another one.\n\nWhat should you do?",
         ["Create a different password for Netflix", "Keep it since the password is very strong",
          "Change only the last character for Netflix", "Use a password manager for both passwords"],
         0, "If Netflix is breached, attackers get your work password. Keep them separate.",
         "Work/personal password overlap", "Work and personal = always different passwords.", "all"),

        ("Auto-Fill on Work Computer",
         "Your browser has auto-filled your banking login on your work computer. You notice it saves both username and password.\n\nWhat should you do?",
         ["Delete saved credentials from the browser", "Keep it since it is your own work computer",
          "Add a master password to the browser now", "Turn off auto-fill only for banking sites"],
         0, "Work computers may be accessed by IT or shared during maintenance. Do not save banking credentials.",
         "Banking credentials on work device", "Never save bank logins on work computers.", "all"),

        ("Shared Master Bank Password",
         "The junior accountant asks for the master bank portal password to process invoices while you are on leave next week.\n\nWhat should you do?",
         ["Ask the bank to create a sub-account login", "Share the master password for the week",
          "Share it but change it when you come back", "Write it in a sealed envelope for them"],
         0, "Master bank passwords should never be shared. Request sub-accounts with limited access.",
         "Master credential sharing, absence excuse", "Never share master passwords. Request sub-accounts.", "finance"),
    ]

    d3 = [
        ("Admin Passwords in Google Doc",
         "Your IT team stores all admin passwords in a shared Google Doc that everyone on the team can read, edit, and copy.\n\nWhat should you do?",
         ["Move all passwords to a password manager", "Keep the Doc since it is convenient to use",
          "Password-protect the Google Doc for safety", "Print passwords and delete the Doc now"],
         0, "Shared docs have no audit trail or encryption. Use a real password manager.",
         "Shared password storage, no audit trail", "Use a real password manager for teams.", "it"),

        ("Skipping 2FA on Admin Panel",
         "A team member says 2FA on the admin panel is annoying and suggests turning it off. The firewall is strong, they say.\n\nWhat should you do?",
         ["Keep 2FA. firewalls do not stop all attacks", "Turn it off since the firewall is enough",
          "Enable 2FA on weekdays only for compromise", "Use 2FA only on the main admin account"],
         0, "Firewalls protect the perimeter. Stolen passwords bypass them. 2FA is essential.",
         "False sense of firewall security", "2FA for admin accounts is mandatory. Period.", "it"),

        ("Emergency Password Sharing",
         "A critical deadline looms. The only person with system access is sick. Your manager asks you to call them and get their password.\n\nWhat should you do?",
         ["Ask IT to create temporary access instead", "Call them and get their password urgently",
          "Ask IT to share the password from records", "Use a coworker's account with similar access"],
         0, "Emergencies do not justify password sharing. IT can grant temporary access.",
         "Emergency pressure, manager request", "IT handles emergencies. No password sharing.", "all"),

        ("Post-Breach Password Strategy",
         "Your company discovers a data breach. You are told to change your password. You plan to change it to your previous password since you remember it.\n\nWhat should you do?",
         ["Create a completely new password you never used", "Reuse the previous password since it was good",
          "Use the current password with a '!' at the end", "Wait to see if your account was affected"],
         0, "Old passwords may also be compromised. Post-breach = completely new password.",
         "Password reuse after breach, old password in logs", "After a breach: completely new password.", "all"),

        ("Password Written in Shared Notebook",
         "Your team keeps a physical notebook with all shared service passwords. It sits on a desk where anyone can open it.\n\nWhat should you do?",
         ["Move passwords to a secure password manager", "Lock the notebook in a desk drawer instead",
          "Add a fake entry to confuse any intruder", "Replace the notebook with a spreadsheet"],
         0, "Physical notebooks with passwords are easily stolen or photographed.",
         "Physical password storage, accessible location", "Digital password managers replace notebooks.", "all"),

        ("Biometric vs Password Discussion",
         "Your manager suggests replacing all passwords with fingerprint-only login. No backup password needed, they say.\n\nWhat should you do?",
         ["Use biometrics as a second factor with password", "Switch to fingerprint-only for convenience",
          "Use fingerprint but keep passwords as a backup", "Reject biometrics due to privacy concerns only"],
         0, "Biometrics alone are risky. fingerprints cannot be changed if compromised. Use as 2FA.",
         "Biometric-only proposal, no backup method", "Biometrics = second factor, not replacement.", "all"),

        ("SSO Token Left Active",
         "You finish work and close your browser but do not log out of the company single sign-on (SSO) portal. Your session stays active.\n\nWhat should you do?",
         ["Always log out of SSO when leaving work", "Close the browser since that is enough",
          "Leave it since you will be back tomorrow", "Lock your computer and leave SSO active"],
         0, "SSO sessions may persist even after browser close. Always log out explicitly.",
         "Active SSO session, not explicitly logged out", "Log out of SSO, not just the browser.", "all"),
    ]

    for t, c, o, ci, e, rf, tip, role in d1:
        _add(_make(t, c, o, ci, e, rf, tip, C, 1, role))
    for t, c, o, ci, e, rf, tip, role in d2:
        _add(_make(t, c, o, ci, e, rf, tip, C, 2, role))
    for t, c, o, ci, e, rf, tip, role in d3:
        _add(_make(t, c, o, ci, e, rf, tip, C, 3, role))

_password()


# ════════════════════════════════════════════════════════════════════════════
# 6. USB BAITING. ~55 scenarios
# ════════════════════════════════════════════════════════════════════════════

def _usb():
    C = "usb_baiting"

    d1 = [
        ("Free USB at Trade Fair",
         "At a trade fair, a company gives you a free branded USB stick. Back at the office you think about plugging it into your work computer.\n\nWhat should you do?",
         ["Give it to IT for scanning before using", "Plug it in since it is from a real company",
          "Plug it into your personal laptop first", "Use it only for your own personal files"],
         0, "Free USB drives can contain hidden malware. Let IT check them first.",
         "Free USB from unknown source", "Unknown USB = IT scans it first.", "all"),

        ("Found USB in Parking Lot",
         "You find a USB drive on the ground in the parking lot. The label says 'Employee Bonus List 2026'.\n\nWhat should you do?",
         ["Give it to IT. do not plug it in", "Plug it in to find who it belongs to",
          "Plug it in on a spare offline computer", "Throw it in the bin to be safe now"],
         0, "Tempting labels are designed to exploit curiosity. This is classic USB baiting.",
         "Found on ground, tempting label on drive", "Curiosity is the hacker's best weapon.", "all"),

        ("USB Pen Left on Reception Desk",
         "A shiny new USB pen drive appears on the reception desk. Nobody knows who left it or where it came from.\n\nWhat should you do?",
         ["Put it in a drawer and report it to IT", "Plug it in to check whose files are on it",
          "Keep it as your own since nobody claimed it", "Throw it away since it is suspicious now"],
         0, "Unknown USB devices on desks could be planted. Report to IT.",
         "Unknown origin, appeared on desk", "Unknown USB on desk = report, not plug.", "all"),

        ("USB Memory Card in Elevator",
         "You find a small memory card dropped on the elevator floor. It could be someone's photos or something else.\n\nWhat should you do?",
         ["Give it to reception as a lost item", "Put it in your phone to check the contents",
          "Put it in your laptop to find the owner", "Keep it since nobody will come looking"],
         0, "Memory cards can carry malware just like USB drives. Do not insert them.",
         "Found memory card, curiosity about contents", "Memory cards are tiny USBs. Same rules.", "all"),

        ("Coworker Brings USB From Home",
         "A coworker brings a USB from home with family photos and plugs it into their work computer to show you during lunch break.\n\nWhat should you do?",
         ["Tell them personal USBs should not be used", "Look at the photos since it is just fun",
          "It is fine since they are a trusted coworker", "Ask them to email the photos to you instead"],
         0, "Personal USBs can unknowingly carry malware from home computers.",
         "Personal device on work computer", "Personal USBs do not belong in work computers.", "all"),

        ("USB Promotional Bracelet",
         "At a conference, you receive a USB bracelet as a promotional gift. It looks cool and you want to use it for work files.\n\nWhat should you do?",
         ["Give it to IT for scanning before using", "Use it since it is from a real conference",
          "Format it first and then use it safely", "Use it only for non-sensitive documents"],
         0, "Promotional USB devices can be pre-loaded with tracking or malware.",
         "Promotional item, looks harmless", "All unknown USBs = IT scans first.", "all"),
    ]

    d2 = [
        ("Unknown Charging Cable at Cafe",
         "Your phone battery is low at a cafe. A charging cable is already plugged into the wall outlet. Someone must have left it behind.\n\nWhat should you do?",
         ["Use your own charger or a power outlet", "Use it because it is just a charging cable",
          "Use it but turn your phone off while it charges", "Use it but disconnect if you see alerts"],
         0, "Modified charging cables can steal data. Always use your own cable.",
         "Unknown cable, data theft possible", "Always carry your own charger.", "all"),

        ("Client Hands You a USB Drive",
         "A client hands you a USB saying 'Here are our requirements. review by tomorrow.' You were not expecting them to bring a USB drive.\n\nWhat should you do?",
         ["Ask them to email the documents instead", "Plug it in since the client is trusted",
          "Plug it in but only open PDF files safely", "Copy files to your PC and return the USB"],
         0, "Even trusted clients can carry infected USBs unknowingly.",
         "USB from known person, unknown device state", "Ask for documents by email. Safer and traceable.", "sales"),

        ("USB Labelled Confidential Photos",
         "You find a USB in the elevator labelled 'Confidential Photos. DO NOT OPEN'. You are very curious about the contents.\n\nWhat should you do?",
         ["Give it to IT and resist the temptation", "Plug it in quickly to see what is inside",
          "Plug it into an offline PC to be safer", "Open it at home on your personal laptop"],
         0, "Tempting labels like 'Confidential' are designed to exploit curiosity.",
         "Curiosity bait label, social engineering", "More tempting label = more dangerous USB.", "all"),

        ("Guest Wants to Charge via Computer",
         "A guest at reception asks to plug their phone into your computer's USB port to charge because they forgot their charger.\n\nWhat should you do?",
         ["Offer a wall charger or power bank instead", "Let them plug in since they are just charging",
          "Let them but watch the screen for anything", "Say there are no USB ports available now"],
         0, "USB data connections work both ways. The guest's phone could infect your computer.",
         "USB data connection, guest device risk", "Computer USB = data connection. Use wall outlets.", "receptionist"),

        ("USB From Vendor With Receipts",
         "A vendor gives you a USB claiming it has receipts and invoices for the quarter. They say it is faster than email.\n\nWhat should you do?",
         ["Ask them to email the files to finance", "Plug it in since vendor receipts are needed",
          "Plug it in on a computer without internet", "Accept the USB but scan it with antivirus"],
         0, "Even known vendors can unknowingly carry infected USBs. Use email instead.",
         "Business context, vendor relationship", "Business files should come by email.", "finance"),

        ("External Hard Drive in Lobby",
         "You find a portable hard drive in the office lobby labelled with your company's finance department name.\n\nWhat should you do?",
         ["Give it to IT security for investigation", "Plug it in to return it to the department",
          "Give it directly to the finance department", "Leave it at reception for someone to claim"],
         0, "Attackers label devices with department names to target specific teams.",
         "Targeted labelling, department name as bait", "Labelled devices might be targeted attacks.", "all"),

        ("Rubber Ducky USB Attack Device",
         "An IT colleague tells you about 'USB Rubber Ducky' devices that look like normal USBs but inject malicious commands in seconds.\n\nWhat should you do?",
         ["Never plug in any USB you did not buy", "Only worry about USBs that look suspicious",
          "Plug unknown USBs into Linux computers only", "Scan USBs with antivirus before opening them"],
         0, "Rubber Ducky attacks execute faster than antivirus can detect. Never plug in unknown USBs.",
         "Looks normal, acts malicious, very fast", "If you did not buy it, do not plug it in.", "it"),
    ]

    d3 = [
        ("USB With Autorun Malware",
         "IT found malware on a computer from a USB someone used last week. They are asking who used an unknown USB. Your coworker did but you are afraid they will get in trouble.\n\nWhat should you do?",
         ["Tell IT honestly. company safety matters", "Stay quiet to protect your good coworker",
          "Tell your coworker to go to IT themselves", "Tell IT but do not name the specific person"],
         0, "Network-wide malware needs fast containment. Honest reporting saves the company.",
         "Known infection, reporting obligation", "Report security incidents honestly. Speed matters.", "all"),

        ("Promotional Power Bank With Cable",
         "At a conference you receive a free power bank with a built-in USB cable. You want to charge your work phone during the event.\n\nWhat should you do?",
         ["Use it with your own cable or data blocker", "Use it directly from the conference booth",
          "Use it but keep your phone locked while on", "Open the power bank and check for chips"],
         0, "Built-in cables can access data. Use your own cable or a data-blocking adapter.",
         "Free device, built-in cable, data access risk", "Use your own cable and a data blocker.", "all"),

        ("USB Left by Fired Employee",
         "A recently fired employee left a USB drive in their desk. You find it while cleaning out their workspace.\n\nWhat should you do?",
         ["Give it to IT for secure investigation", "Plug it in to check for company files",
          "Throw it away since they no longer work here", "Give it to HR to forward to them later"],
         0, "A terminated employee's USB could contain anything. IT must investigate securely.",
         "Unknown contents, former employee, potential grudge", "Former employee USBs go to IT only.", "all"),

        ("USB Dropped During Meeting by Visitor",
         "A visitor drops a USB drive during a meeting and does not notice. You pick it up. They have already left the building.\n\nWhat should you do?",
         ["Give it to IT. do not check the contents", "Plug it in to find their contact details",
          "Mail it to their company's address directly", "Keep it at reception for them to collect"],
         0, "This could be accidental or a deliberate social engineering drop. Let IT check.",
         "Dropped by visitor, might be intentional", "Even accidental drops should go through IT.", "all"),

        ("DIY USB Sanitization",
         "You want to use a found USB for personal storage. You plan to format it yourself to make it safe before using it.\n\nWhat should you do?",
         ["Do not use found USBs. formatting is not enough", "Format it and use it since it will be clean",
          "Run antivirus and then format it to be sure", "Format it twice for extra safety measures"],
         0, "Some USB malware survives formatting by hiding in firmware. Never use found USBs.",
         "Formatting does not clean firmware malware", "Found USBs cannot be made safe by formatting.", "all"),

        ("Charging Station at Airport",
         "At the airport, you see a free charging station with USB ports and built-in cables. Your phone is at 5% and you have an important call soon.\n\nWhat should you do?",
         ["Use a wall outlet with your own charger", "Use the station since you urgently need charge",
          "Use it but enable flight mode on your phone", "Use it for just 5 minutes to get some charge"],
         0, "Public USB charging stations can be modified to steal data (juice jacking).",
         "Public charging station, USB ports, data risk", "Public USB ports = data risk. Use wall outlets.", "all"),
    ]

    for t, c, o, ci, e, rf, tip, role in d1:
        _add(_make(t, c, o, ci, e, rf, tip, C, 1, role))
    for t, c, o, ci, e, rf, tip, role in d2:
        _add(_make(t, c, o, ci, e, rf, tip, C, 2, role))
    for t, c, o, ci, e, rf, tip, role in d3:
        _add(_make(t, c, o, ci, e, rf, tip, C, 3, role))

_usb()


# ════════════════════════════════════════════════════════════════════════════
# 7. SOCIAL ENGINEERING. ~60 scenarios
# ════════════════════════════════════════════════════════════════════════════

def _social():
    C = "social_engineering"

    d1 = [
        ("Boss Gift Card WhatsApp",
         "A WhatsApp message claims to be your boss. They need you to buy 5 Daraz gift cards for Rs. 10,000 each for a surprise reward. 'Keep it secret.'\n\nWhat should you do?",
         ["Call your boss on their regular number", "Buy the gift cards since the boss asked",
          "Buy them but keep all of the receipts", "Ask which denominations they prefer today"],
         0, "Gift card scams are extremely common. 'Keep it secret' prevents verification.",
         "'Keep secret', gift cards, messaging app", "Gift card requests = scam. Call to verify.", "all"),

        ("LinkedIn Staff Directory Request",
         "A friendly LinkedIn user says they are writing an article about your company. They want a copy of the staff directory to verify names.\n\nWhat should you do?",
         ["Decline and point to the public website", "Send a partial list with names only shown",
          "Send the full directory since it is LinkedIn", "Ask your manager if sharing is allowed"],
         0, "Staff directories enable targeted phishing. Only share public information.",
         "LinkedIn trust, internal data request", "Company directories are internal documents.", "all"),

        ("AC Repairman Wants WiFi",
         "The AC repair person asks for the staff WiFi password to check the 'smart controls' from their phone while fixing the unit.\n\nWhat should you do?",
         ["Offer the guest WiFi network to them", "Give staff WiFi since they need it to work",
          "Give it but ask them to forget it when done", "Let them use your phone hotspot instead"],
         0, "Contractors use guest WiFi. Staff WiFi gives access to internal systems.",
         "Reasonable excuse, contractor WiFi request", "Staff WiFi = staff only. Guests use guest.", "all"),

        ("Caller Asking Security Guard Times",
         "Someone calls asking what time the security guard goes home and what time the office is usually empty in the evening.\n\nWhat should you do?",
         ["Refuse and report the call to security", "Tell them since it is not secret information",
          "Give approximate times to be helpful today", "Ask why they need to know the schedule"],
         0, "Questions about security schedules are reconnaissance for a physical attack.",
         "Security schedule interest, unknown caller", "Security schedule questions = report them.", "all"),

        ("Stranger Borrowing ID Badge",
         "A stranger in the hallway asks to borrow your ID badge for 'just a minute' to access the meeting room. They say their host is running late.\n\nWhat should you do?",
         ["Refuse and escort them to wait at reception", "Lend your badge for just one quick minute",
          "Lend your badge but walk with them closely", "Ask them who their host is and check first"],
         0, "Lending your badge means they have your identity and access. Never do this.",
         "Temporary badge request, reasonable excuse", "Never lend your badge. Not even for a minute.", "all"),

        ("Cleaner Asking for Server Room Keys",
         "The office cleaner asks where the server room keys are kept so they can clean inside. They clean the rest of the office every day.\n\nWhat should you do?",
         ["Tell them the server room is restricted area", "Show them where the keys are for cleaning",
          "Give the keys but stay to watch them clean", "Ask your manager to make the final decision"],
         0, "Server rooms are restricted. Cleaning staff do not have access rights.",
         "Regular staff, unusual access request", "Server rooms = restricted. No cleaning inside.", "all"),

        ("Email List Request Over Phone",
         "A caller asks for a list of all employee email addresses. They say they need it for a company-wide survey from head office.\n\nWhat should you do?",
         ["Ask them to submit the request to HR by email", "Read out the email addresses over the phone",
          "Send only department head emails to be safe", "Ask for their employee ID to verify first"],
         0, "Email lists enable mass phishing attacks. All data requests go through HR.",
         "Bulk email request, head office claim", "Data requests go through HR. Always.", "all"),
    ]

    d2 = [
        ("Supplier Bank Detail Change",
         "A known supplier calls urgently saying they changed bank accounts. Update records before the next payment goes to the wrong account.\n\nWhat should you do?",
         ["Call them back on your saved phone number", "Update records since they called directly",
          "Update but keep old details as a backup", "Ask for the change on their letterhead"],
         0, "Bank detail changes need verification through a separate, trusted channel.",
         "Urgency, known supplier, bank change", "Bank changes = verify separately. Always.", "finance"),

        ("Building Inspector Full Access",
         "A person at reception claims to be a building inspector. They need immediate access to all areas including the server room for fire safety.\n\nWhat should you do?",
         ["Verify with your manager and building team", "Give access since inspections are important",
          "Give access except to the server room area", "Ask them to come back when the boss is in"],
         0, "Real inspectors schedule visits. Your management would know about them.",
         "Authority impersonation, full access demand", "Real inspectors have scheduled appointments.", "receptionist"),

        ("Research Access Request",
         "Someone calls saying they are a university student researching your industry. They ask very specific questions about pricing and client lists.\n\nWhat should you do?",
         ["Offer only info from your public website", "Help them since you were a student once too",
          "Share pricing but not any client details", "Ask them to email questions for a response"],
         0, "Competitors use student personas to extract sensitive business data.",
         "Student persona, specific business questions", "Public info only. Everything else is internal.", "sales"),

        ("Angry Customer Demanding CEO Info",
         "An extremely angry customer demands the CEO's personal phone number and home address. They threaten legal action if refused.\n\nWhat should you do?",
         ["Stay calm and offer the complaints channel", "Give the info to avoid legal problems now",
          "Give a fake number to calm them down fast", "Hang up since they are too aggressive"],
         0, "Anger is a social engineering tool. Redirect to proper complaints channels.",
         "Emotional manipulation, personal data request", "Anger is a weapon. Stay calm. Follow rules.", "receptionist"),

        ("Vendor Asking for Admin Login",
         "A software vendor calls asking for admin login to fix a bug urgently. They say the system might crash during payroll processing.\n\nWhat should you do?",
         ["Refuse and coordinate access through IT", "Give the login since you know this vendor",
          "Create temporary login with limited access", "Give login but change password right after"],
         0, "Vendors coordinate through IT for supervised access. Never share admin passwords.",
         "Known vendor, admin credential request", "Vendors work through IT. No direct passwords.", "finance"),

        ("Incoming Call from Microsoft",
         "A caller says they are from Microsoft and detected unusual activity on your server. They need remote access to fix it before data is lost.\n\nWhat should you do?",
         ["Hang up. Microsoft does not make such calls", "Give remote access to fix the problem",
          "Give access but watch the screen carefully", "Ask them for their Microsoft employee ID"],
         0, "Microsoft never calls individual companies about server issues.",
         "Microsoft impersonation, remote access request", "Microsoft does not cold-call about problems.", "it"),

        ("Password Reset Social Engineering",
         "Someone calls IT saying they are a manager and demand an immediate password reset for an employee account. They sound authoritative and impatient.\n\nWhat should you do?",
         ["Follow verification procedure regardless", "Reset it since they sound like a real manager",
          "Reset it but set a temporary weak password", "Ask them to submit a ticket by email first"],
         0, "Authority and impatience are manipulation tactics. Always follow verification.",
         "Authority tone, impatience, bypassing process", "Process exists for a reason. Follow it.", "it"),

        ("Pretexting: IT Contractor",
         "A person arrives unannounced saying they are a new IT contractor starting today. They ask for WiFi access, a desk, and a computer login.\n\nWhat should you do?",
         ["Ask them to wait while you verify with HR", "Set them up since contractors start often",
          "Give WiFi but not a computer login today", "Ask for their contract letter for proof"],
         0, "Unannounced contractors must be verified through HR. Social engineers use this excuse.",
         "Unannounced arrival, resource requests", "No announcement = no access. Verify with HR.", "all"),
    ]

    d3 = [
        ("Reverse Social Engineering",
         "You have computer problems. A coworker says a 'helpful tech support person' called yesterday and left their number. You consider calling.\n\nWhat should you do?",
         ["Only contact IT through official channels", "Call the number since coworker recommends it",
          "Call but do not share any login passwords", "Text the number first to check legitimacy"],
         0, "Reverse social engineering: the attacker plants their number and waits for you to call.",
         "Planted contact, you initiate the contact", "IT support = official channels only. Always.", "all"),

        ("Watering Hole Attack Discussion",
         "A vendor suggests your team visit a specific industry forum to download free security tools. They say many companies in Nepal use it.\n\nWhat should you do?",
         ["Only download tools approved by your IT", "Visit the forum since the vendor recommends it",
          "Download the tools on a personal device first", "Ask a coworker to check the forum first"],
         0, "Watering hole attacks compromise websites your industry commonly visits.",
         "Trusted recommendation, free tools, industry forum", "Only use IT-approved tools and websites.", "all"),

        ("CEO Impersonation via Deepfake Call",
         "A video call from your 'CEO' asks you to transfer funds to a new investment account. The video and voice look real but the request is unusual.\n\nWhat should you do?",
         ["Verify through a separate channel first", "Transfer since the video call looks genuine",
          "Transfer half the amount to reduce the risk", "Ask the CEO a personal question to verify"],
         0, "AI deepfake video calls can fool anyone. Always verify financial requests separately.",
         "Deepfake video, financial request, unusual", "Deepfakes exist. Verify money requests separately.", "finance"),

        ("Multi-Stage Pretexting Attack",
         "Over two weeks, someone befriends you at a nearby cafe. They gradually ask about your work, your office layout, and eventually which systems you use.\n\nWhat should you do?",
         ["Stop sharing work details with strangers", "Keep chatting since they are just friendly",
          "Share general info but nothing specific", "Introduce them to your coworkers at work"],
         0, "Long-term relationship building is advanced social engineering called pretexting.",
         "Gradual trust building, progressive questioning", "Strangers asking about work = red flag.", "all"),

        ("Quid Pro Quo Attack",
         "Someone calls offering free IT support. They will fix your slow computer if you just install a small remote access tool they will send you.\n\nWhat should you do?",
         ["Refuse and report the call to your IT", "Accept since free IT support saves money",
          "Install it but uninstall it right after fix", "Ask them to fix it without remote access"],
         0, "Quid pro quo: attackers offer something free in exchange for system access.",
         "Free help offer, remote access tool", "Free IT help from strangers = system compromise.", "all"),

        ("Insider Threat Social Engineering",
         "A new employee asks detailed questions about backup schedules, admin password policies, and which security software your company uses.\n\nWhat should you do?",
         ["Report concerns to your manager discreetly", "Answer since they are learning the company",
          "Answer general questions but not specifics", "Tell them to ask IT for all tech questions"],
         0, "New employees asking detailed security questions on day one is unusual.",
         "Day-one security questions, unusual interest", "New hires asking security details = flag it.", "all"),

        ("Dumpster Diving Prevention",
         "You see someone going through the company dumpster outside the office. They are collecting papers and putting them in a bag.\n\nWhat should you do?",
         ["Report to security or building management", "Ignore them since they might be recycling",
          "Ask them what they are looking for politely", "Chase them away from the dumpster area"],
         0, "Dumpster diving recovers discarded company info. Report and shred all documents.",
         "Searching company trash, document recovery", "Shred everything. Report dumpster divers.", "all"),
    ]

    for t, c, o, ci, e, rf, tip, role in d1:
        _add(_make(t, c, o, ci, e, rf, tip, C, 1, role))
    for t, c, o, ci, e, rf, tip, role in d2:
        _add(_make(t, c, o, ci, e, rf, tip, C, 2, role))
    for t, c, o, ci, e, rf, tip, role in d3:
        _add(_make(t, c, o, ci, e, rf, tip, C, 3, role))

_social()


# ════════════════════════════════════════════════════════════════════════════
# 8. DATA HANDLING. ~60 scenarios
# ════════════════════════════════════════════════════════════════════════════

def _data():
    C = "data_handling"

    d1 = [
        ("Work Files to Personal Gmail",
         "You want to finish a report at home. You think about emailing a spreadsheet with client contacts to your personal Gmail.\n\nWhat should you do?",
         ["Use your company cloud storage or VPN", "Email it since it is just a spreadsheet",
          "Email it but delete it from Gmail after", "Email it but remove the client names first"],
         0, "Personal email has no company security controls. Use approved tools.",
         "Company data leaving secure environment", "Company files stay on company tools.", "all"),

        ("Photo of Whiteboard Notes",
         "After a meeting, you photograph the whiteboard on your personal phone. It shows revenue targets and client names.\n\nWhat should you do?",
         ["Use a company device to take the photo", "Take the photo since you need the notes",
          "Take it but delete it when you are done", "Take it but blur out the client names"],
         0, "Personal phone photos auto-sync to cloud (Google Photos, iCloud) outside company control.",
         "Personal device, cloud backup risk", "Work notes stay on work devices.", "all"),

        ("Copying Files to Personal USB",
         "You copy company files to your personal USB drive to work on a presentation at home tonight.\n\nWhat should you do?",
         ["Use company cloud storage or VPN access", "Copy since it is just a presentation file",
          "Copy but encrypt the USB drive first now", "Copy only slides without company logos"],
         0, "Personal USBs are not encrypted or managed. If lost, data is exposed.",
         "Unmanaged device, loss risk", "Use cloud storage or VPN for home work.", "all"),

        ("Printing Confidential Document",
         "You need to print a confidential document. The shared printer is on a different floor and takes a few minutes to reach.\n\nWhat should you do?",
         ["Go to the printer right after you print", "Print now and collect it in thirty minutes",
          "Ask a coworker near it to collect for you", "Print and hope nobody reads it before you"],
         0, "Confidential documents on shared printers can be read by anyone.",
         "Shared printer, delay risk", "Print confidential docs only when you can collect.", "all"),

        ("Leaving Documents on Desk Overnight",
         "You leave printed client contracts on your desk when going home. You plan to work on them first thing tomorrow morning.\n\nWhat should you do?",
         ["Lock them in a drawer before leaving work", "Leave them since the office is locked at night",
          "Put a folder on top to hide the contents", "Take them home to work on them tonight"],
         0, "Cleaning staff, early arrivals, or visitors could see documents left out overnight.",
         "Documents in open overnight, cleaning access", "Lock documents away at end of every day.", "all"),

        ("Discussing Secrets in Cafe",
         "At a cafe near the office, you and a coworker discuss a confidential client deal. The client name and deal value are mentioned aloud.\n\nWhat should you do?",
         ["Stop and continue the talk at the office", "Lower your voice and keep the conversation",
          "Use code words for the client name only", "Continue since nobody knows your company"],
         0, "You never know who is listening. Competitors could be at the next table.",
         "Public space, no audience control", "Confidential talks happen behind closed doors.", "all"),

        ("Screenshot of Internal Email Online",
         "A coworker posts a screenshot of a funny internal email on Instagram. Company info is visible in the background of the shot.\n\nWhat should you do?",
         ["Privately ask them to delete the post", "Like the post because it is very funny",
          "Report to HR immediately without telling them", "Screenshot the post for evidence later"],
         0, "Internal emails are company property. Competitors and media can use leaked info.",
         "Internal info on public social media", "Internal = internal. Nothing goes on social media.", "all"),

        ("Talking on Phone in Public Transport",
         "You are on a bus call discussing a project deadline and budget with your manager. Other passengers can hear everything.\n\nWhat should you do?",
         ["End the call and continue at the office", "Keep talking but lower your voice a bit",
          "Use code words for the project and budget", "Move to the back of the bus for privacy"],
         0, "Public transport conversations are overheard by strangers. Wait until private.",
         "Public transport, audible conversation", "Work calls = private places only.", "all"),
    ]

    d2 = [
        ("Old Hard Drive Disposal",
         "Your office replaces old computers. Your manager says throw the old hard drives in the bin since the data is 5 years old.\n\nWhat should you do?",
         ["Give them to IT for secure data wiping", "Throw them out since data is very old now",
          "Delete visible files and throw them away", "Format the drives yourself then throw away"],
         0, "Deleting or formatting does not erase data. Free tools can recover it all.",
         "Simple deletion does not erase data", "IT must securely destroy data on old drives.", "all"),

        ("Guest Logbook in Regular Trash",
         "The guest visitor logbook is full. You think about throwing it in the regular dustbin to make space for a new one.\n\nWhat should you do?",
         ["Shred it or give it to office manager", "Throw it since guest names are not important",
          "Tear pages and scatter in different bins", "Keep it in your drawer indefinitely now"],
         0, "Guest logbooks contain personal data. They must be shredded.",
         "Personal data in visitor log, improper disposal", "Visitor logs = personal data. Shred them.", "receptionist"),

        ("Payroll Sent to Wrong Email",
         "You accidentally emailed the payroll spreadsheet with all salaries to someone outside the company. You notice immediately.\n\nWhat should you do?",
         ["Tell your manager and IT right away now", "Send a follow-up asking them to delete it",
          "Do nothing and hope they ignore the email", "Try to recall the email using the feature"],
         0, "Salary data sent externally is a data breach. Report immediately.",
         "Data sent to wrong recipient, salary info", "Report data mistakes immediately. Do not hide.", "finance"),

        ("Client List in WhatsApp Group",
         "A coworker shares a client list with phone numbers in the team WhatsApp group. Former employees who quit are still members.\n\nWhat should you do?",
         ["Ask them to delete it and use company tools", "It is fine since it is a work team group",
          "Save the list to your phone for quick access", "Remove ex-employees then it should be fine"],
         0, "Ex-employees in the group can see and forward client data.",
         "Former employees in group, personal devices", "Company data goes on company tools only.", "sales"),

        ("Backup to Free Cloud Service",
         "A team member suggests backing up the customer database to a free cloud service because the backup server is running out of space.\n\nWhat should you do?",
         ["Refuse and request proper storage from IT", "Use free cloud temporarily until server fixed",
          "Upload encrypted backup to free cloud now", "Use free cloud and delete it once fixed"],
         0, "Free cloud services lack security guarantees for customer data.",
         "Customer data on uncontrolled platform", "Customer data needs enterprise storage only.", "it"),

        ("Sharing Sales Data Verbally",
         "During a networking event, someone asks about your company's quarterly revenue. You know the exact number but it has not been published yet.\n\nWhat should you do?",
         ["Politely decline to share the figures now", "Share since it will be public next month",
          "Give a rough estimate but not exact number", "Share if they share their company's data too"],
         0, "Unpublished financial data is confidential. It gives competitors an advantage.",
         "Unpublished financial data, social setting", "Unpublished numbers = confidential. Always.", "sales"),

        ("Employee Medical Records Left Out",
         "You see an employee's medical sick note left on a shared desk in the HR area. It shows their diagnosis and personal information.\n\nWhat should you do?",
         ["Put it in a locked folder and tell HR now", "Leave it since HR will collect it later",
          "Read it to check if the employee is alright", "Take a photo for your records just in case"],
         0, "Medical records are highly sensitive personal data. Secure them immediately.",
         "Medical data in public, privacy violation", "Medical records must be locked away always.", "hr"),

        ("Forwarding CV With Personal Details",
         "A friend asks you to forward a candidate's CV to them. The CV has the candidate's home address, phone number, and date of birth.\n\nWhat should you do?",
         ["Refuse. CVs contain protected personal data", "Forward it since your friend asked politely",
          "Forward but remove the personal details first", "Ask the candidate for permission to forward"],
         0, "CVs contain personal data. Forwarding without consent may violate privacy laws.",
         "Personal data sharing, no consent obtained", "CVs = personal data. Need consent to share.", "hr"),
    ]

    d3 = [
        ("Database Export on Unsecured Laptop",
         "You export a database of 5,000 customer records to your laptop for analysis. The laptop does not have full-disk encryption enabled.\n\nWhat should you do?",
         ["Enable encryption before storing any data", "Proceed since laptop has a strong password",
          "Store on an encrypted USB drive attached", "Delete the export after analysis is done"],
         0, "Without disk encryption, a stolen laptop exposes all data. Enable encryption first.",
         "Unencrypted device, bulk customer data", "Full-disk encryption is mandatory for data.", "all"),

        ("Data Retention Policy Violation",
         "You discover that your team keeps customer records for 7 years even though company policy says delete them after 3 years.\n\nWhat should you do?",
         ["Report it and start the deletion process", "Keep them since more data is always better",
          "Archive them to a different storage location", "Wait for the annual audit to deal with it"],
         0, "Retaining data beyond policy creates legal liability. Delete as policy requires.",
         "Policy violation, excess data retention", "Follow retention policy. Old data = liability.", "all"),

        ("Third-Party Data Sharing Request",
         "A partner company asks for access to your customer database for a 'joint marketing campaign'. There is no data sharing agreement in place.\n\nWhat should you do?",
         ["Refuse until a formal agreement is signed", "Share it since they are a trusted partner",
          "Share anonymized data without real names", "Share a small sample to test the campaign"],
         0, "Data sharing without a formal agreement violates privacy regulations.",
         "No data sharing agreement, partner request", "No agreement = no data sharing. Get it signed.", "all"),

        ("Shadow IT Data Storage",
         "You discover that a team member has been using their personal Dropbox to store company reports for two years because it is faster.\n\nWhat should you do?",
         ["Report it and migrate data to company tools", "Let it continue since it has worked fine",
          "Ask them to password-protect the Dropbox", "Tell them to use Google Drive instead"],
         0, "Personal cloud storage is 'shadow IT'. outside company security and compliance.",
         "Shadow IT, unapproved data storage", "Company data on personal cloud = shadow IT.", "all"),

        ("Cross-Border Data Transfer Issue",
         "Your company stores Nepal customer data on servers in India without checking if this complies with Nepal's data protection laws.\n\nWhat should you do?",
         ["Flag it to management for legal review now", "It is fine since India is a neighbor country",
          "Move the data back to Nepal servers quietly", "Wait until a lawyer mentions it in audit"],
         0, "Cross-border data transfers have legal requirements. Management must review.",
         "Cross-border transfer, legal compliance risk", "Cross-border data = legal review required.", "all"),

        ("Incident Response Data Handling",
         "During a data breach investigation, you are told to preserve all logs and not delete anything. A coworker suggests deleting suspicious files.\n\nWhat should you do?",
         ["Refuse. deleting evidence is a serious issue", "Delete them to stop the breach from spreading",
          "Move the files to a different server location", "Copy the files before deleting the originals"],
         0, "Deleting evidence during a breach investigation can have legal consequences.",
         "Evidence preservation, breach investigation", "During investigations: preserve everything.", "all"),

        ("BYOD Policy Gap Exploitation",
         "Your company allows personal devices but has no Mobile Device Management (MDM). Staff store company emails and files on unmanaged phones.\n\nWhat should you do?",
         ["Raise the issue with IT for an MDM solution", "Continue since personal phones work just fine",
          "Install a free antivirus on your own phone", "Use only WiFi to access company data safely"],
         0, "Unmanaged personal devices with company data are a breach waiting to happen.",
         "No MDM, company data on personal devices", "BYOD needs MDM. Raise it with IT.", "it"),
    ]

    for t, c, o, ci, e, rf, tip, role in d1:
        _add(_make(t, c, o, ci, e, rf, tip, C, 1, role))
    for t, c, o, ci, e, rf, tip, role in d2:
        _add(_make(t, c, o, ci, e, rf, tip, C, 2, role))
    for t, c, o, ci, e, rf, tip, role in d3:
        _add(_make(t, c, o, ci, e, rf, tip, C, 3, role))

_data()


# ════════════════════════════════════════════════════════════════════════════
# 9. EXTRA SCENARIOS. fill to ~500
# ════════════════════════════════════════════════════════════════════════════

def _extra_phishing():
    C = "phishing_email"
    items = [
        ("WhatsApp Account Verification",
         "An email from 'WhatsApp Security' says verify your account by clicking a link or lose your chat history.\n\nWhat should you do?",
         ["Ignore it. WhatsApp does not send these", "Click the link to keep your chats safe",
          "Forward the email to WhatsApp support", "Reply asking if the message is real"],
         0, "WhatsApp does not send verification emails. This steals your account.",
         "WhatsApp impersonation, chat loss fear", "WhatsApp does not send emails. Ever.", "all", 1),

        ("LinkedIn Job Opportunity Message",
         "An email from LinkedIn says a Fortune 500 company wants to hire you. Click to see the offer letter.\n\nWhat should you do?",
         ["Log into LinkedIn directly to check inbox", "Click the link to view the job offer",
          "Reply with your updated CV and details", "Forward the email to your HR department"],
         0, "LinkedIn job messages show up in the app. Email links redirect to fake pages.",
         "Dream job bait, LinkedIn impersonation", "Check LinkedIn in the app, not email links.", "all", 1),

        ("Meeting Minutes Malware",
         "An email from an unknown person says 'Attached are the meeting minutes from today.' You did not attend any external meeting.\n\nWhat should you do?",
         ["Delete it since you attended no meeting", "Open it to check what meeting it is about",
          "Forward it to your manager to verify it", "Save the file but do not open it yet"],
         0, "Attackers send fake meeting minutes with malware attachments.",
         "Unknown sender, unexpected attachment", "No meeting = no real meeting minutes.", "all", 1),

        ("Adobe Cloud Storage Warning",
         "An email says your Adobe Cloud storage is full. Upgrade now or lose your saved files. You do not use Adobe Cloud.\n\nWhat should you do?",
         ["Delete it. you do not use this service", "Click to upgrade in case files are at risk",
          "Reply asking what files are being stored", "Forward it to IT to check for you today"],
         0, "If you do not use a service, emails from it are fake.",
         "Service you do not use, urgency", "No account = no real email. Delete it.", "all", 1),

        ("Charity Donation Appeal",
         "An email asks for donations to earthquake victims in Nepal. The link goes to a page that asks for credit card details.\n\nWhat should you do?",
         ["Donate through a verified charity website", "Enter card details to help the victims",
          "Share the link so more people can donate", "Reply asking which charity this is for"],
         0, "Scammers exploit disasters. Always donate through verified charity websites.",
         "Emotional manipulation, disaster exploitation", "Donate through verified charity sites only.", "all", 2),

        ("DocuSign Signature Request",
         "An email from 'DocuSign' asks you to review and sign a contract. You are not expecting any contract. The email looks very professional.\n\nWhat should you do?",
         ["Delete it since you expect no contract", "Click to review it just in case it is real",
          "Reply asking what the contract is about", "Forward it to your legal department now"],
         0, "DocuSign phishing is common. If you are not expecting a document, do not click.",
         "Professional appearance, unexpected document", "Not expecting a contract = not real.", "all", 2),

        ("Google Drive Shared Doc Alert",
         "An email says someone shared a Google Doc with you. The sender's email has a subtle typo. The document title is 'Q4 Budget Review.'\n\nWhat should you do?",
         ["Go to Google Drive directly to check docs", "Click the link since the title is relevant",
          "Reply asking who shared the document today", "Forward the email to your finance team"],
         0, "Fake Google Doc sharing notifications are a common phishing method.",
         "Relevant title bait, email typo", "Go directly to Drive. Never click email links.", "finance", 2),

        ("IT Audit Compliance Email",
         "An email says your company failed an IT audit. Click a link to download the compliance report. Your IT team has not mentioned any audit.\n\nWhat should you do?",
         ["Ask your IT team about any recent audits", "Click the link to see the audit findings",
          "Reply to the email asking for more details", "Forward the report to your IT director"],
         0, "Audit-themed phishing exploits authority and compliance fear.",
         "Audit fear, IT impersonation, download link", "IT knows about audits. Ask them first.", "it", 2),

        ("Zoom Meeting Recording Email",
         "An email says you missed an important Zoom meeting. Click to watch the recording. You were not invited to any such meeting.\n\nWhat should you do?",
         ["Delete it since you were not invited", "Click to watch what the meeting was about",
          "Reply asking who organized the meeting today", "Forward the link to your whole team"],
         0, "Fake Zoom recording links are designed to steal your login credentials.",
         "FOMO bait, fake meeting recording link", "No invitation = no real meeting recording.", "all", 2),

        ("Vendor Proposal Phishing Email",
         "An email from a potential vendor attaches a 'Detailed Proposal' as a .docm file. Your procurement team has been looking for vendors.\n\nWhat should you do?",
         ["Ask the vendor to send a PDF by email", "Open it since procurement needs proposals",
          "Open it but disable macros for safety now", "Save it and ask IT to scan it tomorrow"],
         0, ".docm files contain macros that can run malware. Request PDFs instead.",
         "Macro-enabled file, relevant business context", "Ask for PDFs. Never open .docm files.", "all", 3),

        ("HMRC Tax Refund Notification",
         "An email from 'HMRC' (UK tax office) says your company is due a refund. Click to claim. Your company only operates in Nepal.\n\nWhat should you do?",
         ["Delete it. your company is not in the UK", "Click just to check if there is a refund",
          "Forward it to your accountant for review", "Reply asking how they got your email"],
         0, "Foreign tax office emails targeting Nepali companies are always scams.",
         "Foreign government, irrelevant jurisdiction", "Foreign tax emails = always fake.", "finance", 1),

        ("IT Security Alert Email",
         "An email from 'IT Security Department' warns that your account was compromised. Reset password using the link provided before noon.\n\nWhat should you do?",
         ["Walk to IT and ask about the alert now", "Click the link to reset before the deadline",
          "Reply asking which account was compromised", "Forward it to IT to verify the alert"],
         0, "IT department alerts should be verified in person or through known channels.",
         "IT impersonation, noon deadline pressure", "IT alerts need verification in person.", "all", 2),

        ("Customer Feedback Survey Email",
         "An email says a customer left negative feedback and your manager wants you to read it. Click a link to view the full feedback.\n\nWhat should you do?",
         ["Ask your manager in person about feedback", "Click the link to read what was said",
          "Reply asking which customer left feedback", "Forward it to your customer service team"],
         0, "Negative feedback emails exploit your desire to fix problems quickly.",
         "Curiosity and worry bait, manager mention", "Ask your manager directly about feedback.", "all", 2),

        ("Subscription Renewal Notice",
         "An email says your annual software subscription auto-renewed for Rs. 45,000. Click to cancel if you did not approve this.\n\nWhat should you do?",
         ["Check the subscription through official site", "Click to cancel the unwanted renewal now",
          "Reply asking for an invoice number first", "Call the number provided in the email"],
         0, "Fake renewal emails use fear of unwanted charges to make you click.",
         "Cancellation urgency, large unexpected charge", "Check subscriptions on the official site.", "all", 3),

        ("Board Meeting Invite Phishing",
         "An email invites you to an urgent board meeting next Monday. Click to confirm attendance. You have never been invited to board meetings before.\n\nWhat should you do?",
         ["Check with your manager about the invite", "Click to confirm since it seems important",
          "Reply asking who organized the board meeting", "Forward the invite to your department head"],
         0, "Unusual or elevated access invitations are often targeted phishing.",
         "Unusual access level, urgent meeting invite", "First-time board invite = verify with boss.", "all", 3),

        ("Payroll Update Notification",
         "An email from 'Payroll Department' asks you to verify your bank details for the next salary transfer. Click a link to update.\n\nWhat should you do?",
         ["Visit payroll in person to check this out", "Click the link to verify your bank details",
          "Reply with your current bank information", "Forward the email to your manager first"],
         0, "Payroll departments never ask for bank details through email links.",
         "Payroll impersonation, bank details request", "Payroll changes happen in person. Always.", "all", 2),

        ("Package Tracking Number Phishing",
         "An email with a subject 'Your Tracking Number' contains a link to track a package. You recently ordered something online from Daraz.\n\nWhat should you do?",
         ["Track the order from the Daraz app itself", "Click the link since you expect a package",
          "Reply asking what is in the package today", "Forward the tracking link to your friend"],
         0, "Attackers know many people expect packages. Always track from the original app.",
         "Relevant timing, tracking link bait", "Track packages from the store app directly.", "all", 2),

        ("HR Policy Update Notification",
         "An email from 'HR' says the leave policy has changed. Download the new policy document from an attached file.\n\nWhat should you do?",
         ["Check the HR portal for any policy updates", "Download the file to read the new policy",
          "Reply asking HR to summarize the changes", "Forward the attachment to all your team"],
         0, "HR posts policy updates on the portal. Attachments from email can contain malware.",
         "HR impersonation, malicious attachment risk", "HR policies are on the portal, not in email.", "hr", 2),

        ("Domain Expiry Notification",
         "An email says your company domain expires in 12 hours. Pay now to keep it. Your IT team manages all domain registrations.\n\nWhat should you do?",
         ["Let IT know about the domain expiry email", "Pay immediately to keep your website up",
          "Reply asking for an invoice or receipt first", "Call the number in the email to discuss"],
         0, "Domain registrars email weeks in advance. Same-day threats are scams.",
         "12-hour deadline, domain loss panic", "IT manages domains. Tell them, not the email.", "it", 2),

        ("Award Nomination Email",
         "An email says you were nominated for a 'Best Employee Award.' Click to accept the nomination and provide your personal details.\n\nWhat should you do?",
         ["Ask HR if any award program is running", "Click to accept the nomination right away",
          "Reply asking who nominated you for the award", "Forward the email to your whole team"],
         0, "Flattery-based phishing exploits your ego. Always verify with HR.",
         "Flattery bait, personal details request", "Awards need HR confirmation, not email links.", "all", 3),
    ]

    for t, c, o, ci, e, rf, tip, role, diff in items:
        _add(_make(t, c, o, ci, e, rf, tip, C, diff, role))

_extra_phishing()


def _extra_smishing():
    C = "smishing"
    items = [
        ("Ncell Reward Points SMS",
         "An SMS says you earned 5,000 Ncell reward points about to expire. Click a link to redeem before midnight tonight.\n\nWhat should you do?",
         ["Check the Ncell app for any reward points", "Click the link to redeem before midnight",
          "Reply to the SMS asking about the points", "Forward the SMS to Ncell customer care"],
         0, "Ncell sends reward notifications in the app, not through random SMS links.",
         "Expiry urgency, reward points bait", "Check rewards through the official app.", "all", 1),

        ("Hospital Bill Payment SMS",
         "An SMS says you have an unpaid hospital bill of Rs. 15,000. Click to pay or face legal action. You have not visited any hospital recently.\n\nWhat should you do?",
         ["Delete the SMS. you owe no hospital bill", "Click the link to check the bill details",
          "Call the number in the SMS to ask about it", "Pay a small amount to avoid legal action"],
         0, "If you have not visited a hospital, any bill SMS is fake.",
         "Legal threat, no hospital visit", "No visit = no bill. Delete and ignore.", "all", 1),

        ("KYC Verification SMS",
         "An SMS says your bank needs KYC verification within 24 hours. Click a link to upload your citizenship and photo.\n\nWhat should you do?",
         ["Visit your bank branch for KYC in person", "Click the link and upload your documents",
          "Reply asking which bank is requesting KYC", "Call the number in the SMS to verify"],
         0, "Banks handle KYC at branches. They never ask for citizenship uploads via SMS links.",
         "24-hour deadline, document upload request", "KYC happens at the bank. Not via SMS links.", "all", 2),

        ("FonePay Transaction Alert",
         "An SMS says a Rs. 25,000 FonePay transaction was made from your account. Click to dispute if you did not make it.\n\nWhat should you do?",
         ["Check your bank app for any transactions", "Click the link to dispute the transaction",
          "Reply STOP to cancel the transaction now", "Call the number in the SMS immediately"],
         0, "FonePay and banks use their own apps for dispute. SMS dispute links are fake.",
         "Fake transaction alert, dispute link bait", "Dispute through your bank app directly.", "all", 2),

        ("Immigration Visa SMS",
         "An SMS says your visa application was approved. Click a link and pay Rs. 3,000 processing fee. You never applied for any visa.\n\nWhat should you do?",
         ["Delete it. you never applied for a visa", "Click to check which visa was approved",
          "Pay Rs. 3,000 since it is a small amount", "Forward the SMS to the immigration office"],
         0, "No visa application = no approval. This is advance fee fraud.",
         "No application made, processing fee request", "No application = no approval. Always.", "all", 1),

        ("WhatsApp Gold Upgrade SMS",
         "An SMS promotes 'WhatsApp Gold' with extra features. Click a link to upgrade your WhatsApp for free before the offer expires.\n\nWhat should you do?",
         ["Ignore it. WhatsApp Gold does not exist", "Click to get the special features for free",
          "Forward it to friends who might want it", "Reply asking about the extra features now"],
         0, "WhatsApp Gold is a well-known hoax used to distribute malware.",
         "Fake product, free upgrade bait", "WhatsApp Gold is fake. Always has been.", "all", 1),

        ("Electricity Bill Overdue SMS",
         "An SMS says your Nepal Electricity Authority bill is overdue. Pay via a link or face disconnection today. Your bill was paid last week.\n\nWhat should you do?",
         ["Ignore it since your bill is already paid", "Click to pay again to avoid disconnection",
          "Reply asking for your account number first", "Call NEA on their official support number"],
         0, "If your bill was paid, any overdue message is fake.",
         "Already paid, disconnection threat", "Already paid = ignore overdue messages.", "all", 1),

        ("Investment Scheme SMS",
         "An SMS promises 200% returns on a Rs. 10,000 investment within 30 days. 'Limited slots available. act now.'\n\nWhat should you do?",
         ["Delete it. guaranteed returns are a scam", "Invest since the return sounds very good",
          "Invest only Rs. 1,000 to test it first", "Reply asking for their office address now"],
         0, "Guaranteed high returns are always a scam. Legitimate investments carry risk.",
         "Guaranteed returns, urgency, limited slots", "Guaranteed returns = guaranteed scam.", "all", 2),

        ("Government Subsidy SMS",
         "An SMS from 'Nepal Government' says you qualify for a Rs. 50,000 subsidy. Click to register with your citizenship number.\n\nWhat should you do?",
         ["Ignore it. government uses official channels", "Click to register for the free subsidy",
          "Enter citizenship to check eligibility first", "Forward the SMS to your family for advice"],
         0, "Government subsidies are announced officially, not through random SMS links.",
         "Government impersonation, citizenship request", "Government programs use official channels.", "all", 2),

        ("Job Offer From Unknown Company",
         "An SMS offers you a job with a Rs. 80,000 monthly salary at a company you never heard of. Click to apply immediately.\n\nWhat should you do?",
         ["Delete it. unsolicited job offers are scams", "Click to see the job description details",
          "Reply asking about the job responsibilities", "Forward it to friends looking for jobs"],
         0, "Legitimate companies do not send unsolicited job offers via random SMS.",
         "Unsolicited job offer, unknown company", "Real jobs are not offered via random SMS.", "all", 1),

        ("Fake Prize Draw SMS",
         "An SMS says your phone number was selected in a prize draw. Claim Rs. 1,00,000 by clicking a link within 6 hours.\n\nWhat should you do?",
         ["Delete it. phone numbers are not in draws", "Click the link before the 6 hours expire",
          "Reply asking which organization held the draw", "Call the number to verify the prize draw"],
         0, "Phone numbers are not entered into prize draws. This is a common scam.",
         "Random selection claim, tight deadline", "Your phone number cannot win a prize draw.", "all", 1),

        ("Credit Card Activation SMS",
         "An SMS says your new credit card is ready. Click a link to activate it. You never applied for a credit card.\n\nWhat should you do?",
         ["Delete it. you never applied for a card", "Click to check what credit card it is",
          "Call the number in the SMS to ask about it", "Reply CANCEL to stop the card activation"],
         0, "If you never applied for a credit card, this SMS is harvesting your data.",
         "No application, card activation bait", "No application = no card. Delete the SMS.", "all", 1),

        ("Fake Property Tax Notice SMS",
         "An SMS from 'Ward Office' says you owe property tax. Click to pay or face a penalty. You already paid your property tax.\n\nWhat should you do?",
         ["Ignore it since your tax is already paid", "Click the link to check the tax amount",
          "Reply asking for the property registration", "Visit the ward office to verify in person"],
         0, "Ward offices do not send SMS payment links. They send paper notices.",
         "Government impersonation, already paid", "Government offices use paper, not SMS links.", "all", 2),

        ("SIM Registration Warning SMS",
         "An SMS warns your SIM will be blocked due to 'incomplete registration.' Click to verify your identity within 48 hours.\n\nWhat should you do?",
         ["Visit your carrier store to check in person", "Click the link to complete registration",
          "Reply with your citizenship number to verify", "Call your carrier's customer care number"],
         0, "Carriers do not block SIMs via SMS links. They send proper notices.",
         "SIM block threat, identity verification bait", "SIM issues = visit the carrier store.", "all", 2),

        ("Fake Health Insurance SMS",
         "An SMS says you qualify for free government health insurance. Click to enroll with your name and citizenship number.\n\nWhat should you do?",
         ["Check official government sites for schemes", "Click the link to enroll for free insurance",
          "Enter only your name but not citizenship ID", "Forward the SMS to friends and family"],
         0, "Government insurance schemes are enrolled through proper channels, not SMS.",
         "Free insurance bait, citizenship data request", "Government schemes use official enrollment.", "all", 2),

        ("Fake Survey Cash Reward SMS",
         "An SMS offers Rs. 5,000 cash for completing a 2-minute survey. Click a link to start. 'Only 50 slots remaining.'\n\nWhat should you do?",
         ["Delete it. surveys do not pay that much", "Click to complete the quick survey today",
          "Complete the survey but skip bank details", "Forward to friends who could use the money"],
         0, "No legitimate survey pays Rs. 5,000 for 2 minutes. This collects personal data.",
         "Too good to be true, scarcity pressure", "No 2-minute survey pays Rs. 5,000.", "all", 1),

        ("Ride Share Surge Pricing SMS",
         "An SMS from an unknown number says Pathao surge pricing is active. Use a special code via a link for 50% discount on your next ride.\n\nWhat should you do?",
         ["Ignore it. Pathao deals are in the app", "Click the link to get the discount code",
          "Share the code with friends for discounts", "Reply asking for the promo code directly"],
         0, "Pathao promotions are only in the official app. External SMS deals are fake.",
         "Discount bait, unofficial channel", "App deals are only in the official app.", "all", 1),

        ("WhatsApp Payment Received SMS",
         "An SMS says someone sent you Rs. 15,000 via WhatsApp Pay. Click to accept. WhatsApp Pay is not available in Nepal.\n\nWhat should you do?",
         ["Delete it. WhatsApp Pay is not in Nepal", "Click the link to accept the money now",
          "Forward to a friend who knows about tech", "Reply asking who sent the money to you"],
         0, "WhatsApp Pay does not exist in Nepal. This SMS is a scam.",
         "Non-existent service, money acceptance bait", "WhatsApp Pay is not available in Nepal.", "all", 1),

        ("Fake Court Summons SMS",
         "An SMS says you have a court summons for unpaid debts. Click a link to view the case details. You have no pending legal matters.\n\nWhat should you do?",
         ["Ignore it. courts do not send SMS summons", "Click the link to check the case details",
          "Call the number to discuss the court case", "Reply asking which court sent the summons"],
         0, "Courts serve legal notices in person or by mail, never through SMS links.",
         "Legal intimidation, court impersonation", "Courts do not issue summons by SMS.", "all", 2),

        ("Parcel Return Fee SMS",
         "An SMS says a parcel you sent was returned. Pay Rs. 300 return fee via a link. You did not send any parcel recently.\n\nWhat should you do?",
         ["Delete it. you did not send any parcel", "Pay Rs. 300 since it is a small amount",
          "Click the link to check which parcel it is", "Call the courier company from their website"],
         0, "No parcel sent = no return fee owed. Small amounts are used to lower your guard.",
         "No parcel sent, small fee manipulation", "No parcel = no fee. Delete and ignore.", "all", 1),
    ]

    for t, c, o, ci, e, rf, tip, role, diff in items:
        _add(_make(t, c, o, ci, e, rf, tip, C, diff, role))

_extra_smishing()


def _extra_vishing():
    C = "vishing"
    items = [
        ("Fake Electricity Department Call",
         "A caller says they are from Nepal Electricity Authority. Your power will be cut in 1 hour unless you pay Rs. 5,000 via eSewa right now.\n\nWhat should you do?",
         ["Hang up and check your bill status online", "Pay via eSewa to keep your power running",
          "Ask them to hold while you get the money", "Give your eSewa account details to them"],
         0, "NEA does not call for instant eSewa payments. Check your bill through their office.",
         "Instant payment demand, disconnection threat", "NEA does not collect bills by phone.", "all", 1),

        ("Fake Insurance Claim Call",
         "A caller says your medical insurance claim was approved for Rs. 50,000. Share your bank details to receive the payment immediately.\n\nWhat should you do?",
         ["Call your insurance company from your card", "Share bank details to get the payment",
          "Give only your account number, not the PIN", "Ask them to send you a cheque instead"],
         0, "Insurance companies process claims through official channels, not random calls.",
         "Insurance bait, bank details request", "Insurance claims go through official process.", "all", 1),

        ("Fake HR Benefits Call",
         "A caller says they are from your company's HR partner. You qualify for additional benefits. They need your PAN number and date of birth.\n\nWhat should you do?",
         ["Tell them to contact HR directly instead", "Give details since benefits sound attractive",
          "Give only your PAN but not date of birth", "Ask for their company name and call back"],
         0, "HR benefits are managed through your company, not random phone calls.",
         "Benefits bait, PAN and DOB harvesting", "Benefits come through your HR, not calls.", "hr", 2),

        ("Tech Guru Scam Call",
         "A caller offers a free 'complete computer cleanup' for your office. They need remote access to start. 'This service is worth Rs. 10,000.'\n\nWhat should you do?",
         ["Refuse. IT handles all computer services", "Accept the free service to save money now",
          "Let them access one computer to test first", "Ask them to send a quote to your IT team"],
         0, "Free tech support calls are a classic way to install malware via remote access.",
         "Free service bait, remote access request", "Computer services go through IT only.", "all", 2),

        ("Kidnapping Ransom Scam Call",
         "A panicked caller says they kidnapped your family member. They demand Rs. 2,00,000 immediately. In the background you hear crying.\n\nWhat should you do?",
         ["Hang up and call your family member now", "Pay the ransom to keep your family safe",
          "Ask to speak with the family member first", "Transfer a smaller amount and negotiate"],
         0, "Virtual kidnapping scams use panic. Hang up and verify with your family.",
         "Panic tactics, emotional manipulation, ransom", "Call your family first. Verify. Stay calm.", "all", 3),

        ("Fake Scholarship Call",
         "A caller says your child won a scholarship. Pay Rs. 5,000 registration fee by phone to secure the spot before tomorrow.\n\nWhat should you do?",
         ["Contact the school or university directly", "Pay the fee to secure the scholarship now",
          "Ask them to email the scholarship details", "Pay but ask for a receipt by email first"],
         0, "Real scholarships do not require phone payments. Contact the institution directly.",
         "Scholarship bait, phone payment request", "Scholarships do not require phone payments.", "all", 2),

        ("Fake Charity Phone Drive",
         "A caller from a 'children's charity' asks for a Rs. 10,000 donation right now. They can take your credit card details over the phone.\n\nWhat should you do?",
         ["Donate through verified charity sites only", "Give your credit card details to donate now",
          "Donate a smaller amount like Rs. 1,000 only", "Ask them to send donation info by email"],
         0, "Legitimate charities never pressure for immediate phone donations.",
         "Emotional appeal, phone payment pressure", "Donate through official charity websites.", "all", 2),

        ("Fake Census Call",
         "A caller says they are conducting the national census. They need your full name, citizenship number, income, and bank account details.\n\nWhat should you do?",
         ["Refuse. census takers visit in person only", "Give details since the census is important",
          "Give only name and address, not bank info", "Ask for their census officer ID number now"],
         0, "Census data is collected in person by official enumerators, never by phone.",
         "Government impersonation, bulk data request", "Census is done in person. Never by phone.", "all", 2),

        ("Fake Pension Update Call",
         "A caller from 'Social Security Fund' says your pension details need updating. Share your citizenship and bank details over the phone.\n\nWhat should you do?",
         ["Visit the SSF office to update in person", "Share details to keep your pension correct",
          "Share citizenship but not your bank details", "Ask them to send a letter to your address"],
         0, "SSF manages updates at their offices, not through random phone calls.",
         "Pension fear, official impersonation", "Pension updates happen at the SSF office.", "all", 2),

        ("Fake Hotel Reservation Call",
         "A caller says you have a hotel reservation and your card will be charged Rs. 20,000 unless you cancel now by confirming your card number.\n\nWhat should you do?",
         ["Hang up. you made no hotel reservation", "Give your card number to cancel the charge",
          "Give the card number but not the CVV code", "Ask them which hotel and dates were booked"],
         0, "Charge fear makes you share card details. No reservation = no charge.",
         "Charge fear, card number harvesting", "No reservation made = no charge possible.", "all", 2),

        ("Fake Network Upgrade Call",
         "A caller from 'Ncell' says your number is being upgraded to 5G. They need your SIM PIN and account password to complete the process.\n\nWhat should you do?",
         ["Hang up and visit an Ncell service center", "Give your SIM PIN for the 5G upgrade",
          "Give only your account name, not the PIN", "Ask them to upgrade it at the store next"],
         0, "Ncell does not call for SIM upgrades. Upgrades happen at service centers.",
         "5G bait, SIM PIN and password request", "Network upgrades happen at service centers.", "all", 1),

        ("Fake Award Ceremony Call",
         "A caller says your company won a 'Best Business Award.' Pay Rs. 15,000 registration fee to attend the ceremony.\n\nWhat should you do?",
         ["Refuse. real awards do not charge to attend", "Pay to attend the award ceremony event",
          "Ask for a brochure before paying the fee", "Check online if the award show is real"],
         0, "Legitimate awards do not charge winners registration fees.",
         "Flattery bait, registration fee scam", "Real awards do not charge winners to attend.", "management", 2),

        ("Fake NRB Monetary Policy Call",
         "A caller from 'Nepal Rastra Bank' says new monetary policy requires all businesses to verify bank details by phone within 24 hours.\n\nWhat should you do?",
         ["Contact NRB through their official channels", "Give bank details to comply with the policy",
          "Give only the account number, not passwords", "Ask them to send the policy by email now"],
         0, "NRB does not call individual businesses for bank verification.",
         "Central bank impersonation, compliance pressure", "NRB communicates through official notices.", "finance", 3),

        ("Fake Customs Clearance Call",
         "A caller says your international package needs customs clearance. Pay Rs. 8,000 via phone or the package will be returned.\n\nWhat should you do?",
         ["Contact the actual courier company directly", "Pay to get your package cleared right now",
          "Ask which courier service they represent now", "Pay only half now and half on delivery"],
         0, "Customs fees are paid at delivery or through official courier channels.",
         "Package bait, phone payment for clearance", "Customs fees go through official channels.", "all", 2),

        ("Fake Market Research Salary Call",
         "A 'market research firm' calls asking about your company's salary structure, number of employees, and annual revenue for a 'benchmark study.'\n\nWhat should you do?",
         ["Refuse to share confidential business data", "Share since benchmarking sounds legitimate",
          "Share general industry data, not specifics", "Ask them to send a formal request by email"],
         0, "Market research calls can be competitive intelligence operations.",
         "Professional pretexting, confidential data request", "Business data is confidential. Do not share.", "management", 3),

        ("Fake Software Refund Call",
         "A caller says your company overpaid for a software license. They will process a Rs. 30,000 refund if you provide bank and admin access.\n\nWhat should you do?",
         ["Hang up and check with your vendor directly", "Provide details to receive the refund now",
          "Give bank details but not admin access now", "Ask them to process the refund by cheque"],
         0, "Refund scams trick you into giving away access. Verify with the actual vendor.",
         "Refund bait, admin access request", "Refunds never require admin access to systems.", "it", 3),

        ("Fake Board Member Caller",
         "Someone calls claiming to be a new board member. They ask about employee headcount, upcoming projects, and financial targets.\n\nWhat should you do?",
         ["Ask them to contact through the CEO office", "Share info since board members need it all",
          "Share headcount but not financial targets", "Verify with the CEO if a new member joined"],
         0, "Board members communicate through official channels, not unsolicited calls.",
         "Authority impersonation, strategic data request", "Board members use official channels.", "management", 3),
    ]

    for t, c, o, ci, e, rf, tip, role, diff in items:
        _add(_make(t, c, o, ci, e, rf, tip, C, diff, role))

_extra_vishing()


def _extra_physical():
    C = "physical_security"
    items = [
        ("Unescorted Vendor Near Wiring",
         "A vendor you recognize is alone near the network wiring closet. They say they were told to check the cables.\n\nWhat should you do?",
         ["Stay with them until IT staff arrives", "Leave since you recognize the vendor person",
          "Ask them to wait outside until IT comes", "Help them find the right cables yourself"],
         0, "Even known vendors need an escort in sensitive areas.",
         "Known vendor, unsupervised sensitive area", "Known does not mean unsupervised. Stay present.", "all", 2),

        ("Dumpster with Unshredded Papers",
         "You see the dumpster outside the office full of unshredded documents, including contracts and employee records.\n\nWhat should you do?",
         ["Report to office manager for shredding now", "Leave it since cleaning staff handles trash",
          "Take the documents and shred them yourself", "Pull out only the documents with your name"],
         0, "Unshredded company documents are a goldmine for dumpster divers.",
         "Unshredded documents, public dumpster", "All company documents must be shredded.", "all", 2),

        ("Visitor Photographing Reception",
         "A visitor at reception is taking photos of the visitor logbook while waiting. The logbook has names and company details.\n\nWhat should you do?",
         ["Ask them to stop and close the logbook now", "Let them take photos since it is public",
          "Move the logbook away without saying anything", "Ask them to delete the photos they took"],
         0, "Visitor logbooks contain personal data. Photography should not be allowed.",
         "Data capture attempt, visitor logbook exposure", "Logbooks are not for photography.", "receptionist", 2),

        ("Badge Cloning Tool Spotted",
         "You notice a visitor holding a small device near your coworker's badge while talking to them. It looks like a card reader.\n\nWhat should you do?",
         ["Alert security about the device right away", "Ignore it since it might be a phone case",
          "Ask the visitor what the device is for now", "Take a photo of the device for evidence"],
         0, "RFID badge cloners look like small card readers. Alert security immediately.",
         "Suspicious device near badge, cloning risk", "Small devices near badges = alert security.", "all", 3),

        ("Cleaning Staff After Hours Alone",
         "You work late and notice the cleaning staff propped open the CEO's office with all files and computer accessible while they clean other rooms.\n\nWhat should you do?",
         ["Close the CEO's door until they come back", "Leave it since cleaning staff has access",
          "Lock the door and take the key with you", "Tell the cleaning staff when they return"],
         0, "Executive offices contain sensitive data. They should never be left open unattended.",
         "Executive office exposed, unattended access", "Close sensitive offices when left open.", "all", 2),

        ("Shoulder Surfing at ATM Area",
         "In the office building lobby ATM, you notice someone standing too close behind you, looking at the screen.\n\nWhat should you do?",
         ["Cover the keypad and ask them to step back", "Enter your PIN quickly so they cannot see",
          "Cancel the transaction and come back later", "Ask a guard to watch while you use the ATM"],
         0, "Shoulder surfing captures PINs and account details. Always shield the keypad.",
         "Close proximity, visible screen and keypad", "Shield your PIN. Ask people to step back.", "all", 1),

        ("Sensitive Meeting Room Not Cleared",
         "After a client meeting, you see whiteboards covered in strategy notes and printed handouts left on the table in the room.\n\nWhat should you do?",
         ["Erase the whiteboard and collect handouts", "Leave it for the next team to deal with",
          "Take photos of the board for your records", "Close the door but leave everything inside"],
         0, "The next group using the room could be external visitors. Clear everything.",
         "Strategy data visible, shared room", "Clear everything after sensitive meetings.", "all", 1),

        ("Security Camera Blind Spot",
         "You discover that the back entrance has no security camera coverage. You mentioned this to your boss months ago and nothing was done.\n\nWhat should you do?",
         ["Raise it again formally in writing to boss", "Accept it since you already mentioned it",
          "Install a personal camera to monitor it", "Post a warning sign at the back entrance"],
         0, "Security gaps need persistent follow-up. Escalate in writing.",
         "Known security gap, no action taken", "Security issues need written escalation.", "all", 2),

        ("Server Room Temp Too High",
         "You enter the server room and notice it feels unusually hot. The AC unit seems to have stopped working.\n\nWhat should you do?",
         ["Alert IT and facilities management right now", "Open the server room door to cool it down",
          "Turn off some servers to reduce the heat", "Ignore it since someone will notice it soon"],
         0, "High server room temperatures cause hardware failure. Report immediately.",
         "Server room overheating, AC failure risk", "Report immediately. Overheating damages servers.", "it", 1),

        ("Visitor Badge Left Behind",
         "At the end of the day, you find a visitor badge left on a desk. It has not been returned to reception.\n\nWhat should you do?",
         ["Return it to reception and log the return", "Throw it away since the visitor has left",
          "Keep it at your desk for them to collect", "Put it in the lost and found box today"],
         0, "Unreturned visitor badges are a security risk. They could be reused.",
         "Unreturned badge, potential reuse risk", "All badges must be returned to reception.", "all", 1),

        ("Piggyback Into Parking Gate",
         "A car follows closely behind yours through the parking garage gate without scanning their own access card.\n\nWhat should you do?",
         ["Report the car details to building security", "Let it go since they probably work here",
          "Block the gate until they scan their card", "Flash your lights to get their attention"],
         0, "Parking gates control vehicle access. Piggybacking bypasses security.",
         "Vehicle tailgating, no badge scan", "Report vehicles that bypass parking gates.", "all", 2),

        ("Unknown Laptop on Company WiFi",
         "IT alerts you that an unknown laptop connected to the company WiFi. It appeared during visitor hours today.\n\nWhat should you do?",
         ["Help IT identify who brought the device", "Ignore it since visitors often use WiFi now",
          "Disconnect the device yourself from WiFi", "Send an email asking who owns the laptop"],
         0, "Unknown devices on company WiFi could be performing network reconnaissance.",
         "Unknown device, company network access", "Unknown devices on WiFi = investigate now.", "it", 3),

        ("Fire Exit Blocked by Boxes",
         "You notice the fire exit is blocked by boxes of office supplies. The boxes have been there for at least a week.\n\nWhat should you do?",
         ["Move the boxes and report to management", "Leave them since others must know about it",
          "Report to fire safety but do not move them", "Move them only if there is a fire emergency"],
         0, "Blocked fire exits are a life safety hazard. Move the boxes and report.",
         "Fire exit blocked, safety violation", "Fire exits must be clear at all times.", "all", 1),

        ("Broken Access Card Reader",
         "The card reader at the main entrance has been broken for two days. The door is propped open for staff to enter.\n\nWhat should you do?",
         ["Report it and ask for a temporary guard", "Accept it since it will be fixed eventually",
          "Prop it open more securely with a chair", "Lock the door and give keys to reception"],
         0, "A broken card reader with an open door eliminates access control entirely.",
         "Broken access control, open door risk", "Broken card readers need temporary security.", "all", 2),

        ("Suspicious Package at Reception",
         "A package with no return address or label is left at reception. Nobody knows who dropped it off or who it is for.\n\nWhat should you do?",
         ["Do not touch it and call building security", "Open it to see what is inside the package",
          "Move it outside and open it in the parking", "Ask coworkers if anyone expects a delivery"],
         0, "Unidentified packages without labels should be reported to security immediately.",
         "No return address, unknown origin", "Unidentified packages = call security.", "receptionist", 2),

        ("Former Employee Still Has Badge",
         "You see a former employee who left the company last month enter the building using their old badge. They walk towards their old desk.\n\nWhat should you do?",
         ["Alert security or HR about the access now", "Let them in since they used to work here",
          "Ask them what they are doing back in office", "Tell them to return the badge at reception"],
         0, "Former employees should not have active building access. Report immediately.",
         "Former employee, active badge not deactivated", "Badges must be deactivated on termination.", "all", 3),

        ("Open WiFi Network In Building",
         "You notice a new open WiFi network called 'Company_Guest_Free' in your building. Your IT team did not set up any new network.\n\nWhat should you do?",
         ["Report the unknown network to IT right now", "Connect since it says guest and is free",
          "Test it on your phone before using at work", "Ask coworkers if they set up a hotspot"],
         0, "Rogue WiFi networks are used for man-in-the-middle attacks. Report to IT.",
         "Unknown network, potential evil twin", "Unknown WiFi networks = report to IT.", "all", 3),

        ("Tailgater With Legitimate Story",
         "A person at the entrance says they are a courier from Foodmandu delivering lunch orders. They cannot reach the person who ordered.\n\nWhat should you do?",
         ["Take delivery at reception, do not let in", "Let them in to find the person who ordered",
          "Call the person who ordered to come collect", "Ask them to wait while you find the person"],
         0, "Deliveries happen at reception. Couriers should never go inside the office.",
         "Legitimate reason, still should not enter", "Deliveries happen at reception only.", "receptionist", 1),

        ("Sensitive Printout Left in Printer Tray",
         "You go to collect your printout and find someone else's document with employee performance reviews and salary details in the tray.\n\nWhat should you do?",
         ["Put it face-down and notify HR immediately", "Read it since it is already on the printer",
          "Leave it in the tray for the owner to get", "Throw it in the recycling bin right away"],
         0, "Performance reviews are confidential. Secure them and notify HR.",
         "Confidential data in shared space", "Confidential printouts go to HR. Face-down.", "all", 1),

        ("CCTV System Password Shared",
         "The building security guard shares the CCTV login password with you so you can check footage of a recent incident.\n\nWhat should you do?",
         ["Ask security to show you the footage only", "Accept the password and review the footage",
          "Write down the password for future use now", "Share the password with your IT team too"],
         0, "CCTV access should be controlled by security. Do not accept shared passwords.",
         "Shared CCTV credentials, access control bypass", "CCTV access stays with security only.", "all", 3),
    ]

    for t, c, o, ci, e, rf, tip, role, diff in items:
        _add(_make(t, c, o, ci, e, rf, tip, C, diff, role))

_extra_physical()


def _extra_password():
    C = "password_hygiene"
    items = [
        ("Writing Password in Phone Notes",
         "You save your work email password in the Notes app on your personal phone. Your phone has no screen lock set up.\n\nWhat should you do?",
         ["Use a password manager and set a lock", "Keep it since the phone is always with you",
          "Set a screen lock but keep notes as is", "Delete the note and memorize the password"],
         0, "An unlocked phone with passwords is like leaving your house keys on the doorstep.",
         "No screen lock, plain text password storage", "Use a password manager. Set a screen lock.", "all", 1),

        ("Sharing WiFi Password Verbally",
         "A delivery driver asks for the office WiFi password while waiting. You tell them the staff WiFi password out loud.\n\nWhat should you do?",
         ["Offer the guest WiFi password next time", "It is fine since they will leave shortly",
          "Change the staff WiFi password right after", "Ask them to use their own mobile data now"],
         0, "Staff WiFi provides internal network access. Always offer guest WiFi instead.",
         "Staff WiFi shared verbally, network exposure", "Guests get guest WiFi. Staff WiFi is internal.", "all", 1),

        ("Password Complexity Complaint",
         "Your company requires passwords with 12+ characters, numbers, symbols, and uppercase. You complain it is too complicated to remember.\n\nWhat should you do?",
         ["Use a passphrase like 'TigerClimbs@Mount8848'", "Use 'Password123!' since it meets rules",
          "Write it on paper and keep in your wallet", "Ask IT to make the policy less strict now"],
         0, "Passphrases are long but memorable. Combine random words with numbers and symbols.",
         "Complexity frustration, need memorable solution", "Passphrases are long AND memorable.", "all", 1),

        ("Manager Asks for Shared Login",
         "Your manager asks the team to share one login account for a project tool because buying extra licenses is too expensive.\n\nWhat should you do?",
         ["Suggest individual accounts for audit trail", "Share the login since the manager approved",
          "Share but change the password every month", "Use the shared login but log activities"],
         0, "Shared logins prevent accountability. Each person needs their own account.",
         "Manager request, shared credentials", "Individual accounts enable accountability.", "all", 2),

        ("Password in Browser Warning",
         "Your browser shows a warning that one of your saved passwords appeared in a data breach. You use this password for three sites.\n\nWhat should you do?",
         ["Change the password on all three sites now", "Change only the breached site password now",
          "Ignore it since you have not been hacked yet", "Add a symbol to the existing password today"],
         0, "Breached passwords are sold on the dark web. Change all sites that use it.",
         "Data breach notification, password reuse risk", "Breached password = change everywhere.", "all", 2),

        ("Temporary Password Never Changed",
         "IT gave you a temporary password 6 months ago and you never changed it. 'Temp@1234' still works and you remember it.\n\nWhat should you do?",
         ["Change it to a strong unique password now", "Keep it since it has worked fine for months",
          "Add your name to the temp password for now", "Ask IT to reset it to a new temp password"],
         0, "Temporary passwords are meant to be changed immediately. 6 months is too long.",
         "Temporary password never changed, known pattern", "Temp passwords must be changed immediately.", "all", 1),

        ("Coworker Knows Your Password",
         "You realize a coworker saw you type your password last week. They have not done anything suspicious but they know it now.\n\nWhat should you do?",
         ["Change your password immediately right now", "Keep it since they are a trusted coworker",
          "Ask them if they actually saw your password", "Change it but tell them the new one too"],
         0, "If anyone sees your password, change it. Trust does not eliminate risk.",
         "Password observed by another person", "Seen password = change immediately.", "all", 1),

        ("Multiple Failed Login Attempts",
         "You get a notification that there were 5 failed login attempts on your account overnight. You were sleeping.\n\nWhat should you do?",
         ["Change your password and enable 2FA today", "Ignore it since your account was not hacked",
          "Wait to see if more attempts happen tonight", "Disable the notification since it is annoying"],
         0, "Failed login attempts mean someone is trying to access your account.",
         "Brute force indicator, overnight attempts", "Failed logins = change password and enable 2FA.", "all", 2),

        ("Password Reset Link From Unknown",
         "You receive a password reset email for your work account that you did not request. It looks like it came from your company's system.\n\nWhat should you do?",
         ["Do not click it and report it to IT now", "Click to reset since someone might be trying",
          "Ignore it since you did not request a reset", "Forward the reset email to your manager"],
         0, "Unrequested password reset links may be phishing or indicate someone targeting your account.",
         "Unrequested reset, possible attack indicator", "Unrequested reset = report to IT.", "all", 2),

        ("Password Autofill on Shared Tablet",
         "The office tablet used by multiple staff has autofill enabled. Everyone's passwords are saved in the browser.\n\nWhat should you do?",
         ["Ask IT to disable autofill on the tablet", "Leave it since everyone knows each other",
          "Delete only your password from the browser", "Add a master password to the browser now"],
         0, "Shared devices with autofill give everyone access to all saved accounts.",
         "Shared device, multiple saved passwords", "Shared devices = no saved passwords.", "all", 2),

        ("PIN Same As Phone Number",
         "Your ATM PIN is the last 4 digits of your phone number. Your phone number is listed on your business card and LinkedIn.\n\nWhat should you do?",
         ["Change your PIN to something not public", "Keep it since nobody would connect the two",
          "Remove your phone number from LinkedIn now", "Change only the LinkedIn number, not the PIN"],
         0, "If your PIN can be derived from public information, it is not secure.",
         "PIN from public data, business card exposure", "PINs must not come from public information.", "all", 2),

        ("Excel Spreadsheet of Passwords",
         "Your team maintains a shared Excel spreadsheet with all project tool passwords. It has no password protection on the file.\n\nWhat should you do?",
         ["Migrate all passwords to a password manager", "Password-protect the Excel file right now",
          "Move the file to a more secure shared drive", "Delete the file and memorize all passwords"],
         0, "Excel files with passwords are easily copied and shared. Use a password manager.",
         "Unprotected password file, shared access", "Password managers replace spreadsheets.", "all", 3),

        ("Default Admin Password on Camera",
         "The new security camera system in your office still uses the default admin login 'admin/admin123' after 3 months.\n\nWhat should you do?",
         ["Change the default password to a strong one", "Leave it since only security accesses it",
          "Add a firewall rule to block external access", "Write down the default in case you forget"],
         0, "Default passwords on any device are the first thing attackers try. Change immediately.",
         "Default credentials, IoT device exposure", "Change defaults on ALL devices. Priority one.", "it", 2),

        ("Using Birthday As Security Answer",
         "Your security question answer is your mother's birthday, which is posted on your Facebook page every year.\n\nWhat should you do?",
         ["Use a random fake answer and save it securely", "Keep it since nobody would check your Facebook",
          "Change it to your father's birthday instead", "Delete your mother's birthday from Facebook"],
         0, "Security answers from social media are easy to find. Use random answers.",
         "Security answer from public social media", "Security answers should be random, not real.", "all", 2),

        ("Credential Stuffing Attack Ongoing",
         "IT alerts that many employees are being hit by credential stuffing attacks using passwords leaked from a social media site breach.\n\nWhat should you do?",
         ["Change passwords on all work and personal sites", "Change only work passwords immediately now",
          "Wait to see if your specific account is hit", "Disable your social media accounts right now"],
         0, "Credential stuffing uses leaked passwords. If you reused them, all accounts are at risk.",
         "Breach notification, password reuse exposure", "Leaked passwords = change everywhere now.", "all", 3),

        ("Hardware Token Lost",
         "You lost the physical 2FA security token assigned to you. You can still log in using a backup code you saved.\n\nWhat should you do?",
         ["Report the loss to IT immediately today", "Use backup codes until you find the token",
          "Ask a coworker to lend their token for now", "Order a replacement online from the vendor"],
         0, "Lost tokens could be used by anyone who finds them. Report immediately.",
         "Lost authentication device, security risk", "Lost tokens must be reported immediately.", "all", 2),

        ("Password Manager Master Password",
         "You set up a password manager. For the master password, you use 'master123' because you are afraid of forgetting it.\n\nWhat should you do?",
         ["Create a strong passphrase as the master key", "Keep 'master123' since you will remember it",
          "Write the master password on a sticky note", "Use your email password as the master too"],
         0, "The master password protects ALL your other passwords. It must be the strongest one.",
         "Weak master password, single point of failure", "Master password = strongest password you have.", "all", 2),

        ("Shared Service Account No Rotation",
         "Your team has a shared service account password that has not been changed in 2 years. Three people who knew it have since left the company.\n\nWhat should you do?",
         ["Change the password immediately right now", "Keep it since it still works without issues",
          "Add the ex-employees to a watch list first", "Change it only after the current project ends"],
         0, "Former employees with active credentials are a major security risk.",
         "No rotation, former employee access risk", "Rotate passwords when people leave. Always.", "all", 3),
    ]

    for t, c, o, ci, e, rf, tip, role, diff in items:
        _add(_make(t, c, o, ci, e, rf, tip, C, diff, role))

_extra_password()


def _extra_usb():
    C = "usb_baiting"
    items = [
        ("USB In Meeting Room",
         "After a client meeting, you find a USB drive on the meeting room table. The client did not mention leaving any USB behind.\n\nWhat should you do?",
         ["Give it to IT. do not plug it in first", "Plug it in to find the client's name",
          "Put it in your desk and email the client", "Mail it back to the client's company now"],
         0, "The USB may not belong to the client. Let IT check it safely.",
         "Unknown ownership, client meeting context", "Unknown USB = IT handles it. Always.", "all", 1),

        ("USB Gift at Networking Event",
         "At a networking dinner, a stranger hands you a USB with 'Exclusive Market Research' on it. 'This will change your business.'\n\nWhat should you do?",
         ["Politely decline or give it to IT later", "Plug it in since the research sounds useful",
          "Accept it and scan with antivirus at work", "Use it at home on your personal computer"],
         0, "Free USB drives from strangers are a classic attack vector.",
         "Stranger, tempting label, networking context", "USBs from strangers = never plug in.", "sales", 2),

        ("USB From Conference Speaker",
         "A conference speaker offers USB drives with their presentation slides. Everyone in the audience takes one.\n\nWhat should you do?",
         ["Ask them to email the slides to you instead", "Take one since the speaker seems legitimate",
          "Take one and scan it before opening files", "Take one and open it on your phone only"],
         0, "Even conference speakers can unknowingly distribute infected USB drives.",
         "Mass distribution, speaker authority trust", "Ask for email slides. Avoid USB drives.", "all", 2),

        ("USB With Company Logo Found",
         "You find a USB drive with your company logo on it in the office bathroom. It could belong to anyone.\n\nWhat should you do?",
         ["Give it to IT without plugging it in", "Plug it in since it has your company logo",
          "Ask around the office if anyone lost a USB", "Put it in the lost and found box at desk"],
         0, "Attackers can print any logo on a USB drive. Logo does not mean it is safe.",
         "Company logo as trust signal, found device", "Logos can be faked. Give all found USBs to IT.", "all", 2),

        ("Encrypted USB Drive Found",
         "You find an encrypted USB drive with a password hint sticker on it. The hint says 'company name backwards.'\n\nWhat should you do?",
         ["Give it to IT. do not try to open it", "Try the password since it is easy to guess",
          "Plug it in but do not enter the password", "Peel off the sticker and throw the USB away"],
         0, "The password hint makes it MORE suspicious. This is designed to be opened.",
         "Password hint to encourage opening, bait", "Password hints on USBs = deliberate bait.", "all", 3),

        ("USB Keyboard Logger Device",
         "You notice a small USB device plugged between your keyboard cable and the computer that was not there yesterday.\n\nWhat should you do?",
         ["Do not touch it and alert IT security now", "Unplug it and throw it in the dustbin",
          "Plug it into a different USB port to check", "Ask your coworker if they plugged it in"],
         0, "Hardware keyloggers capture every keystroke. Do not touch it. alert IT.",
         "Unknown hardware between keyboard and PC", "Unknown USB hardware = alert IT immediately.", "all", 3),

        ("USB Cable Left on Desk",
         "You find a USB charging cable on your desk that does not belong to you. Nobody claims ownership when you ask around.\n\nWhat should you do?",
         ["Throw it away and use your own cable only", "Use it since it is just a charging cable",
          "Test it by plugging into a spare computer", "Keep it as a spare cable in your drawer"],
         0, "Modified USB cables can contain hidden chips that steal data or inject malware.",
         "Unknown cable, potential OMG cable attack", "Unknown cables can contain hidden chips.", "all", 2),

        ("USB From Vendor Sales Demo",
         "A vendor leaves a USB with product demo files after a sales presentation. They say it includes pricing and proposals.\n\nWhat should you do?",
         ["Ask the vendor to email the files instead", "Plug it in to review the demo pricing now",
          "Give it to IT to scan before reviewing it", "Open only PDF files from the USB to be safe"],
         0, "Even business USBs from vendors can carry malware unknowingly.",
         "Business context, vendor relationship trust", "Ask vendors to email documents. Not USB.", "all", 2),

        ("USB Found Near Parking Security",
         "A USB drive is found near the parking security booth. The label says 'Security Camera Footage - Do Not Delete.'\n\nWhat should you do?",
         ["Give it to IT. do not open the footage", "Plug it in to check the security footage",
          "Give it to the security guard to review", "Leave it where you found it for the owner"],
         0, "Tempting labels like 'Security Camera Footage' are designed to make you plug it in.",
         "Tempting label targeting curiosity", "Tempting label = more dangerous. Report to IT.", "all", 1),

        ("USB Mouse From Unknown Source",
         "A new wireless USB mouse appears on your desk. It looks identical to the ones your company uses, but you did not request one.\n\nWhat should you do?",
         ["Do not use it. report to IT right away", "Use it since it matches company equipment",
          "Try it for a day and return it if it is weird", "Keep it as a spare mouse in your drawer"],
         0, "Wireless mice can be replaced with modified ones that inject keystrokes.",
         "Matching company equipment, unknown source", "Unknown peripherals = report to IT.", "all", 3),

        ("USB At Hotel Business Center",
         "At a hotel business center, someone left a USB in the shared computer. You need to print documents for tomorrow's meeting.\n\nWhat should you do?",
         ["Do not touch it and use your own USB drive", "Check it to return it to the front desk",
          "Remove it and ask the front desk about it", "Use the computer but leave the USB alone"],
         0, "USBs in shared computers could be there to infect the next user's files.",
         "Shared computer, unknown USB, business travel", "Never touch unknown USBs in shared PCs.", "all", 2),

        ("SD Card in Company Camera",
         "The company event camera has an SD card you do not recognize. It was not there at the last event.\n\nWhat should you do?",
         ["Remove it and give it to IT for checking", "Use it to take photos at the next event",
          "Format it and use it as an extra backup card", "Leave it since someone must have put it in"],
         0, "Unknown SD cards in devices should be treated like unknown USB drives.",
         "Unknown media in company device", "Unknown storage media = IT checks it first.", "all", 2),
    ]

    for t, c, o, ci, e, rf, tip, role, diff in items:
        _add(_make(t, c, o, ci, e, rf, tip, C, diff, role))

_extra_usb()


def _extra_social():
    C = "social_engineering"
    items = [
        ("Fake Employee Survey Link",
         "An anonymous 'employee satisfaction survey' link is shared in the office WhatsApp group. It asks for your employee ID and password.\n\nWhat should you do?",
         ["Report it. surveys never ask for passwords", "Complete it since everyone is doing it now",
          "Fill it with a fake password to be safe", "Ask your manager if the survey is real"],
         0, "Legitimate surveys never ask for passwords. This is credential harvesting.",
         "Password request in survey, group trust", "Surveys never need your password.", "all", 1),

        ("Fake IT Email About New Tool",
         "An email says IT is rolling out a new tool. Click a link to create your account with your current work email and password.\n\nWhat should you do?",
         ["Verify with IT before creating any account", "Create the account since IT sent the email",
          "Create it but use a different password now", "Ask a coworker if they also got the email"],
         0, "IT roll-outs are communicated through official channels. Verify before acting.",
         "IT impersonation, credential harvesting", "New tools are announced officially by IT.", "all", 2),

        ("Vendor Asking About Network Setup",
         "A vendor casually asks about your network setup, firewall brand, and VPN solution during a lunch meeting.\n\nWhat should you do?",
         ["Politely decline to discuss technical setup", "Share since vendors often need this for integration",
          "Share the firewall brand but not VPN details", "Tell them to coordinate with your IT team"],
         0, "Technical infrastructure details help attackers plan attacks.",
         "Casual setting, technical reconnaissance", "Technical details = IT discusses, not you.", "it", 2),

        ("Fake Emergency Drill Announcement",
         "Someone you do not recognize announces an emergency drill and asks everyone to leave their computers unlocked. Your company's safety officer did not mention any drill.\n\nWhat should you do?",
         ["Lock your computer and verify with safety team", "Leave computer unlocked as told in the drill",
          "Ask the person for their ID before following", "Leave but lock your computer screen first"],
         0, "Fake drills are used to access unlocked computers. Always lock before leaving.",
         "Unverified drill, computers left unlocked", "Lock your computer. Always. Before leaving.", "all", 2),

        ("Overheard Conversation Exploitation",
         "At a restaurant, you discuss a major contract worth Rs. 2 crore with your colleague. The next day, a 'business consultant' calls offering to help win it.\n\nWhat should you do?",
         ["Refuse and investigate how they got the info", "Accept since they could actually help you win",
          "Ask them where they learned about the deal", "Meet them in person to discuss the details"],
         0, "Your restaurant conversation was overheard. Confidential talks need private spaces.",
         "Leaked info from public conversation", "Business talks happen in private spaces only.", "sales", 3),

        ("Impersonating New Employee",
         "Someone calls claiming they started today. They need your help setting up email by sharing the IT admin's phone number and your department's shared drive link.\n\nWhat should you do?",
         ["Tell them to visit IT in person for setup", "Help them since starting a new job is hard",
          "Give the IT number but not the drive link", "Ask them to check with their manager first"],
         0, "New employee setup is handled by IT and HR. Do not share internal resources by phone.",
         "New employee pretexting, resource requests", "New employees get help from IT in person.", "all", 2),

        ("CEO's Personal Assistant Caller",
         "Someone calls claiming to be the CEO's new personal assistant. They need the office security code to prepare for the CEO's early morning visit.\n\nWhat should you do?",
         ["Call the CEO's office to verify this person", "Give the code since the CEO needs access",
          "Give the code but change it the next day", "Ask them to have the CEO call you directly"],
         0, "Security codes should never be shared by phone, especially to unverified callers.",
         "CEO's name as leverage, security code request", "Security codes are not shared by phone.", "receptionist", 3),

        ("Fake Compliance Officer Visit",
         "A person arrives claiming to be a compliance officer from a regulatory body. They want to review employee records, financial documents, and IT systems.\n\nWhat should you do?",
         ["Ask for official identification and verify", "Give access since compliance is important",
          "Show only general documents, not financials", "Ask them to schedule through your management"],
         0, "Real compliance officers schedule visits. They carry official identification.",
         "Authority impersonation, full access demand", "Compliance visits are scheduled in advance.", "management", 3),

        ("LinkedIn Recruiter Information",
         "A LinkedIn recruiter asks about your company's org structure, team sizes, key people, and which departments are growing.\n\nWhat should you do?",
         ["Share only what is on the public website", "Share openly since recruiters need this info",
          "Share team sizes but not key people names", "Redirect them to the HR department online"],
         0, "Recruiters can be competitors gathering intelligence. Share only public info.",
         "Recruiter cover, organizational intelligence", "Only share publicly available information.", "all", 2),

        ("Pretexting Via Shared Interest",
         "At a tech meetup, someone talks to you about your company's software stack. They gradually ask about security measures and vulnerabilities.\n\nWhat should you do?",
         ["Stop sharing details about company security", "Continue since tech meetups are about sharing",
          "Share general tech but not security specifics", "Exchange business cards and meet at office"],
         0, "Tech meetups are used for intelligence gathering. Never discuss security details.",
         "Social setting, gradual information extraction", "Security details are never shared socially.", "it", 3),

        ("Baiting With Infected Document",
         "A stranger at a conference says 'I have the latest industry report everyone wants.' They hand you a USB with the file.\n\nWhat should you do?",
         ["Ask them to email the report to you instead", "Take the USB since the report sounds useful",
          "Take it and scan with antivirus before opening", "Accept it but only open it at home later"],
         0, "Industry report bait combined with USB delivery is a classic attack.",
         "Social pressure, USB delivery, curiosity bait", "Ask for email delivery. Never accept USBs.", "all", 2),

        ("Fake IT Support Chat Bot",
         "A chat popup on a website says 'IT Support: Your session expired. Enter your work email and password to continue.'\n\nWhat should you do?",
         ["Close the popup and go to IT's real page", "Enter credentials to continue your session",
          "Enter email but not the password to check", "Reply in the chat asking if it is real IT"],
         0, "Fake IT chat popups harvest credentials. Real IT support has a dedicated portal.",
         "Popup credential request, IT impersonation", "IT has a portal. Popups are not from IT.", "all", 2),

        ("Elicitation During Business Trip",
         "During a business trip, a friendly stranger at the hotel bar asks detailed questions about your company's expansion plans and partnerships.\n\nWhat should you do?",
         ["Keep the conversation general and vague", "Share details since they are just being friendly",
          "Share publicly known plans but not the new ones", "Exchange contacts and discuss over email later"],
         0, "Elicitation at hotels during business trips is a known intelligence technique.",
         "Travel setting, friendly probing, business info", "Business details stay confidential. Even socially.", "management", 3),

        ("Phishing Via Dropped Business Card",
         "You find a business card on the floor with a handwritten note: 'Urgent: Call me about your account - Agent Smith, IRD.' A phone number is written on it.\n\nWhat should you do?",
         ["Ignore it. IRD does not leave business cards", "Call the number since IRD matters are urgent",
          "Google the name to check if they work at IRD", "Take the card to reception for the lost box"],
         0, "IRD agents do not leave handwritten notes on the floor. This is social engineering.",
         "Planted card, authority impersonation", "IRD uses official mail, not dropped notes.", "all", 2),

        ("Insider Threat: Disgruntled Employee",
         "A coworker who was recently passed over for promotion asks you to copy sensitive project files to their personal drive 'for backup.'\n\nWhat should you do?",
         ["Refuse and report the request to your boss", "Help them since they are your good coworker",
          "Copy only non-sensitive files to help them", "Ask them why they need personal backup now"],
         0, "Disgruntled employees requesting data is a classic insider threat indicator.",
         "Motivation change, unusual data request", "Unusual data requests = report to manager.", "all", 3),

        ("Fake Fire Alarm Social Engineering",
         "The fire alarm goes off. While evacuating, you see a person in firefighter gear heading straight to the finance area instead of checking for fire.\n\nWhat should you do?",
         ["Alert real emergency services about them", "Let them work since they are a firefighter",
          "Follow them to see what they are doing now", "Go back in and check on the finance area"],
         0, "Fake emergencies combined with uniforms are advanced social engineering.",
         "Uniform trust, distraction technique", "Fake emergencies = report unusual behavior.", "all", 3),
    ]

    for t, c, o, ci, e, rf, tip, role, diff in items:
        _add(_make(t, c, o, ci, e, rf, tip, C, diff, role))

_extra_social()


def _extra_data():
    C = "data_handling"
    items = [
        ("Laptop Screen Visible to Visitors",
         "Your desk faces the waiting area. Visitors can see your screen showing client records and financial data.\n\nWhat should you do?",
         ["Get a privacy screen filter for your monitor", "Turn the screen slightly away from visitors",
          "Minimize windows when visitors are waiting", "Move to a different desk facing the wall"],
         0, "Privacy screen filters prevent visual hacking from side angles.",
         "Visual data exposure, public-facing screen", "Privacy screen filters block side viewing.", "all", 1),

        ("Emailing Unencrypted Sensitive Data",
         "You need to email a spreadsheet with customer credit card numbers to a partner company. You plan to send it as a regular email attachment.\n\nWhat should you do?",
         ["Encrypt the file before sending by email", "Send it since the partner is a trusted company",
          "Password-protect the Excel file before sending", "Remove credit card numbers and send the rest"],
         0, "Credit card data must always be encrypted in transit. Regular email is not secure.",
         "Unencrypted sensitive data, email transit risk", "Encrypt sensitive data before emailing.", "finance", 2),

        ("Personal USB For Work Backup",
         "You backup important work files to your personal USB drive every Friday. The USB has no encryption and you carry it in your bag.\n\nWhat should you do?",
         ["Use company-approved cloud backup instead", "Continue since you have never lost the USB",
          "Encrypt the USB but keep your current backup", "Copy files to your personal laptop instead"],
         0, "Personal USBs without encryption are lost easily. Use company-approved backup.",
         "Unencrypted portable device, loss risk", "Use company backup solutions. Not personal USB.", "all", 2),

        ("Public WiFi for Work Email",
         "You check your work email at a coffee shop using the free public WiFi without VPN.\n\nWhat should you do?",
         ["Use VPN before accessing any work systems", "It is fine since the email is encrypted",
          "Use public WiFi but avoid downloading files", "Switch to your mobile data for email only"],
         0, "Public WiFi can be intercepted. Always use VPN for any work access.",
         "Public WiFi, no VPN, work email exposure", "Public WiFi + work = always use VPN.", "all", 1),

        ("Old Client Files Not Deleted",
         "A project with a client ended 2 years ago. Their files including contracts and personal data are still on your shared drive.\n\nWhat should you do?",
         ["Archive and delete per data retention policy", "Keep them in case the client comes back",
          "Move them to a personal folder for reference", "Delete only the personal data, keep contracts"],
         0, "Data retention policies exist for a reason. Old data creates legal liability.",
         "Expired retention, unnecessary data storage", "Follow retention policy. Delete old data.", "all", 2),

        ("Sending Data to Personal Cloud",
         "You upload work documents to your personal Google Drive to access them on your tablet at home for weekend work.\n\nWhat should you do?",
         ["Use company cloud or VPN for remote access", "Continue since Google Drive is very secure",
          "Use Google Drive but enable 2FA on it first", "Download files to your tablet directly now"],
         0, "Personal cloud services are outside company security controls.",
         "Personal cloud, company data, no IT oversight", "Company data stays on company cloud.", "all", 1),

        ("Disposing Old Phone With Work App",
         "You are selling your old phone. It still has the company email app, Slack, and some work files in the downloads folder.\n\nWhat should you do?",
         ["Factory reset and remove from all accounts", "Delete just the work apps before selling",
          "Log out of apps and sell it as it is today", "Sell it to a coworker who will not misuse it"],
         0, "Factory reset removes all data. Simply deleting apps leaves data recoverable.",
         "Device disposal, work data on personal device", "Factory reset before disposing any device.", "all", 2),

        ("Customer Data in Test Environment",
         "Your development team uses real customer data in the test environment for more accurate testing. There is no anonymization.\n\nWhat should you do?",
         ["Anonymize or use synthetic test data instead", "Continue since testing needs realistic data",
          "Restrict test environment access to senior devs", "Copy only 10% of customer data for testing"],
         0, "Real customer data in test environments violates privacy. Use anonymized data.",
         "Real data in non-production environment", "Test environments use synthetic data only.", "it", 3),

        ("Open API Keys In Code Repository",
         "You discover API keys for payment processing hard-coded in the source code repository that all developers can see.\n\nWhat should you do?",
         ["Remove keys and use environment variables", "Leave them since only developers see the code",
          "Add a comment saying 'do not share these keys'", "Move them to a config file in the same repo"],
         0, "Hard-coded API keys can be extracted from code. Use environment variables or vaults.",
         "Hard-coded secrets, repository exposure", "API keys go in env variables, not in code.", "it", 3),

        ("Screenshot of Dashboard Shared Online",
         "A coworker posts a screenshot of their analytics dashboard on Twitter. The dashboard shows real customer behavior data.\n\nWhat should you do?",
         ["Ask them to delete the post immediately", "Like the post since the dashboard looks great",
          "Report the post to your manager right away", "Ask them to blur the numbers and repost it"],
         0, "Customer data in any form should never be shared on social media.",
         "Customer data on public platform", "Customer data never goes on social media.", "all", 2),

        ("Printed Reports in Recycling Bin",
         "You see printed financial reports in the recycling bin near the printer. They show quarterly revenue and expense details.\n\nWhat should you do?",
         ["Take them out and shred them immediately", "Leave them since recycling is sorted offsite",
          "Put them in a different bin to be safe now", "Tear them into small pieces and then recycle"],
         0, "Recycling bins are not secure. Financial documents must be shredded.",
         "Financial data in recycling, not shredded", "Financial documents = shred. Never recycle.", "finance", 1),

        ("Sharing Screen During Video Call",
         "During a video call with an external client, you share your screen. Your email inbox, desktop files, and bookmarks are all visible.\n\nWhat should you do?",
         ["Share only the specific window or app needed", "Continue since the client will not read them",
          "Close email but keep desktop files visible", "Ask the client to look away while you switch"],
         0, "Screen sharing exposes everything visible. Only share the specific app window.",
         "Screen share, unintended data exposure", "Share specific windows, never full screen.", "all", 1),

        ("Data Breach Notification Delay",
         "Your company discovers a data breach on Monday. By Friday, customers have not been notified. Your manager says 'wait for legal advice.'\n\nWhat should you do?",
         ["Escalate to senior management urgently now", "Wait for legal advice as your manager says",
          "Notify customers yourself without approval", "Post about the breach on social media today"],
         0, "Data breach notifications have legal deadlines. Escalate to speed up the process.",
         "Notification delay, legal and ethical risk", "Breach notifications have legal deadlines.", "management", 3),

        ("Confidential Document on Shared PC",
         "You create a confidential report on the shared office computer but forget to log out. The next person can see your document.\n\nWhat should you do?",
         ["Go back and log out of the shared computer", "Call a coworker to close the file for you",
          "It is fine since coworkers are trustworthy", "Change the document password from your phone"],
         0, "Shared computers must be logged out after every session. Go back immediately.",
         "Shared PC, open confidential document", "Always log out of shared computers.", "all", 1),

        ("Employee Records In Plain Email",
         "HR emails a spreadsheet of all employee names, addresses, phone numbers, and salaries to the department heads in a regular email.\n\nWhat should you do?",
         ["Ask HR to use encrypted channels for this", "Accept it since department heads need this data",
          "Forward it to your team for their reference", "Save it on your personal drive for backup"],
         0, "Employee records are sensitive. Email is not secure for bulk personal data.",
         "Bulk personal data, unencrypted channel", "Sensitive HR data needs encrypted channels.", "hr", 2),

        ("Using Free Online PDF Converter",
         "You upload a confidential contract to a free online PDF conversion tool to convert it from Word format.\n\nWhat should you do?",
         ["Use offline software to convert the file", "Continue since the conversion is quick and easy",
          "Use the tool but delete the file after done", "Upload only the non-confidential pages today"],
         0, "Free online tools may store or index uploaded files. Use offline tools for confidential documents.",
         "Confidential file on third-party service", "Confidential files use offline tools only.", "all", 2),

        ("AI Chatbot With Company Data",
         "You paste customer names, phone numbers, and order details into a public AI chatbot to help you write a report faster.\n\nWhat should you do?",
         ["Remove personal data before using AI tools", "Continue since the AI does not store inputs",
          "Use the AI but do not paste phone numbers", "Ask IT for an approved AI tool for work use"],
         0, "Public AI tools may store or learn from your inputs. Never paste personal data.",
         "Personal data in public AI tool", "Never paste personal data into public AI.", "all", 2),

        ("USB Drive Left In Taxi",
         "You realize you left a USB drive with client proposals in the taxi you just took. The USB has no encryption.\n\nWhat should you do?",
         ["Report the data loss to IT and your manager", "Call the taxi company to try to get it back",
          "Do nothing since the proposals are not secret", "Create new proposals and forget about the USB"],
         0, "Lost unencrypted data = data breach. Report immediately regardless of content.",
         "Lost device, unencrypted data, reporting duty", "Lost data devices = report immediately.", "all", 2),
    ]

    for t, c, o, ci, e, rf, tip, role, diff in items:
        _add(_make(t, c, o, ci, e, rf, tip, C, diff, role))

_extra_data()


# ════════════════════════════════════════════════════════════════════════════
# 10. FINAL BATCH. fill remaining to ~500
# ════════════════════════════════════════════════════════════════════════════

def _final_batch():
    batch = [
        # --- PHISHING ---
        ("Fake Facebook Login Alert", "An email says someone logged into your Facebook from a new device. Click a link to secure your account. The link URL looks suspicious.\n\nWhat should you do?",
         ["Open Facebook directly to check security", "Click the link to secure your account now", "Reply asking which device logged in today", "Forward the email to Facebook support"], 0, "Facebook sends alerts in the app. Email links may be fake.", "Suspicious URL, account fear bait", "Check account security from the app.", "phishing_email", 1, "all"),

        ("Fake Viber Update Email", "An email says Viber has a mandatory security update. Download it from a link. The Play Store has no such update.\n\nWhat should you do?",
         ["Update apps only from the Play Store", "Click the link to get the latest update", "Forward the email to Viber support now", "Ask friends if they got the same email"], 0, "App updates only come through official stores.", "App update outside official store", "Updates come from app stores only.", "phishing_email", 1, "all"),

        ("Fake PayPal Receipt Email", "An email shows a PayPal receipt for Rs. 25,000 you did not make. Click 'Dispute' to cancel. You do not have a PayPal account.\n\nWhat should you do?",
         ["Delete it. you have no PayPal account", "Click 'Dispute' to cancel the charge now", "Reply saying you did not make this purchase", "Forward it to your bank to investigate"], 0, "No PayPal account means no real receipt. This is phishing.", "Service you do not use, fear trigger", "No account = no transaction. Delete it.", "phishing_email", 1, "all"),

        ("CEO Travel Fund Request", "Your CEO emails asking for Rs. 3,00,000 to be transferred for an urgent overseas trip. They say 'Handle this quietly.'\n\nWhat should you do?",
         ["Call the CEO to verify the request first", "Transfer the funds since the CEO asked you", "Transfer half and confirm the rest by email", "Ask a coworker for their opinion on this"], 0, "'Handle quietly' prevents verification. Always call.", "'Handle quietly', large amount, urgency", "Quiet requests for money = verify by phone.", "phishing_email", 3, "finance"),

        ("Fake SSL Certificate Email", "An email says your website SSL certificate expired. Click to renew or customers will see warnings. IT manages all certificates.\n\nWhat should you do?",
         ["Forward it to IT to handle the renewal", "Click to renew before customers see errors", "Reply asking for the certificate details now", "Check the website yourself to see warnings"], 0, "IT manages SSL certificates. Do not renew via email links.", "IT impersonation, SSL urgency", "IT handles certificates. Not your job.", "phishing_email", 2, "it"),

        # --- SMISHING ---
        ("Fake Blood Donation SMS", "An SMS says there is an urgent blood shortage at a hospital. Click a link to register as a donor with your personal details.\n\nWhat should you do?",
         ["Contact the hospital directly to volunteer", "Click the link to register as a blood donor", "Reply with your blood type to help quickly", "Share the link on social media to help more"], 0, "Hospitals do not collect donor info via SMS links.", "Emotional manipulation, hospital impersonation", "Contact hospitals directly to donate blood.", "smishing", 1, "all"),

        ("Fake OTP From Unknown Service", "You receive an OTP code from a service you never signed up for. Seconds later, someone calls asking for the code.\n\nWhat should you do?",
         ["Never share the code with any caller now", "Read the code since they seem to know you", "Read only the first three digits to be safe", "Ask them which service sent the OTP code"], 0, "OTPs sent to your number are for your protection. Never share them.", "Unknown service OTP, immediate phone call", "Any OTP on your phone = your protection.", "smishing", 2, "all"),

        ("Fake Airline Ticket SMS", "An SMS says your flight to Dubai is confirmed. Click to view e-ticket. You did not book any flight.\n\nWhat should you do?",
         ["Delete it. you did not book any flight", "Click to check if someone booked for you", "Reply asking which airline and flight number", "Call the airline to verify the booking now"], 0, "No booking = no real confirmation. This steals your data.", "No booking made, curiosity bait", "No booking = no real ticket. Delete.", "smishing", 1, "all"),

        ("Fake Loan Approval SMS", "An SMS says your loan of Rs. 5,00,000 was approved. Click to accept the terms. You never applied for any loan.\n\nWhat should you do?",
         ["Delete it. you never applied for a loan", "Click to see the loan terms and interest", "Reply asking which bank approved the loan", "Call the number to reject the loan quickly"], 0, "No application = no real approval. This is advance fee fraud.", "No application, loan approval bait", "No application = no approval. Ever.", "smishing", 1, "all"),

        ("Fake Traffic Fine SMS", "An SMS says you have an unpaid traffic fine of Rs. 3,000. Click to pay or your license will be suspended. You have not driven recently.\n\nWhat should you do?",
         ["Ignore it. check with traffic police office", "Click the link to pay the fine right away", "Reply asking for the violation date and place", "Call the number in the SMS to discuss it"], 0, "Traffic police send fines through their office, not SMS payment links.", "Government impersonation, license suspension", "Traffic fines come from the traffic office.", "smishing", 1, "all"),

        # --- VISHING ---
        ("Fake Microsoft License Call", "A caller says your company's Microsoft 365 license is about to expire. They need your credit card to renew it before everyone loses access.\n\nWhat should you do?",
         ["Hang up and check with IT about licenses", "Give card details to keep access running now", "Ask them to send a renewal invoice by email", "Give only the card number but not the CVV"], 0, "Microsoft does not call for license renewals. IT handles subscriptions.", "Microsoft impersonation, payment urgency", "IT manages all software licenses.", "vishing", 2, "it"),

        ("Fake Delivery Confirmation Call", "A caller says they have a COD delivery for you. Confirm your full name and address to deliver. You did not order anything.\n\nWhat should you do?",
         ["Refuse. you did not order anything today", "Confirm your details to receive the delivery", "Give only your name but not your full address", "Ask them which company sent the package now"], 0, "No order = no legitimate delivery call. Do not confirm personal details.", "No order placed, personal info request", "No order = no delivery. Refuse details.", "vishing", 1, "all"),

        ("Fake Investment Advisor Call", "A caller claims to be a licensed investment advisor. They guarantee 50% returns if you invest Rs. 1,00,000 in their fund today.\n\nWhat should you do?",
         ["Hang up. guaranteed returns are impossible", "Invest since they sound very knowledgeable", "Invest a smaller amount to test them first", "Ask for their SEBON registration number now"], 0, "No investment can guarantee returns. Licensed advisors do not cold-call.", "Guaranteed returns, cold call, pressure", "Guaranteed returns = guaranteed scam.", "vishing", 2, "all"),

        ("Fake Hospital Emergency Call", "A caller says your coworker had an accident and is in the hospital. They need Rs. 50,000 for emergency surgery. Your coworker's phone is off.\n\nWhat should you do?",
         ["Call other coworkers to verify the story", "Transfer money since it is an emergency now", "Go to the hospital in person to check first", "Ask the caller which hospital and room number"], 0, "Emergency calls that demand money are scams. Verify through other channels.", "Emergency panic, money demand, phone off", "Verify emergencies through other contacts.", "vishing", 3, "all"),

        ("Fake Government Grant Call", "A caller says your company qualifies for a government business grant. Pay Rs. 20,000 processing fee to receive Rs. 5,00,000.\n\nWhat should you do?",
         ["Hang up. real grants have no upfront fees", "Pay the fee to get the larger grant amount", "Ask them to send official grant papers by post", "Pay half now and half after receiving the grant"], 0, "Government grants never require upfront fees. This is advance fee fraud.", "Upfront fee for grant, government impersonation", "Grants never charge processing fees.", "vishing", 2, "management"),

        # --- PHYSICAL ---
        ("Unattended Laptop in Meeting Room", "A coworker's laptop is open and logged in in the meeting room. They are in another meeting and will not return for an hour.\n\nWhat should you do?",
         ["Lock the screen and tell them you did so", "Leave it since the meeting room is internal", "Close the lid to put the laptop to sleep now", "Use it to check if they finished the report"], 0, "Unlocked laptops in shared spaces risk unauthorized access.", "Unlocked device, shared meeting room", "Lock unattended laptops. Tell the owner.", "physical_security", 1, "all"),

        ("Window Left Open Overnight", "You are the last to leave and notice a ground-floor window is open. It faces a public sidewalk.\n\nWhat should you do?",
         ["Close the window and check all others too", "Leave it since the building has an alarm now", "Close it but leave it unlocked for fresh air", "Report it to security but do not close it"], 0, "Open ground-floor windows are easy entry points. Close them before leaving.", "Open window, ground floor, public access", "Close all windows before leaving.", "physical_security", 1, "all"),

        ("Shared Desk Clean Policy", "Your company has a clean desk policy but many people leave documents, sticky notes, and USBs on their desks overnight.\n\nWhat should you do?",
         ["Follow the policy and remind your team too", "Ignore it since nobody enforces the policy", "Follow it but do not remind other team members", "Ask management to remove the policy instead"], 0, "Clean desk policies prevent overnight data exposure. Follow and encourage others.", "Policy non-compliance, data exposure risk", "Clean desk policies exist for a reason.", "physical_security", 1, "all"),

        ("Visitor In IT Area Alone", "You see a visitor walking alone through the IT area. They are looking at screens and taking mental notes.\n\nWhat should you do?",
         ["Approach them and escort to reception now", "Ignore them since someone must know them here", "Follow them quietly to see what they are doing", "Send an email to IT asking about the visitor"], 0, "Unescorted visitors in IT areas can observe sensitive information.", "Unescorted visitor, IT area, observing screens", "Visitors need escorts. Especially in IT.", "physical_security", 2, "all"),

        ("Smoke Break Door Propped Open", "Staff prop the side door open during smoke breaks. The door bypasses the main entrance and its security.\n\nWhat should you do?",
         ["Report this habit to building management", "Accept it since staff need smoke break access", "Prop it open only when you are standing nearby", "Ask for a keycard-accessible smoking area"], 0, "Propped doors bypass security. Smokers should use badge access to re-enter.", "Habitual security bypass, side entrance", "Propped doors = security holes. Report it.", "physical_security", 2, "all"),

        # --- PASSWORD ---
        ("Using Free WiFi Without Caution", "You connect to free WiFi at a coffee shop and log into your work email. You notice the WiFi has no password.\n\nWhat should you do?",
         ["Disconnect and use VPN or mobile data now", "Continue since the coffee shop WiFi is fine", "Use it but avoid accessing banking websites", "Change your password after leaving the cafe"], 0, "Open WiFi networks can intercept your login credentials.", "Open WiFi, no encryption, login credentials", "Open WiFi = use VPN. No exceptions.", "password_hygiene", 1, "all"),

        ("Security Question Same as Password", "Your security question answer is the same as your email password. You set it up when you were in a hurry.\n\nWhat should you do?",
         ["Change the security answer to something else", "Keep it since you will remember it easily now", "Change the password to match a different answer", "Remove the security question entirely today"], 0, "Security answers and passwords must be different. One compromises the other.", "Same credential for two purposes", "Security answers and passwords = always different.", "password_hygiene", 2, "all"),

        ("Guest Account Never Disabled", "A guest account was created for a contractor 6 months ago. The project ended but the account is still active.\n\nWhat should you do?",
         ["Ask IT to disable the account immediately", "Leave it in case the contractor returns later", "Change the password but keep the account alive", "Remove only the admin privileges from the account"], 0, "Unused accounts are attack vectors. Disable them when the project ends.", "Stale account, former contractor access", "Disable accounts when projects end.", "password_hygiene", 2, "it"),

        ("Using Pattern Lock on Work Phone", "Your work phone uses a simple L-shaped pattern lock. Your coworker says they figured it out by watching smudge marks.\n\nWhat should you do?",
         ["Switch to a PIN or biometric lock instead", "Change to a different pattern shape right now", "Wipe the screen more often to remove smudges", "Keep the pattern since biometrics fail often"], 0, "Pattern locks leave visible smudge trails. Use PIN or biometrics instead.", "Smudge attack, observable pattern lock", "PINs and biometrics are more secure.", "password_hygiene", 1, "all"),

        # --- USB ---
        ("USB From IT Department Mailbox", "You find a USB in the IT department's internal mailbox with a note: 'Install this driver update on all computers.'\n\nWhat should you do?",
         ["Verify with IT staff before using the USB", "Install the driver on your computer right now", "Install it on one computer to test it first", "Email IT asking who left the USB and note"], 0, "Even internal-looking USBs could be planted by an attacker.", "Internal mailbox, plausible instruction", "Verify USB origin with the actual IT team.", "usb_baiting", 2, "all"),

        ("USB Charging Hub in Co-working Space", "A co-working space offers a free USB charging hub. You want to charge your work phone during a meeting.\n\nWhat should you do?",
         ["Use a wall outlet with your own charger only", "Use the hub since it is in a professional space", "Use the hub with a USB data blocker adapter", "Use the hub but keep your phone locked tightly"], 0, "Shared USB charging hubs can steal data. Use wall outlets or data blockers.", "Shared USB hub, data access risk", "Shared USB hubs = use wall outlets instead.", "usb_baiting", 2, "all"),

        ("USB Promotional Pen With Storage", "You receive a promotional pen with built-in USB storage at a business meeting. You want to use it for presentations.\n\nWhat should you do?",
         ["Have IT scan it before any use at all", "Use it since it came from a business meeting", "Format it before using it for presentations", "Use it for personal files but not for work"], 0, "Promotional USB devices can contain pre-loaded malware.", "Promotional item, built-in USB storage", "All promotional USBs = IT scans first.", "usb_baiting", 1, "all"),

        # --- SOCIAL ENGINEERING ---
        ("Fake Cleaning Crew Leader", "A person claiming to be the new cleaning crew supervisor asks which offices have valuable equipment and what time the building is empty.\n\nWhat should you do?",
         ["Refer them to the building management office", "Answer since cleaning crews need this info now", "Share only the office layout, not the schedule", "Ask for their ID and company name to verify"], 0, "Real crew supervisors are briefed by management. They do not ask staff.", "Reconnaissance questions, new supervisor claim", "Cleaning supervisors are briefed by management.", "social_engineering", 2, "receptionist"),

        ("Pretending To Be Lost Visitor", "A person wanders through the office saying they are lost and looking for a meeting room. They ask about security cameras and door codes.\n\nWhat should you do?",
         ["Escort them to reception immediately now", "Help them find the room and answer questions", "Give directions but not security information", "Tell them to use the building directory instead"], 0, "Lost visitors should be escorted. Questions about security are red flags.", "Lost visitor pretexting, security questions", "Lost visitors = escort to reception.", "social_engineering", 2, "all"),

        ("Fake Journalist Interview Request", "A 'journalist' calls wanting to interview you about your company's finances and upcoming merger plans. They say it is for a business magazine.\n\nWhat should you do?",
         ["Decline and refer them to the PR department", "Answer since media coverage is good for company", "Share general info but not financial details now", "Ask them to send their press card by email"], 0, "Media inquiries go through PR. Never share financial or strategic information.", "Journalist pretexting, financial data request", "Media inquiries go through PR only.", "social_engineering", 3, "management"),

        ("Fake Parking Lot Attendant", "A person in a vest at the parking lot says they are the new attendant. They ask for your employee badge number to 'log your parking spot.'\n\nWhat should you do?",
         ["Refuse and check with building management", "Give your badge number since it seems normal", "Give only your car plate number to them today", "Ask a coworker if they know the new attendant"], 0, "Employee badge numbers are sensitive. New attendants are announced by management.", "Badge number harvesting, new staff claim", "Badge numbers are not shared with strangers.", "social_engineering", 2, "all"),

        ("Fake Software Demo Social Engineer", "A software sales rep asks for a live demo using your actual company data. They say it gives a 'more realistic experience.'\n\nWhat should you do?",
         ["Use only sample data for any demos today", "Load company data for a realistic demo to see", "Use data but hide client names during the demo", "Ask them to bring their own sample dataset"], 0, "Company data should never be used in external demos. Use sample data.", "Real data exposure, sales demo request", "Demos use sample data. Never real data.", "social_engineering", 2, "all"),

        # --- DATA HANDLING ---
        ("Sharing Meeting Notes Via WhatsApp", "After a strategy meeting, you share detailed meeting notes including revenue targets in the team WhatsApp group.\n\nWhat should you do?",
         ["Use company email or approved tools instead", "Continue since it is a private team group now", "Share only action items, not revenue targets", "Delete the message after everyone reads it"], 0, "WhatsApp is not a company-controlled tool. Sensitive data needs approved channels.", "Strategy data on personal messaging app", "Company data goes through company tools.", "data_handling", 1, "all"),

        ("Leaving Desk Without Locking Screen", "You go to the bathroom for 2 minutes without locking your computer screen. Your email and financial reports are open.\n\nWhat should you do?",
         ["Always lock screen with Win+L before going", "Leave it since you will be back in 2 minutes", "Ask a coworker to watch your screen for you now", "Close only the financial report before going"], 0, "2 minutes is enough time for data theft. Lock every time you leave.", "Unlocked screen, brief absence", "Lock with Win+L. Even for 2 minutes.", "data_handling", 1, "all"),

        ("Cloud Storage Link Shared Publicly", "A coworker shares a Google Drive link to a folder with client contracts in a public Slack channel. The link has 'anyone with link' access.\n\nWhat should you do?",
         ["Ask them to change link permissions right now", "Leave it since the Slack channel is internal", "Download the files and ask to remove the link", "Report the link to IT for review and removal"], 0, "Public links mean anyone with the URL can access the files.", "Public link, client contracts, open access", "Cloud links need restricted access settings.", "data_handling", 2, "all"),

        ("Taking Work Home On Paper", "You print 50 pages of customer data to review at home this weekend. You plan to carry them in your bag.\n\nWhat should you do?",
         ["Review the data on your laptop using VPN", "Take the papers since you need to review them", "Take only the pages without customer names today", "Photograph the pages and leave them at office"], 0, "Paper copies of customer data are easily lost. Use VPN and digital access.", "Physical data transport, loss risk", "Use VPN for remote access. No paper copies.", "data_handling", 2, "all"),

        ("Work Laptop At Airport Security", "At airport security, you put your work laptop in the tray. Someone in line behind you picks it up first and hands it back.\n\nWhat should you do?",
         ["Check for any attached USB devices on laptop", "Thank them and continue to your gate quickly", "Ask security to check the laptop for tampering", "Open the laptop to verify nothing was changed"], 0, "Someone handling your laptop could attach a hardware device. Check for anomalies.", "Brief physical access, potential tampering", "Check devices after anyone handles them.", "data_handling", 3, "all"),

        ("Disposing Printed Proposals", "You have printed proposals from a lost bid. They contain pricing strategy and competitive analysis. You want to throw them away.\n\nWhat should you do?",
         ["Shred all pages before disposing of them", "Throw them in the regular bin since we lost", "Tear them in half and put in different bins", "Keep them in a drawer indefinitely as backup"], 0, "Even lost bids contain competitive intelligence. Shred everything.", "Competitive data, disposal without shredding", "All business documents must be shredded.", "data_handling", 1, "all"),

        ("Backup Tapes in Unlocked Cabinet", "Your company's backup tapes sit in an unlocked cabinet in the hallway. The tapes contain full database backups.\n\nWhat should you do?",
         ["Move them to a locked secure area right now", "Leave them since backup tapes are encrypted now", "Put a lock on the cabinet door immediately now", "Report it to IT and wait for their response"], 0, "Backup tapes are portable copies of your entire database. They need physical security.", "Unlocked backup storage, hallway exposure", "Backup tapes = locked storage. Always.", "data_handling", 3, "it"),

        ("AI Tool Generating From Company Data", "Your marketing team uses a public AI image generator, uploading product photos with unreleased designs to create ads.\n\nWhat should you do?",
         ["Stop uploads and use approved tools only", "Continue since the AI only generates new images", "Upload only final released product photos today", "Ask the AI company if they store the uploads"], 0, "Public AI tools may train on uploaded content. Unreleased designs could leak.", "Unreleased IP in public AI tool", "Unreleased designs stay off public AI tools.", "data_handling", 3, "all"),

        # --- MORE PHISHING ---
        ("Fake Google Security Alert", "An email from 'Google Security' says someone in Vietnam accessed your account. Click to secure. The sender email is not from google.com.\n\nWhat should you do?",
         ["Go to Google account security directly", "Click the link to block the Vietnam access", "Reply asking for more details about the login", "Forward the email to Google for verification"], 0, "Check the sender's email domain. Real Google emails come from google.com.", "Wrong sender domain, location fear bait", "Check sender domain. Go to sites directly.", "phishing_email", 1, "all"),

        ("Fake Conference Invitation Email", "An email invites you to an exclusive industry conference. Early bird tickets are free if you register with your credit card for 'verification.'\n\nWhat should you do?",
         ["Verify the conference on their official site", "Register since early bird tickets are free now", "Enter card details since it is just verification", "Forward the invite to your whole team to join"], 0, "Free tickets requiring credit cards are scams. Verify on the official conference website.", "Free ticket bait, credit card verification", "Free events do not need credit card info.", "phishing_email", 2, "all"),

        ("Fake Shared Calendar Phishing", "You receive a Google Calendar invite for a 'Mandatory Security Training' from an external email. It has a link to 'join.'\n\nWhat should you do?",
         ["Check with IT if any training was scheduled", "Accept and click the link to join the training", "Decline the invite but click the link to check", "Forward the invite to your manager to verify"], 0, "Calendar invites from external sources with links are a newer phishing technique.", "External calendar invite, mandatory label", "Unknown calendar invites = verify with IT.", "phishing_email", 2, "all"),

        ("Fake Crypto Investment Email", "An email says your colleague recommended you for a crypto investment with guaranteed daily returns. Click to start with Rs. 10,000.\n\nWhat should you do?",
         ["Delete it. guaranteed returns are always fake", "Click since your colleague recommended you", "Invest Rs. 1,000 first to test the returns", "Ask your colleague if they really recommended it"], 0, "Guaranteed returns do not exist. The colleague's name is used to build trust.", "Colleague name drop, guaranteed returns", "Guaranteed returns in crypto = scam.", "phishing_email", 2, "all"),

        ("Fake WeTransfer Download", "An email says someone sent you files via WeTransfer. Click to download before the link expires. You are not expecting any files.\n\nWhat should you do?",
         ["Delete it since you are not expecting files", "Click to download before the link expires", "Reply asking who sent the files to you today", "Forward the email to IT for their analysis"], 0, "Fake WeTransfer links are common phishing. If you are not expecting files, ignore.", "Expiring link urgency, no expected files", "Not expecting files = not real. Delete.", "phishing_email", 1, "all"),

        # --- MORE SMISHING ---
        ("Fake Mobile Recharge SMS", "An SMS says your mobile recharge of Rs. 500 failed. Click to retry. You did not attempt any recharge today.\n\nWhat should you do?",
         ["Delete it. you did not recharge today", "Click to check why the recharge has failed", "Reply asking which number was being recharged", "Call your carrier to check your balance now"], 0, "No recharge attempted = no failed recharge. Delete the SMS.", "No action taken, failed action claim", "No attempt = no failure. Ignore it.", "smishing", 1, "all"),

        ("Fake Social Media Violation SMS", "An SMS says your Instagram account violated terms. Click to appeal or your account will be deleted in 24 hours.\n\nWhat should you do?",
         ["Open Instagram app to check for any alerts", "Click the link to appeal before deletion now", "Reply asking what violation was found on your account", "Forward the SMS to Instagram support team"], 0, "Instagram sends violations through the app, not SMS. Check directly.", "Platform impersonation, account deletion fear", "Check the app directly for any alerts.", "smishing", 1, "all"),

        # --- MORE VISHING ---
        ("Fake Electricity Meter Reading Call", "A caller says they are from NEA and need to verify your electricity meter number. If you do not provide it, your bill will be estimated higher.\n\nWhat should you do?",
         ["Refuse and check your meter number yourself", "Give the number to avoid a higher estimated bill", "Ask them to visit in person to check the meter", "Give only the first few digits to verify them"], 0, "NEA meter readers visit in person. They do not call for meter numbers.", "NEA impersonation, bill fear manipulation", "Meter readings happen in person.", "vishing", 1, "all"),

        ("Fake Alumni Association Call", "A caller claims to be from your university's alumni association. They want your current employer, salary, and home address for a 'directory update.'\n\nWhat should you do?",
         ["Refuse personal details and verify by email", "Share details since alumni networks are useful", "Share only employer name, not salary or address", "Ask them to send the update form by email"], 0, "Alumni associations do not ask for salary and home address by phone.", "Personal data harvesting, alumni trust", "Alumni updates do not need salary info.", "vishing", 2, "all"),

        # --- MORE SOCIAL ENGINEERING ---
        ("Tailgating With Baby and Bags", "A person with a baby and shopping bags asks you to hold the secure door. They say they live in the building.\n\nWhat should you do?",
         ["Ask them to badge in or call a resident", "Hold the door since they have a baby with them", "Let them in but follow to see where they go", "Take their bags while they badge in themselves"], 0, "Sympathy is a powerful social engineering tool. Security rules still apply.", "Sympathy exploitation, baby and bags", "Rules apply equally. Even with a baby.", "social_engineering", 2, "all"),

        ("Fake Charity Volunteer at Office", "A person comes to the office collecting for a children's charity. They ask for employee names and email addresses to send 'thank you' notes.\n\nWhat should you do?",
         ["Refuse employee data and donate through HR", "Give names and emails to support the charity", "Give only first names but not email addresses", "Ask for their charity registration number first"], 0, "Charities collecting at offices should coordinate through management.", "Charity pretext, employee data harvesting", "Charities coordinate through management.", "social_engineering", 1, "all"),

        # --- MORE DATA HANDLING ---
        ("Client Data On USB To Auditor", "An external auditor asks you to copy client financial records to their personal USB drive for the audit review.\n\nWhat should you do?",
         ["Provide access through a secure portal only", "Copy data to their USB since auditors need it", "Copy only summary data, not detailed records", "Ask them to bring an encrypted USB next time"], 0, "Audit data should be shared through secure, controlled channels.", "External party, personal device, data transfer", "Audit data goes through secure portals.", "data_handling", 2, "finance"),

        ("Auto-Forwarding Email Rule Set", "You discover someone set up an auto-forward rule on your email sending copies of all messages to an external address.\n\nWhat should you do?",
         ["Delete the rule and report to IT right now", "Leave it since it might be a company policy", "Change your email password but keep the rule", "Ask your manager if they set up the rule"], 0, "Auto-forward rules to external addresses are a sign of account compromise.", "Account compromise indicator, data exfiltration", "External auto-forward = report to IT now.", "data_handling", 3, "all"),

        ("Sending Work Files to Spouse", "You email a confidential project plan to your spouse to 'get their opinion.' The plan has client names and contract values.\n\nWhat should you do?",
         ["Never share company data with family members", "Send it since your spouse is very trustworthy", "Remove client names and send only the plan now", "Print it and show at home without emailing it"], 0, "Family trust does not override data protection. Confidential data stays at work.", "Confidential data to family, trust assumption", "Work data stays at work. No family sharing.", "data_handling", 2, "all"),

        # --- MORE PHYSICAL ---
        ("Sensitive Documents in Car", "You leave a folder of employee performance reviews in your car while shopping. The car is locked.\n\nWhat should you do?",
         ["Take them with you or lock in the boot now", "Leave them since the car doors are locked", "Put them under the seat so they are not visible", "Cover them with a jacket on the back seat"], 0, "Locked cars are broken into. Sensitive documents should not be left visible.", "Documents in car, visible through window", "Never leave documents visible in a car.", "physical_security", 1, "all"),

        ("Shared Meeting Room Screen Left On", "The meeting room display is showing the previous meeting's financial projections. A client meeting is about to start in the room.\n\nWhat should you do?",
         ["Turn off the display or clear the content", "Start your meeting since the client is waiting", "Minimize the projection and open your slides", "Ask the previous team to clear their data now"], 0, "Previous meeting data on screen exposes confidential info to the next group.", "Residual data on display, upcoming meeting", "Clear all screens between meetings.", "physical_security", 1, "all"),

        # --- MORE PASSWORD ---
        ("Testing Password on HaveIBeenPwned", "You test your work password on HaveIBeenPwned website. The result shows it appeared in 3 data breaches.\n\nWhat should you do?",
         ["Change it immediately to a new strong one", "Keep it since your account was not breached", "Add a number at the end to make it different", "Test all your other passwords on the site"], 0, "A breached password should be changed immediately on all accounts.", "Breached password confirmed, multiple accounts", "Breached = change immediately. Everywhere.", "password_hygiene", 2, "all"),

        ("WiFi Password Same For Two Years", "Your office WiFi password has not been changed in 2 years. Several employees who left the company know it.\n\nWhat should you do?",
         ["Change the password and notify current staff", "Keep it since changing causes inconvenience", "Change it only when the next person leaves", "Add the year to the existing password instead"], 0, "Former employees with WiFi access can enter the network. Change regularly.", "Stale password, former employee access risk", "Change WiFi passwords when staff leave.", "password_hygiene", 2, "all"),
    ]

    for item in batch:
        t, c, o, ci, e, rf, tip, cat, diff, role = item
        _add(_make(t, c, o, ci, e, rf, tip, cat, diff, role))

_final_batch()


# ════════════════════════════════════════════════════════════════════════════
# 11. LAST FILL. push to 500+
# ════════════════════════════════════════════════════════════════════════════

def _last_fill():
    batch = [
        # PHISHING - 15 more
        ("Fake Apple ID Lock Email", "An email says your Apple ID was locked for security. Click to verify. You own an iPhone.\n\nWhat should you do?",
         ["Go to Apple settings on your phone now", "Click the link to unlock your Apple ID", "Reply with your Apple ID and password", "Forward the email to Apple support now"], 0, "Apple sends alerts in the device itself, not via email links.", "Apple impersonation, device lock fear", "Check Apple settings on your device.", "phishing_email", 1, "all"),

        ("Fake Cloud Backup Email", "An email says your iCloud backup failed. Click to fix or lose all your photos and contacts forever.\n\nWhat should you do?",
         ["Check iCloud backup in phone settings", "Click the link to fix backup immediately", "Reply asking what caused the failure", "Forward the email to IT for analysis"], 0, "iCloud shows backup status in your phone settings.", "Data loss fear, cloud impersonation", "Check backup in your phone settings.", "phishing_email", 1, "all"),

        ("Fake Employee Survey Email", "An email from 'CEO Office' asks you to fill a satisfaction survey. It asks for your login credentials as 'verification.'\n\nWhat should you do?",
         ["Report it. surveys never need passwords", "Fill it since the CEO office sent it out", "Fill it using a fake password for safety", "Forward it to HR to verify the survey"], 0, "Employee surveys never ask for passwords.", "CEO name, password in survey", "Surveys never need your password.", "phishing_email", 2, "all"),

        ("Fake Invoice Attachment Email", "An email with an invoice attachment from an unknown company asks you to pay Rs. 35,000. Your company has no record of this vendor.\n\nWhat should you do?",
         ["Delete it. no record of this vendor here", "Open the attachment to check the details", "Reply asking for the purchase order number", "Forward it to finance to investigate now"], 0, "Unknown vendors sending invoices = phishing with malware attachments.", "Unknown vendor, unexpected invoice", "No record = not real. Delete the email.", "phishing_email", 2, "finance"),

        ("Fake Browser Update Popup", "An email says your Chrome browser needs an urgent security update. Click to download the latest patch.\n\nWhat should you do?",
         ["Update Chrome from its settings menu only", "Click the link to download the update now", "Forward the email to IT for their review", "Reply asking which vulnerability was found"], 0, "Browser updates happen through the browser itself, not email links.", "Browser update bait, download link", "Browsers update through their own menus.", "phishing_email", 1, "all"),

        ("Fake Courier Delivery Email", "An email from 'Nepal Post' says your package needs Rs. 800 customs fee. You are expecting a letter from abroad.\n\nWhat should you do?",
         ["Check Nepal Post's website or call them", "Pay the fee since you expect a letter now", "Click the link to track your package today", "Reply asking for the tracking number first"], 0, "Nepal Post does not collect customs via email. Verify through official channels.", "Real expectation exploited, small fee", "Verify delivery fees through official sites.", "phishing_email", 2, "all"),

        ("Fake Training Certificate Email", "An email says your cybersecurity training certificate is ready. Download it from a link. You did not take any training.\n\nWhat should you do?",
         ["Delete it. you took no such training", "Click to download your certificate today", "Reply asking which training this was for", "Forward it to HR to check their records"], 0, "No training taken = no certificate available.", "No training taken, download bait", "No training = no certificate. Delete.", "phishing_email", 1, "all"),

        ("Fake Visa Card Statement Email", "An email shows a credit card statement with purchases you did not make. Click 'Dispute' to cancel the charges immediately.\n\nWhat should you do?",
         ["Log into your bank app to check charges", "Click 'Dispute' to cancel the fake charges", "Reply asking for the card number on record", "Call the number listed in the email now"], 0, "Check your bank app or card statement directly. Never click email dispute links.", "Charge fear, dispute link phishing", "Check charges through your bank app.", "phishing_email", 2, "all"),

        ("Fake System Administrator Email", "An email from 'System Admin' says your account will be deleted in 48 hours unless you confirm your identity via a form.\n\nWhat should you do?",
         ["Contact IT admin directly to verify this", "Fill the form to keep your account active", "Reply asking why your account is at risk", "Forward the email to your IT department"], 0, "IT admins do not threaten account deletion via email forms.", "Account deletion threat, form phishing", "IT admins verify in person, not by email.", "phishing_email", 2, "all"),

        ("Fake Job Reference Check Email", "An email claims a company is checking your job reference. Click a link to confirm your employment details.\n\nWhat should you do?",
         ["Contact your HR to verify the reference", "Click the link to confirm your employment", "Reply with your job title and start date", "Forward it to your current manager first"], 0, "Reference checks go through HR, not through email links to candidates.", "Reference check bait, employment data", "Reference checks go through HR directly.", "phishing_email", 2, "hr"),

        ("Fake Email Quota Warning", "An email says your mailbox is 99% full. Click to upgrade storage or your emails will bounce starting tomorrow.\n\nWhat should you do?",
         ["Check your actual mailbox storage settings", "Click to upgrade before emails bounce back", "Reply asking how much extra storage costs", "Delete old emails to make more room today"], 0, "Check your email storage in settings. Quota warnings via email links are phishing.", "Storage urgency, bounce threat", "Check storage in your email settings.", "phishing_email", 1, "all"),

        # SMISHING - 8 more
        ("Fake Driving License Renewal SMS", "An SMS says your driving license expires tomorrow. Click to renew online. Your license does not expire for 2 more years.\n\nWhat should you do?",
         ["Ignore it. your license is valid for 2 years", "Click to renew since it might be an error", "Reply asking which license number they have", "Visit the transport office to double check"], 0, "You know your license expiry. False urgency is a manipulation tactic.", "False urgency, known validity dates", "You know when your license expires.", "smishing", 1, "all"),

        ("Fake Cashback SMS", "An SMS says you earned Rs. 2,000 cashback on your last purchase. Click to claim before midnight tonight.\n\nWhat should you do?",
         ["Check your bank app for any real cashback", "Click the link to claim the cashback now", "Reply asking which purchase earned cashback", "Forward the SMS to your bank's support"], 0, "Real cashback appears in your bank app automatically.", "Cashback bait, midnight deadline", "Real cashback shows in your bank app.", "smishing", 1, "all"),

        ("Fake Vaccine Registration SMS", "An SMS says register for a free booster vaccine by clicking a link and entering your citizenship number and health details.\n\nWhat should you do?",
         ["Register through the official health portal", "Click the link to register for the vaccine", "Reply with your citizenship number to register", "Forward the SMS to your family group chat"], 0, "Health registrations go through government health portals, not SMS links.", "Health urgency, citizenship data request", "Health services use official portals.", "smishing", 2, "all"),

        ("Fake Account Upgrade SMS", "An SMS from 'your bank' offers a premium account upgrade. Click a link to switch for free within 24 hours.\n\nWhat should you do?",
         ["Visit your bank branch to ask about this", "Click the link for a free premium upgrade", "Reply asking what benefits the upgrade gives", "Call the number in the SMS for more info"], 0, "Banks offer account upgrades at branches, not through SMS links.", "Free upgrade bait, bank impersonation", "Account upgrades happen at the branch.", "smishing", 1, "all"),

        ("Fake UPI Transaction SMS", "An SMS says Rs. 50,000 was debited from your account via UPI. Click to dispute. UPI is not widely used in Nepal.\n\nWhat should you do?",
         ["Ignore it. UPI is not used in your bank", "Click the link to dispute the transaction", "Call the number to cancel the transaction", "Check your bank app for the transaction"], 0, "If your bank does not use UPI, the SMS is irrelevant and fake.", "Non-existent service, debit fear", "If you do not use the service, ignore it.", "smishing", 1, "all"),

        ("Fake Data Pack Expiry SMS", "An SMS says your data pack expires in 1 hour. Click to renew or lose internet. You just bought a monthly pack yesterday.\n\nWhat should you do?",
         ["Ignore it. you just renewed yesterday", "Click to renew before internet is cut off", "Reply asking which data pack is expiring", "Check your data balance in the carrier app"], 0, "You renewed yesterday. The SMS is fake.", "Known recent action contradicts claim", "You know when you renewed. Trust that.", "smishing", 1, "all"),

        ("Fake Contest Entry SMS", "An SMS from an unknown number says you are the 1000th visitor to a website. Claim a free iPhone by clicking a link now.\n\nWhat should you do?",
         ["Delete it. these are always scam messages", "Click the link to claim the free iPhone", "Reply asking which website you visited today", "Forward it to friends who might want one"], 0, "1000th visitor scams are one of the oldest internet tricks.", "Classic scam pattern, too good to be true", "1000th visitor messages are always scams.", "smishing", 1, "all"),

        ("Fake Weather Alert SMS With Link", "An SMS warns about extreme weather. Click a link for 'safety instructions.' Weather alerts do not normally include links.\n\nWhat should you do?",
         ["Check weather on trusted weather apps only", "Click the link for safety instructions now", "Forward the SMS to your family for awareness", "Reply asking which weather service sent this"], 0, "Weather alerts come from weather apps or TV, not SMS links.", "Emergency exploitation, link in alert", "Weather updates come from weather apps.", "smishing", 1, "all"),

        # VISHING - 8 more
        ("Fake Water Supply Call", "A caller says your office water supply will be cut for non-payment. Pay Rs. 3,000 right now via phone banking.\n\nWhat should you do?",
         ["Hang up and check payment records yourself", "Pay via phone to avoid water supply cut off", "Ask them to send the overdue bill by email", "Give your bank details to process the payment"], 0, "Utility companies send bills, not phone demands for instant payment.", "Utility cut threat, instant payment demand", "Utility bills come on paper, not by phone.", "vishing", 1, "all"),

        ("Fake University Exam Results Call", "A caller says they have your university exam results early. Share your student ID and date of birth to receive them by email.\n\nWhat should you do?",
         ["Check the university website for results", "Share your student ID to get results early", "Give only your ID, not your date of birth", "Ask them which university they represent now"], 0, "Universities post results on their portals. They do not call with results.", "Curiosity bait, personal data request", "Exam results are posted on university portals.", "vishing", 1, "all"),

        ("Fake Car Insurance Call", "A caller says your car insurance premium went up due to an error. They need your policy number and bank details to process a refund.\n\nWhat should you do?",
         ["Call your insurer from the policy documents", "Give your details to receive the refund now", "Give only the policy number, not bank details", "Ask them to send a refund cheque by post"], 0, "Insurance companies process refunds through official channels.", "Refund bait, policy and bank details", "Contact your insurer through official channels.", "vishing", 2, "all"),

        ("Fake Building Safety Inspector Call", "A caller says they need to inspect your office for earthquake preparedness. They ask for floor plans and emergency exit locations by email.\n\nWhat should you do?",
         ["Ask them to schedule through your management", "Email the floor plans for safety compliance", "Give only emergency exit info, not floor plans", "Ask for their inspector ID and call them back"], 0, "Safety inspectors schedule visits through management.", "Safety compliance pressure, floor plan request", "Inspectors coordinate through management.", "vishing", 2, "management"),

        ("Fake Real Estate Agent Call", "A caller says they are a real estate agent. A buyer wants to see your company building and they need the floor layout.\n\nWhat should you do?",
         ["Refuse and refer to your company management", "Email the layout since the building is on sale", "Give a general description but not exact layout", "Ask them to contact the building owner directly"], 0, "Building layouts are sensitive information. Refer to management.", "Real estate pretext, building layout request", "Building information goes through management.", "vishing", 2, "all"),

        ("Fake Environmental Audit Call", "A caller from an 'environmental agency' demands details of your chemical storage, waste disposal, and security protocols.\n\nWhat should you do?",
         ["Ask for official notice and verify with agency", "Share details since compliance is important", "Share only waste disposal, not security details", "Ask them to email the audit questionnaire now"], 0, "Environmental auditors schedule visits and carry identification.", "Compliance pressure, security data included", "Auditors have scheduled visits and proper ID.", "vishing", 3, "management"),

        ("Fake Event Organizer Call", "A caller says they are organizing a company event and need a list of all employees with dietary preferences and phone numbers.\n\nWhat should you do?",
         ["Tell them to coordinate through HR directly", "Share the list since events need this planning", "Share only names but not phone numbers today", "Ask which company authorized the event first"], 0, "Employee data goes through HR, even for company events.", "Event pretext, employee data harvesting", "Employee data requests go through HR.", "vishing", 2, "hr"),

        ("Fake Bank Loan Officer Call", "A caller offers a pre-approved loan at low interest. They just need your PAN, salary slips, and bank statements to 'finalize.'\n\nWhat should you do?",
         ["Hang up and contact your bank if interested", "Share the documents for the pre-approved loan", "Visit the bank branch to ask about this loan", "Share only PAN but not salary or bank details"], 0, "Pre-approved loans do not require you to share documents over the phone.", "Pre-approved bait, document harvesting", "Loans are discussed at the bank branch.", "vishing", 2, "all"),

        # PHYSICAL - 8 more
        ("Unlocked Cash Register After Hours", "You find the cash register drawer open after closing time. Cash is visible inside.\n\nWhat should you do?",
         ["Close and lock it and tell your manager now", "Leave it since the closing staff handles this", "Count the cash and leave a note with total", "Take the cash to your desk for safe keeping"], 0, "Unlocked cash is a loss risk. Secure it and notify management.", "Cash exposure, after hours, no supervision", "Lock cash and notify management.", "physical_security", 1, "all"),

        ("ID Printer Left Accessible", "The visitor badge printer is left on and accessible in the reception area. Anyone could print a badge.\n\nWhat should you do?",
         ["Turn it off and report to office management", "Leave it since reception staff will return now", "Print yourself an extra badge as a backup card", "Move it to a locked room behind the desk now"], 0, "Badge printers create access credentials. They must be secured.", "Badge creation capability, unsecured device", "Badge printers must be secured at all times.", "physical_security", 2, "receptionist"),

        ("Suspicious Vehicle Parked Outside", "A vehicle has been parked near the office entrance for 3 days. Nobody recognizes it. The windows are tinted.\n\nWhat should you do?",
         ["Report it to building security or police", "Ignore it since it is a public parking area", "Try to look through the tinted car windows", "Put a note on the windshield asking to move"], 0, "Unusual vehicles near office entrances warrant security attention.", "Unknown vehicle, extended presence, tinted", "Report suspicious vehicles to security.", "physical_security", 2, "all"),

        ("Emergency Contact List on Wall", "The emergency contact list with personal phone numbers and addresses of all staff is posted on the common room wall.\n\nWhat should you do?",
         ["Ask HR to move it to a secure shared drive", "Leave it since everyone needs emergency contacts", "Remove it and keep a copy in your own desk", "Cover the personal details with a paper strip"], 0, "Personal contact details should not be publicly displayed.", "Personal data on public display, wall exposure", "Emergency lists belong in secure systems.", "physical_security", 2, "hr"),

        ("Biometric Scanner Not Working", "The fingerprint scanner at the entrance stopped working. Staff are using a shared backup PIN to enter.\n\nWhat should you do?",
         ["Report to IT and ask for individual temp PINs", "Use the shared PIN since everyone else does too", "Enter without scanning until it is fixed today", "Write down the shared PIN for future reference"], 0, "Shared PINs eliminate individual accountability. Request individual alternatives.", "Shared credential, no accountability", "Shared PINs = no accountability. Fix it.", "physical_security", 2, "all"),

        ("Laptop Left in Conference Room Overnight", "You see a laptop left in the conference room at end of day. The room will be used by external clients tomorrow morning.\n\nWhat should you do?",
         ["Lock the laptop in a cabinet or take to IT", "Leave it since the room will be locked tonight", "Put it under the table so clients cannot see", "Email all staff asking whose laptop it is now"], 0, "External clients accessing the room could access the laptop.", "Overnight exposure, external clients next day", "Secure unattended devices before you leave.", "physical_security", 1, "all"),

        # PASSWORD - 6 more
        ("Reusing Password After Breach", "You heard your email provider had a data breach. Your work email uses the same password as the breached provider.\n\nWhat should you do?",
         ["Change both passwords to different ones now", "Change only the breached provider password now", "Wait to see if your account was affected first", "Add a number to the existing password for both"], 0, "Same password on breached service = your work account is at risk too.", "Breach notification, same password reuse", "Same password on breached site = change all.", "password_hygiene", 2, "all"),

        ("Sharing Password Via Slack", "A coworker DMs you on Slack asking for the shared team password. You type it in the chat.\n\nWhat should you do?",
         ["Delete the message and use a password manager", "Leave it since Slack is an internal tool only", "Edit the message to remove the password text", "Tell them to remember it and delete the message"], 0, "Slack messages are logged and searchable. Never type passwords in chat.", "Password in plaintext chat, searchable logs", "Never type passwords in any chat tool.", "password_hygiene", 2, "all"),

        ("Two Accounts Same Password", "You use the same password for your email and banking. A friend says reusing passwords is fine if they are strong.\n\nWhat should you do?",
         ["Use different passwords for email and bank", "Keep them since the password is very strong now", "Change only the bank password to be extra safe", "Add the year to one to make them different"], 0, "Even strong passwords should not be reused. One breach compromises both.", "Strong password reuse, false safety belief", "Strong does not mean reusable. One per site.", "password_hygiene", 1, "all"),

        ("Service Account With Weak Password", "A critical server uses 'admin123' as the service account password. It has been this way since the server was set up 3 years ago.\n\nWhat should you do?",
         ["Change it to a strong random password today", "Keep it since only IT knows about the server", "Change it but write the new one on a sticky note", "Add the server name to make it more unique now"], 0, "Service accounts with weak passwords are prime targets. Change immediately.", "Weak service credential, years without rotation", "Service accounts need strong passwords too.", "password_hygiene", 3, "it"),

        ("Asking IT to Share Root Password", "Your manager asks IT to share the server root password via email to the whole IT team.\n\nWhat should you do?",
         ["Use a password vault for shared credentials", "Email it since the IT team is all trusted now", "Email but mark it as confidential and urgent", "Share it verbally in a meeting room instead"], 0, "Root passwords in email are stored forever in inboxes. Use password vaults.", "Root password in email, permanent storage risk", "Root passwords belong in vaults, not email.", "password_hygiene", 3, "it"),

        ("Ignoring Password Breach Alert", "Your browser warns that your saved password for a banking site was found in a data breach. You dismiss the notification.\n\nWhat should you do?",
         ["Change the banking password right now today", "Dismiss it since your bank has extra security", "Change it next month during regular maintenance", "Enable 2FA but keep the same password for now"], 0, "Banking credential breaches need immediate action. Do not dismiss.", "Banking breach alert, dismissed notification", "Banking breach = immediate password change.", "password_hygiene", 2, "all"),

        # USB - 6 more
        ("USB From IT Training", "During IT security training, the trainer gives everyone a USB with training materials. The USB is not branded or sealed.\n\nWhat should you do?",
         ["Ask IT to host materials online or email them", "Use it since the IT trainer provided it today", "Scan it with antivirus before using it at work", "Format it first and then check for the files"], 0, "Even training USBs can carry malware if not from a trusted source.", "Training context, unbranded unsealed USB", "Ask for materials by email instead of USB.", "usb_baiting", 2, "all"),

        ("USB Left On Bus", "You find a USB drive on the bus seat. It has a label with a company name you recognize.\n\nWhat should you do?",
         ["Leave it or give to the bus driver instead", "Plug it in to find the owner contact details", "Take it to the company written on the label", "Keep it since nobody will come looking for it"], 0, "Even labelled USBs should not be plugged in. Leave it or hand to authorities.", "Public transport, company label as trust signal", "Never plug in USBs you find anywhere.", "usb_baiting", 1, "all"),

        ("USB Received In Mail", "You receive a USB drive in the mail from an unknown sender. The package says 'Important: Review contents immediately.'\n\nWhat should you do?",
         ["Give it to IT. do not plug it in at all", "Plug it in since it says it is important now", "Open it on an offline computer for safety only", "Throw it away since you do not know the sender"], 0, "USBs from unknown senders in the mail are a known attack technique.", "Unknown sender, urgency label, mail delivery", "Unknown USB in mail = give to IT.", "usb_baiting", 2, "all"),

        ("USB From Repairman", "The computer repairman finishes fixing your PC and hands you a USB. 'Install this driver for best performance.'\n\nWhat should you do?",
         ["Ask IT to verify the driver before using it", "Install the driver since the repairman said so", "Install it but check task manager for odd processes", "Decline the USB and download drivers from vendor"], 0, "Drivers should come from official vendor websites, not random USBs.", "Repairman trust, unofficial driver source", "Drivers come from official vendor sites.", "usb_baiting", 2, "all"),

        ("USB Keychain Gift", "A business partner gifts you a keychain with a built-in USB drive as a souvenir. You want to use it for work files.\n\nWhat should you do?",
         ["Have IT scan it before using it for work", "Use it since it is from a business partner now", "Use it only for personal photos and music", "Format it before using it for any work files"], 0, "Gift USBs from any source should be scanned by IT before use.", "Gift from known person, USB storage device", "Gift USBs = IT scans before any use.", "usb_baiting", 1, "all"),

        ("USB Found Inside New Equipment Box", "Inside a box of new office equipment, you find a loose USB drive that is not listed on the packing slip.\n\nWhat should you do?",
         ["Report it to IT. it should not be there", "Plug it in to check if it has setup software", "Contact the vendor to ask about the extra USB", "Throw it away since it was not on the list"], 0, "Supply chain attacks plant USBs inside legitimate shipments.", "Supply chain risk, unlisted item in shipment", "Unlisted USBs in shipments = report to IT.", "usb_baiting", 3, "all"),

        # SOCIAL ENGINEERING - 8 more
        ("Fake Internship Coordinator Call", "A caller says they are placing interns at your company. They ask for department budgets, headcount, and manager names.\n\nWhat should you do?",
         ["Refer them to HR for all intern placements", "Share info since interns would help the team", "Share only headcount but not budget details now", "Ask them which university they represent today"], 0, "Internship placements go through HR. Do not share organizational data.", "Internship pretext, organizational data request", "Intern placements go through HR only.", "social_engineering", 2, "hr"),

        ("Shoulder Surfing On Train", "On the train, you work on a spreadsheet with client financial data. The person next to you is looking at your screen.\n\nWhat should you do?",
         ["Close the file and work on it at the office", "Continue but tilt the screen slightly away now", "Ask the person politely to look the other way", "Cover the screen with your hand while working"], 0, "Public transport is not safe for viewing confidential data.", "Public transport, shoulder surfing risk", "Confidential work = private places only.", "social_engineering", 1, "all"),

        ("Fake Health Inspector Visit", "A person arrives claiming to be a health inspector. They want to inspect the kitchen but also ask about office layout and staff schedules.\n\nWhat should you do?",
         ["Verify with your local health department now", "Give full access since health inspections matter", "Allow kitchen inspection but not office details", "Ask for identification and inspection notice"], 0, "Health inspectors carry ID and schedule visits. They inspect kitchens, not offices.", "Authority impersonation, scope creep questions", "Inspectors have IDs and scheduled visits.", "social_engineering", 2, "all"),

        ("Vendor Asking For Client List", "A vendor says they need your client list to 'ensure no conflicts of interest' before signing a partnership.\n\nWhat should you do?",
         ["Refuse. client lists are confidential data", "Share the list since partnerships need this info", "Share only industry types, not specific clients", "Ask your manager to decide if sharing is fine"], 0, "Client lists are highly confidential. Vendors do not need them.", "Client data request, partnership pretext", "Client lists are never shared with vendors.", "social_engineering", 3, "sales"),

        ("Fake Alumni Reunion Organizer", "Someone contacts you claiming to organize a university alumni reunion. They ask for addresses and phone numbers of former classmates who work at your company.\n\nWhat should you do?",
         ["Refuse. share your own contact if desired", "Share details since alumni events are fun now", "Give only names but not addresses or phone numbers", "Ask them to send reunion details by email first"], 0, "Never share other people's contact information without their consent.", "Alumni pretext, coworker contact harvesting", "Never share others' contacts without consent.", "social_engineering", 2, "all"),

        ("Pretexting Using Delivery Excuse", "A person at reception says they have a delivery for the CEO but need to deliver it in person to the CEO's desk. They insist it is confidential.\n\nWhat should you do?",
         ["Accept the delivery at reception for the CEO", "Escort them to the CEO's office right now", "Let them go since they seem to know the CEO", "Call the CEO's assistant to come to reception"], 0, "All deliveries are accepted at reception. Nobody goes directly to executive offices.", "Confidential delivery excuse, direct access demand", "All deliveries are accepted at reception.", "social_engineering", 2, "receptionist"),

        ("Social Media OSINT for Phishing", "You notice your personal social media shows your workplace, job title, coworkers' names, and daily routine details.\n\nWhat should you do?",
         ["Review and restrict your privacy settings now", "Keep it since everyone shares on social media", "Remove only your workplace info from profiles", "Make your profile private but keep all content"], 0, "Public social media details fuel targeted phishing and social engineering.", "Personal OSINT exposure, social media sharing", "Review and restrict social media privacy.", "social_engineering", 1, "all"),

        ("Fake Partner Company Request", "A caller claims to be from a partner company. They need your API keys and database credentials to 'integrate their system.'\n\nWhat should you do?",
         ["Refuse and coordinate through IT teams only", "Share credentials since they are a partner now", "Create temporary credentials with limited access", "Ask them to send the integration specs by email"], 0, "API keys and database credentials are never shared by phone.", "Partner impersonation, credential request", "Credentials go through IT, not by phone.", "social_engineering", 3, "it"),

        # DATA HANDLING - 8 more
        ("Photographing Client Whiteboard", "During a meeting at a client's office, you photograph their whiteboard with strategy notes. They did not say you could.\n\nWhat should you do?",
         ["Delete the photo and ask permission first", "Keep it since you need it for your notes now", "Keep it but blur the confidential parts later", "Send it to your team for context on the project"], 0, "You should always ask before photographing someone else's confidential information.", "Unauthorized photography, client data capture", "Ask before photographing client information.", "data_handling", 1, "all"),

        ("Sending Files Via Personal Email", "Your company email has a 10MB attachment limit. You use your personal Gmail to send a 25MB client report to a colleague.\n\nWhat should you do?",
         ["Use company approved file sharing tools only", "Send via Gmail since the file is too large", "Compress the file to fit the company email limit", "Upload to personal Google Drive and share link"], 0, "Personal email bypasses company security controls. Use approved file sharing.", "Personal email, company data, size workaround", "Use company file sharing for large files.", "data_handling", 2, "all"),

        ("Talking About Salaries in Canteen", "In the canteen, you overhear coworkers loudly discussing another employee's salary and performance rating.\n\nWhat should you do?",
         ["Privately suggest they discuss this elsewhere", "Join the conversation since you are curious now", "Ignore it since it is not your responsibility", "Report them to HR for the privacy violation"], 0, "Salary and performance data is confidential. Suggest they move to a private space.", "Public discussion of confidential HR data", "Salary talks need a private room.", "data_handling", 1, "all"),

        ("Leaving VPN Connected at Home", "You leave your company VPN connected after work. Your family uses the same home computer for browsing.\n\nWhat should you do?",
         ["Disconnect VPN when you finish working today", "Leave it since VPN does not affect browsing", "Leave it for extra security while browsing now", "Create separate user accounts for your family"], 0, "Family browsing through corporate VPN creates compliance and security issues.", "VPN always on, shared device, family use", "Disconnect VPN when work is done.", "data_handling", 2, "all"),

        ("Printed Report Left in Taxi", "You realize you left a printed financial report in the taxi you just took. It has quarterly revenue data.\n\nWhat should you do?",
         ["Report the data loss to your manager today", "Try to contact the taxi company to retrieve it", "Do nothing since nobody will care about the report", "Create a new report and forget the lost one"], 0, "Lost documents with financial data = data breach. Report immediately.", "Lost physical document, financial data exposed", "Lost documents = report immediately.", "data_handling", 2, "finance"),

        ("Sharing Screen With Notifications On", "During a presentation to external clients, your screen shows email notification popups with subject lines about other clients.\n\nWhat should you do?",
         ["Turn off notifications before presenting", "Continue since the popups disappear quickly", "Apologize and minimize the email application", "Close the email app after the first popup now"], 0, "Notification popups during presentations expose confidential client information.", "Screen share, notification exposure risk", "Turn off all notifications before presenting.", "data_handling", 1, "all"),

        ("Employee Data In Shared Spreadsheet", "Your team stores employee emergency contacts, medical conditions, and bank details in a shared Google Sheet that everyone can access.\n\nWhat should you do?",
         ["Raise this with HR for proper data handling", "Continue since the team needs this information", "Restrict access to HR and management accounts", "Move the data to an encrypted local file today"], 0, "Employee personal data needs restricted access and proper security controls.", "Bulk personal data, unrestricted shared access", "Employee data needs restricted access.", "data_handling", 3, "hr"),

        ("Auto Backup to iCloud On Work Mac", "Your work MacBook automatically backs up work files to your personal iCloud. IT has not configured this.\n\nWhat should you do?",
         ["Disable iCloud backup for all work folders", "Leave it since iCloud is encrypted and secure", "Only disable backup for confidential folders now", "Ask IT to set up a proper backup solution instead"], 0, "Personal iCloud with work files is shadow IT. Company data needs company backup.", "Personal cloud backup, shadow IT risk", "Disable personal cloud for work files.", "data_handling", 2, "all"),
    ]

    for item in batch:
        t, c, o, ci, e, rf, tip, cat, diff, role = item
        _add(_make(t, c, o, ci, e, rf, tip, cat, diff, role))

_last_fill()


# ════════════════════════════════════════════════════════════════════════════
# SEED SCRIPT
# ════════════════════════════════════════════════════════════════════════════

def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        print("Wiping all existing scenarios and attempts...")
        attempt_n = Attempt.query.delete()
        scenario_n = Scenario.query.delete()
        db.session.commit()
        print(f"  Cleared {scenario_n} scenarios and {attempt_n} attempts.")

        added = 0
        skipped = 0
        seen_titles: set[str] = set()
        for row in SCENARIOS:
            t = row["title"]
            n = 1
            while t in seen_titles:
                n += 1
                t = f"{row['title']} ({n})"
            row["title"] = t
            seen_titles.add(t)
            db.session.add(Scenario(**row))
            added += 1
            if added % 50 == 0:
                db.session.commit()

        db.session.commit()

        # Verify option length balance
        all_sc = Scenario.query.all()
        bad_spread = 0
        for s in all_sc:
            opts = [s.option_a, s.option_b, s.option_c, s.option_d]
            lengths = [len(o) for o in opts if o]
            if lengths and (max(lengths) - min(lengths)) > MAX_SPREAD:
                bad_spread += 1

        per_cat = (
            db.session.query(Scenario.category, db.func.count(Scenario.id))
            .group_by(Scenario.category).all()
        )
        per_diff = (
            db.session.query(Scenario.difficulty, db.func.count(Scenario.id))
            .group_by(Scenario.difficulty).all()
        )

        print(f"\nInserted {added} scenarios ({bad_spread} with spread > {MAX_SPREAD} chars).")
        print("\n--- By Category ---")
        for cat, n in sorted(per_cat):
            print(f"  {cat:22s} {n}")
        print("\n--- By Difficulty ---")
        for diff, n in sorted(per_diff):
            print(f"  Level {diff}: {n}")
        print(f"\nTotal: {sum(n for _, n in per_cat)}")


if __name__ == "__main__":
    main()
