(function () {
  var root = document.documentElement;

  /* ---------- Theme ---------- */
  // The saved theme is applied by an inline script in <head> so the page never flashes.
  var sun = '<circle cx="12" cy="12" r="4.5"/><line x1="12" y1="2" x2="12" y2="4.5"/><line x1="12" y1="19.5" x2="12" y2="22"/><line x1="2" y1="12" x2="4.5" y2="12"/><line x1="19.5" y1="12" x2="22" y2="12"/><line x1="4.9" y1="4.9" x2="6.7" y2="6.7"/><line x1="17.3" y1="17.3" x2="19.1" y2="19.1"/><line x1="4.9" y1="19.1" x2="6.7" y2="17.3"/><line x1="17.3" y1="6.7" x2="19.1" y2="4.9"/>';
  var moon = '<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/>';
  var darkQuery = window.matchMedia('(prefers-color-scheme: dark)');
  var themeIcon = document.getElementById('theme-icon');
  function effectiveTheme() {
    return root.getAttribute('data-theme') || (darkQuery.matches ? 'dark' : 'light');
  }
  function paintThemeIcon() {
    if (themeIcon) themeIcon.innerHTML = effectiveTheme() === 'dark' ? sun : moon;
  }
  paintThemeIcon();
  if (darkQuery.addEventListener) darkQuery.addEventListener('change', paintThemeIcon);
  var themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) themeToggle.addEventListener('click', function () {
    var next = effectiveTheme() === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('ctv-theme', next); } catch (e) {}
    paintThemeIcon();
  });

  /* ---------- Language ---------- */
  // Each language is its own static page (/ and /en/). Remember the visitor's choice so the
  // Spanish pages can send them back to English on their next visit.
  document.querySelectorAll('a.lang-switch[hreflang]').forEach(function (a) {
    a.addEventListener('click', function () {
      try { localStorage.setItem('ctv-lang', a.getAttribute('hreflang')); } catch (e) {}
      if (location.hash) a.setAttribute('href', a.getAttribute('href').split('#')[0] + location.hash);
    });
  });

  /* ---------- Year ---------- */
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
