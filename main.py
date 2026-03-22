"""
Endo Health Challenge — Blog Header Image Generator

AI-Chaining Pipeline:
  1. Scrape blog titles from endometriose.app
  2. Claude generates scene descriptions (prompt engineering)
  3. DALL-E 3 generates consistent header images

Author: Groth Automation
"""

import os
import re
import sys
import time
from pathlib import Path

# Fix Windows console encoding for emoji output
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import anthropic
import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).parent / "output"

STYLE_PREFIX = (
    "Flat vector illustration, healthcare editorial style, "
    "burgundy wine-red (#960f37) and teal (#00B38F) color palette "
    "with warm ivory background, rounded organic shapes, soft gradients, "
    "no text, no typography, no letters, no words, "
    "empowering and warm mood, minimalist composition, "
    "consistent visual identity across a blog series. Scene: "
)

ART_DIRECTOR_SYSTEM = """You are a visual art director for a German women's health app called endometriose.app.
Your job: Given a German blog post title, write ONE English sentence (max 25 words) describing a specific, symbolic visual scene for a blog header image.

Rules:
- English only
- No text, signs, or typography in the scene
- Use metaphors: journeys, growth, care, connection, cycles, warmth, nature
- Avoid medical gore, clinical imagery, or anatomical details
- Focus on emotions: empowerment, hope, support, self-care
- Output ONLY the scene description sentence, nothing else"""

FALLBACK_TITLES = [
    {"title": "Künstliche Wechseljahre — was steckt dahinter und was kannst du tun?", "slug": "kuenstliche-wechseljahre"},
    {"title": "Endometriose kennt kein Alter", "slug": "endometriose-kennt-kein-alter"},
    {"title": "Was brauche ich für meinen Reha-Aufenthalt", "slug": "was-brauche-ich-fuer-meinen-reha-aufenthalt"},
    {"title": "Anschlussheilbehandlung (AHB) und Reha bei Endometriose", "slug": "ahb-und-reha-bei-endometriose"},
    {"title": "Mit deiner Endotasche bist du auf alles vorbereitet", "slug": "mit-deiner-endotasche-vorbereitet"},
    {"title": "Endometriose und Psyche — warum beides zusammenhängt", "slug": "endometriose-und-psyche"},
    {"title": "Yoga und Entspannung bei Endometriose", "slug": "yoga-und-entspannung"},
    {"title": "Ernährung bei Endometriose — was dir gut tut", "slug": "ernaehrung-bei-endometriose"},
    {"title": "Schmerztagebuch führen — so trackst du deine Symptome", "slug": "schmerztagebuch-fuehren"},
    {"title": "Selbsthilfegruppen — gemeinsam stärker", "slug": "selbsthilfegruppen-gemeinsam-staerker"},
]

BLOG_URL = "https://endometriose.app/impulse/"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def slugify(title: str) -> str:
    """Convert a German title to a safe filename slug."""
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
    }
    slug = title.lower()
    for original, replacement in replacements.items():
        slug = slug.replace(original, replacement)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug[:80]


def scrape_blog_titles(url: str = BLOG_URL, count: int = 10) -> list[dict]:
    """Scrape blog titles from endometriose.app/impulse/. Falls back to hardcoded titles."""
    print(f"\n📡 Scraping blog titles from {url} ...")
    try:
        response = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; EndoHealthChallenge/1.0)"
        })
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        titles = []
        # Try common WordPress article title patterns
        for selector in ["article h2 a", "h2.entry-title a", ".post-title a", "h2 a"]:
            elements = soup.select(selector)
            if elements:
                for el in elements[:count]:
                    title = el.get_text(strip=True)
                    if title and len(title) > 5:
                        titles.append({"title": title, "slug": slugify(title)})
                break

        if len(titles) >= 5:
            print(f"   ✅ Found {len(titles)} titles via scraping")
            return titles[:count]
        else:
            print(f"   ⚠️  Only found {len(titles)} titles, using fallback")
            return FALLBACK_TITLES[:count]

    except Exception as e:
        print(f"   ⚠️  Scraping failed ({e}), using fallback titles")
        return FALLBACK_TITLES[:count]


def generate_image_prompt(title: str, claude_client: anthropic.Anthropic) -> str:
    """Use Claude to generate an English scene description for a blog title."""
    try:
        response = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            system=ART_DIRECTOR_SYSTEM,
            messages=[{"role": "user", "content": f"Blog-Titel: {title}"}],
        )
        scene = response.content[0].text.strip()
        return STYLE_PREFIX + scene
    except Exception as e:
        print(f"   ⚠️  Claude API error ({e}), using generic prompt")
        # Fallback: generic scene based on title keywords
        return STYLE_PREFIX + "A warm, supportive scene of personal growth and healing with gentle natural elements."


def generate_image(prompt: str, openai_client: openai.OpenAI, slug: str, quality: str = "standard") -> str | None:
    """Generate an image via DALL-E 3 and save it to output/."""
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",
            quality=quality,
            n=1,
        )
        image_url = response.data[0].url
        filepath = OUTPUT_DIR / f"{slug}.png"
        save_image(image_url, filepath)
        return str(filepath)
    except Exception as e:
        print(f"   ❌ DALL-E error for '{slug}': {e}")
        return None


def save_image(url: str, filepath: Path) -> None:
    """Download image from URL and save to disk."""
    response = requests.get(url, timeout=60, stream=True)
    response.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    size_kb = filepath.stat().st_size / 1024
    print(f"   💾 Saved: {filepath.name} ({size_kb:.0f} KB)")


def run_pipeline(
    titles: list[dict] | None = None,
    quality: str = "standard",
    claude_client: anthropic.Anthropic | None = None,
    openai_client: openai.OpenAI | None = None,
    progress_callback=None,
) -> list[dict]:
    """
    Run the full pipeline: titles → Claude prompts → DALL-E images.

    Returns list of dicts with title, slug, prompt, filepath, success.
    """
    if claude_client is None:
        claude_client = anthropic.Anthropic()
    if openai_client is None:
        openai_client = openai.OpenAI()
    if titles is None:
        titles = scrape_blog_titles()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    print(f"\n🎨 Generating {len(titles)} header images...\n")

    for i, entry in enumerate(tqdm(titles, desc="Generating images")):
        title = entry["title"]
        slug = entry["slug"]

        print(f"\n[{i+1}/{len(titles)}] {title}")

        # Step 1: Claude generates scene description
        print("   🤖 Generating prompt via Claude...")
        prompt = generate_image_prompt(title, claude_client)
        print(f"   📝 Prompt: ...{prompt[-80:]}")

        # Step 2: DALL-E generates image
        print("   🖼️  Generating image via DALL-E 3...")
        filepath = generate_image(prompt, openai_client, slug, quality)

        results.append({
            "title": title,
            "slug": slug,
            "prompt": prompt,
            "filepath": filepath,
            "success": filepath is not None,
        })

        if progress_callback:
            progress_callback(i + 1, len(titles))

        # Rate limit courtesy (skip after last image)
        if i < len(titles) - 1:
            time.sleep(2)

    # Summary
    success_count = sum(1 for r in results if r["success"])
    print(f"\n{'='*60}")
    print(f"✅ Generated {success_count}/{len(titles)} images successfully")
    print(f"📁 Output directory: {OUTPUT_DIR.resolve()}")
    print(f"{'='*60}\n")

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    load_dotenv()

    # Validate API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env")
        return
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return

    claude_client = anthropic.Anthropic()
    openai_client = openai.OpenAI()

    titles = scrape_blog_titles()

    print("\n📋 Blog titles to process:")
    for i, t in enumerate(titles, 1):
        print(f"   {i}. {t['title']}")

    run_pipeline(titles, claude_client=claude_client, openai_client=openai_client)


if __name__ == "__main__":
    main()
