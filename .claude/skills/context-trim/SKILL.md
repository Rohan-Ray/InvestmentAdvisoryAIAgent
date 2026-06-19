---
name: context-trim
description: Standard context trimming policy for all sub-agents when memory allocation exceeds 80%.
---

# Skill: context-trim

Shared trimming policy across all sub-agents. Apply when context usage exceeds 80% of the agent's allocated budget.

## Steps

1. Summarise all prior chat history into a ≤150-word digest
2. Keep only the latest 10 prompts in the active window; discard older turns
3. Tag the summary with: `[{AGENT_PREFIX}-SUMMARY-v{N}]`
   - Backend agent prefix: `BE`
   - Frontend agent prefix: `FE`
   - Triage agent prefix: `P3`

## Summary Format

```
[{PREFIX}-SUMMARY-v{N}]
<150-word digest covering: current task state, key decisions made, open issues, last known file state>
```

## Trigger Thresholds

| Agent | Budget | Trim at |
|-------|--------|---------|
| `frontend-agent` | 12% of context | >80% of 12% used |
| `backend-agent` | 12% of context | >80% of 12% used |
| `p3-triage-agent` | 8% of context | >80% of 8% used |
