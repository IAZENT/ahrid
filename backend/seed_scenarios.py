"""Seed the AHRIP scenario question bank (BSc demo).

This script wipes every existing Scenario row and reseeds a fresh catalogue
of MCQ training items covering all 8 risk categories. Each question carries
four options whose length is deliberately balanced so wording length never
gives the correct answer away.

Categories (3 questions each = 24 total):
  phishing_email, smishing, vishing, physical_security,
  password_hygiene, usb_baiting, social_engineering, data_handling

Run after seed_users.py:

    python seed_scenarios.py
"""
from __future__ import annotations

from app import create_app
from app.extensions import db
from app.models.attempt import Attempt
from app.models.scenario import Scenario


# Each entry has 4 options of roughly equal character length so length
# alone never reveals the correct answer.
SCENARIOS = [
    # ────────── PHISHING EMAIL ──────────
    {
        "title": "Bank security alert email",
        "content": (
            "An email from \"alerts@yourbank-secure.co\" warns that suspicious "
            "activity was detected and asks you to verify your account at the "
            "linked page within 24 hours."
        ),
        "category": "phishing_email", "difficulty": 1, "correct_answer": "C",
        "option_a": "Click the link and sign in to confirm the activity is yours.",
        "option_b": "Reply to the sender and ask them to confirm authenticity.",
        "option_c": "Delete the email and log in via your usual bank app instead.",
        "option_d": "Forward the email to family so they can also stay alert.",
        "explanation": (
            "Lookalike domains, urgency, and a verification link are classic "
            "phishing markers. Always log in through a channel you trust."
        ),
        "red_flags": "Lookalike domain; 24-hour pressure; embedded verification link.",
        "learning_tip": "Verify by opening the official app yourself, never via email links.",
    },
    {
        "title": "HR benefits enrolment email",
        "content": (
            "An email claiming to be from HR asks you to confirm your benefits "
            "selection by entering your password on a portal hosted on a "
            "domain you have never seen before."
        ),
        "category": "phishing_email", "difficulty": 2, "correct_answer": "B",
        "option_a": "Enter your password to make sure benefits remain active.",
        "option_b": "Verify with HR using your usual internal contact channel.",
        "option_c": "Forward to colleagues so they can complete it before you.",
        "option_d": "Reply to ask which manager approved the new HR portal.",
        "explanation": (
            "Real HR processes never live on unfamiliar external domains. "
            "Verify out-of-band before entering any credentials."
        ),
        "red_flags": "Unknown portal domain; password requested; HR impersonation.",
        "learning_tip": "Credentials never belong on a portal you can't recognise.",
    },
    {
        "title": "Invoice attachment from a vendor",
        "content": (
            "A vendor email contains an unexpected invoice attachment named "
            "\"INVOICE_OVERDUE.html\" and urges you to open it immediately to "
            "avoid late fees being applied."
        ),
        "category": "phishing_email", "difficulty": 2, "correct_answer": "D",
        "option_a": "Open the attachment to check the invoice number quickly.",
        "option_b": "Forward to finance so they can open and review the file.",
        "option_c": "Reply asking the vendor to resend the file in a new format.",
        "option_d": "Report it to IT and confirm the invoice through known contacts.",
        "explanation": (
            "HTML invoice attachments are a known credential-harvest delivery "
            "method. Verify with a trusted contact before opening anything."
        ),
        "red_flags": "Unexpected HTML invoice; urgency; unfamiliar sender pressure.",
        "learning_tip": "Unexpected attachments deserve a phone call, not a click.",
    },

    # ────────── SMISHING ──────────
    {
        "title": "Bank text about a frozen card",
        "content": (
            "An SMS says: \"Your card has been temporarily blocked. Verify your "
            "details now at secure-bank-verify.co/np to restore access within "
            "the next sixty minutes.\""
        ),
        "category": "smishing", "difficulty": 1, "correct_answer": "C",
        "option_a": "Open the link and confirm details to unblock the card.",
        "option_b": "Reply STOP so the bank stops sending the alert messages.",
        "option_c": "Ignore the text and call your bank using its known number.",
        "option_d": "Forward the text to friends so they avoid the same scam.",
        "explanation": (
            "Banks never restore access through SMS links. The lookalike "
            "domain and tight deadline are textbook smishing patterns."
        ),
        "red_flags": "Lookalike domain; 60-minute pressure; unsolicited SMS link.",
        "learning_tip": "Phone the number on your card, never the one in the text.",
    },
    {
        "title": "Tax refund text from the government",
        "content": (
            "An SMS claims you are eligible for a tax refund of NPR 14,500 and "
            "asks you to enter your bank details at the supplied link to "
            "receive the funds quickly."
        ),
        "category": "smishing", "difficulty": 2, "correct_answer": "A",
        "option_a": "Delete the text and verify directly on the official site.",
        "option_b": "Tap the link and enter details so the refund clears today.",
        "option_c": "Reply with your bank account number to speed up the refund.",
        "option_d": "Share the SMS with colleagues who may also have a refund.",
        "explanation": (
            "Tax authorities never collect bank details via SMS. Refund lures "
            "are a common smishing payload aimed at harvesting account info."
        ),
        "red_flags": "Unsolicited refund offer; bank-detail request; SMS link.",
        "learning_tip": "Government services use their official portal, not text links.",
    },
    {
        "title": "Two-factor code request via SMS",
        "content": (
            "You receive a text asking you to forward a six-digit code that "
            "was just sent to your phone, claiming it will help recover a "
            "colleague's locked work account."
        ),
        "category": "smishing", "difficulty": 2, "correct_answer": "B",
        "option_a": "Forward the code to help your colleague get back to work.",
        "option_b": "Refuse and confirm with the colleague through a known channel.",
        "option_c": "Reply asking which system the locked account belongs to.",
        "option_d": "Send the code only after the colleague replies with thanks.",
        "explanation": (
            "Sharing 2FA codes is never legitimate. Account-recovery scams "
            "rely on social pressure to extract one-time codes from victims."
        ),
        "red_flags": "Code-forwarding request; urgency; impersonation of colleague.",
        "learning_tip": "One-time codes are personal; treat them like passwords.",
    },

    # ────────── VISHING ──────────
    {
        "title": "Caller from \"the IT helpdesk\"",
        "content": (
            "Someone phones claiming to be from IT and says they need your "
            "password to apply an urgent security patch before the system "
            "starts locking accounts at the end of the day."
        ),
        "category": "vishing", "difficulty": 1, "correct_answer": "B",
        "option_a": "Give the password so the patch can be applied on time.",
        "option_b": "Decline and call IT back using your saved company number.",
        "option_c": "Read out only part of the password to stay slightly safer.",
        "option_d": "Ask their badge number and continue the call as normal.",
        "explanation": (
            "Real IT teams never request passwords. Always verify by calling "
            "your known internal number  never trust the inbound channel."
        ),
        "red_flags": "Password request; urgency; inbound caller you can't verify.",
        "learning_tip": "Hang up and call IT back on the official number.",
    },
    {
        "title": "Bank fraud team verification call",
        "content": (
            "A caller claims to be from your bank's fraud team and reads back "
            "your card's last four digits, then asks for the full card number "
            "to confirm a suspicious overseas transaction."
        ),
        "category": "vishing", "difficulty": 2, "correct_answer": "D",
        "option_a": "Read the card number so the fraud team can block charges.",
        "option_b": "Confirm only the expiry date to avoid handing over too much.",
        "option_c": "Provide the CVV instead of the full card number for safety.",
        "option_d": "Hang up and call the bank using the number on your card.",
        "explanation": (
            "Real fraud teams already have your account details. Knowing the "
            "last four digits is not proof of identity in any direction."
        ),
        "red_flags": "Inbound call; card-number request; fake authority claim.",
        "learning_tip": "Banks call to alert, never to harvest your card numbers.",
    },
    {
        "title": "Recorded voicemail about a court case",
        "content": (
            "A robotic voicemail says a legal case has been opened against you "
            "and instructs you to press 1 to speak with an officer who can "
            "settle the matter before any further action is taken."
        ),
        "category": "vishing", "difficulty": 1, "correct_answer": "A",
        "option_a": "Delete the voicemail and report the number to your IT team.",
        "option_b": "Press 1 and listen to the officer to learn what is wrong.",
        "option_c": "Call the number back later to clarify the alleged charges.",
        "option_d": "Reply to the message so the case officer can verify you.",
        "explanation": (
            "Courts and police never serve legal notices through robotic "
            "voicemails. This is a common authority-pressure scam pattern."
        ),
        "red_flags": "Robotic voice; legal threat; press-1 callback prompt.",
        "learning_tip": "Authority scams disappear the moment you stop engaging.",
    },

    # ────────── PHYSICAL SECURITY ──────────
    {
        "title": "Stranger asking for door access",
        "content": (
            "A person you do not recognise stands at the secure office door "
            "and says their access badge is broken, asking you to swipe them "
            "in so they don't miss an important client meeting."
        ),
        "category": "physical_security", "difficulty": 1, "correct_answer": "C",
        "option_a": "Swipe them through so they can attend the meeting on time.",
        "option_b": "Let them in but stay nearby in case anything looks unusual.",
        "option_c": "Ask them to wait while reception verifies their identity.",
        "option_d": "Hold the door open since they look like a legitimate guest.",
        "explanation": (
            "Tailgating bypasses every digital control. Visitors must always "
            "be verified through reception, not by individual employees."
        ),
        "red_flags": "Unknown person; broken-badge story; pressure to be polite.",
        "learning_tip": "Politely redirecting to reception is always the safe answer.",
    },
    {
        "title": "Unattended laptop in a meeting room",
        "content": (
            "Walking past a meeting room you spot a colleague's laptop left "
            "unlocked and unattended on the table while they appear to have "
            "stepped out for a coffee break."
        ),
        "category": "physical_security", "difficulty": 1, "correct_answer": "B",
        "option_a": "Leave it as it is; the colleague is responsible for it.",
        "option_b": "Lock the screen and let the colleague know when they return.",
        "option_c": "Move the laptop to your own desk so it stays nearby and safe.",
        "option_d": "Take a picture as a reminder for the colleague when they return.",
        "explanation": (
            "Unlocked devices are an open door. A quick lock protects the "
            "owner without violating their privacy or workflow."
        ),
        "red_flags": "Unattended device; unlocked screen; shared meeting space.",
        "learning_tip": "If you wouldn't leave your wallet, don't leave your laptop.",
    },
    {
        "title": "Printout left on the shared printer",
        "content": (
            "On the shared office printer you find a stack of pages clearly "
            "marked \"CONFIDENTIAL  payroll\" that no one has collected, and "
            "the area around the printer is currently empty."
        ),
        "category": "physical_security", "difficulty": 2, "correct_answer": "D",
        "option_a": "Leave the stack on the printer for the owner to find later.",
        "option_b": "Take it back to your desk and try to identify the author.",
        "option_c": "Throw the stack into the nearest open recycling bin straight away.",
        "option_d": "Bring it to HR or the security team for proper handling.",
        "explanation": (
            "Confidential printouts must be controlled, not left in the open. "
            "Hand them to the function that owns the data  usually HR."
        ),
        "red_flags": "Confidential label; uncollected printout; unattended area.",
        "learning_tip": "Sensitive paper belongs in a controlled hand, not an open tray.",
    },

    # ────────── PASSWORD HYGIENE ──────────
    {
        "title": "Sharing a password with a colleague",
        "content": (
            "A teammate is rushing to finish a deadline and asks you to share "
            "your account password so they can log in once and submit the "
            "report on your behalf before the cut-off."
        ),
        "category": "password_hygiene", "difficulty": 1, "correct_answer": "C",
        "option_a": "Share it once since the teammate is trusted and in a hurry.",
        "option_b": "Share it but change the password right after they finish using it.",
        "option_c": "Refuse and offer to submit the report on the teammate's behalf.",
        "option_d": "Write it on a sticky note so they can use it discreetly.",
        "explanation": (
            "Account ownership is non-transferable. Sharing makes audit "
            "trails meaningless and exposes you to whatever the other does."
        ),
        "red_flags": "Password-sharing pressure; deadline urgency; trust appeal.",
        "learning_tip": "Your password identifies you, never anyone else.",
    },
    {
        "title": "Reusing one strong password",
        "content": (
            "You created one long, complex password that you find easy to "
            "remember and you are tempted to reuse it across both your work "
            "accounts and your personal email and shopping accounts."
        ),
        "category": "password_hygiene", "difficulty": 1, "correct_answer": "A",
        "option_a": "Use a password manager to generate a unique one per site.",
        "option_b": "Reuse it because the password itself is genuinely strong.",
        "option_c": "Reuse it but tweak the last two characters for each site.",
        "option_d": "Keep one for work, and reuse another one for everything else.",
        "explanation": (
            "Credential-stuffing relies entirely on password reuse. A "
            "manager defeats this without any memorisation effort."
        ),
        "red_flags": "Reuse temptation; \"strong enough\" excuse; cross-account risk.",
        "learning_tip": "Unique passwords + a manager makes credential-stuffing fail.",
    },
    {
        "title": "Browser asking to save a password",
        "content": (
            "On a shared kiosk machine the browser pops up an offer to save "
            "your work password so you don't have to enter it again the next "
            "time you sign in from this same machine."
        ),
        "category": "password_hygiene", "difficulty": 2, "correct_answer": "B",
        "option_a": "Save it because the browser will encrypt it before storing.",
        "option_b": "Decline and ensure you sign out fully when leaving the device.",
        "option_c": "Save it but only for the rest of the day to limit exposure.",
        "option_d": "Save it and clear the saved entry yourself before leaving.",
        "explanation": (
            "Shared machines must never retain credentials. The next user "
            "inherits whatever the browser remembers, encrypted or not."
        ),
        "red_flags": "Shared device; persistent credential storage; convenience prompt.",
        "learning_tip": "On shared machines, save nothing and sign out cleanly.",
    },

    # ────────── USB BAITING ──────────
    {
        "title": "Branded USB given at a conference",
        "content": (
            "At a tech conference a friendly stall hands you a branded USB "
            "stick supposedly containing slides, a discount code, and a free "
            "trial activation key for one of their products."
        ),
        "category": "usb_baiting", "difficulty": 1, "correct_answer": "B",
        "option_a": "Plug it into your work laptop to grab the slides quickly.",
        "option_b": "Ask the vendor for an online download link instead of using it.",
        "option_c": "Plug it into a personal laptop first to keep work isolated.",
        "option_d": "Give it to a colleague who has not yet collected one.",
        "explanation": (
            "Even branded USB devices have shipped with malware in real "
            "incidents. Online downloads from a known domain are far safer."
        ),
        "red_flags": "Unverified hardware; mass giveaway; convenience offer.",
        "learning_tip": "When a link works, never choose the USB instead.",
    },
    {
        "title": "USB drive in the staff toilet",
        "content": (
            "While leaving the staff toilet you notice an unlabelled USB stick "
            "on the counter near the sink, and there is no obvious owner "
            "anywhere in the surrounding office area."
        ),
        "category": "usb_baiting", "difficulty": 1, "correct_answer": "C",
        "option_a": "Plug it into your laptop to look for an owner identity file.",
        "option_b": "Leave it where it is; the owner will probably come back soon.",
        "option_c": "Hand it to IT or security and let them decide what to do.",
        "option_d": "Drop it into a recycling bin to make sure no one uses it.",
        "explanation": (
            "USB drops are a low-cost initial-access vector. Any unknown "
            "device must reach IT or security through a controlled chain."
        ),
        "red_flags": "Unknown device; convenient drop location; unlabelled stick.",
        "learning_tip": "Unknown USB ⇒ not your problem to plug in, only to report.",
    },
    {
        "title": "Charging cable found at airport",
        "content": (
            "At the airport you spot an unattended USB-C cable left at a "
            "charging station and your phone battery is almost empty before "
            "you board your next long-distance flight."
        ),
        "category": "usb_baiting", "difficulty": 2, "correct_answer": "D",
        "option_a": "Use it briefly since the cable cannot really transfer data.",
        "option_b": "Use it but only with the phone screen locked the entire time.",
        "option_c": "Plug it into a power bank first, then charge the phone from that.",
        "option_d": "Avoid it and use your own cable with a wall socket adapter.",
        "explanation": (
            "Malicious cables (\"O.MG cable\" class) can inject keystrokes or "
            "exfiltrate data. Treat unknown cables exactly like unknown USB."
        ),
        "red_flags": "Unattended hardware; public location; convenience pressure.",
        "learning_tip": "Carry your own cable; treat strangers' hardware as hostile.",
    },

    # ────────── SOCIAL ENGINEERING ──────────
    {
        "title": "Urgent gift-card request from \"the CEO\"",
        "content": (
            "A WhatsApp message from a number claiming to be the CEO asks you "
            "to urgently buy five gift cards for a client surprise and send "
            "the codes back without telling anyone in finance."
        ),
        "category": "social_engineering", "difficulty": 2, "correct_answer": "C",
        "option_a": "Buy the cards immediately because the CEO sounds rushed.",
        "option_b": "Reply to clarify which client team the cards are intended for.",
        "option_c": "Verify by calling the CEO on a number you already know.",
        "option_d": "Forward the request to the CFO without any verification call.",
        "explanation": (
            "Authority + urgency + secrecy is the BEC gift-card scam. Always "
            "verify on a phone number you already trust before any spend."
        ),
        "red_flags": "Authority claim; secrecy demand; gift-card payment method.",
        "learning_tip": "Real executives are happy to be verified by a phone call.",
    },
    {
        "title": "New \"colleague\" on LinkedIn asking for org chart",
        "content": (
            "A new LinkedIn connection claiming to be a recently joined "
            "colleague asks you to share an internal org chart so they can "
            "settle in faster and find the right people to talk to."
        ),
        "category": "social_engineering", "difficulty": 2, "correct_answer": "A",
        "option_a": "Decline and direct them to HR for the official onboarding.",
        "option_b": "Share a partial chart that excludes only the leadership team.",
        "option_c": "Send the chart since onboarding always takes longer than expected.",
        "option_d": "Ask for their employee ID first before sharing the document.",
        "explanation": (
            "Org-chart harvesting fuels later spear-phishing. Onboarding is "
            "owned by HR, not by individual employees on social platforms."
        ),
        "red_flags": "External recon; insider-information request; LinkedIn pretext.",
        "learning_tip": "Internal documents stay internal, even for nice strangers.",
    },
    {
        "title": "Friendly contractor asking for a Wi-Fi password",
        "content": (
            "A contractor working on the office air-conditioning asks for the "
            "office Wi-Fi password so they can quickly download a manual that "
            "they say is needed to complete the repair today."
        ),
        "category": "social_engineering", "difficulty": 1, "correct_answer": "B",
        "option_a": "Share the password since contractors visit the building often.",
        "option_b": "Direct them to reception so the guest network can be enabled.",
        "option_c": "Give them the password but ask them to forget it after use.",
        "option_d": "Let them tether to your phone hotspot for a few minutes only.",
        "explanation": (
            "Internal Wi-Fi is part of the corporate network boundary. "
            "Guests use the guest network, provisioned through the proper desk."
        ),
        "red_flags": "Outsider on internal network; convenience excuse; trust appeal.",
        "learning_tip": "Guests get the guest network  never the staff one.",
    },

    # ────────── DATA HANDLING ──────────
    {
        "title": "Sending customer list to a personal email",
        "content": (
            "A vendor asks you to send a recent customer list to their "
            "personal Gmail address, explaining that their work mailbox is "
            "currently being slow and they need the file before lunch."
        ),
        "category": "data_handling", "difficulty": 2, "correct_answer": "D",
        "option_a": "Send it since the vendor is already a contracted partner.",
        "option_b": "Send it after compressing the file with a short shared password.",
        "option_c": "Upload it to a public link and send them the URL by email.",
        "option_d": "Refuse and use only the approved file-sharing channel for it.",
        "explanation": (
            "Personal email accounts are out-of-policy for any sensitive "
            "data. Convenient excuses are usually the actual red flag."
        ),
        "red_flags": "Personal email; convenience excuse; bypass of approved channel.",
        "learning_tip": "Sensitive data only ever travels through approved channels.",
    },
    {
        "title": "Photo of a whiteboard before a meeting",
        "content": (
            "Before a strategy meeting you take a quick mobile photo of a "
            "whiteboard full of customer names and revenue figures so you "
            "have a personal copy you can review later from home."
        ),
        "category": "data_handling", "difficulty": 1, "correct_answer": "A",
        "option_a": "Don't take the photo and use the official meeting notes instead.",
        "option_b": "Take it but store it only in your encrypted personal cloud.",
        "option_c": "Take it and delete the photo right after the meeting concludes.",
        "option_d": "Take it but blur the customer names before saving the image.",
        "explanation": (
            "Sensitive data on personal devices defeats every corporate "
            "control. Use the official notes that the company actually owns."
        ),
        "red_flags": "Sensitive data; personal device storage; bypassed retention.",
        "learning_tip": "If it's not in a corporate system, it shouldn't exist.",
    },
    {
        "title": "Disposing of an old work laptop",
        "content": (
            "Your old work laptop is being replaced and you need to dispose "
            "of the original device, which still contains historical work "
            "documents and locally cached customer information."
        ),
        "category": "data_handling", "difficulty": 2, "correct_answer": "B",
        "option_a": "Reformat the disk yourself and then drop it at a recycling centre.",
        "option_b": "Return it to IT for secure wipe and certified disposal handling.",
        "option_c": "Sell the device after deleting all the visible files manually.",
        "option_d": "Give it to a family member after running a quick factory reset.",
        "explanation": (
            "Reformat and \"factory reset\" do not reliably remove sensitive "
            "data. Certified secure disposal is the only safe answer here."
        ),
        "red_flags": "Residual data; informal disposal; unverified data destruction.",
        "learning_tip": "End-of-life hardware always goes back to IT, not the bin.",
    },
]


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        # Wipe attempts first (FK), then all existing scenarios. We are
        # rebuilding the question bank from scratch.
        attempt_n = Attempt.query.delete()
        scenario_n = Scenario.query.delete()
        db.session.commit()
        print(f"Cleared {scenario_n} scenarios and {attempt_n} attempts.")

        for sc in SCENARIOS:
            db.session.add(Scenario(
                title=sc["title"],
                content=sc["content"],
                question_type="mcq",
                category=sc["category"],
                difficulty=sc["difficulty"],
                target_roles="all",
                correct_answer=sc["correct_answer"],
                option_a=sc["option_a"],
                option_b=sc["option_b"],
                option_c=sc["option_c"],
                option_d=sc["option_d"],
                explanation=sc["explanation"],
                red_flags=sc["red_flags"],
                learning_tip=sc["learning_tip"],
                source="manual",
                is_active=True,
            ))
        db.session.commit()

        # Sanity check: report category distribution + option-length spread
        # so you can see at a glance that no question has wildly imbalanced
        # option lengths (which would leak the answer to the user).
        rows = Scenario.query.all()
        per_cat: dict[str, int] = {}
        worst_spread = 0
        worst_title = ""
        for s in rows:
            per_cat[s.category] = per_cat.get(s.category, 0) + 1
            lens = [len(s.option_a), len(s.option_b), len(s.option_c), len(s.option_d)]
            spread = max(lens) - min(lens)
            if spread > worst_spread:
                worst_spread = spread
                worst_title = s.title
        print(f"Seeded {len(rows)} scenarios across {len(per_cat)} categories.")
        for cat, n in sorted(per_cat.items()):
            print(f"  {cat:22s} {n}")
        print(f"Worst option-length spread: {worst_spread} chars ({worst_title!r})")


if __name__ == "__main__":
    main()
