(function () {
  var months = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  fetch('posts.json')
    .then(function (res) {
      if (!res.ok) throw new Error('Failed to load posts');
      return res.json();
    })
    .then(function (posts) {
      function render() {
        var groups = {};
        var groupOrder = [];
        posts.forEach(function (p) {
          var d = new Date(p.date + 'T00:00:00');
          var key = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
          var label = months[d.getMonth()] + ' ' + d.getFullYear();
          if (!groups[key]) {
            groups[key] = { label: label, posts: [] };
            groupOrder.push(key);
          }
          groups[key].posts.push(p);
        });

        var html = '';
        groupOrder.forEach(function (key) {
          var g = groups[key];
          html += '<div class="post-group">';
          html += '<div class="post-group-label">' + g.label + '</div>';
          html += '<ul class="post-list">';
          g.posts.forEach(function (p) {
            html += '<li class="post-item">';
            html += '<a href="post.html?slug=' + encodeURIComponent(p.slug) + '">' + esc(p.title) + '</a>';
            html += '<span class="post-date">' + esc(p.dateDisplay) + '</span>';
            html += '</li>';
          });
          html += '</ul></div>';
        });

        if (!html) {
          html = '<p style="color:var(--text-secondary)">No posts found.</p>';
        }

        document.getElementById('posts-section').innerHTML = html;
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', render);
      } else {
        render();
      }
    })
    .catch(function () {
      function showError() {
        document.getElementById('posts-section').innerHTML = '<p>Failed to load posts.</p>';
      }
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', showError);
      } else {
        showError();
      }
    });
})();
