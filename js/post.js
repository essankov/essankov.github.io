// Toggle highlight.js theme based on data-theme
function updateHljsTheme() {
  var theme = document.documentElement.getAttribute('data-theme') || 'light';
  var light = document.getElementById('hljs-light');
  var dark = document.getElementById('hljs-dark');
  if (light) light.disabled = (theme === 'dark');
  if (dark) dark.disabled = (theme !== 'dark');
}
updateHljsTheme();
new MutationObserver(updateHljsTheme).observe(document.documentElement, {
  attributes: true, attributeFilter: ['data-theme']
});

(function () {
  var params = new URLSearchParams(window.location.search);
  var slug = params.get('slug');

  if (!slug) {
    document.addEventListener('DOMContentLoaded', function () {
      document.getElementById('post-title').textContent = 'Post not found';
      document.getElementById('post-content').innerHTML = '<p>No post specified.</p>';
    });
    return;
  }

  slug = slug.replace(/[^a-zA-Z0-9\-_]/g, '');

  fetch('posts/' + slug + '.md')
    .then(function (res) {
      if (!res.ok) throw new Error('Not found');
      return res.text();
    })
    .then(function (text) {
      var title = slug;
      var date = '';
      var body = text;

      var match = text.match(/^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/);
      if (match) {
        var fm = match[1];
        body = match[2];

        var t = fm.match(/^title:\s*(.+)$/m);
        if (t) title = t[1].trim();

        var d = fm.match(/^date:\s*(.+)$/m);
        if (d) date = d[1].trim();

        var dirVal = fm.match(/^dir:\s*(.+)$/m);
        var langVal = fm.match(/^lang:\s*(.+)$/m);

        if (dirVal) document.documentElement.setAttribute('dir', dirVal[1].trim());
        if (langVal) document.documentElement.setAttribute('lang', langVal[1].trim());
      }

      // Calculate reading time
      var wordCount = body.trim().split(/\s+/).length;
      var readingMin = Math.max(1, Math.round(wordCount / 200));

      function render() {
        document.getElementById('post-title').textContent = title;
        document.getElementById('post-date').textContent = date;
        document.title = title + ' \u2014 Essa';

        // Update OG tags dynamically (for JS-based sharing tools)
        var ogTitle = document.querySelector('meta[property="og:title"]');
        var ogDesc = document.querySelector('meta[property="og:description"]');
        if (ogTitle) ogTitle.setAttribute('content', title + ' \u2014 Essa');
        if (ogDesc) ogDesc.setAttribute('content', body.substring(0, 160).replace(/[#*_\n]/g, ''));

        // Reading time
        var rtEl = document.getElementById('reading-time');
        if (document.documentElement.getAttribute('lang') === 'ar') {
          rtEl.textContent = readingMin + ' \u062F\u0642\u064A\u0642\u0629 \u0642\u0631\u0627\u0621\u0629';
        } else {
          rtEl.textContent = readingMin + ' min read';
        }
        rtEl.style.display = '';

        // Sanitize and render markdown
        var rawHtml = marked.parse(body);
        document.getElementById('post-content').innerHTML = DOMPurify.sanitize(rawHtml);

        // Syntax highlighting
        document.querySelectorAll('.post-content pre code').forEach(function (block) {
          hljs.highlightElement(block);
        });

        if (document.documentElement.getAttribute('lang') === 'ar') {
          document.getElementById('back-link').textContent = '\u062C\u0645\u064A\u0639 \u0627\u0644\u0645\u0642\u0627\u0644\u0627\u062A';
        }
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', render);
      } else {
        render();
      }
    })
    .catch(function () {
      function showError() {
        document.getElementById('post-title').textContent = 'Post not found';
        document.getElementById('post-content').innerHTML = '<p>The requested post could not be loaded.</p>';
      }
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', showError);
      } else {
        showError();
      }
    });
})();
