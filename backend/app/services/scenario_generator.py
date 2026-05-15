"""Rule-based threat-feed → Scenario converter.

Takes a ``ThreatFeedEntry`` plus the classifier output and produces a
fully-populated MCQ Scenario row. Pure templates; no LLM calls.
"""
from __future__ import annotations

import random
from urllib.parse import urlparse, urlunparse

from app.models.scenario import Scenario
from app.services.scenario_classifier import Classification

# Map lure_type → (title_template, prompt_template, correct_answer_text,
# distractor pool). Distractors are deliberately plausible so the
# question rewards reasoning, not pattern-matching on length.
_LURE_TEMPLATES: dict[str, dict] = {
    "credential_harvest": {
        "title": "Suspicious sign-in page from {brand}",
        "prompt": (
            "You receive a message asking you to verify your account at "
            "{url}. The page asks for your username and password. What is "
            "the safest action?"
        ),
        "correct": "Don't enter credentials. Verify by typing the brand's known address into the browser yourself.",
        "distractors": [
            "Enter the credentials — the URL looks close enough to the real site.",
            "Forward the link to a colleague to ask whether it's safe.",
            "Reply to the message to ask the sender for confirmation first.",
        ],
        "explanation": (
            "Credential-harvesting pages mimic real login screens to capture "
            "usernames and passwords. The only safe verification path is to "
            "navigate to the brand's known URL yourself and check there."
        ),
        "red_flags": "Unfamiliar host; urgency to verify; mismatched brand spelling.",
    },
    "invoice_fraud": {
        "title": "Unexpected invoice from {brand}",
        "prompt": (
            "An email attaches an unexpected invoice and asks you to pay via "
            "the link {url}. The amount and supplier look almost right. What "
            "should you do?"
        ),
        "correct": "Stop. Confirm with the supplier through a phone number you already have on file before paying.",
        "distractors": [
            "Pay it — invoices look legitimate and finance approves them later.",
            "Reply to the email asking the sender to resend a clearer copy.",
            "Forward it to your manager and assume they will validate it.",
        ],
        "explanation": (
            "Invoice fraud relies on near-miss supplier identities. Always "
            "verify payment requests through a side channel using contact "
            "details you already trust — never the ones in the email."
        ),
        "red_flags": "Unexpected invoice; pay-link in email; near-miss sender.",
    },
    "delivery_notification": {
        "title": "Parcel delivery notification",
        "prompt": (
            "You get an SMS / email saying a parcel is held at {url}. "
            "It asks for a small fee or address re-confirmation. What should "
            "you do?"
        ),
        "correct": "Don't click. Track the parcel via the courier's official site or app instead.",
        "distractors": [
            "Pay the fee — couriers do charge for redelivery sometimes.",
            "Reply with your address so the courier can re-attempt.",
            "Click the link to check what the parcel is.",
        ],
        "explanation": (
            "Delivery scams trade on the chance you really are expecting a "
            "parcel. Always go through the courier's official channel — "
            "never the link or number in the message."
        ),
        "red_flags": "Unsolicited courier ping; small fee request; shortened link.",
    },
    "it_support": {
        "title": "IT support warning",
        "prompt": (
            "A pop-up or email claiming to be IT says your account is at "
            "risk and tells you to act via {url}. What should you do?"
        ),
        "correct": "Ignore the link. Contact IT through the channel you already use to confirm.",
        "distractors": [
            "Follow the steps the message describes to fix the issue.",
            "Reply to the email asking IT for more detail first.",
            "Disable your antivirus so the IT tool can run.",
        ],
        "explanation": (
            "Fake IT-support lures bank on authority bias. Real IT will be "
            "reachable through your established channel — and they would "
            "never ask you to disable security tools."
        ),
        "red_flags": "Unsolicited IT ping; pressure to act; ask to disable security.",
    },
    "ceo_impersonation": {
        "title": "Urgent request from leadership",
        "prompt": (
            "You receive what looks like a message from a senior leader "
            "asking for an urgent wire transfer or confidential data via "
            "{url}. What should you do?"
        ),
        "correct": "Pause. Verify by calling the leader on a number you already have, not one in the message.",
        "distractors": [
            "Comply quickly — leadership requests are time-sensitive.",
            "Reply asking the leader to confirm by email.",
            "Forward the message to the leader's PA without verifying.",
        ],
        "explanation": (
            "CEO-fraud lures combine authority and urgency to bypass the "
            "usual checks. Always confirm sensitive requests through an "
            "existing trusted channel before acting."
        ),
        "red_flags": "Authority + urgency + confidentiality.",
    },
    "prize_scam": {
        "title": "You've won a prize!",
        "prompt": (
            "A message says you've been selected for a prize and to claim it "
            "at {url}. What should you do?"
        ),
        "correct": "Delete it. If you didn't enter, you didn't win — assume it's a scam.",
        "distractors": [
            "Click the link to claim the prize before it expires.",
            "Reply asking what the prize is.",
            "Share it with friends so they can also win.",
        ],
        "explanation": (
            "Prize scams use reward bias. If you didn't enter a draw you "
            "cannot win it; the link almost always leads to a credential "
            "or payment-detail capture page."
        ),
        "red_flags": "Unsolicited reward; urgent claim deadline.",
    },
}


def sanitise_url(url: str) -> str:
    """Return a defanged, *short* display copy of the URL.

    Strips query strings entirely and trims very long paths so the
    rendered question doesn't overflow the card. Replaces the scheme +
    dots so the user can't accidentally click the rendered text. The
    original URL is still kept on the ThreatFeedEntry for audit purposes.
    """
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        host = (parsed.netloc or parsed.path or "").replace(".", "[.]")
        scheme = (parsed.scheme or "http").replace("http", "hxxp")
        path = parsed.path if parsed.netloc else ""
        # Trim long paths so the question card stays readable. We keep
        # only the first segment + ellipsis if the path is long, and we
        # always drop the query string (it's noise for an end-user).
        if len(path) > 24:
            path = path[:24].rstrip("/") + "/…"
        defanged = urlunparse((scheme, host, path, "", "", ""))
        # Hard cap as a last line of defence against pathological inputs.
        if len(defanged) > 80:
            defanged = defanged[:80] + "…"
        return defanged
    except Exception:  # pragma: no cover
        return url.replace(".", "[.]").replace("http", "hxxp")[:80]


def _brand_from_url(url: str, fallback: str | None = None) -> str:
    if fallback:
        return fallback
    try:
        host = urlparse(url).netloc or url
        # naive: take the second-to-last component of the host
        parts = [p for p in host.split(".") if p]
        if len(parts) >= 2:
            return parts[-2].title()
        return host.title()
    except Exception:
        return "the sender"


def generate_scenario_from_entry(
    entry,
    sanitised_url: str,
    classification: Classification,
) -> Scenario:
    """Instantiate (but do NOT add/commit) a Scenario row for ``entry``."""
    template = _LURE_TEMPLATES.get(
        classification.lure_type, _LURE_TEMPLATES["credential_harvest"],
    )
    brand = _brand_from_url(entry.original_url, entry.target_brand)

    # Place correct answer in a uniformly chosen slot to defeat C-bias.
    letters = ["A", "B", "C", "D"]
    correct_letter = random.choice(letters)
    correct_idx = letters.index(correct_letter)

    distractors = list(template["distractors"])
    random.shuffle(distractors)
    options = list(distractors)
    options.insert(correct_idx, template["correct"])
    options = options[:4]

    title = template["title"].format(brand=brand)
    prompt = template["prompt"].format(brand=brand, url=sanitised_url)

    return Scenario(
        title=title[:200],
        content=prompt,
        question_type="mcq",
        category=classification.category,
        difficulty=classification.difficulty,
        target_roles=classification.target_roles,
        correct_answer=correct_letter,
        option_a=options[0],
        option_b=options[1],
        option_c=options[2],
        option_d=options[3],
        explanation=template["explanation"],
        red_flags=template["red_flags"],
        learning_tip="Verify any unexpected request through a channel you already trust.",
        source=entry.source,
        threat_url=entry.original_url[:2000],
        threat_brand=brand[:100],
        threat_feed_id=entry.id,
        is_active=True,
    )
