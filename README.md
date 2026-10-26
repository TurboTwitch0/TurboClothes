# EVOVO

A complete responsive men's streetwear storefront, rebuilt from the original Turbo Clothes draft. Original EVOVO branding with a bold athletic editorial direction.

## What's included

- Homepage with local editorial imagery, category collections, featured pieces, brand story, and full footer.
- Dedicated Shirts, Hoodies, Pants, Socks, and all-products pages.
- Seven product detail pages with sizes, size guide, product information, and related pieces.
- Product search, price/name sorting, saved pieces, and empty states.
- Persistent shopping bag with quantity controls, removal, totals, and a checkout link to EVOVOFinds on eBay.
- Brand story, store information, sizing, privacy, shipping/returns status, and 404 page.
- Responsive mobile navigation, accessible native dialogs, keyboard controls, and reduced-motion support.
- Static builds for Vercel, Netlify, and Sites. No runtime dependencies or environment variables required for the preview.

## Run

Node.js 20+ and Python 3 are required for the supplied local preview command.

```sh
npm run dev
# http://localhost:3000
```

```sh
npm run check
npm run build
```

The build emits 17 HTML pages plus a 404 page into `dist/`. Every product/category URL works when loaded directly; no SPA rewrite is needed.

## Verification

The integration test requires Python Playwright and Chromium. With the local preview running:

```sh
npm test
```

`tests/storefront.py` tests desktop/mobile navigation, search, sorting, product sizing, cart quantity/totals/removal, reload persistence, saved items, empty states, the eBay checkout handoff, and the 404 page. Chromium is expected at `/usr/bin/chromium` unless the test configuration is adapted.

## Hosting

**Vercel:** Import `TurboTwitch0/TurboClothes`. Included `vercel.json` uses `npm run build` and `dist`.

**Netlify:** Import the same repository. Included `netlify.toml` sets the build and publish directory.

**Sites:** `.openai/hosting.json` retains the existing Site identity. Publishing requires the corresponding Sites source repository to contain the exact reviewed commit.

**Squarespace:** This is a standalone static storefront. Squarespace doesn't directly import a GitHub static site as a native Commerce store. Moving to Squarespace requires a connected Squarespace account, its real product catalog, and a Squarespace-native implementation or external link. This repository does not claim a Squarespace connection.

## Purchasing through eBay

The checkout button opens https://www.ebay.com/usr/evovofinds in the same tab. The existing `/checkout/` route also redirects there, including with JavaScript disabled. The destination is defined once as `EBAY_STORE_URL` in `catalog.js`.

This is a seller-page handoff, not a direct eBay cart integration. The EVOVO bag stays on this device and is not transferred. Customers select and purchase the real items from current eBay listings. Availability, final prices, shipping, taxes, returns, and payments are handled on eBay. This site does not collect payment details or submit orders.

The on-site product photography and prices remain illustrative until the owner supplies the final catalog.

See `catalog.js` for sample product data and `assets-manifest.json` for source-image references. Stock imagery is illustrative and is not represented as the merchant's actual clothing. Bags and saved items are stored only on the visitor's device. No newsletter, account, or contact form pretends to submit data.
