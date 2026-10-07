# IPTV Auto-Blogging Bot (WavePro TV)

Automated SEO blog writer powered by OpenAI and GitHub Actions.

## Setup Instructions:

1. Push all files in this repository to GitHub.
2. In GitHub, go to **Settings > Secrets and variables > Actions**.
3. Add the following Repository Secrets:
   - `WP_URL`: Your WordPress website URL (e.g. `https://waveprotv.com`)
   - `WP_USERNAME`: Your WordPress admin username (e.g. `sevone`)
   - `WP_APP_PASSWORD`: WordPress Application Password (from WP Admin > Users > Profile > Application Passwords)
   - `OPENAI_API_KEY`: Your OpenAI API key (`sk-...`)
4. Go to **Actions** tab in GitHub and click **Run workflow** to test it anytime!
