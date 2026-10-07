import os
import random
import requests
import base64
import json
from openai import OpenAI

# 1. Configuration from Environment Variables (GitHub Secrets)
WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")

# Uses GitHub's own free AI Token
GH_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")

if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD or not GH_TOKEN:
    print("Error: Missing required environment variables (WP_URL, WP_USERNAME, WP_APP_PASSWORD, GH_TOKEN).")
    exit(1)

# Connect to GitHub Models AI (Official GitHub Endpoint)
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=GH_TOKEN
)

# 2. Pick a Topic
TOPICS_FILE = "topics.txt"
USED_TOPICS_FILE = "used_topics.txt"

topics = []
if os.path.exists(TOPICS_FILE):
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip()]

if not topics:
    print("Topics list is empty! Using fallback topic.")
    selected_topic = "How to Choose the Best IPTV Subscription in 2026: Complete Guide"
else:
    selected_topic = topics[0]

print(f"Selected Topic for today: '{selected_topic}'")

# 3. Generate Article using GitHub Models AI
system_prompt = """
You are an expert tech writer and SEO specialist for 'WavePro TV' (waveprotv.com), a premier 4K IPTV service.
Write an engaging, highly informative, 1000-word SEO-optimized blog post in HTML format.

Formatting requirements:
- Return ONLY clean HTML (no <html>, <head>, or <body> wrappers).
- Use <h2>, <h3>, <p>, <ul>, <li>, and <strong> tags.
- Break up text into short, readable paragraphs.
- Include a step-by-step tutorial or numbered list.
- Include a 'Frequently Asked Questions' section with 3 FAQs.
- End with a strong Call-To-Action inviting readers to test WavePro TV's 24-hour trial at waveprotv.com.
- Do NOT use Markdown code fences (no ```html).
"""

user_prompt = f"Write a comprehensive, SEO-friendly guide about: '{selected_topic}'. Target IPTV users, streaming enthusiasts, and cord-cutters."

models_to_try = ["gpt-4o-mini", "meta-llama-3.1-70b-instruct", "gpt-4o"]
article_html = None

for model_name in models_to_try:
    try:
        print(f"Calling GitHub AI using model '{model_name}'...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        article_html = response.choices[0].message.content.strip()
        print(f"Article successfully generated with {model_name}!")
        break
    except Exception as e:
        print(f"Model {model_name} failed: {e}. Trying next fallback...")

if not article_html:
    print("Error: All AI models failed to generate content.")
    exit(1)

# Clean code fences if present
if article_html.startswith("```html"):
    article_html = article_html[7:]
if article_html.startswith("```"):
    article_html = article_html[3:]
if article_html.endswith("```"):
    article_html = article_html[:-3]
article_html = article_html.strip()

# 4. Generate Article Excerpt
try:
    excerpt_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Write a 1-sentence catchy meta description (under 160 characters) for this blog post."},
            {"role": "user", "content": selected_topic}
        ],
        temperature=0.5
    )
    article_excerpt = excerpt_response.choices[0].message.content.strip()
except Exception:
    article_excerpt = f"Read our comprehensive guide on {selected_topic}. Tips, setup, and troubleshooting for WavePro TV subscribers."

# 5. Publish to WordPress via REST API
wp_api_endpoint = f"{WP_URL}/wp-json/wp/v2/posts"

# Strip potential spaces in Application Password
clean_password = WP_APP_PASSWORD.replace(" ", "")
credentials = f"{WP_USERNAME}:{clean_password}"
token = base64.b64encode(credentials.encode()).decode("utf-8")

headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}

post_data = {
    "title": selected_topic,
    "content": article_html,
    "excerpt": article_excerpt,
    "status": "publish",  # Post live immediately
    "format": "standard"
}

print(f"Posting to WordPress: {wp_api_endpoint}...")
res = requests.post(wp_api_endpoint, headers=headers, json=post_data, timeout=30)

if res.status_code in [200, 201]:
    post_info = res.json()
    post_link = post_info.get("link", "")
    print(f"SUCCESS! Article published live at: {post_link}")

    # Remove used topic and save to used_topics.txt
    if topics:
        remaining_topics = topics[1:]
        with open(TOPICS_FILE, "w", encoding="utf-8") as f:
            for t in remaining_topics:
                f.write(t + "\n")
        
        with open(USED_TOPICS_FILE, "a", encoding="utf-8") as f:
            f.write(selected_topic + "\n")
        print("Updated topics list successfully.")
else:
    print(f"Failed to post. Status code: {res.status_code}")
    print("Response:", res.text)
    exit(1)
