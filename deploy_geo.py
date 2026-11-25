import os
import json
import base64
import requests

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "").replace(" ", "")

if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
    print("Error: Missing WordPress credentials.")
    exit(1)

auth_str = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
headers = {
    "Authorization": f"Basic {base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

cs_url = f"{WP_URL}/wp-json/code-snippets/v1/snippets"

with open("geo_bundle.json", "r", encoding="utf-8-sig") as f:
    bundle = json.load(f)

print("Deploying GEO Theme & LLMs.txt files via Code Snippets API...")
for filename, b64_content in bundle.items():
    if filename == "_root_llms.txt":
        php_code = f"""
file_put_contents(ABSPATH . 'llms.txt', base64_decode('{b64_content}'));
file_put_contents(ABSPATH . 'llms-full.txt', base64_decode('{b64_content}'));
"""
    else:
        php_code = f"""
$theme_dir = WP_CONTENT_DIR . '/themes/waveprotv-theme';
if (is_dir($theme_dir)) {{
    file_put_contents($theme_dir . '/{filename}', base64_decode('{b64_content}'));
}}
"""
    create_snip = requests.post(cs_url, headers=headers, json={
        "name": f"Deploy GEO {filename}",
        "code": php_code.strip(),
        "scope": "global",
        "active": True
    }, timeout=15)
    print(f"Deployed {filename}: status {create_snip.status_code}")
    if create_snip.status_code in [200, 201]:
        snip_id = create_snip.json().get("id")
        requests.get(f"{WP_URL}/wp-json/", headers=headers, timeout=10)
        if snip_id:
            requests.delete(f"{cs_url}/{snip_id}", headers=headers, timeout=10)

# Purge LiteSpeed Cache
purge_code = """
if (class_exists('LiteSpeed\\Purge')) {
    \\LiteSpeed\\Purge::purge_all();
}
if (function_exists('litespeed_purge_all')) {
    litespeed_purge_all();
}
"""
try:
    p_snip = requests.post(cs_url, headers=headers, json={
        "name": "Purge Cache GEO",
        "code": purge_code.strip(),
        "scope": "global",
        "active": True
    }, timeout=15)
    if p_snip.status_code in [200, 201]:
        pid = p_snip.json().get("id")
        requests.get(f"{WP_URL}/wp-json/", headers=headers, timeout=10)
        if pid:
            requests.delete(f"{cs_url}/{pid}", headers=headers, timeout=10)
    print("LiteSpeed Cache purged successfully!")
except Exception as e:
    print(f"Cache purge note: {e}")

print("GEO deployment completed!")
