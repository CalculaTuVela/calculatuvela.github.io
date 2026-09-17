# calculatuvela.github.io

Landing page for **CalculaTuVela**, an Android app for candle makers, and portfolio of its developer,
Diego Casas. Plain static HTML/CSS/JS served by GitHub Pages at https://calculatuvela.github.io/ — no
framework, no bundler.

## Pages

| Path | What it is |
| --- | --- |
| `index.html` | Landing page, in Spanish (source of truth) |
| `privacy-policy.html` | App privacy policy linked from Google Play, in Spanish (source of truth) |
| `en/index.html`, `en/privacy-policy.html` | English versions — **generated, don't edit by hand** |
| `cv.html` | Résumé (English only), plus `DiegoCasas-CV.pdf` |
| `assets/site.css`, `assets/site.js` | Shared color tokens, header, theme toggle and language switch |
| `assets/` | Screenshots (WebP), avatar, favicon and social preview images (`og-es.png`, `og-en.png`) |

## Editing copy

Each language is a separate static page so search engines index both and nobody sees a flash of
the wrong language. The English text lives next to the Spanish text as attributes:

```html
<h2 data-es="El producto" data-en="The product">El producto</h2>
<img alt="Lista de recetas" data-en-alt="Recipe list" ...>
<meta name="description" content="..." data-en-content="...">
```

- `data-en` / `data-en-html` replace the element's text / inner HTML.
- `data-en-<attr>` replaces any attribute (`alt`, `content`, `href`, `aria-label`...).
- `data-es-only` drops an element from the English page; `<template data-en-only>` adds its content
  only to the English page (used for the long-form privacy policy).

After changing `index.html` or `privacy-policy.html`, regenerate the English pages and commit them:

```sh
python3 scripts/build_en.py
```

CI runs `python3 scripts/build_en.py --check` and fails if `en/` is out of date.

## Theme and language preferences

Both are stored in `localStorage` (`ctv-theme`, `ctv-lang`). An inline script in each `<head>` applies
the saved theme before the first paint; on the Spanish pages it also redirects to `/en/` if the visitor
previously chose English.

## Running locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000/.
