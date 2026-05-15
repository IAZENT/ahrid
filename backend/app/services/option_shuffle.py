"""Per-attempt MCQ option shuffling.

Why this exists
---------------
Even with read-time length balancing, a clever cheater who plays the same
scenario twice can spot that ``correct_answer`` is always letter "C" and
just smash C every time. We close that loophole by *shuffling option
positions on every fetch*, including the same user re-attempting the same
scenario in a brand-new session.

The shuffle is stateless: we ship the inverse permutation back to the
client inside an HMAC-signed token. On submit, the client echoes the
token along with the displayed letter; we verify the HMAC, decode the
permutation, translate the displayed letter back to the *original*
letter (the one stored in ``Scenario.correct_answer``), and grade.

This means:
* No DB schema change.
* No per-presentation row in any table.
* The token is unforgeable — without the server secret a user cannot
  re-map letters to game the answer.
* The token has a short TTL so a leaked token can't be replayed forever.

Format
------
    <base64url(json_payload)>.<base64url(hmac_sha256(key, payload))>

Payload::

    {
        "sid": "<scenario_uuid>",
        "p":   {"A": "C", "B": "A", "C": "D", "D": "B"},
        "exp": 1735689600
    }

``p`` maps **displayed letter → original letter**.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import random
import secrets
import time
from typing import Iterable

from flask import current_app

# Tokens expire 60 min after issue. Sessions are typically <30 min, so
# this is generous enough to absorb a slow user without letting a token
# be replayed days later.
TOKEN_TTL_SECONDS = 60 * 60

ORIGINAL_LETTERS = ("A", "B", "C", "D")


def _secret() -> bytes:
    key = current_app.config.get("SECRET_KEY") or "dev-shuffle-secret"
    return key.encode("utf-8") if isinstance(key, str) else bytes(key)


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64d(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _sign(payload: bytes) -> str:
    sig = hmac.new(_secret(), payload, hashlib.sha256).digest()
    return _b64e(sig)


def shuffle_options(
    scenario_id: str,
    options: dict[str, str],
    *,
    rng: random.Random | None = None,
) -> tuple[dict[str, str], str]:
    """Return (shuffled_options_dict, presentation_token).

    ``options`` is the ``{"A":..., "B":..., "C":..., "D":...}`` dict
    already produced by ``Scenario.to_public_dict`` (i.e. lengths already
    balanced). We permute it uniformly at random and emit a token the
    submit endpoint can use to translate displayed letter → original.
    """
    rng = rng or random.SystemRandom()
    originals = list(ORIGINAL_LETTERS)
    rng.shuffle(originals)

    # ``p`` = displayed_letter -> original_letter
    perm = {disp: orig for disp, orig in zip(ORIGINAL_LETTERS, originals)}
    shuffled = {disp: options[orig] for disp, orig in perm.items()}

    payload = {
        "sid": str(scenario_id),
        "p": perm,
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
        # Nonce so two tokens for the same scenario in the same second
        # still compare unequal — useful for server-side dedupe / logs.
        "n": secrets.token_urlsafe(6),
    }
    payload_b = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    token = f"{_b64e(payload_b)}.{_sign(payload_b)}"
    return shuffled, token


def decode_presentation_token(
    token: str,
    expected_scenario_id: str,
) -> dict[str, str] | None:
    """Verify HMAC + expiry + scenario binding. Return the perm dict, or None."""
    if not token or "." not in token:
        return None
    try:
        body_b64, sig_b64 = token.split(".", 1)
        payload = _b64d(body_b64)
    except (ValueError, TypeError):
        return None
    expected_sig = _sign(payload)
    if not hmac.compare_digest(expected_sig, sig_b64):
        return None
    try:
        data = json.loads(payload.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if data.get("sid") != str(expected_scenario_id):
        return None
    if int(data.get("exp", 0)) < int(time.time()):
        return None
    perm = data.get("p") or {}
    if set(perm.keys()) != set(ORIGINAL_LETTERS):
        return None
    if set(perm.values()) != set(ORIGINAL_LETTERS):
        return None
    return {str(k): str(v) for k, v in perm.items()}


def translate_displayed_to_original(
    displayed_letter: str,
    perm: dict[str, str] | None,
) -> str:
    """Map a user-submitted displayed letter back to the stored letter."""
    letter = (displayed_letter or "").strip().upper()[:1]
    if not perm:
        return letter
    return perm.get(letter, letter)


def attach_presentation(
    scenario_dict: dict,
    *,
    skip_question_types: Iterable[str] = ("short_answer", "descriptive", "fill_in_blank"),
) -> dict:
    """Mutate ``scenario_dict`` (output of ``to_public_dict``) in-place to
    apply per-attempt shuffling and length-balancing on the four MCQ options.

    Length-balancing is deterministic per scenario (seeded by scenario_id)
    so the *same* scenario always renders with the same option text — only
    the *positions* change between attempts. This keeps the question stable
    while still defeating positional cheating.

    Free-text scenarios are returned unchanged.
    """
    qtype = scenario_dict.get("question_type")
    if qtype in skip_question_types:
        return scenario_dict
    options = scenario_dict.get("options") or {}
    if set(options.keys()) != set(ORIGINAL_LETTERS):
        return scenario_dict  # malformed — leave alone

    # Stage 1 — pad short distractors up toward the longest so an
    # attentive user can't just pick the longest option and win.
    from app.services.answer_utils import balance_options_for_display

    keyed = {f"option_{k.lower()}": v for k, v in options.items()}
    balance_options_for_display(keyed, seed=scenario_dict.get("id"))
    balanced = {k.upper(): keyed[f"option_{k.lower()}"] for k in ORIGINAL_LETTERS}

    # Stage 2 — per-attempt position shuffle + signed token.
    shuffled, token = shuffle_options(scenario_dict["id"], balanced)
    scenario_dict["options"] = shuffled
    scenario_dict["presentation_token"] = token
    return scenario_dict
