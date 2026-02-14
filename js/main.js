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

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;
  var icon = btn.querySelector('.icon');
  var label = btn.querySelector('.label');
  if (icon) icon.textContent = theme === 'dark' ? '\u2600' : '\u263E';
  if (label) label.textContent = theme === 'dark' ? 'Light' : 'Dark';
}

// Update button UI to match theme already set by theme-init.js
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
