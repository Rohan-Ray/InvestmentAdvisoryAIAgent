---
tags: [component, backend, python, allocation]
aliases: [Rule-based Engine, Allocation Engine]
---

# Rule Engine

The backend logic that maps a [[User Profile]] to investment allocations.

## How It Works
1. Receives `age`, `income`, `savings`, `risk_profile`, `goal_horizon`
2. Applies deterministic rules to produce percentage allocations
3. Returns recommendations for: [[Fixed Deposit]], [[Recurring Deposit]], [[Bonds]], [[Mutual Funds]], [[Equity]]

## Exposure
- Exposed via [[MCP Server]] as callable tools
- Called directly by [[Streamlit UI]]

## Related Notes
- [[User Profile]]
- [[MCP Server]]
- [[RAG Engine]]
- [[Risk Profiles]]
