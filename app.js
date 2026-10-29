import {products, categories, EBAY_STORE_URL} from '/catalog.js';
import '/interactions.js';

const $ = selector => document.querySelector(selector);
const escapeHTML = value => String(value).replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
const arrow = '<svg class="arrow-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg>';

const icons = {
  search: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.7"/><path d="m16 16 5 5"/></svg>',
  heart: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.7c-2.3-2.2-6-1.5-8.8 1.5C9.2 3.2 5.5 2.5 3.2 4.7c-2.4 2.4-1.6 6.5.8 9L12 21l8-7.3c2.4-2.5 3.2-6.6.8-9z"/></svg>',
  menu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7h18M3 16h18"/></svg>'
};
$('#search-open').innerHTML = icons.search;
$('.saved-link').innerHTML = icons.heart + '<span class="saved-count" data-saved-count aria-hidden="true">0</span>';
document.querySelectorAll('[data-heart-icon]').forEach(element => element.innerHTML = icons.heart);
$('#menu-open').innerHTML = icons.menu;
$('#year').textContent = new Date().getFullYear();
document.querySelectorAll('[data-arrow]').forEach(element => element.innerHTML = arrow);

function readSaved() {
  try {
    const value = JSON.parse(localStorage.getItem('evovo.saved') || '[]');
    return Array.isArray(value) ? [...new Set(value.filter(id => products.some(p => p.id === id)))] : [];
  } catch { return []; }
}
let saved = readSaved();
let toastTimer;
let clearSnapshot = null;
function dismissToastLater() {
  clearTimeout(toastTimer);
  const notification = $('#toast');
  if (notification.querySelector('[data-undo-save], [data-undo-clear]') || notification.contains(document.activeElement) || notification.matches(':hover')) return;
  toastTimer = setTimeout(() => notification.hidden = true, 3200);
}
function toast(message, undoId = '', undoClear = false) {
  $('#toast').innerHTML = `<span>${escapeHTML(message)}</span>${undoId ? `<button data-undo-save="${undoId}">Undo</button>` : undoClear ? '<button data-undo-clear>Undo clear</button>' : ''}${undoId || undoClear ? '<button class="toast-dismiss" data-dismiss-toast aria-label="Dismiss notification">×</button>' : ''}`;
  $('#toast').hidden = false;
  dismissToastLater();
}
$('#toast').addEventListener('pointerenter', () => clearTimeout(toastTimer));
$('#toast').addEventListener('pointerleave', dismissToastLater);
$('#toast').addEventListener('focusin', () => clearTimeout(toastTimer));
$('#toast').addEventListener('focusout', () => queueMicrotask(dismissToastLater));
const asset = p => '/assets/' + p.image;
const productURL = p => '/products/' + p.id + '/';
const searchAliases = {
  Shirts: 'shirt shirts tee tees t shirt tshirt tshirts',
  Hoodies: 'hoodie hoodies sweatshirt sweatshirts',
  Pants: 'pant pants trouser trousers',
  Socks: 'sock socks'
};
function matchesProduct(p, value) {
  const words = text => text.toLowerCase().normalize('NFKD').match(/[\p{L}\p{N}]+/gu) || [];
  const terms = words(value);
  const searchable = words(`${p.name} ${p.category} ${p.color} ${p.fit || ''} ${searchAliases[p.category]} ${p.color === 'Grey' ? 'gray' : ''}`);
  return terms.every(term => searchable.some(word => word.includes(term)));
}
function collectionProductURL(p) {
  const from = isCatalog ? location.pathname + location.search : collectionReturn()?.href;
  return productURL(p) + (from ? '?from=' + encodeURIComponent(from) : '');
}
function collectionReturn() {
  const from = new URLSearchParams(location.search).get('from');
  if (!from || !from.startsWith('/') || from.startsWith('//')) return null;
  try {
    const url = new URL(from, location.origin);
    if (url.origin !== location.origin || !/^\/(shop(?:\/(shirts|hoodies|pants|socks))?|saved)\/?$/.test(url.pathname)) return null;
    const label = url.pathname.startsWith('/saved') ? url.searchParams.has('board') ? 'Back to this shared board' : 'Back to your saved ideas' : 'Back to your style ideas';
    return {href: url.pathname + url.search, label};
  } catch { return null; }
}
const ebayButton = (label = 'Shop EVOVOFinds on eBay', className = 'pill') => `<a class="${className}" href="${EBAY_STORE_URL}" data-haptic>${label} ${arrow}</a>`;
const referenceNote = '<p class="reference-note">Style inspiration using reference photography. For items, prices, and availability, visit our eBay listings.</p>';

function card(p) {
  const isSaved = saved.includes(p.id);
  return `<article class="product-card" id="idea-${p.id}">
    <a class="product-image" href="${escapeHTML(collectionProductURL(p))}"><img src="${asset(p)}" alt="${p.name}, style reference" loading="lazy" width="800" height="960"><span class="product-tag">Style idea</span></a>
    <button class="save-button" data-save="${p.id}" aria-label="${isSaved ? 'Unsave' : 'Save'} ${p.name}" aria-pressed="${isSaved}">${icons.heart}</button>
    <div class="product-info"><a href="${escapeHTML(collectionProductURL(p))}">${p.name}</a><span>${arrow}</span></div>
    <p class="product-meta">${p.category} · ${p.color}</p>
  </article>`;
}
function sectionHeading(label, title, href = '/shop/', link = 'All style ideas') {
  return `<div class="section-head"><div><span class="eyebrow">${label}</span><h2>${title}</h2></div><a class="text-link" href="${href}">${link} ${arrow}</a></div>`;
}
function steps() {
  return `<div class="steps-grid">
    <article><span class="step-number">01</span><h3>Explore the listings</h3><p>Our eBay seller page is the place to see what's currently available.</p></article>
    <article><span class="step-number">02</span><h3>Check the details</h3><p>Look at the item photos, measurements, condition, and delivery details on each listing.</p></article>
    <article><span class="step-number">03</span><h3>Buy through eBay</h3><p>Choose your item and complete checkout on eBay. You can message the seller there, too.</p></article>
  </div>`;
}
const exampleBoardURL = '/saved/?board=core-tee,studio-layer,off-duty-pant';
function editPreview() {
  const edit = ['core-tee', 'studio-layer', 'off-duty-pant'].map(id => products.find(p => p.id === id));
  return `<section class="edit-feature section" data-reveal><div class="edit-feature-copy"><span class="eyebrow">THE PERSONAL EDIT / YOUR IDEAS, TOGETHER</span><h2>Less scrolling.<br>More <em>you.</em></h2><p>Keep the styles that catch your eye. Search your saved ideas, find a combination you like, and share your whole board with a link.</p><a class="pill" href="${exampleBoardURL}">Open the example board ${arrow}</a><span class="feature-footnote">Try it first. Nothing is added to your saved ideas until you choose.</span></div><div class="edit-preview"><div class="edit-preview-head"><div><span class="eyebrow">EXAMPLE BOARD</span><h3>The everyday edit</h3></div><span class="edit-count">3 style ideas</span></div><div class="edit-preview-grid">${edit.map(p => `<article class="preview-card"><a href="${productURL(p)}"><img src="${asset(p)}" alt="${p.name}, style reference" loading="lazy" width="240" height="300"></a><button class="save-button" data-save="${p.id}" aria-label="${saved.includes(p.id) ? 'Unsave' : 'Save'} ${p.name}" aria-pressed="${saved.includes(p.id)}">${icons.heart}</button><a href="${productURL(p)}" class="preview-name">${p.name}</a><span>${p.category}</span></article>`).join('')}</div><div class="edit-preview-footer"><span>Save an idea with the heart. Make the edit yours.</span><a href="${exampleBoardURL}" aria-label="Explore the everyday example board">${arrow}</a></div></div></section>`;
}
const showcaseIdeas = ['core-tee','daily-hoodie','studio-layer','off-duty-pant','graphic-tee'].map(id => products.find(p => p.id === id));
let showcaseIndex = 0;
function stageCards() {
  const current = showcaseIdeas[showcaseIndex];
  const previous = showcaseIdeas[(showcaseIndex + showcaseIdeas.length - 1) % showcaseIdeas.length];
  const next = showcaseIdeas[(showcaseIndex + 1) % showcaseIdeas.length];
  return `<div class="stage-orbit" aria-hidden="true"></div><div class="stage-card stage-card-before" aria-hidden="true"><img src="${asset(previous)}" alt="" loading="eager" decoding="async"><span>${previous.category}</span></div><a href="${productURL(current)}" class="stage-card stage-card-active" aria-label="Read ${current.name}"><img src="${asset(current)}" alt="${current.name}, style reference" loading="eager" decoding="async"><span class="stage-reference-label">STYLE REFERENCE</span></a><div class="stage-card stage-card-after" aria-hidden="true"><img src="${asset(next)}" alt="" loading="eager" decoding="async"><span>${next.category}</span></div>`;
}
function styleShowcase() {
  const current = showcaseIdeas[showcaseIndex];
  return `<section id="style-showcase" class="style-showcase section" data-style-stage aria-label="Style showcase" aria-roledescription="carousel" tabindex="0"><div class="showcase-heading"><div><span class="eyebrow">THE STYLE NOTES / A DIFFERENT ANGLE</span><h2>A point<br>of <em>view.</em></h2></div><p>One idea at a time. Take a closer look, save what feels right, and make the edit your own.</p><a href="/shop/" class="text-link">All style ideas ${arrow}</a></div><div class="showcase-layout"><div class="stage-viewport" data-stage-viewport>${stageCards()}</div><div class="stage-slide-copy"><span class="eyebrow" data-stage-category>${current.category} / ${current.color}</span><h3 data-stage-title>${current.name}</h3><p data-stage-description>${current.description}</p><div class="stage-actions"><a class="pill" data-stage-read href="${productURL(current)}">Read the style note ${arrow}</a><button class="pill outline stage-save" data-save="${current.id}" aria-pressed="${saved.includes(current.id)}">${icons.heart}<span>${saved.includes(current.id) ? 'Saved to your ideas' : 'Save this idea'}</span></button></div><p class="stage-disclosure">Inspiration photography. Actual items and availability are on eBay.</p></div></div><div class="stage-navigation"><div class="stage-arrows"><button data-stage-move="-1" aria-label="Previous style idea"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m6-6-6 6 6 6"/></svg></button><button data-stage-move="1" aria-label="Next style idea"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg></button></div><div class="stage-choices" role="group" aria-label="Choose a style idea">${showcaseIdeas.map((p,i) => `<button data-stage-index="${i}" aria-label="Show ${p.name}" aria-pressed="${i === showcaseIndex}"><span>${String(i+1).padStart(2,'0')}</span></button>`).join('')}</div><p data-stage-status role="status" aria-live="polite">${current.name} · 1 of ${showcaseIdeas.length}</p><span class="stage-keyboard-hint">Arrows to explore. Yours to save.</span></div></section>`;
}
function setShowcase(index) {
  const stage = $('[data-style-stage]');
  if (!stage) return;
  const cardHadFocus = !!$('[data-stage-viewport]')?.contains(document.activeElement);
  showcaseIndex = (index + showcaseIdeas.length) % showcaseIdeas.length;
  const p = showcaseIdeas[showcaseIndex];
  $('[data-stage-viewport]').innerHTML = stageCards();
  $('[data-stage-category]').textContent = p.category + ' / ' + p.color;
  $('[data-stage-title]').textContent = p.name;
  $('[data-stage-description]').textContent = p.description;
  $('[data-stage-read]').href = productURL(p);
  const saveButton = $('.stage-save');
  saveButton.dataset.save = p.id;
  saveButton.setAttribute('aria-pressed', String(saved.includes(p.id)));
  saveButton.innerHTML = icons.heart + '<span>' + (saved.includes(p.id) ? 'Saved to your ideas' : 'Save this idea') + '</span>';
  stage.querySelectorAll('[data-stage-index]').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.stageIndex) === showcaseIndex)));
  $('[data-stage-status]').textContent = p.name + ' · ' + (showcaseIndex + 1) + ' of ' + showcaseIdeas.length;
  if (cardHadFocus) $('.stage-card-active').focus({preventScroll:true});
}
function stateIllustration() {
  return `<svg class="state-illustration" viewBox="0 0 140 105" aria-hidden="true"><rect x="20" y="18" width="65" height="76" rx="8" transform="rotate(-9 20 18)"/><rect x="54" y="12" width="65" height="76" rx="8" transform="rotate(7 54 12)"/><path d="m76 42 9 8 13-12M69 65h25"/><circle cx="25" cy="13" r="3"/></svg>`;
}
function home() {
  return `<section class="home-hero">
    <div class="hero-copy"><span class="eyebrow">EVOVO / THE PERSONAL EDIT</span><h1>Find your style.<br><em>Keep your edit.</em></h1><p>A little inspiration. A place to keep it. Explore style ideas, save your favorites, and share your edit. For the real listings, find EVOVOFinds on eBay.</p><div class="hero-actions"><a class="pill" href="/shop/">Build your edit ${arrow}</a>${ebayButton('Shop EVOVOFinds', 'text-link')}</div><div class="hero-detail"><span class="small-dot"></span>Listing details and checkout are on eBay.</div></div>
    <div class="hero-visual"><img class="hero-photo" src="/assets/hero.jpg" alt="Menswear style reference in a sunlit architectural setting" width="1800" height="2250" fetchpriority="high"><span class="photo-caption">A little inspiration for the everyday.</span><div class="seller-card"><img src="/assets/evovofinds-avatar.png" alt="EVOVOFinds EF monogram" width="64" height="64"><div><strong>EVOVOFinds</strong><span>Find us on eBay</span></div><a href="${EBAY_STORE_URL}" class="seller-arrow" aria-label="View EVOVOFinds on eBay">${arrow}</a></div></div>
  </section>
  <section class="how-strip" aria-label="Shopping at EVOVO"><span>One seller. One clear place to shop.</span><a href="/help/">Here's how it works ${arrow}</a><div><span>Browse on eBay</span><i></i><span>Buy on eBay</span><i></i><span>Message on eBay</span></div></section>
  ${editPreview()}
  <section class="section" data-reveal>${sectionHeading('A LITTLE INSPIRATION', 'Make it your everyday.')}<div class="category-grid">${categories.map((c, i) => `<a class="category-card" href="/shop/${c.toLowerCase()}/"><div><img src="/assets/${['tee-plain-black.jpg','hoodie-white.jpg','pants-olive.jpg','socks-plain.jpg'][i]}" alt="${c} style inspiration" loading="lazy"></div><span>${c} ${arrow}</span></a>`).join('')}</div>${referenceNote}</section>
  ${styleShowcase()}
  <section class="shopping-story section" data-reveal><div><span class="eyebrow">A CLEARER WAY TO SHOP</span><h2>The details<br>make the difference.</h2><p>We keep this site for the inspiration, and eBay for the shopping. No second checkout, no separate account to create here.</p><a href="/help/" class="text-link">More about shopping with us ${arrow}</a></div><div>${steps()}</div></section>
  <section class="seller-section" data-reveal><div class="seller-profile"><img src="/assets/evovofinds-avatar.png" alt="EVOVOFinds logo" width="72" height="72"><div><span class="eyebrow">THE SELLER BEHIND THE SITE</span><h2>Meet EVOVOFinds.</h2></div></div><p>See our current listings, read the seller profile, or get in touch directly on eBay.</p>${ebayButton('Visit our eBay page')}</section>`;
}

const path = location.pathname.replace(/\/+$/, '') || '/';
const isSavedPage = path === '/saved';
const isCatalog = path === '/shop' || path.startsWith('/shop/') || isSavedPage;
let currentCategory = 'All';
let query = '';
let sort = 'editorial';
let sharedIds = null;
function readCatalogState() {
  const params = new URLSearchParams(location.search);
  query = params.get('q') || '';
  sort = params.get('sort') === 'name' ? 'name' : 'editorial';
  if (isSavedPage) {
    currentCategory = categories.includes(params.get('category')) ? params.get('category') : 'All';
    sharedIds = params.has('board') ? [...new Set(params.get('board').split(',').filter(id => products.some(p => p.id === id)))] : null;
  }
}
readCatalogState();
const boardIds = () => sharedIds === null ? saved : sharedIds;
function categoryURL(category) {
  const url = new URL(isSavedPage ? '/saved/' : '/shop/' + (category === 'All' ? '' : category.toLowerCase() + '/'), location.origin);
  if (isSavedPage && category !== 'All') url.searchParams.set('category', category);
  if (isSavedPage && sharedIds !== null) url.searchParams.set('board', sharedIds.join(','));
  if (query) url.searchParams.set('q', query);
  if (sort !== 'editorial') url.searchParams.set('sort', sort);
  return url.pathname + url.search;
}
function saveCatalogState(push = false) {
  const url = new URL(location.href);
  query ? url.searchParams.set('q', query) : url.searchParams.delete('q');
  sort !== 'editorial' ? url.searchParams.set('sort', sort) : url.searchParams.delete('sort');
  if (isSavedPage) currentCategory !== 'All' ? url.searchParams.set('category', currentCategory) : url.searchParams.delete('category');
  history[push ? 'pushState' : 'replaceState'](null, '', url);
  document.querySelectorAll('[data-category-link]').forEach(link => link.href = categoryURL(link.dataset.categoryLink));
}
function catalogPage(category = 'All', savedPage = false) {
  if (!savedPage) currentCategory = category;
  const shared = savedPage && sharedIds !== null;
  return `<div class="breadcrumbs"><a href="/">Home</a><span>/</span><span>${savedPage ? shared ? 'Shared board' : 'Saved ideas' : category === 'All' ? 'Style ideas' : category}</span></div>
    <section class="catalog-head"><span class="eyebrow">${savedPage ? shared ? 'A LITTLE INSPIRATION, SHARED' : 'YOUR OWN MOODBOARD' : 'THE STYLE NOTES'}</span><h1>${savedPage ? shared ? 'Good ideas travel.' : 'Keep the good ideas.' : category === 'All' ? 'A little inspiration.' : category + ', your way.'}</h1><p>${savedPage ? shared ? 'Someone shared these style ideas with you. Explore them here, or save them alongside your own favorites.' : 'Your personal edit, kept on this device. Find a look, save it, and share your board when inspiration strikes.' : 'A few ways to think about your everyday wardrobe. These are style references, not items listed for sale.'}</p>
    ${savedPage ? `<div class="board-actions"><button class="pill" data-copy-board>Copy board link ${arrow}</button>${shared ? '<button class="pill outline" data-import-board>Save these ideas</button><a class="text-link" href="/saved/">My saved ideas</a>' : '<span class="board-local">No account needed · Saved on this device</span>'}</div>` : ebayButton('Shop current listings', 'text-link')}</section>
    <section class="catalog-body"><div class="catalog-controls"><nav class="category-tabs" aria-label="Style categories">${['All', ...categories].map(c => `<a class="${c === currentCategory ? 'active' : ''}" ${c === currentCategory ? 'aria-current="page"' : ''} data-category-link="${c}" href="${escapeHTML(categoryURL(c))}">${c === 'All' ? 'All ideas' : c}</a>`).join('')}</nav><label class="sort"><span class="sr-only">Sort style ideas</span><select id="product-sort"><option value="editorial" ${sort === 'editorial' ? 'selected' : ''}>Our edit</option><option value="name" ${sort === 'name' ? 'selected' : ''}>Name: A to Z</option></select></label></div>
    <div class="results-line"><span id="results-count" role="status" aria-live="polite"></span><form class="inline-search" id="collection-search"><label class="sr-only" for="collection-query">Search style ideas</label><input id="collection-query" type="search" placeholder="${savedPage ? 'Search your board…' : 'Try black pants…'}" value="${escapeHTML(query)}"><button type="button" data-clear-search aria-label="Clear search" ${query ? '' : 'hidden'}>×</button><button aria-label="Search ideas">${icons.search}</button></form></div><div class="product-grid" id="collection-grid"></div>${referenceNote}</section>`;
}
function updateBoardActions() {
  const copy = $('[data-copy-board]');
  if (copy) copy.disabled = !boardIds().length;
  const add = $('[data-import-board]');
  if (add) {
    const missing = boardIds().filter(id => !saved.includes(id));
    add.disabled = !missing.length;
    add.textContent = missing.length ? 'Save these ideas' : boardIds().length ? 'All ideas saved' : 'No ideas to save';
  }
}
function filterProducts() {
  const source = products.filter(p => !isSavedPage || boardIds().includes(p.id));
  let list = source.filter(p => currentCategory === 'All' || p.category === currentCategory);
  const q = query.trim().toLowerCase();
  if (q) list = list.filter(p => matchesProduct(p, q));
  if (sort === 'name') list.sort((a,b) => a.name.localeCompare(b.name));
  $('#results-count').textContent = `${list.length} ${list.length === 1 ? 'idea' : 'ideas'}${q ? ' for “' + query + '”' : ''}`;
  $('[data-clear-search]').hidden = !query;
  const emptyBoard = isSavedPage && !source.length;
  $('#collection-grid').innerHTML = list.length ? list.map(card).join('') : `<div class="empty">${stateIllustration()}<span class="eyebrow">THE PERSONAL EDIT</span><h2>${emptyBoard ? sharedIds === null ? 'Start your moodboard.' : 'No ideas in this link.' : 'Try another direction.'}</h2><p>${emptyBoard ? sharedIds === null ? 'Tap the heart on a style idea to keep it here.' : 'This board link has no recognized style ideas. Explore a few of your own.' : 'Your ideas are still here. Try another search or clear your filters.'}</p>${emptyBoard ? `<a href="/shop/" class="pill">Explore style ideas ${arrow}</a>` : '<button class="pill" data-reset-filters>Clear filters</button>'}</div>`;
  updateBoardActions();
}
function updateSavedCounts() {
  document.querySelectorAll('[data-saved-count]').forEach(element => element.textContent = saved.length);
  document.querySelectorAll('[data-saved-nav]').forEach(link => link.setAttribute('aria-label', `Saved ideas (${saved.length})`));
}
async function copyBoardLink() {
  if (!boardIds().length) return;
  const url = new URL('/saved/', location.origin);
  url.searchParams.set('board', boardIds().join(','));
  try {
    if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(url.href);
    toast('Board link copied');
  } catch {
    $('#board-link').value = url.href;
    $('#share-dialog').showModal();
    $('#board-link').select();
  }
}

function detail(p) {
  const back = collectionReturn();
  return `<nav class="breadcrumbs" aria-label="Breadcrumb">${back ? `<a class="collection-return" data-collection-return href="${escapeHTML(back.href + '#idea-' + p.id)}">← ${back.label}</a>` : `<a href="/">Home</a><span>/</span><a href="/shop/${p.category.toLowerCase()}/">${p.category}</a>`}<span>/</span><span>Style note</span></nav>
    <article class="product-detail"><div class="detail-image"><img src="${asset(p)}" alt="${p.name}, reference photography"><span class="product-tag">Style reference</span></div><div class="detail-content"><span class="eyebrow">THE STYLE NOTES / ${p.category}</span><h1>${p.name}</h1><p class="detail-copy">${p.description}</p><div class="reference-box"><strong>A little inspiration, not a listing.</strong><p>This photograph is a style reference. It doesn't represent an item available from EVOVOFinds. Check eBay for the actual item photos, prices, sizes, and availability.</p></div>${ebayButton('Browse EVOVOFinds on eBay')}<button class="pill outline detail-save" data-save="${p.id}" aria-pressed="${saved.includes(p.id)}">${icons.heart}<span>${saved.includes(p.id) ? 'Saved to your ideas' : 'Save this idea'}</span></button><details><summary>Shopping, delivery & returns ${arrow}</summary><p>Read the details on the individual eBay listing before buying. Shipping costs, condition, and return terms are shown there. If you have questions, message EVOVOFinds on eBay.</p></details></div></article>
    <section class="section soft">${sectionHeading('ANOTHER DIRECTION', 'More to work with.')}<div class="product-grid">${products.filter(x => x.id !== p.id).slice(0,4).map(card).join('')}</div></section>`;
}
function about() {
  return `<section class="about-page"><div class="about-image"><img src="/assets/editorial.jpg" alt="Casual menswear style reference"></div><div><span class="eyebrow">EVOVO / EVOVOFINDS</span><h1>A home for<br>your next find.</h1><p>EVOVO is the site. EVOVOFinds is the seller name you'll see on eBay. We wanted a place to share a little clothing inspiration, with a clear route to the actual listings.</p><p>The style notes here are references, not a product catalog. For what's available, see the photos and details on our eBay seller page.</p>${ebayButton()}<a class="text-link" href="/help/">How to shop ${arrow}</a></div></section>`;
}
function help() {
  return `<article class="help-layout"><span class="eyebrow">GOOD TO KNOW</span><h1>Shopping,<br>made clearer.</h1><section class="help-section"><h2>Where do I buy?</h2><p>Go to EVOVOFinds on eBay to see the current listings. Select your item and complete checkout there. You don't need a separate EVOVO account, and this site doesn't collect payment information.</p>${ebayButton('Checkout on eBay')}</section><section class="help-section"><h2>Are these items for sale?</h2><p>The photographs in our style notes are inspiration only. They are not the seller's inventory. The actual item photos, prices, sizes, condition, and availability are on eBay.</p></section><section id="shipping" class="help-section"><h2>Shipping & returns</h2><p>Check the individual eBay listing for delivery estimates, shipping prices, and return terms. These can vary by item. Read the listing before you purchase.</p></section><section id="contact" class="help-section"><h2>A question about an item?</h2><p>Visit our seller page and use eBay's contact option to message EVOVOFinds. Keeping the conversation on eBay puts it alongside your listing or order.</p>${ebayButton('Visit the seller page', 'text-link')}</section><section id="privacy" class="help-section"><h2>Your saved ideas & preferences</h2><p>Your saved style ideas and tap-feedback preference are stored on this device. Board links contain only the public style-reference IDs you choose to share; opening one never replaces your own saved ideas. There is no EVOVO account, tracking analytics, payment collection, or newsletter signup. Fonts and photographs are served with this site. If you follow a link to eBay, eBay's own policies apply there.</p><button class="text-link" id="clear-data">Clear saved ideas & preferences</button></section><section class="help-section"><h2>A little tap feedback</h2><p>Supported phones can give a very short vibration when you tap a control. Use the tap-feedback switch in the footer to turn it off. iPhone Safari doesn't support web vibration, so you will see a small visual press instead. Reduced-motion settings are respected.</p></section></article>`;
}
function notFound() {
  document.title = 'Page not found — EVOVO';
  $('#main').innerHTML = `<section class="section empty error-state">${stateIllustration()}<span class="eyebrow">EVOVO / 404</span><h1>A different direction.</h1><p>We couldn't find that page.</p><a href="/" class="pill">Back to EVOVO ${arrow}</a></section>`;
}
function renderPage() {
  if (path === '/') $('#main').innerHTML = home();
  else if (isCatalog) {
    const slug = path.split('/')[2];
    const category = categories.find(c => c.toLowerCase() === slug) || 'All';
    if (slug && !categories.some(c => c.toLowerCase() === slug)) return notFound();
    $('#main').innerHTML = catalogPage(category, isSavedPage);
    document.title = (isSavedPage ? 'Saved ideas' : category === 'All' ? 'Style ideas' : category) + ' — EVOVO';
    filterProducts();
  } else if (path.startsWith('/products/')) {
    const p = products.find(p => p.id === path.split('/')[2]);
    if (!p) return notFound();
    $('#main').innerHTML = detail(p);
    document.title = p.name + ' — EVOVO';
  } else if (path === '/about') { $('#main').innerHTML = about(); document.title = 'About EVOVOFinds — EVOVO'; }
  else if (path === '/help') { $('#main').innerHTML = help(); document.title = 'How to shop — EVOVO'; }
  else if (path === '/checkout') location.replace(EBAY_STORE_URL);
  else notFound();
  document.querySelectorAll('.desktop-nav a').forEach(a => {
    if (a.getAttribute('href').replace(/\/$/, '') === path) a.setAttribute('aria-current', 'page');
  });
}
function updateSaved(write = true) {
  const focusedSave = document.activeElement?.closest('#collection-grid [data-save]');
  const focusedIndex = focusedSave ? [...document.querySelectorAll('#collection-grid [data-save]')].indexOf(focusedSave) : -1;
  let stored = true;
  if (write) {
    try { localStorage.setItem('evovo.saved', JSON.stringify(saved)); } catch { stored = false; }
  }
  document.querySelectorAll('[data-save]').forEach(button => {
    const yes = saved.includes(button.dataset.save);
    const p = products.find(p => p.id === button.dataset.save);
    button.setAttribute('aria-pressed', String(yes));
    if (button.classList.contains('save-button')) button.setAttribute('aria-label', `${yes ? 'Unsave' : 'Save'} ${p.name}`);
    else button.querySelector('span').textContent = yes ? 'Saved to your ideas' : 'Save this idea';
  });
  updateSavedCounts();
  if (isSavedPage) {
    filterProducts();
    if (focusedSave) {
      const controls = [...document.querySelectorAll('#collection-grid [data-save]')];
      const next = controls.find(button => button.dataset.save === focusedSave.dataset.save) || controls[Math.min(focusedIndex, controls.length - 1)] || $('#collection-grid .empty .pill');
      next?.focus({preventScroll:true});
    }
  }
  return stored;
}

function searchResults() {
  const q = $('#search-input').value.trim().toLowerCase();
  const matches = products.filter(p => !q || matchesProduct(p, q));
  const list = matches.slice(0,5);
  $('#search-results').innerHTML = `<p class="search-results-label">${q ? 'STYLE IDEAS' : 'EXPLORE AN IDEA'}</p>` + (list.length ? list.map(p => `<a class="search-result" href="${productURL(p)}"><img src="${asset(p)}" alt=""><div><strong>${p.name}</strong><p>${p.category} · Style reference</p></div>${arrow}</a>`).join('') : `<div class="search-empty">${stateIllustration()}<p>No ideas found yet. Try shirts, hoodies, pants, or socks.</p></div>`) + `<a class="search-view-all" href="/shop/${q ? '?q=' + encodeURIComponent($('#search-input').value.trim()) : ''}">${q ? 'See all matching ideas' : 'Explore all ' + products.length + ' ideas'} ${arrow}</a>`;
}
document.addEventListener('click', event => {
  const button = event.target.closest('button');
  if (!button) return;
  if (button.dataset.close) document.getElementById(button.dataset.close).close();
  if (button.id === 'search-open') { searchResults(); $('#search-dialog').showModal(); }
  if (button.id === 'menu-open') $('#menu-dialog').showModal();
  if (button.dataset.stageMove) setShowcase(showcaseIndex + Number(button.dataset.stageMove));
  if (button.dataset.stageIndex !== undefined) setShowcase(Number(button.dataset.stageIndex));
  if (button.hasAttribute('data-dismiss-toast')) {
    $('#toast').hidden = true;
    if (isSavedPage) document.querySelector('#collection-grid .save-button, #collection-grid .empty .pill')?.focus({preventScroll:true});
    else document.querySelector('#clear-data, .detail-save, .stage-save')?.focus({preventScroll:true});
  }
  if (button.hasAttribute('data-copy-board')) copyBoardLink();
  if (button.hasAttribute('data-import-board')) {
    saved = [...new Set([...saved, ...boardIds()])];
    const stored = updateSaved();
    toast(stored ? 'Shared ideas added to your board' : 'Ideas saved for this visit; browser storage is unavailable');
  }
  if (button.hasAttribute('data-reset-filters')) {
    query = ''; if (isSavedPage) currentCategory = 'All'; sort = 'editorial';
    saveCatalogState(true); syncCatalogUI();
    $('#collection-query').focus({preventScroll:true});
  }
  if (button.hasAttribute('data-clear-search')) {
    query = ''; saveCatalogState(true); syncCatalogUI();
    $('#collection-query').focus({preventScroll:true});
  }
  if (button.dataset.undoSave) {
    if (!saved.includes(button.dataset.undoSave)) saved.push(button.dataset.undoSave);
    const stored = updateSaved();
    toast(stored ? 'Idea restored' : 'Idea restored for this visit; browser storage is unavailable');
    document.querySelector(`[data-save="${button.dataset.undoSave}"]`)?.focus({preventScroll:true});
  }
  if (button.dataset.save) {
    const id = button.dataset.save;
    const wasSaved = saved.includes(id);
    saved = wasSaved ? saved.filter(x => x !== id) : [...saved, id];
    const stored = updateSaved();
    toast(wasSaved ? 'Removed from saved ideas' : stored ? 'Saved for another day' : 'Saved for this visit; browser storage is unavailable', wasSaved ? id : '');
  }
  if (button.id === 'clear-data') {
    $('#clear-summary').textContent = saved.length ? `You have ${saved.length} saved ${saved.length === 1 ? 'idea' : 'ideas'} on this device. Clearing also resets your tap-feedback preference.` : 'This resets your tap-feedback preference. There are no saved ideas on this device.';
    $('#clear-dialog').showModal();
  }
  if (button.hasAttribute('data-confirm-clear')) {
    clearSnapshot = {saved: [...saved], preferences: {}};
    try { for (const key of ['evovo.bag', 'evovo.haptics']) clearSnapshot.preferences[key] = localStorage.getItem(key); } catch {}
    saved = [];
    let cleared = true;
    try { ['evovo.saved', 'evovo.bag', 'evovo.haptics'].forEach(key => localStorage.removeItem(key)); } catch { cleared = false; }
    const stored = updateSaved();
    document.dispatchEvent(new Event('evovo:preferences-reset'));
    $('#clear-dialog').close();
    toast(cleared && stored ? 'Saved ideas and preferences cleared on this device' : 'Cleared for this visit; browser storage is unavailable', '', true);
  }
  if (button.hasAttribute('data-undo-clear') && clearSnapshot) {
    saved = [...new Set([...readSaved(), ...clearSnapshot.saved])];
    let stored = updateSaved();
    try {
      for (const [key, value] of Object.entries(clearSnapshot.preferences)) {
        if (value !== null) localStorage.setItem(key, value);
      }
    } catch { stored = false; }
    document.dispatchEvent(new CustomEvent('evovo:preferences-reset', {detail: {feedbackEnabled: clearSnapshot.preferences['evovo.haptics'] !== 'off'}}));
    clearSnapshot = null;
    toast(stored ? 'Your saved ideas and preferences are restored' : 'Ideas restored for this visit; browser storage is unavailable');
    $('#clear-data')?.focus({preventScroll:true});
  }
});
document.addEventListener('keydown', event => {
  if (!event.target.closest?.('[data-style-stage]') || event.altKey || event.ctrlKey || event.metaKey) return;
  if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
    event.preventDefault();
    setShowcase(showcaseIndex + (event.key === 'ArrowRight' ? 1 : -1));
  }
});
document.addEventListener('change', event => {
  if (event.target.id === 'product-sort') { sort = event.target.value; saveCatalogState(true); filterProducts(); }
});
document.addEventListener('input', event => {
  if (event.target.id === 'search-input') searchResults();
  if (event.target.id === 'collection-query') {
    query = event.target.value;
    saveCatalogState();
    filterProducts();
  }
});
document.addEventListener('submit', event => {
  if (event.target.id === 'collection-search') { event.preventDefault(); query = $('#collection-query').value; saveCatalogState(); filterProducts(); }
});
document.querySelectorAll('dialog').forEach(dialog => dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const rect = dialog.getBoundingClientRect();
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
}));
window.addEventListener('storage', event => { if (event.key === 'evovo.saved' || event.key === null) { saved = readSaved(); updateSaved(false); } });
function syncCatalogUI() {
  if (!isCatalog) return;
  $('#collection-query').value = query;
  $('#product-sort').value = sort;
  document.querySelectorAll('[data-category-link]').forEach(link => {
    const active = link.dataset.categoryLink === currentCategory;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'page'); else link.removeAttribute('aria-current');
    link.href = categoryURL(link.dataset.categoryLink);
  });
  filterProducts();
}
window.addEventListener('popstate', () => { readCatalogState(); syncCatalogUI(); });
renderPage();
updateSavedCounts();
if (isCatalog && /^#idea-[a-z-]+$/.test(location.hash)) {
  const idea = document.getElementById(location.hash.slice(1));
  if (idea) requestAnimationFrame(() => {
    idea.querySelector('.product-image').focus({preventScroll:true});
    idea.scrollIntoView({block:'center', behavior:'instant'});
  });
}
document.querySelectorAll('[data-dock]').forEach(link => {
  if ((link.dataset.dock === 'saved' && isSavedPage) || (link.dataset.dock === 'ideas' && (path.startsWith('/shop') || path.startsWith('/products')))) link.setAttribute('aria-current', 'page');
});
// Render first so dynamically generated sections are available to the motion layer.
$('#main').dataset.ready = 'true';
$('#main').setAttribute('aria-busy', 'false');
document.dispatchEvent(new Event('evovo:content-ready'));
