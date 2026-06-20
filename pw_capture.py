from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import sys

SCREENSHOT_PATH = r"c:\Pwc_Learning\ClaudePlayground\InvestmentAdvisoryAIAgent-main\InvestmentAdvisoryAIAgent-main\screenshots\01_advisory_home.png"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()

    print("Step 1: Navigating to http://localhost:8501 ...")
    try:
        page.goto("http://localhost:8501", timeout=30000)
        print("  -> Navigation complete")
    except Exception as e:
        print(f"  -> Navigation error: {e}")

    print("Step 2: Waiting for 'Investment Advisory AI Agent' text (timeout=15000ms)...")
    try:
        page.wait_for_selector("text=Investment Advisory AI Agent", timeout=15000)
        print("  -> FOUND: Title text 'Investment Advisory AI Agent'")
    except PWTimeout:
        print("  -> WARN: Title text not found within 15s, proceeding anyway")
    except Exception as e:
        print(f"  -> ERROR waiting for selector: {e}")

    # Extra wait for Streamlit to fully render
    page.wait_for_timeout(2000)

    print("Step 3: Taking full-page screenshot...")
    try:
        page.screenshot(path=SCREENSHOT_PATH, full_page=True)
        print(f"  -> Screenshot saved: {SCREENSHOT_PATH}")
    except Exception as e:
        print(f"  -> Screenshot error: {e}")

    print("Step 4: Extracting all visible text...")
    try:
        # Get full inner text of the body
        body_text = page.evaluate("""() => {
            const allNodes = [];
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode: (node) => {
                        const parent = node.parentElement;
                        if (!parent) return NodeFilter.FILTER_REJECT;
                        const style = window.getComputedStyle(parent);
                        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0')
                            return NodeFilter.FILTER_REJECT;
                        const text = node.textContent.trim();
                        if (!text) return NodeFilter.FILTER_REJECT;
                        return NodeFilter.FILTER_ACCEPT;
                    }
                }
            );
            let node;
            while ((node = walker.nextNode())) {
                const t = node.textContent.trim();
                if (t) allNodes.push(t);
            }
            return allNodes;
        }""")

        print("\n=== ALL VISIBLE TEXT ON PAGE ===")
        for line in body_text:
            print(f"  {line}")
    except Exception as e:
        print(f"  -> Error extracting text: {e}")

    print("\nStep 5: Extracting UI elements...")
    try:
        elements = page.evaluate("""() => {
            const result = {buttons: [], inputs: [], dropdowns: [], links: [], headings: [], labels: [], alerts: []};

            // Buttons
            document.querySelectorAll('button, [role="button"], .stButton button').forEach(b => {
                const t = b.textContent.trim();
                if (t) result.buttons.push(t);
            });

            // Inputs
            document.querySelectorAll('input, textarea').forEach(inp => {
                result.inputs.push({
                    type: inp.type,
                    placeholder: inp.placeholder || '',
                    id: inp.id || '',
                    name: inp.name || '',
                    value: inp.value || ''
                });
            });

            // Selects
            document.querySelectorAll('select').forEach(s => {
                const opts = Array.from(s.options).map(o => o.text);
                result.dropdowns.push({id: s.id || '', options: opts});
            });

            // Streamlit selectbox (custom dropdowns)
            document.querySelectorAll('[data-testid="stSelectbox"]').forEach(sb => {
                result.dropdowns.push('Streamlit Selectbox: ' + sb.textContent.trim().substring(0, 100));
            });

            // Headings
            document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
                result.headings.push(h.tagName + ': ' + h.textContent.trim());
            });

            // Streamlit alerts/errors
            document.querySelectorAll('.stAlert, .stException, [data-testid="stNotificationContentError"], [data-testid="stNotificationContentWarning"], [data-testid="stNotificationContentInfo"]').forEach(a => {
                result.alerts.push(a.textContent.trim().substring(0, 200));
            });

            return result;
        }""")

        print("\n=== UI ELEMENTS ===")
        print(f"\nHEADINGS ({len(elements['headings'])}):")
        for h in elements['headings']:
            print(f"  {h}")

        print(f"\nBUTTONS ({len(elements['buttons'])}):")
        for b in elements['buttons']:
            print(f"  [{b}]")

        print(f"\nINPUTS ({len(elements['inputs'])}):")
        for i in elements['inputs']:
            print(f"  type={i['type']} placeholder=\"{i['placeholder']}\" id=\"{i['id']}\"")

        print(f"\nDROPDOWNS/SELECTBOXES ({len(elements['dropdowns'])}):")
        for d in elements['dropdowns']:
            if isinstance(d, dict):
                print(f"  id={d['id']} options={d['options']}")
            else:
                print(f"  {d}")

        if elements['alerts']:
            print(f"\nALERTS/ERRORS ({len(elements['alerts'])}):")
            for a in elements['alerts']:
                print(f"  ALERT: {a}")
        else:
            print("\nNO ALERTS OR ERRORS DETECTED")

    except Exception as e:
        print(f"  -> Error extracting elements: {e}")

    # Get page title
    print(f"\n=== PAGE TITLE: {page.title()} ===")
    print(f"=== PAGE URL: {page.url} ===")

    browser.close()
    print("\nDone.")
