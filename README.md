# Pringital News

Website for pringital.com: today's front page, the four-minute bulletin, and the archive of past editions.

- `index.html` – landing page
- `today/` – the latest edition's front page
- `bulletin/` – the latest edition's bulletin
- `archive/` – every edition, one folder per date (`archive/YYYY-MM-DD/`), plus the list in `archive/index.html`
- `editions/` – source data for each edition; `scripts/` – build and publish scripts

Hosted on GitHub Pages with the custom domain in `CNAME`.

## Publishing a new edition

1. Add the new edition's files (unzip the edition package over the repo root, or run
   `scripts/build_edition.py` and `scripts/build_bulletin.py` on `editions/YYYY-MM-DD*.json`).
2. Run `python3 scripts/publish.py`. It updates the dates on the landing page, adds the edition
   to the archive list with the LATEST badge, and marks every older edition as archived
   (banner, "Archived Edition" label, its own bulletin link). It also saves each edition's front
   page as a one-page A4 PDF with clickable links (`scripts/make_pdf.js`, needs Node, Playwright
   and access to Google Fonts) and points the "Share on WhatsApp" button at it: on phones the
   button shares the PDF itself; on desktop it opens WhatsApp with a link to the PDF.
   It is safe to run more than once.
3. Commit and push to `main`.
