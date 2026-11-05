"""Embed docs/data.json into docs/template.html -> docs/index.html (GitHub Pages ready)."""
import json
html = open("docs/template.html", encoding="utf-8").read().replace("__DATA__", json.dumps(json.load(open("docs/data.json"))))
open("docs/index.html", "w", encoding="utf-8").write(html); print("Built docs/index.html")
