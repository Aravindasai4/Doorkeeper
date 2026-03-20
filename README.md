# DoorKeeper

> A browser-based security configuration auditing tool. Paste a JSON config, get a full security report — no backend, no setup, no data leaves your machine.

---

## Table of Contents

- [Business Value](#business-value)
- [What It Does](#what-it-does)
- [Live Demo](#live-demo)
- [Technical Stack](#technical-stack)
- [Architecture & Data Flow](#architecture--data-flow)
- [Configuration Schema](#configuration-schema)
- [Sample Scan Output](#sample-scan-output)
- [API Endpoints](#api-endpoints-backend)
- [File Structure](#file-structure)
- [Key Features](#key-features)
- [Implementation Highlights](#implementation-highlights)
- [Governance Framework Mappings](#governance-framework-mappings)
- [Roadmap & Integration](#roadmap--integration)
- [Themes](#themes)
- [License](#license)

---

## Business Value

Security misconfigurations cause **68% of cloud breaches** (IBM Cost of a Data Breach, 2023). Most teams catch them late — after deployment, during an incident, or in a compliance audit.

DoorKeeper moves that check earlier. Drop in a JSON config before you deploy and get an instant, structured report: what's misconfigured, how severe it is, and exactly how to fix it. No agents to install, no credentials to hand over, no data leaves the browser.

For AI systems specifically, DoorKeeper is one of the few open tools that checks model governance controls — version pinning, output logging, human-in-the-loop thresholds, and bias monitoring — mapped directly to NIST AI RMF and ISO 42001.

---

## What It Does

DoorKeeper evaluates system configuration files against a ruleset of security best practices. You describe your infrastructure in JSON — ports, authentication, encryption, logging, backup policy, and AI model controls — and DoorKeeper tells you what's misconfigured, how severe it is, and how to fix it.

**Target users:** Developers, DevOps engineers, security teams, and AI governance practitioners who want to check infrastructure or application configs without running a full penetration test or third-party scanner.

---

## Live Demo

1. Open the app
2. Click **Use Secure Sample** or **Use Vulnerable Sample**
3. Click **Run Scan**
4. Review findings, expand each one for a recommended fix

---

## Technical Stack

### Frontend

| Tool | Role |
|------|------|
| **Alpine.js 3.x** | Reactive UI state — no build step required |
| **Vanilla JavaScript** | All scan logic, validation, and storage |
| **CSS Variables** | Full light/dark theming |
| **Browser LocalStorage** | Persists scan history client-side |
| **Google Fonts (Inter)** | Typography |

### Backend *(optional — app runs fully without it)*

| Tool | Role |
|------|------|
| **FastAPI** | Python REST API framework |
| **Uvicorn** | ASGI server on port 5000 |
| **Pydantic v2** | Request schema modeling and validation |

### Storage
- **Frontend:** `localStorage` under key `doorkeeper_recent_scans`, capped at 10 entries
- **Backend:** In-memory Python dict (intentional for demo — no database dependency)

### AI/ML
None. The `ai_simulation.py` module generates contextual text from hardcoded templates based on findings — it is not a live model call.

---

## Architecture & Data Flow

### Frontend-only flow *(production)*

```
User Input (JSON)
      │
      ▼
schema.js → ConfigSchema.validate()
  Checks required fields and correct types
      │
      ▼
mock-scan.js → runMockScan()
  Rule 1 │ ports.includes(80) && !ports.includes(443)  → HTTPS not enforced
  Rule 2 │ target.startsWith('http://')                → Unencrypted protocol
  Rule 3 │ httpSecurityHeaders flag                    → CSP, HSTS, X-Frame-Options
  Rule 4 │ robotsTxt flag                              → Admin path exposure
  Rule 5 │ ports ∩ [21, 23, 3389, 5900]               → Insecure services open
      │
      ▼
storage.js → ScanStorage.save()
  Prepends result to localStorage array, trims to 10 entries
      │
      ▼
script.js (Alpine.js) → Renders findings to UI
```

### Backend flow *(optional)*

```
POST /api/scan
      │
      ▼
RulesEngine.run_all_checks(config)
  rule_1 │ Password policy       (min length 12, uppercase, numbers, special chars)
  rule_2 │ Encryption standard   (SSL/TLS1.0/1.1 = CRITICAL, TLS1.2/1.3 = pass)
  rule_3 │ Open ports            (risky: 21, 23, 53, 135, 139, 445, 1433, 3389, 5432)
  rule_4 │ Auth method           (MFA/OAuth/SAML = pass, password-only = MEDIUM)
  rule_5 │ Logging config        (enabled, valid level, audit trail, ≥30 day retention)
  rule_6 │ Backup settings       (enabled, daily/hourly, encrypted, offsite, ≥30 days)
  rule_7 │ AI model governance   (version pinning, output logging, human review threshold,
         │                        bias monitoring, data provenance)
         │                        → NIST AI RMF: GOVERN 1.1 │ ISO 42001: 6.1.2
      │
      ▼
ComplianceCalculator → severity-weighted score (0–100)
  Critical = −25 pts │ High = −20 pts │ Medium = −10 pts │ Low = −5 pts
      │
      ▼
ExplanationEngine → loads /fix_library/rule_N_fix.md
      │
      ▼
Response: { scan_id, findings, compliance_score, summary }
```

> **Note:** The frontend and backend implement separate but complementary rule sets. The frontend covers network surface (HTTP/HTTPS, ports, headers). The backend covers system internals (auth, encryption, logging, backup, and AI model governance). They share the same UI but are independent engines.

---

## Configuration Schema

### Standard config (frontend + backend rules 1–6)

```json
{
  "target": "https://example.com",
  "checks": {
    "ports": [80, 443],
    "httpSecurityHeaders": true,
    "robotsTxt": true
  },
  "tags": ["production", "webapp"],
  "note": "Optional description"
}
```

### AI model governance config (backend rule 7)

```json
{
  "ai_model": {
    "version_pinned": true,
    "model_version": "gpt-4-0613",
    "output_logging": true,
    "log_retention_days": 90,
    "human_review_threshold": 0.75,
    "bias_monitoring": true,
    "bias_evaluation_frequency": "monthly",
    "data_provenance": true,
    "training_dataset_version": "v2024-Q3"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target` | `string` | Yes | URL or hostname to scan |
| `checks.ports` | `number[]` | No | Port numbers to evaluate |
| `checks.httpSecurityHeaders` | `boolean` | No | Run HTTP security header checks |
| `checks.robotsTxt` | `boolean` | No | Check for robots.txt path exposure |
| `tags` | `string[]` | No | Labels for organizing scans |
| `note` | `string` | No | Free-text description |
| `ai_model.version_pinned` | `boolean` | No | Whether model version is locked |
| `ai_model.output_logging` | `boolean` | No | Whether model outputs are logged |
| `ai_model.human_review_threshold` | `number` | No | Confidence threshold for human review |
| `ai_model.bias_monitoring` | `boolean` | No | Whether bias monitoring is active |
| `ai_model.data_provenance` | `boolean` | No | Whether input data lineage is tracked |

---

## Sample Scan Output

Running a scan on a vulnerable config produces a structured JSON response:

```json
{
  "scan_id": "a3f9c1d2-7b4e-4a1f-9e8d-2c6b5f0e1a3d",
  "timestamp": "2025-03-20T14:32:01.443Z",
  "compliance_score": 42.5,
  "findings": [
    {
      "rule_id": "rule_2",
      "rule_name": "Encryption Standards",
      "severity": "critical",
      "passed": false,
      "message": "Weak encryption protocol detected: TLS1.0",
      "fix_suggestion": "Upgrade to TLS 1.2 or TLS 1.3. Disable SSL, TLS 1.0, and TLS 1.1.",
      "affected_items": ["network.encryption"]
    },
    {
      "rule_id": "rule_4",
      "rule_name": "Authentication Method Security",
      "severity": "medium",
      "passed": false,
      "message": "Password-only authentication is not recommended",
      "fix_suggestion": "Implement MFA using TOTP, SMS, or hardware tokens.",
      "affected_items": ["authentication.method"]
    },
    {
      "rule_id": "rule_7",
      "rule_name": "AI Model Governance Controls",
      "severity": "high",
      "passed": false,
      "message": "AI governance issues found: Model version is not pinned; Output logging disabled; No human-in-the-loop threshold defined",
      "fix_suggestion": "See fix_library/rule_7_fix.md",
      "affected_items": ["ai_model", "NIST AI RMF: GOVERN 1.1", "ISO 42001: 6.1.2"]
    }
  ]
}
```

---

## API Endpoints *(backend)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves `index.html` |
| `POST` | `/api/scan` | Runs all 7 rules, returns findings + compliance score |
| `GET` | `/api/reports` | Lists all in-memory scan reports |
| `GET` | `/api/reports/{scan_id}` | Retrieves one report by ID |
| `GET` | `/static/*` | Serves frontend assets |

---

## File Structure

```
door_keeper_frontend/
├── index.html          # UI structure and Alpine.js bindings
├── styles.css          # Light/dark theming via CSS variables
├── script.js           # App controller and state management
├── schema.js           # JSON config schema validator
├── mock-scan.js        # Deterministic client-side scan engine
└── storage.js          # LocalStorage wrapper for scan history

door_keeper_backend/
├── main.py             # FastAPI app and route definitions
├── rules_engine.py     # 7 security rule implementations
├── compliance.py       # Severity-weighted score calculation
├── ai_simulation.py    # Contextual summary generation
├── explain.py          # Markdown fix guide loader
├── models/
│   └── schemas.py      # Pydantic models (Finding, ScanRequest, ScanResponse)
└── fix_library/
    └── rule_*_fix.md   # Per-rule remediation guides (rules 1–7)
```

---

## Key Features

- **Drag-and-drop upload** — drop a `.json` file directly onto the upload zone
- **Real-time validation** — JSON syntax and schema errors shown inline as you type
- **Built-in test presets** — Secure, Vulnerable, and Robots-exposed sample configs
- **Collapsible findings** — each finding expands to show a specific recommended fix
- **Filter by severity** — view All, Critical, Warning, or Info findings
- **Scan history** — last 10 scans saved locally; re-open or delete any entry
- **Light/Dark mode** — toggle persisted to localStorage
- **Keyboard shortcuts** — `Ctrl+Enter` to run scan, `Ctrl+Shift+F` to format JSON
- **No installation** — runs from static files, no build process
- **AI governance checks** — Rule 7 evaluates AI model configs against NIST AI RMF and ISO 42001

---

## Implementation Highlights

**Deterministic scan engine**
Scan IDs and timestamps are derived from a bitwise rolling hash of the input config string. Identical configs always produce identical results — making the tool reproducible and testable without a database or random state.

**No build toolchain**
The entire frontend runs from plain `.js` files loaded via `<script>` tags. Alpine.js is pulled from CDN. No webpack, no npm, no compilation — the whole UI is editable and deployable as static files.

**Severity-weighted compliance scoring**
Rather than a simple pass/fail percentage, the backend deducts points by severity from a 100-point baseline. A single CRITICAL finding costs 25 points, producing a more meaningful risk score than counting issues equally.

**Markdown-based fix library**
Each backend rule maps to a `.md` file in `/fix_library/`. Remediation content is fully decoupled from rule logic — fix instructions can be updated without touching the rules engine.

**AI model governance (Rule 7)**
Rule 7 checks AI system configurations against five controls drawn from the NIST AI Risk Management Framework (GOVERN 1.1) and ISO/IEC 42001:2023 (6.1.2): model version pinning, output logging, human-in-the-loop thresholds, bias monitoring, and data provenance tracking. Each failed control maps to a specific remediation guide in `fix_library/rule_7_fix.md`.

**Zero network dependency for core features**
The frontend scan engine, validator, and storage all work completely offline. No API calls are made during a scan. Data never leaves the browser.

---

## Governance Framework Mappings

| Rule | Control | Framework Reference |
|------|---------|-------------------|
| Rule 7 | Model version governance | NIST AI RMF: GOVERN 1.1 |
| Rule 7 | Output auditability | ISO 42001: 6.1.2 |
| Rule 7 | Human oversight | EU AI Act: Article 14 |
| Rule 7 | Bias and fairness monitoring | NIST AI RMF: MANAGE 2.2 |
| Rule 7 | Data lineage | ISO 42001: 8.4 |

---

## Roadmap & Integration

DoorKeeper is the **Identity & Access Layer** of a 4-part AI governance stack being built as an open portfolio:

| Layer | Project | Status |
|-------|---------|--------|
| 1 — Identity & Access | **DoorKeeper** ← you are here | ✅ Complete |
| 2 — Monitoring & Observability | AI Governance Dashboard | ✅ Complete |
| 3 — Safety & Content Guardrails | Guardrails API (NLI model) | ✅ Complete |
| 4 — Security Posture | DevGuard | ✅ Complete |

**Planned enhancements:**
- Wire frontend directly to backend API (replace mock scan engine)
- Add a live AI governance config preset to the frontend test suite
- Export scan reports as PDF for compliance documentation
- Add GitHub Actions integration to run scans on config file changes in CI

> Scan results from DoorKeeper can feed directly into the **AI Governance Dashboard** for cross-project risk aggregation and compliance scoring.

---

## Themes

| | Light | Dark |
|--|-------|------|
| **Background** | `#F3F4F6` | `#1C1F23` |
| **Card** | `#FFFFFF` | `#262A31` |
| **Accent** | `#2C7DF0` | `#6CA5FF` |
| **Text** | `#1F2933` | `#E7E9EC` |

---

## License

MIT
