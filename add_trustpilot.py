import os
import requests
import base64
import json

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")

print(f"Connecting to: {WP_URL} as {WP_USERNAME}")

auth_str = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
auth_bytes = auth_str.encode("utf-8")
headers = {
    "Authorization": f"Basic {base64.b64encode(auth_bytes).decode('utf-8')}",
    "Content-Type": "application/json"
}

# 1. Check settings endpoint
res_settings = requests.get(f"{WP_URL}/wp-json/wp/v2/settings", headers=headers)
print(f"Settings status: {res_settings.status_code}")

# 2. Check plugins
res_plugins = requests.get(f"{WP_URL}/wp-json/wp/v2/plugins", headers=headers)
print(f"Plugins status: {res_plugins.status_code}")
if res_plugins.status_code == 200:
    for p in res_plugins.json():
        print(f"Plugin: {p.get('name')} | Slug/File: {p.get('plugin')} | Status: {p.get('status')}")

# 3. Try to install WPCode (insert-headers-and-footers) via REST API
install_res = requests.post(f"{WP_URL}/wp-json/wp/v2/plugins", headers=headers, json={
    "slug": "insert-headers-and-footers",
    "status": "active"
})
print(f"Install WPCode status: {install_res.status_code}")
print(f"Install response: {install_res.text[:300]}")

# 4. Check LiteSpeed Cache settings or purge
purge_res = requests.get(f"{WP_URL}/?LSCWP_CTRL=PURGE_ALL", headers=headers)
print(f"Purge request status: {purge_res.status_code}")
