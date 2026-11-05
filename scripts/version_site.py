#!/usr/bin/env python3
"""Refresh cache versions for the current site's pages and local assets."""
import hashlib
import html
from pathlib import Path
import re
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent
PAGES = [ROOT / 'index.html', *sorted((ROOT / 'pages').glob('*.html'))]
ATTR = re.compile(r'(?P<prefix>\b(?:href|src)\s*=\s*)(?P<quote>[\'\"])(?P<url>.*?)(?P=quote)', re.I)


def local_reference(page, raw_url):
    url = urlsplit(html.unescape(raw_url))
    if url.scheme or url.netloc or not url.path:
        return None
    target = (ROOT / unquote(url.path.lstrip('/')) if url.path.startswith('/')
              else page.parent / unquote(url.path)).resolve()
    if ROOT not in target.parents or not target.is_file():
        raise ValueError('Missing or invalid local reference: {} in {}'.format(raw_url, page))
    return url, target


def rewrite(page, source, version=None):
    def replace(match):
        reference = local_reference(page, match['url'])
        if reference is None:
            return match.group(0)
        url, _ = reference
        query = [(k, v) for k, v in parse_qsl(url.query, keep_blank_values=True) if k != 'v']
        if version is not None:
            query.append(('v', version))
        value = urlunsplit((url.scheme, url.netloc, url.path, urlencode(query), url.fragment))
        return match['prefix'] + match['quote'] + html.escape(value, quote=True) + match['quote']
    return ATTR.sub(replace, source)


def main():
    sources = {page: page.read_text(encoding='utf-8') for page in PAGES}
    files = {ROOT / 'styles.css', *PAGES}
    for page, source in sources.items():
        for match in ATTR.finditer(source):
            reference = local_reference(page, match['url'])
            if reference is not None:
                files.add(reference[1])
    digest = hashlib.sha256()
    for path in sorted(files):
        digest.update(path.relative_to(ROOT).as_posix().encode('utf-8') + b'\0')
        data = rewrite(path, sources[path]).encode('utf-8') if path in sources else path.read_bytes()
        digest.update(data + b'\0')
    version = digest.hexdigest()[:12]
    for page, source in sources.items():
        updated = rewrite(page, source, version)
        if updated != source:
            page.write_text(updated, encoding='utf-8')
    print('Site version: ' + version)
    print('Preview: http://127.0.0.1:8000/index.html?v=' + version)


if __name__ == '__main__':
    main()
