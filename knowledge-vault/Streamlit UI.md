---
tags: [component, frontend, streamlit, chart, form]
aliases: [Frontend, UI, Dashboard]
---

# Streamlit UI

The user-facing web interface for the Investment Advisory AI Agent.

## Responsibilities
- Collects [[User Profile]] (age, income, savings, risk tolerance, goal)
- Calls [[Rule Engine]] for allocation recommendations
- Renders pie/bar charts of portfolio allocation
- Displays [[Disclaimer]] prominently

## Port
Runs on `:8501` (default Streamlit port).

## Related Notes
- [[User Profile]]
- [[Rule Engine]]
- [[Disclaimer]]
- [[MCP Server]]
