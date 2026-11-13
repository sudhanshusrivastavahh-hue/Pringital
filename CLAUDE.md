# Pringital News site

After adding or updating an edition (e.g. unzipping an edition package over the repo root),
always run `python3 scripts/publish.py` before committing. It rolls the site over to the newest
`archive/YYYY-MM-DD/` edition: landing-page dates, the archive list and LATEST badge, and
archived-edition markings on all older editions, and the shareable front-page PDF behind
the "Share on WhatsApp" button. If PDF generation fails, fix it before pushing. Review `git diff` afterwards.
