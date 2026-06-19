---
name: run-tests
description: Run the full pytest suite with short tracebacks and report pass/fail status.
---

# Skill: run-tests

Run the project's unit tests and surface failures.

## Command

```bash
python3 -m pytest tests/ --tb=short
```

## Output

- Print pass/fail counts
- Show short tracebacks for any failures
- Exit non-zero on failure (agents should treat non-zero as a blocking issue)

## When to use

- After any backend logic change
- Before generating a triage report
- As part of the p3-triage-agent gating step before a merge
