# EVOVO / EVOVOFinds

An independent, coffee-toned home for EVOVOFinds on eBay. A simple editorial site with style inspiration, saved ideas, clear seller links, and subtle mobile feedback.

## Shopping model

Real purchases happen at https://www.ebay.com/usr/evovofinds. The destination is defined as `EBAY_STORE_URL` in `catalog.js`.

- Prominent eBay links appear in the header, homepage, style notes, and help pages.
- `/checkout/` redirects to the eBay seller page, including without JavaScript.
- Style images are clearly labeled references, not seller inventory. No invented prices, stock, size availability, or checkout totals are displayed.
- There is no on-site cart, payment form, account, or order submission. Existing saved style ideas remain available on the same device.
- Shipping, condition, sizes, prices, returns, messages, payments, and orders are handled through the actual eBay listings.
- No ratings, testimonials, registration marks, or seller guarantees are fabricated.

## Interaction details

`interactions.js` adds a 7ms vibration on trusted intentional taps for browsers with the Vibration API and a coarse pointer. It never vibrates on page load or scrolling. Users can turn tap feedback off using the footer switch; the preference persists on their device. Reduced-motion preferences disable haptics and motion. Unsupported browsers, including iPhone Safari, use the small visual press effect without vibration.

The saved-ideas board supports search, category filtering, and name sorting. Search/sort/filter state stays in its URL. Copy board link shares the entire board as a snapshot of public style IDs; recipients see a separate board and must explicitly save ideas to merge them with their own. Unknown/duplicate IDs are ignored. Clipboard failure opens a manual-copy dialog. Unsave includes an undo action, and navigation badges reflect saved ideas across tabs.

Mobile has a safe-area-aware shortcut bar for style ideas, saved ideas, and eBay. It does not add an account gate or payment flow.

Press states, gentle image hover transitions, and one-time section reveals are progressive enhancements. Unsupported JavaScript or IntersectionObserver does not hide content. Fonts and images are served locally.

## Local development

Requires Node.js 20+ and Python 3 for the included preview command.

```sh
npm run dev
# http://localhost:3000
```

```sh
npm run check
npm run build
```

The build emits the homepage, category pages, seven style notes, saved ideas, about/help pages, the checkout redirect, and a 404 page into `dist/`. URLs load directly without a single-page-app rewrite.

## Browser checks

With Python Playwright and Chromium installed and the local preview running:

```sh
npm test
```

The tests cover honest content, categories/search/sorting, saved-idea persistence, mobile navigation, responsive overflow, the eBay handoff, progressive haptics and settings, and reduced-motion behavior. Set `EVOVO_BASE_URL` to test a deployed URL. Chromium is expected at `/usr/bin/chromium`.

## Hosting

Production: https://evovo.vercel.app

Vercel project: `evovo`, team: `turbo-twitch`, repository: `TurboTwitch0/TurboClothes`.

`vercel.json` uses `npm run build` and `dist/`. GitHub pushes to main trigger production builds. `.vercelignore` excludes local credentials and tooling. `netlify.toml` also supports the same static build. `.openai/hosting.json` preserves the earlier Sites identity; Vercel is the current hosting target.

## Content

`catalog.js` contains editorial ideas, not a live inventory feed. Source photographs are listed in `assets-manifest.json`; the EVOVOFinds avatar was generated for the brand in this conversation. The real clothing photos and product data can be added when provided by the owner. Saved ideas and tap-feedback preferences are local to the visitor's browser and can be cleared from the help page.

## The Personal Edit brand system

The homepage now presents the real save/filter/share workflow with a working three-idea example board, while keeping eBay as the shopping destination. Typography, rounded panels, coffee tones, empty/invalid-link states, and a graceful module-loading/error fallback share the same visual language. `boot.js` offers a user-triggered reload and eBay route if the app module cannot start; it never simulates success.

The original logo and artwork are preserved. Reusable brand exports and actual product screenshots are in `outputs/evovo-brand-kit/`. The local generator is `scripts/render-brand-kit.py`; it needs the supplied screenshots and local Chromium/Pillow/fontTools, and makes no paid API calls. No social content is published.

Published download page: https://evovo.vercel.app/brand-kit/

Complete ZIP: https://evovo.vercel.app/brand-kit/evovo-brand-kit.zip

Style-guide PDF: https://evovo.vercel.app/brand-kit/brand-sheet.pdf

Social preview art: `/brand-kit/launch-landscape.png` (1200×630) and `/brand-kit/launch-portrait.png` (1080×1350). These use actual product-screen captures and describe only delivered features. All exports remain within the existing authorized Vercel project; the private Sites audience is unchanged.
