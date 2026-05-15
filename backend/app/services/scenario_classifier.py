"""URL → (lure_type, category, difficulty) classification.

Pure functions; no I/O. Used by the threat ingestion pipeline (Stage 4) and
also exposed for ad-hoc testing via the admin API.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Lure detection
# ---------------------------------------------------------------------------
LURE_TYPE_PATTERNS: dict[str, tuple[str, ...]] = {
    "credential_harvest": (
        "login", "signin", "account", "verify", "password",
        "secure", "update", "confirm", "validate",
    ),
    "invoice_fraud": (
        "invoice", "payment", "billing", "receipt", "transaction",
        "order", "po-", "purchase-order",
    ),
    "delivery_notification": (
        "delivery", "parcel", "shipment", "dhl", "fedex",
        "ups", "usps", "track", "package",
    ),
    "it_support": (
        "microsoft", "google", "apple", "support", "help",
        "alert", "warning", "security", "teams",
    ),
    "ceo_impersonation": (
        "ceo", "director", "urgent", "wire", "transfer",
        "confidential", "board",
    ),
    "prize_scam": (
        "winner", "congratulation", "prize", "award", "selected",
        "reward", "claim",
    ),
}

BRAND_TO_CATEGORY: dict[str, str] = {
    "paypal": "credential_harvest",
    "microsoft": "credential_harvest",
    "google": "credential_harvest",
    "apple": "credential_harvest",
    "amazon": "credential_harvest",
    "netflix": "credential_harvest",
    "dhl": "delivery_notification",
    "fedex": "delivery_notification",
    "bank": "credential_harvest",
    "invoice": "invoice_fraud",
}

# Map our lure_type → AHRID scenario.category (8 categories defined in models).
#
# Each lure offers SEVERAL plausible categories; the final one is chosen
# deterministically from the URL hash so the *distribution* across the 8
# categories is roughly even. Previously every lure but two collapsed onto
# ``phishing_email``, which left the threat-feed pipeline pumping out 80%+
# phishing scenarios — fine for category 1, useless for the other seven.
LURE_TYPE_CATEGORY_OPTIONS: dict[str, tuple[str, ...]] = {
    "credential_harvest": ("phishing_email", "password_hygiene", "data_handling"),
    "invoice_fraud": ("phishing_email", "social_engineering", "data_handling"),
    "delivery_notification": ("smishing", "phishing_email"),
    "it_support": ("phishing_email", "social_engineering", "usb_baiting"),
    "ceo_impersonation": ("social_engineering", "vishing", "phishing_email"),
    "prize_scam": ("smishing", "phishing_email"),
}

# Legacy single-category mapping kept for callers that import it directly.
# Equivalent to picking the first option of each lure.
LURE_TYPE_TO_CATEGORY: dict[str, str] = {
    lure: opts[0] for lure, opts in LURE_TYPE_CATEGORY_OPTIONS.items()
}


def _category_for(lure: str, url: str) -> str:
    options = LURE_TYPE_CATEGORY_OPTIONS.get(lure, ("phishing_email",))
    if len(options) == 1:
        return options[0]
    digest = hashlib.sha1((url or "").encode("utf-8", "ignore")).digest()
    return options[digest[0] % len(options)]

# Map lure_type → comma-separated target_roles for Scenario.target_roles.
LURE_TYPE_TO_ROLES: dict[str, str] = {
    "credential_harvest": "all",
    "invoice_fraud": "accountant,finance",
    "delivery_notification": "all",
    "it_support": "it,management",
    "ceo_impersonation": "management,finance",
    "prize_scam": "all",
}

# Difficulty heuristics ------------------------------------------------------
FREE_HOSTING_TLDS = (".tk", ".ml", ".ga", ".cf")
FREE_HOSTING_HOSTS = ("blogspot", "weebly", "000webhost", "wixsite", "github.io")
KNOWN_BRANDS = (
    "paypal", "microsoft", "google", "apple", "amazon", "netflix",
    "facebook", "instagram", "twitter", "linkedin", "dhl", "fedex",
)
LEGIT_CLOUD_HOSTS = (
    "azurewebsites.net", "amazonaws.com", "s3.amazonaws.com",
    "firebaseapp.com", "web.app", "netlify.app", "vercel.app",
    "googleusercontent.com",
)
# Typosquats are spellings where ≥1 letter is replaced by a digit/symbol 
# the real brand spellings are deliberately excluded.
KNOWN_TYPOSQUATS = (
    "paypa1", "paypa0", "paypal!",
    "micros0ft", "micr0soft", "micr0s0ft",
    "g00gle", "g0ogle",
    "app1e", "amaz0n", "amaz00n",
    "netf1ix", "fac3book",
)


@dataclass(frozen=True)
class Classification:
    lure_type: str
    category: str
    difficulty: int
    target_roles: str
    xp_reward: int

    def to_dict(self) -> dict:
        return {
            "lure_type": self.lure_type,
            "category": self.category,
            "difficulty": self.difficulty,
            "target_roles": self.target_roles,
            "xp_reward": self.xp_reward,
        }


def _detect_lure_type(url: str, brand: str | None, context: str | None) -> str:
    haystack = " ".join(filter(None, (url, brand, context))).lower()
    # Score every lure type by how many of its tokens hit the haystack and
    # pick the highest scorer. The previous "first-match wins" loop biased
    # the output toward ``credential_harvest`` because its tokens (login,
    # account, verify) appear in nearly every phishing URL.
    scores: dict[str, int] = {}
    for lure, patterns in LURE_TYPE_PATTERNS.items():
        hits = sum(1 for token in patterns if token in haystack)
        if hits:
            scores[lure] = hits
    if scores:
        # Tiebreak by URL hash so two equally-strong lures don't always
        # collapse to the same one.
        best = max(scores.values())
        candidates = sorted(l for l, s in scores.items() if s == best)
        if len(candidates) == 1:
            return candidates[0]
        digest = hashlib.sha1((url or "").encode("utf-8", "ignore")).digest()
        return candidates[digest[1] % len(candidates)]
    if brand and brand.lower() in BRAND_TO_CATEGORY:
        return BRAND_TO_CATEGORY[brand.lower()]
    return "credential_harvest"  # safe default


def _detect_difficulty(url: str) -> int:
    parsed = urlparse(url if "://" in url else f"http://{url}")
    host = (parsed.hostname or "").lower()
    scheme = parsed.scheme

    # Difficulty 1  obvious
    if scheme != "https":
        return 1
    if host.endswith(FREE_HOSTING_TLDS):
        return 1
    if any(token in host for token in FREE_HOSTING_HOSTS):
        return 1
    if any(token in host for token in KNOWN_TYPOSQUATS):
        return 1

    # Difficulty 3  advanced
    parts = host.split(".")
    if len(parts) >= 3:
        # Subdomain attack: known brand appears in subdomain but not as registered domain
        for brand in KNOWN_BRANDS:
            if brand in parts[:-2]:
                return 3
    if any(host.endswith(legit) for legit in LEGIT_CLOUD_HOSTS):
        return 3  # compromised legit cloud
    try:
        host.encode("ascii")
    except UnicodeEncodeError:
        return 3  # IDN / homograph

    # Difficulty 2  subtle (anything else is "lookalike but plausible")
    if any(brand in host for brand in KNOWN_BRANDS) and not host.endswith(
        tuple(f"{b}.com" for b in KNOWN_BRANDS)
    ):
        return 2
    return 2


_XP_BY_DIFFICULTY = {1: 10, 2: 15, 3: 25}


def classify_url(
    url: str, brand: str | None = None, pulse_name: str | None = None
) -> Classification:
    """Return the full classification for a malicious URL."""
    lure = _detect_lure_type(url, brand, pulse_name)
    diff = _detect_difficulty(url)
    return Classification(
        lure_type=lure,
        category=_category_for(lure, url),
        difficulty=diff,
        target_roles=LURE_TYPE_TO_ROLES.get(lure, "all"),
        xp_reward=_XP_BY_DIFFICULTY[diff],
    )
