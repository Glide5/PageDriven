# PageDriven site source

The site Vercel serves is the repo root: 19 HTML pages, `assets/`, and `api/submit.js`.
Those pages are **generated**. Edit the files in this folder, then rebuild.

This folder is listed in `/.vercelignore`, so it is stored in Git but never deployed.

| File | What it holds |
|---|---|
| `src.html` | Homepage markup and the shared base CSS (the `<style>` block) |
| `build.py` | Builds every page: header, footer, inner pages, case studies, service pages |
| `site.json` | Content: services, FAQs, case studies, testimonials, CTAs |
| `inner.css` | Styles appended after the base CSS → `assets/site.css` |
| `site.js` | All interactions and animations → `assets/site.js` |
| `images/` | Source images copied into `assets/img/` |
| `assets.json` | A few original images stored as data URIs (icons 0–7, Riz waist, avatar) |
| `export.py` | Copies the build into the repo root, adding production's wrapper to `index.html` and the Microsoft Clarity tag to every page's `<head>` |
| `tools/icon-renderer.html` | WebGL renderer used to make the 3D icons |

## Make a change
```bash
python3 _source/build.py     # writes _source/.out/site (preview build)
python3 _source/export.py    # copies it to the repo root
git checkout -b my-change && git add -A && git commit -m "Describe the change"
git push -u origin my-change # Vercel builds a preview URL for the branch
```
Open a pull request into `main`. Merging it deploys to pagedriven.com.
Requires Python 3 with Pillow (`pip install pillow`).

Never edit the generated `*.html` or `assets/site.css`/`assets/site.js` in the root
directly; the next build overwrites them. `api/submit.js` and `package.json` are edited by hand.

## Forms → riz@gopagedriven.com
Every lead form (the review modal, the contact modal, the inline review form on Book and Work,
and the chat widget's "leave your email") posts to Formspree at `https://formspree.io/f/xwllyvv`,
set as `FORM_ENDPOINT` in `site.js`. Formspree emails each submission to the address set on that
form in the Formspree dashboard (riz@gopagedriven.com). The visitor's `email` field is used as reply-to.

The success message appears only after Formspree answers `ok: true`. On any error, visitors see
"Couldn't send right now. Please email riz@gopagedriven.com instead." If Formspree rejects the
email address, they see the usual email hint instead.
No Vercel environment variables are needed. `api/submit.js` (the earlier Resend function) is no longer called.
In the claude.ai preview, and when a page is opened as a local file, forms only simulate a send.
