# Endo Health Challenge — Workflow-Beschreibung

## Aufgabe

Automatische Generierung von 10 konsistenten Blog-Header-Bildern fuer endometriose.app — passend zur Brand Identity.

## Wie funktioniert der Workflow?

### AI-Chaining: Drei Stufen, ein konsistentes Ergebnis

```
endometriose.app/impulse/
        |
        |  1. Web Scraper (BeautifulSoup)
        v
10 deutsche Blog-Titel
        |
        |  2. Claude Haiku (Art Director)
        v
10 englische Szenen-Prompts
        |
        |  3. + Style-Prefix (Farben, Stil, Format)
        v
DALL-E 3 (Bildgenerierung)
        |
        v
10 konsistente Header-Bilder (1792x1024)
```

### Stufe 1: Blog-Titel scrapen

Das Script liest automatisch die aktuellen Blog-Titel von `endometriose.app/impulse/` per BeautifulSoup. Falls die Seite nicht erreichbar ist, greift ein Fallback mit 10 vordefinierten Titeln.

### Stufe 2: Claude als "Art Director"

Jeder deutsche Blog-Titel wird an Claude Haiku geschickt mit der Rolle eines visuellen Art Directors. Claude versteht den medizinischen Kontext und uebersetzt ihn in eine **metaphorische Szenenbeschreibung** auf Englisch (max. 25 Woerter).

Beispiel:
- **Input:** "Kuenstliche Wechseljahre — was steckt dahinter und was kannst du tun?"
- **Output:** "A woman tenderly nurturing wildflowers emerging through gentle fog, symbolizing transformation and reclaimed agency."

### Stufe 3: Konsistenz durch Style-Prefix

Der Trick fuer visuelle Konsistenz: Jeder DALL-E Prompt beginnt mit einem **identischen Style-Prefix** (~50 Woerter), der festlegt:

- **Stil:** Flat vector illustration, healthcare editorial
- **Farben:** Burgundy (#960f37) + Teal (#00B38F) + warm ivory background
- **Formen:** Rounded organic shapes, soft gradients
- **Stimmung:** Empowering, warm, minimalist
- **Einschraenkungen:** No text, no typography

Erst danach folgt Claudes individuelle Szenenbeschreibung. So entsteht eine **Serie**, keine Sammlung von Einzelbildern.

## Warum diese Architektur?

| Entscheidung | Begruendung |
|---|---|
| **Claude + DALL-E statt nur DALL-E** | Claude versteht den deutschen medizinischen Kontext und erzeugt einfuehlsame Metaphern. DALL-E allein wuerde zu generische Bilder erzeugen. |
| **Style-Prefix statt individuelle Prompts** | Garantiert visuelle Konsistenz ueber alle 10 Bilder hinweg. |
| **Haiku statt Sonnet/Opus** | Fuer kurze Szenenbeschreibungen reicht Haiku — schneller und guenstiger (~$0.002 fuer 10 Calls). |
| **Streamlit statt Next.js** | Schneller Prototyp, zero Frontend-Overhead, direkte Python-Integration. |
| **Fallback-Strategie** | Scraping oder APIs koennen fehlschlagen — das Script laeuft trotzdem weiter. |

## Brand Identity

| Rolle | Farbe | Hex |
|---|---|---|
| Primary | Weinrot/Burgund | `#960f37` |
| Secondary | Teal | `#00B38F` |
| Accent | Orange | `#ff7a00` |
| Background | Warm Ivory | `#FEFCF9` |

## Tech-Stack

- **Python 3.11+** — Hauptsprache
- **Claude Haiku** (Anthropic API) — Prompt-Generierung / Art Direction
- **DALL-E 3** (OpenAI API) — Bildgenerierung
- **BeautifulSoup** — Web Scraping
- **Streamlit** — Interaktive Web-UI
- **Streamlit Community Cloud** — Live-Hosting (Bonus)

## Kosten pro Durchlauf

| Service | Kosten |
|---|---|
| Claude Haiku (10 Calls) | ~$0.002 |
| DALL-E 3 Standard (10 Bilder) | ~$0.80 |
| **Gesamt** | **~$0.80** |

## Ergebnis

10 Header-Bilder im konsistenten Flat-Vector-Stil mit durchgehender Burgund/Teal-Farbpalette. Jedes Bild ist individuell auf den Blog-Inhalt zugeschnitten, wirkt aber als zusammengehoerende Serie.
