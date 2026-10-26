"""Behavioral checks for the EVOVO eBay showroom and progressive touch feedback.
Run the built site on port 3000, or set EVOVO_BASE_URL to a deployed site.
Requires Python Playwright and Chromium at /usr/bin/chromium.
"""
import os
import re
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get('EVOVO_BASE_URL', 'http://localhost:3000').rstrip('/')
EBAY = 'https://www.ebay.com/usr/evovofinds'
MOCK_VIBRATION = """
window.__vibrations = [];
Object.defineProperty(navigator, 'vibrate', {
  configurable: true,
  value: function(duration) { window.__vibrations.push(duration); return true; }
});
"""


def intercept_ebay(context):
    # Verify the destination and navigation without relying on eBay's bot checks.
    context.route('https://www.ebay.com/**', lambda route: route.fulfill(
        status=200, content_type='text/html', body='<h1>External navigation intercepted</h1>'))


def assert_fits(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (
        page.viewport_size, page.url, page.evaluate('document.documentElement.scrollWidth'))


def reveal_and_capture(page, path):
    for section in page.locator('[data-reveal]').all():
        section.scroll_into_view_if_needed()
        expect(section).to_have_class(re.compile(r'\bis-visible\b'))
    for image in page.locator('main img').all():
        image.scroll_into_view_if_needed()
        expect(image).to_have_js_property('complete', True)
        assert image.evaluate('(image) => image.naturalWidth > 0')
    page.evaluate('scrollTo(0, 0)')
    page.screenshot(path=path, full_page=True, animations='disabled')


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'], headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    intercept_ebay(context)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))

    page.goto(BASE + '/', wait_until='networkidle')
    expect(page.locator('h1')).to_contain_text('Your next find.')
    assert page.title().startswith('EVOVO')
    assert page.locator('main .category-card').count() == 4
    assert page.locator('main .product-card').count() == 4
    assert page.locator('#cart-open, #detail-add, .size-options').count() == 0
    assert '$' not in page.locator('main').inner_text()
    assert '®' not in page.locator('body').inner_text()
    expect(page.locator('.hero-actions .pill')).to_have_attribute('href', EBAY)
    expect(page.locator('footer')).to_contain_text('images on this site are style references')
    assert_fits(page)
    reveal_and_capture(page, '/workspace/evovo-credible-desktop.png')

    # Search is useful, and native dialogs restore keyboard focus on Escape.
    page.get_by_role('button', name='Search style ideas', exact=True).click()
    expect(page.locator('#search-dialog')).to_be_visible()
    page.get_by_role('searchbox', name='Search style ideas', exact=True).fill('hoodie')
    expect(page.locator('#search-results .search-result')).not_to_have_count(0)
    # A filled search input uses the first Escape to clear its query.
    page.keyboard.press('Escape')
    if page.locator('#search-dialog').is_visible():
        page.keyboard.press('Escape')
    expect(page.locator('#search-dialog')).not_to_be_visible()
    expect(page.locator('#search-open')).to_be_focused()

    for category in ['Shirts', 'Hoodies', 'Pants', 'Socks']:
        page.goto(BASE + '/shop/' + category.lower() + '/', wait_until='networkidle')
        expect(page.locator('.catalog-head h1')).to_contain_text(category)
        assert page.locator('#collection-grid .product-card').count() >= 1
        expect(page.locator('.catalog-head')).to_contain_text('not items listed for sale')
    page.goto(BASE + '/shop/', wait_until='networkidle')
    count = page.locator('#collection-grid .product-card').count()
    assert count == 7
    page.get_by_role('combobox', name='Sort style ideas').select_option('name')
    names = page.locator('.product-info a').all_text_contents()
    assert names == sorted(names, key=str.casefold), names
    page.get_by_role('searchbox', name='Search style ideas', exact=True).fill('zzzz-no-match')
    expect(page.locator('#collection-grid .product-card')).to_have_count(0)
    page.get_by_role('searchbox', name='Search style ideas', exact=True).fill('')
    expect(page.locator('#collection-grid .product-card')).to_have_count(count)

    # Style details do not pretend to be purchasable inventory.
    page.goto(BASE + '/products/core-tee/', wait_until='networkidle')
    expect(page.locator('h1')).to_have_text('The everyday white tee')
    expect(page.locator('.reference-box')).to_contain_text("doesn't represent an item available")
    assert page.locator('#detail-add, .size-options, .detail-price').count() == 0
    expect(page.get_by_role('link', name='Browse EVOVOFinds on eBay')).to_have_attribute('href', EBAY)
    page.locator('.detail-save').click()
    expect(page.locator('.detail-save')).to_have_attribute('aria-pressed', 'true')
    page.reload(wait_until='networkidle')
    expect(page.locator('.detail-save')).to_have_attribute('aria-pressed', 'true')
    page.goto(BASE + '/saved/', wait_until='networkidle')
    expect(page.locator('#collection-grid .product-card')).to_have_count(1)
    page.locator('.save-button').click()
    expect(page.locator('#collection-grid .product-card')).to_have_count(0)

    # Preferences can be cleared from the user-facing control.
    page.evaluate("localStorage.setItem('evovo.saved', JSON.stringify(['core-tee'])); localStorage.setItem('evovo.bag', '[]'); localStorage.setItem('evovo.haptics', 'off')")
    page.goto(BASE + '/help/', wait_until='networkidle')
    page.get_by_role('button', name='Clear saved ideas & preferences', exact=True).click()
    assert page.evaluate("JSON.parse(localStorage.getItem('evovo.saved'))") == []
    assert page.evaluate("localStorage.getItem('evovo.bag')") is None
    assert page.evaluate("localStorage.getItem('evovo.haptics')") is None

    # Real eBay handoff remains available from both links and old checkout URLs.
    page.get_by_role('link', name='Checkout on eBay', exact=True).first.click()
    expect(page).to_have_url(EBAY)
    page.goto(BASE + '/checkout/')
    expect(page).to_have_url(EBAY)
    no_js = browser.new_context(java_script_enabled=False)
    intercept_ebay(no_js)
    no_js_page = no_js.new_page()
    no_js_page.goto(BASE + '/checkout/')
    expect(no_js_page).to_have_url(EBAY)
    no_js.close()

    page.goto(BASE + '/404.html', wait_until='networkidle')
    expect(page.locator('h1')).to_contain_text('A different direction.')

    # Responsive navigation and typography at small-phone through desktop widths.
    for width in [320, 390, 768, 1440]:
        page.set_viewport_size({'width': width, 'height': 900})
        for route in ['/', '/shop/', '/products/core-tee/', '/help/']:
            page.goto(BASE + route, wait_until='networkidle')
            assert_fits(page)
    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto(BASE + '/', wait_until='networkidle')
    page.get_by_role('button', name='Open navigation', exact=True).click()
    expect(page.locator('#menu-dialog')).to_be_visible()
    page.locator('#menu-dialog').get_by_role('link', name='Hoodies', exact=True).click()
    expect(page.locator('h1')).to_contain_text('Hoodies')
    page.goto(BASE + '/', wait_until='networkidle')
    reveal_and_capture(page, '/workspace/evovo-credible-mobile.png')
    assert not errors, errors
    context.close()

    # Haptics are a small enhancement: mobile intent only, never on load/scroll.
    touch = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    touch.add_init_script(MOCK_VIBRATION)
    touch_page = touch.new_page()
    touch_page.goto(BASE + '/', wait_until='networkidle')
    assert touch_page.evaluate('window.__vibrations') == []
    touch_page.locator('footer').scroll_into_view_if_needed()
    assert touch_page.evaluate('window.__vibrations') == []
    expect(touch_page.locator('[data-haptics-toggle]')).to_be_visible()
    expect(touch_page.locator('[data-haptics-toggle]')).to_have_attribute('aria-pressed', 'true')
    touch_page.locator('#search-open').tap()
    assert touch_page.evaluate('window.__vibrations') == [7]
    touch_page.keyboard.press('Escape')
    touch_page.locator('[data-haptics-toggle]').tap()
    expect(touch_page.locator('[data-haptics-toggle]')).to_have_attribute('aria-pressed', 'false')
    before = touch_page.evaluate('window.__vibrations.length')
    touch_page.locator('#search-open').tap()
    assert touch_page.evaluate('window.__vibrations.length') == before
    touch_page.keyboard.press('Escape')
    touch_page.reload(wait_until='networkidle')
    expect(touch_page.locator('[data-haptics-toggle]')).to_have_attribute('aria-pressed', 'false')
    touch_page.locator('#search-open').tap()
    assert touch_page.evaluate('window.__vibrations') == []
    touch_page.keyboard.press('Escape')
    touch_page.goto(BASE + '/help/', wait_until='networkidle')
    touch_page.locator('#clear-data').tap()
    expect(touch_page.locator('[data-haptics-toggle]')).to_have_attribute('aria-pressed', 'true')
    touch.close()

    reduced = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, reduced_motion='reduce')
    reduced.add_init_script(MOCK_VIBRATION)
    reduced_page = reduced.new_page()
    reduced_page.goto(BASE + '/', wait_until='networkidle')
    expect(reduced_page.locator('[data-haptics-toggle]')).to_be_disabled()
    reduced_page.locator('#search-open').tap()
    assert reduced_page.evaluate('window.__vibrations') == []
    assert not reduced_page.locator('html').evaluate('(el) => el.classList.contains("motion-ready")')
    reduced.close()

    desktop = browser.new_context(viewport={'width': 1440, 'height': 900})
    desktop.add_init_script(MOCK_VIBRATION)
    desktop_page = desktop.new_page()
    desktop_page.goto(BASE + '/', wait_until='networkidle')
    expect(desktop_page.locator('[data-haptics-toggle]')).not_to_be_visible()
    desktop_page.locator('#search-open').click()
    assert desktop_page.evaluate('window.__vibrations') == []
    desktop.close()

    unsupported = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    unsupported.add_init_script("Object.defineProperty(navigator, 'vibrate', {configurable: true, value: undefined})")
    unsupported_page = unsupported.new_page()
    unsupported_page.goto(BASE + '/', wait_until='networkidle')
    expect(unsupported_page.locator('[data-haptics-toggle]')).not_to_be_visible()
    unsupported_page.locator('#search-open').tap()
    expect(unsupported_page.locator('#search-dialog')).to_be_visible()
    unsupported.close()
    browser.close()
    print('PASS: honest style references, search/sort, saved ideas, clear preferences, eBay handoff, mobile navigation/layout, and progressive haptics (toggle, no load/scroll pulse, reduced motion, desktop/unsupported fallback)')
