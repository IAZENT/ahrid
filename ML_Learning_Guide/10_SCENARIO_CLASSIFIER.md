# Chapter 10 - Scenario Classification: URL Intelligence

> When AHRID ingests a real phishing URL from threat feeds, it needs to automatically classify it into a lure type, difficulty level, and training category. This is **heuristic ML** - pattern matching rather than statistical learning.

---

## The Classification Pipeline

```
Raw phishing URL
       │
       ▼
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Lure Detection   │────►│ Category Mapping  │────►│ Difficulty Rating │
│ (keyword scoring)│     │ (hash-based)      │     │ (URL analysis)    │
└─────────────────┘     └──────────────────┘     └──────────────────┘
       │                        │                        │
       ▼                        ▼                        ▼
  credential_harvest      phishing_email                  2
  invoice_fraud           social_engineering              1 or 3
  delivery_notification   smishing                        etc.
  it_support              ...
  ceo_impersonation
  prize_scam
```

---

## Lure Type Detection

The system defines **6 lure types** with keyword patterns:

```python
LURE_TYPE_PATTERNS = {
    "credential_harvest": ("login", "signin", "account", "verify", "password", ...),
    "invoice_fraud":      ("invoice", "payment", "billing", "receipt", ...),
    "delivery_notification": ("delivery", "parcel", "shipment", "dhl", "fedex", ...),
    "it_support":         ("microsoft", "google", "apple", "support", ...),
    "ceo_impersonation":  ("ceo", "director", "urgent", "wire", "transfer", ...),
    "prize_scam":         ("winner", "congratulation", "prize", "award", ...),
}
```

### Scoring Algorithm

Instead of "first match wins" (which biased toward `credential_harvest`), the classifier **scores** every lure type:

```python
def _detect_lure_type(url, brand, context):
    haystack = " ".join(filter(None, (url, brand, context))).lower()
    
    scores = {}
    for lure, patterns in LURE_TYPE_PATTERNS.items():
        hits = sum(1 for token in patterns if token in haystack)
        if hits:
            scores[lure] = hits
    
    # Pick the highest scorer; break ties with URL hash
    best = max(scores.values())
    candidates = sorted(l for l, s in scores.items() if s == best)
    if len(candidates) == 1:
        return candidates[0]
    
    # Deterministic tiebreak using URL hash
    digest = hashlib.sha1(url.encode("utf-8", "ignore")).digest()
    return candidates[digest[1] % len(candidates)]
```

**Why hash-based tiebreaking?** It's **deterministic** - the same URL always gets the same classification. Random tiebreaking would mean re-running the pipeline could produce different results.

---

## Difficulty Rating

URL characteristics determine how "obvious" the phishing attempt is:

```python
def _detect_difficulty(url):
    parsed = urlparse(url)
    host = parsed.hostname.lower()
    
    # Difficulty 1 - Obvious
    if scheme != "https":                   return 1  # No HTTPS
    if host.endswith((".tk", ".ml", ".ga")): return 1  # Free hosting TLD
    if any(t in host for t in KNOWN_TYPOSQUATS): return 1  # paypa1.com
    
    # Difficulty 3 - Advanced
    if brand_in_subdomain_not_domain:       return 3  # paypal.evil.com
    if host_is_legit_cloud:                 return 3  # s3.amazonaws.com
    if has_unicode_chars:                   return 3  # homograph attack
    
    # Difficulty 2 - Subtle (everything else)
    return 2
```

### Examples

| URL | Difficulty | Reason |
|-----|-----------|--------|
| `http://paypa1.com/login` | 1 | HTTP + typosquat |
| `https://microsoft-verify.tk/secure` | 1 | Free hosting TLD |
| `https://secure-login.banking-corp.com` | 2 | Lookalike but plausible |
| `https://paypal.login.evil.com/verify` | 3 | Brand in subdomain |
| `https://storage.googleapis.com/phish` | 3 | Legit cloud hosting |

---

## Category Distribution

A key design decision: lure types map to **multiple** possible categories:

```python
LURE_TYPE_CATEGORY_OPTIONS = {
    "credential_harvest":     ("phishing_email", "password_hygiene", "data_handling"),
    "invoice_fraud":          ("phishing_email", "social_engineering", "data_handling"),
    "delivery_notification":  ("smishing", "phishing_email"),
    "it_support":             ("phishing_email", "social_engineering", "usb_baiting"),
    "ceo_impersonation":      ("social_engineering", "vishing", "phishing_email"),
    "prize_scam":             ("smishing", "phishing_email"),
}
```

The specific category is chosen deterministically from the URL hash:

```python
def _category_for(lure, url):
    options = LURE_TYPE_CATEGORY_OPTIONS.get(lure, ("phishing_email",))
    digest = hashlib.sha1(url.encode()).digest()
    return options[digest[0] % len(options)]
```

**Why spread across categories?** Without this, 80%+ of threat-feed scenarios would be `phishing_email` (since most URLs are email-based phishing). This hash-based distribution ensures all 8 categories get enriched by real-world threats.

---

## 🔬 Exercise

1. **Classify this URL:** `https://secure-paypa1.com/verify-account?urgent=true`
   - What's the lure type? (Look at keyword hits)
   - What's the difficulty? (Check the rules)
   - What category would it map to?

2. **Design question:** This system is entirely rule-based. How would you improve it with actual ML? (Hint: think about a text classifier trained on labelled phishing URLs)

---

> **Next:** [Chapter 11 - Behavioural Telemetry & Profiling →](./11_BEHAVIORAL_TELEMETRY.md)
