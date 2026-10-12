import os
import re
import random
import time
import base64
import json
from datetime import datetime, timezone
import requests

# 1. Configuration
WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")
GH_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
FORCE_POST = os.environ.get("FORCE_POST", "").lower() == "true"

if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
    print("Error: Missing WordPress configuration (WP_URL, WP_USERNAME, or WP_APP_PASSWORD).")
    exit(1)

wp_api_endpoint = f"{WP_URL}/wp-json/wp/v2/posts"
clean_password = WP_APP_PASSWORD.replace(" ", "")
credentials = f"{WP_USERNAME}:{clean_password}"
token = base64.b64encode(credentials.encode()).decode("utf-8")

headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# Check if a post was already published today (UTC / UK date) so multiple cron slots between 5AM-4PM guarantee 1 post/day
today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
if not FORCE_POST:
    try:
        recent_res = requests.get(f"{wp_api_endpoint}?per_page=1", headers=headers, timeout=15)
        if recent_res.status_code == 200 and len(recent_res.json()) > 0:
            latest_post_date = recent_res.json()[0].get("date_gmt", "")[:10]
            if latest_post_date == today_str:
                print(f"A blog post was already published today ({today_str}). Exiting cleanly.")
                exit(0)
    except Exception as e:
        print(f"Date check warning: {e}")

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

# Organic randomized delay (10 to 60 seconds)
delay_seconds = random.randint(10, 60)
print(f"Applying organic delay of {delay_seconds} seconds...")
time.sleep(delay_seconds)

article_html = None
article_excerpt = None

# Custom topic-specific dictionary for queued topics so descriptions & content are always 100% tailored
CUSTOM_TOPIC_GUIDES = {
    "UK IPTV 24-Hour Free Trial: How to Test Buffer-Free Quality in 2026": {
        "excerpt": "Want to test channel stability, 4K sports frame rates, and VOD speed before subscribing? Learn how to claim and test your WavePro TV 24-hour UK trial on Firestick and Smart TV.",
        "content": """
<p>Before committing to an annual television subscription, every smart UK viewer wants to see how channels perform during peak evening hours on their own broadband connection. With a <strong>WavePro TV 24-Hour Trial</strong>, you can test over 20,000+ live channels, 50fps UK sports feeds, and our 100,000+ 4K movie library directly on your Amazon Firestick or Smart TV.</p>
<h2>What to Test During Your 24-Hour UK IPTV Trial</h2>
<ul>
    <li><strong>Peak-Time Sports Stability (7:30 PM – 10:00 PM GMT):</strong> Switch between Sky Sports Main Event UHD, TNT Sports Ultimate 4K, and live PPV events to verify zero buffering on your ISP.</li>
    <li><strong>Channel Zapping Speed:</strong> Test how quickly channels load using Xtream Codes API on TiviMate or IPTV Smarters Pro.</li>
    <li><strong>7-Day UK EPG &amp; Catch-Up:</strong> Browse full British TV listings across BBC, ITV, Channel 4, and Sky Entertainment.</li>
</ul>
<h2>How to Request Your Instant Trial on WhatsApp</h2>
<ol>
    <li>Install <strong>TiviMate</strong>, <strong>IPTV Smarters Pro</strong>, or <strong>IBO Player</strong> on your streaming device.</li>
    <li>Click the WhatsApp button on <a href="https://waveprotv.com">waveprotv.com</a> and tell our UK support team which device you use.</li>
    <li>Receive your Xtream Codes login credentials in minutes and start watching immediately!</li>
</ol>
"""
    },
    "How to Watch Formula 1 and MotoGP Live in the UK in 4K 60FPS": {
        "excerpt": "Stream every Formula 1 Grand Prix, Sprint Qualifying, and MotoGP race weekend live in 4K UHD and 50/60fps via Sky Sports F1 UHD and TNT Sports without paying £70+/month.",
        "content": """
<p>For British motorsport fans, following both <strong>Formula 1</strong> and <strong>MotoGP</strong> across an entire 24-race calendar requires two separate expensive subscriptions: <strong>Sky Sports F1</strong> for Grand Prix weekends and <strong>TNT Sports</strong> for MotoGP, WorldSBK, and Formula E. With <strong>WavePro TV</strong>, you get every practice session, qualifying shootout, Sprint race, and Sunday Grand Prix in native 4K UHD and 50fps/60fps under one roof.</p>
<h2>Complete UK Motorsport Channels Included on WavePro TV</h2>
<ul>
    <li><strong>Sky Sports F1 UHD (4K 50fps):</strong> Full Martin Brundle and Crofty commentary, pit-lane feeds, driver onboard cameras, and Ted's Notebook.</li>
    <li><strong>TNT Sports 2 &amp; Ultimate 4K:</strong> Every MotoGP, Moto2, and Moto3 session live with British studio presentation.</li>
    <li><strong>F1TV Pro International Feeds:</strong> Dedicated driver tracker, telemetry data channel, and international English feeds.</li>
</ul>
<p>Never miss lights out again—explore our motorsport-ready packages at <a href="https://waveprotv.com/#pricing">WavePro TV</a>!</p>
"""
    },
    "Best UK Channels on IPTV: BBC, ITV, Channel 4, Sky Cinema and Documentaries": {
        "excerpt": "Explore the complete UK entertainment lineup on WavePro TV—including regional BBC & ITV HD variants, all 11 Sky Cinema 4K channels, Sky Atlantic, Discovery, and British kids' television.",
        "content": """
<p>While live football often grabs the headlines, a truly great UK IPTV subscription replaces your entire household's living room television. <strong>WavePro TV</strong> delivers the complete British free-to-air and premium entertainment lineup in 1080p Full HD and 4K Ultra HD.</p>
<h2>What UK Entertainment &amp; Movie Channels Are Included?</h2>
<ul>
    <li><strong>UK Terrestrial &amp; Regional HD:</strong> All regional variants of BBC One HD, BBC Two, ITV1–4 HD, Channel 4 HD, Channel 5, E4, More4, and Dave.</li>
    <li><strong>Sky Entertainment &amp; Drama:</strong> Sky Atlantic VIP (home of flagship HBO dramas), Sky Max, Sky Witness, Sky Comedy, Gold, and Alibi.</li>
    <li><strong>All 11 Sky Cinema Channels in FHD/4K:</strong> Sky Cinema Premiere, Select, Hits, Greats, Animation, Action, Comedy, Thriller, Drama, and Sci-Fi/Horror.</li>
    <li><strong>Documentaries &amp; History:</strong> Discovery Channel, National Geographic Wild, Sky Documentaries, Sky Nature, History, and Crime+Investigation.</li>
</ul>
<p>Upgrade your family's home entertainment today at <a href="https://waveprotv.com/#pricing">WavePro TV</a>.</p>
"""
    }
}

if selected_topic in CUSTOM_TOPIC_GUIDES:
    article_excerpt = CUSTOM_TOPIC_GUIDES[selected_topic]["excerpt"]
    article_html = CUSTOM_TOPIC_GUIDES[selected_topic]["content"].strip()

system_prompt = (
    "You are a premier UK tech journalist, streaming specialist, and SEO authority writing for 'WavePro TV' (waveprotv.com). "
    "Write an engaging, highly specific, 900-word SEO-optimized blog post in British English that directly answers and focuses 100% on the exact title provided. "
    "Format in clean semantic HTML with <p>, <h2>, <h3>, <ul>, <li>, and <strong> tags (do NOT include <h1> or markdown code fences). "
    "The very first <p> paragraph MUST be a compelling 2-sentence summary specifically tailored to the exact topic so it can also serve as the meta description/excerpt."
)
user_prompt = f"Write a comprehensive, topic-specific UK guide titled: '{selected_topic}'."

# Attempt 1: GitHub Models Inference API
if not article_html and GH_TOKEN:
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

# Attempt 2: Pollinations OpenAI-compatible AI endpoint
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

if article_html and not article_excerpt:
    article_html = re.sub(r"^```(?:html)?\s*", "", article_html)
    article_html = re.sub(r"\s*```$", "", article_html).strip()
    first_p = re.search(r"<p>(.*?)</p>", article_html, re.DOTALL | re.IGNORECASE)
    if first_p:
        clean_p = re.sub(r"<[^>]+>", "", first_p.group(1)).strip()
        if len(clean_p) > 40:
            article_excerpt = clean_p[:240]

# Fallback: Topic-Specific UK Article & Excerpt Generator
if not article_html or not article_excerpt:
    t_lower = selected_topic.lower()
    if any(k in t_lower for k in ["ppv", "boxing", "ufc", "f1", "formula 1", "football", "premier league", "champions league", "sports", "sky sports", "tnt", "scottish", "fa cup", "nfl", "nba"]):
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
    elif any(k in t_lower for k in ["vpn", "isp", "virgin", "bt", "sky broadband", "buffer", "throttl", "freeze", "speed", "anti-freeze"]):
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
