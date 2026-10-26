"""Behavioral integration checks for EVOVO. Run with local site on port 3000.
Requires Python Playwright and Chromium; EVOVO_BASE_URL may target another host.
"""
import os
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get('EVOVO_BASE_URL', 'http://localhost:3000')

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'], headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE + '/', wait_until='networkidle')
    expect(page.locator('h1')).to_contain_text('STAND')
    assert page.title().startswith('EVOVO')
    assert page.locator('main .category-card').count() == 4
    assert page.locator('main .product-card').count() >= 4
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    for image in page.locator('main img').all():
        image.scroll_into_view_if_needed()
        expect(image).to_have_js_property('complete', True)
        assert image.evaluate('(i)=>i.naturalWidth>0')
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path='/workspace/evovo-desktop.png', full_page=True)

    # Header search finds a known category and can open a product.
    page.get_by_role('button', name='Search products', exact=True).click()
    page.get_by_role('searchbox', name='Search the collection', exact=True).fill('hoodie')
    expect(page.locator('#search-results .search-result')).not_to_have_count(0)
    page.get_by_role('button', name='Close search', exact=True).click()

    for category in ['Shirts', 'Hoodies', 'Pants', 'Socks']:
        page.goto(BASE + '/shop/' + category.lower() + '/')
        expect(page.locator('.catalog-head h1')).to_contain_text(category)
        assert page.locator('#collection-grid .product-card').count() >= 1
    page.goto(BASE + '/shop/')
    count = page.locator('#collection-grid .product-card').count()
    assert count >= 7
    page.get_by_role('combobox', name='Sort products').select_option('low')
    prices = [int(x.replace('$', '').replace(',', '')) for x in page.locator('.product-info > span').all_text_contents()]
    assert prices == sorted(prices)
    page.get_by_role('searchbox', name='Search collection', exact=True).fill('zzzz-no-match')
    expect(page.locator('#collection-grid .product-card')).to_have_count(0)
    page.get_by_role('searchbox', name='Search collection', exact=True).fill('')
    expect(page.locator('#collection-grid .product-card')).to_have_count(count)

    page.goto(BASE + '/products/core-tee/')
    expect(page.locator('h1')).to_contain_text('Core Tee')
    page.locator('#detail-add').click()
    expect(page.locator('#toast')).to_contain_text('Choose a size')
    expect(page.locator('#bag-count')).to_have_text('0')
    page.locator('[data-size="M"]').click()
    page.locator('#detail-add').click()
    expect(page.locator('#bag-count')).to_have_text('1')
    page.reload()
    expect(page.locator('#bag-count')).to_have_text('1')

    # Save, unsave, and persistence use actual rendered controls.
    page.locator('.detail-save').click()
    expect(page.locator('.detail-save')).to_have_attribute('aria-pressed', 'true')
    page.goto(BASE + '/saved/')
    expect(page.locator('#collection-grid .product-card')).to_have_count(1)
    page.locator('.save-button').click()
    expect(page.locator('#collection-grid .product-card')).to_have_count(0)

    page.locator('#cart-open').click()
    expect(page.locator('#cart-dialog')).to_be_visible()
    page.get_by_role('button', name='Increase quantity of Core Tee', exact=True).click()
    expect(page.locator('#bag-count')).to_have_text('2')
    expect(page.locator('.cart-summary .totals strong')).to_have_text('$90')
    page.get_by_role('button', name='Decrease quantity of Core Tee', exact=True).click()
    expect(page.locator('.cart-summary .totals strong')).to_have_text('$45')
    page.locator('.cart-summary a').click()
    expect(page.locator('.checkout-message')).to_contain_text("Checkout isn't open yet.")
    expect(page.locator('.checkout-message')).to_contain_text('No charge has been made')
    page.get_by_role('button', name='Edit your bag', exact=False).click()
    page.get_by_role('button', name='Remove Core Tee', exact=True).click()
    expect(page.locator('#bag-count')).to_have_text('0')
    expect(page.locator('#cart-content')).to_contain_text('Your bag is empty')
    page.get_by_role('button', name='Close bag', exact=True).click()
    page.goto(BASE + '/checkout/')
    expect(page.locator('main')).to_contain_text('Your bag is empty')

    # The built 404 shell recognizes invalid application routes.
    response = page.goto(BASE + '/404.html')
    expect(page.locator('h1')).to_contain_text('Lost your way?')

    # Test mobile navigation and horizontal layout.
    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto(BASE + '/', wait_until='networkidle')
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    page.screenshot(path='/workspace/evovo-mobile.png', full_page=True)
    page.get_by_role('button', name='Open navigation', exact=True).click()
    expect(page.locator('#menu-dialog')).to_be_visible()
    page.locator('#menu-dialog').get_by_role('link', name='Hoodies', exact=True).click()
    expect(page.locator('h1')).to_contain_text('Hoodies')
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    page.goto(BASE + '/products/core-tee/')
    page.get_by_role('button', name='Size guide', exact=False).click()
    expect(page.locator('#size-dialog')).to_be_visible()
    expect(page.locator('#size-dialog table')).to_be_visible()
    page.keyboard.press('Escape')
    expect(page.locator('#size-dialog')).not_to_be_visible()
    assert not errors, errors
    browser.close()
    print('PASS: desktop/mobile navigation, all categories, search/sort, size validation, cart edits/totals, persistence, saved pieces, truthful checkout, 404 and image/layout checks')
