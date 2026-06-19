---
tags: [entity, user, input, profile]
aliases: [Investor Profile, User Input]
---

# User Profile

The set of inputs collected from the user that drive all recommendations.

## Fields
| Field | Type | Notes |
|-------|------|-------|
| Age | integer | Affects long-horizon eligibility |
| Annual Income | ₹ | Determines investment capacity |
| Savings | ₹ | Initial corpus |
| Risk Tolerance | low / medium / high | Maps to [[Risk Profiles]] |
| Goal Horizon | short / medium / long | Maps to product suitability |

## Flow
`User Profile` → [[Rule Engine]] → allocation percentages → [[Streamlit UI]] chart

## Related Notes
- [[Rule Engine]]
- [[Streamlit UI]]
- [[Risk Profiles]]
