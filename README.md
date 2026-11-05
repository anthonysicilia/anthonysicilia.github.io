# anthonysicilia.github.io
Personal Site

## Refresh cache versions before publishing

After editing the website, run:

```sh
python3 scripts/version_site.py
```

Commit the updated HTML files along with your changes. The script derives a
version from the current pages, stylesheet, and referenced images, and appends
it to internal page links, stylesheet URLs, and image URLs. Any content change
produces a new version; running it again without changes keeps the same version.
External links are left unchanged.

An already cached entry page may need a refresh once, or open `index.html?v=VERSION`
using the version printed by the script. Version tags cannot replace a redirect
or HTML document that a browser has already cached before receiving this update.
