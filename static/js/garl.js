/**
 * GARL — Global Academic Research Library
 * Core JavaScript v2
 */

'use strict';

// ══════════════════════════════════════════════════════ NAVBAR HIDE/SHOW ══
(function () {
  const navbar  = document.getElementById('garlNavbar');
  const topbar  = document.getElementById('garlTopbar');
  if (!navbar) return;

  let lastY    = window.scrollY;
  let ticking  = false;
  const THRESH = 70;  // px before hide-on-scroll activates

  function onScroll() {
    const y = window.scrollY;

    // Shadow enhancement when scrolled
    navbar.classList.toggle('nav-scrolled', y > 8);

    if (y > THRESH) {
      if (y > lastY) {
        // Scrolling DOWN — hide navbar (and topbar)
        navbar.classList.add('nav-hidden');
        topbar?.classList.add('hide');
      } else {
        // Scrolling UP — show navbar
        navbar.classList.remove('nav-hidden');
        topbar?.classList.remove('hide');
      }
    } else {
      // Near top — always show both
      navbar.classList.remove('nav-hidden');
      topbar?.classList.remove('hide');
    }

    lastY   = y;
    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) {
      requestAnimationFrame(onScroll);
      ticking = true;
    }
  }, { passive: true });
})();

// ══════════════════════════════════════════════════ ADMIN SIDEBAR TOGGLE ══
(function () {
  const btn     = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('adminSidebar');
  if (!btn || !sidebar) return;
  btn.addEventListener('click', () => sidebar.classList.toggle('garl-admin-sidebar--open'));
})();

// ═══════════════════════════════════════════════════════ THEME TOGGLE ══
(function () {
  const btn = document.getElementById('themeToggleBtn');
  if (!btn) return;
  btn.addEventListener('click', function () {
    fetch('/accounts/theme/toggle/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/json' },
    })
      .then(r => r.json())
      .then(data => {
        document.documentElement.setAttribute('data-bs-theme', data.theme);
        const icon = btn.querySelector('i');
        if (icon) icon.className = data.theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
      })
      .catch(console.error);
  });
})();

// ═══════════════════════════════════════════════════ BOOKMARK TOGGLE ══
document.addEventListener('click', function (e) {
  const btn = e.target.closest('[data-bookmark]');
  if (!btn) return;
  e.preventDefault();
  const contentType = btn.dataset.contentType;
  const objectId    = btn.dataset.objectId;
  if (!contentType || !objectId) return;
  fetch('/bookmark/toggle/', {
    method: 'POST',
    headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `content_type=${contentType}&object_id=${objectId}`,
  })
    .then(r => r.json())
    .then(data => {
      const icon = btn.querySelector('i');
      if (icon) icon.className = data.bookmarked ? 'bi bi-bookmark-fill text-warning' : 'bi bi-bookmark';
    })
    .catch(console.error);
});

// ══════════════════════════════════════════════ LIKE TOGGLE (INNOVATION) ══
document.addEventListener('click', function (e) {
  const btn = e.target.closest('[data-like-project]');
  if (!btn) return;
  e.preventDefault();
  const pk = btn.dataset.likeProject;
  fetch(`/innovation/projects/${pk}/like/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCsrfToken() },
  })
    .then(r => r.json())
    .then(data => {
      const icon = btn.querySelector('i');
      if (icon) icon.className = data.liked ? 'bi bi-hand-thumbs-up-fill text-primary' : 'bi bi-hand-thumbs-up';
      const countEl = document.getElementById(`like-count-${pk}`);
      if (countEl) countEl.textContent = data.count;
    })
    .catch(console.error);
});

// ════════════════════════════════════════════════ AUTO-DISMISS ALERTS ══
document.querySelectorAll('.alert-dismissible').forEach(alert => {
  setTimeout(() => {
    if (typeof bootstrap !== 'undefined') {
      try { new bootstrap.Alert(alert).close(); } catch {}
    }
  }, 7000);
});

// ════════════════════════════════════════════ SMOOTH SCROLL TO ANCHOR ══
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', function (e) {
    const href = this.getAttribute('href');
    if (href === '#' || href === '#!') return;
    const target = document.querySelector(href);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ══════════════════════════════════════════════ CONFIRM DANGEROUS FORMS ══
document.addEventListener('submit', function (e) {
  const msg = e.target.dataset.confirm;
  if (msg && !window.confirm(msg)) e.preventDefault();
});

// ═══════════════════════════════════════════════════ CSRF TOKEN HELPER ══
function getCsrfToken() {
  const el = document.querySelector('[name=csrfmiddlewaretoken]');
  if (el) return el.value;
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  return m ? m[1] : '';
}
