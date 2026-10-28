# EVOVO launch kit

Original local layouts for **The Personal Edit**. Promise: **Find your style. Keep your edit.**

## Files
- `brand-sheet.svg` / `.png` / `.pdf` — 1600 × 1100 visual identity and interface reference; PDF is a compact raster export.
- `launch-landscape.svg` / `.png` — 1200 × 630 launch artwork.
- `launch-portrait.svg` / `.png` — 1080 × 1350 portrait artwork.
- `wordmark-dark.svg` / `.png`, `wordmark-light.svg` / `.png` — transparent wordmarks; dark ink or cream.
- `icon.svg` / `.png` — exact existing favicon artwork.
- `evovofinds-avatar.png` — unchanged copy of the existing 1254 × 1254 avatar artwork.
- `product-desktop.png`, `product-mobile.png` — actual product screenshots captured from this repository’s running site.
- `launch-copy.md` — captions, calls to action, alt text, and accuracy notes.

## Color
| Role | Hex |
| --- | --- |
| Coffee ink | `#2b1d17` |
| Cream paper | `#f7f2ea` |
| Warm surface | `#eee5d9` |
| Caramel accent | `#d6ae86` |
| Border | `#ded1c3` |
| Muted copy | `#746253` |

Use coffee for body text and cream for dark backgrounds. Caramel is an accent; avoid small caramel text on cream. Keep reference photography natural.

## Typography and spacing
DM Sans 400–700 for navigation, labels, and body copy. Georgia for editorial headlines. Keep the current bold italic EVOVO wordmark; exported SVGs outline its glyphs for portable reproduction. The avatar is separate existing artwork, preserved exactly.

Use an 8px spacing rhythm. Maintain at least one capital-letter height of clear space around the wordmark. Keep the wordmark at least 100px wide in digital layouts. Preserve proportions and artwork colors; do not stretch, add effects, or redraw the avatar.

## Product truth
EVOVO browses clearly labeled style references, supports saved ideas, filters, and shareable boards. Purchasing takes place on EVOVOFinds eBay listings. No prices, stock, authentication, or fulfillment promises are invented in these assets. Nothing is published or sent by this kit.

## Re-render locally
Run `python3 scripts/render-brand-kit.py --prepare` to prepare logo/icon exports and copy. For the final composite artwork, first supply actual screenshots named `product-desktop.png` and `product-mobile.png` in this folder, then run `python3 scripts/render-brand-kit.py`.

The renderer uses local Pillow, fontTools, Playwright, and `/usr/bin/chromium`. Fonts and screenshot/avatar images are embedded in composite SVGs, so those SVG files have no external image or font dependencies. PNG output is rendered at exact canvas dimensions. No network calls, Canva credits, or image generation are used.

Embedded DM Sans font license is included in `licenses/DM-Sans-OFL.txt`. Reference-photo source URLs are recorded in `reference-image-sources.json`.
