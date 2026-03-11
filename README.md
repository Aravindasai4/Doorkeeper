1. PROJECT OVERVIEW
What it is: DoorKeeper is a security configuration auditing tool. You give it a JSON file that describes a system's setup — its network, ports, authentication method, encryption, logging, and backup policy — and it evaluates that configuration against a ruleset of security best practices.

Problem it solves: Security misconfigurations are one of the leading causes of breaches. DoorKeeper gives developers and sysadmins a fast, zero-setup way to check whether a system's config follows secure standards before deploying.

Target user: Developers, DevOps engineers, and security teams who want to audit infrastructure or application configs without running a full penetration test or third-party scanner.

How it works at a high level: The user submits a JSON config → the engine runs it through a set of rules → findings are returned with severity ratings and specific fix instructions.

2. TECHNICAL STACK
Frontend
Tool	Role
Alpine.js 3.x	Reactive UI state (no build step required)
Vanilla JS	All scan logic, validation, storage
CSS Variables	Full light/dark theming
Browser LocalStorage	Persisting scan history client-side
Google Fonts (Inter)	Typography
Backend
Tool	Role
FastAPI	REST API framework (Python)
Uvicorn	ASGI server running on port 5000
Pydantic v2	Schema modeling and request validation
Python standard library	All rule logic, no external ML/AI deps
Storage
Frontend: Browser localStorage, key doorkeeper_recent_scans, capped at 10 entries
Backend: In-memory Python dictionary (no database — intentional for demo)
AI/ML
None. The "AI simulation" in the backend (ai_simulation.py) generates hardcoded contextual text based on findings — it is not a real model call.
3. CORE FUNCTIONALITY
What "DoorKeeper" means here: It's a configuration gate — a checker that stands at the door of your infrastructure and says whether the configuration is safe to let through. It is not an authentication system, not a rate limiter, not a reverse proxy. It is a static security auditor.

What it guards: System configuration files. Specifically the security posture defined by:

Network setup (ports, encryption protocol)
Authentication method and password policy
Logging and audit trail settings
Backup and disaster recovery settings
How it makes decisions: Pure rule-based logic. Each rule is an independent function that reads specific keys from the config dict and compares values against hardcoded thresholds. No scoring model, no ML — deterministic pass/fail per rule.

4. ARCHITECTURE & WORKFLOW
Frontend-only flow (what runs in production)
User Input (JSON)
      ↓
schema.js → ConfigSchema.validate()
  - Checks required fields, correct types
  - Returns errors array
      ↓
mock-scan.js → runMockScan()
  - Rule 1: ports.includes(80) && !ports.includes(443) → HTTPS not enforced
  - Rule 2: target.startsWith('http://') → unencrypted protocol
  - Rule 3: httpSecurityHeaders flag → checks for CSP, HSTS, X-Frame-Options
  - Rule 4: robotsTxt flag → admin path exposure
  - Rule 5: ports ∩ [21, 23, 3389, 5900] → insecure services
  - Determinism: scan ID and timestamp generated from hash of config string
      ↓
storage.js → ScanStorage.save()
  - Prepends result to localStorage array
  - Trims to 10 entries
      ↓
script.js (Alpine.js) → renders findings to UI
Backend flow (optional, not used by default)
POST /api/scan  →  RulesEngine.run_all_checks(config)
  - rule_1: password policy (min length 12, uppercase, numbers, special chars)
  - rule_2: encryption (SSL/TLS1.0/1.1 = CRITICAL, TLS1.2/1.3 = pass)
  - rule_3: open ports (risky list: 21,23,53,135,139,445,1433,3389,5432)
  - rule_4: auth method (mfa/2fa/oauth/saml = pass, password-only = MEDIUM)
  - rule_5: logging (enabled, valid level, audit trail, ≥30 day retention)
  - rule_6: backup (enabled, daily/hourly, encrypted, offsite, ≥30 day retention)
      ↓
ComplianceCalculator → severity-weighted score (0–100)
  Critical = -25pts, High = -20pts, Medium = -10pts, Low = -5pts
      ↓
AISimulation → generates contextual text summary (hardcoded templates)
      ↓
ExplanationEngine → loads fix guide from /fix_library/rule_N_fix.md
      ↓
GET /api/reports/{scan_id} → retrieves from in-memory dict
Key architectural note
The frontend and backend have different rule sets. The browser runs 5 network/HTTP-focused rules. The backend runs 6 deeper infrastructure rules (password policy, auth method, backup config, logging). They share the same UI but are separate engines.

5. KEY FEATURES
Configuration options (input schema)
{
  "target": "https://example.com",       // required
  "checks": {
    "ports": [80, 443],                  // optional — array of port numbers
    "httpSecurityHeaders": true,         // optional — trigger header checks
    "robotsTxt": true                    // optional — trigger robots.txt check
  },
  "tags": ["production"],               // optional — labels
  "note": "any string"                  // optional — free text
}
API endpoints (backend)
Method	Endpoint	Description
GET	/	Serves index.html
POST	/api/scan	Runs all 6 rules, returns findings + score
GET	/api/reports	Lists all in-memory scan reports
GET	/api/reports/{scan_id}	Retrieves one report by ID
GET	/static/*	Serves frontend assets
UI components
Drag-and-drop file upload zone
Real-time JSON validation with inline error display
Three built-in test presets (goodHttps, noHttps, robotsExposed)
Collapsible finding cards with severity pills and fix recommendations
Filter chips (All / Warning / Info)
Scan history table (last 10, stored locally)
Light/Dark theme toggle (persisted to localStorage)
Toast notifications
Keyboard shortcuts: Ctrl+Enter = run scan, Ctrl+Shift+F = format JSON
Processing model
Frontend scans: Async with a simulated 1.5–2s delay (deterministic based on target URL length)
Backend scans: Synchronous rule execution, in-memory result storage
No real-time/streaming — single request → full response
6. IMPLEMENTATION HIGHLIGHTS
Deterministic scan engine: The most deliberate design choice. The scan ID and timestamp are derived from a hash of the input config string using a bitwise rolling hash (hash = ((hash << 5) - hash) + charCode). This means identical configs always produce identical scan IDs, timestamps, and findings. This makes the tool reproducible and testable without a database.

No build toolchain: The entire frontend runs from plain .js files loaded via <script> tags. Alpine.js is loaded from CDN. No webpack, no npm, no compilation step — the whole UI is editable and deployable as static files.

Dual rule systems: Frontend and backend implement different but complementary security checks. The frontend covers network surface (HTTP/HTTPS, ports, headers). The backend covers system internals (auth, encryption standards, logging, backup). They could be unified but are currently independent.

Severity-weighted compliance scoring (backend): Rather than a simple pass/fail percentage, the backend deducts points by severity from a 100-point baseline. A single CRITICAL finding costs 25 points. This produces a more meaningful risk score than counting issues equally.

Markdown-based fix library: Each backend rule maps to a .md file in /fix_library/. This decouples remediation content from rule logic — you can update fix instructions without touching the rules engine code.

Relation to security governance: DoorKeeper is a lightweight implementation of the configuration-as-code security review pattern — the same category of tooling as tfsec, checkov, and kube-bench, but simplified for demo and educational use rather than production enforcement.
