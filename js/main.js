(function () {
  // Theme: check saved preference, then system preference
  function getPreferredTheme() {
    var saved = localStorage.getItem('theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    var btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.querySelector('.icon').textContent = theme === 'dark' ? '\u2600' : '\u263E';
      btn.querySelector('.label').textContent = theme === 'dark' ? 'Light' : 'Dark';
    }
  }

  // Apply theme immediately to prevent flash
  applyTheme(getPreferredTheme());

  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!localStorage.getItem('theme')) {
      applyTheme(e.matches ? 'dark' : 'light');
    }
  });

  document.addEventListener('DOMContentLoaded', function () {
    // Theme toggle
    var themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
      applyTheme(getPreferredTheme());
      themeBtn.addEventListener('click', function () {
        var current = document.documentElement.getAttribute('data-theme') || 'light';
        var next = current === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', next);
        applyTheme(next);
      });
    }

    // Mobile menu
    var toggle = document.getElementById('mobile-menu-toggle');
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebar-overlay');

    if (toggle && sidebar && overlay) {
      toggle.addEventListener('click', function () {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
        document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : '';
      });
      overlay.addEventListener('click', function () {
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
        document.body.style.overflow = '';
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
          sidebar.classList.remove('open');
          overlay.classList.remove('open');
          document.body.style.overflow = '';
        }
      });
    }
  });
})();
