import json

with open('data/catalog/companies_catalog.json', 'r', encoding='utf-8') as f:
    catalog_json = f.read()

html_path = r'C:\Users\julia\.gemini\antigravity\brain\9f7a61e6-afb4-4584-a3e5-1f6d74df8639\catalogo_empresas_y_noticias.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Replace the fetch logic with embedded data
old_init = """    // Fetch catalog JSON
    async function init() {
      try {
        const resp = await fetch('data/catalog/companies_catalog.json');
        catalogData = await resp.json();
      } catch (e) {
        console.error("Could not load catalog json via fetch, trying fallback or local", e);
      }"""

new_init = f"""    // Embedded catalog data (CORS-safe)
    const EMBEDDED_DATA = {catalog_json};

    async function init() {{
      catalogData = EMBEDDED_DATA;"""

if old_init in html_content:
    html_content = html_content.replace(old_init, new_init)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Embedded catalog JSON directly into HTML. Zero CORS risk!")
else:
    print("Could not find old_init in html_content")
