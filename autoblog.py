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
    },
    "IPTV Smarters Pro Setup UK": {
        "excerpt": "Complete 2026 UK tutorial for installing and configuring IPTV Smarters Pro on Firestick, Samsung/LG Smart TV, Android, and iOS using Xtream Codes API.",
        "content": """
<p><strong>IPTV Smarters Pro</strong> remains one of the easiest and most reliable streaming apps in the UK because it separates <em>Live TV</em>, <em>Movies (VOD)</em>, and <em>Series</em> into clean, family-friendly sections. Here is how to complete your <strong>IPTV Smarters Pro Setup UK</strong> in under three minutes.</p>
<h2>Step-by-Step Installation &amp; Login</h2>
<ol>
    <li><strong>On Amazon Firestick / Android TV:</strong> Open the free <em>Downloader</em> app, enter code <code>250931</code>, and install IPTV Smarters Pro.</li>
    <li><strong>On Samsung, LG, or iOS:</strong> Download <em>Smarters Player Lite</em> directly from your official App Store.</li>
    <li><strong>Select Xtream Codes API Login:</strong> Enter any profile name (e.g., WavePro 4K) along with the Username, Password, and Server URL provided by <a href="https://waveprotv.com/#pricing">WavePro TV</a>.</li>
    <li><strong>Enable HW+ Decoder:</strong> Go to <em>Settings &rarr; Player Settings</em> inside Smarters and select <strong>Hardware Decoder</strong> for smooth 4K and 50fps sports playback.</li>
</ol>
"""
    },
    "Watch Premier League in 4K UHD": {
        "excerpt": "Experience every Premier League match in native 3840x2160 4K UHD and 50fps—including Super Sunday, TNT Sports Ultimate 4K, and Saturday 3PM kickoffs.",
        "content": """
<p>There is nothing quite like watching live top-flight English football in native <strong>4K Ultra HD (3840x2160) at 50 frames per second</strong>. When you <strong>Watch Premier League in 4K UHD</strong> with WavePro TV, every blade of grass, shirt number, and fast counter-attack is rendered without motion blur.</p>
<h2>Every Premier League Kickoff Slot Covered in 4K &amp; FHD</h2>
<ul>
    <li><strong>Sky Sports Main Event UHD &amp; Premier League UHD:</strong> Friday Night Football, Saturday 5:30 PM, Super Sunday doubleheaders, and Monday Night Football in HLG HDR.</li>
    <li><strong>TNT Sports Ultimate 4K:</strong> Saturday 12:30 PM lunchtime clashes and full midweek Premier League rounds in 4K 50fps.</li>
    <li><strong>Saturday 3:00 PM Blackout Fixtures:</strong> Stream every 3PM kickoff live via Hub Premier 4K, Peacock, Optus Sport, and SuperSport Premier League.</li>
</ul>
<p>Get matchday ready in 2 minutes at <a href="https://waveprotv.com/#pricing">WavePro TV</a>!</p>
"""
    },
    "Best 4K IPTV Subscription UK": {
        "excerpt": "Compare what makes the Best 4K IPTV Subscription in the UK for 2026: real 3840x2160 HEVC channels, 100,000+ 4K VOD titles, 99.9% matchday uptime, and instant activation.",
        "content": """
<p>Upgrading to the <strong>Best 4K IPTV Subscription UK</strong> transforms your television from standard broadcast quality into a true home cinema and live sports arena. Unlike budget playlists that label 720p feeds as 4K, <strong>WavePro TV</strong> provides dedicated high-bitrate <strong>HEVC 4K UHD</strong> and <strong>RAW 50fps</strong> channels.</p>
<h2>What Is Included in Our 2026 UK 4K Subscription?</h2>
<ul>
    <li><strong>20,000+ Live Channels:</strong> Full UK, Irish, US, Canadian, and European lineups with dedicated 4K UHD sports and entertainment categories.</li>
    <li><strong>100,000+ Movies &amp; Series on Demand:</strong> Daily updated 4K HDR movies and complete box sets from Netflix, Disney+, Apple TV+, and Prime Video.</li>
    <li><strong>Anti-Freeze 8.0 UK Routing:</strong> Zero buffering during peak Premier League, Champions League, and boxing PPV broadcasts.</li>
</ul>
<p>View our 1, 3, 6, and 12-month packages today at <a href="https://waveprotv.com/#pricing">waveprotv.com/#pricing</a>.</p>
"""
    },
    "TiviMate 4K Setup Guide UK": {
        "excerpt": "Master TiviMate IPTV Player on your Firestick 4K Max or Nvidia Shield. Learn the Downloader install code, Xtream login steps, and best 4K 50fps EPG settings.",
        "content": """
<p>For UK viewers using an Amazon Firestick 4K Max, Sony Bravia Google TV, or Nvidia Shield, <strong>TiviMate</strong> is the undisputed #1 IPTV player. Follow this <strong>TiviMate 4K Setup Guide UK</strong> to get Sky Q-style TV guides and multi-screen 4K sports running smoothly.</p>
<h2>How to Install &amp; Optimize TiviMate for 4K IPTV</h2>
<ol>
    <li>Open <strong>Downloader</strong> on your Firestick or Android TV and enter code <code>272483</code> to install the latest official TiviMate APK.</li>
    <li>Click <strong>Add Playlist &rarr; Xtream Codes</strong> and enter your <a href="https://waveprotv.com/#pricing">WavePro TV</a> Server URL, Username, and Password.</li>
    <li>Go to <strong>Settings &rarr; Playback</strong>, set Buffer Size to <em>Medium</em>, and enable <strong>Auto Frame Rate (AFR)</strong> so 50fps UK football matches your TV's refresh rate seamlessly.</li>
</ol>
"""
    },
    "Watch UFC & Boxing PPV Live UK": {
        "excerpt": "Stop paying £24.99 per fight night on TNT Sports Box Office, Sky Sports Box Office, and DAZN PPV. Stream every heavyweight boxing main event and UFC card live in HD/4K.",
        "content": """
<p>With major heavyweight boxing clashes and numbered UFC cards now locked behind £19.99 to £29.99 pay-per-view paywalls across <strong>Sky Sports Box Office</strong>, <strong>TNT Sports Box Office</strong>, and <strong>DAZN PPV</strong>, fight fans in the UK face huge extra bills every month. With <strong>WavePro TV</strong>, every single PPV fight night is included automatically in your subscription.</p>
<h2>Where to Find Live Fight Nights on Your EPG</h2>
<ul>
    <li><strong>UK | Box Office &amp; Live PPV Events:</strong> Dedicated channels for Sky Sports Box Office HD, TNT Sports Box Office HD, and DAZN PPV UK/US.</li>
    <li><strong>UFC Fight Pass &amp; ESPN+ PPV Feeds:</strong> Watch Early Prelims, Prelims, and the Main Card in 1080p 60fps and 4K UHD.</li>
</ul>
<p>Never miss ring walks again—join <a href="https://waveprotv.com/#pricing">WavePro TV</a> today!</p>
"""
    },
    "Smart TV 4K IPTV Setup (Samsung & LG)": {
        "excerpt": "Install 4K IPTV directly on your Samsung Tizen or LG webOS Smart TV in 3 minutes using IBO Player Pro, SmartOne IPTV, or Smarters Player—no external box needed.",
        "content": """
<p>Your <strong>Samsung QLED/OLED (Tizen)</strong> or <strong>LG OLED/QNED (webOS)</strong> television already has the hardware power to decode 4K HDR streams natively. Follow this <strong>Smart TV 4K IPTV Setup</strong> guide to watch all 20,000+ channels using your original TV remote.</p>
<h2>Fast Setup on Samsung &amp; LG App Stores</h2>
<ol>
    <li>Open the <strong>Samsung Apps Store</strong> or <strong>LG Content Store</strong> on your television.</li>
    <li>Download <strong>IBO Player Pro</strong>, <strong>SmartOne IPTV</strong>, or <strong>IPTV Smarters Pro</strong>.</li>
    <li>Share the on-screen Device ID &amp; Key with our <a href="https://waveprotv.com">WavePro TV WhatsApp support team</a> (or log in with your Xtream Codes) and we will load your full 4K UK channel list remotely in seconds!</li>
</ol>
"""
    },
    "Watch Formula 1 Live in 4K UHD": {
        "excerpt": "Follow every F1 Practice, Sprint, Qualifying, and Sunday Grand Prix in native 3840x2160 4K 50fps on Sky Sports F1 UHD and F1TV Pro feeds with WavePro TV.",
        "content": """
<p>Formula 1 is a sport of millisecond margins and breathtaking speed, and watching it in compressed standard definition doesn't do it justice. When you <strong>Watch Formula 1 Live in 4K UHD</strong> on WavePro TV, you get the full <strong>Sky Sports F1 UHD (3840x2160 at 50fps)</strong> broadcast alongside dedicated onboard and telemetry feeds.</p>
<h2>Every F1 Session Live &amp; On-Demand</h2>
<ul>
    <li><strong>Sky Sports F1 UHD &amp; Main Event 4K:</strong> Full UK studio build-up, Martin's Grid Walk, live race coverage, and Ted's Notebook.</li>
    <li><strong>F1TV Pro Multi-Cam Feeds:</strong> Pit lane channel, live driver tracker map, and onboard cameras.</li>
</ul>
<p>Start your engines at <a href="https://waveprotv.com/#pricing">WavePro TV</a>!</p>
"""
    },
    "Best UK IPTV Channels List 2026": {
        "excerpt": "Browse the full 2026 UK IPTV channel list included with WavePro TV—covering Sky Sports 4K, TNT Sports Ultimate, Sky Cinema, BBC/ITV Regional HD, and 100,000+ VOD.",
        "content": """
<p>Curious what channels are actually included when you switch from cable to IPTV? Here is the complete <strong>Best UK IPTV Channels List 2026</strong> included with every <a href="https://waveprotv.com/#pricing">WavePro TV</a> package:</p>
<ul>
    <li><strong>UK Freeview &amp; Regional HD:</strong> BBC One/Two/Three/Four HD, ITV1–4 HD, Channel 4/5 HD, E4, Dave, Gold.</li>
    <li><strong>UK Sports (4K UHD &amp; 50fps):</strong> All 11 Sky Sports channels, TNT Sports 1–4 &amp; Ultimate 4K, Premier Sports 1–2, Racing TV, Sky Sports Box Office, and 3PM EPL Matchday feeds.</li>
    <li><strong>Sky Cinema &amp; Entertainment:</strong> All 11 Sky Cinema FHD/4K channels, Sky Atlantic VIP, Sky Max, Discovery, Nat Geo, and UK Kids networks.</li>
    <li><strong>International Bouquets:</strong> Full USA, Canada, Ireland, European, Arabic, and Worldwide live TV + 100,000+ 4K/FHD Movies &amp; Series.</li>
</ul>
"""
    },
    "Fix IPTV Buffering on Virgin & BT": {
        "excerpt": "Stop evening slowdowns and Saturday football blocks on Virgin Media Hub and BT Smart Hub. Apply these 3 quick router and DNS tweaks for instant 4K streaming.",
        "content": """
<p>If your streams freeze during live weekend football on <strong>Virgin Media</strong> or <strong>BT Broadband</strong>, your ISP's built-in traffic filters are likely throttling your connection. Here is how to <strong>Fix IPTV Buffering on Virgin &amp; BT</strong> in under two minutes:</p>
<ol>
    <li><strong>Turn Off ISP Security Shields:</strong> Disable <em>Virgin Media Web Safe / Child Safe</em> in My Virgin Media, or turn off <em>BT Web Protect &amp; Smart Setup</em> in your BT Hub settings.</li>
    <li><strong>Switch DNS to 1.1.1.1:</strong> Change your Firestick or Smart TV DNS from automatic to Cloudflare (<code>1.1.1.1</code>) to bypass slow ISP DNS servers.</li>
    <li><strong>Use 5GHz Wi-Fi or WireGuard VPN:</strong> Connect via 5GHz Wi-Fi and pair with <a href="https://waveprotv.com/#pricing">WavePro TV</a>'s Anti-Freeze 8.0 servers for uninterrupted 4K playback.</li>
</ol>
"""
    },
    "Best 4K IPTV for Apple TV & iPhone": {
        "excerpt": "Stream native 4K HDR live TV and movies on Apple TV 4K, iPad Pro, and iPhone 16 using top App Store players like UHF, iPlayTV, and Smarters Player Lite.",
        "content": """
<p>The <strong>Apple TV 4K</strong> and modern <strong>iPhones/iPads</strong> pack desktop-class A-series and M-series chips that decode 4K HEVC streams effortlessly. Choosing the <strong>Best 4K IPTV for Apple TV &amp; iPhone</strong> lets you enjoy Dolby Vision VOD, Picture-in-Picture sports, and iCloud playlist syncing across all your Apple devices.</p>
<h2>Top 3 App Store Players for WavePro TV 4K</h2>
<ul>
    <li><strong>UHF – Love Your IPTV:</strong> Best overall for Apple TV 4K, iPhone, iPad, and Mac with instant iCloud sync and native Metal 4K decoding.</li>
    <li><strong>iPlayTV:</strong> Sleek tvOS interface with rich UK EPG timelines and channel logos.</li>
    <li><strong>Smarters Player Lite:</strong> Free download on the UK App Store with fast Xtream Codes API login.</li>
</ul>
<p>Get your Apple-ready 4K login at <a href="https://waveprotv.com/#pricing">WavePro TV</a>!</p>
"""
    },
    "Sky Sports & TNT Sports in 4K IPTV": {
        "excerpt": "Watch Sky Sports Main Event UHD and TNT Sports Ultimate 4K together in one subscription. Save over £900/year while enjoying every Premier League and Champions League match.",
        "content": """
<p>Paying separately for Sky Q/Glass UHD and TNT Sports via Discovery+ Premium now costs UK households nearly £100 every month. By streaming <strong>Sky Sports &amp; TNT Sports in 4K IPTV</strong> with WavePro TV, you get every single channel from both broadcasters in native <strong>3840x2160 4K UHD and 50fps</strong> on one screen.</p>
<ul>
    <li><strong>Sky Sports UHD Channels:</strong> Main Event UHD, Premier League, Football, F1 UHD, Cricket, Golf, Tennis, and Arena.</li>
    <li><strong>TNT Sports 4K Channels:</strong> TNT Sports 1, 2, 3, 4, TNT Sports Ultimate 4K, and Box Office PPV events.</li>
</ul>
<p>Switch today at <a href="https://waveprotv.com/#pricing">WavePro TV</a> and get instant activation in 2 minutes!</p>
"""
    },
    "WavePro TV 4K UK Review 2026": {
        "excerpt": "An inside look at WavePro TV's 2026 UK 4K service—testing our 20,000+ live channels, Anti-Freeze 8.0 matchday servers, 100,000+ VOD library, and 24/7 WhatsApp support.",
        "content": """
<p>Why have thousands of British cord-cutters made <strong>WavePro TV</strong> their primary home entertainment service in 2026? In this comprehensive <strong>WavePro TV 4K UK Review</strong>, we examine the server infrastructure, picture quality, and customer support that set WavePro TV apart.</p>
<h2>Key Highlights of WavePro TV 4K</h2>
<ul>
    <li><strong>True 4K UHD &amp; 50fps Sports:</strong> Uncompressed feeds for Premier League, Champions League, Formula 1, UFC, and Boxing PPV.</li>
    <li><strong>Anti-Freeze 8.0 European CDN:</strong> 99.9% uptime even during peak Saturday 3PM and Tuesday 8PM kickoffs.</li>
    <li><strong>100,000+ 4K/FHD VOD Library:</strong> Updated daily with the newest cinema movies and complete streaming box sets.</li>
    <li><strong>3-Minute WhatsApp Support:</strong> Friendly 24/7 assistance to help you configure Firestick, Smart TV, Android TV, or Apple TV.</li>
</ul>
<p>Experience it yourself—view our plans or request a 24H trial at <a href="https://waveprotv.com/#pricing">waveprotv.com</a>!</p>
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
