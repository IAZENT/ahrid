"""Answer-option utilities (BSc scope: MCQ length balancing only).

Free-text helpers and the orchestrator-side correct-letter shuffler have
been removed; per-attempt MCQ shuffling now lives exclusively in
``app.services.option_shuffle`` (HMAC-signed presentation token).
"""
from __future__ import annotations

import random
import re

OPTION_KEYS = ("option_a", "option_b", "option_c", "option_d")
LETTERS = ("A", "B", "C", "D")
MAX_OPTION_CHARS = 220
MIN_OPTION_CHARS = 18
LENGTH_TOLERANCE = 0.25
MIN_MEANINGFUL_OPTION_CHARS = 12

_STUB_PATTERNS = (
    re.compile(r"^\s*$"),
    re.compile(r"^[\s.\-–—…]+$"),
    re.compile(r"^\s*(answer|option)\s*[a-d]?\s*$", re.I),
    re.compile(r"^\s*(n/?a|tbd|todo|placeholder|lorem|ipsum)\b", re.I),
    re.compile(r"\.{4,}"),
    re.compile(r"^answer\s*[—–-]", re.I),
)

_FILLER_PHRASES = (
    "after a quick think",
    "without checking the source",
    "as a precaution",
    "before doing anything else",
    "based on the situation described",
    "regardless of the sender",
    "because it feels urgent",
    "even though it looked normal",
    "to keep the workflow moving",
    "to be on the safe side",
)

_TRAILING_ELLIPSIS_RE = re.compile(r"[\s.…]*(?:\.{2,}|…)\s*$")


def _strip_trailing_ellipsis(text: str) -> str:
    if not text:
        return text
    cleaned = _TRAILING_ELLIPSIS_RE.sub("", text).rstrip()
    if cleaned == text:
        return text
    if not cleaned:
        return text
    if cleaned[-1] not in ".?!":
        cleaned += "."
    return cleaned


def _tidy(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", str(text)).strip()
    return _strip_trailing_ellipsis(text)


def _trim_to(text: str, target: int) -> str:
    if len(text) <= target:
        return text
    head = text[:target]
    for terminator in (". ", "? ", "! "):
        idx = head.rfind(terminator)
        if idx >= max(40, target // 2):
            return head[: idx + 1].rstrip()
    truncated = head.rsplit(" ", 1)[0].rstrip(",;:- ")
    if not truncated.endswith((".", "?", "!")):
        truncated += "."
    return truncated


def _pad_to(text: str, target: int, *, rng: random.Random) -> str:
    if len(text) >= target:
        return text
    if len(text.strip()) < MIN_MEANINGFUL_OPTION_CHARS:
        return text
    body = text.rstrip(".!?,;: ")
    needed = target - len(body)
    fillers: list[str] = []
    pool = list(_FILLER_PHRASES)
    rng.shuffle(pool)
    for filler in pool:
        if needed <= 4:
            break
        fillers.append(filler)
        needed -= len(filler) + 2
    extension = ", ".join(fillers)
    if extension:
        body = f"{body}, {extension}"
    if not body.endswith((".", "?", "!")):
        body += "."
    return body


def balance_answer_lengths(data: dict, *, rng: random.Random | None = None) -> dict:
    """Pad short distractors up toward the longest option."""
    rng = rng or random.Random()
    options = [_tidy(data.get(k, "")) for k in OPTION_KEYS]
    if not all(options[:2]):
        return data
    indices = [i for i, opt in enumerate(options) if opt]
    if len(indices) < 4:
        return data

    options = [_trim_to(opt, MAX_OPTION_CHARS) if opt else "" for opt in options]
    longest = max(len(options[i]) for i in indices)
    target = min(longest, MAX_OPTION_CHARS)
    target = max(target, MIN_OPTION_CHARS)
    lower = int(target * (1 - LENGTH_TOLERANCE))
    for i in indices:
        if len(options[i]) < lower:
            options[i] = _pad_to(options[i], lower, rng=rng)
    for k, v in zip(OPTION_KEYS, options):
        data[k] = v
    return data


def balance_options_for_display(data: dict, *, seed: str | int | None = None) -> dict:
    seed_val: int
    if seed is None:
        seed_val = 0
    elif isinstance(seed, int):
        seed_val = seed
    else:
        import hashlib
        seed_val = int.from_bytes(
            hashlib.sha1(str(seed).encode("utf-8")).digest()[:8], "big"
        )
    rng = random.Random(seed_val)
    balance_answer_lengths(data, rng=rng)
    return data


def is_option_stub(text: str | None, *, min_chars: int = MIN_MEANINGFUL_OPTION_CHARS) -> bool:
    if text is None:
        return True
    cleaned = _tidy(str(text))
    if not cleaned:
        return True
    for pattern in _STUB_PATTERNS:
        if pattern.search(cleaned):
            return True
    no_prefix = re.sub(
        r"^(answer|correct\s*answer|option\s*[a-d])\s*[:.\-—]\s*", "", cleaned, flags=re.I,
    )
    if len(no_prefix.strip()) < min_chars:
        return True
    return False


def validate_options(data: dict, *, question_type: str = "mcq") -> list[str]:
    qt = (question_type or "mcq").lower()
    if qt == "true_false":
        problems: list[str] = []
        for key in ("option_a", "option_b"):
            if is_option_stub(data.get(key), min_chars=1):
                problems.append(key)
        return problems
    if qt == "identify_threat":
        problems = []
        for key in OPTION_KEYS:
            if is_option_stub(data.get(key), min_chars=4):
                problems.append(key)
        return problems
    problems = []
    for key in OPTION_KEYS:
        if is_option_stub(data.get(key)):
            problems.append(key)
    return problems
