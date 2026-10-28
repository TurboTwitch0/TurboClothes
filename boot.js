// Keep a useful route to the shop when the application module cannot start.
(() => {
  const moduleFiles = /\/(?:app|catalog|interactions)\.js$/;
  let main;
  let timer;
  let complete = false;
  let failureRequested = false;

  function applicationFile(source) {
    if (!source) return false;
    try {
      const url = new URL(source, location.href);
      return url.origin === location.origin && moduleFiles.test(url.pathname);
    } catch { return false; }
  }

  function finish() {
    complete = true;
    clearTimeout(timer);
    window.removeEventListener('error', onError, true);
    document.removeEventListener('evovo:content-ready', finish);
    if (main?.dataset.ready === 'true') {
      main.classList.remove('app-loading', 'is-error');
      main.setAttribute('aria-busy', 'false');
    }
  }

  function showFailure() {
    if (complete || main?.dataset.ready === 'true') {
      finish();
      return;
    }
    failureRequested = true;
    if (!main) return;
    clearTimeout(timer);
    main.classList.add('is-error');
    main.removeAttribute('aria-busy');
    const message = main.querySelector('[data-boot-message]');
    if (message) message.textContent = 'The style ideas couldn’t load. Try reloading, or browse our eBay page.';
    const reload = main.querySelector('[data-reload-app]');
    if (reload) reload.hidden = false;
  }

  function onError(event) {
    if (complete) return;
    const target = event.target;
    // Resource error events from images, fonts, and the stylesheet are unrelated.
    const moduleResourceFailed = target instanceof HTMLScriptElement
      && target.type === 'module'
      && applicationFile(target.src);
    const moduleExecutionFailed = event instanceof ErrorEvent
      && applicationFile(event.filename);
    if (moduleResourceFailed || moduleExecutionFailed) showFailure();
  }

  function start() {
    main = document.getElementById('main');
    if (!main || complete || main.dataset.ready === 'true') {
      finish();
      return;
    }
    main.querySelector('[data-reload-app]')?.addEventListener('click', () => location.reload());
    if (failureRequested) showFailure();
    else timer = setTimeout(showFailure, 6500);
  }

  window.addEventListener('error', onError, true);
  document.addEventListener('evovo:content-ready', finish);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once: true});
  else start();
})();
