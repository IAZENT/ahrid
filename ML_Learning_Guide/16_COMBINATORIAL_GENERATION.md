# Chapter 16 - Scenario Design & Generation

> *"Quality over quantity"* - How AHRID's 450 hand-crafted scenarios deliver role-aware, length-balanced security training.

---

## The Challenge: Content Quality vs Quantity

In cybersecurity awareness training, the system needs many unique questions. But quantity without quality creates problems:

1. **Old approach (combinatorial):** Earlier versions multiplied stems × situations × option sets to generate 1,400+ scenarios automatically. The problem? ALL scenarios in a category shared the SAME option sets regardless of situation. A phishing email about a fake Ncell bill had the same answer choices as one about a fake job offer. Users noticed the pattern.

2. **New approach (hand-crafted):** 450 individually written scenarios where each story has unique, situation-specific answer options. Every option is length-balanced so users cannot guess by picking the longest answer.

---

## Design Principles

### 1. Length-Balanced Options

In multiple-choice questions, users often guess the longest answer, assuming it is the most detailed and therefore correct.

**Solution:** All 4 options must be within 12 characters of each other in length.

```python
MAX_SPREAD = 12  # max char difference between longest and shortest option

def _make(title, content, options, correct_idx, ...):
    lengths = [len(o) for o in options]
    spread = max(lengths) - min(lengths)
    if spread > MAX_SPREAD:
        return None  # Skip - options are too unbalanced
```

**Result:** 450 scenarios inserted, 0 with spread violations.

### 2. Deterministic Answer Placement (Hashing)

If the correct answer is always option "A", users will just guess "A". We use a hash of the content to deterministically place the correct answer:

```python
placement = hash(content + title) % 4
correct_text = options[correct_idx]
distractors = [o for i, o in enumerate(options) if i != correct_idx]
random.shuffle(distractors)
final = list(distractors)
final.insert(placement, correct_text)
```

The same question text always has the correct answer in the same position, ensuring consistency across database reseeds.

### 3. Nepal-Contextualized Content

All scenarios use local brands, services, and institutions:
- **Payment:** eSewa, Khalti, FonePay
- **Telecom:** Ncell, NTC, WorldLink
- **Delivery:** Pathao, Daraz, Foodmandu
- **Government:** IRD Nepal, Nepal Rastra Bank, NEA
- **Currency:** Nepali Rupees (Rs.)

### 4. Role-Based Targeting

Each scenario has a `target_roles` field. The Adaptive Engine prioritises role-relevant scenarios:

| Role | Example Scenario |
|------|-----------------|
| finance | Vendor bank account change, CEO wire transfer |
| hr | Candidate CV attachment, employee records |
| receptionist | Delivery person access, visitor badge |
| it | Server patch email, default passwords |
| sales | Client contract link, competitor strategy |
| management | Board meeting phishing, market research call |
| all | General phishing, password hygiene |

---

## Scenario Categories & Coverage

| Category | Count | Topics |
|----------|-------|--------|
| phishing_email | 76 | Fake bills, account locks, CEO fraud, deepfakes |
| data_handling | 60 | USB copies, public WiFi, shredding, cloud storage |
| smishing | 59 | OTP fraud, fake delivery, prize scams, QR codes |
| physical_security | 55 | Tailgating, server rooms, clean desk, badges |
| vishing | 54 | Bank calls, tech support, deepfake voice, census |
| password_hygiene | 53 | Reuse, managers, 2FA, browser save, service accounts |
| social_engineering | 53 | Gift cards, pretexting, dumpster diving, insider threats |
| usb_baiting | 40 | Found drives, charging stations, vendor USBs, rubber ducky |

**Difficulty distribution:** 156 beginner / 191 intermediate / 103 advanced

---

## The Data Pipeline

1. `seed_scenarios.py` wipes all existing scenarios and attempts
2. 8 category functions + 8 extra functions + 2 fill functions generate `_make()` calls
3. `_make()` validates length balance (≤12 char spread) and hashes answer placement
4. Valid scenarios are batch-inserted into the `Scenario` table
5. `seed_synthetic_ml_data.py` creates 1,050 synthetic users with attempts
6. `train_models.py` trains Random Forest + K-Means on the new data

**Pipeline command:**
```bash
python seed_scenarios.py          # 450 scenarios
python seed_synthetic_ml_data.py  # 1,050 users + 25,000+ attempts
python train_models.py            # RF accuracy=91.4%, F1=0.89
```

---

## ML Results After Scenario Redesign

| Metric | Value |
|--------|-------|
| Accuracy | 91.4% |
| F1 (macro) | 0.8878 |
| PR-AUC | 0.9166 |
| Cohen's Kappa | 0.8751 |
| Baseline F1 | 0.3653 |
| Gap over baseline | +0.5224 |
| KMeans silhouette | 0.268 |

---

> **Return to:** [Table of Contents](./00_TABLE_OF_CONTENTS.md)
