#!/usr/bin/env python3
"""Render the EVOVO launch kit locally. No network or paid generation services.

Use --prepare to create logo/icon exports and docs before the frontend screenshots exist.
A full run requires outputs/evovo-brand-kit/product-desktop.png and product-mobile.png.
"""
from pathlib import Path
import argparse, base64, hashlib, html, json, shutil
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'evovo-brand-kit'
OUT.mkdir(parents=True, exist_ok=True)
INK, PAPER, SURFACE, ACCENT, LINE, MUTED = '#2b1d17', '#f7f2ea', '#eee5d9', '#d6ae86', '#ded1c3', '#746253'
FONTPATH = ROOT / 'assets/fonts/dm-sans-400-700.woff2'
FONTDATA = base64.b64encode(FONTPATH.read_bytes()).decode()
STYLE = f'''<style>@font-face{{font-family:DM;src:url(data:font/woff2;base64,{FONTDATA}) format('woff2');font-weight:400 700}}text{{font-family:DM,Arial,sans-serif;fill:{INK}}}.serif{{font-family:Georgia,'Times New Roman',serif}}.small{{font-size:12px;letter-spacing:2px;font-weight:600}}.muted{{fill:{MUTED}}}</style>'''

# The site uses italic 900 Arial with letter-spacing:-3px at 36px. Chromium's
# metrically compatible Arial fallback is Liberation Sans Bold Italic. Outline
# the matching glyphs so the exported wordmark is portable and never substituted.
FONT = TTFont('/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf')
GLYPHS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
UPM = FONT['head'].unitsPerEm
KERN = {}
if 'kern' in FONT:
    for table in FONT['kern'].kernTables:
        KERN.update(table.kernTable)

def outlined_wordmark():
    size, baseline, x = 200, 182, 26
    scale = size / UPM
    pieces, previous = [], None
    for char in 'EVOVO':
        name = CMAP[ord(char)]
        if previous:
            x += KERN.get((previous, name), 0) * scale
        pen = SVGPathPen(GLYPHS)
        GLYPHS[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
        pieces.append(pen.getCommands())
        x += FONT['hmtx'].metrics[name][0] * scale - size / 12
        previous = name
    return ''.join(pieces), x + 30

WORDPATH, WORDW = outlined_wordmark()

def wordmark(x, y, width, color=INK):
    return f'<g transform="translate({x} {y}) scale({width/WORDW})"><path d="{WORDPATH}" fill="{color}"/></g>'

def text(x, y, value, size=18, color=INK, cls='', weight=None, spacing=None):
    attributes = ''
    if weight is not None: attributes += f' font-weight="{weight}"'
    if spacing is not None: attributes += f' letter-spacing="{spacing}"'
    return f'<text x="{x}" y="{y}" font-size="{size}" style="fill:{color}" class="{cls}"{attributes}>{html.escape(value)}</text>'

def rect(x, y, w, h, fill, radius=0, stroke=None):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>'

def rule(x1,y1,x2,y2):return f'<path d="M{x1} {y1}H{x2}" stroke="{LINE}"/>'

def image_data(path):
    mime='image/png' if Path(path).suffix=='.png' else 'image/jpeg'
    return f'data:{mime};base64,'+base64.b64encode(Path(path).read_bytes()).decode()

def picture(path,x,y,w,h,mode='xMidYMid slice',radius=0,id='img'):
    clip=f'<defs><clipPath id="{id}">{rect(x,y,w,h,"white",radius)}</clipPath></defs>' if radius else ''
    return clip+f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{image_data(path)}" preserveAspectRatio="{mode}"'+(f' clip-path="url(#{id})"' if radius else '')+'/>'

def svg(w,h,body,bg=None,title='EVOVO'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title>{STYLE}'+(rect(0,0,w,h,bg) if bg else '')+''.join(body)+'</svg>'

def write_svg(name,source):
    (OUT/name).write_text(source)

AVATAR = ROOT/'assets/evovofinds-avatar.png'
DESKTOP = OUT/'product-desktop.png'
MOBILE = OUT/'product-mobile.png'

def prepare():
    shutil.copyfile(AVATAR,OUT/'evovofinds-avatar.png')
    shutil.copyfile(ROOT/'assets/favicon.svg',OUT/'icon.svg')
    write_svg('wordmark-dark.svg', svg(800,270,[wordmark(20,0,760,INK)],title='EVOVO dark wordmark'))
    write_svg('wordmark-light.svg', svg(800,270,[wordmark(20,0,760,PAPER)],title='EVOVO light wordmark'))
    (OUT/'launch-copy.md').write_text('''# EVOVO — The Personal Edit

## Headline
Find your style. Keep your edit.

## Short launch caption
Meet EVOVO: a personal space for your next style idea. Browse clearly labeled references, filter your favorites, and build a board worth keeping. Save your edit, then share it.

Style inspiration on EVOVO. Purchases on eBay through EVOVOFinds.

## Short caption
Your style, your edit. Browse ideas. Save a board. Share your point of view.

Style inspiration on EVOVO. Purchases on eBay.

## Calls to action
- Explore the edit
- Save your favorites
- Share your board
- Shop EVOVOFinds on eBay

## Profile description
Style ideas to make your own. Save and share your personal edit. Shop current EVOVOFinds listings on eBay.

## Alt text
- Launch landscape: EVOVO's cream-and-coffee identity, the words “Find your style. Keep your edit.”, and a screenshot of its style inspiration website.
- Portrait promo: EVOVO, The Personal Edit, with the original EVOVOFinds avatar and real mobile website preview. Purchases take place on eBay.

## Publishing note
These are prepared launch assets and copy. Nothing has been posted. Style reference images do not assert product availability; listing details, prices, payments, delivery, and orders belong to eBay. Do not add stock counts, customer totals, review scores, or delivery promises without verified information.
''')
    (OUT/'README.md').write_text('''# EVOVO launch kit

Original local layouts for **The Personal Edit**. Promise: **Find your style. Keep your edit.**

## Files
- `brand-sheet.svg` / `.png` / `.pdf` — 1600 × 1100 visual identity and interface reference; PDF is a compact raster export.
- `launch-landscape.svg` / `.png` — 1200 × 630 launch artwork.
- `launch-portrait.svg` / `.png` — 1080 × 1350 portrait artwork.
- `wordmark-dark.svg` / `.png`, `wordmark-light.svg` / `.png` — transparent wordmarks; dark ink or cream.
- `icon.svg` / `.png` — exact existing favicon artwork.
- `evovofinds-avatar.png` — unchanged copy of the existing 1254 × 1254 avatar artwork.
- `product-desktop.png`, `product-mobile.png` — actual website screenshots supplied by the site owner.
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
''')

def brand_sheet():
    b=[text(64,54,'EVOVO / VISUAL IDENTITY',13,cls='small'),text(1250,54,'THE PERSONAL EDIT',12,cls='small'),rule(64,78,1536,78),text(64,124,'01 / THE IDEA',11,MUTED,cls='small'),text(64,206,'Find your style.',70,cls='serif'),text(64,285,'Keep your edit.',70,cls='serif'),text(67,337,'A personal space for your next style idea.',21,MUTED),text(67,378,'Browse references. Save favorites. Share your board.',17,MUTED),rect(939,109,597,310,INK,20),picture(AVATAR,1286,134,214,214,radius=14,id='avatar'),wordmark(969,157,288,PAPER),text(976,317,'THE PERSONAL EDIT',12,ACCENT,cls='small'),text(976,357,'The home of EVOVOFinds.',17,PAPER),text(64,468,'02 / COLOR & TYPE',11,MUTED,cls='small')]
    names=[('COFFEE',INK),('CREAM',PAPER),('SURFACE',SURFACE),('CARAMEL',ACCENT),('BORDER',LINE),('MUTED',MUTED)]
    for i,(name,color) in enumerate(names):
        x=64+i*178;b.extend([rect(x,493,160,65,color,8,LINE if color==PAPER else None),text(x,581,name,10,MUTED,weight=600,spacing=1.1),text(x,605,color.upper(),13)])
    b.extend([text(1180,518,'Georgia',34,cls='serif'),text(1180,549,'Editorial headlines',12,MUTED),text(1180,586,'DM Sans',25),text(1180,611,'Interface & everyday language',12,MUTED),rule(64,640,1536,640),text(64,684,'03 / THE EXPERIENCE',11,MUTED,cls='small'),rect(64,710,450,308,SURFACE,12),picture(DESKTOP,74,720,430,288,mode='xMinYMin meet',radius=6,id='desktop'),text(555,762,'Build a point of view.',35,cls='serif'),text(558,811,'Browse clearly labeled style references.',18,MUTED),text(558,851,'Filter ideas into your own edit.',18,MUTED),text(558,891,'Save favorites and share a board.',18,MUTED),text(558,965,'Purchases on EVOVOFinds eBay listings.',16,MUTED),rect(1221,705,134,325,INK,20),picture(MOBILE,1227,713,122,309,mode='xMinYMin meet',radius=14,id='mobile'),text(1380,750,'Browse.',17),text(1380,779,'Save.',17),text(1380,808,'Share.',17),text(64,1060,'Style inspiration on EVOVO. Purchases on eBay.',16,MUTED),text(1184,1060,'8PX RHYTHM / ORIGINAL ART',10,MUTED,cls='small')])
    return svg(1600,1100,b,PAPER,'EVOVO brand sheet — The Personal Edit')

def landscape():
    b=[wordmark(52,33,185),text(54,141,'THE PERSONAL EDIT',12,MUTED,cls='small'),text(52,230,'Find your style.',57,cls='serif'),text(52,294,'Keep your edit.',57,cls='serif'),text(55,349,'Browse references. Save favorites.',17,MUTED),text(55,378,'Share a board that feels like you.',17,MUTED),rect(54,416,222,52,INK,5),text(77,449,'EXPLORE THE EDIT',12,PAPER,weight=600,spacing=1.1),text(54,564,'Style inspiration on EVOVO.',14,MUTED),text(54,589,'Purchases on eBay.',14,MUTED),rect(578,30,590,570,SURFACE,24),rect(602,70,542,371,PAPER,11),picture(DESKTOP,610,78,526,355,mode='xMinYMin slice',radius=6,id='desktop'),picture(AVATAR,618,466,101,101,radius=12,id='avatar'),text(744,497,'EVOVOFinds',22),text(744,528,'Your next find, on eBay.',16,MUTED),text(744,558,'THE HOME OF EVOVOFINDS',10,MUTED,cls='small')]
    return svg(1200,630,b,PAPER,'EVOVO launch — Find your style. Keep your edit.')

def portrait():
    b=[rect(0,0,1080,570,INK),wordmark(66,52,253,PAPER),text(67,205,'THE PERSONAL EDIT',15,ACCENT,cls='small'),text(64,306,'Find your style.',83,PAPER,cls='serif'),text(64,401,'Keep your edit.',83,PAPER,cls='serif'),text(68,473,'Browse references. Save favorites. Share your board.',21,PAPER),rect(64,612,953,525,SURFACE,18),rect(95,644,584,403,PAPER,11),picture(DESKTOP,105,654,564,383,mode='xMinYMin slice',radius=7,id='desktop'),rect(746,641,186,454,INK,24),picture(MOBILE,753,650,172,436,mode='xMinYMin meet',radius=18,id='mobile'),text(99,1092,'YOUR STYLE. YOUR POINT OF VIEW.',12,MUTED,cls='small'),picture(AVATAR,67,1195,93,93,radius=12,id='avatar'),text(186,1226,'Style inspiration on EVOVO.',23),text(186,1262,'Purchases on eBay.',23,MUTED),text(813,1297,'EVOVOFINDS',11,MUTED,cls='small')]
    return svg(1080,1350,b,PAPER,'EVOVO portrait launch — The Personal Edit')

def render_pngs(names):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page=browser.new_page(device_scale_factor=1)
        for name in names:
            path=OUT/name
            import re
            dimensions=re.search(r'<svg[^>]+width="(\d+)" height="(\d+)"',path.read_text())
            w,h=map(int,dimensions.groups()) if dimensions else (512,512)
            page.set_viewport_size({'width':w,'height':h})
            page.set_content('<!doctype html><html><head><style>html,body{margin:0;background:transparent}svg{display:block}</style></head><body>'+path.read_text()+'</body></html>')
            page.add_style_tag(content=f'body>svg{{width:{w}px;height:{h}px}}')
            page.evaluate('document.fonts.ready')
            page.screenshot(path=str(path.with_suffix('.png')),omit_background=True)
            im=Image.open(path.with_suffix('.png'));assert im.size==(w,h)
        browser.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');args=parser.parse_args()
    prepare()
    names=['wordmark-dark.svg','wordmark-light.svg','icon.svg']
    if not args.prepare:
        if not DESKTOP.exists() or not MOBILE.exists():raise SystemExit('Waiting for actual product-desktop.png and product-mobile.png screenshots; no fabricated mockups rendered.')
        write_svg('brand-sheet.svg',brand_sheet());write_svg('launch-landscape.svg',landscape());write_svg('launch-portrait.svg',portrait())
        names+=['brand-sheet.svg','launch-landscape.svg','launch-portrait.svg']
    render_pngs(names)
    if not args.prepare:
        Image.open(OUT/'brand-sheet.png').convert('RGB').save(OUT/'brand-sheet.pdf', 'PDF', resolution=120.0, quality=90, title='EVOVO — The Personal Edit', author='EVOVO', subject='Visual identity and actual website interface')
    assert hashlib.sha256(AVATAR.read_bytes()).digest()==hashlib.sha256((OUT/'evovofinds-avatar.png').read_bytes()).digest()
    print(json.dumps({'output':str(OUT),'rendered':names,'avatar':'unchanged, SHA-256 verified'},indent=2))
