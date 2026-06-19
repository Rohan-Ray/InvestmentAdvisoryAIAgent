# Investment Advisory AI Agent — Skills Registry

## Project Context
Beginner-friendly Investment Advisory AI Agent for banking customers built with Python + Streamlit.
Rule-based logic for investment category recommendations with educational disclaimers.

---

## Available Skills

Skill files live in `.claude/skills/`. Project-level skills below; global skills (`/code-review`, `/verify`, `/deep-research`, `/security-review`, `/simplify`) are provided by the Claude Code harness.

### `/run` → `.claude/skills/run/SKILL.md`
Launch the Streamlit application.
- Entry: `streamlit run src/frontend/app.py`
- Port: 8501
- Env: `INVESTMENT_APP_ENV=development`

### `/run-tests` → `.claude/skills/run-tests/SKILL.md`
Run the full pytest suite with short tracebacks.
- Used by: `backend-agent`, `p3-triage-agent`

### `/context-trim` → `.claude/skills/context-trim/SKILL.md`
Shared trimming policy for all sub-agents (≤150-word digest, keep 10 prompts, tag summary).
- Used by: all three agents

### `/triage` → `.claude/skills/triage/SKILL.md`
Full P3 cross-cutting review: quality gates, security checklist, performance checklist, report generation.
- Used by: `p3-triage-agent`

### `/code-review`
Run code quality review on changed files.
- Scope: `src/`, `mcp/`, `config/`
- Effort: medium
- Auto-fix: enabled for lint issues

### `/verify`
Verify a code change works end-to-end.
- Runs the app and validates investment rule logic
- Checks pie chart renders
- Validates disclaimer is visible

### `/deep-research`
Research investment domain knowledge.
- Use for: financial product definitions, regulatory disclaimers, risk categorisation
- Output to: `knowledge-vault/`

### `/security-review`
Review for security vulnerabilities.
- Focus: user input sanitisation, no real financial data storage
- Check: no PII logging

### `/simplify`
Simplify and clean up changed code.
- Target: rule engine logic in `src/backend/advisor.py`

---

## Sub-Agent Assignments

| Agent | Scope | Memory Budget |
|-------|-------|---------------|
| `frontend-agent` | `src/frontend/` | 12% of context |
| `backend-agent` | `src/backend/`, `mcp/` | 12% of context |
| `p3-triage-agent` | cross-cutting review | 8% of context |

---

## Plugin Registry

### Internal Tools
- `investment_rule_engine` — rule-based advisor logic
- `portfolio_allocator` — calculates % allocation
- `risk_profiler` — maps age+income+risk to profile
- `rag_retriever` — document retrieval for knowledge vault

### External (MCP)
- `filesystem` — read/write project files
- `investment-mcp` — custom MCP server at `mcp/server.py`

---

## Context Trimming Policy
- Sub-agents: store only summary of full history (≤12% corpus)
- Active window: latest 8-10 prompts
- Summary format: `[SUMMARY-vN] <150-word digest>`
- Trim trigger: when sub-agent context exceeds 80% of allocation
