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

print(f"1. Ensuring /blog/ page exists on {WP_URL}...")
pages_res = requests.get(f"{WP_URL}/wp-json/wp/v2/pages?slug=blog", headers=headers)
if pages_res.status_code == 200 and len(pages_res.json()) == 0:
    create_page = requests.post(f"{WP_URL}/wp-json/wp/v2/pages", headers=headers, json={
        "title": "Blog",
        "slug": "blog",
        "status": "publish"
    })
    print(f"Created /blog/ page: {create_page.status_code}")
else:
    print("/blog/ page already exists or checked.")

print("\n2. Installing / Activating code-snippets plugin via REST API...")
inst = requests.post(f"{WP_URL}/wp-json/wp/v2/plugins", headers=headers, json={
    "slug": "code-snippets",
    "status": "active"
})
print(f"Install code-snippets status: {inst.status_code}")
if inst.status_code != 201 and inst.status_code != 200:
    print(f"Install note: {inst.text[:250]}")
    # Try activating if already installed
    act = requests.post(f"{WP_URL}/wp-json/wp/v2/plugins/code-snippets/code-snippets", headers=headers, json={
        "status": "active"
    })
    print(f"Activate code-snippets status: {act.status_code}")

time.sleep(2)

# Check code-snippets endpoint
cs_url = f"{WP_URL}/wp-json/code-snippets/v1/snippets"
cs_check = requests.get(cs_url, headers=headers)
print(f"Code Snippets API check: {cs_check.status_code}")

with open("theme_bundle.json", "r", encoding="utf-8") as f:
    bundle = json.load(f)

if cs_check.status_code == 200:
    print("\n3. Deploying theme files via Code Snippets API...")
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
            # Trigger execution by hitting the site
            requests.get(f"{WP_URL}/wp-json/", headers=headers)
            # Clean up snippet
            if snip_id:
                requests.delete(f"{cs_url}/{snip_id}", headers=headers)
                print(f"Cleaned up snippet {snip_id} for {filename}")
    
    # Purge LiteSpeed cache via PHP snippet
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
else:
    print(f"Code Snippets API returned {cs_check.status_code}: {cs_check.text[:300]}")

print("\n4. Verifying live homepage HTML...")
verify = requests.get(f"{WP_URL}/?nocache={int(time.time())}", headers={"User-Agent": "Mozilla/5.0"})
print(f"Live Homepage status: {verify.status_code} | Length: {len(verify.text)} bytes")

verify_blog = requests.get(f"{WP_URL}/blog/?nocache={int(time.time())}", headers={"User-Agent": "Mozilla/5.0"})
print(f"Live /blog/ status: {verify_blog.status_code} | Length: {len(verify_blog.text)} bytes")
