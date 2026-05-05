# Claude Code Plugins Reference

Installed plugins as of 2026-05. Manage at: Claude Code → Settings → Plugins.

---

## Enabled Plugins

### 1. caveman (`caveman@caveman`)
**Repo:** [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)  
**Status:** Enabled  
**Purpose:** Ultra-compressed response style — drops articles, filler words, verbose phrasing.

| Skill | Trigger |
|---|---|
| `/caveman` | Activate caveman communication mode |
| `/caveman-cn` | Chinese caveman mode |
| `/caveman-es` | Spanish caveman mode |
| `/compress` | Compress verbose text |

---

### 2. document-skills (`document-skills@anthropic-agent-skills`)
**Repo:** [anthropics/skills](https://github.com/anthropics/skills)  
**Status:** Enabled  
**Purpose:** Official Anthropic document creation and manipulation skills.

| Skill | What it does |
|---|---|
| `/algorithmic-art` | Generative/algorithmic art via p5.js with seeded randomness |
| `/brand-guidelines` | Apply Anthropic brand colors and typography to artifacts |
| `/canvas-design` | Create posters, visual art, static designs → PNG/PDF |
| `/claude-api` | Build and debug Claude API / Anthropic SDK apps (includes prompt caching) |
| `/doc-coauthoring` | Structured co-authoring workflow for docs, proposals, specs |
| `/docx` | Create, read, edit Word (.docx) files |
| `/frontend-design` | Production-grade web UI — React, Tailwind, HTML/CSS |
| `/internal-comms` | Internal communications: status reports, leadership updates, incident reports |
| `/mcp-builder` | Build MCP servers (Python FastMCP or Node/TS SDK) |
| `/pdf` | Read, merge, split, OCR, fill, encrypt PDF files |
| `/pptx` | Create, edit, parse PowerPoint (.pptx) decks |
| `/skill-creator` | Create, modify, benchmark, and eval skills |
| `/slack-gif-creator` | Create animated GIFs optimized for Slack |
| `/theme-factory` | Apply/generate themes (10 presets) to artifacts |
| `/web-artifacts-builder` | Multi-component HTML artifacts with React + shadcn/ui |
| `/webapp-testing` | Test local web apps via Playwright — screenshots, DOM, logs |
| `/xlsx` | Create, edit, clean spreadsheet (.xlsx/.csv/.tsv) files |

---

### 3. context-mode (`context-mode@context-mode`)
**Repo:** [mksglu/context-mode](https://github.com/mksglu/context-mode)  
**Status:** Enabled (project-scoped)  
**Purpose:** Sandbox full-text search for large outputs — prevents context exhaustion on big repos, build logs, multi-file analysis.

| Skill / Command | What it does |
|---|---|
| `/context-mode` | Main context-mode usage guide |
| `/context-mode-ops` | Operational commands reference |
| `ctx stats` / `/ctx-stats` | Show context savings metrics |
| `ctx doctor` / `/ctx-doctor` | Diagnose context-mode health |
| `ctx purge` / `/ctx-purge` | Wipe knowledge base (irreversible) |
| `ctx upgrade` / `/ctx-upgrade` | Upgrade context-mode to latest |
| `ctx insight` / `/ctx-insight` | Insights from indexed data |

**MCP tools (auto-allowlisted):**
- `ctx_batch_execute` — run commands + auto-index output
- `ctx_search` — FTS5 search across indexed content
- `ctx_execute` — run code for analysis/processing
- `ctx_execute_file` — run file-based code
- `ctx_fetch_and_index` — fetch URL and index content
- `ctx_index` — manually index content
- `ctx_stats`, `ctx_doctor`, `ctx_purge`, `ctx_upgrade`, `ctx_insight`

---

### 4. aws-serverless (`aws-serverless@claude-plugins-official`)
**Repo:** Official Claude plugins  
**Status:** Enabled  
**Purpose:** AWS serverless architecture and deployment skills.

| Skill | What it does |
|---|---|
| `/api-gateway` | Design and configure AWS API Gateway |
| `/aws-lambda` | Build, debug, optimize Lambda functions |
| `/aws-lambda-durable-functions` | Durable/stateful Lambda patterns |
| `/aws-serverless-deployment` | Deploy serverless apps (SAM, CDK, Serverless Framework) |

---

## Disabled Plugins

### 5. agent-skills (`agent-skills@addy-agent-skills`)
**Repo:** [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)  
**Author:** Addy Osmani (Google Chrome engineering lead)  
**Status:** Disabled  
**Purpose:** Production-grade engineering skills scaffolding — Google ADK-style lifecycle enforcement for AI coding agents. Maps the full dev lifecycle (Spec → Plan → Build → Test → Review → Ship) to skills that auto-activate by intent. Designed to work with Claude Code, Cursor, Copilot, and OpenCode.

**Lifecycle commands:**

| Phase | Command | Skills activated |
|---|---|---|
| Define | `/spec` | `spec-driven-development` |
| Plan | `/plan` | `planning-and-task-breakdown` |
| Build | `/build` | `incremental-implementation` + `test-driven-development` |
| Verify | `/test` | `debugging-and-error-recovery` |
| Review | `/review` | `code-review-and-quality` |
| Simplify | `/code-simplify` | `code-simplification` |
| Ship | `/ship` | `shipping-and-launch` |

| Skill | What it does |
|---|---|
| `/api-and-interface-design` | Stable API and interface design patterns |
| `/browser-testing-with-devtools` | Real-browser testing via Chrome DevTools MCP |
| `/ci-cd-and-automation` | CI/CD pipeline setup and quality gates |
| `/code-review-and-quality` | Multi-axis code review before merging |
| `/code-simplification` | Refactor for clarity without behavior change |
| `/context-engineering` | Optimize agent context and rules files |
| `/debugging-and-error-recovery` | Systematic root-cause debugging |
| `/deprecation-and-migration` | Manage API/system deprecation and migration |
| `/documentation-and-adrs` | Record architectural decisions and docs |
| `/frontend-ui-engineering` | Production-quality UI components and layouts |
| `/git-workflow-and-versioning` | Commit, branch, conflict resolution practices |
| `/idea-refine` | Iterative divergent + convergent idea refinement |
| `/incremental-implementation` | Break large changes into safe incremental steps |
| `/performance-optimization` | Profile and fix performance bottlenecks |
| `/planning-and-task-breakdown` | Break specs into ordered, parallelizable tasks |
| `/security-and-hardening` | Harden code against OWASP + injection vulnerabilities |
| `/shipping-and-launch` | Pre-launch checklist, monitoring, rollback strategy |
| `/source-driven-development` | Source-cited code grounded in official docs |
| `/spec-driven-development` | Write spec before code for new features |
| `/test-driven-development` | Test-first development for any logic change |
| `/using-agent-skills` | Meta-skill: discover and invoke the right skill |

### 6. context-engineering (`context-engineering@context-engineering-marketplace`)
**Repo:** [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)  
**Status:** Disabled  
**Purpose:** Context engineering patterns for agent prompting and session management.

---

## Also Installed (MCP server)

| Server | Config | Purpose |
|---|---|---|
| `my-server` | `C:/Users/giris/Documents/Claude/Projects/my-mcp-server/server.py` | Personal MCP server (local) |

---

## Template Recommendations

Skills worth adding to `claude-code-template` users' awareness:

| Plugin | Skills to highlight | Why |
|---|---|---|
| `document-skills` | `/claude-api`, `/mcp-builder`, `/doc-coauthoring`, `/webapp-testing` | High utility for AI + web projects |
| `aws-serverless` | `/aws-lambda`, `/aws-serverless-deployment` | Common deployment target |
| `agent-skills` (disabled) | `/spec`, `/plan`, `/build`, `/ship` lifecycle commands | Google ADK-style scaffold; auto-activates skills by intent — enable for teams wanting enforced dev lifecycle |
| `context-mode` | All `ctx_*` tools | Essential for large codebases; pre-allowlisted in template's `.claude/settings.json` |

> **Overlap note:** `agent-skills` `/code-review-and-quality` and `/documentation-and-adrs` overlap with this template's built-in `/review` and `/adr` skills. The lifecycle `/spec` → `/ship` commands are additive and do not conflict. Enable `agent-skills` when you want enforced lifecycle scaffolding on top of the template's skills.
