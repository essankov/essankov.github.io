// Safe localStorage wrapper (Brave Shields can block storage access)
function getStorage(key) {
  try { return localStorage.getItem(key); } catch (e) { return null; }
}
function setStorage(key, val) {
  try { localStorage.setItem(key, val); } catch (e) {}
}

function getPreferredTheme() {
  return getStorage('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}

// Apply theme immediately to prevent flash
document.documentElement.setAttribute('data-theme', getPreferredTheme());

document.addEventListener('DOMContentLoaded', function () {
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.style.colorScheme = theme;
    var btn = document.getElementById('theme-toggle');
    if (!btn) return;
    var icon = btn.querySelector('.icon');
    var label = btn.querySelector('.label');
    if (icon) icon.textContent = theme === 'dark' ? '\u2600' : '\u263E';
    if (label) label.textContent = theme === 'dark' ? 'Light' : 'Dark';
  }

  applyTheme(getPreferredTheme());

  var themeBtn = document.getElementById('theme-toggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var now = document.documentElement.getAttribute('data-theme') || 'light';
      var next = now === 'dark' ? 'light' : 'dark';
      setStorage('theme', next);
      applyTheme(next);
    });
  }

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!getStorage('theme')) {
      applyTheme(e.matches ? 'dark' : 'light');
    }
  });

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
