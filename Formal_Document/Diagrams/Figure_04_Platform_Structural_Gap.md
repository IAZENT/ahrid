# Figure 4 — Structural Mismatch Between Existing Platforms and Kathmandu Valley SME Requirements

**Thesis placement:** Problem Context and Motivation section
**APA7 caption:**
> **Figure 4**
> *Structural Mismatch Between Existing Platforms and Kathmandu Valley SME Requirements*
> Note. SME = Small and Medium Enterprise. Checkmark = requirement met; X = requirement not met.

---

## Canva Design Spec

### Canvas size
A4 landscape, 1920 x 1080 px. White background.

### Layout: Comparison matrix table

```
+─────────────────────────────────────────────────────────────────────────────────+
|  PLATFORM CAPABILITY GAP ANALYSIS   (header bar — dark navy #1B2A4A)           |
+────────────────+──────────────+──────────────+──────────────+────────────────────+
|  REQUIREMENT   |  CybSafe     |  KnowBe4     |  Hoxhunt     |  AHRID             |
+────────────────+──────────────+──────────────+──────────────+────────────────────+
|  No enterprise |     X        |     X        |     X        |     ✓              |
|  licensing     |              |              |              |                    |
+────────────────+──────────────+──────────────+──────────────+────────────────────+
|  No dedicated  |     X        |     X        |     X        |     ✓              |
|  IT staff      |              |              |              |                    |
+────────────────+──────────────+──────────────+──────────────+────────────────────+
|  Nepal threat  |     X        |     X        |     X        |     ✓              |
|  context       |              |              |              |                    |
+────────────────+──────────────+──────────────+──────────────+────────────────────+
|  SHAP explainab|     X        |     X        |     X        |     ✓              |
|  ility         |              |              |              |                    |
+────────────────+──────────────+──────────────+──────────────+────────────────────+
|  Live OSINT    |     X        |     ~        |     X        |     ✓              |
|  integration   |              |              |              |                    |
+────────────────+──────────────+──────────────+──────────────+────────────────────+
|  Free tier     |     X        |     X        |     X        |     ✓              |
|  deployment    |              |              |              |                    |
+────────────────+──────────────+──────────────+──────────────+────────────────────+
```

### Detailed design instructions

**Header row:**
- Background: #1B2A4A (dark navy)
- Text: white, Montserrat Bold 18pt
- Columns: Requirement | CybSafe | KnowBe4 | Hoxhunt | AHRID

**Requirement column (leftmost):**
- Width: 30% of table
- Background: #F0F4F8 (very light grey)
- Text: Open Sans Regular 14pt, dark grey #2C3E50
- 6 rows:
  1. No enterprise licensing required
  2. No dedicated IT staff required
  3. Nepal / South Asia threat contextualisation
  4. SHAP per-prediction explainability
  5. Live OSINT threat feed integration
  6. Free-tier cloud deployment

**CybSafe, KnowBe4, Hoxhunt columns:**
- Width: 17% each
- Background: white
- Cell content: large X symbol, colour #C0392B (red), 28pt bold, centred
- Exception: KnowBe4 for OSINT row — use partial/yellow circle "~" symbol #F39C12

**AHRID column (rightmost):**
- Width: 19%
- Background: #E8F8F0 (very light green)
- Cell content: large checkmark ✓, colour #27AE60 (green), 28pt bold, centred
- Column header background: #27AE60 (green) with white text "AHRID"

**Row alternation:** Even rows background #FAFAFA, odd rows #FFFFFF

**Footer note below table:**
"< 15% of Nepali SMEs conduct any formal security training (IJMIR, 2025)"
Font: Open Sans Italic 11pt, grey #777777

### Colour palette
- Navy: #1B2A4A
- Red X: #C0392B
- Green check: #27AE60
- Orange partial: #F39C12
- Light green column: #E8F8F0
- Light grey req col: #F0F4F8
