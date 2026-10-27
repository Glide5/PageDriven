"""Copy the built site (_source/.out/site) into the repo root, which Vercel serves.

index.html is generated without a document wrapper (the claude.ai preview adds its own),
so it gets the same wrapper production has always used. Files already in the repo root
that the build does not produce are left alone; api/ and package.json are maintained by hand.
"""
import os, shutil, sys
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SITE = os.environ.get("PD_OUT") or os.path.join(BASE, ".out", "site")
INDEX_PREFIX = '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style></head><body>\n'
INDEX_SUFFIX = "\n</body></html>"

if not os.path.exists(os.path.join(SITE, "index.html")):
    sys.exit("No build found. Run: python3 _source/build.py")
n = 0
for d, _, files in os.walk(SITE):
    for f in files:
        src = os.path.join(d, f); rel = os.path.relpath(src, SITE); dst = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if rel == "index.html":
            open(dst, "w").write(INDEX_PREFIX + open(src).read() + INDEX_SUFFIX)
        else:
            shutil.copyfile(src, dst)
        n += 1
print(f"exported {n} files to {ROOT}")
