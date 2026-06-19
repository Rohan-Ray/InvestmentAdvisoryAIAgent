---
name: triage
description: Full P3 triage review — code quality, security, and performance gates. Generates a dated triage report in docs/triage-reports/.
---

# Skill: triage

Cross-cutting review skill invoked by `p3-triage-agent`. Covers code quality, security, and performance, then writes a report.

## Code Quality Gates

1. Verify all investment allocations sum to 100%
2. Confirm disclaimer is present in both header and result sections
3. Check no real financial advice is given (no yield/return promises)
4. Validate input sanitisation: age 18–80, income > 0, savings ≤ income
5. Ensure no PII is logged

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No SQL injection surface (no DB in v1, but check future MCP)
- [ ] Input validation on all numeric fields
- [ ] No unrestricted file write paths
- [ ] Disclaimer text is immutable (not user-controlled)

## Performance Checklist

- [ ] Streamlit rerenders minimised (`st.cache_data` used where appropriate)
- [ ] RAG retrieval latency < 200ms
- [ ] MCP tool call latency < 500ms

## Report

Write to `docs/triage-reports/TRIAGE-{YYYY-MM-DD}.md` using this template:

```markdown
# Triage Report — {date}

## Summary

## Code Quality: PASS/FAIL/WARN

## Security: PASS/FAIL/WARN

## Performance: PASS/FAIL/WARN

## Open Issues

## Recommendations
```

## Post-Review Delegation

- Backend bug found → create task for `backend-agent`
- UI regression found → create task for `frontend-agent`
- Security issue → STOP and escalate to human reviewer
