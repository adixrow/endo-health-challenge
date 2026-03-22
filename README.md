# Endo Health Challenge — Blog Header Image Generator

Automatische Generierung konsistenter Header-Bilder für Blog-Posts von [endometriose.app](https://endometriose.app) — mit AI-Chaining.

## Architektur

```
endometriose.app/impulse/
        │
        │  BeautifulSoup Scraper
        ▼
10 deutsche Blog-Titel
        │
        │  Claude Haiku (Art Director)
        ▼
10 englische Szenenbeschreibungen
        │
        │  + Style-Prefix (Farben, Stil, Format)
        ▼
DALL-E 3 (Bildgenerierung)
        │
        ▼
10 konsistente Header-Bilder (1792×1024)
```

### Warum AI-Chaining?

**Claude** versteht den deutschen medizinischen Kontext und übersetzt Blog-Titel in visuell konkrete Szenen. **DALL-E 3** rendert diese mit einem festen Style-Prefix, der Farbpalette, Illustrationsstil und Stimmung vorgibt. Das Ergebnis: 10 Bilder, die zusammengehören.

## Brand Identity

| Rolle | Farbe | Hex |
|-------|-------|-----|
| Primary | 🟥 Weinrot/Burgund | `#960f37` |
| Secondary | 🟩 Teal | `#00B38F` |
| Accent | 🟧 Orange | `#ff7a00` |

## Setup

### 1. Voraussetzungen

- Python 3.11+
- OpenAI API Key (für DALL-E 3)
- Anthropic API Key (für Claude)

### 2. Installation

```bash
cd endo-health-challenge
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. API Keys konfigurieren

```bash
cp .env .env  # Datei existiert bereits
# Trage deine Keys ein:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

## Verwendung

### CLI (10 Bilder generieren)

```bash
python main.py
```

### Streamlit UI (interaktiv)

```bash
streamlit run streamlit_app.py
```

Die Streamlit-App bietet:
- Blog-Titel scrapen oder eigene eingeben
- Bildqualität wählen (standard/hd)
- Live-Fortschrittsanzeige
- Bildergalerie mit Download-Buttons
- Prompt-Anzeige pro Bild

## Projektstruktur

```
endo-health-challenge/
├── main.py              # Core Pipeline (Scraper + Claude + DALL-E)
├── streamlit_app.py     # Interaktive Web-UI
├── requirements.txt     # Python-Abhängigkeiten
├── .env                 # API Keys (nicht im Git)
├── .gitignore
└── output/              # Generierte Bilder
```

## Kosten

| Service | Kosten pro Run |
|---------|---------------|
| Claude Haiku (10 Calls) | ~$0.002 |
| DALL-E 3 Standard (10 Bilder) | ~$0.80 |
| **Gesamt** | **~$0.80** |

Mit `quality="hd"`: ~$1.20 pro Run.

## Design-Entscheidungen

1. **Style-Prefix statt individuelle Prompts** — Jedes DALL-E Prompt beginnt mit identischen 50+ Wörtern (Farbpalette, Illustrationsstil, Stimmung). Das garantiert visuelle Konsistenz.

2. **Claude als "Art Director"** — Statt simple Keyword-Extraktion versteht Claude den Kontext von Endometriose-Themen und erzeugt metaphorische, einfühlsame Szenenbeschreibungen.

3. **Fallback-Strategie** — Wenn Scraping oder APIs fehlschlagen, läuft das Script trotzdem weiter mit Fallback-Daten. Robust by design.

4. **Streamlit statt Next.js** — Schneller Prototyp, zero Frontend-Overhead, direkte Python-Integration ohne API-Layer.
