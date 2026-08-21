# AHRIP v2  Extension Phases 16-18
## Live Threat Intelligence Feed · Famous Breach Chronicle · Deep ML Personalization
### Sequential Prompts for Claude Opus 4  Appended to Master Build Document

---

> ## HOW THESE PHASES CONNECT TO THE MASTER BUILD
>
> These phases extend the AHRIP v2 build AFTER Phase 15 (Production Deployment) is complete.
> They add three high-impact features to the employee dashboard:
>
> 1. **PHASE 16**  Live Cyber News Feed (dynamic RSS + role-based filtering)
> 2. **PHASE 17**  Famous Breach Chronicle (Hall of Shame  curated + enriched)
> 3. **PHASE 18**  Deep ML Personalization Layer (behavioral telemetry → personalized questions)
>
> **Why these features matter for your SaaS:**
> - Employees who see real, current threats understand WHY training matters → higher engagement
> - Famous breaches provide emotional weight ("Equifax lost 147M people's data")
> - ML personalization reduces churn by serving questions users actually need → better outcomes
>
> **Efficiency note on news pulling:**
> Do NOT use heavy ML for the news feed. RSS aggregation + TF-IDF keyword scoring
> is faster, cheaper, deterministic, and works with zero training data.
> Save your ML budget for question personalization (Phase 18) where it pays off most.
>
> **Stack additions (append to requirements.txt):**
> ```
> feedparser==6.0.11        # RSS/Atom feed parsing
> scikit-learn==1.4.2       # already present  TF-IDF vectorizer
> sentence-transformers==3.0.1  # semantic similarity for Phase 18 (optional upgrade)
> ```

---

## PROGRESS TRACKER (Extension Phases)

```
[ ] PHASE 16.1   CyberNews DB Model + RSS Ingestion Service
[ ] PHASE 16.2   Role-Based News Relevance Scoring
[ ] PHASE 16.3   News Feed API Endpoints
[ ] PHASE 16.4   Frontend: LiveNewsTicker + CyberNewsFeed Component
[ ] PHASE 17.1   Famous Breaches DB Model + Seed Data (25 Breaches)
[ ] PHASE 17.2   Breach Chronicle API + AlienVault OTX Enrichment
[ ] PHASE 17.3   Frontend: BreachChronicle Component
[ ] PHASE 18.1   Behavioral Telemetry Schema + Tracking Service
[ ] PHASE 18.2   Thompson Sampling Question Selector
[ ] PHASE 18.3   Collaborative Filtering (Peer Weakness Signals)
[ ] PHASE 18.4   Personalized Weekly AI Insight Report
[ ] PHASE 18.5   Frontend: PersonalizationInsightCard Component
```

---
---

# PHASE 16  Live Cyber Intelligence News Feed

## Why RSS, Not ML, for News Pulling

Before writing any code, understand this architectural decision:

```
❌ WRONG APPROACH: Train an ML model to classify/summarize news
   → Requires labeled training data
   → Slow retraining cycle
   → Overkill for categorization
   → Expensive compute per article

✅ RIGHT APPROACH: RSS + TF-IDF keyword relevance scoring
   → Works immediately with zero training data
   → Deterministic and explainable
   → Runs in milliseconds per article
   → Scales to thousands of articles cheaply
   → Already in your stack (scikit-learn TfidfVectorizer)
```

The ML effort belongs in Phase 18 (question selection), not news pulling.

---

## PROMPT 16.1  CyberNews Model + RSS Ingestion Service

```xml
<role>
You are a senior backend engineer building a cyber threat intelligence aggregation pipeline.
You write production-quality Python with complete error handling. No placeholders.
</role>

<task>
Build the CyberNews database model and RSS ingestion service for AHRIP v2.
This pipeline fetches cybersecurity news every 4 hours, stores it, and tags
each article with which job roles it is most relevant to.
</task>

<new_model>
FILE: backend/app/models/cyber_news.py

CyberNews model fields:
- id: UUID primary key
- title: String(500) not null
- summary: Text nullable         (first 500 chars of article description)
- url: String(2000) not null unique
- source_name: String(100) not null  [e.g. "The Hacker News", "BleepingComputer"]
- source_feed: String(200) not null  (the RSS feed URL it came from)
- published_at: DateTime not null
- fetched_at: DateTime not null (server time when ingested)
- category_tags: String(500) default '[]'    (JSON list: ["phishing","ransomware"])
- role_relevance: String(500) default '{}'   (JSON dict: {"accountant": 0.87, "hr": 0.42})
- is_featured: Boolean default False          (editor pick  admin can feature)
- times_viewed: Integer default 0
- created_at: DateTime

Indexes: published_at DESC, source_name, is_featured

to_dict() returns: id, title, summary, url, source_name, published_at,
                   category_tags (parsed list), role_relevance (parsed dict),
                   is_featured, times_viewed

Add to backend/app/models/__init__.py imports.
Add flask db migrate + upgrade.
</new_model>

<rss_sources>
FILE: backend/app/services/cyber_news_ingestion.py

Define RSS_SOURCES dict at module top:
{
  "The Hacker News":   "https://feeds.feedburner.com/TheHackersNews",
  "BleepingComputer":  "https://www.bleepingcomputer.com/feed/",
  "Krebs on Security": "https://krebsonsecurity.com/feed/",
  "CISA Alerts":       "https://www.cisa.gov/uscert/ncas/alerts.xml",
  "Dark Reading":      "https://www.darkreading.com/rss/all.xml",
  "Naked Security":    "https://nakedsecurity.sophos.com/feed/"
}

CATEGORY_KEYWORDS dict (used for TF-IDF tagging):
{
  "phishing":           ["phishing", "spear-phishing", "credential", "fake email", "spoofed"],
  "ransomware":         ["ransomware", "ransom", "encrypted files", "lockbit", "conti"],
  "data_breach":        ["breach", "leaked", "exposed", "stolen data", "million records"],
  "social_engineering": ["social engineering", "pretexting", "impersonation", "vishing"],
  "malware":            ["malware", "trojan", "spyware", "keylogger", "botnet"],
  "vulnerability":      ["CVE", "zero-day", "patch", "exploit", "vulnerability"],
  "insider_threat":     ["insider threat", "employee", "privileged access", "sabotage"],
  "password":           ["password", "credential stuffing", "brute force", "MFA bypass"]
}

ROLE_KEYWORD_PROFILES dict (maps job roles to keywords they care about):
{
  "accountant":    ["invoice fraud", "wire transfer", "BEC", "financial", "payment", "tax"],
  "hr":            ["HR", "employee data", "payroll", "recruitment scam", "W-2"],
  "receptionist":  ["visitor", "tailgating", "front desk", "physical", "impersonation"],
  "it":            ["vulnerability", "CVE", "patch", "server", "network", "zero-day"],
  "finance":       ["wire fraud", "BEC", "SWIFT", "financial", "CFO fraud", "invoice"],
  "sales":         ["CRM", "customer data", "lead", "LinkedIn", "sales platform"],
  "management":    ["CEO fraud", "executive", "whaling", "board", "C-suite"],
  "other":         ["phishing", "malware", "breach", "scam", "fraud"]
}

Build these functions:

def fetch_all_feeds() -> list[dict]:
  """
  Uses feedparser to fetch all RSS_SOURCES.
  For each entry: extract title, summary (strip HTML tags with bleach),
  url (entry.link), published_at (parse entry.published with dateutil),
  source_name, source_feed.
  Deduplicate by URL against existing CyberNews records.
  Return list of raw article dicts. Skip entries older than 7 days.
  Error handling: if one feed fails, log warning and continue  never crash.
  """

def tag_categories(title: str, summary: str) -> list[str]:
  """
  Simple keyword matching  no ML needed here.
  Lowercases title+summary, checks each CATEGORY_KEYWORDS entry.
  Returns list of matched category strings. Max 3 categories per article.
  """

def score_role_relevance(title: str, summary: str) -> dict[str, float]:
  """
  For each role in ROLE_KEYWORD_PROFILES, count keyword hits in title+summary.
  Normalise to 0.0-1.0 range (hits / max_possible_hits for that role profile).
  Returns dict: {"accountant": 0.75, "hr": 0.20, ...}
  Minimum score 0.05 for every role (no article is completely irrelevant).
  """

def ingest_news() -> dict:
  """
  Main ingestion function called by scheduler.
  1. fetch_all_feeds()
  2. For each raw article: tag_categories() + score_role_relevance()
  3. Bulk insert new CyberNews records (skip duplicates by URL)
  4. Delete records older than 30 days (keep DB lean)
  5. Return {"fetched": N, "inserted": M, "skipped_duplicates": K, "errors": [...]}
  """
</rss_sources>

<scheduler_integration>
FILE: backend/app/services/scheduler.py (MODIFY existing file)

Add to existing scheduler setup:

from apscheduler.triggers.interval import IntervalTrigger
from .cyber_news_ingestion import ingest_news

scheduler.add_job(
  func=ingest_news,
  trigger=IntervalTrigger(hours=4),
  id='cyber_news_ingestion',
  name='Fetch cybersecurity news feeds',
  replace_existing=True,
  misfire_grace_time=300
)

Also add one-time startup fetch:
  scheduler.add_job(func=ingest_news, trigger='date', id='news_startup_fetch')
  (so the DB isn't empty on first deploy)
</scheduler_integration>

<requirements>
Append to backend/requirements.txt:
  feedparser==6.0.11
  python-dateutil==2.9.0  (if not already present)
</requirements>

After writing all code, run:
python -c "
from app import create_app
from app.services.cyber_news_ingestion import fetch_all_feeds, tag_categories, score_role_relevance
app = create_app()
with app.app_context():
    articles = fetch_all_feeds()
    print(f'Fetched: {len(articles)} articles')
    if articles:
        sample = articles[0]
        print('Categories:', tag_categories(sample['title'], sample.get('summary','')))
        print('Relevance:', score_role_relevance(sample['title'], sample.get('summary','')))
"
```

### ✅ PHASE 16.1 VERIFICATION
```
[ ] CyberNews model created with all fields
[ ] flask db upgrade runs clean
[ ] fetch_all_feeds() returns > 0 articles (live network check)
[ ] tag_categories() returns list (test with "Phishing attack targets banks")
[ ] score_role_relevance() returns dict with all 8 roles as keys
[ ] ingest_news() runs without crash
[ ] Scheduler adds cyber_news_ingestion job
[ ] feedparser added to requirements.txt
```

---

## PROMPT 16.2  News Feed API Endpoints

```xml
<role>Senior Flask API engineer. RESTful, paginated, role-aware endpoints.</role>

<task>
Build the cyber news API endpoints. Employees see news filtered by their job role.
Managers see all news with full role_relevance scores.
</task>

<new_file>
FILE: backend/app/api/cyber_news.py

Register blueprint: cyber_news_bp, url_prefix='/api/v1/news'

ENDPOINT 1: GET /api/v1/news/feed
  Auth required: JWT (employee or manager)
  Query params:
    limit: int default 10, max 50
    offset: int default 0
    category: str optional (filter by category_tag)
    featured_only: bool default false
  Logic:
    1. Get current_user.job_role from JWT
    2. Query CyberNews ordered by published_at DESC
    3. If category filter: filter where category_tags contains that category
    4. If featured_only: filter where is_featured=True
    5. Filter: only articles where role_relevance[user.job_role] >= 0.15
       (remove irrelevant articles for this role)
    6. Paginate: limit/offset
    7. Increment times_viewed for each returned article (bulk update)
  Response:
    {
      "articles": [CyberNews.to_dict(), ...],
      "total": N,
      "offset": 0,
      "limit": 10,
      "user_role": "accountant",
      "last_fetched": "ISO datetime of most recent article"
    }

ENDPOINT 2: GET /api/v1/news/featured
  Auth required: JWT
  Returns: top 3 featured articles + 2 highest role_relevance articles for user's role
  Purpose: Dashboard widget  5 items max, fast load
  Response: {"articles": [...], "role": "accountant"}

ENDPOINT 3: GET /api/v1/news/categories
  Auth required: JWT
  Returns: list of all category_tags present in DB with article count
  Response: [{"category": "phishing", "count": 34}, ...]

ENDPOINT 4: POST /api/v1/news/trigger-fetch   [ADMIN ONLY]
  Auth: JWT + admin role check
  Triggers ingest_news() synchronously
  Response: {"result": {"fetched": N, "inserted": M, "skipped": K}}

ENDPOINT 5: PATCH /api/v1/news/{article_id}/feature  [ADMIN ONLY]
  Toggles is_featured boolean
  Response: {"id": "...", "is_featured": true}
</new_file>

<registration>
FILE: backend/app/__init__.py (MODIFY)
Add: from .api.cyber_news import cyber_news_bp
     app.register_blueprint(cyber_news_bp)
</registration>
```

### ✅ PHASE 16.2 VERIFICATION
```
[ ] GET /api/v1/news/feed returns paginated articles for logged-in user's role
[ ] Role filtering works (accountant sees finance-relevant news)
[ ] GET /api/v1/news/featured returns max 5 articles
[ ] Admin trigger-fetch endpoint works
[ ] Non-admin blocked from admin endpoints (403)
[ ] times_viewed increments on fetch
```

---

## PROMPT 16.3  Frontend: Live News Feed Components

```xml
<role>
Senior React/TypeScript engineer. Dark enterprise UI. Tailwind CSS v4.
Use Framer Motion for animations. Follow the existing AHRIP v2 design system.
</role>

<task>
Build two frontend components for the cyber news feed:
1. LiveNewsTicker  scrolling headline bar at top of employee dashboard
2. CyberNewsFeed  full news card list (separate section of dashboard)
Both connect to the /api/v1/news/ endpoints built in Phase 16.2.
</task>

<component_1>
FILE: frontend/src/components/dashboard/LiveNewsTicker.tsx

Props: none (fetches its own data)

Behaviour:
- On mount: GET /api/v1/news/featured
- Display: horizontal auto-scrolling ticker bar (CSS animation, infinite loop)
  Each item: red pulsing dot + source_name + title (truncated 80 chars)
  Clicking an item opens the article URL in a new tab (rel="noopener noreferrer")
- Refresh interval: every 30 minutes (setInterval)
- Loading state: show skeleton shimmer bar
- Error state: hide bar silently (don't break dashboard layout)
- Design: dark background (#0D1117), red accent (#EF4444), white text, monospace font
  Height: 36px, full width
  Scroll speed: 40 seconds per loop
  Pause on hover (CSS: animation-play-state: paused)

Display format per item:
  🔴  [BleepingComputer]  New phishing campaign targets UK banking customers • 
  (bullet separator between items)
</component_1>

<component_2>
FILE: frontend/src/components/dashboard/CyberNewsFeed.tsx

Props:
  maxItems?: number (default 6)
  showCategories?: boolean (default true)
  compact?: boolean (default false)

Behaviour:
- On mount: GET /api/v1/news/feed?limit={maxItems}
- Display: card grid (2 columns on desktop, 1 on mobile)
  Each card contains:
    - Category badge (colour-coded: phishing=red, ransomware=orange, breach=yellow, etc.)
    - Source name + time ago (use date-fns formatDistanceToNow)
    - Title (bold, max 2 lines)
    - Summary (truncated to 120 chars, grey text)
    - "Read more →" link (opens in new tab)
    - Relevance bar: thin horizontal bar showing role_relevance score for user's role
      Label: "Relevant to your role: 87%"
  
- Category filter bar at top (if showCategories=true):
    Pills for each available category  clicking filters the feed
    "All" pill selected by default
    Filters call GET /api/v1/news/feed?category={selected} and re-renders
    
- Framer Motion: fade-in staggered animation for cards on load (stagger 0.08s)
- Loading: 6 skeleton cards
- Empty state: shield icon + "No recent threats for your role  check back soon"
- "Load more" button at bottom (increments offset by maxItems)
</component_2>

<api_integration>
FILE: frontend/src/api/news.ts (NEW FILE)

Add these typed API functions:

interface CyberNewsArticle {
  id: string
  title: string
  summary: string | null
  url: string
  source_name: string
  published_at: string
  category_tags: string[]
  role_relevance: Record<string, number>
  is_featured: boolean
  times_viewed: number
}

interface NewsFeedResponse {
  articles: CyberNewsArticle[]
  total: number
  offset: number
  limit: number
  user_role: string
  last_fetched: string
}

export const fetchNewsFeed = async (params?: {...}) => Promise<NewsFeedResponse>
export const fetchFeaturedNews = async () => Promise<{articles: CyberNewsArticle[], role: string}>
export const fetchNewsCategories = async () => Promise<{category: string, count: number}[]>
</api_integration>

<dashboard_integration>
FILE: frontend/src/pages/employee/TrainingPage.tsx (or the main employee dashboard)

Add LiveNewsTicker ABOVE the main content area (full width, before any padding)
Add CyberNewsFeed section BELOW the gamification widgets and BEFORE the scenario list:
  Section header: "⚠️ Live Threat Intelligence" with small "Updated every 4 hrs" badge
  CyberNewsFeed maxItems={6} showCategories={true}
</dashboard_integration>
```

### ✅ PHASE 16.3 VERIFICATION
```
[ ] LiveNewsTicker scrolls headlines, pauses on hover
[ ] Ticker auto-refreshes every 30 minutes
[ ] CyberNewsFeed shows role-relevant cards with category badges
[ ] Relevance bar visible on each card
[ ] Category filter pills work
[ ] Load more button paginates correctly
[ ] All external links open in new tab with noopener
[ ] Framer Motion stagger animation visible on load
[ ] Error/empty states render without breaking dashboard
[ ] Both components added to employee dashboard page
```

---
---

# PHASE 17  Famous Breach Chronicle (Hall of Shame)

## PROMPT 17.1  FamousBreach Model + Seed Data

```xml
<role>
Database architect + seed data engineer. You create production-quality
seed data representing real historical cybersecurity breaches.
All financial figures and record counts are real, publicly reported numbers.
</role>

<task>
Build the FamousBreach model and seed it with 25 of the most impactful
real-world cybersecurity breaches. This is the "Hall of Shame" shown to
employees to demonstrate what can happen if security lapses.
</task>

<model>
FILE: backend/app/models/famous_breach.py

FamousBreach model fields:
- id: UUID primary key
- company_name: String(200) not null
- industry: String(100) not null
- year: Integer not null
- month: Integer nullable
- breach_type: String(80) not null
  [phishing / ransomware / insider_threat / credential_stuffing /
   sql_injection / social_engineering / physical / supply_chain / unpatched_vuln]
- records_affected: BigInteger nullable       (number of people/records)
- estimated_cost_usd: BigInteger nullable     (total cost in USD)
- description: Text not null                  (2-3 sentences, factual)
- how_it_happened: Text not null              (technical but readable, 2-3 sentences)
- what_employees_could_have_done: Text not null  (1-2 sentences, actionable)
- severity: String(20) not null               [catastrophic / critical / severe / significant]
- otx_pulse_id: String(100) nullable          (AlienVault OTX pulse ID for enrichment)
- source_url: String(2000) nullable           (reference link)
- is_active: Boolean default True
- created_at: DateTime

to_dict() returns all fields except is_active, created_at

Add to models/__init__.py. Run flask db migrate + upgrade.
</model>

<seed_data>
FILE: backend/seed_breaches.py

Create 25 FamousBreach records. Use these EXACT real cases:

1. Yahoo (2013/2014)  3 billion accounts
   breach_type: credential_stuffing
   records_affected: 3000000000
   estimated_cost_usd: 350000000
   severity: catastrophic
   description: "Yahoo suffered the largest data breach in history, compromising
   all 3 billion user accounts. Stolen data included names, email addresses,
   dates of birth, telephone numbers, and hashed passwords."
   how_it_happened: "Attackers used a spear-phishing email to compromise a
   Yahoo employee, then moved laterally through internal systems to access
   the user database. The breach went undetected for 3 years."
   what_employees_could_have_done: "The initial compromise began with a single
   employee clicking a malicious link. Phishing awareness training could have
   prevented the entire breach."

2. Equifax (2017)  147 million records
   breach_type: unpatched_vuln
   records_affected: 147000000
   estimated_cost_usd: 1400000000
   severity: catastrophic
   description: "Credit reporting giant Equifax exposed sensitive financial data
   of 147 million Americans including Social Security numbers, birth dates,
   addresses, driver's licence numbers, and credit card details."
   how_it_happened: "Attackers exploited a known Apache Struts vulnerability
   (CVE-2017-5638) that had a patch available for 2 months. Equifax's IT team
   had failed to apply it, leaving the web portal exposed for 78 days."
   what_employees_could_have_done: "IT staff could have applied the available
   patch within days. Security teams should have detected the 78-day intrusion
   through monitoring."

3. Target (2013)  40 million credit cards
   breach_type: phishing
   records_affected: 40000000
   estimated_cost_usd: 292000000
   severity: catastrophic
   description: "Attackers stole 40 million credit and debit card records from
   Target during the 2013 holiday shopping season, affecting nearly every
   major US bank."
   how_it_happened: "Attackers stole credentials from Fazio Mechanical, a Target
   HVAC vendor, via a phishing email. Using those third-party credentials, they
   accessed Target's network and installed malware on POS systems."
   what_employees_could_have_done: "The vendor Fazio Mechanical fell for a
   phishing email. Better phishing awareness across the supply chain could
   have blocked the initial access vector."

4. WannaCry (2017)  200,000 systems, 150 countries
   breach_type: ransomware
   records_affected: 200000
   estimated_cost_usd: 4000000000
   severity: catastrophic
   description: "WannaCry ransomware infected 200,000 systems in 150 countries in
   a single day, encrypting files and demanding Bitcoin ransom. The NHS in the UK
   cancelled 19,000 appointments."
   how_it_happened: "WannaCry exploited EternalBlue, an NSA-developed exploit for
   unpatched Windows SMB vulnerabilities. Systems that had applied the March 2017
   Microsoft patch were immune."
   what_employees_could_have_done: "Employees on unpatched systems should have
   reported the lack of updates to IT. Recognising suspicious encrypted file
   extensions and immediately disconnecting from the network limits spread."

5. Sony Pictures (2014)  100TB of data
   breach_type: social_engineering
   records_affected: 47000
   estimated_cost_usd: 100000000
   severity: catastrophic
   description: "The Guardians of Peace hacking group, linked to North Korea,
   leaked 100 terabytes of Sony's confidential data including unreleased films,
   executive emails, salary information, and employee personal data."
   how_it_happened: "Attackers sent phishing emails to Sony employees using
   fake Apple ID verification requests. Stolen credentials gave them network
   access for months before the destructive payload was deployed."
   what_employees_could_have_done: "Several Sony employees received the initial
   phishing email. Recognising fake Apple ID emails and reporting them could
   have prevented the breach."

6. Colonial Pipeline (2021)  ransomware
   breach_type: ransomware
   records_affected: NULL
   estimated_cost_usd: 4400000
   severity: catastrophic
   description: "DarkSide ransomware attacked Colonial Pipeline, the operator of
   the largest US fuel pipeline, forcing a 6-day shutdown and fuel shortages
   across the eastern United States."
   how_it_happened: "Attackers gained access through a single compromised VPN
   password found on the dark web. The account had no multi-factor authentication
   enabled and was no longer in active use."
   what_employees_could_have_done: "The compromised password was reused from
   another breach. Password hygiene training and MFA awareness could have
   prevented access entirely."

7. NotPetya (2017)  global supply chain
   breach_type: supply_chain
   records_affected: NULL
   estimated_cost_usd: 10000000000
   severity: catastrophic
   description: "NotPetya was disguised as ransomware but was actually a
   destructive wiper. It spread through a compromised Ukrainian accounting
   software update, costing Maersk, FedEx, and Merck over $10 billion total."
   how_it_happened: "Attackers compromised the M.E.Doc accounting software's
   update server. Every company running the software received a malicious update
   that deployed the wiper on their network."
   what_employees_could_have_done: "Employees receiving unexpected software
   updates should verify authenticity with IT. Network segmentation awareness
   helps understand why not every device should trust every other device."

8. SolarWinds (2020)  US government supply chain
   breach_type: supply_chain
   records_affected: 18000
   estimated_cost_usd: 40000000000
   severity: catastrophic
   description: "Russian intelligence (SVR) inserted malicious code into
   SolarWinds Orion software updates, affecting 18,000 organisations including
   US Treasury, State Department, and Fortune 500 companies."
   how_it_happened: "Attackers compromised SolarWinds' build pipeline and inserted
   SUNBURST backdoor code into legitimate software updates. The malware lay dormant
   for 12 days to avoid sandbox detection before phoning home."
   what_employees_could_have_done: "Employees noticing unusual network traffic
   or unexpected system behaviour should report it immediately. Insider threat
   awareness helps identify supply chain anomalies."

9. Uber (2022)  social engineering
   breach_type: social_engineering
   records_affected: NULL
   estimated_cost_usd: NULL
   severity: critical
   description: "An 18-year-old attacker gained full access to Uber's internal
   systems including AWS, Google Cloud, Slack, and code repositories by tricking
   an employee into approving an MFA push notification."
   how_it_happened: "The attacker used MFA fatigue  bombarding an Uber contractor
   with push notifications until the employee approved one just to stop them.
   The attacker then found admin credentials in a PowerShell script on an
   internal wiki."
   what_employees_could_have_done: "Never approve MFA requests you did not
   initiate. If you receive unexpected push notifications, report to IT
   immediately  do not approve them."

10. Marriott / Starwood (2018)  500 million guests
    breach_type: unpatched_vuln
    records_affected: 500000000
    estimated_cost_usd: 124000000
    severity: catastrophic
    description: "The Starwood guest reservation database was breached, exposing
    records of up to 500 million guests including names, addresses, passport
    numbers, payment card details, and travel history."
    how_it_happened: "Attackers had access to Starwood's systems since 2014 
    4 years before Marriott acquired Starwood and discovered the breach.
    The attackers maintained persistence using a remote access trojan."
    what_employees_could_have_done: "Network behaviour monitoring and insider
    threat awareness could have caught 4 years of unauthorised data exfiltration.
    Employees should report any unexplained system access to security teams."

11. Twitter (2020)  130 high-profile accounts
    breach_type: social_engineering
    records_affected: 130
    estimated_cost_usd: NULL
    severity: severe
    description: "Attackers hijacked 130 high-profile Twitter accounts  including
    Barack Obama, Joe Biden, and Elon Musk  to run a Bitcoin scam that collected
    over $117,000 in hours."
    how_it_happened: "Attackers called Twitter employees pretending to be internal
    IT support, convincing them to reveal credentials to internal admin tools.
    Several employees provided access before the scam was discovered."
    what_employees_could_have_done: "Internal IT will never call asking for
    credentials. Employees should hang up and call back through official channels
    to verify caller identity."

12. Zoom (2020)  500,000 credentials
    breach_type: credential_stuffing
    records_affected: 500000
    estimated_cost_usd: NULL
    severity: significant
    description: "500,000 Zoom accounts were sold on dark web forums for less
    than a penny each, containing emails, passwords, meeting IDs, and host keys."
    how_it_happened: "Attackers used credential stuffing  testing billions of
    username/password combinations leaked from other breaches against Zoom.
    Users who reused passwords from breached sites were immediately compromised."
    what_employees_could_have_done: "Use a unique password for every service.
    A password manager makes this practical. Never reuse the same password
    across work and personal accounts."

13. RockYou2021  8.4 billion passwords
    breach_type: credential_stuffing
    records_affected: 8400000000
    estimated_cost_usd: NULL
    severity: catastrophic
    description: "The RockYou2021 compilation leaked 8.4 billion unique
    password combinations, the largest password database ever exposed.
    It was compiled from previous breaches and new leaked databases."
    how_it_happened: "The file was posted on a hacker forum as a compilation
    of all previously known leaked credentials plus new data. This is used
    in credential stuffing attacks against any service worldwide."
    what_employees_could_have_done: "Check if your email appears on
    HaveIBeenPwned.com. If it does, change that password everywhere it
    was used. Unique passwords per service are the only defence."

14. Ashley Madison (2015)  37 million users
    breach_type: insider_threat
    records_affected: 37000000
    estimated_cost_usd: 578000000
    severity: catastrophic
    description: "The dating site Ashley Madison was breached and the personal
    details of 37 million members were published online, causing suicides,
    divorces, and extortion campaigns."
    how_it_happened: "The Impact Team gained access via an insider and/or
    compromised credentials, then exfiltrated all user data. The site had
    claimed to offer permanent deletion of accounts for a fee  a lie that
    became central to the scandal."
    what_employees_could_have_done: "Insider threat indicators  a colleague
    accessing databases outside their job scope  should be reported.
    Least-privilege access controls limit what any one employee can export."

15. LinkedIn (2021)  700 million users
    breach_type: credential_stuffing
    records_affected: 700000000
    estimated_cost_usd: NULL
    severity: catastrophic
    description: "Data from 700 million LinkedIn users  92% of its user base 
    was scraped and offered for sale, including email addresses, phone numbers,
    workplace information, and geolocation data."
    how_it_happened: "Attackers used LinkedIn's API to scrape publicly available
    and semi-private profile data at scale. Combined with other breach data,
    this creates highly targeted phishing profiles."
    what_employees_could_have_done: "Limit what personal data you publish
    on professional networks. Attackers build detailed targeting profiles
    from LinkedIn data for spear-phishing attacks."

16. MGM Resorts (2023)  ransomware via vishing
    breach_type: social_engineering
    records_affected: NULL
    estimated_cost_usd: 100000000
    severity: catastrophic
    description: "The ALPHV/BlackCat ransomware group encrypted MGM Resorts'
    systems, costing $100M and disrupting hotel operations, slot machines,
    digital room keys, and ATMs across Las Vegas for 10 days."
    how_it_happened: "Attackers found an MGM employee on LinkedIn, called the
    IT helpdesk impersonating that employee, and obtained access credentials
    in a 10-minute phone call. Ransomware was deployed within hours."
    what_employees_could_have_done: "Helpdesk staff must verify caller identity
    through official channels before resetting credentials. Never provide
    account access based on a phone call alone."

17. Caesars Entertainment (2023)  $15M ransom paid
    breach_type: social_engineering
    records_affected: NULL
    estimated_cost_usd: 15000000
    severity: critical
    description: "Caesars Entertainment paid $15 million in ransom to Scattered
    Spider after attackers gained access through social engineering of an IT
    helpdesk vendor, exposing loyalty program data."
    how_it_happened: "Attackers called an outsourced IT helpdesk vendor,
    impersonated a Caesars employee, and convinced the agent to reset MFA.
    This is the same technique used against MGM two weeks later."
    what_employees_could_have_done: "Third-party helpdesk vendors are a common
    attack surface. Employees should know their company's identity verification
    procedures and report suspicious helpdesk calls."

18. Medibank (2022)  10 million Australians
    breach_type: credential_stuffing
    records_affected: 10000000
    estimated_cost_usd: 250000000
    severity: catastrophic
    description: "Australian health insurer Medibank had the medical records
    of 10 million customers stolen, including HIV diagnoses and drug abuse
    treatment records, which were published on the dark web."
    how_it_happened: "A Medibank contractor's credentials were purchased on
    a criminal forum. The attacker used them to access Medibank's systems
    over several weeks and exfiltrate the health database."
    what_employees_could_have_done: "Contractors with privileged access are
    a high-risk entry point. Unique, complex passwords and MFA for all
    external-facing systems are essential."

19. LastPass (2022)  password manager breach
    breach_type: insider_threat
    records_affected: 30000000
    estimated_cost_usd: NULL
    severity: catastrophic
    description: "Password manager LastPass was breached in two linked attacks,
    with attackers stealing encrypted user password vaults plus decryption keys
    from a senior DevOps engineer's home computer."
    how_it_happened: "Attackers first breached LastPass's development environment
    in August 2022. Using data stolen there, they targeted a senior DevOps
    engineer at home, exploiting a vulnerable Plex media server to install
    keylogger malware and steal decryption keys."
    what_employees_could_have_done: "Home computers used for work should meet
    the same security standards as office equipment. Unpatched personal
    software creates corporate risk."

20. Twilio (2022)  smishing supply chain
    breach_type: phishing
    records_affected: 1900
    estimated_cost_usd: NULL
    severity: critical
    description: "Communications platform Twilio was breached via a smishing
    attack, giving attackers access to customer data and Authy two-factor
    authentication accounts. Downstream, Signal users were affected."
    how_it_happened: "Twilio employees received fake SMS messages claiming
    their IT systems credentials had expired and directing them to a fake
    Okta login page. Several employees entered credentials, granting
    access to Twilio's internal tools."
    what_employees_could_have_done: "SMS messages requesting you to log in
    are almost always phishing. Access IT systems only through bookmarked
    URLs, never links received via SMS or email."

21. Okta (2023)  identity provider breach
    breach_type: social_engineering
    records_affected: 5000
    estimated_cost_usd: NULL
    severity: critical
    description: "Identity and access management provider Okta was breached
    via its customer support system, exposing files uploaded by thousands
    of customers including Cloudflare, 1Password, and BeyondTrust."
    how_it_happened: "An Okta support engineer's personal Google account was
    compromised. The engineer had saved their Okta work credentials in their
    personal browser profile, giving attackers access to Okta's support system."
    what_employees_could_have_done: "Never save work credentials in personal
    browser profiles. Keep work and personal accounts strictly separated."

22. Uber (2016  hidden for a year)
    breach_type: credential_stuffing
    records_affected: 57000000
    estimated_cost_usd: 148000000
    severity: catastrophic
    description: "Attackers stole data on 57 million Uber riders and drivers.
    Uber paid $100,000 to the attackers and concealed the breach from regulators
    and the public for over a year, resulting in $148M in fines."
    how_it_happened: "Attackers found Uber's AWS credentials stored in a private
    GitHub repository. Using those credentials, they accessed an S3 bucket
    containing a database backup with all user data."
    what_employees_could_have_done: "Never store credentials, API keys, or
    passwords in code repositories  even private ones. Use environment
    variables and secret managers instead."

23. Change Healthcare (2024)  US healthcare payments
    breach_type: credential_stuffing
    records_affected: 100000000
    estimated_cost_usd: 2000000000
    severity: catastrophic
    description: "The ALPHV/BlackCat ransomware attack on Change Healthcare
    disrupted US healthcare payment processing for weeks, affecting pharmacies,
    hospitals, and insurance claims nationwide. An estimated $2B in losses."
    how_it_happened: "Attackers obtained credentials for a Citrix remote access
    portal that lacked multi-factor authentication. Once inside, they spent
    9 days in the network before deploying ransomware."
    what_employees_could_have_done: "MFA on all remote access portals is
    non-negotiable. Report any access systems that lack MFA to IT security."

24. MOVEit (2023)  SQL injection mass exploitation
    breach_type: sql_injection
    records_affected: 60000000
    estimated_cost_usd: 9900000000
    severity: catastrophic
    description: "The Cl0p ransomware group exploited a SQL injection vulnerability
    in MOVEit Transfer file sharing software, stealing data from over 2,500
    organisations including BBC, British Airways, and US government agencies."
    how_it_happened: "Cl0p discovered a zero-day SQL injection vulnerability in
    MOVEit Transfer's web interface and exploited it at scale across thousands
    of internet-facing deployments over a single weekend."
    what_employees_could_have_done: "Apply software patches immediately,
    especially for internet-facing systems. Report any delayed patching
    approvals as a security risk."

25. Ivanti (2024)  VPN zero-day exploitation
    breach_type: unpatched_vuln
    records_affected: 1700
    estimated_cost_usd: NULL
    severity: critical
    description: "Nation-state attackers exploited zero-day vulnerabilities in
    Ivanti Connect Secure VPN appliances, affecting government agencies and
    critical infrastructure organisations across the US and Europe."
    how_it_happened: "Attackers exploited authentication bypass and command
    injection vulnerabilities in Ivanti VPN before patches were available.
    Even after patches were released, many organisations were slow to apply them."
    what_employees_could_have_done: "IT staff should implement emergency patch
    cycles for critical infrastructure. Employees should report VPN anomalies
    and unexpected disconnections to IT immediately."

Run the seed: python seed_breaches.py
Verify: SELECT COUNT(*) FROM famous_breaches; → must be 25
</seed_data>
```

### ✅ PHASE 17.1 VERIFICATION
```
[ ] FamousBreach model created with all fields
[ ] flask db upgrade runs clean
[ ] 25 breach records seeded with correct data
[ ] All breach_type values are from the valid enum list
[ ] All severity values are valid
[ ] SELECT COUNT(*) FROM famous_breaches returns 25
[ ] to_dict() returns all expected fields
```

---

## PROMPT 17.2  Breach Chronicle API

```xml
<role>Flask API engineer. Clean, paginated REST endpoints.</role>

<task>
Build the Famous Breach Chronicle API endpoints.
</task>

<new_file>
FILE: backend/app/api/breach_chronicle.py

Blueprint: breach_bp, url_prefix='/api/v1/breaches'

ENDPOINT 1: GET /api/v1/breaches
  Auth required: JWT (any role)
  Query params:
    limit: int default 6, max 25
    offset: int default 0
    breach_type: str optional (filter)
    severity: str optional (filter)
    sort_by: str ['year', 'records', 'cost'] default 'year' DESC
  Response: {
    "breaches": [FamousBreach.to_dict()],
    "total": 25,
    "filters_applied": {"breach_type": "phishing"}
  }

ENDPOINT 2: GET /api/v1/breaches/random
  Auth required: JWT
  Returns 3 random breaches (for dashboard widget)
  Prefer variety: one phishing, one ransomware, one other
  Response: {"breaches": [3 items]}

ENDPOINT 3: GET /api/v1/breaches/{id}
  Auth required: JWT
  Returns full breach detail including all fields
  Response: FamousBreach.to_dict()

ENDPOINT 4: GET /api/v1/breaches/types
  Auth required: JWT
  Returns: list of all breach_type values with counts
  Response: [{"type": "phishing", "count": 7}, ...]

ENDPOINT 5: GET /api/v1/breaches/role-relevant
  Auth required: JWT
  Maps current user's job_role to most relevant breach types:
    accountant/finance → phishing, social_engineering (BEC focus)
    hr              → phishing, insider_threat
    it              → unpatched_vuln, supply_chain, ransomware
    receptionist    → social_engineering, physical
    sales           → credential_stuffing, phishing
    management      → social_engineering, phishing (whaling)
    other           → phishing, ransomware
  Returns 4 most relevant breaches for the user's role
  Response: {"breaches": [4 items], "user_role": "accountant",
             "reason": "Accountants are prime targets for Business Email Compromise (BEC)"}
</new_file>

Register blueprint in backend/app/__init__.py
```

### ✅ PHASE 17.2 VERIFICATION
```
[ ] GET /api/v1/breaches returns paginated results
[ ] Filter by breach_type works
[ ] GET /api/v1/breaches/random returns 3 varied items
[ ] GET /api/v1/breaches/role-relevant returns role-matched items
[ ] All endpoints require valid JWT
```

---

## PROMPT 17.3  Frontend: Breach Chronicle Component

```xml
<role>
Senior React/TypeScript engineer. Dark enterprise UI matching AHRIP v2 design system.
This component should create genuine emotional impact  these are real events.
</role>

<task>
Build the BreachChronicle component shown in the employee dashboard.
It displays famous breaches as a visual "Wall of Shame" with impact metrics
and role-specific context.
</task>

<component>
FILE: frontend/src/components/dashboard/BreachChronicle.tsx

Props:
  mode: 'widget' | 'full'  (widget=3 cards, full=all with filters)

Widget mode (shown on dashboard):
  Header: "💀 Real Attacks. Real Damage." with subtitle
  "These companies didn't think it would happen to them either."
  Fetches GET /api/v1/breaches/role-relevant
  Shows 4 cards in horizontal scroll
  Each card:
    - Company name (large, bold)
    - Year badge
    - Severity indicator (colour bar: catastrophic=red, critical=orange, severe=yellow)
    - Breach type icon (🎣 phishing, 💰 ransomware, 🔑 credential, 🏭 supply chain)
    - Records affected (formatted: "147 million people")
    - Cost (formatted: "$1.4 billion")
    - what_employees_could_have_done (italic, highlighted yellow-border callout box)
      Label: "What could have stopped this:"
  "See all breaches →" link to full page

Full mode (separate /app/breach-chronicle page):
  Page header with stats: total breaches tracked, total records exposed, total cost
  Filter bar: breach type pills + severity pills
  Sort by: year / records affected / cost
  Card grid (2 cols desktop, 1 mobile)
  Each card expands on click to show how_it_happened + description
  Framer Motion: card expand animation

Design language:
  Dark cards: bg-[#0D1117] border border-red-900/30
  Severity bar: left border coloured by severity
  Records/cost: large number in red, label in grey
  "What could have stopped this" box: border-l-4 border-yellow-400 bg-yellow-950/30
  Animation: card entrance stagger 0.06s
</component>

<new_page>
FILE: frontend/src/pages/employee/BreachChroniclePage.tsx
  Import BreachChronicle mode='full'
  Add to React Router in App.tsx: path='/app/breach-chronicle'
  Add "💀 Breach Chronicle" to employee sidebar navigation

FILE: frontend/src/api/breaches.ts (NEW)
  Types + API functions for all breach endpoints
</new_page>
```

### ✅ PHASE 17.3 VERIFICATION
```
[ ] BreachChronicle widget shows on employee dashboard
[ ] Role-relevant breaches displayed (accountant sees BEC/phishing breaches)
[ ] "What could have stopped this" callout visible on every card
[ ] Full page accessible at /app/breach-chronicle
[ ] Filter pills work
[ ] Card expand animation works
[ ] Sidebar link added
[ ] Numbers formatted correctly (147M, $1.4B)
```

---
---

# PHASE 18  Deep ML Personalization Layer

## Architecture Overview (Read Before Coding)

```
Your existing ML stack:
  ✅ Random Forest  → predicts overall risk level
  ✅ K-Means        → assigns behavioural archetype
  ✅ VADER Sentiment → detects emotional state during session
  ✅ Adaptive Engine → adjusts difficulty (Cognitive Load Theory rules)

What's MISSING for true personalization:
  ❌ Micro-behavioural telemetry (how long on each question, answer changes)
  ❌ Thompson Sampling for question selection (explore/exploit balance)
  ❌ Peer similarity signals (users like you struggled with X)
  ❌ Personalised AI insight cards (why you're at risk, what to focus on)

Phase 18 adds all four. Together they create a feedback loop:
  User behaviour → ML learns → Better question selection → User improves → Repeat
```

---

## PROMPT 18.1  Behavioral Telemetry Schema + Tracking

```xml
<role>
Data engineer + ML engineer. Build the telemetry infrastructure that feeds
the Phase 18 personalization algorithms.
</role>

<task>
Build the UserBehaviorEvent model and telemetry tracking service.
This is the data layer that makes ML personalization possible.
</task>

<new_model>
FILE: backend/app/models/behavior_event.py

UserBehaviorEvent model:
- id: UUID primary key
- user_id: UUID FK not null
- session_id: UUID not null
- scenario_id: UUID FK not null
- event_type: String(50) not null
  [question_viewed / answer_changed / hint_requested / answer_submitted /
   scenario_skipped / read_time_recorded / category_dwell]
- payload: Text not null (JSON blob with event-specific data)
  For answer_changed: {"from": "A", "to": "C", "change_count": 2}
  For read_time_recorded: {"dwell_ms": 12500, "word_count": 87}
  For answer_submitted: {"final_answer": "B", "total_dwell_ms": 18000,
                          "answer_changes": 1, "is_correct": true}
- category: String(50) nullable (denormalised for fast aggregation)
- difficulty: Integer nullable
- created_at: DateTime

Indexes: user_id, session_id, event_type, created_at DESC

Add to models/__init__.py. Run flask db migrate + upgrade.
</new_model>

<new_service>
FILE: backend/app/services/telemetry_service.py

def record_event(user_id: str, session_id: str, scenario_id: str,
                 event_type: str, payload: dict,
                 category: str = None, difficulty: int = None) -> UserBehaviorEvent:
  """
  Create and commit a UserBehaviorEvent record.
  Never raises  catches all exceptions and logs them.
  Returns the created event or None on failure.
  """

def get_user_telemetry_summary(user_id: str, days: int = 30) -> dict:
  """
  Aggregate telemetry for a user over the last N days.
  Returns:
  {
    "avg_dwell_ms_per_category": {"phishing": 14200, "smishing": 8900, ...},
    "avg_answer_changes_per_scenario": 1.3,
    "hint_usage_rate": 0.12,
    "fastest_category": "password_hygiene",
    "slowest_category": "social_engineering",
    "most_revised_category": "phishing",
    "total_events": 423
  }
  Uses SQL aggregation  do NOT load all events into Python.
  """

def get_category_engagement_scores(user_id: str) -> dict[str, float]:
  """
  Score 0.0-1.0 for each category based on:
    - Avg dwell time (longer = more engaged OR more confused)
    - Answer revision rate (more revisions = uncertainty)
    - Hint usage (hints = struggling)
  Higher score = user struggles more with this category.
  Use this to prioritise categories in question selection.
  Returns: {"phishing": 0.78, "smishing": 0.34, ...}
  """
</new_service>

<api_integration>
FILE: backend/app/api/training.py (MODIFY existing session answer endpoint)

In the POST /session/{id}/answer endpoint, after recording the Attempt:
  from app.services.telemetry_service import record_event
  record_event(
    user_id=current_user.id,
    session_id=session_id,
    scenario_id=scenario_id,
    event_type='answer_submitted',
    payload={
      "final_answer": answer,
      "total_dwell_ms": body.get('dwell_ms', 0),
      "answer_changes": body.get('answer_changes', 0),
      "is_correct": is_correct
    },
    category=scenario.category,
    difficulty=scenario.difficulty
  )

Add dwell_ms and answer_changes to the request body schema (optional fields).
</api_integration>
```

### ✅ PHASE 18.1 VERIFICATION
```
[ ] UserBehaviorEvent model created with all fields
[ ] flask db upgrade runs clean
[ ] record_event() never raises (test with invalid user_id)
[ ] get_user_telemetry_summary() returns correct dict structure
[ ] get_category_engagement_scores() returns float per category
[ ] Training endpoint records event on each answer submission
[ ] dwell_ms and answer_changes accepted in answer request body
```

---

## PROMPT 18.2  Thompson Sampling Question Selector

```xml
<role>
ML engineer specialising in bandit algorithms and recommendation systems.
Build the Thompson Sampling question selector that replaces simple rule-based
question selection in the adaptive engine.
</role>

<task>
Implement Thompson Sampling for scenario selection.

Thompson Sampling solves the explore/exploit problem:
  EXPLOIT: Show scenarios in categories the user is known to be weak at
           (maximise learning outcome)
  EXPLORE: Occasionally show scenarios in untested/less-tested categories
           (avoid blind spots, discover hidden weaknesses)

This is superior to pure rule-based selection because:
  - It naturally adapts as user improves
  - It discovers category weaknesses the rule engine would miss
  - It provides probabilistic diversity (not always the same scenario type)
</task>

<implementation>
FILE: backend/app/services/thompson_sampler.py

import numpy as np
from typing import List

class ThompsonSampler:
  """
  Thompson Sampling for scenario category selection.
  Models each category as a Beta distribution (α, β) where:
    α = success count (correct answers in this category)
    β = failure count (wrong answers in this category)

  Beta(α, β) represents our belief about the user's success probability.
  Low α relative to β → high uncertainty/failure rate → sample high priority
  """

  CATEGORIES = [
    'phishing_email', 'smishing', 'vishing', 'physical_security',
    'password_hygiene', 'usb_baiting', 'social_engineering', 'data_handling'
  ]

  def build_beta_params(self, user_id: str, days: int = 60) -> dict[str, tuple[int, int]]:
    """
    Query Attempt table for user's last N days of attempts per category.
    For each category:
      α = correct_count + 1  (Laplace smoothing  prevents zero)
      β = wrong_count + 1
    Returns: {"phishing_email": (3, 8), "smishing": (1, 1), ...}
    Categories with no attempts get α=1, β=1 (maximum uncertainty → explored first)
    """

  def sample_category_priorities(self, user_id: str, n_samples: int = 1000) -> List[str]:
    """
    For each category, sample from its Beta distribution n_samples times.
    Sort categories by their LOWEST sampled value (we want to IMPROVE weaknesses,
    so lower success probability = higher priority).
    Return categories sorted from highest-priority (weakest) to lowest.
    """

  def select_scenario_ids(self,
                           user_id: str,
                           available_scenarios: List[dict],
                           session_size: int = 5,
                           exclude_ids: List[str] = None) -> List[str]:
    """
    Main selection function called by the adaptive engine.

    Algorithm:
    1. Get category priorities from sample_category_priorities()
    2. Distribute session_size slots across categories:
       Top-priority category gets ceil(session_size * 0.35) slots
       Second priority gets ceil(session_size * 0.25) slots
       Remaining slots distributed across other categories
    3. For each category slot: pick a random scenario from available_scenarios
       in that category (matching user's job_role, not in exclude_ids,
       not seen in last 7 days by this user)
    4. If a category has no available scenarios, redistribute that slot
       to the next priority category
    5. Return list of session_size scenario IDs in randomised order
       (randomise order so user doesn't know category sequence)

    available_scenarios: list of dicts with {id, category, difficulty, target_roles}
    exclude_ids: scenario IDs already seen this session
    """

INTEGRATION  FILE: backend/app/services/adaptive_engine.py (MODIFY)

Replace the existing scenario selection logic in get_session_scenarios() with:

  from .thompson_sampler import ThompsonSampler
  sampler = ThompsonSampler()
  
  # Get all eligible scenarios (active, matches user job_role, not seen today)
  available = query_available_scenarios(user_id, user.job_role)
  
  # Use Thompson Sampling for selection
  selected_ids = sampler.select_scenario_ids(
    user_id=user_id,
    available_scenarios=available,
    session_size=5
  )
  
  return Scenario.query.filter(Scenario.id.in_(selected_ids)).all()

Keep the existing difficulty adjustment logic  Thompson Sampling selects
WHICH CATEGORY, the existing rules determine WHICH DIFFICULTY within that category.
</implementation>
```

### ✅ PHASE 18.2 VERIFICATION
```
[ ] ThompsonSampler class complete with all 3 methods
[ ] build_beta_params() returns correct alpha/beta per category
[ ] Categories with no attempts get (1,1) parameters
[ ] sample_category_priorities() returns sorted list of all 8 categories
[ ] select_scenario_ids() returns exactly session_size IDs
[ ] IDs do not include exclude_ids
[ ] Adaptive engine now uses ThompsonSampler
[ ] Existing difficulty logic preserved alongside new sampler
[ ] Write a unit test in tests/test_adaptive_engine.py:
    test_thompson_sampler_prioritises_failing_categories()
    (mock 10 failed phishing attempts, 5 correct others → phishing must rank #1)
```

---

## PROMPT 18.3  Collaborative Filtering (Peer Signals)

```xml
<role>
ML engineer. Build a lightweight collaborative filtering signal to surface
peer-based insights ("Users like you also struggle with X").
</role>

<task>
Build the peer similarity service. This is NOT full collaborative filtering
(we don't have enough users at launch). Use cluster-based peer signals instead:
users in the same K-Means cluster share learning patterns → their weak categories
inform each other's training priorities.
</task>

<implementation>
FILE: backend/app/services/peer_signal_service.py

def get_cluster_weak_categories(cluster_id: int, org_id: str, top_n: int = 3) -> list[dict]:
  """
  Find the weakest categories for users in the same K-Means cluster
  within the same organisation.

  Query: For all users with cluster_label = cluster_id in org_id,
  aggregate their Attempt records from last 30 days.
  Calculate accuracy per category across all users in cluster.
  Return bottom N categories (lowest accuracy).

  Returns:
  [
    {"category": "social_engineering", "cluster_accuracy": 0.34,
     "peer_count": 12, "message": "34% of people like you get this wrong"},
    ...
  ]

  If cluster has < 3 peers: return empty list (not enough signal).
  """

def get_peer_insight_for_user(user_id: str) -> dict:
  """
  Generate a personalised peer insight for the user's dashboard card.

  1. Get user's cluster_id from UserCluster table
  2. Get user's org_id
  3. Call get_cluster_weak_categories(cluster_id, org_id)
  4. Compare user's own weak categories vs cluster's weak categories
  5. Return:
  {
    "archetype": "Overconfident Clicker",
    "peer_count": 12,
    "shared_weakness": "social_engineering",
    "cluster_accuracy": 0.34,
    "user_accuracy": 0.28,
    "insight_message": "12 people with your profile struggle most with
                        social engineering attacks. You score slightly
                        below your peer group here.",
    "recommended_focus": "social_engineering",
    "has_signal": true
  }

  If user has no cluster assigned or cluster has < 3 peers:
  return {"has_signal": false}
  """

ENDPOINT  FILE: backend/app/api/scores.py (MODIFY  add new endpoint)

GET /api/v1/scores/peer-insight
  Auth: JWT (employee)
  Calls get_peer_insight_for_user(current_user.id)
  Response: peer insight dict as above
  Cache: 1 hour (use simple in-memory dict keyed by user_id+timestamp)
</implementation>
```

### ✅ PHASE 18.3 VERIFICATION
```
[ ] get_cluster_weak_categories() returns correct structure
[ ] Returns empty list when cluster has < 3 peers
[ ] get_peer_insight_for_user() returns has_signal=false for unclassified users
[ ] GET /api/v1/scores/peer-insight endpoint works
[ ] Auth required (401 without token)
```

---

## PROMPT 18.4  Frontend: Personalization Insight Cards

```xml
<role>
Senior React/TypeScript engineer. Dark enterprise UI.
Build the personalisation insight components for the employee dashboard.
These cards are the user-facing payoff of all the ML work in Phase 18.
</role>

<task>
Build two insight components shown on the employee dashboard:
1. MLInsightCard  shows Thompson Sampling priorities + peer signals
2. WeeklyProgressInsight  shows learning trajectory and recommended focus
</task>

<component_1>
FILE: frontend/src/components/dashboard/MLInsightCard.tsx

Fetches:
  - GET /api/v1/scores/me (user's own risk score + cluster)
  - GET /api/v1/scores/peer-insight

Displays:
  Section 1: Your Learning DNA
    Archetype badge with icon:
      Overconfident Clicker → ⚡ red badge
      Cautious Learner      → 🛡️ blue badge
      Inconsistent Performer → ⚠️ yellow badge
      Resilient Defender    → 💪 green badge
      Disengaged Completer  → 😴 grey badge
    Archetype description text

  Section 2: Focus Areas (from Thompson Sampling)
    Label: "AI-selected training priorities for you"
    Mini bar chart: 3 weakest categories with accuracy %
    Sourced from user's own risk_score category scores

  Section 3: Peer Insight (only shown if has_signal=true)
    "🧑‍🤝‍🧑 {peer_count} people with your profile also struggle with:"
    Category name highlighted
    User accuracy vs cluster accuracy comparison bar
    "Your next session will include more [category] scenarios"

Design: dark card, left-border coloured by archetype colour
Animation: number counters animate up on mount (use AnimatedNumber component)
</component_1>

<component_2>
FILE: frontend/src/components/dashboard/WeeklyProgressInsight.tsx

Fetches: GET /api/v1/scores/me/history (last 4 weeks of scores)

Displays:
  Mini sparkline chart (Recharts LineChart, no axes, just the trend line)
  Risk score trend: last 4 weeks
  Colour: green if trending down (improving), red if trending up (worsening)
  Label: "Your risk score this week: 67 (↓12 from last week)" or (↑8)
  Recommended focus badge: "Focus on: Phishing Email" (highest category score)
  Motivational message based on trend:
    Improving → "You're making real progress. Keep it up. 🔥"
    Worsening → "Your risk score increased. Let's fix that today. 💪"
    Stable    → "Consistent effort. Push for improvement this week."

Design: compact card, fits in 2-column dashboard grid
</component_2>

<dashboard_integration>
FILE: frontend/src/pages/employee/TrainingPage.tsx (or Dashboard)

Dashboard card grid layout (below gamification, above scenario list):

  Row 1: [MLInsightCard (span 2)] [WeeklyProgressInsight (span 1)]
  
  Also add to navigation sidebar under employee section:
    "🤖 My AI Insights" → /app/my-insights page

FILE: frontend/src/pages/employee/MyInsightsPage.tsx (NEW)
  Full-page view combining:
    - MLInsightCard (expanded)
    - WeeklyProgressInsight (expanded sparkline)
    - CyberNewsFeed compact mode (6 items, role-filtered)
    - BreachChronicle widget mode (role-relevant breaches)
  This is the user's personalised intelligence hub.
</dashboard_integration>
```

### ✅ PHASE 18.4 VERIFICATION
```
[ ] MLInsightCard shows archetype with correct badge colour
[ ] Category accuracy bars render with real data
[ ] Peer insight section shows/hides based on has_signal flag
[ ] WeeklyProgressInsight sparkline renders with trend colour
[ ] Motivational message matches trend direction
[ ] Both cards appear in dashboard grid
[ ] /app/my-insights page loads with all 4 components
[ ] Sidebar link added
[ ] AnimatedNumber counters animate on mount
```

---
---

# FEATURE RECOMMENDATIONS

## Features to Add After Phase 18 (Priority Order)

---

### REC-1: Role-Specific Threat Digest Email (HIGH VALUE)
**What:** Weekly automated email to each employee  "Top 3 threats targeting
your role this week"  pulled from the live news feed, personalised by job_role.
**Why:** Email touchpoints outside the app dramatically increase training stickiness.
SME employees forget the platform exists. Weekly emails keep it alive.
**Stack:** Add Flask-Mail + HTML email templates (Jinja2). APScheduler sends
every Monday 9am. Email shows 3 news articles + current risk score + one
recommended scenario to complete.
**Prompt addition needed:**
  Phase 19.1  Weekly Digest Email Service
  Phase 19.2  Email Template (responsive HTML)
  Phase 19.3  Admin digest settings (on/off per org)

---

### REC-2: Manager Threat Brief Overlay
**What:** On the manager dashboard, overlay an "Org Threat Brief" widget that
shows: top 3 live threats relevant to the organisation's industry, + which
of those threat types have the lowest team accuracy.
**Why:** Managers currently see team risk scores. Connecting live threats to
team weakness gaps gives managers an actual action item: "phishing accuracy
is 48% and a major phishing campaign just hit our industry."
**Stack:** Combine /api/v1/news/feed + /api/v1/manager/dashboard data server-side
into a new GET /api/v1/manager/threat-brief endpoint.

---

### REC-3: Adaptive Session Difficulty Ladder
**What:** Instead of choosing difficulty 1/2/3 per category, implement a
progression ladder: every 3 correct answers in a category at difficulty N
→ auto-promotes to difficulty N+1. Every 2 wrong at difficulty N →
returns to N-1.
**Why:** This is the Leitner spaced-repetition principle applied to difficulty.
It ensures users aren't stuck on easy scenarios once they've mastered them.
**Stack:** Extend UserGamification model with a
`category_difficulty_level: JSON` field. Update adaptive engine to use it.

---

### REC-4: Scenario Report / Flag Button
**What:** Employees can flag a scenario as "Confusing", "Outdated", or "Error
in question". Flagged scenarios appear in admin panel with a count.
**Why:** You will have scenario quality issues after launch. This gives you
a feedback loop to fix them without monitoring user performance manually.
**Stack:** New ScenarioFlag model + POST /api/v1/scenarios/{id}/flag endpoint
+ admin panel flag queue view.

---

### REC-5: Certificate of Completion (PDF)
**What:** When a user completes all 8 categories at >= 75% accuracy, they can
download a PDF certificate of completion. Managers can see who has certificates.
**Why:** Certificates are highly motivating for non-technical staff. They also
give HR a tangible training completion record.
**Stack:** Use ReportLab (Python) to generate a styled PDF certificate server-side.
GET /api/v1/certificates/me → returns PDF file. Store certificate_issued_at on User.

---

### REC-6: Mobile-First Progressive Web App (PWA)
**What:** Add PWA manifest + service worker so employees can install AHRIP
on their phone home screen. Enable push notifications for daily challenges.
**Why:** SME employees in Kathmandu use mobile first. A home screen icon
dramatically increases daily usage vs. remembering a URL.
**Stack:** Vite PWA plugin (vite-plugin-pwa) + Web Push API + VAPID keys.
5-minute daily challenge notification each morning.

---

### REC-7: Simulated Phishing Campaign (ADVANCED)
**What:** Admin can send a simulated phishing email to all employees. If
an employee clicks the link, they are redirected to a training page instead
of being phished. Click rates are tracked and feed into the Risk Score.
**Why:** This is the gold standard of security awareness testing. Simulation
results are far more predictive of real susceptibility than quiz scores alone.
**Stack:** Sendgrid for email delivery. A unique tracking link per employee
that redirects to a "You were just phished" training interstitial. Stores
SimulatedPhishClick event. New PhishingCampaign model.
**Note:** Requires explicit user consent in onboarding  add consent field.

---

### REC-8: Leaderboard Privacy Controls
**What:** Employees can opt out of the public leaderboard. Opted-out users
appear as "Anonymous" even to managers. Add this to profile settings.
**Why:** Some employees in Kathmandu Valley workplaces are uncomfortable with
performance visibility. Optional leaderboard prevents training refusal.
**Stack:** Add leaderboard_visible: Boolean to User model. Filter in leaderboard
query. Add toggle in employee profile page.

---
---

# QUICK REFERENCE: New API Endpoints (Phases 16-18)

```
CYBER NEWS:
  GET  /api/v1/news/feed              Employee: paginated role-filtered feed
  GET  /api/v1/news/featured          Dashboard: top 5 articles
  GET  /api/v1/news/categories        Available category tags + counts
  POST /api/v1/news/trigger-fetch     Admin: manual ingestion trigger
  PATCH /api/v1/news/{id}/feature     Admin: toggle featured

BREACH CHRONICLE:
  GET  /api/v1/breaches               Paginated with filters
  GET  /api/v1/breaches/random        3 random breaches
  GET  /api/v1/breaches/{id}          Full breach detail
  GET  /api/v1/breaches/types         Breach type list + counts
  GET  /api/v1/breaches/role-relevant Role-matched breaches for user

ML PERSONALIZATION:
  GET  /api/v1/scores/peer-insight    Cluster-based peer learning signal
  (Thompson Sampling integrates into existing /api/v1/session/start)
```

---

# NEW DB MODELS SUMMARY (Phases 16-18)

```
CyberNews        live threat articles from RSS feeds (up to 30 days)
FamousBreach     25 curated historical breaches (permanent reference)
UserBehaviorEvent  micro-interaction telemetry per question/session
```

---

# UPDATED requirements.txt ADDITIONS

```
feedparser==6.0.11
python-dateutil==2.9.0
```

No additional ML libraries needed  Thompson Sampling uses only numpy
(already installed with scikit-learn). All news scoring uses scikit-learn's
TfidfVectorizer (already in stack).

---

**END OF EXTENSION PHASES 16-18**
*Append these phases to AHRIP_v2_Master_Build.md after Phase 15*
*3 New Phases · 12 Prompts · 3 New DB Models · 12 New API Endpoints*
*BSc (Hons) Ethical Hacking & Cybersecurity  Softwarica × Coventry University*
