#!/usr/bin/env python3
"""Build static site from templates, pages, and Markdown posts."""
import os
import re
import html
import shutil
import math
from datetime import datetime, timezone
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
DIST = ROOT / 'dist'
TEMPLATES = ROOT / 'templates'
PAGES = ROOT / 'pages'
CONTENT = ROOT / 'content' / 'posts'
STATIC = ROOT / 'static'

SITE_URL = 'https://essankov.github.io'
SITE_TITLE = 'Essa'
SITE_DESC = 'Personal blog by Essa \u2014 thoughts on technology, building things, and simplicity.'

MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
]

FOOTER = '      <footer class="footer">\n        <p>&copy; 2026 Essa. All rights reserved.</p>\n      </footer>'


def render(template, variables):
    """Simple {{var}} replacement."""
    result = template
    for key, val in variables.items():
        result = result.replace('{{' + key + '}}', val)
    return result


def parse_frontmatter(text):
    """Parse YAML-like frontmatter from Markdown text."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not match:
        return {}, text
    meta = {}
    for line in match.group(1).split('\n'):
        line = line.strip()
        if not line:
            continue
        colon = line.index(':')
        key = line[:colon].strip()
        val = line[colon + 1:].strip()
        meta[key] = val
    return meta, text[match.end():]


def build_nav(root='', active=''):
    """Generate nav HTML with correct active link and root paths."""
    blog_cls = ' class="active"' if active == 'blog' else ''
    about_cls = ' class="active"' if active == 'about' else ''
    return (
        '  <nav class="topnav">\n'
        f'    <div class="topnav-logo"><a href="{root}index.html">Essa</a></div>\n'
        '    <ul class="topnav-links">\n'
        f'      <li><a href="{root}blog.html"{blog_cls}>Blog</a></li>\n'
        f'      <li><a href="{root}about.html"{about_cls}>About</a></li>\n'
        '      <li>\n'
        '        <button class="theme-toggle" id="theme-toggle" aria-label="Toggle theme">\n'
        '          <span class="icon">&#9790;</span>\n'
        '          <span class="label">Dark</span>\n'
        '        </button>\n'
        '      </li>\n'
        '    </ul>\n'
        '  </nav>'
    )


def build_meta_tags(title, desc, og_type='website', url=''):
    """Build OG and Twitter meta tag string."""
    t = html.escape(title)
    d = html.escape(desc)
    u = html.escape(url)
    lines = [
        f'  <meta name="description" content="{d}">',
        f'  <meta property="og:title" content="{t}">',
        f'  <meta property="og:description" content="{d}">',
        f'  <meta property="og:type" content="{og_type}">',
        f'  <meta property="og:url" content="{u}">',
        '  <meta name="twitter:card" content="summary">',
    ]
    if og_type == 'website':
        lines.extend([
            f'  <meta name="twitter:title" content="{t}">',
            f'  <meta name="twitter:description" content="{d}">',
        ])
    return '\n'.join(lines)


def reading_time(text, lang='en'):
    """Estimate reading time."""
    words = len(text.split())
    wpm = 150 if lang == 'ar' else 200
    minutes = max(1, math.ceil(words / wpm))
    if lang == 'ar':
        return f'{minutes} \u062f\u0642\u064a\u0642\u0629 \u0642\u0631\u0627\u0621\u0629'
    return f'{minutes} min read'


def format_date(date_str):
    """YYYY-MM-DD -> 'Feb 14, 2026'."""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    month = dt.strftime('%b')
    return f'{month} {dt.day}, {dt.year}'


def copy_static():
    """Copy static/ -> dist/."""
    for item in STATIC.iterdir():
        dest = DIST / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)


def build_posts(template):
    """Build all Markdown posts, return list of post metadata sorted newest first."""
    posts_dir = DIST / 'posts'
    posts_dir.mkdir(exist_ok=True)

    posts = []
    for md_file in sorted(CONTENT.glob('*.md')):
        text = md_file.read_text(encoding='utf-8')
        meta, body_md = parse_frontmatter(text)

        title = meta.get('title', 'Untitled')
        date = meta.get('date', '2026-01-01')
        desc = meta.get('description', '')
        slug = meta.get('slug', md_file.stem)
        lang = meta.get('lang', 'en')
        direction = meta.get('dir', 'ltr')

        # Convert markdown to HTML
        body_html = markdown.markdown(body_md, extensions=[])

        date_display = format_date(date)
        rt = reading_time(body_md, lang)
        back_text = '\u062c\u0645\u064a\u0639 \u0627\u0644\u0645\u0642\u0627\u0644\u0627\u062a' if lang == 'ar' else 'All posts'

        # Build post body
        nav = build_nav(root='../', active='')
        post_body = (
            f'\n{nav}\n'
            '\n'
            '  <main class="main">\n'
            '    <div class="content">\n'
            '\n'
            f'      <a href="../blog.html" class="back-link">{back_text}</a>\n'
            '\n'
            '      <header class="post-header">\n'
            f'        <h1>{html.escape(title)}</h1>\n'
            '        <div class="post-meta">\n'
            f'          <span>{date_display}</span>\n'
            f'          <span class="reading-time">{rt}</span>\n'
            '        </div>\n'
            '      </header>\n'
            '\n'
            f'      <article class="post-content">{body_html}</article>\n'
            '\n'
            f'{FOOTER}\n'
            '\n'
            '    </div>\n'
            '  </main>\n'
        )

        # Extra preloads for Arabic
        extra = ''
        if lang == 'ar':
            extra = '  <link rel="preload" href="../fonts/Jali-Arabic-Regular.woff2" as="font" type="font/woff2" crossorigin>\n'

        page_title = f'{title} \u2014 {SITE_TITLE}'
        meta_tags = build_meta_tags(
            page_title, desc, 'article',
            f'{SITE_URL}/posts/{slug}.html'
        )

        page_html = render(template, {
            'lang': lang,
            'dir': direction,
            'title': page_title,
            'meta_tags': meta_tags,
            'root': '../',
            'extra_preloads': extra,
            'body': post_body,
        })

        (posts_dir / f'{slug}.html').write_text(page_html, encoding='utf-8')

        posts.append({
            'title': title,
            'date': date,
            'date_display': date_display,
            'description': desc,
            'slug': slug,
            'lang': lang,
            'dir': direction,
        })

    posts.sort(key=lambda p: (p['date'], p['slug']), reverse=True)
    print(f'  Built {len(posts)} posts')
    return posts


def build_blog(template, posts):
    """Build blog.html with post list grouped by month."""
    # Group posts by month
    groups = []
    group_map = {}
    for p in posts:
        dt = datetime.strptime(p['date'], '%Y-%m-%d')
        key = f'{dt.year}-{dt.month:02d}'
        label = f'{MONTHS[dt.month - 1]} {dt.year}'
        if key not in group_map:
            group = {'label': label, 'posts': []}
            group_map[key] = group
            groups.append(group)
        group_map[key]['posts'].append(p)

    # Build post list HTML
    lines = []
    for g in groups:
        lines.append('      <div class="post-group">')
        lines.append(f'        <div class="post-group-label">{html.escape(g["label"])}</div>')
        lines.append('        <ul class="post-list">')
        for p in g['posts']:
            lines.append('          <li class="post-item">')
            lines.append(f'            <a href="posts/{html.escape(p["slug"])}.html">{html.escape(p["title"])}</a>')
            lines.append(f'            <span class="post-date">{html.escape(p["date_display"])}</span>')
            lines.append('          </li>')
        lines.append('        </ul>')
        lines.append('      </div>')
    post_list_html = '\n'.join(lines)

    # Read blog page fragment and inject post list
    blog_fragment = (PAGES / 'blog.html').read_text(encoding='utf-8')
    blog_content = render(blog_fragment, {'post_list': post_list_html})

    nav = build_nav(root='', active='blog')
    body = (
        f'\n{nav}\n'
        '\n'
        '  <main class="main">\n'
        '    <div class="content">\n'
        '\n'
        f'      {blog_content}\n'
        '\n'
        f'{FOOTER}\n'
        '\n'
        '    </div>\n'
        '  </main>\n'
    )

    title = f'Blog \u2014 {SITE_TITLE}'
    meta_tags = build_meta_tags(
        title,
        'All posts by Essa, organized by date. Thoughts on technology, building things, and simplicity.',
        'website',
        f'{SITE_URL}/blog.html'
    )

    page_html = render(template, {
        'lang': 'en',
        'dir': 'ltr',
        'title': title,
        'meta_tags': meta_tags,
        'root': '',
        'extra_preloads': '',
        'body': body,
    })

    (DIST / 'blog.html').write_text(page_html, encoding='utf-8')
    print('  Built blog.html')


def build_pages(template):
    """Build index.html, about.html, 404.html."""
    # Index (hero page — no nav, no footer)
    index_fragment = (PAGES / 'index.html').read_text(encoding='utf-8')
    index_body = (
        '\n  <main class="main">\n'
        '    <div class="hero">\n'
        f'      {index_fragment}'
        '    </div>\n'
        '  </main>\n'
    )
    meta_tags = build_meta_tags(
        SITE_TITLE, SITE_DESC, 'website', f'{SITE_URL}/'
    )
    page_html = render(template, {
        'lang': 'en', 'dir': 'ltr', 'title': SITE_TITLE,
        'meta_tags': meta_tags, 'root': '', 'extra_preloads': '',
        'body': index_body,
    })
    (DIST / 'index.html').write_text(page_html, encoding='utf-8')
    print('  Built index.html')

    # About
    about_fragment = (PAGES / 'about.html').read_text(encoding='utf-8')
    nav = build_nav(root='', active='about')
    about_body = (
        f'\n{nav}\n'
        '\n'
        '  <main class="main">\n'
        '    <div class="content">\n'
        '\n'
        '      <section class="post-header">\n'
        '        <h1>About</h1>\n'
        '      </section>\n'
        '\n'
        f'      <div class="about-content">\n'
        f'        {about_fragment}'
        '      </div>\n'
        '\n'
        f'{FOOTER}\n'
        '\n'
        '    </div>\n'
        '  </main>\n'
    )
    title = f'About \u2014 {SITE_TITLE}'
    meta_tags = build_meta_tags(
        title,
        'About Essa \u2014 passionate about technology, building things, and exploring new ideas.',
        'website',
        f'{SITE_URL}/about.html'
    )
    page_html = render(template, {
        'lang': 'en', 'dir': 'ltr', 'title': title,
        'meta_tags': meta_tags, 'root': '', 'extra_preloads': '',
        'body': about_body,
    })
    (DIST / 'about.html').write_text(page_html, encoding='utf-8')
    print('  Built about.html')

    # 404 (hero page — no nav, no footer)
    four04_fragment = (PAGES / '404.html').read_text(encoding='utf-8')
    four04_body = (
        '\n  <main class="main">\n'
        '    <div class="hero">\n'
        f'      {four04_fragment}'
        '    </div>\n'
        '  </main>\n'
    )
    page_html = render(template, {
        'lang': 'en', 'dir': 'ltr', 'title': f'404 \u2014 {SITE_TITLE}',
        'meta_tags': '', 'root': '', 'extra_preloads': '',
        'body': four04_body,
    })
    (DIST / '404.html').write_text(page_html, encoding='utf-8')
    print('  Built 404.html')


def build_rss(posts):
    """Generate feed.xml."""
    now = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    items = []
    for p in posts:
        dt = datetime.strptime(p['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        pub_date = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        url = f'{SITE_URL}/posts/{p["slug"]}.html'
        items.append(
            '    <item>\n'
            f'      <title>{html.escape(p["title"])}</title>\n'
            f'      <link>{html.escape(url)}</link>\n'
            f'      <guid isPermaLink="true">{html.escape(url)}</guid>\n'
            f'      <pubDate>{pub_date}</pubDate>\n'
            f'      <description>{html.escape(p.get("description", ""))}</description>\n'
            '    </item>'
        )

    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '  <channel>\n'
        f'    <title>{SITE_TITLE}</title>\n'
        f'    <link>{SITE_URL}</link>\n'
        f'    <description>{html.escape(SITE_DESC)}</description>\n'
        '    <language>en</language>\n'
        f'    <lastBuildDate>{now}</lastBuildDate>\n'
        f'    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>\n'
        + '\n'.join(items) + '\n'
        '  </channel>\n'
        '</rss>\n'
    )

    (DIST / 'feed.xml').write_text(rss, encoding='utf-8')
    print('  Built feed.xml')


def main():
    print('Building site...')

    # Clean and create dist
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / 'posts').mkdir()

    # Copy static assets
    copy_static()
    print('  Copied static assets')

    # Load template
    template = (TEMPLATES / 'base.html').read_text(encoding='utf-8')

    # Build posts
    posts = build_posts(template)

    # Build blog listing
    build_blog(template, posts)

    # Build pages
    build_pages(template)

    # Build RSS
    build_rss(posts)

    print('Done!')


if __name__ == '__main__':
    main()
