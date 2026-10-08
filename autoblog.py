import os
import random
import requests
import base64
import json

# 1. Configuration
WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")
GH_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")

print(f"Checking environment variables:")
print(f" - WP_URL: {WP_URL}")
print(f" - WP_USERNAME: {WP_USERNAME}")
print(f" - WP_APP_PASSWORD set: {bool(WP_APP_PASSWORD)}")
print(f" - GH_TOKEN set: {bool(GH_TOKEN)}")

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
    selected_topic = "How to Choose the Best IPTV Subscription in 2026: Complete Guide"
else:
    selected_topic = topics[0]

print(f"\nProcessing Topic: '{selected_topic}'")

# 3. Generate Article Content
article_html = None
article_excerpt = f"Complete expert guide on '{selected_topic}'. Tips, installation instructions, and best streaming practices for WavePro TV subscribers."

# Attempt AI Generation if GH_TOKEN is present
if GH_TOKEN:
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://models.github.ai/inference",
            api_key=GH_TOKEN
        )
        system_prompt = (
            "You are an expert tech writer and SEO specialist for 'WavePro TV' (waveprotv.com), a premier 4K IPTV service. "
            "Write an engaging, highly informative, 1000-word SEO-optimized blog post in clean HTML format. "
            "Use <h2>, <h3>, <p>, <ul>, <li>, and <strong> tags. Include an introduction, key benefits, step-by-step setup, "
            "troubleshooting FAQs, and conclude with a Call-To-Action to get a 24H trial at waveprotv.com. Do NOT include ```html markdown fences."
        )
        user_prompt = f"Write an in-depth article about: '{selected_topic}'."

        for model in ["gpt-4o-mini", "meta-llama-3.1-70b-instruct", "gpt-4o"]:
            try:
                print(f"Attempting AI generation with model: {model}...")
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                article_html = resp.choices[0].message.content.strip()
                print("AI content generation successful!")
                break
            except Exception as e:
                print(f"Model {model} failed: {e}")
    except Exception as e:
        print(f"AI Client initialization failed: {e}")

# Fallback: Rich, SEO-Optimized Built-in Article Generator
if not article_html:
    print("Generating comprehensive built-in SEO article...")
    article_html = f"""
    <p>Are you looking for the ultimate streaming experience without buffering or freezing? In this detailed 2026 guide, we explore everything you need to know about <strong>{selected_topic}</strong>, so you can enjoy live television, international sports, and 4K cinema with total peace of mind.</p>
    
    <h2>Why High-Quality Streaming Matters in 2026</h2>
    <p>Cord-cutting has reached an all-time high. Modern viewers no longer want to pay expensive cable bills for a handful of standard channels. Instead, next-generation IPTV services deliver over 20,000+ live premium channels and on-demand video libraries directly over high-speed internet connections.</p>
    <ul>
        <li><strong>Crystal-Clear Ultra HD:</strong> Enjoy 4K and FHD streams at 60 frames per second without frame drops.</li>
        <li><strong>Anti-Freeze 8.0 Technology:</strong> Redundant server clusters ensure smooth playback during high-demand live sporting events.</li>
        <li><strong>Multi-Device Compatibility:</strong> Stream effortlessly on Amazon Firestick, Android TV, Smart TVs, iOS, and PC.</li>
    </ul>

    <h2>Step-by-Step Setup & Configuration</h2>
    <p>Setting up your streaming playlist is quick and straightforward. Follow these essential steps to get started in less than five minutes:</p>
    <ol>
        <li><strong>Choose a Reliable IPTV Application:</strong> Popular options include IPTV Smarters Pro, TiviMate, GSE Smart IPTV, and NetIPTV.</li>
        <li><strong>Enter Your Subscription Details:</strong> Input your M3U playlist URL or Xtream Codes API credentials provided by WavePro TV.</li>
        <li><strong>Update Your EPG (Electronic Program Guide):</strong> Synchronize the channel guide to view real-time TV schedules.</li>
        <li><strong>Optimize Your Player Settings:</strong> Switch the hardware decoder to Hardware Plus (HW+) and set the stream format to HLS or MPEG-TS for maximum stability.</li>
    </ol>

    <h2>Expert Tips for Buffer-Free Playback</h2>
    <p>If you experience occasional stuttering, apply these proven optimizations:</p>
    <ul>
        <li>Connect via a 5GHz Wi-Fi band or an Ethernet cable for consistent throughput.</li>
        <li>Maintain an internet connection speed of at least 25 Mbps for 4K streaming.</li>
        <li>Clear your streaming device cache weekly to prevent memory congestion.</li>
        <li>Use a high-speed VPN if your internet service provider throttles video streaming traffic.</li>
    </ul>

    <h2>Frequently Asked Questions</h2>
    <h3>Can I watch live sports and pay-per-view events?</h3>
    <p>Yes! With WavePro TV, all major sporting networks, Premier League, Champions League, UFC, and Boxing pay-per-view events are included in full HD and 4K resolution.</p>

    <h3>How many devices can stream simultaneously?</h3>
    <p>Standard plans allow 1 active connection, while annual packages and multi-room options support simultaneous streaming across multiple devices.</p>

    <h3>Do I need technical experience to install the service?</h3>
    <p>Not at all. We provide step-by-step video tutorials and 24/7 dedicated WhatsApp support to assist you through every step of configuration.</p>

    <h2>Start Watching Today with WavePro TV</h2>
    <p>Ready to upgrade your home entertainment? Visit <a href="https://waveprotv.com" target="_blank" rel="noopener">WavePro TV</a> today to explore our premium channel packages or request an instant 24-hour test trial!</p>
    """

# Clean code fences if present
if article_html.startswith("```html"):
    article_html = article_html[7:]
if article_html.startswith("```"):
    article_html = article_html[3:]
if article_html.endswith("```"):
    article_html = article_html[:-3]
article_html = article_html.strip()

# 4. Post to WordPress via REST API
wp_api_endpoint = f"{WP_URL}/wp-json/wp/v2/posts"
clean_password = WP_APP_PASSWORD.replace(" ", "")

credentials = f"{WP_USERNAME}:{clean_password}"
token = base64.b64encode(credentials.encode()).decode("utf-8")

headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}

# Permanently delete default 'Hello world' post (ID 1) if present
try:
    print("Checking and permanently deleting default 'Hello world' post (ID 1)...")
    del_res = requests.delete(f"{wp_api_endpoint}/1?force=true", headers=headers, timeout=15)
    if del_res.status_code in [200, 201, 204]:
        print("Successfully permanently deleted 'Hello world!' (Post ID 1).")
    else:
        print(f"Delete response status code: {del_res.status_code}")
except Exception as e:
    print(f"Cleanup check warning: {e}")

post_data = {
    "title": selected_topic,
    "content": article_html,
    "excerpt": article_excerpt,
    "status": "publish",
    "format": "standard"
}

print(f"\nPosting article to WordPress: {wp_api_endpoint}...")
res = requests.post(wp_api_endpoint, headers=headers, json=post_data, timeout=30)

print(f"WordPress Response Status Code: {res.status_code}")

if res.status_code in [200, 201]:
    post_info = res.json()
    post_link = post_info.get("link", "")
    print(f"\nSUCCESS! Post is LIVE at: {post_link}")

    # Remove published topic from queue
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
