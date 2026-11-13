#!/usr/bin/env python3
"""Roll the site over to the newest edition. Run after every publish.

Usage:
  python3 scripts/publish.py                # newest archive/YYYY-MM-DD/ is the latest edition
  python3 scripts/publish.py 2026-11-14     # name the latest edition explicitly
  python3 scripts/publish.py --build        # first run build_edition.py and build_bulletin.py
                                            # for the newest editions/YYYY-MM-DD.json

What it does (safe to run any number of times):
  1. Landing page (index.html): the "Latest edition" pill and button show the latest date.
  2. Archive list (archive/index.html): adds the latest edition at the top if missing and
     moves the LATEST badge onto it.
  3. The latest edition's archive copy links to its own archived bulletin.
  4. Every older edition in archive/ is marked as archived: an ARCHIVED EDITION banner,
     "Archived Edition" instead of "Latest Edition", "Archive" in the page title, and
     links to its own bulletin rather than today's.
  5. "Share on WhatsApp": each edition gets a one-page A4 PDF of its front page with working
     links (archive/YYYY-MM-DD/Pringital-News-D-Mon-YYYY.pdf, made by scripts/make_pdf.js), and
     the button shares that PDF (script in scripts/_share.html). A PDF is (re)made when it is
     missing or its page changed; pass --pdf to remake them all.

Optional overrides in editions/YYYY-MM-DD.json for the archive list entry:
  "archive_h": headline text, "archive_also": the "Also: ..." line.
"""
import datetime
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse

SITE = "https://pringital.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
changed = []


def path(*p):
    return os.path.join(ROOT, *p)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, new):
    if os.path.exists(p) and read(p) == new:
        return
    with open(p, "w", encoding="utf-8") as f:
        f.write(new)
    changed.append(os.path.relpath(p, ROOT))


def day(d):
    return datetime.date.fromisoformat(d)


def dateline(d):  # Friday, 13 November 2026
    x = day(d)
    return f"{x:%A}, {x.day} {x:%B %Y}"


def short(d):  # 13 Nov 2026
    x = day(d)
    return f"{x.day} {x:%b %Y}"


def archive_dates():
    a = path("archive")
    return sorted(n for n in os.listdir(a)
                  if DATE_RE.match(n) and os.path.exists(os.path.join(a, n, "index.html")))


def build_latest():
    eds = sorted(n[:-5] for n in os.listdir(path("editions"))
                 if n.endswith(".json") and DATE_RE.match(n[:-5]))
    if not eds:
        sys.exit("No editions/YYYY-MM-DD.json to build.")
    d = eds[-1]
    subprocess.run([sys.executable, path("scripts", "build_edition.py"), path("editions", f"{d}.json")], check=True)
    b = path("editions", f"{d}-bulletin.json")
    if os.path.exists(b):
        subprocess.run([sys.executable, path("scripts", "build_bulletin.py"), b], check=True)
    return d


# ------------------------------------------------------------------ landing page

def update_landing(d):
    p = path("index.html")
    s = read(p)
    s = re.sub(r'(<a class="latest" href="today/">Latest edition<span class="lg"> · )[^<]*', r"\g<1>" + short(d), s)
    s = re.sub(r"(Read the latest edition <small>)[^<]*", r"\g<1>" + dateline(d), s)
    write(p, s)


# ------------------------------------------------------------------ archive list

def archive_entry(d):
    src = path("editions", f"{d}.json")
    if not os.path.exists(src):
        sys.exit(f"archive/index.html has no entry for {d} and editions/{d}.json is missing, "
                 "so its headline is unknown. Add the entry by hand or supply the JSON.")
    E = json.load(open(src, encoding="utf-8"))
    h = E.get("archive_h") or E["lead"]["h"]
    also = E.get("archive_also")
    if not also:
        heads = [E[k]["h"] for k in ("second", "beside") if isinstance(E.get(k), dict) and E[k].get("h")]
        top = (E.get("right") or {}).get("top") or {}
        if top.get("h"):
            heads.append(top["h"])
        also = "Also: " + "; ".join(heads) + "." if heads else ""
    x = day(d)
    edition = E.get("edition", "New Delhi Edition")
    listen = (f'<a class="btn listen" href="/archive/{d}/bulletin/">▶ Listen · 4 min</a>'
              if os.path.exists(path("archive", d, "bulletin", "index.html")) else "")
    return f"""<li>
      <div class="date"><span class="d">{x.day}</span><span class="m">{x:%b}</span><span class="y">{x.year} · {x:%a}</span></div>
      <div class="ed">
        <span class="kick">{html.escape(edition)}</span>
        <h3><a href="/archive/{d}/">{html.escape(h, quote=False)}</a></h3>
        <p>{html.escape(also, quote=False)}</p>
        <div class="links"><a class="btn" href="/archive/{d}/">Read front page</a>{listen}</div>
      </div>
    </li>
    """


def update_archive_list(d):
    p = path("archive", "index.html")
    s = read(p)
    if f'href="/archive/{d}/"' not in s:
        s = s.replace("<ol>\n    <li>", "<ol>\n    " + archive_entry(d) + "<li>", 1)
        if f'href="/archive/{d}/"' not in s:
            sys.exit("Could not find where to add the entry in archive/index.html.")
    s = s.replace('<span class="latest">LATEST</span>', "")
    s = re.sub(r'(<span class="kick">[^<]*</span>)(\s*<h3><a href="/archive/' + d + '/">)',
               r'\1<span class="latest">LATEST</span>\2', s, count=1)
    write(p, s)


# ------------------------------------------------------------------ edition pages

def banner(d, bulletin):
    t = f"ARCHIVED EDITION · {dateline(d).upper()} &nbsp;·&nbsp; "
    if bulletin:
        style, link = "background:#141414;color:#fff;font:700 12px/1.4 Inter,Arial,sans-serif", "color:#ffb3b8"
    else:
        style = "background:var(--ink);color:var(--bg);font:600 12px/1.4 Montserrat,Arial,sans-serif"
        link = "color:inherit;text-decoration:underline"
    return (f'<div style="{style};letter-spacing:.06em;text-align:center;padding:8px 16px">{t}'
            f'<a href="/today/" style="{link}">Read today’s edition</a> &nbsp;·&nbsp; '
            f'<a href="/archive/" style="{link}">All editions</a></div>\n')


def own_bulletin_links(d):
    """The archive copy of an edition should play its own day's bulletin, not today's."""
    p = path("archive", d, "index.html")
    write(p, read(p).replace('href="/bulletin/"', f'href="/archive/{d}/bulletin/"'))


def mark_archived(d):
    for rel, is_bulletin in (("index.html", False), (os.path.join("bulletin", "index.html"), True)):
        p = path("archive", d, rel)
        if not os.path.exists(p):
            continue
        s = read(p)
        if "ARCHIVED EDITION ·" not in s:
            s = re.sub(r"(<body[^>]*>\n?)", lambda m: m.group(1) + banner(d, is_bulletin), s, count=1)
        s = s.replace("● Latest Edition", "● Archived Edition")
        if not is_bulletin:
            s = re.sub(r"<title>Pringital News · (?!Archive)", "<title>Pringital News · Archive · ", s, count=1)
        write(p, s)


# ------------------------------------------------------------------ WhatsApp PDF share

def pdf_url(d):
    x = day(d)
    return f"/archive/{d}/Pringital-News-{x.day}-{x:%b}-{x.year}.pdf"


def wire_share(p, d):
    """Point the page's Share on WhatsApp button at the edition PDF and add the share script."""
    if not os.path.exists(p):
        return False
    s = read(p)
    if 'class="lnk wa"' not in s:
        return False
    title = f"Pringital News · {dateline(d)}"
    wa = "https://wa.me/?text=" + urllib.parse.quote(f"{title} — front page (PDF): {SITE}{pdf_url(d)}", safe="")
    s = re.sub(r'<a class="lnk wa" href="[^"]*"(?: data-pdf="[^"]*")?(?: data-title="[^"]*")?',
               lambda m: f'<a class="lnk wa" href="{html.escape(wa)}" data-pdf="{pdf_url(d)}" data-title="{html.escape(title)}"', s)
    js = read(path("scripts", "_share.html"))
    if 'id="pn-share"' in s:
        s = re.sub(r'<script id="pn-share">.*?</script>\n?', lambda m: js, s, count=1, flags=re.S)
    else:
        i = s.rfind("</body>")
        s = s[:i] + js + s[i:] if i >= 0 else s + js
    write(p, s)
    return True


def make_pdfs(dates):
    if not dates:
        return
    r = subprocess.run(["node", path("scripts", "make_pdf.js"), *dates], cwd=ROOT)
    if r.returncode:
        sys.exit("PDF generation failed: the Share on WhatsApp button would point at a missing PDF. "
                 "Fix it and run publish.py again before pushing.")
    changed.extend(pdf_url(d).lstrip("/") for d in dates)


def main():
    args = sys.argv[1:]
    built = build_latest() if "--build" in args else None
    named = [a for a in args if DATE_RE.match(a)]
    dates = archive_dates()
    latest = named[0] if named else (max(dates) if dates else built)
    if not latest or latest not in dates:
        sys.exit(f"archive/{latest}/index.html not found; build the edition first.")

    update_landing(latest)
    update_archive_list(latest)
    for d in dates:
        own_bulletin_links(d)
        if d != latest:
            mark_archived(d)
    shared = [d for d in dates if wire_share(path("archive", d, "index.html"), d)]
    wire_share(path("today", "index.html"), latest)
    make_pdfs([d for d in shared if "--pdf" in args
               or not os.path.exists(path(pdf_url(d).lstrip("/")))
               or f"archive/{d}/index.html" in changed])

    print(f"Latest edition: {dateline(latest)}")
    print("Updated:\n  " + "\n  ".join(changed) if changed else "Already up to date.")


if __name__ == "__main__":
    main()
