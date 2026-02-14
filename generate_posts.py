#!/usr/bin/env python3
"""Generate posts.json and feed.xml from existing post HTML files."""
import json, os, re, html
from datetime import datetime, timezone

SITE_URL = 'https://essankov.github.io'
POSTS_DIR = os.path.join(os.path.dirname(__file__), 'posts')
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), 'posts.json')
OUTPUT_RSS = os.path.join(os.path.dirname(__file__), 'feed.xml')


def extract_metadata(filepath):
    with open(filepath, encoding='utf-8') as f:
        text = f.read()

    meta = {}

    m = re.search(r'<html\s+lang="([^"]*)"', text)
    if m:
        meta['lang'] = m.group(1)

    m = re.search(r'<html\s[^>]*dir="([^"]*)"', text)
    if m:
        meta['dir'] = m.group(1)

    m = re.search(r'<h1>([^<]+)</h1>', text)
    if m:
        meta['title'] = html.unescape(m.group(1))

    m = re.search(r'<div class="post-meta">\s*<span>([^<]+)</span>', text)
    if m:
        meta['dateDisplay'] = m.group(1).strip()

    m = re.search(r'<meta name="description" content="([^"]*)"', text)
    if m:
        meta['description'] = html.unescape(m.group(1))

    return meta


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
        if not fname.endswith('.html'):
            continue

        meta = extract_metadata(os.path.join(POSTS_DIR, fname))
        title = meta.get('title')
        date_display = meta.get('dateDisplay')
        if not title or not date_display:
            continue

        slug = fname[:-5]
        dt = datetime.strptime(date_display, '%b %d, %Y')

        entry = {
            'slug': slug,
            'title': title,
            'date': dt.strftime('%Y-%m-%d'),
            'dateDisplay': date_display,
        }
        if meta.get('dir') and meta['dir'] != 'ltr':
            entry['dir'] = meta['dir']
        if meta.get('lang') and meta['lang'] != 'en':
            entry['lang'] = meta['lang']
        if meta.get('description'):
            entry['description'] = meta['description']

        posts.append(entry)

    posts.sort(key=lambda p: p['date'], reverse=True)

    # Write posts.json (without description — only used for RSS)
    posts_json = []
    for p in posts:
        posts_json.append({k: v for k, v in p.items() if k != 'description'})

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
