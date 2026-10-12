import os
import base64
import requests

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "").replace(" ", "")

auth_str = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
headers = {
    "Authorization": f"Basic {base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}
cs_url = f"{WP_URL}/wp-json/code-snippets/v1/snippets"

with open("funcs_b64.txt", "r", encoding="utf-8-sig") as f:
    b64_content = f.read().strip()

php_code = f"""
$theme_dir = WP_CONTENT_DIR . '/themes/waveprotv-theme';
if (is_dir($theme_dir)) {{
    file_put_contents($theme_dir . '/functions.php', base64_decode('{b64_content}'));
}}
if (class_exists('LiteSpeed\\Purge')) {{
    \\LiteSpeed\\Purge::purge_all();
}}
if (function_exists('litespeed_purge_all')) {{
    litespeed_purge_all();
}}
"""
create_snip = requests.post(cs_url, headers=headers, json={
    "name": "Deploy functions.php",
    "code": php_code.strip(),
    "scope": "global",
    "active": True
})
print(f"Deployed functions.php: {create_snip.status_code}")
if create_snip.status_code in [200, 201]:
    snip_id = create_snip.json().get("id")
    requests.get(f"{WP_URL}/wp-json/", headers=headers)
    if snip_id:
        requests.delete(f"{cs_url}/{snip_id}", headers=headers)
print("Done!")
