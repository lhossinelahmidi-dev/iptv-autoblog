import os
import re
import random
import time
import base64
import json
import requests

# 1. Configuration
WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")
GH_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")

if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
    print("Error: Missing WordPress configuration (WP_URL, WP_USERNAME, or WP_APP_PASSWORD).")
    exit(1)

# 2. Pick a Topic
TOPICS_FILE = "topics.txt"
USED_TOPICS_FILE = "used_topics.txt"

topics = []
if os.path.exists(TOPICS_FILE):
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip()]

if not topics:
    selected_topic = "How to Watch Premier League and Champions League in 4K UHD in the UK"
else:
    selected_topic = topics[0]

print(f"\nProcessing Topic: '{selected_topic}'")

# Organic randomized delay (10 to 90 seconds)
delay_seconds = random.randint(10, 90)
print(f"Applying organic delay of {delay_seconds} seconds...")
time.sleep(delay_seconds)

article_html = None
article_excerpt = None

system_prompt = (
    "You are a premier UK tech journalist, streaming specialist, and SEO authority writing for 'WavePro TV' (waveprotv.com). "
    "Write an engaging, highly specific, 900-word SEO-optimized blog post in British English that directly answers and focuses 100% on the exact title provided. "
    "Format in clean semantic HTML with <p>, <h2>, <h3>, <ul>, <li>, and <strong> tags (do NOT include <h1> or markdown code fences). "
    "The very first <p> paragraph MUST be a compelling 2-sentence summary specifically tailored to the exact topic (no generic filler) so it can also serve as the meta description/excerpt."
)
user_prompt = f"Write a comprehensive, topic-specific UK guide titled: '{selected_topic}'."

# Attempt 1: GitHub Models Inference API
if GH_TOKEN:
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=GH_TOKEN
        )
        for model in ["gpt-4o-mini", "gpt-4o"]:
            try:
                print(f"Attempting GitHub Models generation with: {model}...")
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                content = resp.choices[0].message.content.strip()
                if len(content) > 400:
                    article_html = content
                    print("GitHub Models AI generation successful!")
                    break
            except Exception as e:
                print(f"GitHub Model {model} note: {e}")
    except Exception as e:
        print(f"OpenAI client init note: {e}")

# Attempt 2: Pollinations OpenAI-compatible AI endpoint (no key required)
if not article_html:
    try:
        print("Attempting Pollinations AI generation...")
        poll_res = requests.post(
            "https://text.pollinations.ai/openai",
            headers={"Content-Type": "application/json"},
            json={
                "model": "openai",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7
            },
            timeout=45
        )
        if poll_res.status_code == 200:
            data = poll_res.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if len(content) > 400:
                article_html = content
                print("Pollinations AI generation successful!")
    except Exception as e:
        print(f"Pollinations AI note: {e}")

# Clean code fences if present
if article_html:
    article_html = re.sub(r"^```(?:html)?\s*", "", article_html)
    article_html = re.sub(r"\s*```$", "", article_html).strip()
    # Extract the first paragraph text as a 100% matching custom excerpt
    first_p = re.search(r"<p>(.*?)</p>", article_html, re.DOTALL | re.IGNORECASE)
    if first_p:
        clean_p = re.sub(r"<[^>]+>", "", first_p.group(1)).strip()
        if len(clean_p) > 40:
            article_excerpt = clean_p[:240]

# Fallback: Topic-Specific UK Article & Excerpt Generator
if not article_html or not article_excerpt:
    t_lower = selected_topic.lower()
    if any(k in t_lower for k in ["ppv", "boxing", "ufc", "f1", "formula 1", "football", "premier league", "champions league", "sports", "sky sports", "tnt"]):
        article_excerpt = f"Discover how UK sports fans stream {selected_topic} live in true 4K UHD and 50fps without expensive pay-per-view fees or broadcaster blackouts."
        article_html = f"""
<p>Watching live sport in the United Kingdom has become increasingly fragmented across Sky Sports Box Office, TNT Sports Box Office, DAZN PPV, and subscription channels. In this dedicated UK guide to <strong>{selected_topic}</strong>, we break down how you can stream every live event in native 4K UHD and smooth 50fps with WavePro TV.</p>
<h2>Why UK Sports Fans Are Ditching Expensive PPV Add-Ons</h2>
<p>With single pay-per-view fight nights and motorsport packages now costing £19.99 to £29.99 on top of £85+/month Sky and TNT subscriptions, thousands of British households have switched to all-in-one IPTV streaming.</p>
<ul>
    <li><strong>All UK &amp; International Sports Channels Included:</strong> Instant access to Sky Sports Main Event UHD, Sky Sports F1, TNT Sports Ultimate 4K, DAZN, and international English feeds.</li>
    <li><strong>Dedicated Live Events &amp; PPV Section:</strong> Updated daily with direct channel feeds for Saturday 3PM Premier League fixtures, Champions League nights, UFC numbered cards, and heavyweight boxing.</li>
    <li><strong>Anti-Freeze 8.0 Matchday Servers:</strong> Load-balanced European servers engineered to handle peak UK weekend traffic with zero buffering.</li>
</ul>
<h2>How to Watch {selected_topic} on Your TV Tonight</h2>
<ol>
    <li>Open your IPTV app (TiviMate, IPTV Smarters Pro, or IBO Player) on your Firestick or Smart TV and refresh your playlist.</li>
    <li>Browse to the <strong>UK | Live Sports &amp; PPV</strong> category on your EPG guide.</li>
    <li>Select the <strong>UHD 4K</strong> or <strong>1080p 50fps</strong> broadcast feed for crystal-clear stadium motion.</li>
</ol>
<p>Ready for kick-off? Visit <a href="https://waveprotv.com/#pricing">WavePro TV Plans</a> or message us on WhatsApp for an instant 24-hour trial!</p>
"""
    elif any(k in t_lower for k in ["vpn", "isp", "virgin", "bt", "sky broadband", "buffer", "throttl", "freeze", "speed"]):
        article_excerpt = f"Practical technical guide for {selected_topic}—learn how to bypass UK ISP traffic shaping, optimize your router DNS, and achieve buffer-free 4K playback."
        article_html = f"""
<p>If your live television streams suffer from sudden evening slowdowns or weekend matchday blocks on Sky Broadband, Virgin Media, or BT Halo, our technical guide on <strong>{selected_topic}</strong> walks you through the exact network tweaks to restore instant, buffer-free 4K streaming.</p>
<h2>How UK Broadband Providers Affect Live IPTV Traffic</h2>
<p>Major UK ISPs use automated Deep Packet Inspection (DPI) and default security shields (such as Virgin Media Web Safe and Sky Broadband Shield) that throttle continuous video streams during peak hours between 7:00 PM and 11:00 PM.</p>
<ul>
    <li><strong>Switch to Cloudflare DNS (1.1.1.1):</strong> Bypasses slow ISP DNS lookups for faster channel switching.</li>
    <li><strong>Disable ISP Shield Filters:</strong> Turn off Web Safe, Child Safe, and BT Smart Setup inside your broadband account settings.</li>
    <li><strong>Use a 5GHz Wi-Fi Band or Ethernet Adapter:</strong> Eliminates wireless interference from neighbouring routers.</li>
</ul>
<p>Combined with <a href="https://waveprotv.com/#pricing">WavePro TV</a>'s UK-optimized Anti-Freeze servers, these steps guarantee smooth 4K playback on every device.</p>
"""
    else:
        article_excerpt = f"Step-by-step UK walkthrough for {selected_topic}. Learn the fastest setup methods, best player settings, and remote optimization tips for WavePro TV."
        article_html = f"""
<p>Getting the best possible picture quality and channel zapping speed starts with proper setup. In this focused UK tutorial on <strong>{selected_topic}</strong>, we show you step by step how to configure your device and unlock over 20,000+ live channels and 100,000+ 4K movies and series with WavePro TV.</p>
<h2>Key Advantages of Optimizing Your Setup</h2>
<ul>
    <li><strong>Instant EPG TV Guide Sync:</strong> Browse 7-day UK television listings with catch-up playback on major channels.</li>
    <li><strong>Hardware-Accelerated 4K Decoding:</strong> Enable HW+ decoding in your player for silky-smooth 50fps sports and Dolby audio.</li>
    <li><strong>Multi-Device Flexibility:</strong> Works seamlessly across Amazon Firestick 4K Max, Samsung Tizen, LG webOS, Sony Bravia Google TV, and Apple TV 4K.</li>
</ul>
<p>Need personalized setup assistance? Visit <a href="https://waveprotv.com/#pricing">WavePro TV</a> and chat with our 24/7 UK support team on WhatsApp!</p>
"""

# 4. Post to WordPress via REST API
wp_api_endpoint = f"{WP_URL}/wp-json/wp/v2/posts"
clean_password = WP_APP_PASSWORD.replace(" ", "")
credentials = f"{WP_USERNAME}:{clean_password}"
token = base64.b64encode(credentials.encode()).decode("utf-8")

headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}

post_data = {
    "title": selected_topic,
    "content": article_html.strip(),
    "excerpt": article_excerpt.strip(),
    "status": "publish",
    "format": "standard"
}

print(f"\nPosting article to WordPress: {wp_api_endpoint}...")
res = requests.post(wp_api_endpoint, headers=headers, json=post_data, timeout=30)
print(f"WordPress Response Status Code: {res.status_code}")

if res.status_code in [200, 201]:
    post_info = res.json()
    print(f"\nSUCCESS! Post is LIVE at: {post_info.get('link', '')}")
    if topics:
        remaining_topics = topics[1:]
        with open(TOPICS_FILE, "w", encoding="utf-8") as f:
            for t in remaining_topics:
                f.write(t + "\n")
        with open(USED_TOPICS_FILE, "a", encoding="utf-8") as f:
            f.write(selected_topic + "\n")
        print("Updated topics list successfully.")
else:
    print(f"Error publishing post: {res.text}")
    exit(1)
