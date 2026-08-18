"""
Builds public/index.html with all Python modules and YAML configs embedded inline.
This eliminates all external network calls to GitHub raw URLs in browser WASM.
"""

import json
from pathlib import Path

root = Path(__file__).resolve().parent

files_to_embed = [
    "src/dashboard/app.py",
    "src/dashboard/charts.py",
    "src/models/clustering.py",
    "src/models/fuzzy_engine.py",
    "src/models/classifier.py",
    "src/models/uplift.py",
    "src/rules/before_after.py",
    "src/rules/budget.py",
    "src/rules/roi.py",
    "src/analytics/financials.py",
    "src/analytics/metrics.py",
    "src/analytics/statistics.py",
    "src/data/clean.py",
    "src/data/sample_generator.py",
    "src/features/basket.py",
    "src/features/brand.py",
    "src/features/need_want.py",
    "src/features/supply.py",
    "src/validation/checks.py",
    "src/config.py",
    "src/logging.py",
    "src/exceptions.py",
    "src/utils/io.py",
    "config/settings.yaml",
    "config/financials.yaml",
    "config/pg_brands.yaml",
    "config/need_want_mapping.yaml",
    "config/supply.yaml",
    "data/output/pg_need_share.csv",
    "data/output/budget_recommendations.csv",
    "data/output/before_after_metrics.csv",
    "data/output/financial_estimate.csv",
    "data/output/data_quality_report.csv"
]

files_dict = {
    "src/__init__.py": {"content": ""},
    "src/analytics/__init__.py": {"content": ""},
    "src/dashboard/__init__.py": {"content": ""},
    "src/data/__init__.py": {"content": ""},
    "src/features/__init__.py": {"content": ""},
    "src/models/__init__.py": {"content": ""},
    "src/rules/__init__.py": {"content": ""},
    "src/utils/__init__.py": {"content": ""},
    "src/validation/__init__.py": {"content": ""}
}

for rel_path in files_to_embed:
    file_path = root / rel_path
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        files_dict[rel_path.replace("\\", "/")] = {"content": content}

files_json = json.dumps(files_dict, indent=2)

html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>P&amp;G Advertisement Budget Decision Engine</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.73.0/build/stlite.css" />
    <style>
      body, html {{
        margin: 0;
        padding: 0;
        height: 100%;
        background-color: #0b0f19;
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }}
      #root {{
        height: 100%;
      }}
      #loader-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: #0b0f19;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 99999;
        transition: opacity 0.5s ease;
      }}
      .loader-logo {{
        background: #003da5;
        color: #ffffff;
        font-weight: 900;
        font-size: 1.8rem;
        padding: 12px 24px;
        border-radius: 12px;
        letter-spacing: 0.08em;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 61, 165, 0.5);
      }}
      .loader-spinner {{
        width: 44px;
        height: 44px;
        border: 4px solid rgba(56, 189, 248, 0.15);
        border-top: 4px solid #38bdf8;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
      }}
      @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
      }}
      .loader-title {{
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 8px;
      }}
      .loader-subtitle {{
        font-size: 0.85rem;
        color: #94a3b8;
        max-width: 400px;
        text-align: center;
        line-height: 1.5;
      }}
    </style>
  </head>
  <body>
    <div id="loader-overlay">
      <div class="loader-logo">P&amp;G</div>
      <div class="loader-spinner"></div>
      <div class="loader-title">Loading Decision Intelligence Engine...</div>
      <div class="loader-subtitle">Initializing Python WebAssembly runtime &amp; Machine Learning models in your browser.</div>
    </div>
    <div id="root"></div>
    <script src="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.73.0/build/stlite.js"></script>
    <script>
      const files = {files_json};

      stlite.mount(
        {{
          requirements: ["pandas", "numpy", "scipy", "scikit-learn", "plotly", "pyyaml"],
          entrypoint: "src/dashboard/app.py",
          files: files
        }},
        document.getElementById("root")
      );

      // Hide loader once streamlit loads
      const observer = new MutationObserver((mutations, obs) => {{
        const stApp = document.querySelector('.stApp');
        if (stApp) {{
          const overlay = document.getElementById('loader-overlay');
          if (overlay) {{
            overlay.style.opacity = '0';
            setTimeout(() => overlay.remove(), 500);
          }}
          obs.disconnect();
        }}
      }});
      observer.observe(document.getElementById('root'), {{ childList: true, subtree: true }});
    </script>
  </body>
</html>
"""

(root / "public" / "index.html").write_text(html_content, encoding="utf-8")
print(f"Successfully generated public/index.html ({len(html_content)} bytes, {len(files_dict)} embedded files).")
