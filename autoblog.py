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
    "Best IPTV 4K UK (2026)": {
        "excerpt": "Looking for true 4K Ultra HD (3840x2160) IPTV in the UK? Discover how WavePro TV delivers native 4K 50fps/60fps sports, HLG HDR cinema, and zero-buffer British servers.",
        "content": """
<p>If you own a 4K OLED, QLED, or Mini-LED television, watching compressed 720p streams wastes your screen's potential. Finding the <strong>Best IPTV 4K UK</strong> service in 2026 means choosing a provider with genuine, uncompressed <strong>3840x2160 Ultra HD</strong> feeds at 50 and 60 frames per second (fps) rather than upscaled HD.</p>
<h2>What Makes True 4K IPTV Different?</h2>
<ul>
    <li><strong>Native 3840x2160 Resolution &amp; HLG HDR:</strong> Watch flagship football on <em>Sky Sports Main Event UHD</em> and <em>TNT Sports Ultimate 4K</em> with razor-sharp pitch detail and vivid HDR colours.</li>
    <li><strong>High-Bitrate HEVC (H.265) Encoding:</strong> WavePro TV uses next-generation HEVC compression so you get cinema-grade 4K clarity while requiring only 25 Mbps of broadband speed.</li>
    <li><strong>100,000+ 4K &amp; 1080p VOD Movies &amp; Box Sets:</strong> Stream the latest cinema releases and series with Dolby Digital 5.1 and Atmos audio tracks.</li>
</ul>
<h2>Best Devices for 4K IPTV in the UK</h2>
<p>To decode 4K 60fps streams smoothly, pair your <a href="https://waveprotv.com/#pricing">WavePro TV 4K subscription</a> with an <strong>Amazon Firestick 4K Max</strong>, <strong>Nvidia Shield TV Pro</strong>, <strong>Apple TV 4K</strong>, or a modern Samsung/LG/Sony 4K Smart TV.</p>
"""
    },
    "IPTV Free Trial UK: 24H 4K Test": {
        "excerpt": "Test our 20,000+ live channels, 4K UHD sports feeds, and 100,000+ VOD library before you buy. Here is how to activate your 24-hour UK 4K IPTV trial in 2 minutes.",
        "content": """
<p>Before committing to an annual television plan, testing the picture quality and matchday stability on your own broadband connection is essential. With our <strong>IPTV Free Trial UK (24H 4K Test)</strong>, you get full, unrestricted access to WavePro TV's entire UK and international lineup on your Firestick, Smart TV, or smartphone.</p>
<h2>What to Check During Your 24H 4K Test</h2>
<ul>
    <li><strong>True 4K UHD Sports Channels:</strong> Test <em>Sky Sports Main Event UHD</em>, <em>Sky Sports F1 UHD</em>, and <em>TNT Sports Ultimate 4K</em> during live evening broadcasts.</li>
    <li><strong>Instant Channel Switching:</strong> Experience sub-second zapping across BBC, ITV, Sky Cinema, and USA/European entertainment networks.</li>
    <li><strong>7-Day UK EPG &amp; Catch-Up:</strong> Verify full British TV schedules and replay functionality.</li>
</ul>
<h2>How to Get Your 24H Trial Login Now</h2>
<p>Simply message our 24/7 UK team via WhatsApp on <a href="https://waveprotv.com">waveprotv.com</a>, tell us which app or device you use (TiviMate, IPTV Smarters Pro, or IBO Player), and receive your instant test login within minutes!</p>
"""
    },
    "Best IPTV for Firestick UK": {
        "excerpt": "Unlock the full power of your Amazon Fire TV Stick 4K and 4K Max. Compare the best UK IPTV apps, Downloader shortcodes, and 4K playback settings for 2026.",
        "content": """
<p>Over 70% of British IPTV viewers stream using an <strong>Amazon Fire TV Stick 4K</strong> or <strong>Firestick 4K Max</strong>. Choosing the <strong>Best IPTV for Firestick UK</strong> ensures your device loads channels instantly, displays a clean Sky-style TV guide, and plays 4K 50fps football without overheating or buffering.</p>
<h2>Why WavePro TV Is Built for Amazon Firestick 4K</h2>
<ul>
    <li><strong>1-Click Xtream Codes Login:</strong> No complicated M3U files—just type your short Server URL, Username, and Password into TiviMate or IPTV Smarters Pro.</li>
    <li><strong>Hardware-Accelerated 4K HEVC Streams:</strong> Optimized specifically for the Firestick 4K Max's quad-core processor and Wi-Fi 6 antenna.</li>
    <li><strong>Fast Downloader Installation:</strong> Use code <code>250931</code> (Smarters Pro) or <code>272483</code> (TiviMate) in the free Downloader app to get set up in under 3 minutes.</li>
</ul>
<p>Order your Firestick-ready subscription today at <a href="https://waveprotv.com/#pricing">WavePro TV</a>!</p>
"""
    },
    "How to Watch 4K IPTV Without Buffering": {
        "excerpt": "Streaming 4K Ultra HD live channels requires stable throughput and hardware decoding. Follow these 5 quick UK network and player tweaks for zero-buffer 4K IPTV.",
        "content": """
<p>Streaming live <strong>4K IPTV (3840x2160 at 50/60fps)</strong> delivers breathtaking stadium and cinema clarity, but it also demands a clean connection between your broadband router and your television. If you want to watch <strong>4K IPTV without buffering</strong> in the UK, follow these five proven optimizations.</p>
<h2>5 Steps for Buffer-Free 4K UHD Streaming</h2>
<ol>
    <li><strong>Enable Hardware Decoding (HW+):</strong> Always set your IPTV player (TiviMate or Smarters) to Hardware Decoder so your TV's GPU handles 4K HEVC video effortlessly.</li>
    <li><strong>Use 5GHz Wi-Fi or Ethernet:</strong> Never stream 4K over 2.4GHz Wi-Fi. Connect to your router's 5GHz band or plug in a wired Ethernet adapter.</li>
    <li><strong>Disable ISP Traffic Filters:</strong> Turn off <em>Virgin Media Web Safe</em>, <em>Sky Broadband Shield</em>, and <em>BT Smart Setup</em> so your ISP doesn't throttle high-bitrate 4K packets.</li>
    <li><strong>Set DNS to Cloudflare (1.1.1.1):</strong> Speeds up channel handshakes and prevents ISP DNS blocks.</li>
    <li><strong>Choose a True Anti-Freeze 4K Server:</strong> <a href="https://waveprotv.com/#pricing">WavePro TV</a> uses dedicated UK/EU load-balanced servers with 99.9% uptime.</li>
</ol>
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
