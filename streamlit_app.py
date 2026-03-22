"""
Endo Health — Blog Header Image Generator (Streamlit UI)

Interactive UI for generating brand-consistent blog header images
for endometriose.app using AI chaining (Claude + DALL-E 3).
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from main import (
    FALLBACK_TITLES,
    OUTPUT_DIR,
    STYLE_PREFIX,
    generate_image,
    generate_image_prompt,
    scrape_blog_titles,
    slugify,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Endo Health — Header Generator",
    page_icon="🌸",
    layout="wide",
)

# Brand colors
BURGUNDY = "#960f37"
TEAL = "#00B38F"

st.markdown(f"""
<style>
    .stApp {{ }}
    h1 {{ color: {BURGUNDY}; }}
    .brand-box {{
        display: inline-block;
        width: 40px; height: 40px;
        border-radius: 8px;
        margin-right: 8px;
        vertical-align: middle;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Einstellungen")

    openai_key = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
    )
    anthropic_key = st.text_input(
        "Anthropic API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
    )

    quality = st.radio("Bildqualität", ["standard", "hd"], index=0)

    st.divider()
    st.subheader("🎨 Brand Identity")
    st.markdown(f"""
    <span class="brand-box" style="background:{BURGUNDY};"></span> Primary: `{BURGUNDY}`<br>
    <span class="brand-box" style="background:{TEAL};"></span> Secondary: `{TEAL}`<br>
    <span class="brand-box" style="background:#ff7a00;"></span> Accent: `#ff7a00`
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("💡 Style-Prefix (wird jedem DALL-E Prompt vorangestellt):")
    st.code(STYLE_PREFIX, language=None)

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.title("🌸 Endo Health — Blog Header Generator")
st.markdown("Generiere konsistente Header-Bilder für Blog-Posts von **endometriose.app** mit AI-Chaining.")

# Tab layout
tab_scrape, tab_custom = st.tabs(["📡 Blog-Titel scrapen", "✏️ Eigene Titel eingeben"])

with tab_scrape:
    if st.button("Titel von endometriose.app laden", type="primary"):
        with st.spinner("Scraping..."):
            titles = scrape_blog_titles()
        st.session_state["titles"] = titles
        st.success(f"{len(titles)} Titel geladen!")

    if st.button("Fallback-Titel verwenden"):
        st.session_state["titles"] = FALLBACK_TITLES.copy()
        st.success("10 Fallback-Titel geladen!")

with tab_custom:
    custom_input = st.text_area(
        "Blog-Titel (einer pro Zeile)",
        height=250,
        placeholder="Künstliche Wechseljahre — was steckt dahinter?\nEndometriose kennt kein Alter\n...",
    )
    if st.button("Eigene Titel übernehmen"):
        lines = [l.strip() for l in custom_input.strip().split("\n") if l.strip()]
        if lines:
            st.session_state["titles"] = [
                {"title": t, "slug": slugify(t)} for t in lines
            ]
            st.success(f"{len(lines)} Titel übernommen!")
        else:
            st.warning("Bitte mindestens einen Titel eingeben.")

# ---------------------------------------------------------------------------
# Show & edit titles
# ---------------------------------------------------------------------------

if "titles" in st.session_state and st.session_state["titles"]:
    st.subheader("📋 Aktuelle Titel")
    titles = st.session_state["titles"]

    for i, t in enumerate(titles):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text(f"{i+1}. {t['title']}")
        with col2:
            st.caption(f"`{t['slug'][:30]}...`")

    st.divider()

    # Generate button
    if st.button("🎨 Header-Bilder generieren", type="primary", use_container_width=True):
        if not openai_key or not anthropic_key:
            st.error("Bitte beide API Keys in der Sidebar eingeben.")
        else:
            import anthropic
            import openai as openai_module

            claude_client = anthropic.Anthropic(api_key=anthropic_key)
            oai_client = openai_module.OpenAI(api_key=openai_key)

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []

            for i, entry in enumerate(titles):
                status_text.text(f"🤖 [{i+1}/{len(titles)}] {entry['title']}")

                prompt = generate_image_prompt(entry["title"], claude_client)
                filepath = generate_image(prompt, oai_client, entry["slug"], quality)

                results.append({
                    "title": entry["title"],
                    "slug": entry["slug"],
                    "prompt": prompt,
                    "filepath": filepath,
                    "success": filepath is not None,
                })

                progress_bar.progress((i + 1) / len(titles))

            st.session_state["results"] = results
            success_count = sum(1 for r in results if r["success"])
            status_text.empty()
            st.success(f"✅ {success_count}/{len(titles)} Bilder erfolgreich generiert!")

# ---------------------------------------------------------------------------
# Results gallery
# ---------------------------------------------------------------------------

if "results" in st.session_state and st.session_state["results"]:
    st.subheader("🖼️ Generierte Header-Bilder")

    results = st.session_state["results"]
    cols = st.columns(2)

    for i, result in enumerate(results):
        with cols[i % 2]:
            st.markdown(f"**{result['title']}**")
            if result["success"] and result["filepath"]:
                filepath = Path(result["filepath"])
                if filepath.exists():
                    st.image(str(filepath), use_container_width=True)

                    with open(filepath, "rb") as f:
                        st.download_button(
                            f"⬇️ Download {filepath.name}",
                            data=f.read(),
                            file_name=filepath.name,
                            mime="image/png",
                            key=f"dl_{i}",
                        )
            else:
                st.error("Bildgenerierung fehlgeschlagen")

            with st.expander("Prompt anzeigen"):
                st.code(result["prompt"], language=None)

            st.divider()
