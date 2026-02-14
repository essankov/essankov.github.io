#!/usr/bin/env python3
"""Generate posts.json from markdown frontmatter in posts/."""
import json, os, re
from datetime import datetime

POSTS_DIR = os.path.join(os.path.dirname(__file__), 'posts')
OUTPUT = os.path.join(os.path.dirname(__file__), 'posts.json')

posts = []
for fname in os.listdir(POSTS_DIR):
    if not fname.endswith('.md'):
        continue
    with open(os.path.join(POSTS_DIR, fname), encoding='utf-8') as f:
        text = f.read()
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not m:
        continue
    fm = m.group(1)
    def field(key):
        r = re.search(rf'^{key}:\s*(.+)$', fm, re.MULTILINE)
        return r.group(1).strip() if r else None

    title = field('title')
    date_raw = field('date')
    if not title or not date_raw:
        continue

    dt = datetime.strptime(date_raw, '%B %d, %Y')
    entry = {
        'slug': fname[:-3],
        'title': title,
        'date': dt.strftime('%Y-%m-%d'),
        'dateDisplay': dt.strftime('%b %-d, %Y'),
    }
    if field('dir'):
        entry['dir'] = field('dir')
    if field('lang'):
        entry['lang'] = field('lang')
    posts.append(entry)

posts.sort(key=lambda p: p['date'], reverse=True)

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(posts, f, indent=2, ensure_ascii=False)
    f.write('\n')
