const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  try {
    console.log('Navigating to http://localhost:8501 ...');
    await page.goto('http://localhost:8501', { timeout: 30000 });

    // Wait for the title text
    try {
      await page.waitForSelector('text=Investment Advisory AI Agent', { timeout: 15000 });
      console.log('FOUND: Investment Advisory AI Agent text');
    } catch (e) {
      console.log('WARN: Could not find title text within 15s, proceeding anyway...');
    }

    // Take full-page screenshot
    const screenshotPath = 'c:\Pwc_Learning\ClaudePlayground\InvestmentAdvisoryAIAgent-main\InvestmentAdvisoryAIAgent-main\screenshots\01_advisory_home.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log('Screenshot saved to: ' + screenshotPath);

    // Get all visible text
    const bodyText = await page.evaluate(() => {
      // Get all text nodes visible on the page
      const allText = [];
      
      // Get page title
      allText.push('=== PAGE TITLE: ' + document.title + ' ===');
      
      // Get all text content
      const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        {
          acceptNode: (node) => {
            const parent = node.parentElement;
            if (!parent) return NodeFilter.FILTER_REJECT;
            const style = window.getComputedStyle(parent);
            if (style.display === 'none' || style.visibility === 'hidden') return NodeFilter.FILTER_REJECT;
            const text = node.textContent.trim();
            if (!text) return NodeFilter.FILTER_REJECT;
            return NodeFilter.FILTER_ACCEPT;
          }
        }
      );
      
      let node;
      while ((node = walker.nextNode())) {
        const text = node.textContent.trim();
        if (text && text.length > 0) {
          allText.push(text);
        }
      }
      return allText.join('\n');
    });

    console.log('\n=== ALL VISIBLE TEXT ON PAGE ===');
    console.log(bodyText);

    // Get interactive elements
    const elements = await page.evaluate(() => {
      const result = [];
      
      // Buttons
      const buttons = document.querySelectorAll('button, [role="button"]');
      buttons.forEach(b => {
        const text = b.textContent.trim();
        if (text) result.push('BUTTON: ' + text);
      });
      
      // Inputs
      const inputs = document.querySelectorAll('input, textarea');
      inputs.forEach(inp => {
        const label = inp.placeholder || inp.name || inp.id || inp.type || 'unknown';
        result.push('INPUT: type=' + inp.type + ' placeholder="' + (inp.placeholder || '') + '" id="' + (inp.id || '') + '"');
      });
      
      // Selects / dropdowns
      const selects = document.querySelectorAll('select');
      selects.forEach(s => {
        const opts = Array.from(s.options).map(o => o.text).join(', ');
        result.push('DROPDOWN: id=' + (s.id || 'unknown') + ' options=[' + opts + ']');
      });
      
      // Links
      const links = document.querySelectorAll('a');
      links.forEach(a => {
        const text = a.textContent.trim();
        if (text) result.push('LINK: ' + text + ' href=' + a.href);
      });
      
      return result.join('\n');
    });

    console.log('\n=== UI ELEMENTS ===');
    console.log(elements);

    // Check for any error messages
    const errors = await page.evaluate(() => {
      const errTexts = [];
      const errorSelectors = ['.stException', '.stError', '[data-testid="stException"]', '.element-container .stAlert'];
      errorSelectors.forEach(sel => {
        const els = document.querySelectorAll(sel);
        els.forEach(el => errTexts.push('ERROR/ALERT: ' + el.textContent.trim()));
      });
      return errTexts.join('\n');
    });

    if (errors) {
      console.log('\n=== ERRORS/ALERTS ===');
      console.log(errors);
    } else {
      console.log('\n=== NO ERRORS DETECTED ===');
    }

  } catch (err) {
    console.error('FATAL ERROR: ' + err.message);
    // Still try to screenshot on error
    try {
      await page.screenshot({ path: 'c:\Pwc_Learning\ClaudePlayground\InvestmentAdvisoryAIAgent-main\InvestmentAdvisoryAIAgent-main\screenshots\01_advisory_home.png', fullPage: true });
      console.log('Error screenshot saved.');
    } catch (e2) {}
  }

  await browser.close();
})();
