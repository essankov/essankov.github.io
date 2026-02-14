#!/usr/bin/env python3
"""Generate posts.json, per-post HTML pages, and feed.xml from markdown files."""
import json, os, re, html
from datetime import datetime, timezone

import markdown

SITE_URL = 'https://essankov.github.io'
POSTS_DIR = os.path.join(os.path.dirname(__file__), 'posts')
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), 'posts.json')
OUTPUT_RSS = os.path.join(os.path.dirname(__file__), 'feed.xml')

md = markdown.Markdown(extensions=['fenced_code', 'tables'])


def parse_frontmatter(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n([\s\S]*)$', text, re.DOTALL)
    if not m:
        return None, text
    fm_text = m.group(1)
    body = m.group(2)
    fm = {}
    for line in fm_text.strip().splitlines():
        colon = line.find(':')
        if colon != -1:
            fm[line[:colon].strip()] = line[colon + 1:].strip()
    return fm, body


def reading_time(text):
    words = len(text.split())
    return max(1, round(words / 200))


POST_TEMPLATE = '''\
<!DOCTYPE html>
<html lang="{lang}" dir="{dir}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self'; connect-src 'self'; base-uri 'self'; form-action 'none'; upgrade-insecure-requests">
  <meta name="referrer" content="no-referrer-when-downgrade">
  <title>{title_escaped} — Essa</title>
  <meta name="description" content="{description_escaped}">
  <meta property="og:title" content="{title_escaped} — Essa">
  <meta property="og:description" content="{description_escaped}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{post_url}">
  <meta name="twitter:card" content="summary">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="alternate" type="application/rss+xml" title="Essa" href="../feed.xml">
  <link rel="stylesheet" href="../css/style.css">
  <script src="../js/main.js"></script>
</head>
<body>

  <nav class="topnav">
    <div class="topnav-logo"><a href="../index.html">Essa</a></div>
    <ul class="topnav-links">
      <li><a href="../blog.html">Blog</a></li>
      <li><a href="../about.html">About</a></li>
      <li>
        <button class="theme-toggle" id="theme-toggle" aria-label="Toggle theme">
          <span class="icon">&#9790;</span>
          <span class="label">Dark</span>
        </button>
      </li>
    </ul>
  </nav>

  <main class="main">
    <div class="content">

      <a href="../blog.html" class="back-link">{back_text}</a>

      <header class="post-header">
        <h1>{title}</h1>
        <div class="post-meta">
          <span>{date_display}</span>
          <span class="reading-time">{reading_time_text}</span>
        </div>
      </header>

      <article class="post-content">{content}</article>

      <footer class="footer">
        <p>&copy; 2026 Essa. All rights reserved.</p>
      </footer>

    </div>
  </main>

</body>
</html>
'''


def generate_post_html(slug, fm, body_md):
    md.reset()
    content_html = md.convert(body_md)

    lang = fm.get('lang', 'en')
    direction = fm.get('dir', 'ltr')
    title = fm.get('title', slug)
    date_raw = fm.get('date', '')
    is_arabic = lang == 'ar'

    try:
        dt = datetime.strptime(date_raw, '%B %d, %Y')
        date_display = dt.strftime('%b %-d, %Y')
    except ValueError:
        date_display = date_raw

    rt = reading_time(body_md)
    reading_time_text = f'{rt} دقيقة قراءة' if is_arabic else f'{rt} min read'
    back_text = 'جميع المقالات' if is_arabic else 'All posts'

    description = re.sub(r'[#*_\n]', '', body_md[:160]).strip()

    post_url = f'{SITE_URL}/posts/{slug}.html'

    return POST_TEMPLATE.format(
        lang=html.escape(lang),
        dir=html.escape(direction),
        title_escaped=html.escape(title),
        title=html.escape(title),
        description_escaped=html.escape(description),
        post_url=html.escape(post_url),
        back_text=back_text,
        date_display=html.escape(date_display),
        reading_time_text=reading_time_text,
        content=content_html,
    )


def generate_rss(posts):
    now = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    items = []
    for p in posts:
        dt = datetime.strptime(p['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        pub_date = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        url = f'{SITE_URL}/posts/{p["slug"]}.html'
        items.append(
            f'    <item>\n'
            f'      <title>{html.escape(p["title"])}</title>\n'
            f'      <link>{html.escape(url)}</link>\n'
            f'      <guid isPermaLink="true">{html.escape(url)}</guid>\n'
            f'      <pubDate>{pub_date}</pubDate>\n'
            f'      <description>{html.escape(p.get("description", ""))}</description>\n'
            f'    </item>'
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '  <channel>\n'
        '    <title>Essa</title>\n'
        f'    <link>{SITE_URL}</link>\n'
        '    <description>Personal blog by Essa — thoughts on technology, building things, and simplicity.</description>\n'
        '    <language>en</language>\n'
        f'    <lastBuildDate>{now}</lastBuildDate>\n'
        f'    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>\n'
        + '\n'.join(items) + '\n'
        '  </channel>\n'
        '</rss>\n'
    )


def main():
    posts = []

    for fname in os.listdir(POSTS_DIR):
        if not fname.endswith('.md'):
            continue

        with open(os.path.join(POSTS_DIR, fname), encoding='utf-8') as f:
            text = f.read()

        fm, body = parse_frontmatter(text)
        if not fm:
            continue

        title = fm.get('title')
        date_raw = fm.get('date')
        if not title or not date_raw:
            continue

        slug = fname[:-3]
        dt = datetime.strptime(date_raw, '%B %d, %Y')

        # Build posts.json entry
        entry = {
            'slug': slug,
            'title': title,
            'date': dt.strftime('%Y-%m-%d'),
            'dateDisplay': dt.strftime('%b %-d, %Y'),
        }
        if fm.get('dir'):
            entry['dir'] = fm['dir']
        if fm.get('lang'):
            entry['lang'] = fm['lang']

        # Description for RSS (first line of body, cleaned)
        description = re.sub(r'[#*_\n]', '', body[:160]).strip()
        entry['description'] = description

        posts.append(entry)

        # Generate post HTML page
        post_html = generate_post_html(slug, fm, body)
        out_path = os.path.join(POSTS_DIR, f'{slug}.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(post_html)
        print(f'  posts/{slug}.html')

    posts.sort(key=lambda p: p['date'], reverse=True)

    # Write posts.json (without description field — only used for RSS)
    posts_json = []
    for p in posts:
        entry = {k: v for k, v in p.items() if k != 'description'}
        posts_json.append(entry)

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(posts_json, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'  posts.json ({len(posts_json)} posts)')

    # Write feed.xml
    rss = generate_rss(posts)
    with open(OUTPUT_RSS, 'w', encoding='utf-8') as f:
        f.write(rss)
    print(f'  feed.xml')


if __name__ == '__main__':
    main()
