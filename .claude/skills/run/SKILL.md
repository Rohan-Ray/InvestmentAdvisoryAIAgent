---
name: run
description: Launch the Streamlit investment advisory app locally on port 8501.
---

# Skill: run

Start the Streamlit frontend for local development and verification.

## Command

```bash
INVESTMENT_APP_ENV=development streamlit run src/frontend/app.py
```

## Port

`8501` — open `http://localhost:8501` after launch.

## Verification steps after launch

1. App loads without errors
2. Input form renders (age, income, savings, risk tolerance, goal)
3. Submitting the form renders a Plotly pie chart
4. Allocation breakdown table shows rupee amounts
5. Educational disclaimer is visible in both header and result sections

## When to use

- After any frontend change
- During the `/verify` skill flow
- Any time `frontend-agent` needs to confirm UI state
