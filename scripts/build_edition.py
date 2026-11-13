#!/usr/bin/env python3
"""Build a Pringital News edition (paper A4 + web modes) from editions/YYYY-MM-DD.json.

Usage: python3 scripts/build_edition.py editions/2026-11-13.json
Writes today/index.html and archive/YYYY-MM-DD/index.html.
"""
import json, sys, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "scripts")
RED = "#D32F2F"


def rd(p):
    with open(os.path.join(HERE, p), encoding="utf-8") as f:
        return f.read()


def a(url, text, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="{html.escape(url)}" target="_blank" rel="noopener">{text}</a>'


def arrow(url):
    return f'<a class="dn" href="{html.escape(url)}" target="_blank" rel="noopener" aria-label="Full story">↗</a>'

# ---------------------------------------------------------------- graphics

IMG = {}  # name -> (url, w, h, alt)


def art(kind):
    if kind.startswith("img:"):
        n = kind[4:]
        url, w, h, alt = IMG[n]
        return f'<img class="photo" src="{url}" width="{w}" height="{h}" alt="{html.escape(alt)}" loading="lazy">'
    if kind == "exports":
        return '''<svg viewBox="0 0 300 190" role="img" aria-label="Bar chart: total exports $89.99 bn, goods exports $49.47 bn, goods trade deficit $39.88 bn, overall deficit $20.09 bn, October 2026">
<rect width="300" height="190" rx="6" fill="#EEF3FA"/>
<text x="14" y="22" font-size="10" font-weight="700" fill="#2A323C" letter-spacing="1">OCTOBER 2026 · US$ BILLION</text>
<line x1="14" y1="160" x2="286" y2="160" stroke="#7C8796" stroke-width="1"/>
<g font-size="11" font-weight="700" text-anchor="middle">
<rect x="26" y="40" width="48" height="120" rx="3" fill="#3D5F92"/><text x="50" y="34" fill="#3D5F92">89.99</text>
<rect x="92" y="94" width="48" height="66" rx="3" fill="#5E8C6A"/><text x="116" y="88" fill="#5E8C6A">49.47</text>
<rect x="158" y="107" width="48" height="53" rx="3" fill="#D98C73"/><text x="182" y="101" fill="#B8573C">39.88</text>
<rect x="224" y="133" width="48" height="27" rx="3" fill="#C9853D"/><text x="248" y="127" fill="#8A5420">20.09</text>
</g>
<g font-size="8.5" fill="#535C68" text-anchor="middle">
<text x="50" y="172">Total</text><text x="50" y="182">exports</text>
<text x="116" y="172">Goods</text><text x="116" y="182">exports (record)</text>
<text x="182" y="172">Goods</text><text x="182" y="182">deficit</text>
<text x="248" y="172">Overall</text><text x="248" y="182">deficit</text>
</g></svg>'''
    if kind == "gulf":
        return '''<svg viewBox="0 0 300 200" role="img" aria-label="Schematic map of the Gulf showing Bahrain, Iran and the Strait of Hormuz">
<rect width="300" height="200" rx="6" fill="#DCE8F3"/>
<path d="M0 0H300V70Q250 60 230 90Q200 70 170 64Q130 50 90 30Q50 18 0 26Z" fill="#EADFCB"/>
<path d="M0 200V96Q40 110 70 118Q96 128 104 150Q120 140 150 150Q190 160 214 134Q236 126 252 140Q270 150 300 140V200Z" fill="#EADFCB"/>
<text x="150" y="42" font-size="12" font-weight="700" fill="#8A5420" text-anchor="middle" letter-spacing="2">IRAN</text>
<text x="70" y="178" font-size="10" font-weight="700" fill="#8A5420" letter-spacing="1">SAUDI ARABIA</text>
<text x="226" y="178" font-size="10" font-weight="700" fill="#8A5420">UAE</text>
<circle cx="88" cy="108" r="6" fill="#D32F2F"/><circle cx="88" cy="108" r="11" fill="none" stroke="#D32F2F" stroke-width="1.5"/>
<text x="100" y="104" font-size="9.5" font-weight="700" fill="#2A323C">Bahrain</text><text x="100" y="115" font-size="8" fill="#535C68">US radar targeted</text>
<path d="M246 96l7-12 7 12z" fill="#D32F2F"/><text x="262" y="86" font-size="9.5" font-weight="700" fill="#2A323C" text-anchor="end">Hormuz</text>
<text x="290" y="114" font-size="8" fill="#535C68" text-anchor="end">LPG tanker blast</text>
<text x="150" y="98" font-size="9" font-style="italic" fill="#3D5F92" text-anchor="middle">The Gulf</text>
</svg>'''
    if kind == "rocket":
        return '''<svg viewBox="0 0 200 150" role="img" aria-label="PSLV rocket on the launch pad at Sriharikota">
<rect width="200" height="150" rx="5" fill="#E8EEF6"/>
<circle cx="160" cy="34" r="16" fill="#EBD58E"/>
<rect y="124" width="200" height="26" fill="#C9B48F"/>
<rect x="60" y="34" width="10" height="92" fill="#7C8796"/><g stroke="#7C8796" stroke-width="2"><path d="M70 50h18M70 74h18M70 98h18"/></g>
<path d="M100 18q8 10 8 26v72h-16v-72q0-16 8-26z" fill="#FFFFFF" stroke="#3D5F92" stroke-width="2"/>
<rect x="92" y="64" width="16" height="16" fill="#D98C73"/>
<path d="M92 104l-10 16h10zM108 104l10 16h-10z" fill="#3D5F92"/>
<path d="M95 118q5 14 5 24q0-10 5-24z" fill="#E8B27F"/>
<text x="100" y="58" font-size="7" font-weight="700" fill="#3D5F92" text-anchor="middle">PS3</text>
</svg>'''
    if kind == "train":
        return """<svg viewBox="0 0 300 120" role="img" aria-label="Vande Bharat train running along the ghats">
<rect width="300" height="120" rx="6" fill="#E8EEF6"/>
<path d="M0 78 L50 40 L90 66 L140 30 L200 70 L250 44 L300 70 V120 H0Z" fill="#9CC9A6"/>
<rect y="96" width="300" height="24" fill="#C9B48F"/><g stroke="#7C8796" stroke-width="2"><path d="M0 104H300M0 110H300"/></g>
<path d="M30 74h196q34 0 50 22H30z" fill="#FFFFFF" stroke="#3D5F92" stroke-width="2"/>
<path d="M30 88h236" stroke="#D98C73" stroke-width="5"/>
<g fill="#3D5F92"><rect x="40" y="78" width="22" height="7" rx="2"/><rect x="70" y="78" width="22" height="7" rx="2"/><rect x="100" y="78" width="22" height="7" rx="2"/><rect x="130" y="78" width="22" height="7" rx="2"/><rect x="160" y="78" width="22" height="7" rx="2"/><rect x="190" y="78" width="22" height="7" rx="2"/></g>
<path d="M236 78h22q8 4 12 10h-34z" fill="#3D5F92"/>
<text x="16" y="22" font-size="10" font-weight="800" fill="#3D5F92" letter-spacing="1">BENGALURU → MANGALURU → MADGAON</text>
</svg>"""
    if kind == "cat":
        return """<svg viewBox="0 0 220 150" role="img" aria-label="A cat meowing at a treat box while a person watches">
<rect width="220" height="150" rx="6" fill="#FBF1E6"/>
<rect y="120" width="220" height="30" fill="#EADFCB"/>
<rect x="138" y="88" width="56" height="34" rx="4" fill="#DCE8F3" stroke="#7C8796" stroke-width="2"/><circle cx="166" cy="106" r="7" fill="#D98C73"/>
<g fill="#E8B27F"><ellipse cx="72" cy="104" rx="30" ry="20"/><circle cx="96" cy="78" r="17"/><path d="M84 66l2-16 10 12zM100 62l10-12 2 16z"/><path d="M42 104q-20-6-16-30" stroke="#E8B27F" stroke-width="7" fill="none" stroke-linecap="round"/></g>
<circle cx="92" cy="76" r="2.4" fill="#2A323C"/><circle cx="102" cy="76" r="2.4" fill="#2A323C"/><ellipse cx="98" cy="86" rx="3" ry="2.6" fill="#B86A6A"/>
<path d="M118 70q12-8 22-2" stroke="#3D5F92" stroke-width="2" fill="none"/>
<rect x="116" y="28" width="62" height="26" rx="12" fill="#FFFFFF" stroke="#3D5F92" stroke-width="1.5"/><path d="M128 52l-6 10 14-8z" fill="#FFFFFF" stroke="#3D5F92" stroke-width="1.5"/>
<text x="147" y="46" font-size="12" font-weight="800" fill="#D32F2F" text-anchor="middle">MEOW!</text>
<text x="196" y="22" font-size="20" text-anchor="middle" fill="#D98C73">♥</text>
</svg>"""
    if kind == "beach":
        return '''<svg viewBox="0 0 200 150" role="img" aria-label="Beach with a blue flag, waves and the sun">
<rect width="200" height="150" rx="5" fill="#DCE8F3"/>
<circle cx="40" cy="38" r="15" fill="#EBD58E"/>
<path d="M0 86q25-8 50 0t50 0t50 0t50 0V150H0z" fill="#9DBCE8"/>
<path d="M0 100q25-8 50 0t50 0t50 0t50 0" fill="none" stroke="#fff" stroke-width="2"/>
<path d="M0 118q60-20 200-8V150H0z" fill="#EADFCB"/>
<rect x="140" y="40" width="3" height="80" fill="#535C68"/>
<path d="M143 42h38l-8 12 8 12h-38z" fill="#1F5FBF"/>
<text x="160" y="58" font-size="7" font-weight="700" fill="#fff" text-anchor="middle">BLUE</text>
<path d="M60 128l24-10 4 10z" fill="#D98C73"/>
</svg>'''
    return ""


def bulletin_graphic(sfx='p'):
    return """<svg class="bgfx" viewBox="0 0 120 120" role="img" aria-label="News bulletin: listen in 4 minutes">
<defs><linearGradient id="bgg{sfx}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF6F61"/><stop offset=".35" stop-color="#FFB300"/><stop offset=".7" stop-color="#26A69A"/><stop offset="1" stop-color="#1F3F7A"/></linearGradient>
<linearGradient id="bgm{sfx}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E53935"/><stop offset="1" stop-color="#1F3F7A"/></linearGradient></defs>
<rect x="1" y="1" width="118" height="118" rx="14" fill="url(#bgg{sfx})"/>
<rect x="6" y="6" width="108" height="108" rx="10" fill="#FFFFFF"/>
<text x="60" y="22" font-family="Montserrat,Arial" font-size="9.5" font-weight="800" letter-spacing="1.4" fill="#D32F2F" text-anchor="middle">NEWS BULLETIN</text>
<g transform="translate(46 28)"><rect x="6" y="0" width="16" height="28" rx="8" fill="url(#bgm{sfx})"/><path d="M0 18q0 14 14 14t14-14" fill="none" stroke="#1F3F7A" stroke-width="3" stroke-linecap="round"/><rect x="12" y="32" width="4" height="7" fill="#1F3F7A"/><rect x="5" y="39" width="18" height="3.5" rx="1.7" fill="#1F3F7A"/></g>
<g stroke-width="3" stroke-linecap="round" fill="none"><path d="M82 34q6 8 0 16" stroke="#FFB300"/><path d="M89 29q11 13 0 26" stroke="#26A69A"/><path d="M38 34q-6 8 0 16" stroke="#FFB300"/><path d="M31 29q-11 13 0 26" stroke="#26A69A"/></g>
<text x="60" y="86" font-family="Montserrat,Arial" font-size="14" font-weight="700" font-style="italic" fill="#1F3F7A" text-anchor="middle">Now Listen</text>
<rect x="30" y="94" width="60" height="15" rx="7.5" fill="#D32F2F"/><text x="60" y="105" font-family="Montserrat,Arial" font-size="9" font-weight="800" fill="#FFFFFF" text-anchor="middle">▶ 4 MIN</text>
</svg>""".replace('{sfx}', sfx)


# ---------------------------------------------------------------- paper

PAPER_CSS = """
html[data-mode="web"] #fit{display:none}
html[data-mode="paper"] .w{display:none}
html[data-mode="paper"] body{padding:0 max(16px,env(safe-area-inset-right,0px)) 0 max(16px,env(safe-area-inset-left,0px))}
#fit{width:100%;max-width:980px;margin:20px auto 28px;overflow:hidden}
#page{width:980px;height:1386px;overflow:hidden;transform-origin:0 0;background:var(--card);box-shadow:0 16px 40px -24px var(--shadow);padding:20px 24px 14px;display:flex;flex-direction:column;gap:6px;color:var(--ink);font-family:var(--font);letter-spacing:-.005em}
html[data-theme="dark"] #page{border:1px solid var(--rule)}
#page a{color:inherit;text-decoration:none}
#page a:hover{text-decoration:underline}
#page h1,#page h2,#page h3,#page p,#page ul{margin:0}
#page ul{list-style:none;padding:0}
#page .dn{font-size:11px!important;font-weight:800;line-height:1;display:inline-block;margin-left:3px;color:#D32F2F!important;text-decoration:none!important;vertical-align:baseline}
#page .dn:hover{color:#1F3F7A!important}
#page h2 a,#page h3 a,#page .p-list a{text-decoration:none;border-bottom:1px dotted transparent}
#page h2 a:hover,#page h3 a:hover,#page .p-list a:hover{border-bottom-color:currentColor;text-decoration:none}
.p-top{display:flex;justify-content:space-between;font-size:8.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
.p-top .live{color:%(red)s}
.p-mast{border-top:3px solid var(--ink);border-bottom:1px solid var(--ink);padding:5px 0 4px;display:grid;grid-template-columns:172px 1fr 150px;align-items:center;gap:10px}
.p-mast .bgl{display:block;line-height:0}
.p-mast .bgfx{width:172px;height:74px;display:block}
.p-mast h1{font-size:44px;font-weight:600;letter-spacing:.02em;text-align:center;line-height:1;white-space:nowrap}
.p-mast h1 span{color:var(--accent)}
.p-mast .ear{text-align:right;font-size:8.5px;line-height:1.4}
.p-mast .ear strong{display:block;font-size:9px;letter-spacing:.08em}
.p-slogan{text-align:center;border-bottom:3px double var(--ink);padding:1px 0 4px;font-size:17px;font-weight:700;font-style:italic;color:%(red)s;letter-spacing:.01em}
.p-slogan i{display:inline-block;width:5px;height:5px;background:%(red)s;transform:rotate(45deg);margin:0 12px;vertical-align:4px}
.p-main{flex:1;min-height:0;display:grid;grid-template-columns:160px minmax(0,1fr) 160px}
.p-side{display:flex;flex-direction:column;min-height:0}
.p-side.l{padding-right:8px;border-right:1px solid var(--ink)}
.p-side.r{padding-left:8px;border-left:1px solid var(--ink)}
.p-cat{background:var(--ink);color:var(--card);text-align:center;font-size:8.5px;font-weight:800;letter-spacing:.16em;padding:2px 0;margin:5px 0 1px}
.p-cat.first{margin-top:0}
.p-cat.alt{background:%(red)s;color:#fff}
.p-topst{padding:3px 0 4px;border-bottom:1px solid var(--rule)}
.p-topst h3{font-size:12.4px;font-weight:700;line-height:1.12;margin:1px 0 3px}
.p-topst p{font-size:8.6px;line-height:1.3;color:var(--muted)}
.p-k{font-size:6.6px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:%(red)s;margin-right:3px}
.p-side .p-list{flex:1 1 auto;display:flex;flex-direction:column;justify-content:space-around}
.p-list li{border-top:1px solid var(--rule);padding:2.6px 0;font-size:9.6px;font-weight:700;line-height:1.17}
.p-list li:first-child{border-top:0}
.p-bot{border-top:2px solid var(--ink);padding-top:4px}
.p-bot svg{display:block;width:100%;height:auto;border-radius:4px;margin:3px 0}
.p-bot h3{font-size:11px;font-weight:700;line-height:1.14}
.p-bot p{font-size:8.3px;line-height:1.28;color:var(--muted)}
.p-center{padding:0 10px;display:flex;flex-direction:column;gap:6px;min-width:0;min-height:0}
.p-kick{display:block;font-size:7px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:%(red)s;margin-bottom:1px}
.p-copy{font-size:9.4px;line-height:1.33;text-align:left;hyphens:auto}
.p-copy p+p{margin-top:3px}
.p-copy b{font-weight:700}
.p-row1{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));column-gap:10px}
.p-lead{grid-column:span 3;padding-right:9px;border-right:1px solid var(--rule)}
.p-lead h2{font-size:22px;font-weight:700;line-height:1.06;letter-spacing:-.01em;margin-bottom:4px}
.p-lead .flow{columns:3;column-gap:10px;column-rule:1px solid var(--rule)}
.p-lead figure{margin:0 0 4px;break-inside:avoid}
.p-lead figure svg{display:block;width:100%;height:auto}
.p-lead .fig2{column-span:all;display:grid;grid-template-columns:2fr 1fr;gap:10px;align-items:end;margin-bottom:4px}
figcaption{font-size:6.8px;color:var(--muted);margin-top:1px}
.p-src{font-size:7px;color:var(--muted);margin-top:2px}
.p-src a{color:var(--accent)!important}
.p-beside h2{font-size:14.5px;font-weight:700;line-height:1.08;margin-bottom:3px}
.p-beside{display:flex;flex-direction:column;gap:5px}
.p-beside .p-copy{text-align:left}
.p-watch,.p-also{border-top:2px solid var(--ink);padding-top:2px}
.p-watch{background:var(--accent-soft);padding:3px 5px 2px;border-top-color:var(--accent)}
.wh{font-size:6.8px;font-weight:800;letter-spacing:.14em;color:#D32F2F;margin-bottom:1px}
.p-watch li{display:flex;justify-content:space-between;font-size:8.4px;padding:2px 0;border-top:1px solid var(--rule)}
.p-watch li:first-child{border-top:0}
.p-watch b{font-weight:800}
.p-more{border-top:2px solid var(--ink);padding-top:3px}
.p-more h3{margin:0 0 2px;font-size:11.6px;font-weight:700;line-height:1.14}
.p-more p{margin:0;font-size:8.8px;line-height:1.3;color:var(--muted)}
.p-also{flex:1;display:flex;flex-direction:column}
.p-also ul{flex:1;display:flex;flex-direction:column;justify-content:space-around}
.p-also li{font-size:9px;font-weight:700;line-height:1.18;padding:2px 0;border-top:1px solid var(--rule)}
.p-also li:first-child{border-top:0}
.p-second{border-top:2px solid var(--ink);padding-top:4px}
.p-second h2{font-size:18px;font-weight:700;line-height:1.08;margin-bottom:4px}
.p-second .flow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));column-gap:10px}
.p-second .txt{grid-column:span 3;columns:3;column-gap:10px;column-rule:1px solid var(--rule)}
.p-second figure{margin:0}
.p-second .side2{display:flex;flex-direction:column;gap:4px}
.p-why{flex:1;display:flex;flex-direction:column;background:var(--accent-soft);border-top:3px solid #D32F2F;padding:3px 6px}
.p-why ul{flex:1;display:flex;flex-direction:column;justify-content:space-around}
.p-why li{font-size:8.6px;font-weight:700;line-height:1.2;padding:2px 0 2px 8px;position:relative;border-top:1px solid var(--rule)}
.p-why li:first-child{border-top:0}
.p-why li::before{content:"";position:absolute;left:0;top:6px;border-left:5px solid #D32F2F;border-top:3px solid transparent;border-bottom:3px solid transparent}
.p-second figure svg{display:block;width:100%;height:auto}
.p-singles{border-top:2px solid var(--ink);padding-top:4px;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));column-gap:0;row-gap:5px}
.p-singles article:nth-child(4n+1){padding-left:0;border-left:0}
.p-singles article:nth-child(4n){padding-right:0}
.p-singles article:nth-child(n+5){border-top:1px solid var(--rule);padding-top:5px}
.p-singles article{padding:0 8px;border-left:1px solid var(--rule)}
.p-singles article:first-child{padding-left:0;border-left:0}
.p-singles article:last-child{padding-right:0}
.p-singles h3{font-size:11.6px;font-weight:700;line-height:1.12;margin-bottom:2px}
.p-singles p{font-size:8.5px;line-height:1.3;color:var(--muted)}
.p-briefs{margin-top:auto;border-top:3px double var(--ink);padding-top:3px}
.p-briefs .bh{background:var(--accent);color:#fff;text-align:center;font-size:8px;font-weight:800;letter-spacing:.2em;padding:2px 0;margin-bottom:3px}
.p-briefs .g{display:grid;align-items:stretch;grid-template-columns:repeat(4,minmax(0,1fr))}
.p-briefs section{display:flex;flex-direction:column;padding:0 7px;border-left:1px solid var(--rule)}
.p-briefs section:first-child{padding-left:0;border-left:0}
.p-briefs section:last-child{padding-right:0}
.p-briefs .sec{font-size:6.8px;font-weight:800;letter-spacing:.12em;color:%(red)s;border-bottom:1.5px solid var(--ink);padding-bottom:1px}
.p-briefs ul{flex:1;display:flex;flex-direction:column;justify-content:space-around}
.p-briefs li{font-size:8.8px;font-weight:700;line-height:1.18;padding:2.4px 0;border-bottom:1px solid var(--rule)}
.p-briefs li:last-child{border-bottom:0}
.p-imprint{border-top:3px double var(--ink);padding-top:3px;display:flex;justify-content:space-between;font-size:8.5px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
.p-imprint span span{color:%(red)s}
.p-imprint .m{font-weight:600;color:var(--muted);font-size:7.8px}

.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.mastimg{background:var(--mast) center/contain no-repeat #fff;aspect-ratio:1600/335;width:100%;max-height:112px;border-radius:6px}
.w .mastimg{max-height:none}
.p-mast{grid-template-columns:100px 1fr 100px!important;gap:12px!important;padding:6px 0!important;border-bottom:3px double var(--ink)!important}
.p-mast .bgfx{width:100px!important;height:100px!important}
.p-mast .ear{font-size:8px!important}
.p-lead h2{font-size:30px!important;font-weight:800!important;line-height:1.02!important;letter-spacing:-.02em!important;margin-bottom:5px!important}
.p-lead .leadgrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);gap:10px;align-items:start}
.p-lead figure{margin:0}.p-lead figure svg{display:block;width:100%;height:auto}
.intro{font-size:10.6px;line-height:1.34;font-weight:600;margin-bottom:4px!important}
.p-row2{border-top:2px solid var(--ink);padding-top:5px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:10px}
.p-sec h2{font-size:16.5px;font-weight:800;line-height:1.08;margin-bottom:4px}
.p-sec figure{margin:0 0 4px}.p-sec figure svg{display:block;width:100%;height:auto;max-height:118px}
.p-sec.b{border-left:1px solid var(--rule);padding-left:10px}
.p-brow{border-top:3px double var(--ink);padding-top:3px}
.p-brow .bh{background:var(--accent);color:#fff;text-align:center;font-size:8px;font-weight:800;letter-spacing:.2em;padding:2px 0;margin-bottom:3px}
.p-brow .g{display:grid;grid-template-columns:repeat(4,minmax(0,1fr))}
.p-brow article{padding:0 7px;border-left:1px solid var(--rule)}
.p-brow article:first-child{padding-left:0;border-left:0}.p-brow article:last-child{padding-right:0}
.p-brow h4{margin:0;font-size:10px;font-weight:800;line-height:1.15}
.p-brow p{font-size:8.4px;line-height:1.28;color:var(--muted)}
.figcol{display:flex;flex-direction:column;gap:5px;align-self:stretch}
.glance{flex:1;display:flex;flex-direction:column;background:var(--accent-soft);border-top:3px solid #D32F2F;padding:3px 6px}
.glance ul{flex:1;display:flex;flex-direction:column;justify-content:space-around}
.glance li{font-size:9px;font-weight:700;line-height:1.2;padding:2px 0 2px 9px;position:relative;border-top:1px solid var(--rule)}
.glance li:first-child{border-top:0}
.glance li::before{content:"";position:absolute;left:0;top:6px;border-left:5px solid #D32F2F;border-top:3px solid transparent;border-bottom:3px solid transparent}
.p-side .p-list li{font-size:10.7px!important;line-height:1.22!important;padding:3px 0!important}
.p-side .p-k{font-size:7px}
.p-topst h3{font-size:13px!important}
.p-topst p{font-size:9.4px!important}
.p-bot h3{font-size:12.4px!important}
.p-bot p{font-size:9.2px!important}
.p-cat{font-size:9px!important;padding:2px 0!important;margin-top:5px!important}
img.photo{display:block;width:100%;height:auto;border-radius:4px}
.p-lead{display:flex;flex-direction:column}
.p-lead .lbody{display:flex;flex-direction:column;gap:5px;flex:1}
.leadfig{margin:0}
.leadtxt{columns:2;column-gap:12px;column-rule:1px solid var(--rule);flex:1;column-fill:balance}
.leadtxt .intro{margin-top:0}
.p-sec figure img.photo{max-height:none}
.p-light{flex:1 0 auto;align-content:stretch;border-top:2px solid var(--ink);padding-top:5px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,3fr);gap:10px;align-items:center;background:linear-gradient(var(--warm-soft),var(--warm-soft)) 0 5px/100% calc(100% - 5px) no-repeat;padding-bottom:4px}
.p-light figure{margin:0}.p-light figure svg{display:block;width:100%;height:auto}
.p-light h2{font-size:19px;font-weight:800;line-height:1.1;margin-bottom:4px;padding-right:8px}
.p-light{grid-template-columns:minmax(0,1fr) minmax(0,1.25fr)!important;padding:5px 0 0!important}
.p-light figure{align-self:stretch;position:relative;min-height:150px}.p-light figure img.photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 40%;border-radius:0}
.p-light .lt{padding:4px 8px 6px 0}
.p-light .intro{font-size:11.6px}
.p-light .p-copy{font-size:10.6px;line-height:1.38}
.p-light .cols{columns:2;column-gap:10px;padding-right:6px}
.p-light .p-kick{color:var(--warm-ink)}
""".replace("%(red)s", RED)


def k(x):
    return f'<span class="p-k">{html.escape(x)}</span>'


def side(col, cls):
    d = []
    t = col["top"]
    d.append(f'<div class="p-cat first">{t["cat"]}</div>')
    d.append(f'<div class="p-topst">{k(t["k"])}<h3>{a(t["url"], t["h"])}</h3><p>{t["intro"]}{arrow(t["url"])}</p></div>')
    for i, s in enumerate(col["sections"]):
        if i > 0 or s["name"] != t["cat"]:
            d.append(f'<div class="p-cat{" alt" if i % 2 else ""}">{s["name"]}</div>')
        d.append('<ul class="p-list">' + "".join(
            f'<li>{k(it["k"])}{a(it["url"], it["h"])}{arrow(it["url"])}</li>' for it in s["items"]) + '</ul>')
    b = col["bottom"]
    d.append(f'<div class="p-bot">{k(b["cat"])}{art(b["art"])}<h3>{a(b["url"], b["h"])}</h3><p>{b["intro"]}{arrow(b["url"])}</p></div>')
    return f'<aside class="p-side {cls}">' + "".join(d) + '</aside>'


def beside_extra(bz):
    o = ""
    if bz.get("watch"):
        w = bz["watch"]
        o += f'<div class="p-watch"><div class="wh">{w["title"]}</div><ul>' + "".join(
            f'<li><span>{a(r[2], r[0])}</span><b>{r[1]}</b></li>' for r in w["rows"]) + '</ul></div>'
    for m in bz.get("more", []):
        o += f'<div class="p-more">{k(m["k"])}<h3>{a(m["url"], m["h"])}</h3><p>{m["intro"]}{arrow(m["url"])}</p></div>'
    if bz.get("also"):
        al = bz["also"]
        o += f'<div class="p-also"><div class="wh">{al["title"]}</div><ul>' + "".join(
            f'<li>{a(i["url"], i["h"])}{arrow(i["url"])}</li>' for i in al["items"]) + '</ul></div>'
    return o


def mast():
    return '<div class="mastimg" role="img" aria-label="Pringital News: Credible like Print, Fast like Digital"></div>'


def paper(E):
    L, S, R2, bz, LT = E["lead"], E["second"], E["row2b"], E["beside"], E["lighter"]
    singles = "".join(
        f'<article>{k(s["k"])}<h3>{a(s["url"], s["h"])}</h3><p>{s["intro"]}{arrow(s["url"])}</p></article>' for s in E["singles"])
    brow = "".join(
        f'<article>{k(b["k"])}<h4>{a(b["url"], b["h"])}</h4><p>{b["intro"]}{arrow(b["url"])}</p></article>' for b in E["briefrow"])
    def two(x, cls):
        return (f'<article class="{cls}"><span class="p-kick">{x["k"]}</span><h2>{a(x["url"], x["h"])}</h2>'
                f'<figure>{art(x["art"])}</figure><p class="intro">{x["intro"]}</p><div class="p-copy"><p>{x["para"]}{arrow(x["url"])}</p></div></article>')
    return f'''<div id="fit"><div id="page">
<div class="p-top"><span>{E["dateline"]}</span><span class="live">● Latest Edition</span><span>{E["edition"]} · <a href="/archive/" style="text-decoration:underline">Archive</a></span></div>
<header class="p-mast"><a class="bgl" href="/bulletin/" aria-label="Listen to the 4-minute Pringital News bulletin">{bulletin_graphic()}</a>
<h1 class="vh">Pringital News</h1>{mast()}<div class="ear"><strong>PRINT + DIGITAL</strong>Tap <b style="color:#D32F2F">↗</b> or any headline for the detailed news</div></header>
<main class="p-main">
{side(E["left"], "l")}
<section class="p-center">
<div class="p-row1">
<article class="p-lead"><span class="p-kick">{L["k"]}</span><h2>{a(L["url"], L["h"])}</h2>
<div class="lbody"><figure class="leadfig">{art(L["art"])}<figcaption>Graphic: Pringital News</figcaption></figure>
<div class="leadtxt"><p class="intro">{L["intro"]}</p><div class="p-copy"><p>{L["para"]}{arrow(L["url"])}</p><div class="p-src">Sources: {a(L["url"], L["src"])} · {a(L["url2"], L["src2"])}</div></div></div></div></article>
<article class="p-beside"><span class="p-kick">{bz["k"]}</span><h2>{a(bz["url"], bz["h"])}</h2><div class="p-copy"><p>{bz["intro"]}{arrow(bz["url"])}</p></div>{beside_extra(bz)}</article>
</div>
<div class="p-row2">{two(S, "p-sec")}{two(R2, "p-sec b")}</div>
<div class="p-singles">{singles}</div>
<article class="p-light"><figure>{art(LT["art"])}</figure><div class="lt"><span class="p-kick">{LT["k"]}</span><h2>{a(LT["url"], LT["h"])}</h2><p class="intro">{LT["intro"]}</p><div class="p-copy"><p>{LT["para"]}{arrow(LT["url"])}</p></div></div></article>
</section>
{side(E["right"], "r")}
</main>
<footer class="p-imprint"><span>A journalism initiative by <span>Sudhanshu Srivastava</span></span><span class="m">Pringital News · Page 1 · pringital.com</span></footer>
</div></div>'''


# ---------------------------------------------------------------- web

WEB_CSS = """
html[data-mode="web"] body{font-size:15px;line-height:1.6}
.w{max-width:1200px;margin:0 auto;padding:0 max(20px,env(safe-area-inset-right,0px)) 40px max(20px,env(safe-area-inset-left,0px));color:var(--ink)}
.w a{color:inherit;text-decoration:none}.w a:hover{color:var(--accent)}
.w h1,.w h2,.w h3,.w p,.w ul{margin:0}.w ul{list-style:none;padding:0}
.w .arr{color:#D32F2F!important;font-weight:800;margin-left:5px;font-size:.95em;text-decoration:none}
.w .arr:hover{color:#1F3F7A!important}
.w-mast{text-align:center;padding:clamp(24px,5vw,48px) 0 20px}
.w-mast h1{font-weight:300;font-size:clamp(34px,7vw,72px);letter-spacing:.08em;line-height:1.05}
.w-mast h1 span{font-weight:500;color:var(--accent)}
.w-slogan{margin-top:10px;font-size:clamp(15px,2.2vw,19px);font-weight:700;font-style:italic;color:%(red)s}
.w-meta{margin-top:12px;display:flex;justify-content:center;flex-wrap:wrap;gap:6px 18px;font-size:12.5px;color:var(--muted)}
.w-bul{display:inline-block;margin-top:16px;line-height:0}.w-bul svg{width:220px;height:auto}
.w-kick{display:block;font-size:11px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--warm-ink);margin-bottom:8px}
.w-card{background:var(--card);border:1px solid var(--rule);border-radius:16px;padding:22px}
.w-lead{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:28px;align-items:start;margin-top:8px}
.w-lead h2{font-size:clamp(24px,3vw,36px);font-weight:600;line-height:1.2;margin-bottom:12px}
.w-card p{margin:0 0 12px;font-size:15px;line-height:1.7}
.w-card figure{margin:0}.w-card figure svg{display:block;width:100%;height:auto;border-radius:10px}
.w-src{font-size:12px;color:var(--muted)}.w-src a{color:var(--accent)}
.w-pair{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:24px;margin-top:24px}
.w-pair h2{font-size:clamp(20px,2.4vw,26px);font-weight:600;line-height:1.25;margin-bottom:10px}
.w-four{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;margin-top:24px}
.w-four h3{font-size:17px;font-weight:600;line-height:1.3;margin-bottom:6px}
.w-four p{font-size:13.5px;color:var(--muted);line-height:1.6;margin:0}
.w-zone{margin:36px 0 16px;border-top:2px solid var(--warm);padding-top:20px;font-size:12px;font-weight:600;letter-spacing:.24em;text-transform:uppercase;color:var(--warm-ink);text-align:center}
.w-cols{columns:3 300px;column-gap:24px}
.w-sec{background:var(--card);border:1px solid var(--rule);border-radius:14px;overflow:hidden;break-inside:avoid;margin:0 0 24px}
.w-sh{padding:11px 16px;background:var(--warm-soft);border-bottom:2px solid var(--warm);font-size:12px;font-weight:600;letter-spacing:.18em;color:var(--warm-ink)}
.w-sec ul{padding:4px 16px 8px}
.w-sec li{padding:10px 0;border-bottom:1px solid var(--warm-line);font-size:14px;font-weight:500;line-height:1.45}
.w-sec li:last-child{border-bottom:0}
.w-sec .wk{display:block;font-size:10px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.w-sec .intro{padding:14px 16px 4px}.w-sec .intro h3{font-size:17px;font-weight:600;line-height:1.35;margin-bottom:6px}.w-sec .intro p{font-size:13.5px;color:var(--muted);line-height:1.6}
.w-sec .intro svg{display:block;width:100%;max-width:320px;height:auto;border-radius:8px;margin:6px 0}
.w-watch{margin-top:18px}.w-watch li{display:flex;justify-content:space-between;gap:10px;padding:8px 0;border-top:1px solid var(--rule);font-size:14px}.w-watch li:first-child{border-top:0}.w-watch b{font-weight:600}
.w-glance{margin-top:16px;padding:14px 18px;background:var(--accent-soft);border-radius:10px;font-size:14px;font-weight:500}.w-glance li{padding:4px 0}.w-glance li::before{content:"▸  ";color:%(red)s}
.w-logo{max-width:960px;margin:0 auto}
.w-bul svg{width:120px!important;height:120px}
.w-intro{font-weight:600}
.w-two{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;margin-top:24px}
.w-two h2{font-size:clamp(20px,2.2vw,24px);font-weight:700;line-height:1.25;margin-bottom:10px}
.w-fig{margin:0 0 12px!important}
.w-lead h2{font-weight:800!important}
.w-brow p{margin:0}
.w-light{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:24px;margin-top:24px;background:var(--warm-soft)}
.w-light h2{font-size:clamp(20px,2.4vw,26px);font-weight:700;line-height:1.25;margin-bottom:10px}
@media (max-width:900px){.w-two{grid-template-columns:1fr}.w-light{grid-template-columns:1fr}}
.w-imprint{margin-top:20px;border-top:2px solid var(--warm);padding-top:16px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px 20px;font-size:12.5px;color:var(--muted)}
.w-imprint b{color:var(--ink)}.w-imprint b span{color:var(--accent)}
@media (max-width:900px){.w-four{grid-template-columns:repeat(2,minmax(0,1fr))}.w-pair{grid-template-columns:1fr}}
@media (max-width:700px){.w-lead{grid-template-columns:1fr}.w-four{grid-template-columns:1fr}.w-card{padding:16px}}
""".replace("%(red)s", RED)


def wa(url, text):
    return a(url, text) + f'<a class="arr" href="{html.escape(url)}" target="_blank" rel="noopener" aria-label="Detailed news">↗</a>'


def web_section(name, items, intro=None):
    s = f'<section class="w-sec"><div class="w-sh">{name}</div>'
    if intro:
        s += f'<div class="intro"><span class="wk" style="font-size:10px;letter-spacing:.14em;color:var(--muted);font-weight:600">{intro["k"]}</span>'
        if intro.get("art"):
            s += art(intro["art"])
        s += f'<h3>{wa(intro["url"], intro["h"])}</h3><p>{intro["intro"]}</p></div>'
    if items:
        s += '<ul>' + "".join(f'<li><span class="wk">{html.escape(i["k"])}</span>{wa(i["url"], i["h"])}</li>' for i in items) + '</ul>'
    return s + '</section>'


def web_extra(bz):
    o = ""
    if bz.get("watch"):
        w = bz["watch"]
        o += f'<div class="w-watch"><div class="w-kick">{w["title"].title()}</div><ul>' + "".join(f'<li><span>{a(r[2], r[0])}</span><b>{r[1]}</b></li>' for r in w["rows"]) + '</ul></div>'
    if bz.get("also"):
        o += '<div class="w-watch"><div class="w-kick">Also today</div><ul>' + "".join(f'<li>{wa(i["url"], i["h"])}</li>' for i in bz["also"]["items"]) + '</ul></div>'
    return o


def web(E):
    L, S, R2, bz, LT = E["lead"], E["second"], E["row2b"], E["beside"], E["lighter"]
    secs = []
    for col in (E["left"], E["right"]):
        first = True
        for s in col["sections"]:
            secs.append(web_section(s["name"], s["items"], col["top"] if first and s["name"] == col["top"]["cat"] else None))
            first = False
        secs.append(web_section(col["bottom"]["cat"], [], col["bottom"]))
    def card(x):
        return (f'<article class="w-card"><span class="w-kick">{x["k"]}</span><h2>{wa(x["url"], x["h"])}</h2>'
                f'<figure class="w-fig">{art(x["art"])}</figure><p class="w-intro">{x["intro"]}</p><p>{x["para"]}</p></article>')
    brow = "".join(f'<article class="w-card"><span class="w-kick">{b["k"]}</span><h3>{wa(b["url"], b["h"])}</h3><p>{b["intro"]}</p></article>' for b in E["briefrow"])
    return f'''<div class="w">
<div class="w-mast"><h1 class="vh">Pringital News</h1><div class="mastimg w-logo" role="img" aria-label="Pringital News: Credible like Print, Fast like Digital"></div>
<div class="w-meta"><span>{E["dateline"]}</span><span>{E["edition"]}</span><span>Tap <b style="color:#D32F2F">↗</b> for the detailed news</span></div>
<a class="w-bul" href="/bulletin/" aria-label="Listen to the bulletin">{bulletin_graphic("w")}</a></div>
<article class="w-card w-lead"><div><figure>{art(L["art"])}</figure></div><div><span class="w-kick">{L["k"]}</span><h2>{wa(L["url"], L["h"])}</h2><p class="w-intro">{L["intro"]}</p><p>{L["para"]}</p><p class="w-src">Sources: {a(L["url"], L["src"])} · {a(L["url2"], L["src2"])}</p></div></article>
<div class="w-two">{card(S)}{card(R2)}<article class="w-card"><span class="w-kick">{bz["k"]}</span><h2>{wa(bz["url"], bz["h"])}</h2><p>{bz["intro"]}</p>{web_extra(bz)}</article></div>
<div class="w-four">{"".join(f'<article class="w-card"><span class="w-kick">{s["k"]}</span><h3>{wa(s["url"], s["h"])}</h3><p>{s["intro"]}</p></article>' for s in E["singles"])}</div>
<article class="w-card w-light"><figure>{art(LT["art"])}</figure><div><span class="w-kick">{LT["k"]}</span><h2>{wa(LT["url"], LT["h"])}</h2><p class="w-intro">{LT["intro"]}</p><p>{LT["para"]}</p></div></article>
<h2 class="w-zone">The day in brief</h2>
<div class="w-cols">{"".join(secs)}</div>
<footer class="w-imprint"><b>A journalism initiative by <span>Sudhanshu Srivastava</span></b><span>Pringital News · pringital.com</span></footer>
</div>'''


# ---------------------------------------------------------------- page

def mast_b64():
    import base64
    return base64.b64encode(open(os.path.join(ROOT, "assets", "masthead.jpg"), "rb").read()).decode()


def build(E):
    base = rd("_base.css")
    sbar = rd("_sbar.html")
    script = rd("_script.html")
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Pringital News · {E["dateline"]}</title>
<meta name="description" content="Pringital News, {E["edition"]}, {E["dateline"]}. Credible like print, fast like digital.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600;1,700&display=swap">
<style>
:root{{--mast:url(data:image/jpeg;base64,{mast_b64()})}}
{base}
{PAPER_CSS}
{WEB_CSS}
</style>
</head>
<body>
{sbar}
{paper(E)}
{web(E)}
{script}
</body>
</html>
'''


def count(E):
    n = 0
    for c in (E["left"], E["right"]):
        n += 2 + sum(len(s["items"]) for s in c["sections"])
    return n


def setup_images(E, outdir=None, embed=False):
    import base64, shutil
    from PIL import Image
    IMG.clear()
    for n, alt in E.get("images", {}).items():
        f = os.path.join(ROOT, "assets", E["date"], n + ".jpg")
        w, h = Image.open(f).size
        if embed:
            url = "data:image/jpeg;base64," + base64.b64encode(open(f, "rb").read()).decode()
        else:
            os.makedirs(os.path.join(outdir, "img"), exist_ok=True)
            shutil.copy(f, os.path.join(outdir, "img", n + ".jpg"))
            url = "img/" + n + ".jpg"
        IMG[n] = (url, w, h, alt)


if __name__ == "__main__":
    src = sys.argv[1]
    E = json.load(open(src, encoding="utf-8"))
    for d in ("today", f"archive/{E['date']}"):
        p = os.path.join(ROOT, d)
        os.makedirs(p, exist_ok=True)
        setup_images(E, p)
        open(os.path.join(p, "index.html"), "w", encoding="utf-8").write(build(E))
    if len(sys.argv) > 2:  # self-contained preview copy
        setup_images(E, embed=True)
        open(sys.argv[2], "w", encoding="utf-8").write(build(E))
    print("side stories:", count(E))
