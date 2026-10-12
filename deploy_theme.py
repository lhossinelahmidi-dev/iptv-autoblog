import os
import json
import base64
import time
import requests

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")

if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
    print("Missing WordPress credentials")
    exit(1)

auth_str = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
headers = {
    "Authorization": f"Basic {base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

cs_url = f"{WP_URL}/wp-json/code-snippets/v1/snippets"

with open("theme_bundle.json", "r", encoding="utf-8") as f:
    bundle = json.load(f)

print("Deploying updated theme files via Code Snippets API...")
for filename, b64_content in bundle.items():
    php_code = f"""
$theme_dir = WP_CONTENT_DIR . '/themes/waveprotv-theme';
if (is_dir($theme_dir)) {{
    file_put_contents($theme_dir . '/{filename}', base64_decode('{b64_content}'));
}}
"""
    create_snip = requests.post(cs_url, headers=headers, json={
        "name": f"Deploy {filename}",
        "code": php_code.strip(),
        "scope": "global",
        "active": True
    })
    print(f"Deployed snippet for {filename}: status {create_snip.status_code}")
    if create_snip.status_code in [200, 201]:
        snip_id = create_snip.json().get("id")
        requests.get(f"{WP_URL}/wp-json/", headers=headers)
        if snip_id:
            requests.delete(f"{cs_url}/{snip_id}", headers=headers)
            print(f"Cleaned up snippet {snip_id} for {filename}")

purge_code = """
if (class_exists('LiteSpeed\\Purge')) {
    \\LiteSpeed\\Purge::purge_all();
}
if (function_exists('litespeed_purge_all')) {
    litespeed_purge_all();
}
"""
p_snip = requests.post(cs_url, headers=headers, json={
    "name": "Purge Cache",
    "code": purge_code.strip(),
    "scope": "global",
    "active": True
})
if p_snip.status_code in [200, 201]:
    pid = p_snip.json().get("id")
    requests.get(f"{WP_URL}/wp-json/", headers=headers)
    if pid:
        requests.delete(f"{cs_url}/{pid}", headers=headers)
print("LiteSpeed Cache purged!")
