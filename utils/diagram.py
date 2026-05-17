"""
Diagram Generator Module
=========================
WHY Mermaid diagrams (not images):
- Mermaid renders in-browser from text — no image APIs, no costs, no latency.
- Streamlit can render Mermaid via st.markdown with a custom HTML block.
- The AI generates valid Mermaid syntax; we just display it.
- Completely free, works offline after initial model load.

Diagram types supported:
  flowchart   — process flows, algorithms, decision trees
  mindmap     — concept hierarchies and relationships
  sequence    — API flows, system interactions
  classDiagram— OOP structures, data models
"""

import re
from typing import Tuple
from utils.llm     import ask_llm
from utils.prompts import build_diagram_prompt


# ────────────────────────────────────────────────────────────────────────────
# GENERATION
# ────────────────────────────────────────────────────────────────────────────
def generate_diagram(topic: str, diagram_type: str = "flowchart") -> Tuple[str, str]:
    """
    Generate a Mermaid diagram for a given topic.

    Args:
        topic:        Concept or topic to visualise.
        diagram_type: flowchart | mindmap | sequence | classDiagram

    Returns:
        (mermaid_code, error_message)
        On success: (valid mermaid string, "")
        On failure: ("", error description)
    """
    prompt      = build_diagram_prompt(topic, diagram_type)
    raw_output  = ask_llm(prompt)

    if "⚠️" in raw_output:
        return "", raw_output   # LLM returned an error message

    cleaned = clean_mermaid(raw_output)
    valid, err = validate_mermaid(cleaned)

    if not valid:
        # Try once more with explicit error feedback
        retry_prompt = f"""{prompt}

Your previous output had an issue: {err}
Please output ONLY valid Mermaid syntax, nothing else."""
        raw_output = ask_llm(retry_prompt)
        cleaned    = clean_mermaid(raw_output)
        valid, err = validate_mermaid(cleaned)
        if not valid:
            return "", f"Could not generate valid diagram: {err}"

    return cleaned, ""


# ────────────────────────────────────────────────────────────────────────────
# CLEANING + VALIDATION
# ────────────────────────────────────────────────────────────────────────────
def clean_mermaid(raw: str) -> str:
    """
    Strip markdown fences and extra text that LLMs often wrap around Mermaid code.
    LLMs frequently output: ```mermaid
...
``` — we strip that.
    """
    # Remove markdown code fences
    raw = re.sub(r"```(?:mermaid)?\s*", "", raw)
    raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE)

    # Remove lines that look like prose (start with common explanation words)
    lines = raw.splitlines()
    code_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip explanation lines the LLM sometimes prepends
        if re.match(r"^(here|this|the|i |note:|explanation)", stripped, re.IGNORECASE):
            continue
        code_lines.append(line)

    return "\n".join(code_lines).strip()


def validate_mermaid(code: str) -> Tuple[bool, str]:
    """
    Basic Mermaid validation — checks that it starts with a known type keyword.
    Full rendering validation happens in the browser.
    """
    if not code or not code.strip():
        return False, "Empty output"

    first_line = code.strip().splitlines()[0].strip().lower()
    valid_starters = [
        "flowchart", "graph", "sequencediagram", "classdiagram",
        "statediagram", "erdiagram", "gantt", "pie", "mindmap",
        "timeline", "gitgraph", "quadrantchart", "xychart-beta",
    ]

    if not any(first_line.startswith(s) for s in valid_starters):
        return False, f"Unrecognised diagram type. First line: '{first_line}'"

    return True, ""


# ────────────────────────────────────────────────────────────────────────────
# RENDERING HELPER  — returns HTML for st.components.v1.html()
# ────────────────────────────────────────────────────────────────────────────
def mermaid_to_html(mermaid_code: str) -> str:
    """
    Wrap Mermaid code in a self-contained HTML snippet that renders it
    using the Mermaid.js CDN and adds pan/zoom controls.
    """
    panzoom_lib_url = "https://cdn.jsdelivr.net/npm/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"
    
    return f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script src="{panzoom_lib_url}"></script>
<style>
  body {{{{
    background: #181c27;
    margin: 0;
    font-family: 'DM Sans', sans-serif;
  }}}}
  #mermaid-container {{{{
    width: 100%;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    padding: 1rem;
    box-sizing: border-box;
  }}}}
  .mermaid {{{{
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
  }}}}
  .mermaid svg {{{{
    max-width: 100%;
    max-height: 100%;
  }}}}
  #mermaid-controls, #download-controls {{{{
    position: absolute;
    right: 10px;
    display: flex;
    gap: 8px;
    z-index: 100;
  }}}}
  #mermaid-controls {{{{ top: 10px; }}}}
  #download-controls {{{{ bottom: 10px; }}}}

  #mermaid-controls button, #download-controls button {{{{
    background: #2e3447;
    color: #e8eaf0;
    border: 1px solid #7c8499;
    border-radius: 6px;
    cursor: pointer;
    transition: all .2s;
    font-size: .8rem;
    padding: 6px 12px;
  }}}}
  #mermaid-controls button {{{{
    width: 32px;
    height: 32px;
    font-size: 1.2rem;
  }}}}
  #mermaid-controls button:hover, #download-controls button:hover {{{{
    background: #6c63ff;
    border-color: #6c63ff;
  }}}}
</style>
</head>
<body>

<div id="mermaid-controls">
  <button id="zoom-in" title="Zoom In">＋</button>
  <button id="zoom-out" title="Zoom Out">－</button>
  <button id="reset" title="Reset View">⟲</button>
</div>

<div id="download-controls">
  <button id="download-svg">Download SVG</button>
  <button id="download-png">Download PNG</button>
</div>

<div id="mermaid-container">
  <div class="mermaid">
    {mermaid_code}
  </div>
</div>

<script>
  mermaid.initialize({{{{
    startOnLoad: false,
    theme: 'dark',
    themeVariables: {{
      primaryColor: '#6c63ff',
      primaryTextColor: '#e8eaf0',
      primaryBorderColor: '#2e3447',
      lineColor: '#7c8499',
      secondaryColor: '#1e2333',
      tertiaryColor: '#181c27',
      background: '#181c27',
      mainBkg: '#1e2333',
      nodeBorder: '#2e3447',
      clusterBkg: '#181c27',
      titleColor: '#e8eaf0',
      edgeLabelBackground: '#181c27',
      fontFamily: 'DM Sans, sans-serif',
    }}
  }}}});

  function setupPanzoomAndDownload() {{{{
    const container = document.getElementById('mermaid-container');
    const svgElement = container.querySelector('svg');
    if (svgElement) {{{{
      svgElement.style.width = '100%';
      svgElement.style.height = '100%';

      const panzoom = Panzoom(svgElement, {{{{
          maxScale: 10,
          minScale: 0.1,
          contain: 'outside',
          canvas: true,
      }}}});

      const zoomInBtn = document.getElementById('zoom-in');
      const zoomOutBtn = document.getElementById('zoom-out');
      const resetBtn = document.getElementById('reset');

      zoomInBtn.addEventListener('click', () => panzoom.zoomIn());
      zoomOutBtn.addEventListener('click', () => panzoom.zoomOut());
      resetBtn.addEventListener('click', () => panzoom.reset());

      container.addEventListener('wheel', panzoom.zoomWithWheel);

      setTimeout(() => {{{{
        const containerRect = container.getBoundingClientRect();
        const svgRect = svgElement.getBoundingClientRect();
        if (svgRect.width > 0 && svgRect.height > 0) {{{{
            const scaleX = containerRect.width / svgRect.width;
            const scaleY = containerRect.height / svgRect.height;
            const scale = Math.min(scaleX, scaleY) * 0.95;
            const x = (containerRect.width - svgRect.width * scale) / 2;
            const y = (containerRect.height - svgRect.height * scale) / 2;
            panzoom.zoomTo(x, y, scale);
        }}}} else {{{{
            panzoom.reset();
        }}}}
      }}}}, 200);

      // --- Download Logic ---
      const downloadSvgBtn = document.getElementById('download-svg');
      const downloadPngBtn = document.getElementById('download-png');

      downloadSvgBtn.addEventListener('click', () => {{{{
        const svgData = new XMLSerializer().serializeToString(svgElement);
        const blob = new Blob([svgData], {{{{ type: 'image/svg+xml;charset=utf-8' }}}});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'diagram.svg';
        a.click();
        URL.revokeObjectURL(url);
      }}}});

      downloadPngBtn.addEventListener('click', () => {{{{
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();

        const clonedSvg = svgElement.cloneNode(true);
        clonedSvg.style.transform = '';

        const viewBox = svgElement.viewBox.baseVal;
        const width = viewBox.width;
        const height = viewBox.height;
        const padding = 40;

        clonedSvg.setAttribute('width', width);
        clonedSvg.setAttribute('height', height);

        const svgData = new XMLSerializer().serializeToString(clonedSvg);
        const svgUrl = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgData);

        img.onload = function() {{{{
          canvas.width = width + padding;
          canvas.height = height + padding;

          ctx.fillStyle = '#181c27';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, padding / 2, padding / 2);
          
          const pngUrl = canvas.toDataURL('image/png');
          const a = document.createElement('a');
          a.href = pngUrl;
          a.download = 'diagram.png';
          a.click();
        }}}};
        img.src = svgUrl;
      }}}});
    }}}}
  }}

  window.addEventListener('load', function() {{{{
    mermaid.run({{{{
      nodes: document.querySelectorAll('.mermaid'),
      suppressErrors: true,
    }}}}).then(() => {{{{
      setupPanzoomAndDownload();
    }}}});
  }}}});
</script>
</body>
</html>
"""


# ────────────────────────────────────────────────────────────────────────────
# DIAGRAM TYPE METADATA  — for the UI dropdown
# ────────────────────────────────────────────────────────────────────────────
DIAGRAM_TYPES = {
    "flowchart":    {"label": "🔀 Flowchart",     "desc": "Process flows & decision trees"},
    "mindmap":      {"label": "🧠 Mind Map",       "desc": "Concept hierarchies"},
    "sequence":     {"label": "↔️ Sequence",       "desc": "System/API interactions"},
    "classDiagram": {"label": "🏗️ Class Diagram",  "desc": "OOP structures & data models"},
}
