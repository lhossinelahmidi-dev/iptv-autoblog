import os
import json
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
with open("rocket_bundle.json", "r", encoding="utf-8-sig") as f:
    bundle = json.load(f)

print("1. Deploying IndexNow + Related Guides (functions.php & single.php)...")
for filename, b64_content in bundle.items():
    php_code = f"""
$theme_dir = WP_CONTENT_DIR . '/themes/waveprotv-theme';
if (is_dir($theme_dir)) {{
    file_put_contents($theme_dir . '/{filename}', base64_decode('{b64_content}'));
}}
"""
    create_snip = requests.post(cs_url, headers=headers, json={
        "name": f"Deploy Rocket {filename}",
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
        "name": "Purge Cache Rocket",
        "code": purge_code.strip(),
        "scope": "global",
        "active": True
    }, timeout=15)
    if p_snip.status_code in [200, 201]:
        pid = p_snip.json().get("id")
        requests.get(f"{WP_URL}/wp-json/", headers=headers, timeout=10)
        if pid:
            requests.delete(f"{cs_url}/{pid}", headers=headers, timeout=10)
    print("LiteSpeed Cache purged!")
except Exception as e:
    print(f"Cache purge note: {e}")

# 2. Submit ALL existing URLs to IndexNow immediately
print("\n2. Pinging IndexNow for instant indexing of all site URLs...")
try:
    posts_res = requests.get(f"{WP_URL}/wp-json/wp/v2/posts?per_page=100&_fields=link", headers=headers, timeout=20)
    url_list = [f"{WP_URL}/", f"{WP_URL}/blog/"]
    if posts_res.status_code == 200:
        for p in posts_res.json():
            if p.get("link"):
                url_list.append(p["link"])
    indexnow_key = "wptv2026indexnow8a9f3c7d1e4b2a5f"
    host_domain = WP_URL.replace("https://", "").replace("http://", "").split("/")[0]
    in_res = requests.post(
        "https://api.indexnow.org/indexnow",
        json={
            "host": host_domain,
            "key": indexnow_key,
            "keyLocation": f"{WP_URL}/{indexnow_key}.txt",
            "urlList": url_list
        },
        timeout=15
    )
    print(f"IndexNow bulk submission ({len(url_list)} URLs): HTTP {in_res.status_code}")
except Exception as e:
    print(f"IndexNow bulk error: {e}")
