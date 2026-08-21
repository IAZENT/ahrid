# AHRIP v2 - Final Combined Prompts v2.0
## Bug Fixes + NVIDIA NIM Multimodal Integration (Corrected & Verified)
### 6 Sequential Prompts - Feed to Claude Code / Claude Opus 4.7 one at a time

---

> ## VERIFIED API REFERENCE (Read before any code is written)
>
> These are the EXACT, CONFIRMED endpoints and methods for every model.
> The code below comes directly from the official NVIDIA docs and user-verified samples.
>
> ─────────────────────────────────────────────────────────────
> MODEL 1 - Gemini 3 Flash Preview (Scenario/Question Generation)
> ─────────────────────────────────────────────────────────────
> Package:     pip install google-genai           (NOT google-generativeai)
> Model ID:    gemini-3-flash-preview
> Client:      genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
> Method:      client.models.generate_content_stream(model, contents, config)
> Thinking:    types.ThinkingConfig(thinking_level="HIGH")
> Search:      types.Tool(googleSearch=types.GoogleSearch())
> Streaming:   yes - iterate chunks, check chunk.text
>
> ─────────────────────────────────────────────────────────────
> MODEL 2 - Kimi K2.6 (Vishing Script Generation, long-form)
> ─────────────────────────────────────────────────────────────
> Endpoint:    https://integrate.api.nvidia.com/v1/chat/completions
> Model ID:    moonshotai/kimi-k2.6     (NOT kimi-k2-instruct)
> Auth:        Authorization: Bearer $NVIDIA_API_KEY
> Thinking:    chat_template_kwargs: {"thinking": True}
> Streaming:   stream=True → iter_lines() → decode UTF-8
> Max tokens:  16384
>
> ─────────────────────────────────────────────────────────────
> MODEL 3 - FLUX.2-klein-4B (Text-to-Image Visual Scenarios)
> ─────────────────────────────────────────────────────────────
> Endpoint:    https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b
>              (NOT integrate.api.nvidia.com - different base URL)
> Auth:        Authorization: Bearer $NVIDIA_API_KEY
> Payload:     {"prompt": str, "width": 1024, "height": 1024, "seed": 0, "steps": 4}
> Response:    response_body dict - image data inside (see Step 2 for exact parsing)
> Accept:      application/json
>
> ─────────────────────────────────────────────────────────────
> MODEL 4 - Magpie TTS Multilingual (Vishing Voice - CLOUD HOSTED)
> ─────────────────────────────────────────────────────────────
> KEY DISCOVERY: This IS cloud-hosted - NO GPU required on your side.
> Server:      grpc.nvcf.nvidia.com:443   (NVIDIA cloud, not your server)
> Auth:        gRPC metadata: function-id + Bearer token
> Function ID: 877104f7-e885-42b9-8de8-f6e4c6303969
> Package:     pip install nvidia-riva-client
> Python API:  riva.client.Auth + riva.client.SpeechSynthesisService
> Output:      WAV bytes (PCM 22050Hz mono 16-bit)
> Voices:      Magpie-Multilingual.EN-US.Aria/Jason/Leo/Sofia/Mia
>
> ─────────────────────────────────────────────────────────────
> MODEL 5 - Magpie TTS Zeroshot (Voice Cloning - access pending)
> ─────────────────────────────────────────────────────────────
> Status:      Access requested - function-id will be provided on approval
> Pattern:     Same gRPC/riva pattern as Multilingual + zero_shot_audio_prompt_file
> Fallback:    If not available, use Multilingual (already sounds professional)
>
> ─────────────────────────────────────────────────────────────
> RESILIENCE DESIGN - No single point of failure
> ─────────────────────────────────────────────────────────────
> Scenario generation:   Gemini → fallback Kimi → fallback Ollama (local)
> Vishing scripts:       Kimi → fallback Gemini → fallback Ollama
> Image generation:      FLUX → fallback: skip image (graceful, non-blocking)
> Voice synthesis:       Magpie Multilingual → fallback Magpie Zeroshot (when available)
>                        → fallback pyttsx3 (offline, zero-cost, always available)
> All AI calls:          Async + cached - generated once, stored forever

---

> ## EXECUTION ORDER
>
> Run prompts in this exact order. Each prompt is independent but builds on prior.
>
> PROMPT 1 - Fix Feed Pipeline (PhishTank dead, OTX/URLScan broken, conversion 0)
> PROMPT 2 - LLM Scenario Generation (Gemini + Kimi with exact API)
> PROMPT 3 - Fix MCQ Answer Pattern + Add Question Variety
> PROMPT 4 - Fix ML Training Threshold + Synthetic Seed Data
> PROMPT 5 - PHASE 19: FLUX.2-klein-4B Text-to-Image
> PROMPT 6 - PHASE 20: Magpie TTS Vishing Audio Engine
>
> After all 6 prompts run these scripts in order:
>   python fix_answer_patterns.py
>   python seed_ml_data.py
>   python train_models.py
>   POST /api/v1/admin/trigger-feed-ingestion
>   POST /api/v1/admin/generate-scenarios
>   POST /api/v1/admin/generate-images
>   POST /api/v1/admin/generate-audio

---
---

# PROMPT 1 - Fix Feed Pipeline

```
You are fixing critical bugs in the AHRIP threat intelligence pipeline.
Read this entire prompt before touching any file.

═══════════════════════════════════════════════════════════
PROBLEM 1 - PhishTank is dead. Remove it completely.
═══════════════════════════════════════════════════════════

Delete all references to PhishTank from:
  - backend/app/services/threat_ingestion.py
  - backend/app/config.py
  - backend/.env.example
  - backend/render.yaml
  - Any requirements or seed files that reference phishtank

Replace with Source B (PhishStats):
  URL: https://phishstats.info/phish_score.csv
  Free, no API key, continuously updated
  Columns: #, date, url, ip
  Parse with pandas. Keep rows where url starts with http/https.

═══════════════════════════════════════════════════════════
PROBLEM 2 - URL validation is too strict. Fix it.
═══════════════════════════════════════════════════════════

In backend/app/services/threat_ingestion.py,
replace the validate_url() method entirely:

  def validate_url(self, url: str) -> bool:
      """
      Validate URL structure only. Do NOT make HTTP requests.
      Phishing URLs die in hours - HEAD requests always fail.
      The threat value is in the domain pattern, not liveness.
      """
      try:
          parsed = urlparse(url)
          if parsed.scheme not in ['http', 'https']:
              return False
          if not parsed.netloc or len(parsed.netloc) < 4:
              return False
          if len(url) < 15:
              return False
          # Reject bare IPs with no path (e.g., http://1.2.3.4)
          import re
          if re.match(r'^https?://\d+\.\d+\.\d+\.\d+/?$', url):
              return False
          return True
      except Exception:
          return False

Remove ALL HEAD/GET request validation from the entire pipeline.

═══════════════════════════════════════════════════════════
PROBLEM 3 - Phishing.Database ingests 50 rows but converts 0.
═══════════════════════════════════════════════════════════

Fix in backend/app/services/scenario_generator.py:
  a. Remove any minimum threshold check before conversion
  b. Every validated entry MUST attempt generate_scenario()
  c. generate_scenario() must NEVER return None silently
     If any step fails, log exactly which step:
       logger.error(f"Scenario gen FAILED at step '{step}' for entry {entry.id}: {reason}")
  d. Add logging to every conversion attempt:
       logger.info(f"[CONVERT] entry={entry.id} lure_type={entry.lure_type} url={entry.url[:40]}")
       logger.info(f"[RESULT]  scenario={'CREATED: '+scenario.title if scenario else 'FAILED'}")

Fix in backend/app/services/threat_ingestion.py:
  e. The ingestion flow must be:
       fetch_feed() → validate_url() → classify() → generate_scenario()
     Remove any intermediate "batch threshold" that skips generation.

═══════════════════════════════════════════════════════════
PROBLEM 4 - OTX endpoint is wrong.
═══════════════════════════════════════════════════════════

WRONG endpoint (requires paid subscription):
  GET /api/v1/pulses/subscribed

CORRECT endpoint (free with API key):
  GET https://otx.alienvault.com/api/v1/search/pulses?q=phishing&limit=20
  Header: X-OTX-API-KEY: {Config.ALIENVAULT_OTX_KEY}
  Extract: pulse['indicators'] where indicator['type'] == 'URL'
  Yield: indicator['indicator'] as the URL value

═══════════════════════════════════════════════════════════
PROBLEM 5 - URLScan query is wrong.
═══════════════════════════════════════════════════════════

Correct query string:
  q=task.tags:phishing&size=100&sort=date:desc
  Header: API-Key: {Config.URLSCAN_API_KEY}
  Extract: results[].page.url
  Filter: results[].verdicts.overall.malicious == True

═══════════════════════════════════════════════════════════
VERIFICATION CHECKLIST
═══════════════════════════════════════════════════════════
[ ] grep -r "phishtank" backend/ returns ZERO results
[ ] validate_url() contains no requests.head() or requests.get()
[ ] PhishStats feed parses CSV and yields URLs
[ ] OTX uses /search/pulses not /pulses/subscribed
[ ] URLScan uses task.tags:phishing query
[ ] POST /api/v1/admin/trigger-feed-ingestion returns converted > 0
[ ] Logs show [CONVERT] and [RESULT] lines for every entry
```

---

# PROMPT 2 - LLM Scenario Generation (Gemini + Kimi - Exact API)

```
You are adding two LLM generators to AHRIP for producing training scenarios
across ALL 8 security categories. Use the EXACT API code patterns below.

═══════════════════════════════════════════════════════════
DEPENDENCIES
═══════════════════════════════════════════════════════════

pip install google-genai requests
# Do NOT install google-generativeai - use google-genai only

Add to .env:
  GEMINI_API_KEY=your-key-from-aistudio.google.com
  NVIDIA_API_KEY=nvapi-your-key-from-build.nvidia.com

Add to backend/app/config.py:
  GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
  NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY', '')
  GEMINI_MODEL = 'gemini-3-flash-preview'
  KIMI_MODEL = 'moonshotai/kimi-k2.6'

═══════════════════════════════════════════════════════════
FILE: backend/app/services/gemini_generator.py
(COMPLETE FILE - no placeholders, no truncation)
═══════════════════════════════════════════════════════════

import os
import json
import time
import logging
from google import genai
from google.genai import types
from app.config import Config

logger = logging.getLogger(__name__)

# Lazy client init - created once on first use
_gemini_client = None

def get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment")
        _gemini_client = genai.Client(api_key=Config.GEMINI_API_KEY)
    return _gemini_client


CATEGORY_CONTEXTS = {
    'phishing_email':    'email-based phishing with fake links and spoofed senders',
    'smishing':          'SMS phishing to mobile phones with urgent fake messages',
    'vishing':           'phone call social engineering and voice phishing impersonation',
    'physical_security': 'tailgating, shoulder surfing, visitor impersonation, USB drops',
    'password_hygiene':  'weak passwords, reuse, sharing, sticky notes, browser saves',
    'usb_baiting':       'malicious USB drives in car parks, breakrooms, labelled temptingly',
    'social_engineering':'impersonation, pretexting, help desk manipulation, BEC',
    'data_handling':     'sending to wrong recipient, personal cloud storage, screen sharing',
}

JOB_ROLE_CONTEXTS = {
    'receptionist': 'works at front desk, handles visitors, answers main phone',
    'accountant':   'processes invoices, handles payments, manages financial records',
    'hr':           'handles job applications, employee records, payroll data',
    'it':           'manages systems, resets passwords, handles IT support tickets',
    'finance':      'approves transfers, manages vendor payments, accesses banking',
    'sales':        'contacts prospects, shares proposals, uses CRM, travels frequently',
    'management':   'approves budgets, receives executive communications, delegates',
}

SCENARIO_JSON_SCHEMA = """
{
  "title": "Short descriptive title (max 60 chars)",
  "content": "Scenario text 100-300 words. Vivid, specific, Nepali context. Kathmandu Valley business setting. Use Nepali names and NPR amounts.",
  "correct_answer": "A or B or C or D - MUST BE RANDOMISED, NEVER always C",
  "option_a": "First option 50-100 words - all options must be SIMILAR length",
  "option_b": "Second option 50-100 words",
  "option_c": "Third option 50-100 words",
  "option_d": "Fourth option 50-100 words",
  "explanation": "Why correct is right, why others are wrong. 150-250 words. Name specific psychological manipulation tactics used.",
  "red_flags": ["Specific red flag 1", "Specific red flag 2", "Specific red flag 3", "Specific red flag 4"],
  "learning_tip": "One memorable sentence the employee will remember next time.",
  "target_roles": "job_role or 'all'"
}
"""

def _build_scenario_prompt(category: str, difficulty: int, job_role: str,
                             threat_context: str = None) -> str:
    role_ctx = JOB_ROLE_CONTEXTS.get(job_role, 'works in a small business')
    cat_ctx = CATEGORY_CONTEXTS.get(category, category)
    diff_desc = {1: 'obvious red flags, easy to spot',
                 2: 'subtle and realistic',
                 3: 'sophisticated and highly convincing'}[difficulty]
    threat_hint = f"\nBase the scenario on this real threat pattern: {threat_context}" if threat_context else ""

    return f"""You are a cybersecurity training content creator for SME businesses in Nepal.

Generate a realistic cybersecurity training scenario with these exact specifications:
- Category: {category} ({cat_ctx})
- Difficulty: {difficulty}/3 ({diff_desc})
- Target employee: {job_role} ({role_ctx})
- Setting: Small or medium business in Kathmandu Valley, Nepal{threat_hint}

CRITICAL RULES - violating these makes the training useless:
1. The scenario must feel like a REAL situation this employee would actually face
2. Use SPECIFIC details: Nepali names (Raju, Sita, Dipendra), amounts in NPR, local banks (NIC Asia, Nabil, Everest), local telecom (NTC, Ncell), local brands
3. The correct answer MUST be randomised - it should be A, B, C, or D with equal probability. DO NOT default to C.
4. All four answer options MUST be similar in length (50-100 words each)
5. Wrong answers must be PLAUSIBLE traps - not obviously stupid choices
6. Red flags must be SPECIFIC - not "it seemed suspicious" but the exact detail

Return ONLY valid JSON matching this schema. No preamble, no markdown fences, no explanation outside the JSON:
{SCENARIO_JSON_SCHEMA}"""


def generate_scenario(category: str, difficulty: int, job_role: str = 'all',
                       threat_context: str = None) -> dict | None:
    """
    Generate a single training scenario using Gemini 3 Flash Preview.
    Uses streaming to handle long responses. Returns parsed dict or None.
    """
    try:
        client = get_gemini_client()
        prompt = _build_scenario_prompt(category, difficulty, job_role, threat_context)

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]

        # Use ThinkingConfig for better JSON structure, no search needed for generation
        generate_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="LOW"),
            # LOW thinking for speed; HIGH for complex scenarios
        )

        # Collect streamed chunks into full response
        full_text = ""
        for chunk in client.models.generate_content_stream(
            model=Config.GEMINI_MODEL,
            contents=contents,
            config=generate_config,
        ):
            if chunk.text:
                full_text += chunk.text

        return _parse_scenario_json(full_text, category, job_role)

    except Exception as e:
        logger.error(f"Gemini generation failed for {category}/{job_role}: {e}")
        return None


def _parse_scenario_json(text: str, category: str, job_role: str) -> dict | None:
    """Parse and validate scenario JSON from LLM response."""
    # Strip markdown fences if present
    text = text.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        # Remove first and last fence lines
        text = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])
    if text.startswith('json'):
        text = text[4:].strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Gemini returned invalid JSON for {category}: {e}")
        logger.debug(f"Raw response (first 500 chars): {text[:500]}")
        return None

    # Validate required keys
    required = ['title', 'content', 'correct_answer', 'option_a', 'option_b',
                'option_c', 'option_d', 'explanation', 'red_flags', 'learning_tip']
    missing = [k for k in required if k not in data]
    if missing:
        logger.error(f"Gemini response missing keys {missing} for {category}")
        return None

    # Validate correct_answer
    if data['correct_answer'] not in ['A', 'B', 'C', 'D']:
        logger.error(f"Invalid correct_answer '{data['correct_answer']}' - defaulting to A")
        data['correct_answer'] = 'A'

    # Ensure red_flags is a list
    if isinstance(data['red_flags'], str):
        data['red_flags'] = [data['red_flags']]

    return data


def generate_batch(category: str, count: int = 3,
                   job_roles: list = None) -> list[dict]:
    """
    Generate multiple scenarios for a category, varied by difficulty and role.
    Used by weekly scheduler and admin manual trigger.
    """
    if job_roles is None:
        job_roles = list(JOB_ROLE_CONTEXTS.keys())

    difficulty_distribution = [1, 1, 2, 2, 3]
    results = []

    for i in range(count):
        difficulty = difficulty_distribution[i % len(difficulty_distribution)]
        job_role = job_roles[i % len(job_roles)]

        data = generate_scenario(category, difficulty, job_role)
        if data:
            results.append({
                **data,
                'source': 'gemini',
                'category': category,
                'difficulty': difficulty,
                'xp_reward': {1: 10, 2: 15, 3: 25}[difficulty],
                'target_roles': data.get('target_roles', job_role),
                'question_type': 'mcq',
            })
            logger.info(f"[GEMINI] Generated '{data['title']}' ({category}, diff={difficulty}, role={job_role}, answer={data['correct_answer']})")
        else:
            logger.warning(f"[GEMINI] Failed to generate {category} diff={difficulty} role={job_role}")

        time.sleep(1.5)  # Respect rate limits

    return results


═══════════════════════════════════════════════════════════
FILE: backend/app/services/kimi_generator.py
(COMPLETE FILE - Kimi K2.6 for vishing scripts)
═══════════════════════════════════════════════════════════

import json
import logging
import time
import requests
from app.config import Config

logger = logging.getLogger(__name__)

NVIDIA_CHAT_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"

VISHING_PROMPT_TEMPLATE = """You are creating a cybersecurity awareness training scenario for SME employees in Nepal.

Create a VISHING (voice phishing) phone call scenario for a {job_role} at a small business in Kathmandu Valley.
Difficulty: {difficulty}/3 ({diff_desc})
{context_hint}

The scenario centres on a realistic incoming phone call from an attacker.

CRITICAL RULES:
1. Use Nepali context: local banks (NIC Asia, Nabil, Standard Chartered Nepal), 
   government agencies (IRD, DoTM, NRB), telecom companies (NTC, Ncell)
2. The CALL TRANSCRIPT must be realistic, multi-turn dialogue (200-400 words)
3. Format transcript as: CALLER: [text] \\nEMPLOYEE: [hesitates/pauses] \\nCALLER: [text]
4. Include specific psychological tactics in the call: urgency, authority, fear, reciprocity
5. RANDOMISE the correct answer - do NOT always pick C
6. All four answer options must be similar in length (50-80 words each)

Return ONLY valid JSON, no markdown fences, no preamble:
{{
  "title": "Scenario title max 60 chars",
  "caller_persona": "Who the attacker is pretending to be",
  "content": "Scene-setting narrative 100-200 words. Employee is at desk when phone rings. Include caller ID context.",
  "call_script": "Full realistic phone dialogue 200-400 words. Alternate CALLER:/EMPLOYEE: turns. Make it feel uncomfortably real.",
  "correct_answer": "A, B, C, or D - RANDOMISE THIS",
  "option_a": "What employee should do - option 1 (50-80 words)",
  "option_b": "What employee could do - option 2 (50-80 words)",
  "option_c": "What employee could do - option 3 (50-80 words)",
  "option_d": "What employee could do - option 4 (50-80 words)",
  "explanation": "Why correct is right and others are wrong. 150-250 words. Name the specific manipulation tactics.",
  "red_flags": ["Specific red flag 1", "Specific red flag 2", "Specific red flag 3", "Specific red flag 4"],
  "learning_tip": "One memorable sentence.",
  "psychological_tactics": ["Tactic 1 used in the call", "Tactic 2", "Tactic 3"],
  "target_roles": "{job_role}"
}}"""


def generate_vishing_scenario(job_role: str, difficulty: int,
                               scenario_context: str = None) -> dict | None:
    """
    Generate a vishing scenario using Kimi K2.6 via NVIDIA NIM.
    Uses streaming for reliability with long responses.
    Returns parsed dict or None on failure.
    """
    if not Config.NVIDIA_API_KEY:
        logger.error("NVIDIA_API_KEY not set - cannot use Kimi")
        return None

    diff_desc = {
        1: 'obvious red flags, poor execution, easy to identify',
        2: 'professional tone, believable backstory, moderate pressure',
        3: 'highly convincing, researched target, sophisticated multi-step attack'
    }[difficulty]

    context_hint = f"Base it on this threat pattern: {scenario_context}" if scenario_context else ""

    prompt = VISHING_PROMPT_TEMPLATE.format(
        job_role=job_role,
        difficulty=difficulty,
        diff_desc=diff_desc,
        context_hint=context_hint
    )

    headers = {
        "Authorization": f"Bearer {Config.NVIDIA_API_KEY}",
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Config.KIMI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 16384,
        "temperature": 0.85,
        "top_p": 1.00,
        "stream": True,
        "chat_template_kwargs": {"thinking": True},
    }

    try:
        response = requests.post(
            NVIDIA_CHAT_ENDPOINT,
            headers=headers,
            json=payload,
            stream=True,
            timeout=120
        )
        response.raise_for_status()

        # Collect SSE stream into full text
        full_content = ""
        for line in response.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                data_str = decoded[6:]
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    if "content" in delta and delta["content"]:
                        full_content += delta["content"]
                except (json.JSONDecodeError, IndexError, KeyError):
                    continue

        return _parse_vishing_json(full_content, job_role)

    except requests.exceptions.Timeout:
        logger.error(f"Kimi K2.6 timed out for vishing {job_role} diff={difficulty}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"Kimi K2.6 HTTP error {e.response.status_code}: {e}")
        return None
    except Exception as e:
        logger.error(f"Kimi K2.6 generation failed: {e}")
        return None


def _parse_vishing_json(text: str, job_role: str) -> dict | None:
    text = text.strip()
    # Strip thinking tags if present (Kimi uses <think>...</think>)
    if '<think>' in text:
        import re
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    # Strip markdown fences
    if text.startswith('```'):
        lines = text.split('\n')
        text = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
    if text.startswith('json'):
        text = text[4:].strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Kimi returned invalid JSON for vishing/{job_role}: {e}")
        logger.debug(f"Raw (first 500): {text[:500]}")
        return None

    required = ['title', 'content', 'call_script', 'correct_answer',
                'option_a', 'option_b', 'option_c', 'option_d',
                'explanation', 'red_flags', 'learning_tip']
    missing = [k for k in required if k not in data]
    if missing:
        logger.error(f"Kimi response missing keys: {missing}")
        return None

    if data['correct_answer'] not in ['A', 'B', 'C', 'D']:
        logger.warning(f"Kimi invalid correct_answer '{data['correct_answer']}' - fixing to A")
        data['correct_answer'] = 'A'

    # Store combined content + call script for display
    data['full_content'] = (
        data['content'] +
        "\n\n---\n**CALL TRANSCRIPT:**\n\n" +
        data['call_script']
    )

    return data


def generate_vishing_batch(count: int = 3,
                            job_roles: list = None) -> list[dict]:
    """Generate multiple vishing scenarios across roles and difficulties."""
    if job_roles is None:
        job_roles = ['receptionist', 'accountant', 'hr', 'it',
                     'finance', 'sales', 'management']

    difficulties = [1, 1, 2, 2, 3]
    results = []

    for i in range(count):
        difficulty = difficulties[i % len(difficulties)]
        job_role = job_roles[i % len(job_roles)]

        data = generate_vishing_scenario(job_role, difficulty)
        if data:
            results.append({
                'title': data['title'],
                'content': data['full_content'],
                'vishing_audio_script': _extract_caller_lines(data['call_script']),
                'correct_answer': data['correct_answer'],
                'option_a': data['option_a'],
                'option_b': data['option_b'],
                'option_c': data['option_c'],
                'option_d': data['option_d'],
                'explanation': data['explanation'],
                'red_flags': json.dumps(data.get('red_flags', [])),
                'learning_tip': data.get('learning_tip', ''),
                'target_roles': job_role,
                'category': 'vishing',
                'question_type': 'mcq',
                'difficulty': difficulty,
                'xp_reward': {1: 10, 2: 15, 3: 25}[difficulty],
                'source': 'kimi',
            })
            logger.info(f"[KIMI] Generated vishing '{data['title']}' (role={job_role}, diff={difficulty}, answer={data['correct_answer']})")

        time.sleep(2)  # Rate limit buffer

    return results


def _extract_caller_lines(call_script: str) -> str:
    """
    Extract only the CALLER lines from the call script for TTS synthesis.
    Removes stage directions in [brackets] and EMPLOYEE lines.
    """
    import re
    lines = call_script.split('\n')
    caller_lines = []
    for line in lines:
        if line.strip().startswith('CALLER:'):
            text = line.replace('CALLER:', '').strip()
            # Remove stage directions like [pauses], [laughs], [urgent tone]
            text = re.sub(r'\[.*?\]', '', text).strip()
            if text:
                caller_lines.append(text)

    combined = ' '.join(caller_lines)
    # Normalise whitespace
    combined = re.sub(r'\s+', ' ', combined).strip()
    return combined if len(combined) > 20 else call_script[:500]


═══════════════════════════════════════════════════════════
RESILIENCE: Ollama local fallback
═══════════════════════════════════════════════════════════

FILE: backend/app/services/ollama_fallback.py

"""
Local Ollama fallback for scenario generation.
Used when both Gemini and Kimi are unavailable.
Requires: ollama running locally with llama3.2 or similar model.
Install: curl -fsSL https://ollama.ai/install.sh | sh
Model:   ollama pull llama3.2
"""
import json, logging, requests
from app.config import Config

logger = logging.getLogger(__name__)
OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_scenario_ollama(prompt: str) -> dict | None:
    """Call local Ollama as last-resort fallback. Returns parsed JSON or None."""
    if not Config.OLLAMA_ENABLED:
        return None
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": Config.OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=120
        )
        response.raise_for_status()
        text = response.json().get('response', '')
        # Parse JSON from response (same logic as Gemini parser)
        if text.startswith('```'):
            text = '\n'.join(text.split('\n')[1:-1])
        return json.loads(text)
    except Exception as e:
        logger.error(f"Ollama fallback failed: {e}")
        return None

Add to Config:
  OLLAMA_ENABLED = os.environ.get('OLLAMA_ENABLED', 'false').lower() == 'true'
  OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2')


═══════════════════════════════════════════════════════════
ORCHESTRATOR: LLM Service with fallback chain
═══════════════════════════════════════════════════════════

FILE: backend/app/services/llm_orchestrator.py

"""
Central LLM orchestrator with fallback chain:
  Gemini (primary) → Kimi (secondary) → Ollama (last resort)
All callers use this, not the individual services.
"""
import logging
from app.services.gemini_generator import generate_scenario as gemini_generate
from app.services.kimi_generator import generate_vishing_scenario
from app.services.ollama_fallback import generate_scenario_ollama
from app.services.gemini_generator import _build_scenario_prompt

logger = logging.getLogger(__name__)

def generate_scenario_with_fallback(category: str, difficulty: int,
                                     job_role: str = 'all',
                                     threat_context: str = None) -> dict | None:
    """
    Generate a scenario using the best available model.
    Vishing → tries Kimi first (better call scripts), then Gemini.
    Others → tries Gemini first, then Kimi, then Ollama.
    """
    if category == 'vishing':
        # Kimi is better for vishing (long dialogue)
        logger.info(f"[LLM] Trying Kimi for vishing/{job_role}/diff={difficulty}")
        result = generate_vishing_scenario(job_role, difficulty, threat_context)
        if result:
            return {**result, 'llm_used': 'kimi'}

        logger.warning(f"[LLM] Kimi failed for vishing - trying Gemini")
        result = gemini_generate('vishing', difficulty, job_role, threat_context)
        if result:
            return {**result, 'llm_used': 'gemini_fallback'}

    else:
        # Gemini is primary for non-vishing categories
        logger.info(f"[LLM] Trying Gemini for {category}/{job_role}/diff={difficulty}")
        result = gemini_generate(category, difficulty, job_role, threat_context)
        if result:
            return {**result, 'llm_used': 'gemini'}

        logger.warning(f"[LLM] Gemini failed for {category} - trying Kimi")
        # Kimi fallback using same scenario prompt
        from app.services.kimi_generator import generate_vishing_scenario
        prompt = _build_scenario_prompt(category, difficulty, job_role, threat_context)
        result = _kimi_generic_scenario(prompt)
        if result:
            return {**result, 'llm_used': 'kimi_fallback'}

    # Last resort - Ollama
    logger.warning(f"[LLM] All cloud LLMs failed for {category} - trying Ollama")
    prompt = _build_scenario_prompt(category, difficulty, job_role, threat_context)
    result = generate_scenario_ollama(prompt)
    if result:
        return {**result, 'llm_used': 'ollama_fallback'}

    logger.error(f"[LLM] ALL generators failed for {category}/{job_role}/diff={difficulty}")
    return None


def _kimi_generic_scenario(prompt: str) -> dict | None:
    """Use Kimi for non-vishing scenario generation (generic fallback)."""
    import json, requests
    from app.config import Config
    from app.services.kimi_generator import _parse_vishing_json
    from app.services.gemini_generator import _parse_scenario_json

    headers = {
        "Authorization": f"Bearer {Config.NVIDIA_API_KEY}",
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }
    payload = {
        "model": Config.KIMI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096,
        "temperature": 0.8,
        "stream": True,
        "chat_template_kwargs": {"thinking": True},
    }
    try:
        response = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers=headers, json=payload, stream=True, timeout=90
        )
        response.raise_for_status()
        full_content = ""
        for line in response.iter_lines():
            if not line: continue
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                data_str = decoded[6:]
                if data_str == "[DONE]": break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    if "content" in delta and delta["content"]:
                        full_content += delta["content"]
                except: continue
        return _parse_scenario_json(full_content, 'generic', 'all')
    except Exception as e:
        logging.error(f"Kimi generic fallback failed: {e}")
        return None


═══════════════════════════════════════════════════════════
SCHEDULER INTEGRATION (update scheduler.py)
═══════════════════════════════════════════════════════════

In backend/app/services/scheduler.py, add:

def generate_weekly_scenarios():
    """
    Weekly job: generate 3 scenarios per category.
    Vishing via Kimi, all others via Gemini (with fallback chain).
    """
    from app.services.llm_orchestrator import generate_scenario_with_fallback
    from app.models.scenario import Scenario
    from app.extensions import db
    import json

    categories = [
        'smishing', 'vishing', 'physical_security', 'password_hygiene',
        'usb_baiting', 'social_engineering', 'data_handling'
    ]
    job_roles = ['receptionist', 'accountant', 'hr', 'it', 'finance', 'sales', 'management']
    total_created = 0

    for category in categories:
        for i in range(3):
            difficulty = [1, 2, 3][i]
            job_role = job_roles[i % len(job_roles)]

            data = generate_scenario_with_fallback(category, difficulty, job_role)
            if not data:
                continue

            scenario = Scenario(
                title=data['title'],
                content=data['content'],
                correct_answer=data['correct_answer'],
                option_a=data['option_a'],
                option_b=data['option_b'],
                option_c=data['option_c'],
                option_d=data['option_d'],
                explanation=data['explanation'],
                red_flags=json.dumps(data.get('red_flags', [])),
                learning_tip=data.get('learning_tip', ''),
                target_roles=data.get('target_roles', job_role),
                category=category,
                difficulty=difficulty,
                xp_reward={1: 10, 2: 15, 3: 25}[difficulty],
                source=data.get('llm_used', 'gemini'),
                question_type=data.get('question_type', 'mcq'),
                is_active=True,
                times_served=0,
                times_correct=0,
                # Vishing-specific
                vishing_audio_script=data.get('vishing_audio_script'),
                audio_status='pending' if category == 'vishing' else 'not_applicable',
            )
            db.session.add(scenario)
            total_created += 1

    db.session.commit()
    logger.info(f"[SCHEDULER] Weekly LLM generation: {total_created} scenarios created")

scheduler.add_job(
    func=generate_weekly_scenarios,
    trigger='cron',
    day_of_week='monday',
    hour=2,
    minute=0,
    id='weekly_llm_generation',
    replace_existing=True
)


═══════════════════════════════════════════════════════════
ADMIN ENDPOINT
═══════════════════════════════════════════════════════════

Add to backend/app/api/admin.py:

POST /api/v1/admin/generate-scenarios
  Auth: admin only
  Body: {"category": str, "count": int, "job_role": str (optional)}
  Action: calls generate_scenario_with_fallback() N times
  Returns: {
    "created": int,
    "failed": int,
    "scenarios": [{"title": str, "llm_used": str, "correct_answer": str}],
    "answer_distribution": {"A": n, "B": n, "C": n, "D": n}
  }

Add admin UI button: "Generate AI Scenarios" with category + count selector.
Show which model was used (gemini/kimi/ollama) in the result list.


═══════════════════════════════════════════════════════════
VERIFICATION CHECKLIST
═══════════════════════════════════════════════════════════
[ ] google-genai installed (NOT google-generativeai - they are different packages)
[ ] gemini_generator.py uses genai.Client() not genai.GenerativeModel()
[ ] kimi_generator.py model ID is 'moonshotai/kimi-k2.6'
[ ] kimi_generator.py strips <think>...</think> before JSON parsing
[ ] ollama_fallback.py created (even if OLLAMA_ENABLED=false)
[ ] llm_orchestrator.py routes vishing to Kimi first
[ ] Admin endpoint returns answer_distribution (should NOT be all C)
[ ] Weekly scheduler job registered in APScheduler
[ ] Test: POST /api/v1/admin/generate-scenarios body={"category":"smishing","count":3}
[ ] Test output shows correct_answer varies across A/B/C/D
```

---

# PROMPT 3 - Fix MCQ Answer Pattern + Add Question Types

```
You are fixing the training answer pattern problem and adding question variety.

═══════════════════════════════════════════════════════════
PROBLEM - Answer C is always correct. Employees learn the pattern.
═══════════════════════════════════════════════════════════

FIX A - Randomise existing 48 manual seed scenarios:

FILE: backend/fix_answer_patterns.py

import random
from collections import Counter
from app import create_app
from app.extensions import db
from app.models.scenario import Scenario

app = create_app()
with app.app_context():
    scenarios = Scenario.query.filter_by(source='manual').all()
    for scenario in scenarios:
        options = {
            'A': scenario.option_a, 'B': scenario.option_b,
            'C': scenario.option_c, 'D': scenario.option_d,
        }
        correct_content = options[scenario.correct_answer]
        keys = list(options.keys())
        values = list(options.values())
        random.shuffle(values)
        new_options = dict(zip(keys, values))
        new_correct = next(k for k, v in new_options.items() if v == correct_content)
        scenario.option_a = new_options['A']
        scenario.option_b = new_options['B']
        scenario.option_c = new_options['C']
        scenario.option_d = new_options['D']
        scenario.correct_answer = new_correct

    db.session.commit()
    answers = [s.correct_answer for s in scenarios]
    dist = dict(Counter(answers))
    print(f"Fixed {len(scenarios)} scenarios. Distribution: {dist}")
    # Expected: roughly 12 each across A/B/C/D

Run: python fix_answer_patterns.py

FIX B - Frontend client-side shuffle (defence in depth):

In frontend/src/components/training/AnswerOptions.tsx, add:

  interface DisplayOption {
    displayIndex: number    // 0-3 (shown as A-D on screen)
    originalKey: 'A' | 'B' | 'C' | 'D'  // original key in DB
    text: string
  }

  const shuffleOptions = (scenario: Scenario): DisplayOption[] => {
    const original = [
      { originalKey: 'A' as const, text: scenario.option_a },
      { originalKey: 'B' as const, text: scenario.option_b },
      { originalKey: 'C' as const, text: scenario.option_c },
      { originalKey: 'D' as const, text: scenario.option_d },
    ]
    // Fisher-Yates shuffle
    const shuffled = [...original]
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
    }
    return shuffled.map((opt, idx) => ({ ...opt, displayIndex: idx }))
  }

  // Store once per scenario load (not on every render)
  const [displayOptions, setDisplayOptions] = useState<DisplayOption[]>([])
  useEffect(() => {
    setDisplayOptions(shuffleOptions(scenario))
  }, [scenario.id])

  // When checking answer:
  // user clicked displayIndex i → displayOptions[i].originalKey
  // compare to scenario.correct_answer

ADD: question_type field to Scenario model:

In backend/app/models/scenario.py add:
  question_type = db.Column(db.String(30), default='mcq', nullable=False)
  tf_statement = db.Column(db.Text, nullable=True)  # for true_false type

Run: flask db migrate && flask db upgrade

Implement true_false question type in frontend:
  In AnswerOptions.tsx, add switch on scenario.question_type:
    'mcq':        → current shuffled A/B/C/D cards
    'true_false': → two large styled buttons TRUE and FALSE
                    correct_answer 'A' = True, 'B' = False
                    XP = difficulty * 7 (lower than MCQ: difficulty * 10)

XP by question type (update adaptive engine):
  mcq:        difficulty * 10
  true_false: difficulty * 7
  vishing (mcq with audio): difficulty * 12  (bonus for audio engagement)

VERIFICATION CHECKLIST:
[ ] python fix_answer_patterns.py runs, shows ~12 each for A/B/C/D
[ ] Frontend shuffles options on scenario load (useEffect on scenario.id)
[ ] Shuffled display maps back to correct original key for answer checking
[ ] question_type field in DB with migration
[ ] true_false scenarios show TRUE/FALSE buttons
[ ] XP calculation respects question type
```

---

# PROMPT 4 - Fix ML Training Threshold

```
You are fixing the ML models so they train on fresh deployment.

═══════════════════════════════════════════════════════════
FIX 1 - Lower thresholds in Config
═══════════════════════════════════════════════════════════

In backend/app/config.py:
  MIN_TRAINING_SAMPLES = 20   # was 50
  MIN_USERS_FOR_KMEANS = 3    # was higher

In backend/train_models.py:
  Use Config.MIN_TRAINING_SAMPLES (not hardcoded 50)

In backend/app/services/kmeans_clustering.py:
  user_count = get_eligible_user_count()
  n_clusters = min(5, max(2, user_count // 2))
  # Dynamic cluster count - works with 3+ users

═══════════════════════════════════════════════════════════
FIX 2 - Synthetic seed data for ML bootstrapping
═══════════════════════════════════════════════════════════

Add is_synthetic = db.Column(db.Boolean, default=False) to Attempt model.
Run: flask db migrate && flask db upgrade

FILE: backend/seed_ml_data.py (COMPLETE)

"""
Generates 100 synthetic Attempt records for ML bootstrapping.
Run once on fresh deployment: python seed_ml_data.py
Synthetic data is used ONLY for model training - excluded from user scores.
Document this in thesis limitations section (standard practice).
"""
import random
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.attempt import Attempt
from app.models.user import User
from app.models.scenario import Scenario

CATEGORIES = ['phishing_email','smishing','vishing','physical_security',
              'password_hygiene','usb_baiting','social_engineering','data_handling']
SENTIMENTS = ['neutral','cautious','rushed','overconfident','anxious']
CATEGORY_WEIGHTS = [0.25,0.15,0.10,0.10,0.15,0.05,0.10,0.10]

app = create_app()
with app.app_context():
    scenarios = Scenario.query.filter(Scenario.is_active == True).limit(20).all()
    if not scenarios:
        print("ERROR: No scenarios found. Run seed.py first.")
        exit(1)

    synthetic_users = User.query.filter_by(role='employee').limit(5).all()
    if not synthetic_users:
        print("ERROR: No users found. Run seed.py first.")
        exit(1)

    now = datetime.utcnow()
    created_count = 0

    for i in range(100):
        user = random.choice(synthetic_users)
        scenario = random.choice(scenarios)
        is_correct = random.random() < 0.60   # 60% correct rate

        attempt = Attempt(
            user_id=user.id,
            scenario_id=scenario.id,
            selected_answer=scenario.correct_answer if is_correct else random.choice(
                [x for x in ['A','B','C','D'] if x != scenario.correct_answer]
            ),
            is_correct=is_correct,
            response_time_ms=random.randint(3000, 20000),
            sentiment_label=random.choices(SENTIMENTS, weights=[30,25,20,15,10])[0],
            category=random.choices(CATEGORIES, weights=CATEGORY_WEIGHTS)[0],
            difficulty=random.choices([1,2,3], weights=[40,40,20])[0],
            created_at=now - timedelta(days=random.randint(0, 30),
                                       hours=random.randint(0, 23)),
            is_synthetic=True,   # EXCLUDE from user-facing metrics
            session_id='synthetic_bootstrap'
        )
        db.session.add(attempt)
        created_count += 1

    db.session.commit()
    print(f"Created {created_count} synthetic attempts across {len(synthetic_users)} users.")
    print("Run: python train_models.py")

═══════════════════════════════════════════════════════════
FIX 3 - Exclude synthetic data from user-facing scores
═══════════════════════════════════════════════════════════

In backend/app/services/risk_scorer.py:
  All queries on Attempt must add .filter(Attempt.is_synthetic == False)

In backend/app/services/random_forest_model.py:
  Training query: DO include synthetic (is_synthetic can be True OR False)
  Prediction query: EXCLUDE synthetic (is_synthetic == False only)

═══════════════════════════════════════════════════════════
FIX 4 - Health endpoint accuracy
═══════════════════════════════════════════════════════════

GET /api/v1/health must return:
  {
    "status": "healthy",
    "ml": {
      "random_forest": "trained" | "untrained",
      "kmeans": "trained" | "untrained",
      "training_samples_real": N,      # excludes synthetic
      "training_samples_total": M,     # includes synthetic
      "threshold": 20
    }
  }

VERIFICATION CHECKLIST:
[ ] is_synthetic field on Attempt model with migration
[ ] seed_ml_data.py runs without error
[ ] python train_models.py succeeds after seeding (not skipped)
[ ] ml_models/risk_rf_model.pkl exists
[ ] ml_models/user_clusters.pkl exists
[ ] /api/v1/health shows both models as "trained"
[ ] Risk scores for real users exclude synthetic attempts
```

---

# PROMPT 5 - PHASE 19: FLUX.2-klein-4B Text-to-Image

```
You are adding AI-generated visual scenario images using FLUX.2-klein-4B
via NVIDIA's hosted API. No GPU required - this is a REST API call.

Read the EXACT endpoint below before writing any code.

═══════════════════════════════════════════════════════════
CONFIRMED EXACT API (from official NVIDIA docs)
═══════════════════════════════════════════════════════════

import requests
import base64

FLUX_ENDPOINT = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b"

def call_flux(prompt: str, nvidia_api_key: str) -> bytes | None:
    """Returns raw PNG bytes or None on failure."""
    headers = {
        "Authorization": f"Bearer {nvidia_api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "width": 1024,
        "height": 1024,
        "seed": 0,
        "steps": 4,          # 4 steps is optimal for klein (distilled model)
    }
    response = requests.post(FLUX_ENDPOINT, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    response_body = response.json()
    # The image data is in response_body - log the structure on first call
    # to confirm exact key path (may be response_body['artifacts'][0]['base64']
    # or response_body['data'][0]['b64_json'] depending on API version)
    # Handle both formats:
    if 'artifacts' in response_body:
        b64 = response_body['artifacts'][0]['base64']
    elif 'data' in response_body:
        b64 = response_body['data'][0]['b64_json']
    else:
        raise KeyError(f"Unexpected FLUX response structure: {list(response_body.keys())}")
    return base64.b64decode(b64)

NOTE: Log the full response_body structure on the FIRST call to confirm
which key contains the image. Add this to the service:
  logger.debug(f"FLUX response keys: {list(response_body.keys())}")

═══════════════════════════════════════════════════════════
DB CHANGES
═══════════════════════════════════════════════════════════

Add to backend/app/models/scenario.py:
  image_url    = db.Column(db.String(2000), nullable=True)
  image_prompt = db.Column(db.Text, nullable=True)
  image_source = db.Column(db.String(50), nullable=True)  # 'flux_nim', 'manual', None
  image_status = db.Column(db.String(20), default='pending', nullable=False)
    # 'pending' | 'generated' | 'failed' | 'not_applicable'

Run: flask db migrate && flask db upgrade

Set image_status = 'pending' for all active scenarios during migration.

═══════════════════════════════════════════════════════════
FILE: backend/app/services/nvidia_image_service.py (COMPLETE)
═══════════════════════════════════════════════════════════

import base64
import logging
import requests
from app.config import Config

logger = logging.getLogger(__name__)

FLUX_ENDPOINT = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b"

# Image prompts by category - specific, realistic, avoids generic
IMAGE_PROMPT_TEMPLATES = {
    'phishing_email': (
        "A realistic computer monitor screenshot showing a suspicious email. "
        "The email has a slightly misspelled sender address, an urgent subject line about account suspension, "
        "a generic greeting, and a prominent blue 'Verify Now' button. "
        "The email client interface is visible. Kathmandu office setting in background. "
        "Photorealistic, corporate email client, subtle red flag details visible. "
        "No real brand logos. Professional office lighting."
    ),
    'smishing': (
        "A photorealistic smartphone screen showing an SMS message from an unknown number. "
        "The SMS contains urgent text about a package delivery or bank alert with a suspicious shortened link. "
        "Modern Android or iOS SMS interface visible. Phone on a desk in a Nepali office. "
        "Photorealistic mobile phone photography style."
    ),
    'vishing': (
        "A photorealistic image of a desk telephone or mobile phone on an office desk "
        "showing an incoming call from an unfamiliar number. "
        "Kathmandu Valley small business office environment. Warm afternoon lighting. "
        "The phone screen shows the call is incoming. Slightly anxious atmosphere. "
        "Photorealistic documentary photography style."
    ),
    'physical_security': (
        "A photorealistic image of an office building entrance or reception area in Nepal. "
        "A person in business attire attempting to enter through a security door without an ID badge, "
        "or a reception desk with a visitor signing in. South Asian office environment. "
        "Photorealistic architectural photography style."
    ),
    'password_hygiene': (
        "A photorealistic close-up photograph of a computer monitor with a sticky note "
        "containing a written password attached to the screen bezel. "
        "Office desk in Kathmandu. Slightly shallow depth of field. "
        "Photorealistic documentary photography, security awareness context."
    ),
    'usb_baiting': (
        "A photorealistic image of a USB flash drive sitting on an office car park ground or "
        "on a breakroom table. The USB has a label saying 'Salary Data 2024' or 'Confidential'. "
        "Kathmandu office environment. "
        "Photorealistic ground-level photography, the USB is the clear subject."
    ),
    'social_engineering': (
        "A photorealistic image of an office scene showing someone impersonating an IT technician "
        "or delivery person attempting to gain trust from an employee. "
        "South Asian professional office environment in Nepal. "
        "Photorealistic candid documentary style."
    ),
    'data_handling': (
        "A photorealistic screenshot of a computer screen showing an email compose window "
        "where sensitive financial data is about to be sent to the wrong email address. "
        "The autocomplete dropdown shows both a correct and incorrect recipient. "
        "Office computer in Nepal. Photorealistic screenshot style."
    ),
}

def build_image_prompt(scenario) -> str:
    """Build a specific image prompt from scenario metadata."""
    base = IMAGE_PROMPT_TEMPLATES.get(
        scenario.category,
        "A photorealistic cybersecurity awareness training illustration for a small business in Nepal."
    )
    return (
        f"{base} "
        f"Scene context: {scenario.title}. "
        "Style requirements: photorealistic, NOT cartoon or illustration, "
        "South Asian / Nepali professional context, safe for work, "
        "NO real brand logos or real company names, subtle security threat visible."
    )


def generate_scenario_image(scenario) -> str | None:
    """
    Generate an image for a scenario via FLUX.2-klein-4B.
    Uploads to Supabase Storage and returns public URL.
    Returns None on any failure (non-blocking).
    """
    if not Config.NVIDIA_API_KEY:
        logger.warning("NVIDIA_API_KEY not set - skipping image generation")
        return None

    if scenario.image_url:
        logger.debug(f"Image already exists for scenario {scenario.id} - skipping")
        return scenario.image_url

    # Check daily rate limit
    if _daily_limit_reached():
        logger.warning("Daily FLUX image limit reached - queuing for tomorrow")
        return None

    prompt = build_image_prompt(scenario)
    logger.info(f"[FLUX] Generating image for scenario '{scenario.title}' ({scenario.category})")

    headers = {
        "Authorization": f"Bearer {Config.NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "width": 1024,
        "height": 1024,
        "seed": 0,
        "steps": 4,
    }

    try:
        response = requests.post(
            FLUX_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        response_body = response.json()

        # Log structure on first call for debugging
        logger.debug(f"[FLUX] Response keys: {list(response_body.keys())}")

        # Handle both API response formats
        if 'artifacts' in response_body:
            b64_image = response_body['artifacts'][0]['base64']
        elif 'data' in response_body:
            b64_image = response_body['data'][0]['b64_json']
        else:
            raise KeyError(f"Unknown FLUX response format: {list(response_body.keys())}")

        image_bytes = base64.b64decode(b64_image)
        _increment_daily_counter()

        # Upload to Supabase Storage
        from app.services.storage_service import upload_to_supabase
        image_url = upload_to_supabase(
            bucket='scenario-assets',
            filename=f"scenario_{scenario.id}_image.png",
            content=image_bytes,
            content_type='image/png'
        )

        if image_url:
            logger.info(f"[FLUX] Image uploaded: {image_url}")
        return image_url

    except requests.exceptions.Timeout:
        logger.error(f"[FLUX] Timeout for scenario {scenario.id}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"[FLUX] HTTP {e.response.status_code} for scenario {scenario.id}: {e.response.text[:200]}")
        return None
    except KeyError as e:
        logger.error(f"[FLUX] Unexpected response structure: {e}")
        return None
    except Exception as e:
        logger.error(f"[FLUX] Unexpected error for scenario {scenario.id}: {e}")
        return None


def _daily_limit_reached() -> bool:
    """Simple DB-based daily counter. Reset at midnight UTC."""
    from app.models.system_counter import get_counter, MAX_IMAGES_PER_DAY
    return get_counter('flux_images_today') >= MAX_IMAGES_PER_DAY

def _increment_daily_counter():
    from app.models.system_counter import increment_counter
    increment_counter('flux_images_today')

Add MAX_IMAGES_PER_DAY = 50 to Config.
Create a simple SystemCounter model (id, key, value, date) for tracking.
Reset counter where date < today on each check.


═══════════════════════════════════════════════════════════
FILE: backend/app/services/storage_service.py (COMPLETE)
═══════════════════════════════════════════════════════════

pip install supabase

import logging
from supabase import create_client
from app.config import Config

logger = logging.getLogger(__name__)

_supabase_client = None

def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
    return _supabase_client

def upload_to_supabase(bucket: str, filename: str, content: bytes,
                        content_type: str = 'application/octet-stream') -> str | None:
    """
    Upload bytes to Supabase Storage. Returns public URL or None.
    Buckets must exist: scenario-assets (images), vishing-audio (WAV)
    Both buckets set to public read in Supabase dashboard.
    """
    try:
        client = get_supabase()
        client.storage.from_(bucket).upload(
            path=filename,
            file=content,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        url = client.storage.from_(bucket).get_public_url(filename)
        return url
    except Exception as e:
        logger.error(f"Supabase upload failed [{bucket}/{filename}]: {e}")
        return None

Add to .env:
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_SERVICE_KEY=your-service-role-key

Create in Supabase Dashboard (Storage → New Bucket):
  scenario-assets  (public: true)
  vishing-audio    (public: true)


═══════════════════════════════════════════════════════════
ASYNC IMAGE GENERATION ON SCENARIO SERVE
═══════════════════════════════════════════════════════════

In backend/app/api/training.py, after loading a scenario for a session:

from threading import Thread
from flask import current_app
from app.services.nvidia_image_service import generate_scenario_image, build_image_prompt
from app.extensions import db

def trigger_image_async(scenario_id: int):
    """Non-blocking image generation. Fires and forgets."""
    def _generate():
        with current_app.app_context():
            from app.models.scenario import Scenario
            scenario = Scenario.query.get(scenario_id)
            if not scenario or scenario.image_status != 'pending':
                return
            url = generate_scenario_image(scenario)
            scenario.image_url = url
            scenario.image_prompt = build_image_prompt(scenario)
            scenario.image_source = 'flux_nim'
            scenario.image_status = 'generated' if url else 'failed'
            db.session.commit()

    thread = Thread(target=_generate, daemon=True)
    thread.start()

Call trigger_image_async(scenario.id) after building the session response.
The API response returns immediately. Image loads when ready (polling).


═══════════════════════════════════════════════════════════
FRONTEND: VisualScenario.tsx
═══════════════════════════════════════════════════════════

In frontend/src/components/training/VisualScenario.tsx:

Show image ABOVE the scenario content text:
  - image_status === 'generated': <img src={image_url} /> in styled container
  - image_status === 'pending':   animated skeleton with text "Generating visual..."
  - image_status === 'failed':    show category SVG icon instead (silent fallback)

Poll for image_status every 10 seconds if still 'pending':
  useEffect with setInterval, stop polling once generated or failed.

Styling:
  max-height: 280px, border-radius: 12px, overflow: hidden
  subtle frame with 1px border in theme accent color
  Caption: "AI Visual Simulation - {categoryLabel}"
  Small italic note: "Generated for training purposes"

═══════════════════════════════════════════════════════════
VERIFICATION CHECKLIST
═══════════════════════════════════════════════════════════
[ ] FLUX endpoint is ai.api.nvidia.com (NOT integrate.api.nvidia.com)
[ ] Response body structure is logged on first call
[ ] Both 'artifacts' and 'data' response formats are handled
[ ] image_url/image_prompt/image_source/image_status on Scenario model
[ ] Migration ran successfully
[ ] Supabase buckets created (scenario-assets, vishing-audio)
[ ] storage_service.py uploads and returns public URL
[ ] Image generation is async - API response not delayed
[ ] Frontend polls for image_status updates
[ ] Graceful fallback (category icon) when image_status === 'failed'
[ ] Daily limit guard prevents overspending credits
[ ] Admin: POST /api/v1/admin/generate-images works
```

---

# PROMPT 6 - PHASE 20: Magpie TTS Vishing Audio Engine

```
You are adding realistic AI-generated voice to vishing scenarios using
NVIDIA Magpie TTS Multilingual via the CLOUD-HOSTED gRPC API.

CRITICAL DISCOVERY: Magpie TTS is CLOUD-HOSTED. You do NOT need a GPU.
The server is grpc.nvcf.nvidia.com:443 - NVIDIA's cloud infrastructure.
Your NVIDIA_API_KEY is all you need. No Docker container, no local GPU.

═══════════════════════════════════════════════════════════
CONFIRMED EXACT API (from official build.nvidia.com docs)
═══════════════════════════════════════════════════════════

CLI usage (for testing):
  python python-clients/scripts/tts/talk.py \
    --server grpc.nvcf.nvidia.com:443 --use-ssl \
    --metadata function-id "877104f7-e885-42b9-8de8-f6e4c6303969" \
    --metadata authorization "Bearer $NVIDIA_API_KEY" \
    --language-code en-US \
    --text "Your text here" \
    --voice "Magpie-Multilingual.EN-US.Jason" \
    --output audio.wav

Python programmatic (what we use in the service):
  pip install nvidia-riva-client
  import riva.client

  auth = riva.client.Auth(
      ssl_cert=None,
      use_ssl=True,
      uri="grpc.nvcf.nvidia.com:443",
      metadata_args=[
          ["function-id", "877104f7-e885-42b9-8de8-f6e4c6303969"],
          ["authorization", f"Bearer {nvidia_api_key}"]
      ]
  )
  tts_service = riva.client.SpeechSynthesisService(auth)

  # Offline synthesis (full audio at once):
  req = riva.client.SynthesizeSpeechRequest()
  req.text = "Hello, this is your text."
  req.language_code = "en-US"
  req.voice_name = "Magpie-Multilingual.EN-US.Jason"
  req.encoding = riva.client.AudioEncoding.LINEAR_PCM
  req.sample_rate_hz = 22050

  resp = tts_service.synthesize_online(req)  # or .synthesize() for non-streaming
  # resp.audio is raw PCM bytes
  audio_bytes = resp.audio

  # Convert PCM to WAV (add WAV header):
  import wave, io
  wav_buffer = io.BytesIO()
  with wave.open(wav_buffer, 'wb') as wf:
      wf.setnchannels(1)         # mono
      wf.setsampwidth(2)         # 16-bit
      wf.setframerate(22050)     # 22050 Hz
      wf.writeframes(audio_bytes)
  wav_bytes = wav_buffer.getvalue()

IMPORTANT - Function ID:
  Magpie TTS Multilingual: 877104f7-e885-42b9-8de8-f6e4c6303969
  (This is the NVCF function-id, hardcoded - it is stable)

AVAILABLE VOICES:
  EN-US: Magpie-Multilingual.EN-US.Aria   (female, professional)
         Magpie-Multilingual.EN-US.Jason  (male, authoritative)
         Magpie-Multilingual.EN-US.Leo    (male, casual)
         Magpie-Multilingual.EN-US.Sofia  (female, warm)
         Magpie-Multilingual.EN-US.Mia    (female, neutral)

═══════════════════════════════════════════════════════════
DB CHANGES
═══════════════════════════════════════════════════════════

Add to backend/app/models/scenario.py:
  vishing_audio_url    = db.Column(db.String(2000), nullable=True)
  vishing_audio_script = db.Column(db.Text, nullable=True)
  audio_source         = db.Column(db.String(50), nullable=True)
  audio_status         = db.Column(db.String(20), default='not_applicable')
    # 'not_applicable' | 'pending' | 'generated' | 'failed'
  audio_voice          = db.Column(db.String(100), nullable=True)

For all existing vishing scenarios: audio_status = 'pending'
For all other categories:           audio_status = 'not_applicable'
Run: flask db migrate && flask db upgrade


═══════════════════════════════════════════════════════════
FILE: backend/app/services/magpie_tts_service.py (COMPLETE)
═══════════════════════════════════════════════════════════

import io
import wave
import logging
from app.config import Config

logger = logging.getLogger(__name__)

# Cloud-hosted NVCF endpoint - no GPU required
MAGPIE_GRPC_SERVER = "grpc.nvcf.nvidia.com:443"
MAGPIE_MULTILINGUAL_FUNCTION_ID = "877104f7-e885-42b9-8de8-f6e4c6303969"
# Zeroshot function ID - will be provided when access is approved
MAGPIE_ZEROSHOT_FUNCTION_ID = ""  # Leave empty until access granted

VOICE_PROFILES = {
    'bank_official': {
        'voice': 'Magpie-Multilingual.EN-US.Jason',
        'language': 'en-US',
        'description': 'Authoritative male - bank/financial institution'
    },
    'it_helpdesk': {
        'voice': 'Magpie-Multilingual.EN-US.Leo',
        'language': 'en-US',
        'description': 'Casual male - IT helpdesk technician'
    },
    'executive': {
        'voice': 'Magpie-Multilingual.EN-US.Jason',
        'language': 'en-US',
        'description': 'Authoritative male - CEO/director'
    },
    'telecom_rep': {
        'voice': 'Magpie-Multilingual.EN-US.Leo',
        'language': 'en-US',
        'description': 'Casual male - telecom representative'
    },
    'government_official': {
        'voice': 'Magpie-Multilingual.EN-US.Aria',
        'language': 'en-US',
        'description': 'Professional female - government/inspector'
    },
    'default': {
        'voice': 'Magpie-Multilingual.EN-US.Jason',
        'language': 'en-US',
        'description': 'Default authoritative voice'
    }
}

def select_voice_for_scenario(scenario) -> dict:
    """Infer voice profile from scenario title and content keywords."""
    text = ((scenario.title or '') + ' ' + (scenario.content or '')).lower()
    if any(w in text for w in ['bank', 'nrb', 'payment', 'account', 'transaction', 'nic asia', 'nabil']):
        return VOICE_PROFILES['bank_official']
    if any(w in text for w in ['it', 'helpdesk', 'password reset', 'system', 'tech support']):
        return VOICE_PROFILES['it_helpdesk']
    if any(w in text for w in ['ceo', 'director', 'manager', 'executive', 'boss']):
        return VOICE_PROFILES['executive']
    if any(w in text for w in ['ncell', 'ntc', 'telecom', 'sim', 'number']):
        return VOICE_PROFILES['telecom_rep']
    if any(w in text for w in ['tax', 'ird', 'government', 'irb', 'revenue', 'inspector', 'official']):
        return VOICE_PROFILES['government_official']
    return VOICE_PROFILES['default']


def _pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 22050,
                channels: int = 1, sampwidth: int = 2) -> bytes:
    """Wrap raw PCM bytes in a WAV container."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


def synthesise_with_magpie(text: str, voice_profile: dict) -> bytes | None:
    """
    Call Magpie TTS Multilingual via cloud-hosted gRPC.
    Returns WAV bytes or None on failure.
    Uses nvidia-riva-client package.
    """
    if not Config.NVIDIA_API_KEY:
        logger.error("NVIDIA_API_KEY not set - cannot use Magpie TTS")
        return None

    try:
        import riva.client

        auth = riva.client.Auth(
            ssl_cert=None,
            use_ssl=True,
            uri=MAGPIE_GRPC_SERVER,
            metadata_args=[
                ["function-id", MAGPIE_MULTILINGUAL_FUNCTION_ID],
                ["authorization", f"Bearer {Config.NVIDIA_API_KEY}"]
            ]
        )

        tts_service = riva.client.SpeechSynthesisService(auth)

        req = riva.client.SynthesizeSpeechRequest()
        req.text = text
        req.language_code = voice_profile['language']
        req.voice_name = voice_profile['voice']
        req.encoding = riva.client.AudioEncoding.LINEAR_PCM
        req.sample_rate_hz = 22050

        # Use offline synthesis (entire audio returned at once)
        # For texts > ~200 words, use streaming to avoid 4MB gRPC limit
        if len(text) > 1000:
            # Streaming synthesis
            audio_chunks = []
            for chunk in tts_service.synthesize_online(req):
                audio_chunks.append(chunk.audio)
            pcm_bytes = b''.join(audio_chunks)
        else:
            resp = tts_service.synthesize(req)
            pcm_bytes = resp.audio

        wav_bytes = _pcm_to_wav(pcm_bytes)
        logger.info(f"[MAGPIE] Synthesised {len(pcm_bytes)} PCM bytes → {len(wav_bytes)} WAV bytes using {voice_profile['voice']}")
        return wav_bytes

    except ImportError:
        logger.error("nvidia-riva-client not installed. Run: pip install nvidia-riva-client")
        return None
    except Exception as e:
        logger.error(f"[MAGPIE] Synthesis failed with voice {voice_profile['voice']}: {e}")
        return None


def synthesise_zeroshot(text: str, reference_audio: bytes) -> bytes | None:
    """
    Magpie TTS Zeroshot - clone voice from ~5s audio sample.
    Only available when MAGPIE_ZEROSHOT_FUNCTION_ID is set (access approved).
    """
    if not MAGPIE_ZEROSHOT_FUNCTION_ID:
        logger.warning("[ZEROSHOT] Access not yet approved - MAGPIE_ZEROSHOT_FUNCTION_ID is empty")
        return None
    if not Config.NVIDIA_API_KEY:
        return None

    try:
        import riva.client

        auth = riva.client.Auth(
            ssl_cert=None,
            use_ssl=True,
            uri=MAGPIE_GRPC_SERVER,
            metadata_args=[
                ["function-id", MAGPIE_ZEROSHOT_FUNCTION_ID],
                ["authorization", f"Bearer {Config.NVIDIA_API_KEY}"]
            ]
        )
        tts_service = riva.client.SpeechSynthesisService(auth)

        req = riva.client.SynthesizeSpeechRequest()
        req.text = text
        req.language_code = "en-US"
        req.encoding = riva.client.AudioEncoding.LINEAR_PCM
        req.sample_rate_hz = 22050
        # Pass reference audio for voice cloning
        req.zero_shot_data.audio_prompt = reference_audio
        req.zero_shot_data.audio_prompt_transcript = ""  # optional hint

        resp = tts_service.synthesize(req)
        wav_bytes = _pcm_to_wav(resp.audio)
        logger.info(f"[ZEROSHOT] Cloned voice synthesis successful: {len(wav_bytes)} bytes")
        return wav_bytes

    except Exception as e:
        logger.error(f"[ZEROSHOT] Failed: {e}")
        return None


def synthesise_with_pyttsx3_fallback(text: str) -> bytes | None:
    """
    Last-resort local TTS using pyttsx3 (offline, zero API cost, always works).
    pip install pyttsx3
    Quality is robotic but functional for testing.
    """
    try:
        import pyttsx3
        import tempfile
        import os

        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # Prefer a male voice for attacker realism
        for voice in voices:
            if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 0.9)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            tmp_path = f.name

        engine.save_to_file(text, tmp_path)
        engine.runAndWait()

        with open(tmp_path, 'rb') as f:
            wav_bytes = f.read()
        os.unlink(tmp_path)

        logger.warning("[PYTTSX3] Using offline fallback TTS - robotic voice quality")
        return wav_bytes

    except ImportError:
        logger.error("pyttsx3 not installed. Run: pip install pyttsx3")
        return None
    except Exception as e:
        logger.error(f"[PYTTSX3] Fallback failed: {e}")
        return None


═══════════════════════════════════════════════════════════
FILE: backend/app/services/vishing_audio_orchestrator.py
═══════════════════════════════════════════════════════════

"""
Orchestrates vishing audio generation with full fallback chain:
  1. Magpie TTS Multilingual (cloud gRPC - primary)
  2. Magpie TTS Zeroshot (cloud gRPC - when access approved)
  3. pyttsx3 (local offline - last resort, always available)

Never fails silently. Always logs which service was used or why all failed.
"""
import logging
from app.services.magpie_tts_service import (
    synthesise_with_magpie,
    synthesise_zeroshot,
    synthesise_with_pyttsx3_fallback,
    select_voice_for_scenario,
    MAGPIE_ZEROSHOT_FUNCTION_ID,
)
from app.services.storage_service import upload_to_supabase
from app.services.kimi_generator import _extract_caller_lines

logger = logging.getLogger(__name__)


def generate_vishing_audio(scenario) -> tuple[str | None, str]:
    """
    Generate and store audio for a vishing scenario.
    Returns: (audio_url, audio_source) - url is None if all methods failed.
    audio_source is one of: 'magpie_multilingual', 'magpie_zeroshot', 'pyttsx3', 'failed'
    """
    if scenario.category != 'vishing':
        return None, 'not_applicable'

    if scenario.vishing_audio_url:
        return scenario.vishing_audio_url, scenario.audio_source or 'cached'

    # Extract the caller's spoken lines for TTS
    script = scenario.vishing_audio_script or ''
    if not script and scenario.content:
        # Fallback: extract from content
        script = _extract_caller_lines(scenario.content)
    if not script or len(script) < 20:
        logger.warning(f"[AUDIO] No usable script for scenario {scenario.id}")
        return None, 'failed'

    voice_profile = select_voice_for_scenario(scenario)
    logger.info(f"[AUDIO] Generating for scenario '{scenario.title}' using voice {voice_profile['voice']}")

    # Attempt 1: Magpie TTS Multilingual (cloud, primary)
    wav_bytes = synthesise_with_magpie(script, voice_profile)
    if wav_bytes:
        url = _upload_audio(wav_bytes, scenario.id)
        return url, 'magpie_multilingual'

    logger.warning(f"[AUDIO] Magpie Multilingual failed for scenario {scenario.id} - trying pyttsx3")

    # Attempt 2: pyttsx3 (local offline fallback - always available)
    wav_bytes = synthesise_with_pyttsx3_fallback(script)
    if wav_bytes:
        url = _upload_audio(wav_bytes, scenario.id)
        return url, 'pyttsx3_fallback'

    logger.error(f"[AUDIO] ALL audio generation methods failed for scenario {scenario.id}")
    return None, 'failed'


def generate_vishing_audio_zeroshot(scenario, reference_audio: bytes) -> tuple[str | None, str]:
    """
    Generate audio with voice cloning (Zeroshot).
    Only available when MAGPIE_ZEROSHOT_FUNCTION_ID is set.
    Falls back to standard Multilingual if zeroshot unavailable.
    """
    if not MAGPIE_ZEROSHOT_FUNCTION_ID:
        logger.info("[ZEROSHOT] Not available yet - using standard Multilingual")
        return generate_vishing_audio(scenario)

    script = scenario.vishing_audio_script or ''
    if not script:
        return generate_vishing_audio(scenario)

    wav_bytes = synthesise_zeroshot(script, reference_audio)
    if wav_bytes:
        url = _upload_audio(wav_bytes, scenario.id, suffix='_zeroshot')
        return url, 'magpie_zeroshot'

    logger.warning("[ZEROSHOT] Failed - falling back to Multilingual")
    return generate_vishing_audio(scenario)


def _upload_audio(wav_bytes: bytes, scenario_id: int, suffix: str = '') -> str | None:
    return upload_to_supabase(
        bucket='vishing-audio',
        filename=f"scenario_{scenario_id}_caller{suffix}.wav",
        content=wav_bytes,
        content_type='audio/wav'
    )


═══════════════════════════════════════════════════════════
ASYNC AUDIO GENERATION ON SCENARIO SERVE
═══════════════════════════════════════════════════════════

In backend/app/api/training.py, after building session response:

from threading import Thread
from flask import current_app
from app.services.vishing_audio_orchestrator import generate_vishing_audio
from app.extensions import db

def trigger_audio_async(scenario_id: int):
    """Non-blocking audio generation. Only runs for vishing scenarios."""
    def _generate():
        with current_app.app_context():
            from app.models.scenario import Scenario
            scenario = Scenario.query.get(scenario_id)
            if not scenario or scenario.category != 'vishing':
                return
            if scenario.audio_status not in ('pending', 'failed'):
                return
            url, source = generate_vishing_audio(scenario)
            scenario.vishing_audio_url = url
            scenario.audio_source = source
            scenario.audio_status = 'generated' if url else 'failed'
            scenario.audio_voice = source  # log which service was used
            db.session.commit()
            logger.info(f"[AUDIO] Scenario {scenario_id}: status={scenario.audio_status} source={source}")

    thread = Thread(target=_generate, daemon=True)
    thread.start()


═══════════════════════════════════════════════════════════
FRONTEND: VishingAudioPlayer.tsx (COMPLETE COMPONENT)
═══════════════════════════════════════════════════════════

FILE: frontend/src/components/training/VishingAudioPlayer.tsx

Design a realistic "incoming phone call" UI:

STATES:
  1. loading:   "Generating caller audio..." - pulsing phone icon animation
  2. ready:     Phone call card UI - "INCOMING CALL" header, caller persona name,
                phone ring animation, [ANSWER CALL] button (prominent, green)
  3. playing:   Call active UI - animated waveform bars (CSS), timer counting up,
                "End Call" button, caller name displayed
  4. completed: "Call Ended" message - then reveal the answer options below
                "View Transcript" toggle button (shows call_script text)

IMPORTANT UX:
  - Answer options (MCQ) are HIDDEN until audio has played at least 80%
  - A "Skip Audio" link is always visible (some users can't hear audio)
  - Clicking Skip immediately reveals answer options
  - After call ends, "Replay" button available

Audio controls:
  - HTML <audio> element with src={scenario.vishing_audio_url}
  - Track progress via onTimeUpdate → reveal options at 80%
  - Playback rate selector: 0.75x, 1x, 1.25x (accessibility)
  - Volume control slider

Visual style (dark card):
  - Background: dark grey card (#1a1a2e or similar)
  - Green "CALL ACTIVE" indicator dot (pulsing CSS)
  - Phone icon from lucide-react
  - Caller name in large font, "Unknown Caller" if persona not set
  - Waveform: 4-6 animated bars during playback (CSS keyframe animation)
  - Framer Motion for transitions between states

In ScenarioCard.tsx:
  If scenario.category === 'vishing':
    Render <VishingAudioPlayer /> ABOVE the scenario content
    Pass: audio_url, audio_status, caller_persona, content
    The scenario text still shows (below the player)
    Answer options: controlled by VishingAudioPlayer state


═══════════════════════════════════════════════════════════
ADMIN ENDPOINTS
═══════════════════════════════════════════════════════════

POST /api/v1/admin/generate-audio
  Auth: admin only
  Body: {"scenario_ids": [list]} OR {"category": "vishing"}
  For each: calls generate_vishing_audio() synchronously
  Returns: {"generated": N, "failed": K, "sources_used": {"magpie_multilingual": N, "pyttsx3_fallback": K}}

POST /api/v1/admin/generate-zeroshot-audio
  Auth: admin only
  Body: {"scenario_id": int, "voice_profile_id": str (future)}
  Returns 503 with message "Zeroshot access pending" if function-id not set

In admin panel ScenariosPage.tsx (vishing filter):
  Show: audio_status badge, audio_source badge (magpie/pyttsx3), preview button
  "Generate Missing Audio" button → POST /api/v1/admin/generate-audio {"category":"vishing"}
  Audio preview: <audio controls src={vishing_audio_url} />


═══════════════════════════════════════════════════════════
DEPENDENCIES (add to requirements.txt)
═══════════════════════════════════════════════════════════

nvidia-riva-client>=2.14.0
pyttsx3>=2.90           # offline fallback TTS
google-genai>=0.8.0     # Gemini (NOT google-generativeai)
supabase>=2.10.0
openai>=1.82.0          # Kimi via NVIDIA NIM


═══════════════════════════════════════════════════════════
VERIFICATION CHECKLIST
═══════════════════════════════════════════════════════════
[ ] nvidia-riva-client installed: pip install nvidia-riva-client
[ ] pyttsx3 installed: pip install pyttsx3
[ ] magpie_tts_service.py uses riva.client.Auth with grpc.nvcf.nvidia.com:443
[ ] Function ID hardcoded: 877104f7-e885-42b9-8de8-f6e4c6303969
[ ] _pcm_to_wav() correctly wraps PCM in WAV container
[ ] Streaming used for texts > 1000 chars (avoids 4MB gRPC limit)
[ ] vishing_audio_orchestrator.py fallback chain works:
    Magpie → pyttsx3 (zeroshot slot reserved)
[ ] DB fields: vishing_audio_url, audio_status, audio_source, audio_voice
[ ] Migration ran
[ ] trigger_audio_async() non-blocking
[ ] VishingAudioPlayer.tsx hides answer options until 80% played
[ ] "Skip Audio" option always visible
[ ] Admin POST /api/v1/admin/generate-audio returns sources_used breakdown
[ ] Zeroshot endpoint returns 503 when function-id not set
[ ] Test CLI first: python talk.py --server grpc.nvcf.nvidia.com:443 --use-ssl ...
```

---
---

# COMPLETE .env REFERENCE

```bash
# ─── Existing (keep) ───────────────────────────────────────
DATABASE_URL=
SECRET_KEY=
JWT_SECRET_KEY=
ALIENVAULT_OTX_KEY=
URLSCAN_API_KEY=
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# ─── LLM Generation ────────────────────────────────────────
GEMINI_API_KEY=             # from aistudio.google.com (free)
# GEMINI_MODEL auto-set to gemini-3-flash-preview in Config
NVIDIA_API_KEY=nvapi-...    # from build.nvidia.com/settings/api-keys
# KIMI_MODEL auto-set to moonshotai/kimi-k2.6 in Config

# ─── Image Generation ──────────────────────────────────────
# Uses NVIDIA_API_KEY (same key, different endpoint)
MAX_IMAGES_PER_DAY=50       # daily credit guard

# ─── Voice Generation ──────────────────────────────────────
# Uses NVIDIA_API_KEY (same key, gRPC cloud endpoint)
# No MAGPIE_TTS_BASE_URL needed - it's cloud-hosted
# MAGPIE_ZEROSHOT_FUNCTION_ID - leave empty until access approved

# ─── Local Ollama Fallback (optional) ──────────────────────
OLLAMA_ENABLED=false        # set true if you run Ollama locally
OLLAMA_MODEL=llama3.2       # run: ollama pull llama3.2

# ─── REMOVED ───────────────────────────────────────────────
# PHISHTANK_API_KEY - deleted
# MAGPIE_TTS_BASE_URL - not needed (cloud-hosted)
# OPENAI_API_KEY - not needed (pyttsx3 is the fallback)
```

---

# render.yaml ADDITIONS

```yaml
envVars:
  # ... all existing vars ...
  - key: GEMINI_API_KEY
    sync: false
  - key: NVIDIA_API_KEY
    sync: false
  - key: MAX_IMAGES_PER_DAY
    value: "50"
  - key: OLLAMA_ENABLED
    value: "false"
  # REMOVE: PHISHTANK_API_KEY (delete this line entirely)
```

---

# COMPLETE requirements.txt ADDITIONS

```
# LLM Generation (EXACT packages - spelling matters)
google-genai>=0.8.0            # NOT google-generativeai - different package!
openai>=1.82.0                 # for Kimi via NVIDIA NIM (requests-based also fine)

# Voice Generation
nvidia-riva-client>=2.14.0    # Magpie TTS gRPC client
pyttsx3>=2.90                  # offline fallback TTS (no internet needed)

# Image/Storage
supabase>=2.10.0
```

---

# ARCHITECTURE DIAGRAM - Fallback Chain

```
SCENARIO GENERATION:
  Category = vishing?
    YES → Kimi K2.6 (kimi-k2.6 via integrate.api.nvidia.com) ──▶ parse ──▶ DB
          ↓ if fails
          Gemini 3 Flash (gemini-3-flash-preview) ──▶ parse ──▶ DB
          ↓ if fails
          Ollama local (llama3.2 via localhost:11434) ──▶ parse ──▶ DB
    NO →  Gemini 3 Flash ──▶ parse ──▶ DB
          ↓ if fails
          Kimi K2.6 ──▶ parse ──▶ DB
          ↓ if fails
          Ollama local ──▶ parse ──▶ DB

IMAGE GENERATION:
  FLUX.2-klein-4B (ai.api.nvidia.com) ──▶ base64 decode ──▶ Supabase ──▶ URL
  ↓ if fails / daily limit
  No image (graceful - category icon shown instead)

VOICE SYNTHESIS:
  Magpie TTS Multilingual (grpc.nvcf.nvidia.com:443) ──▶ PCM→WAV ──▶ Supabase ──▶ URL
  [RESERVED SLOT: Magpie TTS Zeroshot - same gRPC, different function-id, when approved]
  ↓ if Magpie fails
  pyttsx3 offline ──▶ WAV ──▶ Supabase ──▶ URL
  ↓ if pyttsx3 fails (rare - system TTS missing)
  No audio (graceful - text transcript shown instead)
```

---

**END OF AHRIP v2 COMBINED FINAL PROMPTS v2.0**
*6 Sequential Prompts · Exact API Implementations · Full Fallback Chains*
*Models: Gemini 3 Flash · Kimi K2.6 · FLUX.2-klein-4B · Magpie TTS Multilingual/Zeroshot · pyttsx3*
*BSc (Hons) Ethical Hacking & Cybersecurity - Softwarica × Coventry University*
