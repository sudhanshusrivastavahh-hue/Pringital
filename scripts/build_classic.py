#!/usr/bin/env python3
"""Build a "classic" Mist Blue edition (the 15 Nov 2026 design) sized exactly A4.

Usage: python3 scripts/build_classic.py editions/YYYY-MM-DD.json [TEMPLATE_DATE]

Takes the page shell (styles, top bar, masthead, scripts) from archive/TEMPLATE_DATE/index.html
(default: 2026-11-15), fills it with the edition's content, and writes
today/index.html and archive/YYYY-MM-DD/index.html. The paper page is 980 x 1386 px, the
A4 proportion, and every column is filled to the bottom. Run scripts/publish.py afterwards.
"""
import datetime, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PW, PH = 980, 1386  # A4 proportion (1 : 1.4142)


def esc(s):
    return html.escape(s, quote=True)


def a(url, text):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{text}</a>'


def arrow(url):
    return f'<a class="dn" href="{esc(url)}" target="_blank" rel="noopener" aria-label="Detailed news">↗</a>'


# ------------------------------------------------------------------ illustrations (original)
def art(kind):
    if kind.startswith("svg:"):
        fp = os.path.join(ROOT, "assets", "art", kind[4:] + ".svg")
        return open(fp, encoding="utf-8").read() if os.path.exists(fp) else ""
    if kind == "manila":
        return '''<svg viewBox="0 0 400 230" role="img" aria-label="Map-style graphic: India and the ten ASEAN countries linked to Manila, venue of the 23rd India-ASEAN Summit and 21st East Asia Summit">
<rect width="400" height="230" fill="#0D47A1"/><circle cx="330" cy="40" r="80" fill="#1565C0"/>
<path d="M0 200 Q200 170 400 200 V230 H0Z" fill="#26A69A"/>
<text x="16" y="30" font-size="15" font-weight="800" letter-spacing="1.2" fill="#FFD23F">MANILA · 17 NOV</text>
<text x="16" y="50" font-size="11" font-weight="600" fill="#E3F0FF">23rd India-ASEAN · 21st East Asia Summit</text>
<g font-size="10" font-weight="700" fill="#fff">
<circle cx="70" cy="120" r="22" fill="#FF9933"/><text x="70" y="124" text-anchor="middle">INDIA</text>
<circle cx="300" cy="120" r="26" fill="#FFD23F"/><text x="300" y="117" text-anchor="middle" fill="#0D2B5E">MANILA</text><text x="300" y="129" text-anchor="middle" fill="#0D2B5E" font-size="8">PHILIPPINES</text>
</g>
<path d="M92 120 Q185 70 274 118" fill="none" stroke="#FFD23F" stroke-width="3" stroke-dasharray="6 5"/>
<path d="M266 110 l10 8 -12 4z" fill="#FFD23F"/>
<g fill="#E3F0FF">''' + "".join(f'<circle cx="{150+i*16}" cy="{170 - (i%2)*8}" r="5"/>' for i in range(10)) + '''</g>
<text x="222" y="194" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">10 ASEAN nations</text>
<text x="16" y="222" font-size="9.5" fill="#E3F0FF">South China Sea code: about 80% agreed, not final</text>
</svg>'''
    if kind == "royal":
        return '''<svg viewBox="0 0 400 260" role="img" aria-label="Illustration: a crown above the Gateway of India arch with a green Earthshot globe, for the royal visit">
<rect width="400" height="260" fill="#E8EEF6"/><circle cx="330" cy="58" r="34" fill="#9CC9A6"/><path d="M300 58h60M330 28v60M308 38q22 20 44 0M308 78q22-20 44 0" stroke="#5E8C6A" stroke-width="2" fill="none"/>
<path d="M120 70l18 22 22-30 22 30 18-22-8 44h-64z" fill="#FFC93C" stroke="#C98B2E" stroke-width="2"/>
<rect x="70" y="140" width="190" height="96" fill="#EADFCB" stroke="#C9B48F" stroke-width="2"/>
<path d="M140 236v-50a25 25 0 0 1 50 0v50z" fill="#E8EEF6" stroke="#C9B48F" stroke-width="2"/>
<rect x="64" y="128" width="202" height="14" fill="#C9B48F"/><rect x="82" y="150" width="40" height="30" rx="4" fill="#fff" opacity=".6"/><rect x="208" y="150" width="40" height="30" rx="4" fill="#fff" opacity=".6"/>
<text x="330" y="118" font-size="11" font-weight="800" text-anchor="middle" fill="#3D5F92">EARTHSHOT</text><text x="330" y="132" font-size="10" text-anchor="middle" fill="#535C68">Mumbai</text>
<text x="16" y="252" font-size="10" fill="#535C68">3-day visit · meets PM on Wednesday</text>
</svg>'''
    if kind.startswith("aqi"):
        parts = (kind.split(":") + [None]*5)[:5]
        now = int(parts[1] or 213); prev = int(parts[2] or 353)
        nowl = parts[3] or "Mon 6 am"; prevl = parts[4] or "Sunday"
        segs = [("#9CC9A6", "Good"), ("#C9DB9A", "Sat."), ("#EBD58E", "Mod."), ("#E8B27F", "Poor"), ("#D98C73", "V. poor"), ("#B86A6A", "Severe")]
        import math
        out = []
        for i, (c, _) in enumerate(segs):
            a0, a1 = math.pi * (1 - i / 6), math.pi * (1 - (i + 1) / 6)
            x0, y0, x1, y1 = 200 + 120 * math.cos(a0), 190 - 120 * math.sin(a0), 200 + 120 * math.cos(a1), 190 - 120 * math.sin(a1)
            out.append(f'<path d="M200 190 L{x0:.1f} {y0:.1f} A120 120 0 0 1 {x1:.1f} {y1:.1f} Z" fill="{c}"/>')
        band = lambda v: min(5.95, (v/50) if v<=100 else (2+(v-100)/100))
        ang = math.pi * (1 - band(now) / 6)
        nx, ny = 200 + 100 * math.cos(ang), 190 - 100 * math.sin(ang)
        ang2 = math.pi * (1 - band(prev) / 6)
        mx, my = 200 + 100 * math.cos(ang2), 190 - 100 * math.sin(ang2)
        return f'''<svg viewBox="0 0 400 240" role="img" aria-label="Air quality gauge: Delhi AQI {now} now, {prev} earlier">
<rect width="400" height="240" fill="#F6F8FA"/>{"".join(out)}<circle cx="200" cy="190" r="62" fill="#F6F8FA"/>
<line x1="200" y1="190" x2="{mx:.1f}" y2="{my:.1f}" stroke="#7C8796" stroke-width="3" stroke-dasharray="5 4"/>
<line x1="200" y1="190" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#2A323C" stroke-width="5" stroke-linecap="round"/><circle cx="200" cy="190" r="8" fill="#2A323C"/>
<text x="200" y="168" font-size="30" font-weight="800" text-anchor="middle" fill="#B8573C">{now}</text>
<text x="200" y="226" font-size="12" font-weight="700" text-anchor="middle" fill="#2A323C">AQI ‘poor’ · {nowl}</text>
<text x="16" y="26" font-size="12" font-weight="800" letter-spacing="1" fill="#3D5F92">DELHI AIR</text>
<text x="384" y="26" font-size="11" text-anchor="end" fill="#535C68">{prevl}: {prev} (dashed)</text>
</svg>'''
    if kind == "dhoni":
        return """<svg viewBox="0 0 400 260" role="img" aria-label="Graphic: a yellow number 7 jersey on a hanger with IPL career numbers: 278 matches, 5,439 runs, 264 sixes, 5 titles">
<rect width="400" height="260" fill="#0D2B5E"/><circle cx="340" cy="40" r="90" fill="#123B7A"/>
<path d="M60 70 l40-22 q20 14 40 0 l40 22 -14 34 -18-8 v120 h-96 v-120 l-18 8z" fill="#FFD23F" stroke="#F5A623" stroke-width="3"/>
<path d="M100 48 q20 18 40 0" fill="none" stroke="#0D2B5E" stroke-width="3"/><text x="120" y="160" font-size="64" font-weight="900" text-anchor="middle" fill="#0D2B5E">7</text>
<path d="M120 48 v-14 q0-8 8-8" fill="none" stroke="#E3F0FF" stroke-width="3"/>
<text x="218" y="64" font-size="13" font-weight="800" fill="#FFD23F" letter-spacing="1">IPL CAREER</text>
<g font-weight="800" fill="#fff"><text x="218" y="100" font-size="26">278</text><text x="300" y="100" font-size="26">5,439</text><text x="218" y="160" font-size="26">264</text><text x="300" y="160" font-size="26">5</text></g>
<g font-size="10.5" fill="#BBD3F5"><text x="218" y="116">matches</text><text x="300" y="116">runs</text><text x="218" y="176">sixes</text><text x="300" y="176">titles</text></g>
<rect x="218" y="196" width="160" height="26" rx="13" fill="#FFD23F"/><text x="298" y="213" font-size="11.5" font-weight="800" text-anchor="middle" fill="#0D2B5E">Now CSK mentor</text>
<text x="16" y="250" font-size="9.5" fill="#BBD3F5">Graphic: Pringital News · figures from CSK</text>
</svg>"""
    if kind == "quad":
        return """<svg viewBox="0 0 400 260" role="img" aria-label="Graphic: four linked circles for India, the US, Japan and Australia over a sea with a patrol plane, for new Quad initiatives">
<rect width="400" height="260" fill="#E8EEF6"/><path d="M0 190 q50-14 100 0 t100 0 t100 0 t100 0 V260 H0z" fill="#9DBCE8"/>
<g font-size="12" font-weight="800" text-anchor="middle" fill="#fff">
<circle cx="110" cy="80" r="36" fill="#FF9933"/><text x="110" y="85">INDIA</text>
<circle cx="200" cy="60" r="36" fill="#3D5F92"/><text x="200" y="65">US</text>
<circle cx="290" cy="80" r="36" fill="#D32F2F"/><text x="290" y="85">JAPAN</text>
<circle cx="200" cy="130" r="36" fill="#26A69A"/><text x="200" y="135">AUS</text></g>
<path d="M300 214 l40-8 -6 6 34 -2 -34 8 6 6z" fill="#2A323C"/>
<text x="16" y="250" font-size="10" font-weight="700" fill="#0D2B5E">Maritime surveillance · AI Accelerator · 2027 business forum</text>
</svg>"""
    if kind == "honour":
        figs = "".join(f'<g transform="translate({40+i*44} 120)"><circle r="11" fill="#2E7D32"/><path d="M-13 14 h26 v46 h-26z" fill="#2E7D32"/><path d="M13 20 l16 -16" stroke="#2E7D32" stroke-width="6" stroke-linecap="round"/></g>' for i in range(4))
        figs2 = "".join(f'<g transform="translate({228+i*44} 120)"><circle r="11" fill="#2E7D32"/><path d="M-13 14 h26 v46 h-26z" fill="#2E7D32"/><path d="M-13 20 l-16 -16" stroke="#2E7D32" stroke-width="6" stroke-linecap="round"/></g>' for i in range(4))
        return f"""<svg viewBox="0 0 400 260" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Illustration: two lines of green-shirted players applauding as blue-shirted players walk between them with a trophy">
<rect width="400" height="260" fill="#DCEFE0"/><rect y="190" width="400" height="70" fill="#7CB97F"/>{figs}{figs2}
<g transform="translate(200 128)"><circle r="12" fill="#1F5FBF"/><path d="M-14 15 h28 v50 h-28z" fill="#1F5FBF"/><path d="M-8 -40 h16 v14 q0 10 -8 12 q-8 -2 -8 -12z M-3 -14 h6 v8 h-6z" fill="#FFD23F"/></g>
<text x="200" y="36" font-size="15" font-weight="800" text-anchor="middle" fill="#0D2B5E">INDIA 2-1 PAKISTAN</text><text x="200" y="56" font-size="11" font-weight="700" text-anchor="middle" fill="#2E7D32">10th SAFF title · Dhaka</text>
<text x="200" y="248" font-size="9.5" font-weight="700" text-anchor="middle" fill="#0D2B5E">Illustration: Pringital News</text>
</svg>"""
    if kind == "help":
        return '''<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Warm illustration: two hands reaching toward each other under a film clapperboard and a heart">
<rect width="400" height="300" fill="#FFC93C"/><circle cx="200" cy="140" r="110" fill="#FFB02E"/>
<g transform="translate(150 40)"><rect width="100" height="58" rx="6" fill="#1E2630"/><path d="M0 0l100 0 0-16-100 0z" fill="#1E2630"/><g fill="#fff"><path d="M8-16l12 0 -8 16-12 0z"/><path d="M36-16l12 0 -8 16-12 0z"/><path d="M64-16l12 0 -8 16-12 0z"/></g><text x="50" y="36" font-size="13" font-weight="800" text-anchor="middle" fill="#FFC93C">TAKE 2</text></g>
<path d="M200 150c-14-18-44-6-30 18l30 26 30-26c14-24-16-36-30-18z" fill="#D32F2F"/>
<path d="M20 250 C80 230 120 210 168 214 l12 8 -10 8 -40 6" fill="#F6D9A0" stroke="#C98B2E" stroke-width="2.5"/>
<path d="M380 250 C320 230 280 210 232 214 l-12 8 10 8 40 6" fill="#E8B27F" stroke="#B86A6A" stroke-width="2.5"/>
<text x="200" y="286" font-size="11" font-weight="700" text-anchor="middle" fill="#0D2B5E">Illustration: Pringital News</text>
</svg>'''
    return ""


# ------------------------------------------------------------------ masthead (navy & press red)
BRAND = {"navy": "#1B3A7A", "red": "#D2232A"}


def masthead(d, sfx="p"):
    import random
    rnd = random.Random(7)
    cols = "".join(f'<rect x="{18+i*26}" y="10" width="18" height="76" fill="none" stroke="#BFD2F0" stroke-opacity=".16"/>' +
                   "".join(f'<line x1="{20+i*26}" x2="{34+i*26}" y1="{18+j*7}" y2="{18+j*7}" stroke="#BFD2F0" stroke-opacity=".18" stroke-width="2"/>' for j in range(9))
                   for i in range(9))
    pix = ""
    for _ in range(60):
        x = 470 + rnd.random() * 300; y = 6 + rnd.random() * 70; sz = 3 + rnd.random() * 6
        col = BRAND["red"] if rnd.random() < .28 else "#E8EEF8"
        pix += f'<rect x="{x:.0f}" y="{y:.0f}" width="{sz:.0f}" height="{sz:.0f}" fill="{col}" opacity="{.18+rnd.random()*.45:.2f}"/>'
    sky = ('<g fill="#0A1A3C"><path d="M0 104 V90 H40 V84 H60 V90 H90 V78 H104 V90 H130 V104Z"/>'
           '<path d="M150 104 V86 H170 V72 h4 v-6 h6 v6 h4 V86 H206 V104Z"/>'
           '<path d="M560 104 V74 H568 V66 H612 V74 H620 V104 H604 V84 a14 14 0 0 0 -28 0 V104Z"/>'
           '<path d="M690 104 L696 50 h8 l2 -6 h4 l2 6 h8 L726 104Z"/><path d="M736 104 V86 H760 V78 H780 V86 H800 V104Z"/></g>')
    px = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{w}" rx="1" fill="{c}"/>' for x, y, w, c in
                 [(62, 8, 8, BRAND["red"]), (74, 2, 6, "#FFFFFF"), (70, 18, 6, "#FFFFFF"), (82, 12, 7, BRAND["red"]), (86, 26, 5, "#FFFFFF"), (92, 4, 5, BRAND["red"]), (78, 32, 5, BRAND["red"]), (94, 20, 4, "#FFFFFF")])
    emb = (f'<svg class="pm-emb" viewBox="0 0 100 100" aria-hidden="true"><path d="M10 20 H58 L66 28 V90 H10 Z" fill="#FFFFFF"/>'
           f'<path d="M58 20 V28 H66" fill="none" stroke="#C9D4E6" stroke-width="2"/><rect x="16" y="27" width="34" height="6" rx="1.5" fill="{BRAND["red"]}"/>'
           '<g stroke="#9DB0CC" stroke-width="2.2" stroke-linecap="round"><line x1="16" y1="41" x2="36" y2="41"/><line x1="16" y1="48" x2="36" y2="48"/><line x1="16" y1="55" x2="36" y2="55"/><line x1="16" y1="62" x2="36" y2="62"/>'
           '<line x1="42" y1="41" x2="60" y2="41"/><line x1="42" y1="48" x2="60" y2="48"/><line x1="42" y1="55" x2="60" y2="55"/><line x1="16" y1="72" x2="60" y2="72"/><line x1="16" y1="79" x2="52" y2="79"/></g>'
           f'{px}<path d="M66 52 l18 -18 l8 8 l-18 18 l-11 3 z" fill="{BRAND["red"]}"/><path d="M63 63 l3 -11 l8 8 z" fill="#FFFFFF"/></svg>')
    badge = (f'<svg viewBox="0 0 100 100" aria-hidden="true"><defs><path id="pmring{sfx}" d="M50,50 m-37,0 a37,37 0 1,1 74,0 a37,37 0 1,1 -74,0"/></defs>'
             f'<circle cx="50" cy="50" r="49" fill="{BRAND["red"]}"/><circle cx="50" cy="50" r="27" fill="#0E2350"/><path d="M43 37 L64 50 L43 63 Z" fill="#FFFFFF"/>'
             f'<g class="pm-ring"><text font-family="Montserrat,Inter,Arial,sans-serif" font-size="11" font-weight="800" letter-spacing="1.4" fill="#FFFFFF"><textPath href="#pmring{sfx}">4-MIN BULLETIN • LISTEN •</textPath></text></g></svg>')
    short = f'{d:%a}, {d.day} {d:%b %Y}'
    return f'''<header class="pmast">
  <svg class="pm-bg" viewBox="0 0 800 104" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
    <defs><linearGradient id="pmbg{sfx}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0E2350"/><stop offset=".55" stop-color="#1B3A7A"/><stop offset="1" stop-color="#25539E"/></linearGradient>
    <radialGradient id="pmsun{sfx}"><stop offset="0" stop-color="#F3C969"/><stop offset="1" stop-color="#F3C969" stop-opacity="0"/></radialGradient></defs>
    <rect width="800" height="104" fill="url(#pmbg{sfx})"/><circle cx="640" cy="96" r="80" fill="url(#pmsun{sfx})" opacity=".45"/>{cols}{pix}
    <path d="M0 98 C200 82 420 104 800 88 V104 H0Z" fill="#4F7BC4" opacity=".25"/>{sky}<rect y="100" width="800" height="4" fill="{BRAND["red"]}"/>
  </svg>
  <div class="pm-in">
    <a class="pm-brand" href="/" aria-label="Pringital News home">{emb}<span class="pm-wm"><span class="pm-w1">PRIN<span class="pm-g">GITAL</span><span class="pm-dots"><i></i><i></i><i></i></span></span>
      <span class="pm-w2"><span class="pm-news">NEWS</span><span class="pm-sub">Credible like Print · Fast like Digital</span></span></span></a>
    <div class="pm-ed"><div class="pm-word">The Living Newspaper</div><div class="pm-rule"></div><div class="pm-line">New Delhi · {short}</div><div class="pm-latest">● Latest Edition</div></div>
  </div>
  <a class="pm-listen" href="/archive/{d.isoformat()}/bulletin/" title="Listen to the 4-minute bulletin" aria-label="Listen to the 4-minute bulletin">{badge}</a>
</header>'''


MAST_CSS = """
/* Brand colours: ink navy and press red */
:root{--accent:#1B3A7A;--accent-soft:#E6ECF7;--hl:#EEF2FA;--warm:#D2232A;--warm-soft:#FDECEC;--warm-ink:#A3161C;--warm-line:#F5CDCF}
:root[data-theme="dark"]{--accent:#9DB8F0;--accent-soft:#1F2B44;--hl:#1F2B44;--warm:#F06A6F;--warm-soft:#3A1D20;--warm-ink:#F5A3A6;--warm-line:#4A2629}
/* masthead */
.pmast{position:relative;aspect-ratio:800/104;min-height:84px;border-radius:10px;overflow:hidden;color:#fff;container-type:inline-size;margin-bottom:8px}
.pmast .pm-bg{position:absolute;inset:0;width:100%;height:100%}
.pmast .pm-in{position:relative;display:flex;align-items:center;height:100%;padding:0 14cqw 0 2.4cqw;gap:4cqw}
.pmast a{color:#fff;text-decoration:none}
.pm-brand{flex:0 0 47cqw;display:flex;align-items:center;gap:1.6cqw;min-width:0}
.pm-emb{flex:0 0 8.6cqw;width:8.6cqw;height:8.6cqw;filter:drop-shadow(0 .5cqw 1.2cqw rgba(0,0,0,.35))}
.pm-wm{min-width:0;display:flex;flex-direction:column;gap:.8cqw;font-family:Montserrat,Inter,Arial,sans-serif}
.pm-w1{font-weight:900;font-size:5.3cqw;line-height:.9;letter-spacing:-.025em;white-space:nowrap;text-shadow:0 .25cqw 1cqw rgba(0,0,0,.35);display:flex;align-items:flex-end}
.pm-g{color:#D2232A;text-shadow:0 .2cqw .6cqw rgba(0,0,0,.25)}
.pm-dots{display:inline-flex;gap:.35cqw;margin:0 0 .9cqw .5cqw;align-items:flex-end}
.pm-dots i{display:block;width:.9cqw;height:.9cqw;background:#D2232A;border-radius:.15cqw}
.pm-dots i:nth-child(2){width:.65cqw;height:.65cqw;background:#fff;margin-bottom:1.1cqw}
.pm-dots i:nth-child(3){width:.5cqw;height:.5cqw;margin-bottom:2cqw}
.pm-w2{display:flex;align-items:center;gap:1cqw;white-space:nowrap}
.pm-news{font-weight:900;font-size:2.1cqw;letter-spacing:.5em;padding:.35cqw .4cqw .35cqw .9cqw;background:#D2232A;color:#fff;border-radius:.5cqw}
.pm-sub{font-weight:600;font-size:1.15cqw;letter-spacing:.04em;opacity:.9;font-style:italic}
.pm-ed{min-width:0;display:flex;flex-direction:column;gap:.6cqw;font-family:Montserrat,Inter,Arial,sans-serif}
.pm-word{white-space:nowrap;font-weight:900;font-size:2.8cqw;line-height:1;text-shadow:0 .2cqw .8cqw rgba(0,0,0,.35)}
.pm-rule{height:.45cqw;width:60%;background:#D2232A;border-radius:1cqw}
.pm-line{white-space:nowrap;font-weight:700;font-size:1.45cqw;letter-spacing:.08em;text-transform:uppercase;opacity:.92}
.pm-latest{font-weight:800;font-size:1.05cqw;letter-spacing:.14em;text-transform:uppercase;color:#FFD9DA}
.pm-listen{position:absolute;right:2.2cqw;top:50%;transform:translateY(-50%);width:9.6cqw;aspect-ratio:1;display:block;border-radius:50%;box-shadow:0 .5cqw 1.8cqw rgba(0,0,0,.35)}
.pm-listen svg{width:100%;height:100%;display:block}
.pm-ring{transform-box:view-box;transform-origin:50px 50px;animation:pmspin 18s linear infinite}
@keyframes pmspin{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){.pm-ring{animation:none}}
.pm-listen:focus-visible,.pm-brand:focus-visible{outline:3px solid #fff;outline-offset:3px}
html[data-mode="paper"] .pmast{border-radius:6px;margin-bottom:0}
@media (max-width:640px){
 html[data-mode="web"] .pmast{aspect-ratio:auto;min-height:0;border-radius:12px}
 html[data-mode="web"] .pmast .pm-in{flex-wrap:wrap;padding:14px 14px 16px;gap:12px}
 html[data-mode="web"] .pm-brand{flex:1 1 100%;gap:10px}
 html[data-mode="web"] .pm-emb{flex-basis:44px;width:44px;height:44px}
 html[data-mode="web"] .pm-w1{font-size:clamp(24px,8vw,32px)}
 html[data-mode="web"] .pm-dots i{width:5px;height:5px}
 html[data-mode="web"] .pm-w2{flex-wrap:wrap;gap:5px 8px}
 html[data-mode="web"] .pm-news{font-size:11px;padding:2px 3px 2px 6px}
 html[data-mode="web"] .pm-sub{font-size:clamp(9px,2.7vw,11px);white-space:nowrap}
 html[data-mode="web"] .pm-ed{flex:1 1 auto;padding-right:74px}
 html[data-mode="web"] .pm-word{font-size:clamp(14px,4.4vw,17px)}
 html[data-mode="web"] .pm-rule{height:3px}
 html[data-mode="web"] .pm-line{font-size:10px}
 html[data-mode="web"] .pm-latest{font-size:8.5px}
 html[data-mode="web"] .pm-listen{width:60px;right:14px;top:auto;bottom:14px;transform:none}
}
"""


# ------------------------------------------------------------------ paper page
def side(blocks):
    out = []
    for i, b in enumerate(blocks):
        out.append(f'<div class="boxhead{" sub" if i else ""}">{b["name"]}</div><ul>')
        for k, h, u in b["items"]:
            out.append(f'<li><span class="k">{esc(k)}</span>{a(u, esc(h))}{arrow(u)}</li>')
        out.append('</ul>')
    return "".join(out)


def paper_main(E):
    S, L, D = E["single"], E["lead"], E["second"]
    latest = "".join(f'<li><h3>{a(u, esc(h))}{arrow(u)}</h3><p>{esc(t)}</p></li>' for h, t, u in L["latest"])
    more = "".join(f'<li><h3>{a(u, esc(h))}{arrow(u)}</h3><p>{esc(t)}</p></li>' for h, t, u in D["more"])
    ptr = "".join(f'<li>{a(u, esc(h))}{arrow(u)}</li>' for h, u in D["pointers"])
    band = "".join(f'<section><div class="sec">{esc(b["sec"])}</div><ul>' + "".join(
        f'<li><h3>{a(u, esc(h))}{arrow(u)}</h3><p>{esc(t)}</p></li>' for h, t, u in b["items"]) + '</ul></section>' for b in E["band"])
    duo = "".join(f'<article><h3>{a(u, esc(h))}{arrow(u)}</h3><p>{esc(t)}</p></article>' for h, t, u in E["duo"])
    H = E["human"]
    return f'''<main class="main">
    <aside class="side l">{side(E["left"])}</aside>
    <section class="center">
      <div class="topblock">
        <article class="single"><span class="kick">{S["k"]}</span><h2>{a(S["url"], esc(S["h"]))}</h2>
          <figure class="ill">{art(S["art"])}<figcaption>Illustration: Pringital News</figcaption></figure>
          <p class="copy">{S["copy"]} {arrow(S["url"])}</p></article>
        <article class="lead"><span class="kick">{L["k"]}</span><h2>{a(L["url"], esc(L["h"]))}</h2>
          <div class="leadflow"><figure class="ill">{art(L["art"])}<figcaption>Illustration: Pringital News</figcaption></figure>
            <p class="copy">{L["copy"]} {arrow(L["url"])}</p></div>
          <div class="latest"><div class="lth"><span class="dot"></span>LATEST</div><ul>{latest}</ul></div>
        </article>
      </div>
      <article class="second">
        <div class="head"><span class="kick">{D["k"]}</span><h2>{a(D["url"], esc(D["h"]))}</h2></div>
        <div class="cityl"><figure class="ill">{art(D["art"])}<figcaption>Graphic: Pringital News · CPCB data</figcaption></figure>
          <p class="copy">{D["copy"]} {arrow(D["url"])}</p><ul class="more">{more}</ul></div>
        <div class="pointers"><div class="ph">ALSO IN DELHI–NCR</div><ul>{ptr}</ul></div>
      </article>
      <div class="band">{band}</div>
      <div class="duo">{duo}
        <article class="wide human"><span class="kick">{H["k"]}</span><h3>{a(H["url"], esc(H["h"]))}{arrow(H["url"])}</h3>
          <div class="hbody"><figure class="hfig ill">{art(H["art"])}</figure><p class="copy">{H["copy"]} {arrow(H["url"])}</p></div></article>
      </div>
    </section>
    <aside class="side r">{side(E["right"])}</aside>
  </main>'''


# ------------------------------------------------------------------ web page
def web(E, dateline):
    S, L, D, H = E["single"], E["lead"], E["second"], E["human"]
    def wl(h, u, k=""):
        return f'<li><span class="wk">{esc(k)}</span><a class="wl" href="{esc(u)}" target="_blank" rel="noopener">{esc(h)}<span class="arr" aria-hidden="true">↗</span></a></li>'
    def wl2(h, t, u):
        return f'<li><a class="wl" href="{esc(u)}" target="_blank" rel="noopener">{esc(h)}<span class="arr" aria-hidden="true">↗</span></a><p>{esc(t)}</p></li>'
    def card(x, cls="wcard"):
        return (f'<article class="{cls}"><figure class="wfig">{art(x["art"])}</figure><div class="wtext"><span class="wkick">{x["k"]}</span>'
                f'<h2>{a(x["url"], esc(x["h"]))}</h2><p>{x["copy"]}</p><a class="wmore" href="{esc(x["url"])}" target="_blank" rel="noopener">Read the full story<span class="arr" aria-hidden="true">↗</span></a></div></article>')
    secs = [f'<section class="wsec"><h3 class="wsh"><span>{b["name"].title()}</span></h3><ul class="wlist">' + "".join(wl(h, u, k) for k, h, u in b["items"]) + '</ul></section>' for b in E["left"] + E["right"]]
    secs.insert(1, '<section class="wsec"><h3 class="wsh"><span>Delhi–NCR</span></h3><ul class="wlist">' + "".join(wl2(h, t, u) for h, t, u in D["more"]) + "".join(wl(h, u) for h, u in D["pointers"]) + '</ul></section>')
    secs += [f'<section class="wsec"><h3 class="wsh"><span>{esc(b["sec"])}</span></h3><ul class="wlist">' + "".join(wl2(h, t, u) for h, t, u in b["items"]) + '</ul></section>' for b in E["band"]]
    depth = "".join(f'<article class="wdep"><h3><a href="{esc(u)}" target="_blank" rel="noopener">{esc(h)}<span class="arr" aria-hidden="true">↗</span></a></h3><p>{esc(t)}</p></article>' for h, t, u in E["duo"])
    d = datetime.date.fromisoformat(E["date"])
    return f'''<div class="w">
{masthead(d, "w")}
<section class="wtop">
{card(L, "wlead")}
<section class="wsec wlatest"><h3 class="wsh"><span>Latest</span></h3><ul class="wlist">{"".join(wl2(h, t, u) for h, t, u in L["latest"])}</ul></section>
<div class="wpair">{card(S)}{card(D)}</div>
</section>
<div class="wbreak" role="presentation"></div><h2 class="wzone"><span>In brief</span></h2>
<div class="wbriefs">{"".join(secs)}</div>
<div class="wbreak" role="presentation"></div><h2 class="wzone"><span>In depth</span></h2>
<div class="wdepth">{depth}</div>
<div class="wbreak" role="presentation"></div><h2 class="wzone"><span>Human story</span></h2>
{card(H, "wcard whuman")}
<footer class="imprint"><span class="who">A Journalism Initiative by <span>Sudhanshu Srivastava</span> / 8383823531</span><span>Pringital News · pringital.com</span></footer>
</div>'''


A4_CSS = f"""
/* A4 sizing: the paper page is {PW} x {PH} px (1 : 1.414) and every column ends flush. */
html[data-mode="paper"] #fit{{max-width:{PW}px}}
html[data-mode="paper"] #page{{width:{PW}px;height:{PH}px;min-height:0;overflow:hidden;display:flex;flex-direction:column;gap:7px}}
html[data-mode="paper"] .main{{flex:1;min-height:0;grid-template-columns:172px minmax(0,1fr) 172px}}
html[data-mode="paper"] .side{{display:flex;flex-direction:column;min-height:0}}
html[data-mode="paper"] .side ul{{flex:1 1 auto;display:flex;flex-direction:column;justify-content:space-around}}
html[data-mode="paper"] .side li{{font-size:11.7px;line-height:1.22}}
html[data-mode="paper"] .side .k{{font-size:7.6px}}
html[data-mode="paper"] .center{{min-height:0}}
html[data-mode="paper"] .duo{{flex:1 0 auto;align-content:stretch}}
html[data-mode="paper"] .single h2{{font-size:17px}}
html[data-mode="paper"] .lead h2{{font-size:28px;font-weight:800}}
html[data-mode="paper"] .copy{{font-size:10.6px;line-height:1.38}}
html[data-mode="paper"] .second h2{{font-size:21px;font-weight:800}}
html[data-mode="paper"] .band h3{{font-size:10.8px}}
html[data-mode="paper"] .band p{{font-size:9.2px}}
html[data-mode="paper"] .duo h3{{font-size:15px}}
html[data-mode="paper"] .duo p{{font-size:9.8px}}
html[data-mode="paper"] .duo .human .hbody{{grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:12px;align-items:stretch}}
html[data-mode="paper"] .duo .human .hfig{{position:relative;min-height:110px}}
html[data-mode="paper"] .duo .human .hfig svg{{position:absolute;inset:0;width:100%;height:100%;border-radius:6px}}
html[data-mode="paper"] .duo .human .hbody .copy{{columns:2;column-gap:12px;column-rule:1px solid var(--rule);text-align:left;font-size:12.2px;line-height:1.42}}
html[data-mode="paper"] .hbody figure{{margin:0}}
html[data-mode="paper"] .ill svg{{display:block;width:100%;height:auto}}
html[data-mode="paper"] .latest h3{{font-size:11px}}
html[data-mode="paper"] .latest p{{font-size:9.2px}}
"""


def build(E, tpl, tdate):
    d = datetime.date.fromisoformat(E["date"])
    t = datetime.date.fromisoformat(tdate)
    long_new, long_old = f'{d:%A}, {d.day} {d:%B %Y}', f'{t:%A}, {t.day} {t:%B %Y}'
    i_body = tpl.index("<body>")
    head = tpl[:i_body].replace("</style>", A4_CSS + "</style>", 1) if "</style>" in tpl[:i_body] else tpl[:i_body]
    # last </style> in head gets the A4 rules
    j = tpl[:i_body].rfind("</style>")
    head = tpl[:j] + A4_CSS + MAST_CSS + tpl[j:i_body]
    head = head.replace("0,600;0,700;1,400;1,600", "0,600;0,700;0,800;0,900;1,400;1,600")
    i_main = tpl.index('<main class="main">')
    top = tpl[i_body:i_main]
    top = re.sub(r'<div class="paperonly">.*?<div class="webonly">.*?<div class="meta">.*?</div>\s*</div>\s*</div>', masthead(d), top, count=1, flags=re.S)
    i_imp = tpl.index('<footer class="imprint">')
    i_w = tpl.index('<div class="w">')
    footer = tpl[i_imp:i_w]
    i_script = tpl.index("<script>", i_w)
    tail = tpl[i_script:]
    page = head + top + paper_main(E) + "\n\n  " + footer + web(E, long_new) + "\n" + tail
    page = page.replace(long_old, long_new).replace(tdate, E["date"])
    page = page.replace(f'{t.day}%20{t:%B}%20{t.year}', f'{d.day}%20{d:%B}%20{d.year}')
    page = page.replace(f'{t:%A}%2C%20{t.day}', f'{d:%A}%2C%20{d.day}')
    page = page.replace(f'{t.day}-{t:%b}-{t.year}', f'{d.day}-{d:%b}-{d.year}')
    page = page.replace("var s=Math.min(1,(fit.clientWidth||794)/794);", "var PW=page.offsetWidth||%d;var s=Math.min(1,(fit.clientWidth||PW)/PW);" % PW)
    if "/assets/js/listen.js" not in page:
        i = page.rindex("</body>")
        page = page[:i] + '<script src="/assets/js/listen.js" defer></script>\n' + page[i:]
    return page


if __name__ == "__main__":
    E = json.load(open(sys.argv[1], encoding="utf-8"))
    tdate = sys.argv[2] if len(sys.argv) > 2 else "2026-11-15"
    tpath = os.environ.get("PN_TEMPLATE") or os.path.join(ROOT, "archive", tdate, "index.html")
    tpl = open(tpath, encoding="utf-8").read()
    # undo publish.py's archived markings if the template has been archived since
    tpl = re.sub(r'<div style="background:var\(--ink\)[^>]*>ARCHIVED EDITION.*?</div>\s*', '', tpl, flags=re.S)
    tpl = tpl.replace("Pringital News · Archive · ", "Pringital News · ").replace("● Archived Edition", "● Latest Edition")
    # use the template as it was published (before publish.py marked it archived)
    tpl = re.sub(r'<div class="archbanner".*?</div>\s*', '', tpl, flags=re.S)
    out = build(E, tpl, tdate)
    for p in ("today", f"archive/{E['date']}"):
        os.makedirs(os.path.join(ROOT, p), exist_ok=True)
        open(os.path.join(ROOT, p, "index.html"), "w", encoding="utf-8").write(out)
    n = sum(len(b["items"]) for b in E["left"] + E["right"])
    print("side headlines:", n)
