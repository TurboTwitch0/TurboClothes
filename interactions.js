// Progressive touch feedback. Unsupported browsers keep normal links and buttons.
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const coarsePointer = window.matchMedia('(any-pointer: coarse)');
const preferenceKey = 'evovo.haptics';
const supportsVibration = typeof navigator.vibrate === 'function';
let feedbackEnabled = true;
let lastPulse = -Infinity;
try {
  feedbackEnabled = localStorage.getItem(preferenceKey) !== 'off';
} catch {
  // Storage can be unavailable in private or restricted browsing.
}

function canOfferFeedback() {
  return supportsVibration && coarsePointer.matches;
}

function updateToggle(button) {
  const available = canOfferFeedback();
  const enabled = available && feedbackEnabled && !reducedMotion.matches;
  button.hidden = !available;
  button.disabled = reducedMotion.matches;
  button.setAttribute('aria-pressed', String(enabled));
  const label = enabled ? 'Tap feedback on' : 'Tap feedback off';
  if (button.textContent !== label) button.textContent = label;
  if (reducedMotion.matches) {
    button.title = 'Tap feedback is off while reduced motion is enabled.';
  } else {
    button.removeAttribute('title');
  }
}

function updateToggles() {
  document.querySelectorAll('[data-haptics-toggle]').forEach(updateToggle);
}

function pulse() {
  if (!canOfferFeedback() || !feedbackEnabled || reducedMotion.matches || document.visibilityState !== 'visible') return;
  const now = performance.now();
  if (now - lastPulse < 100) return;
  lastPulse = now;
  try {
    // One gentle pulse. Browser support and system settings determine the result.
    navigator.vibrate(7);
  } catch {
    // Vibration is an enhancement; it never blocks navigation or actions.
  }
}

function actionFrom(target) {
  if (!(target instanceof Element)) return null;
  const action = target.closest('button, a[href], [data-haptic]');
  if (!action || action.disabled || action.getAttribute('aria-disabled') === 'true' || action.closest('[inert]')) return null;
  return action;
}

document.addEventListener('click', event => {
  if (!event.isTrusted) return;
  const action = actionFrom(event.target);
  if (!action) return;
  if (action.matches('[data-haptics-toggle]')) {
    if (!canOfferFeedback() || reducedMotion.matches) return;
    feedbackEnabled = !feedbackEnabled;
    try {
      localStorage.setItem(preferenceKey, feedbackEnabled ? 'on' : 'off');
    } catch {
      // Keep this visit's preference even when saving is unavailable.
    }
    updateToggles();
  }
  pulse();
}, { passive: true });

const pressed = new Map();
function clearPressed(pointerId) {
  const target = pressed.get(pointerId);
  if (!target) return;
  pressed.delete(pointerId);
  // A second finger can still be pressing the same control.
  if (![...pressed.values()].includes(target)) target.classList.remove('is-pressed');
}
function clearAllPressed() {
  for (const target of pressed.values()) target.classList.remove('is-pressed');
  pressed.clear();
}

document.addEventListener('pointerdown', event => {
  if (reducedMotion.matches || event.button !== 0) return;
  const action = actionFrom(event.target);
  if (!action || !action.matches('button, .pill, .icon-button, [data-haptic]')) return;
  pressed.set(event.pointerId, action);
  action.classList.add('is-pressed');
}, { passive: true });
window.addEventListener('pointerup', event => clearPressed(event.pointerId), { passive: true });
window.addEventListener('pointercancel', event => clearPressed(event.pointerId), { passive: true });
window.addEventListener('blur', clearAllPressed);
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState !== 'visible') clearAllPressed();
});

// Content stays visible if JavaScript or IntersectionObserver is unavailable.
let revealObserver;
const waitingForReveal = new Set();
if ('IntersectionObserver' in window) {
  revealObserver = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add('is-visible');
      revealObserver.unobserve(entry.target);
      waitingForReveal.delete(entry.target);
    }
  }, { threshold: 0.08, rootMargin: '0px 0px 24px 0px' });
}

function prepareReveal(element) {
  if (element.classList.contains('is-visible') || waitingForReveal.has(element)) return;
  if (reducedMotion.matches || !revealObserver) {
    element.classList.add('is-visible');
  } else {
    waitingForReveal.add(element);
    revealObserver.observe(element);
  }
}
function prepareContent(root) {
  if (root instanceof Element) {
    if (root.matches('[data-reveal]')) prepareReveal(root);
    if (root.matches('[data-haptics-toggle]')) updateToggle(root);
  }
  root.querySelectorAll?.('[data-reveal]').forEach(prepareReveal);
  root.querySelectorAll?.('[data-haptics-toggle]').forEach(updateToggle);
}
function updateMotionPreference() {
  clearAllPressed();
  if (reducedMotion.matches) {
    document.documentElement.classList.remove('motion-ready');
    for (const element of waitingForReveal) {
      element.classList.add('is-visible');
      revealObserver?.unobserve(element);
    }
    waitingForReveal.clear();
  } else if (revealObserver) {
    document.documentElement.classList.add('motion-ready');
  }
  updateToggles();
}

// The importing application can render its first page before this microtask runs.
queueMicrotask(() => {
  prepareContent(document);
  updateMotionPreference();
  new MutationObserver(records => {
    for (const record of records) {
      for (const node of record.addedNodes) {
        if (node instanceof Element) prepareContent(node);
      }
    }
    for (const element of waitingForReveal) {
      if (element.isConnected) continue;
      revealObserver?.unobserve(element);
      waitingForReveal.delete(element);
    }
  }).observe(document.body, { childList: true, subtree: true });
});

reducedMotion.addEventListener('change', updateMotionPreference);
coarsePointer.addEventListener('change', updateToggles);
document.addEventListener('evovo:preferences-reset', event => {
  feedbackEnabled = event.detail?.feedbackEnabled ?? true;
  updateToggles();
});
window.addEventListener('storage', event => {
  if (event.key !== preferenceKey) return;
  feedbackEnabled = event.newValue !== 'off';
  updateToggles();
});
