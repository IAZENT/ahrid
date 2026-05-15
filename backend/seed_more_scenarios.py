"""Bulk-generate ~500 length-balanced training scenarios.

Strategy:
  * Per category, define several "stems" (a scenario description with a
    `{situation}` placeholder) plus a fixed 4-option set whose strings are
    hand-tuned to the same length.
  * Substitute many distinct `situation` values to multiply each stem
    into many concrete scenarios. Because the answer options never
    change between substitutions, length-balance is preserved exactly.
  * After generation, every question is asserted to have an option-length
    spread of ≤ ``MAX_LEN_SPREAD`` characters (default 12). Anything that
    fails the assertion is dropped before insertion.

This file is **additive**: it does NOT wipe existing scenarios. Run after
``seed_scenarios.py`` to top up the question bank.

    python seed_more_scenarios.py
"""
from __future__ import annotations

import hashlib
import itertools
import random

from app import create_app
from app.extensions import db
from app.models.scenario import Scenario

MAX_LEN_SPREAD = 12          # max difference between longest and shortest option
LETTERS = ["A", "B", "C", "D"]
random.seed(42)              # reproducible insertion order


# ─── helpers ──────────────────────────────────────────────────────────

def _build(stem: str, situation: str, options4: list[str], correct_idx: int,
           explanation: str, red_flags: str, learning_tip: str,
           category: str, difficulty: int) -> dict | None:
    """Return a Scenario kwargs dict, or None if length-balance fails."""
    content = stem.format(situation=situation)
    lengths = [len(o) for o in options4]
    if max(lengths) - min(lengths) > MAX_LEN_SPREAD:
        return None

    # Place the correct option at a deterministic-but-spread position so
    # the answer letter distribution is balanced overall.
    h = int(hashlib.md5(content.encode()).hexdigest(), 16)
    placement = h % 4
    correct_text = options4[correct_idx]
    distractors = [o for i, o in enumerate(options4) if i != correct_idx]
    random.shuffle(distractors)
    final = list(distractors)
    final.insert(placement, correct_text)

    title = situation[:60].rstrip(".") if len(situation) > 4 else stem.split(".")[0][:60]

    return dict(
        title=title[:200],
        content=content,
        question_type="mcq",
        category=category,
        difficulty=difficulty,
        target_roles="all",
        correct_answer=LETTERS[placement],
        option_a=final[0],
        option_b=final[1],
        option_c=final[2],
        option_d=final[3],
        explanation=explanation,
        red_flags=red_flags,
        learning_tip=learning_tip,
        source="manual",
        is_active=True,
    )


# ─── PHISHING EMAIL ───────────────────────────────────────────────────
PHISHING_OPTIONS = [
    # (correct_idx, options[4], explanation, red_flags, learning_tip)
    (
        0,
        [
            "Open the brand's site directly and confirm any alert there.",
            "Click the embedded link to resolve the issue immediately.",
            "Reply to the email asking the sender to confirm details.",
            "Forward the email to colleagues so they avoid the same lure.",
        ],
        "Embedded links in unexpected emails are a textbook credential trap.",
        "Unfamiliar sender; urgent verification request; embedded link.",
        "Verify by typing the address into your browser yourself.",
    ),
    (
        1,
        [
            "Pay it after compressing the file with a temporary password.",
            "Stop and verify the request through a known phone contact.",
            "Forward to finance and assume they will validate the file.",
            "Reply asking the sender to send a clearer copy of the file.",
        ],
        "Invoice scams rely on near-miss supplier identities.",
        "Unexpected invoice; pay-link in email; near-miss sender domain.",
        "Verify any payment request out-of-band before acting.",
    ),
    (
        2,
        [
            "Reply to clarify which department the request belongs to.",
            "Comply quickly so the apparent deadline is not missed.",
            "Pause and confirm the request via a known internal channel.",
            "Forward the request to a teammate without verification.",
        ],
        "Authority + urgency is a classic spear-phishing combo.",
        "Authority claim; urgency pressure; channel mismatch.",
        "Real leaders are happy to be verified before any action.",
    ),
]
PHISHING_STEMS = [
    "An email about {situation} arrives from a sender you do not recognise.",
    "An email claims to be from IT about {situation} and includes a verify link.",
    "A vendor email mentions {situation} and asks you to click a button.",
    "An email purporting to be from HR concerns {situation} on a new portal.",
    "A finance-styled email about {situation} attaches an HTML form to fill in.",
    "An apparent partner email about {situation} asks for your login again.",
]
PHISHING_SITUATIONS = [
    "a security alert on your account",
    "an unpaid invoice from last month",
    "an urgent benefits enrolment update",
    "a suspended mailbox warning",
    "a delayed payroll re-confirmation",
    "an expired single sign-on session",
    "a pending document that needs review",
    "a refund that is awaiting your approval",
    "a Microsoft 365 storage limit notice",
    "a mandatory password rotation reminder",
    "an unusual sign-in from a new device",
    "a shared file from outside the company",
    "a one-time access link expiring soon",
    "a vendor purchase order awaiting reply",
    "a printer-job receipt sent by email",
    "a calendar invite from a new partner",
    "a missed voicemail from a Teams call",
    "a quarterly performance-review survey",
]

# ─── SMISHING ─────────────────────────────────────────────────────────
SMISHING_OPTIONS = [
    (
        2,
        [
            "Tap the link and confirm details so access is restored fast.",
            "Reply STOP so the sender stops sending the alerts to you.",
            "Ignore the text and verify directly via the official app.",
            "Forward the text to friends so they all avoid the same lure.",
        ],
        "Banks and couriers never restore access via SMS links.",
        "Lookalike domain; tight deadline; unsolicited SMS link.",
        "Phone the number on your card, never the one in the text.",
    ),
    (
        1,
        [
            "Reply with your account number so the refund clears today.",
            "Delete the text and verify directly on the official site.",
            "Tap the link and enter details so the refund is processed.",
            "Share the SMS with colleagues who may also have a refund.",
        ],
        "Tax authorities never collect bank details via SMS.",
        "Unsolicited refund offer; bank-detail request; SMS link.",
        "Government services only use their official portal.",
    ),
    (
        3,
        [
            "Forward the code to help your colleague get back to work.",
            "Reply asking which system the locked account belongs to.",
            "Send the code only after the colleague replies with thanks.",
            "Refuse and confirm with the colleague through a known channel.",
        ],
        "Sharing 2FA codes is never legitimate.",
        "Code-forwarding request; urgency; impersonated colleague.",
        "Treat one-time codes like passwords — never share them.",
    ),
]
SMISHING_STEMS = [
    "An SMS about {situation} arrives from an unknown short code.",
    "A text claiming to be from a courier mentions {situation} with a link.",
    "A WhatsApp message mentions {situation} and asks for confirmation.",
    "A Viber message about {situation} includes a payment link to tap.",
    "A text supposedly from your bank mentions {situation} urgently.",
]
SMISHING_SITUATIONS = [
    "a card that has been temporarily blocked",
    "a parcel held at customs awaiting a fee",
    "a tax refund that is ready to release",
    "an account that requires re-verification",
    "a missed delivery that needs rebooking",
    "a one-time code your colleague needs",
    "a banking session that is about to expire",
    "a loyalty reward that is about to lapse",
    "a utility bill that appears overdue",
    "a wallet top-up that is pending approval",
    "a scheduled video appointment update",
    "a free voucher that needs claiming today",
    "a security alert about your debit card",
    "a courier slot that needs rescheduling",
    "a pension statement that is now ready",
    "an overdue toll fee that needs payment",
    "a streaming subscription about to lapse",
    "a charity donation receipt to confirm",
]

# ─── VISHING ──────────────────────────────────────────────────────────
VISHING_OPTIONS = [
    (
        1,
        [
            "Provide the password so the patch can be applied on time.",
            "Decline and call IT back using your saved company number.",
            "Read out only part of the password to be slightly safer.",
            "Ask their badge number and continue the call as normal.",
        ],
        "Real IT teams never request your password by phone.",
        "Inbound caller; password request; manufactured urgency.",
        "Hang up and call IT back on the official number.",
    ),
    (
        3,
        [
            "Read the card number so the fraud team can block charges.",
            "Confirm only the expiry date to avoid handing over too much.",
            "Provide the CVV instead of the full card number for safety.",
            "Hang up and call the bank using the number on your card.",
        ],
        "Real fraud teams already have your account details.",
        "Inbound call; card-number request; fake authority claim.",
        "Banks call to alert, never to harvest card numbers.",
    ),
    (
        0,
        [
            "Delete the voicemail and report the number to your IT team.",
            "Press 1 and listen to the officer to learn what is wrong.",
            "Call the number back later to clarify the alleged charges.",
            "Reply to the message so the case officer can verify you.",
        ],
        "Courts and police never serve legal notices via voicemails.",
        "Robotic voice; legal threat; press-1 callback prompt.",
        "Authority scams disappear the moment you stop engaging.",
    ),
]
VISHING_STEMS = [
    "A caller about {situation} insists on action before end of day.",
    "A robotic voicemail about {situation} asks you to press a number.",
    "A caller claiming to be tech support describes {situation} on your PC.",
    "An inbound call about {situation} requests sensitive details.",
    "A foreign-number call mentions {situation} and presses for a reply.",
]
VISHING_SITUATIONS = [
    "an urgent account-lockout warning",
    "a suspicious overseas card transaction",
    "a court-case threat against your name",
    "a mandatory remote-support session",
    "a system upgrade that requires access",
    "a card-fraud verification step",
    "a regulator-style data request",
    "a refund of a duplicate payment",
    "a customer-service satisfaction survey",
    "a banking-OTP confirmation step",
    "a delayed pension disbursement",
    "an unpaid mobile-tariff balance",
    "an apparent insurance-claim review",
    "a delivery-driver routing question",
    "a follow-up about a vendor invoice",
    "an HR-styled background-check call",
    "a parcel-customs payment request",
    "a software-licence renewal nudge",
]

# ─── PHYSICAL SECURITY ────────────────────────────────────────────────
PHY_OPTIONS = [
    (
        2,
        [
            "Swipe them through so they can attend the meeting on time.",
            "Let them in but stay nearby to keep things looking normal.",
            "Ask them to wait while reception verifies their identity.",
            "Hold the door open since they look like a legitimate guest.",
        ],
        "Tailgating bypasses every digital control.",
        "Unknown person; convenient excuse; pressure to be polite.",
        "Polite redirection to reception is always the safe answer.",
    ),
    (
        1,
        [
            "Leave it as it is; the colleague is responsible for it.",
            "Lock the screen and tell the colleague when they return.",
            "Move the laptop to your desk so it stays nearby and safe.",
            "Take a quick picture as a reminder for the colleague later.",
        ],
        "Unlocked devices are an open door for any passer-by.",
        "Unattended device; unlocked screen; shared meeting space.",
        "If you wouldn't leave your wallet, don't leave your laptop.",
    ),
    (
        3,
        [
            "Leave the stack on the printer for the owner to find later.",
            "Take it back to your desk and try to identify the author.",
            "Throw the stack into the nearest open recycling bin promptly.",
            "Bring it to HR or the security team for proper handling.",
        ],
        "Confidential printouts must be controlled, not left in the open.",
        "Confidential label; uncollected printout; unattended area.",
        "Sensitive paper belongs in a controlled hand, not the tray.",
    ),
]
PHY_STEMS = [
    "You notice {situation} in a part of the office where it doesn't belong.",
    "While walking past a meeting room you observe {situation} unattended.",
    "At the secure entrance you encounter {situation} requiring a decision.",
    "On the shared printer you find {situation} that was never collected.",
    "In the lift lobby you spot {situation} and need to choose how to react.",
]
PHY_SITUATIONS = [
    "a stranger asking to be let through a secure door",
    "an unlocked laptop showing customer details on screen",
    "a stack of papers labelled confidential and unattended",
    "an unknown delivery person without a visible badge",
    "a smartphone unlocked next to a colleague's empty seat",
    "a guest wandering an area meant only for staff use",
    "a portable hard drive plugged into a public terminal",
    "a notebook left open with passwords scribbled inside",
    "a contractor lingering near the server-room door",
    "a printed payslip lying in the recycling bin lid",
    "a building visitor with an expired guest badge",
    "an after-hours stranger asking to charge their phone",
    "a delivery box obstructing the secure-door sensor",
    "a courier insisting on bypassing the visitor desk",
    "a webcam covered with masking tape on a hot desk",
    "a meeting badge clipped to an unknown handbag",
    "an open access panel near the staff entrance",
    "a tripod set up unattended outside reception",
]

# ─── PASSWORD HYGIENE ─────────────────────────────────────────────────
PWD_OPTIONS = [
    (
        2,
        [
            "Share it once since the teammate is trusted and in a hurry.",
            "Share it but change the password right after they finish.",
            "Refuse and offer to submit the report on the teammate's behalf.",
            "Write it on a sticky note so they can use it discreetly.",
        ],
        "Account ownership is non-transferable.",
        "Password-sharing pressure; deadline urgency; trust appeal.",
        "Your password identifies you, never anyone else.",
    ),
    (
        0,
        [
            "Use a password manager to generate a unique one per site.",
            "Reuse it because the password itself is genuinely strong.",
            "Reuse it but tweak the last two characters for each site.",
            "Keep one for work, and reuse another one everywhere else.",
        ],
        "Credential-stuffing relies entirely on password reuse.",
        "Reuse temptation; \"strong enough\" excuse; cross-account risk.",
        "Unique passwords + a manager defeats credential-stuffing.",
    ),
    (
        1,
        [
            "Save it because the browser will encrypt it before storing.",
            "Decline and ensure you sign out fully when leaving the device.",
            "Save it but only for the rest of the day to limit exposure.",
            "Save it and clear the saved entry yourself before leaving.",
        ],
        "Shared machines must never retain credentials.",
        "Shared device; persistent credential storage; convenience prompt.",
        "On shared machines, save nothing and sign out cleanly.",
    ),
]
PWD_STEMS = [
    "A teammate asks about {situation} and wants you to help bypass a control.",
    "You are tempted to take a shortcut around {situation} for convenience.",
    "On a shared workstation you face a prompt about {situation}.",
    "During a busy deadline you weigh up {situation} versus normal procedure.",
    "On a personal device you reconsider {situation} after a recent breach.",
]
PWD_SITUATIONS = [
    "sharing your account password with a teammate",
    "reusing one strong password across many sites",
    "saving a work password in a shared browser",
    "writing a password on a sticky note for now",
    "using your name plus a year as a password",
    "skipping multi-factor authentication for speed",
    "disabling the password expiry policy at work",
    "sending a password by email to a contractor",
    "auto-filling a password on an unknown WiFi",
    "letting a friend use your unlocked laptop",
    "keeping one master password in a text file",
    "reusing a personal password on a work portal",
    "saving a banking password in a notes app",
    "sharing the office Wi-Fi password by email",
    "using a child's name as a memorable secret",
    "keeping the same PIN for every smart device",
    "posting a login screenshot in a chat group",
    "using browser auto-save on a hotel laptop",
]

# ─── USB BAITING ──────────────────────────────────────────────────────
USB_OPTIONS = [
    (
        1,
        [
            "Plug it into your work laptop to grab the slides quickly.",
            "Ask the vendor for an online download link instead of using it.",
            "Plug it into a personal laptop first to keep work isolated.",
            "Give it to a colleague who has not yet collected one.",
        ],
        "Branded USBs have shipped with malware in real incidents.",
        "Unverified hardware; mass giveaway; convenience offer.",
        "When a link works, never choose the USB instead.",
    ),
    (
        2,
        [
            "Plug it into your laptop to look for an owner identity file.",
            "Leave it where it is; the owner will probably come back soon.",
            "Hand it to IT or security and let them decide what to do.",
            "Drop it in a recycling bin to make sure no one uses it.",
        ],
        "USB drops are a low-cost initial-access vector.",
        "Unknown device; convenient drop location; unlabelled stick.",
        "Unknown USB ⇒ not your problem to plug in, only to report.",
    ),
    (
        3,
        [
            "Use it briefly since the cable cannot really transfer data.",
            "Use it but only with the phone screen locked the entire time.",
            "Plug it into a power bank first, then charge the phone from it.",
            "Avoid it and use your own cable with a wall socket adapter.",
        ],
        "Malicious cables can inject keystrokes or exfiltrate data.",
        "Unattended hardware; public location; convenience pressure.",
        "Carry your own cable; treat strangers' hardware as hostile.",
    ),
]
USB_STEMS = [
    "You come across {situation} and you are tempted to use it right away.",
    "At a public area you find {situation} apparently abandoned by someone.",
    "Someone hands you {situation} and insists you should try it first.",
    "Near your desk you discover {situation} with no clear owner attached.",
    "Travelling for work you encounter {situation} at a charging station.",
]
USB_SITUATIONS = [
    "an unlabelled USB stick on the office floor",
    "a branded USB drive given out at a vendor stall",
    "a USB-C cable left at an airport charging point",
    "a memory card found in a meeting-room chair",
    "a USB stick in the staff toilet near the sink",
    "a microSD adaptor on the parking-area pavement",
    "a USB stick taped to a flyer in the lift lobby",
    "a card-reader dongle left next to your keyboard",
    "a USB hub left on a hot-desking workstation",
    "an external SSD with no label found at reception",
    "a charging cable taped to a bench in the canteen",
    "a tiny USB stick disguised as a key-chain ornament",
    "a USB drive labelled bonus details near payroll",
    "a wireless keyboard dongle on a guest workstation",
    "a power bank with mystery cables in the cafeteria",
    "a USB cable left dangling from the boardroom HDMI",
    "a flash drive in an envelope addressed to no one",
    "a smart-watch charging puck on the canteen table",
]

# ─── SOCIAL ENGINEERING ───────────────────────────────────────────────
SOC_OPTIONS = [
    (
        2,
        [
            "Buy the cards immediately because the CEO sounds rushed.",
            "Reply to clarify which client team the cards are intended for.",
            "Verify by calling the CEO on a number you already know.",
            "Forward the request to the CFO without any verification call.",
        ],
        "Authority + urgency + secrecy is the BEC gift-card scam.",
        "Authority claim; secrecy demand; gift-card payment method.",
        "Real executives are happy to be verified by a phone call.",
    ),
    (
        0,
        [
            "Decline and direct them to HR for the official onboarding.",
            "Share a partial chart that excludes only the leadership team.",
            "Send the chart since onboarding always takes longer expected.",
            "Ask for their employee ID first before sharing the document.",
        ],
        "Org-chart harvesting fuels later spear-phishing.",
        "External recon; insider-information request; LinkedIn pretext.",
        "Internal documents stay internal, even for nice strangers.",
    ),
    (
        1,
        [
            "Share the password since contractors visit the building often.",
            "Direct them to reception so the guest network can be enabled.",
            "Give them the password but ask them to forget it after use.",
            "Let them tether to your phone hotspot for a few minutes only.",
        ],
        "Internal Wi-Fi is part of the corporate network boundary.",
        "Outsider on internal network; convenience excuse; trust appeal.",
        "Guests get the guest network — never the staff one.",
    ),
]
SOC_STEMS = [
    "A message about {situation} arrives via an unexpected channel and presses you to act.",
    "Someone you don't know asks for {situation} citing time pressure.",
    "A new contact requests {situation} claiming it will speed up onboarding.",
    "A self-described senior leader asks for {situation} via a personal number.",
    "An apparent contractor needs {situation} to finish a routine task today.",
]
SOC_SITUATIONS = [
    "an urgent purchase of multiple gift cards",
    "a copy of the internal organisation chart",
    "the office Wi-Fi password for a manual",
    "a list of key staff phone-extension numbers",
    "a sample of the customer database for testing",
    "your manager's home phone number to confirm",
    "a copy of the latest sales pipeline summary",
    "a remote-access link into a finance system",
    "an emergency wire transfer to a new account",
    "a quick screenshot of the payroll dashboard",
    "a one-time code to unlock a meeting room",
    "a copy of the office floor plan diagram",
    "a brief summary of the company supplier list",
    "a quiet override on the leave-approval flow",
    "a courtesy note about the new finance system",
    "a peek at the upcoming campaign launch dates",
    "a temporary access pass for a building tour",
    "the staff roster for the upcoming weekend",
]

# ─── DATA HANDLING ────────────────────────────────────────────────────
DATA_OPTIONS = [
    (
        3,
        [
            "Send it since the vendor is already a contracted partner.",
            "Send it after compressing the file with a temporary password.",
            "Upload it to a public link and send them the URL by email.",
            "Refuse and use only the approved file-sharing channel for it.",
        ],
        "Personal email is out-of-policy for any sensitive data.",
        "Personal email; convenience excuse; bypass approved channel.",
        "Sensitive data only travels through approved channels.",
    ),
    (
        0,
        [
            "Don't take the photo and use the official meeting notes instead.",
            "Take it but store it only in your encrypted personal cloud.",
            "Take it and delete the photo right after the meeting concludes.",
            "Take it but blur the customer names before saving the image.",
        ],
        "Sensitive data on personal devices defeats every control.",
        "Sensitive data; personal device storage; bypassed retention.",
        "If it's not in a corporate system, it shouldn't exist.",
    ),
    (
        1,
        [
            "Reformat the disk yourself and drop it at a recycling centre.",
            "Return it to IT for secure wipe and certified disposal handling.",
            "Sell the device after deleting all the visible files manually.",
            "Give it to a family member after running a quick factory reset.",
        ],
        "Reformat does not reliably remove sensitive data.",
        "Residual data; informal disposal; unverified destruction.",
        "End-of-life hardware always goes back to IT, not the bin.",
    ),
]
DATA_STEMS = [
    "A request comes in to handle {situation} outside the approved channels.",
    "You are weighing whether to {situation} just for convenience this once.",
    "A vendor or contractor pressures you to {situation} for a tight deadline.",
    "Before a meeting you consider whether to {situation} to save later effort.",
    "While clearing your workspace you face a choice about {situation}.",
]
DATA_SITUATIONS = [
    "send a customer list to a personal email",
    "photograph a whiteboard full of revenue figures",
    "dispose of an old work laptop without IT help",
    "upload an HR spreadsheet to a free file-share",
    "store payroll data on an unencrypted USB drive",
    "share a strategy deck with a freelancer's Gmail",
    "print and take home a copy of the price-book",
    "save customer files in a personal cloud folder",
    "screenshot a contract for a personal portfolio",
    "share an exit-interview note in a group chat",
    "back up a sensitive folder to a free webmail",
    "move a confidential file to a personal SSD",
    "email a tax-return PDF to a colleague abroad",
    "forward a regulator letter to a personal inbox",
    "copy a salary spreadsheet onto a home machine",
    "share a partner contract via a public file link",
    "upload a board pack to a free transcription site",
    "text a screenshot of a vendor SOW to a friend",
]


# ─── per-category catalogue ───────────────────────────────────────────
CATEGORIES = [
    ("phishing_email",    PHISHING_STEMS, PHISHING_SITUATIONS, PHISHING_OPTIONS, [1, 2, 2]),
    ("smishing",          SMISHING_STEMS, SMISHING_SITUATIONS, SMISHING_OPTIONS, [1, 2, 2]),
    ("vishing",           VISHING_STEMS,  VISHING_SITUATIONS,  VISHING_OPTIONS,  [1, 2, 2]),
    ("physical_security", PHY_STEMS,      PHY_SITUATIONS,      PHY_OPTIONS,      [1, 1, 2]),
    ("password_hygiene",  PWD_STEMS,      PWD_SITUATIONS,      PWD_OPTIONS,      [1, 1, 2]),
    ("usb_baiting",       USB_STEMS,      USB_SITUATIONS,      USB_OPTIONS,      [1, 1, 2]),
    ("social_engineering",SOC_STEMS,      SOC_SITUATIONS,      SOC_OPTIONS,      [2, 2, 2]),
    ("data_handling",     DATA_STEMS,     DATA_SITUATIONS,     DATA_OPTIONS,     [2, 1, 2]),
]


def build_all() -> list[dict]:
    out: list[dict] = []
    for category, stems, situations, options_set, difficulties in CATEGORIES:
        # Cycle through option-sets so each combination uses a different
        # one. With 5 stems × 12 situations × 3 option-sets we get 180 raw
        # combinations per category; that is then capped below.
        combos = list(itertools.product(stems, situations, range(len(options_set))))
        for stem, situation, opt_idx in combos:
            correct_idx, options4, expl, red, tip = options_set[opt_idx]
            difficulty = difficulties[opt_idx % len(difficulties)]
            row = _build(
                stem=stem,
                situation=situation,
                options4=options4,
                correct_idx=correct_idx,
                explanation=expl,
                red_flags=red,
                learning_tip=tip,
                category=category,
                difficulty=difficulty,
            )
            if row is not None:
                out.append(row)
    return out


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        rows = build_all()
        # Cap at 500 cleanly per category share.
        per_cat: dict[str, list[dict]] = {}
        for r in rows:
            per_cat.setdefault(r["category"], []).append(r)
        per_cat_cap = 80                                # 8 × 80 = 640 max
        capped: list[dict] = []
        for cat, lst in per_cat.items():
            random.shuffle(lst)
            capped.extend(lst[:per_cat_cap])
        random.shuffle(capped)

        # Skip duplicates of titles already present.
        existing_titles = {t for (t,) in db.session.query(Scenario.title).all()}
        existing_contents = {c for (c,) in db.session.query(Scenario.content).all()}

        added = 0
        spreads: list[int] = []
        for r in capped:
            if r["content"] in existing_contents:
                continue
            # Auto-disambiguate title clashes by appending difficulty.
            base_title = r["title"]
            t = base_title
            n = 1
            while t in existing_titles:
                n += 1
                t = f"{base_title} ({n})"
            r["title"] = t
            existing_titles.add(t)
            existing_contents.add(r["content"])
            opts = [r["option_a"], r["option_b"], r["option_c"], r["option_d"]]
            spreads.append(max(len(o) for o in opts) - min(len(o) for o in opts))
            db.session.add(Scenario(**r))
            added += 1

        db.session.commit()

        per_cat_count = (
            db.session.query(Scenario.category, db.func.count(Scenario.id))
            .group_by(Scenario.category).all()
        )
        print(f"Inserted {added} new scenarios. Length-spread max={max(spreads or [0])} chars, "
              f"mean={(sum(spreads) / len(spreads)) if spreads else 0:.1f}.")
        for cat, n in sorted(per_cat_count):
            print(f"  {cat:22s} {n}")


if __name__ == "__main__":
    main()
