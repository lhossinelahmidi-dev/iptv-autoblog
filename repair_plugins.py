import os
import requests
import base64
import json

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")

print(f"Connecting to WordPress REST API at: {WP_URL}")
print(f"User: {WP_USERNAME}")

if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
    print("Missing credentials!")
    exit(1)

auth_str = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
auth_bytes = auth_str.encode("utf-8")
headers = {
    "Authorization": f"Basic {base64.b64encode(auth_bytes).decode('utf-8')}",
    "Content-Type": "application/json"
}

# 1. List all plugins
plugins_url = f"{WP_URL}/wp-json/wp/v2/plugins"
res = requests.get(plugins_url, headers=headers)
print(f"GET /wp/v2/plugins status: {res.status_code}")

if res.status_code != 200:
    print(f"Error listing plugins: {res.text}")
    # Let's try activating Elementor directly by common slug
    possible_elementor = ["elementor/elementor", "elementor"]
    for slug in possible_elementor:
        act_res = requests.post(f"{plugins_url}/{slug}", headers=headers, json={"status": "active"})
        print(f"Try activate {slug}: {act_res.status_code} -> {act_res.text[:200]}")
    exit(0)

plugins = res.json()
print(f"Found {len(plugins)} plugins installed:")

elementor_plugin = None
problematic_plugins = []

for p in plugins:
    plugin_file = p.get("plugin", "")
    status = p.get("status", "")
    name = p.get("name", "")
    print(f" - [{status.upper()}] {name} (file: {plugin_file})")
    
    if "elementor" in plugin_file.lower() and "kit" not in plugin_file.lower() and "header" not in plugin_file.lower() and "lastudio" not in plugin_file.lower():
        elementor_plugin = plugin_file
    
    if any(bad in plugin_file.lower() for bad in ["lastudio", "elementskit", "header-footer", "metform"]):
        problematic_plugins.append(plugin_file)

# First: Reactivate Elementor so nothing crashes
if elementor_plugin:
    print(f"\n--> Reactivating Elementor: {elementor_plugin}")
    act = requests.post(f"{plugins_url}/{elementor_plugin}", headers=headers, json={"status": "active"})
    print(f"Result: {act.status_code} -> {act.text[:200]}")

# Second: Deactivate the addons that caused the fatal error
for bad in problematic_plugins:
    print(f"\n--> Deactivating problematic addon: {bad}")
    deact = requests.post(f"{plugins_url}/{bad}", headers=headers, json={"status": "inactive"})
    print(f"Result: {deact.status_code} -> {deact.text[:200]}")

print("\nRepair operation completed!")
