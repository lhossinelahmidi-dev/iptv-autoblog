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

# Ensure /reviews/ page exists via WP REST API
pages_res = requests.get(f"{WP_URL}/wp-json/wp/v2/pages?slug=reviews", headers=headers, timeout=15)
if pages_res.status_code == 200 and len(pages_res.json()) == 0:
    cp = requests.post(f"{WP_URL}/wp-json/wp/v2/pages", headers=headers, json={
        "title": "Reviews",
        "slug": "reviews",
        "status": "publish"
    }, timeout=15)
    print(f"Created /reviews/ page via REST API: {cp.status_code}")

with open("reviews_page_bundle.json", "r", encoding="utf-8-sig") as f:
    bundle = json.load(f)

for filename, b64_content in bundle.items():
    php_code = f"""
$theme_dir = WP_CONTENT_DIR . '/themes/waveprotv-theme';
if (is_dir($theme_dir)) {{
    file_put_contents($theme_dir . '/{filename}', base64_decode('{b64_content}'));
}}
"""
    create_snip = requests.post(cs_url, headers=headers, json={
        "name": f"Deploy ReviewsPage {filename}",
        "code": php_code.strip(),
        "scope": "global",
        "active": True
    }, timeout=15)
    print(f"Deployed {filename}: {create_snip.status_code}")
    if create_snip.status_code in [200, 201]:
        snip_id = create_snip.json().get("id")
        requests.get(f"{WP_URL}/wp-json/", headers=headers, timeout=10)
        if snip_id:
            requests.delete(f"{cs_url}/{snip_id}", headers=headers, timeout=10)

purge_code = """
if (function_exists('flush_rewrite_rules')) {
    flush_rewrite_rules();
}
if (class_exists('LiteSpeed\\Purge')) {
    \\LiteSpeed\\Purge::purge_all();
}
if (function_exists('litespeed_purge_all')) {
    litespeed_purge_all();
}
"""
p_snip = requests.post(cs_url, headers=headers, json={
    "name": "Flush & Purge Cache ReviewsPage",
    "code": purge_code.strip(),
    "scope": "global",
    "active": True
})
if p_snip.status_code in [200, 201]:
    pid = p_snip.json().get("id")
    requests.get(f"{WP_URL}/wp-json/", headers=headers, timeout=10)
    if pid:
        requests.delete(f"{cs_url}/{pid}", headers=headers, timeout=10)
print("Flushed rewrite rules & purged LiteSpeed Cache!")

# Submit /reviews/ to IndexNow for instant indexing
try:
    indexnow_key = "wptv2026indexnow8a9f3c7d1e4b2a5f"
    host_domain = WP_URL.replace("https://", "").replace("http://", "").split("/")[0]
    in_res = requests.post(
        "https://api.indexnow.org/indexnow",
        json={
            "host": host_domain,
            "key": indexnow_key,
            "keyLocation": f"{WP_URL}/{indexnow_key}.txt",
            "urlList": [f"{WP_URL}/reviews/", f"{WP_URL}/"]
        },
        timeout=10
    )
    print(f"IndexNow ping for /reviews/: HTTP {in_res.status_code}")
except Exception as e:
    print(f"IndexNow note: {e}")
