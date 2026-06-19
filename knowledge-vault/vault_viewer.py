"""
Lightweight web viewer for the Investment Knowledge Vault.
Renders Markdown notes with backlinks and the Graphify node/edge graph.
Serves on :8503
"""

import json
import os
import re
from pathlib import Path
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)
VAULT_DIR = Path(__file__).parent

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Investment Knowledge Vault</title>
<script src="https://unpkg.com/vis-network@9.1.9/dist/vis-network.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/vis-network@9.1.9/dist/vis-network.min.css"/>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #1e1e2e; color: #cdd6f4; margin: 0; }
  .container { display: flex; height: 100vh; }
  .sidebar { width: 260px; background: #181825; padding: 1rem;
             border-right: 1px solid #313244; overflow-y: auto; flex-shrink: 0; }
  .sidebar h2 { color: #cba6f7; font-size: 1rem; margin: 0 0 1rem; }
  .sidebar a { display: block; padding: 6px 10px; color: #89b4fa; text-decoration: none;
               border-radius: 6px; margin-bottom: 4px; font-size: 0.9rem; }
  .sidebar a:hover { background: #313244; }
  .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
  .tabs { display: flex; background: #181825; border-bottom: 1px solid #313244; }
  .tab { padding: 10px 20px; cursor: pointer; color: #6c7086; font-size: 0.9rem; }
  .tab.active { color: #cba6f7; border-bottom: 2px solid #cba6f7; }
  #content { flex: 1; padding: 2rem; overflow-y: auto; max-width: 860px; }
  #graph-view { flex: 1; display: none; }
  #graph-canvas { width: 100%; height: 100%; }
  h1,h2,h3 { color: #cba6f7; }
  code { background: #313244; padding: 2px 6px; border-radius: 4px; color: #a6e3a1; }
  pre code { display: block; padding: 1rem; font-size: 0.85rem; }
  table { border-collapse: collapse; width: 100%; }
  th { background: #313244; color: #cba6f7; padding: 8px 12px; text-align: left; }
  td { padding: 8px 12px; border-bottom: 1px solid #313244; }
  blockquote { border-left: 3px solid #f38ba8; padding-left: 1rem;
               color: #f38ba8; margin: 1rem 0; }
  .badge { display: inline-block; background: #313244; color: #89b4fa;
           padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin: 2px; }
  .header-bar { padding: 0.75rem 1.5rem; background: #181825;
                border-bottom: 1px solid #313244; display: flex; align-items: center; gap: 1rem; }
  .header-bar h1 { margin: 0; font-size: 1.1rem; color: #cba6f7; }
  .pill { background: #a6e3a1; color: #1e1e2e; padding: 2px 10px;
          border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
</style>
</head>
<body>
<div class="header-bar">
  <h1>💰 Investment Knowledge Vault</h1>
  <span class="pill">Obsidian-compatible</span>
</div>
<div class="container">
  <div class="sidebar">
    <h2>📄 Notes</h2>
    {% for note in notes %}
    <a href="#" onclick="loadNote('{{ note }}'); return false;">{{ note }}</a>
    {% endfor %}
  </div>
  <div class="main">
    <div class="tabs">
      <div class="tab active" onclick="showTab('doc')">📝 Document</div>
      <div class="tab" onclick="showTab('graph')">🕸️ Graph View</div>
    </div>
    <div id="content">
      <p style="color:#6c7086">← Select a note from the sidebar</p>
    </div>
    <div id="graph-view">
      <div id="graph-canvas"></div>
    </div>
  </div>
</div>

<script>
function showTab(tab) {
  document.querySelectorAll('.tab').forEach((t,i) => t.classList.toggle('active', (tab==='doc'&&i===0)||(tab==='graph'&&i===1)));
  document.getElementById('content').style.display = tab==='doc' ? 'block' : 'none';
  document.getElementById('graph-view').style.display = tab==='graph' ? 'flex' : 'none';
  if (tab==='graph') loadGraph();
}

function loadNote(name) {
  fetch('/note/' + encodeURIComponent(name))
    .then(r => r.json())
    .then(d => {
      document.getElementById('content').innerHTML = marked.parse(d.content);
    });
}

let graphLoaded = false;
function loadGraph() {
  if (graphLoaded) return;
  fetch('/graph').then(r => r.json()).then(data => {
    graphLoaded = true;
    const nodes = new vis.DataSet(data.nodes.map(n => ({
      id: n.id,
      label: n.label,
      color: n.type==='product' ? '#89b4fa' : n.type==='risk_level' ? '#f38ba8' :
             n.type==='goal' ? '#a6e3a1' : n.type==='component' ? '#fab387' : '#cba6f7',
      title: 'Tags: ' + (n.tags||[]).join(', '),
      font: { color: '#cdd6f4' }
    })));
    const edges = new vis.DataSet(data.edges.map((e,i) => ({
      id: i, from: e.source, to: e.target, label: e.relation,
      color: { color: '#45475a' }, font: { color: '#6c7086', size: 9 },
      arrows: 'to'
    })));
    new vis.Network(
      document.getElementById('graph-canvas'),
      { nodes, edges },
      { background: '#1e1e2e', physics: { stabilization: { iterations: 100 } },
        edges: { smooth: { type: 'continuous' } } }
    );
  });
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    notes = [f.stem for f in VAULT_DIR.glob('*.md')]
    return render_template_string(TEMPLATE, notes=notes)

@app.route('/note/<name>')
def get_note(name):
    path = VAULT_DIR / f"{name}.md"
    if not path.exists():
        return jsonify({"content": "# Not found"})
    content = path.read_text()
    # Strip YAML frontmatter
    content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
    return jsonify({"content": content})

@app.route('/graph')
def get_graph():
    path = VAULT_DIR / 'graph_nodes.json'
    data = json.loads(path.read_text())
    data.pop('__comment', None)
    return jsonify(data)

if __name__ == '__main__':
    print("Knowledge Vault Viewer running: http://localhost:8503")
    app.run(host='0.0.0.0', port=8503)
