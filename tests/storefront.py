"""Behavioral checks for the EVOVO eBay showroom and progressive touch feedback.
Run the built site on port 3000, or set EVOVO_BASE_URL to a deployed site.
Requires Python Playwright and Chromium at /usr/bin/chromium.
"""
import os
import re
from urllib.parse import parse_qs, urlparse
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


def check_style_showcase(browser):
    """The dimensional showcase is manually controlled and saves real reference IDs."""
    context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    page = context.new_page()
    stage_errors = []
    page.on('pageerror', lambda error: stage_errors.append(str(error)))
    page.goto(BASE + '/', wait_until='networkidle')
    stage = page.locator('[data-style-stage]')
    expect(stage).to_have_attribute('aria-roledescription', 'carousel')
    expect(stage.locator('[data-stage-index]')).to_have_count(5)
    ideas = ['core-tee', 'daily-hoodie', 'studio-layer', 'off-duty-pant', 'graphic-tee']

    def selected(index):
        expect(stage.locator('.stage-save')).to_have_attribute('data-save', ideas[index])
        expect(stage.locator('[data-stage-read]')).to_have_attribute('href', '/products/' + ideas[index] + '/')
        expect(stage.locator('.stage-card-active')).to_have_attribute('href', '/products/' + ideas[index] + '/')
        expect(stage.locator('[data-stage-index][aria-pressed="true"]')).to_have_count(1)
        expect(stage.locator(f'[data-stage-index="{index}"]')).to_have_attribute('aria-pressed', 'true')
        expect(stage.locator('[data-stage-status]')).to_contain_text(f'{index + 1} of 5')

    selected(0)
    stage.locator('[data-stage-index="4"]').click()
    selected(4)
    expect(stage.locator('[data-stage-index="4"]')).to_be_focused()
    stage.locator('[data-stage-move="1"]').click()
    selected(0)
    expect(stage.locator('[data-stage-move="1"]')).to_be_focused()
    stage.locator('[data-stage-move="-1"]').click()
    selected(4)
    stage.focus()
    page.keyboard.press('ArrowRight')
    selected(0)
    expect(stage).to_be_focused()
    stage.locator('[data-stage-index="2"]').click()
    page.keyboard.press('ArrowLeft')
    selected(1)
    expect(stage.locator('[data-stage-index="2"]')).to_be_focused()
    # The image link is keyboard-focusable too; replacing its slide must retain focus.
    stage.locator('.stage-card-active').focus()
    page.keyboard.press('ArrowRight')
    selected(2)
    expect(stage.locator('.stage-card-active')).to_be_focused()
    assert stage.locator('.stage-card-active').evaluate('(el) => getComputedStyle(el).outlineStyle') != 'none'
    page.locator('#search-open').click()
    page.locator('#search-input').fill('hoodie')
    page.keyboard.press('ArrowRight')
    selected(2)
    page.get_by_role('button', name='Close search', exact=True).click()

    # No timer advances a slide, even after a minute.
    page.clock.install()
    page.clock.fast_forward(60000)
    selected(2)
    stage.locator('.stage-save').click()
    expect(stage.locator('.stage-save')).to_have_attribute('aria-pressed', 'true')
    expect(page.locator('[data-saved-count]')).to_have_text(['1', '1'])
    assert page.evaluate("JSON.parse(localStorage.getItem('evovo.saved'))") == ['studio-layer']
    expect(page.locator('.edit-preview [data-save="studio-layer"]')).to_have_attribute('aria-pressed', 'true')
    stage.locator('[data-stage-read]').click()
    expect(page.locator('h1')).to_have_text('A softer neutral')
    expect(page.locator('.detail-save')).to_have_attribute('aria-pressed', 'true')
    page.goto(BASE + '/', wait_until='networkidle')
    stage.locator('[data-stage-index="2"]').click()
    expect(stage.locator('.stage-save')).to_have_attribute('aria-pressed', 'true')
    stage.locator('.stage-save').click()
    expect(page.locator('[data-saved-count]')).to_have_text(['0', '0'])
    expect(page.locator('.edit-preview [data-save="studio-layer"]')).to_have_attribute('aria-pressed', 'false')
    page.locator('[data-undo-save="studio-layer"]').click()
    expect(stage.locator('.stage-save')).to_have_attribute('aria-pressed', 'true')
    assert not stage_errors, stage_errors
    context.close()

    phone = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    mobile = phone.new_page()
    mobile.goto(BASE + '/', wait_until='networkidle')
    for width in [320, 390, 768, 1440]:
        mobile.set_viewport_size({'width': width, 'height': 900})
        assert_fits(mobile)
        for control in mobile.locator('[data-stage-move], [data-stage-index], .stage-save, [data-stage-read]').all():
            box = control.bounding_box()
            assert box and box['width'] >= 43.9 and box['height'] >= 43.9, (width, box)
    mobile.set_viewport_size({'width': 390, 'height': 844})
    mobile.locator('[data-stage-move="1"]').tap()
    expect(mobile.locator('.stage-save')).to_have_attribute('data-save', 'daily-hoodie')
    mobile.locator('[data-stage-index="4"]').tap()
    expect(mobile.locator('.stage-save')).to_have_attribute('data-save', 'graphic-tee')
    mobile.locator('[data-stage-move="1"]').tap()
    expect(mobile.locator('.stage-save')).to_have_attribute('data-save', 'core-tee')
    mobile.locator('[data-style-stage]').screenshot(path='/workspace/stage-mobile.png', animations='disabled')
    phone.close()

    reduced = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    reduced_page = reduced.new_page()
    reduced_page.goto(BASE + '/', wait_until='networkidle')
    reduced_page.locator('[data-stage-move="1"]').click()
    assert reduced_page.locator('.stage-card-active').evaluate('(el) => getComputedStyle(el).animationName') == 'none'
    for control in reduced_page.locator('[data-stage-move], [data-stage-index]').all():
        assert control.evaluate('(el) => getComputedStyle(el).transitionDuration') == '0s'
    reduced_page.locator('[data-style-stage]').screenshot(path='/workspace/stage-desktop.png', animations='disabled')
    reduced.close()


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'], headless=True)
    if not os.environ.get('EVOVO_SKIP_STAGE'):
        check_style_showcase(browser)
    if os.environ.get('EVOVO_STAGE_ONLY'):
        browser.close()
        print('PASS: manual style showcase wraparound, scoped keyboard/focus, saved persistence/links, no autoplay, touch targets and reduced motion')
        raise SystemExit(0)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    intercept_ebay(context)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))

    page.goto(BASE + '/', wait_until='networkidle')
    expect(page.locator('h1')).to_contain_text('Find your style.')
    assert page.title().startswith('EVOVO')
    assert page.locator('main .category-card').count() == 4
    assert page.locator('main .product-card').count() == 0
    expect(page.locator('[data-style-stage]')).to_have_count(1)
    expect(page.locator('[data-stage-index]')).to_have_count(5)
    assert page.locator('#cart-open, #detail-add, .size-options').count() == 0
    assert '$' not in page.locator('main').inner_text()
    assert '®' not in page.locator('body').inner_text()
    expect(page.locator('.hero-actions .pill')).to_have_attribute('href', '/shop/')
    expect(page.locator('.hero-actions .text-link')).to_have_attribute('href', EBAY)
    expect(page.locator('#main')).to_have_attribute('data-ready', 'true')
    expect(page.locator('#main')).to_have_attribute('aria-busy', 'false')
    expect(page.locator('.app-loading')).to_have_count(0)
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
    page.locator('#search-open').click()
    page.locator('#search-input').fill('black')
    page.locator('.search-view-all').click()
    expect(page).to_have_url(re.compile(r'q=black'))
    expect(page.locator('#collection-query')).to_have_value('black')
    expect(page.locator('#collection-grid .product-card')).to_have_count(2)

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
    expect(page.locator('.empty .state-illustration')).to_have_count(1)
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
    expect(page.locator('.error-state .state-illustration')).to_have_count(1)

    # Responsive navigation and typography at small-phone through desktop widths.
    for width in [320, 390, 768, 1440]:
        page.set_viewport_size({'width': width, 'height': 900})
        for route in ['/', '/shop/', '/products/core-tee/', '/help/']:
            page.goto(BASE + route, wait_until='networkidle')
            assert_fits(page)
            if width <= 760:
                expect(page.locator('.mobile-dock')).to_be_visible()
                page.evaluate('scrollTo(0, document.documentElement.scrollHeight)')
                assert page.locator('.footer-bottom').evaluate('(el) => el.getBoundingClientRect().bottom <= document.querySelector(".mobile-dock").getBoundingClientRect().top + 1')
            else:
                expect(page.locator('.mobile-dock')).not_to_be_visible()
    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto(BASE + '/', wait_until='networkidle')
    expect(page.locator('.mobile-dock')).to_be_visible()
    page.locator('[data-dock="saved"]').click()
    expect(page.locator('h1')).to_contain_text('Keep the good ideas.')
    expect(page.locator('[data-dock="saved"]')).to_have_attribute('aria-current', 'page')
    page.goto(BASE + '/', wait_until='networkidle')
    page.get_by_role('button', name='Open navigation', exact=True).click()
    expect(page.locator('#menu-dialog')).to_be_visible()
    page.locator('#menu-dialog').get_by_role('link', name='Hoodies', exact=True).click()
    expect(page.locator('h1')).to_contain_text('Hoodies')
    page.goto(BASE + '/', wait_until='networkidle')
    reveal_and_capture(page, '/workspace/evovo-launch-mobile.png')
    page.evaluate('scrollTo(0, document.documentElement.scrollHeight)')
    assert page.locator('.footer-bottom').evaluate('(el) => el.getBoundingClientRect().bottom <= document.querySelector(".mobile-dock").getBoundingClientRect().top + 1')
    page.locator('.mobile-dock .dock-ebay').click()
    expect(page).to_have_url(EBAY)
    assert not errors, errors
    context.close()

    # The example edit is a real, reusable shared board, never an automatic import.
    preview_context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    preview = preview_context.new_page()
    preview.goto(BASE + '/', wait_until='networkidle')
    expect(preview.locator('.edit-preview .preview-card')).to_have_count(3)
    preview_ids = preview.locator('.edit-preview .save-button').evaluate_all('(buttons) => buttons.map(button => button.dataset.save)')
    assert preview_ids == ['core-tee', 'studio-layer', 'off-duty-pant']
    expect(preview.get_by_role('link', name='Open the example board', exact=True)).to_have_attribute('href', '/saved/?board=core-tee,studio-layer,off-duty-pant')
    preview.locator('.edit-preview .save-button[data-save="studio-layer"]').click()
    expect(preview.locator('.edit-preview .save-button[data-save="studio-layer"]')).to_have_attribute('aria-pressed', 'true')
    expect(preview.locator('[data-saved-count]')).to_have_text(['1', '1'])
    preview.reload(wait_until='networkidle')
    expect(preview.locator('.edit-preview .save-button[data-save="studio-layer"]')).to_have_attribute('aria-pressed', 'true')
    preview.get_by_role('link', name='Open the example board', exact=True).click()
    expect(preview.locator('h1')).to_contain_text('Good ideas travel.')
    expect(preview.locator('#collection-grid .product-card')).to_have_count(3)
    assert preview.evaluate("JSON.parse(localStorage.getItem('evovo.saved'))") == ['studio-layer']
    preview.locator('[data-import-board]').click()
    assert set(preview.evaluate("JSON.parse(localStorage.getItem('evovo.saved'))")) == set(preview_ids)
    expect(preview.locator('[data-import-board]')).to_be_disabled()
    expect(preview.locator('[data-saved-count]')).to_have_text(['3', '3'])
    preview.goto(BASE + '/', wait_until='networkidle')
    expect(preview.locator('.edit-preview .save-button[aria-pressed="true"]')).to_have_count(3)
    preview.locator('#search-open').click()
    preview.locator('#search-input').fill('not-a-real-style')
    expect(preview.locator('.search-empty .state-illustration')).to_have_count(1)
    preview_context.close()

    # A saved board is useful across filters, reloads, tabs, and explicit sharing.
    board_context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    board_context.add_init_script("""
        window.__copied = null;
        window.__clipboardFails = false;
        Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {
            writeText: async text => {
                if (window.__clipboardFails) throw new Error('Test clipboard denial');
                window.__copied = text;
            }
        }});
        window.__savedWrites = 0;
        const realSetItem = Storage.prototype.setItem;
        Storage.prototype.setItem = function(key, value) {
            if (key === 'evovo.saved') window.__savedWrites++;
            return realSetItem.call(this, key, value);
        };
    """)
    board = board_context.new_page()
    board_errors = []
    board.on('pageerror', lambda error: board_errors.append(str(error)))

    def board_count(expected):
        expect(board.locator('[data-saved-count]')).to_have_text([str(expected), str(expected)])
        for link in board.locator('[data-saved-nav]').all():
            expect(link).to_have_attribute('aria-label', f'Saved ideas ({expected})')

    board.goto(BASE + '/', wait_until='networkidle')
    board_count(0)
    for idea, total in [('core-tee', 1), ('daily-hoodie', 2), ('off-duty-pant', 3)]:
        board.goto(BASE + '/products/' + idea + '/', wait_until='networkidle')
        board.locator('.detail-save').click()
        board_count(total)
    board.reload(wait_until='networkidle')
    board_count(3)
    board.goto(BASE + '/saved/', wait_until='networkidle')
    expect(board.locator('#collection-grid .product-card')).to_have_count(3)
    board.locator('.save-button[data-save="daily-hoodie"]').click()
    board_count(2)
    board.locator('[data-undo-save="daily-hoodie"]').click()
    board_count(3)
    expect(board.locator('#collection-grid .product-card')).to_have_count(3)
    board.locator('[data-category-link="Shirts"]').click()
    expect(board).to_have_url(re.compile(r'category=Shirts'))
    expect(board.locator('#collection-grid .product-card')).to_have_count(1)
    board.locator('#collection-query').fill('black')
    expect(board.locator('#collection-grid .product-card')).to_have_count(0)
    expect(board.locator('#collection-grid')).to_contain_text('Your ideas are still here.')
    board_count(3)
    board.locator('[data-reset-filters]').click()
    expect(board.locator('#collection-grid .product-card')).to_have_count(3)
    expect(board.locator('#collection-query')).to_have_value('')
    expect(board.locator('[data-category-link="All"]')).to_have_attribute('aria-current', 'page')
    board.locator('#product-sort').select_option('name')
    expect(board).to_have_url(re.compile(r'sort=name'))
    board.reload(wait_until='networkidle')
    expect(board.locator('#product-sort')).to_have_value('name')
    names = board.locator('.product-info a').all_text_contents()
    assert names == sorted(names, key=str.casefold), names
    board.go_back(wait_until='networkidle')
    expect(board.locator('#product-sort')).to_have_value('editorial')

    # Copy shares the whole board, even when only one idea is visible.
    board.locator('#collection-query').fill('olive')
    expect(board.locator('#collection-grid .product-card')).to_have_count(1)
    board.locator('[data-copy-board]').click()
    expect(board.locator('#toast')).to_contain_text('Board link copied')
    shared_url = board.evaluate('window.__copied')
    shared_query = parse_qs(urlparse(shared_url).query)
    assert set(shared_query['board'][0].split(',')) == {'core-tee', 'daily-hoodie', 'off-duty-pant'}
    assert 'q' not in shared_query and 'category' not in shared_query
    board.evaluate('window.__clipboardFails = true')
    board.locator('[data-copy-board]').click()
    expect(board.locator('#share-dialog')).to_be_visible()
    expect(board.locator('#board-link')).to_have_value(shared_url)
    expect(board.locator('#board-link')).to_have_attribute('readonly', '')
    expect(board.locator('#board-link')).to_be_focused()
    board.keyboard.press('Escape')
    expect(board.locator('#share-dialog')).not_to_be_visible()

    # A recipient keeps their existing ideas until explicitly importing a board.
    board.evaluate("localStorage.setItem('evovo.saved', JSON.stringify(['crew-socks']))")
    board.goto(BASE + '/saved/?board=core-tee,daily-hoodie,core-tee,not-a-real-id', wait_until='networkidle')
    board_count(1)
    expect(board.locator('#collection-grid .product-card')).to_have_count(2)
    assert board.evaluate("JSON.parse(localStorage.getItem('evovo.saved'))") == ['crew-socks']
    board.locator('[data-import-board]').click()
    board_count(3)
    assert set(board.evaluate("JSON.parse(localStorage.getItem('evovo.saved'))")) == {'crew-socks', 'core-tee', 'daily-hoodie'}
    expect(board.locator('[data-import-board]')).to_be_disabled()
    expect(board.locator('[data-import-board]')).to_have_text('All ideas saved')
    board.goto(BASE + '/saved/?board=unknown-id', wait_until='networkidle')
    expect(board.locator('#collection-grid')).to_contain_text('No ideas in this link.')
    expect(board.locator('[data-copy-board]')).to_be_disabled()
    expect(board.locator('[data-import-board]')).to_be_disabled()
    board_count(3)
    board.goto(BASE + '/saved/', wait_until='networkidle')
    expect(board.locator('#collection-grid .product-card')).to_have_count(3)

    # Actual storage events update other open tabs without writing back.
    other = board_context.new_page()
    other.goto(BASE + '/', wait_until='networkidle')
    before_writes = board.evaluate('window.__savedWrites')
    other.evaluate("localStorage.setItem('evovo.saved', JSON.stringify(['core-tee']))")
    board_count(1)
    expect(board.locator('#collection-grid .product-card')).to_have_count(1)
    assert board.evaluate('window.__savedWrites') == before_writes
    other.evaluate('localStorage.clear()')
    board_count(0)
    expect(board.locator('#collection-grid')).to_contain_text('Start your moodboard.')
    expect(board.locator('[data-copy-board]')).to_be_disabled()
    other.close()
    board.goto(BASE + '/saved/?board=core-tee,daily-hoodie,off-duty-pant', wait_until='networkidle')
    board.set_viewport_size({'width': 390, 'height': 844})
    assert_fits(board)
    board.screenshot(path='/workspace/evovo-launch-board.png', full_page=True, animations='disabled')
    assert not board_errors, board_errors
    board_context.close()

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
    reduced_page.keyboard.press('Escape')
    reduced_page.set_viewport_size({'width': 1440, 'height': 1000})
    reduced_page.locator('.edit-preview').scroll_into_view_if_needed()
    assert reduced_page.locator('.edit-preview').evaluate('(el) => getComputedStyle(el).transform') == 'none'
    reduced_page.locator('.edit-preview').hover()
    assert reduced_page.locator('.edit-preview').evaluate('(el) => getComputedStyle(el).transform') == 'none'
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
    # Actual module failure leaves a useful page, and the explicit reload recovers it.
    failed_context = browser.new_context(viewport={'width': 390, 'height': 844})
    failed = failed_context.new_page()
    failed.clock.install()
    failed.route('**/app.js', lambda route: route.abort())
    failed.goto(BASE + '/', wait_until='load')
    failed.clock.fast_forward(7000)
    expect(failed.locator('#main')).to_have_class(re.compile(r'\bis-error\b'))
    expect(failed.locator('[data-boot-message]')).to_have_text('The style ideas couldn’t load. Try reloading, or browse our eBay page.')
    expect(failed.locator('[data-reload-app]')).to_be_visible()
    assert failed.locator('#main').get_attribute('aria-busy') is None
    expect(failed.locator('#main a')).to_have_attribute('href', EBAY)
    assert failed.locator('.loading-signal').evaluate('(el) => getComputedStyle(el, "::after").animationName') == 'none'
    # A failed photograph must not mark a healthy app as broken.
    failed.unroute('**/app.js')
    failed.route('**/assets/hero.jpg', lambda route: route.abort())
    failed.locator('[data-reload-app]').click()
    expect(failed.locator('h1')).to_contain_text('Find your style.')
    expect(failed.locator('#main')).to_have_attribute('data-ready', 'true')
    expect(failed.locator('#main')).to_have_attribute('aria-busy', 'false')
    failed.clock.fast_forward(7000)
    assert not failed.locator('#main').evaluate('(el) => el.classList.contains("is-error")')
    expect(failed.locator('.app-loading')).to_have_count(0)
    failed_context.close()

    browser.close()
    print('PASS: honest showroom and eBay handoff; mobile dock/live counts; saved-board filters, undo, sharing/import, clipboard fallback and cross-tab sync; responsive layouts, manual style showcase, real example-board preview/import, loading fallback/reload, and progressive haptics')
