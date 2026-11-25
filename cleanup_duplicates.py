import os
import re
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

print(f"Connecting to {WP_URL} to scan and remove duplicate posts...")

# 1. Fetch all posts from WordPress (paginate through all pages)
all_posts = []
page = 1
while True:
    res = requests.get(f"{WP_URL}/wp-json/wp/v2/posts?per_page=100&page={page}&status=publish", headers=headers, timeout=25)
    if res.status_code != 200:
        break
    data = res.json()
    if not data:
        break
    all_posts.extend(data)
    total_pages = int(res.headers.get("X-WP-TotalPages", 1))
    if page >= total_pages:
        break
    page += 1

print(f"Total posts found on WordPress: {len(all_posts)}")

def normalize_title(t):
    clean = re.sub(r"&#\d+;|&[a-z]+;|[^\w\s]", "", t).lower()
    return " ".join(clean.split())

# 2. Group posts by normalized title
title_map = {}
for p in all_posts:
    pid = p.get("id")
    raw_title = p.get("title", {}).get("rendered", "")
    norm = normalize_title(raw_title)
    if norm not in title_map:
        title_map[norm] = []
    title_map[norm].append({"id": pid, "title": raw_title, "date": p.get("date")})

# 3. Identify and delete duplicates
# For each title, sort by date/ID, keep the oldest/first one, and delete all newer duplicates
deleted_count = 0
for norm, items in title_map.items():
    if len(items) > 1:
        # Sort by ID ascending (first created stays)
        items.sort(key=lambda x: x["id"])
        keep = items[0]
        dupes = items[1:]
        print(f"\nTitle: '{keep['title']}' has {len(items)} posts.")
        print(f" -> Keeping Post ID {keep['id']} ({keep['date']})")
        for d in dupes:
            del_url = f"{WP_URL}/wp-json/wp/v2/posts/{d['id']}?force=true"
            del_res = requests.delete(del_url, headers=headers, timeout=15)
            if del_res.status_code in [200, 201, 204]:
                print(f"    [DELETED] Duplicate Post ID {d['id']} ({d['date']})")
                deleted_count += 1
            else:
                print(f"    [FAILED] Could not delete Post ID {d['id']}: {del_res.status_code}")

print(f"\n==========================================")
print(f"Cleanup finished! Total duplicates deleted: {deleted_count}")
print(f"==========================================")

# 4. Purge LiteSpeed Cache
cs_url = f"{WP_URL}/wp-json/code-snippets/v1/snippets"
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
        "name": "Purge Cache After Duplicate Cleanup",
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
