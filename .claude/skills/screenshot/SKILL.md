# /screenshot — Playwright Screenshot Skill

Captures screenshots of all running Investment Advisory app pages using the `playwright` MCP server.

## Trigger
`/screenshot`

## Prerequisites
- All three app services must be running (or this skill will start them):
  - **Port 8501** — Streamlit advisory app (`streamlit run src/frontend/app.py`)
  - **Port 8502** — Prometheus metrics exporter (`python observability/metrics_exporter.py`)
  - **Port 8503** — Knowledge Vault viewer (`python knowledge-vault/vault_viewer.py`)
- The `playwright` MCP server must be active (configured in `mcp/claude_mcp_config.json`)

## Output
All screenshots saved to `screenshots/` at the project root. Filenames:
- `screenshots/01_advisory_home.png` — Streamlit app landing page
- `screenshots/02_advisory_recommendation.png` — App with a filled-in profile + result rendered
- `screenshots/03_metrics_observability.png` — Prometheus metrics page (`:8502/metrics`)
- `screenshots/04_knowledge_vault_home.png` — Vault viewer sidebar + document view (`:8503`)
- `screenshots/05_knowledge_vault_graph.png` — Vault viewer with Graph View tab active (`:8503` graph tab)

## Steps (agent must follow exactly)

1. **Ensure `screenshots/` directory exists** — create it if absent.

2. **Capture Streamlit home** (`http://localhost:8501`):
   - Navigate to the page, wait for the title "Investment Advisory AI Agent" to be visible.
   - Take a full-page screenshot → `screenshots/01_advisory_home.png`.

3. **Capture Streamlit with recommendation**:
   - Fill Age = 35, Monthly Income = 75000, Monthly Savings = 15000.
   - Select Risk Appetite = "Medium", Goal Horizon = "Long-term".
   - Click "Get My Investment Plan".
   - Wait for the pie chart to appear.
   - Screenshot → `screenshots/02_advisory_recommendation.png`.

4. **Capture metrics page** (`http://localhost:8502/metrics`):
   - Navigate, wait for content containing `investment_recommendations_total`.
   - Screenshot → `screenshots/03_metrics_observability.png`.

5. **Capture Knowledge Vault home** (`http://localhost:8503`):
   - Navigate, wait for sidebar to load (element `.sidebar`).
   - Click the first note in the sidebar to load content.
   - Screenshot → `screenshots/04_knowledge_vault_home.png`.

6. **Capture Knowledge Vault graph view**:
   - On the same page, click the "Graph View" tab (text `🕸️ Graph View`).
   - Wait 1 second for the iframe to render.
   - Screenshot → `screenshots/05_knowledge_vault_graph.png`.

7. **Report** — list all saved screenshots with their file sizes.

## Notes
- Use `playwright_screenshot` tool with `fullPage: true` where possible.
- If a service is not running, report which port is unavailable and skip that screenshot rather than failing entirely.
- Viewport: 1280×800 for all captures.
