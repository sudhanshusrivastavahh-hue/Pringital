#!/usr/bin/env python3
"""Build the Pringital News audio bulletin page.

Usage: python3 scripts/build_bulletin.py editions/YYYY-MM-DD-bulletin.json [preview.html]
Writes bulletin/index.html and archive/YYYY-MM-DD/bulletin/index.html, each with its own
img/ and sounds/ folders. The voice is the reader's own device voice; "Microsoft Ravi"
(English, India) is chosen first when the device has it.
"""
import json, os, sys, html, shutil, base64

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS = ["signature_intro.mp3"]

CSS = """
:root{--paper:#fff;--ink:#16202c;--muted:#55606e;--red:#D32F2F;--blue:#1F3F7A;--tint:#F3F6FB;--rule:#dde3ea;--hl:#FFF4C2;
--font:Montserrat,"Segoe UI",Helvetica,Arial,sans-serif;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:#EEF2F7;color:var(--ink);font-family:var(--font);padding:24px max(16px,env(safe-area-inset-right,0px)) 48px max(16px,env(safe-area-inset-left,0px))}
.wrap{max-width:720px;margin:0 auto;background:var(--paper);border-radius:16px;box-shadow:0 18px 50px -30px rgba(20,30,50,.5);padding:22px clamp(16px,4vw,32px) 28px;display:flex;flex-direction:column;gap:18px}
.top{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);border-bottom:3px solid var(--ink);padding-bottom:8px}
.top .live{color:var(--red)}
.mast{display:block;width:100%;height:auto}
.title{display:flex;align-items:center;justify-content:center;gap:14px;border-top:1px solid var(--ink);border-bottom:3px double var(--ink);padding:8px 0}
.title svg{width:64px;height:64px;flex:none}
.title h1{margin:0;font-size:clamp(24px,5vw,34px);font-weight:800;letter-spacing:.02em;color:var(--blue)}
.title h1 span{color:var(--red)}
.player{background:linear-gradient(135deg,#FFF1EE,#FFF8E6 40%,#E9F6F4 75%,#E8EEF8);border:1.5px solid var(--red);border-radius:16px;padding:16px 18px;display:flex;flex-direction:column;gap:12px}
.prow{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.play{width:62px;height:62px;border-radius:50%;border:0;background:var(--red);color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;flex:none;box-shadow:0 6px 16px -6px rgba(211,47,47,.7)}
.play:hover{background:var(--blue)}
.play svg{width:26px;height:26px}
.pmeta{flex:1;min-width:190px}
.pmeta strong{display:block;font-size:15px;font-weight:800}
.pmeta span{font-size:12.5px;font-weight:600;color:var(--muted)}
.ctls{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.ctl{font:800 11.5px/1 var(--font);letter-spacing:.06em;text-transform:uppercase;border:1.5px solid var(--ink);background:#fff;color:var(--ink);border-radius:20px;padding:8px 12px;cursor:pointer}
.ctl:hover{background:var(--ink);color:#fff}
.ctl[aria-pressed="true"]{background:var(--blue);border-color:var(--blue);color:#fff}
label{font-size:12px;font-weight:600;color:var(--muted);display:flex;align-items:center;gap:6px}
select{font:600 12px var(--font);padding:5px 6px;border:1px solid var(--rule);border-radius:6px;background:#fff;color:var(--ink);max-width:230px}
.bar{height:6px;background:#F4C7C7;border-radius:3px;overflow:hidden}
.bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#FF6F61,#FFB300,#26A69A,#1F3F7A);transition:width .3s}
.voice{font-size:12px;font-weight:700;color:var(--blue)}
.note{margin:0;font-size:11.5px;font-weight:600;line-height:1.5;color:var(--muted)}
button:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid var(--blue);outline-offset:2px}
h2{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin:0 0 6px;color:var(--red);border-bottom:1px solid var(--rule);padding-bottom:8px}
.heads{border:2px solid var(--ink);border-radius:10px;padding:12px 16px}
.heads ol{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:5px}
.heads li{font-size:15px;font-weight:700;line-height:1.35}
.t p{margin:0;padding:9px 12px;font-size:15.5px;line-height:1.65;border-left:3px solid transparent;border-radius:3px;transition:background .3s}
.t p.on{background:var(--hl);border-left-color:var(--red)}
.t .sec{display:block;font-size:10.5px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--red);margin-bottom:3px}
.t a.dn{color:var(--blue);font-weight:800;text-decoration:none;margin-left:4px}
.foot{font-size:12px;font-weight:600;line-height:1.5;color:var(--muted);border-top:3px double var(--ink);padding-top:10px;display:flex;flex-direction:column;gap:4px}
.foot strong{color:var(--ink);letter-spacing:.06em;text-transform:uppercase}.foot strong span{color:var(--red)}
.foot a{color:inherit}
@media (prefers-reduced-motion:reduce){.t p,.bar i{transition:none}}
"""

ICON = """<svg viewBox="0 0 120 120" aria-hidden="true"><defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF6F61"/><stop offset=".35" stop-color="#FFB300"/><stop offset=".7" stop-color="#26A69A"/><stop offset="1" stop-color="#1F3F7A"/></linearGradient><linearGradient id="g2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E53935"/><stop offset="1" stop-color="#1F3F7A"/></linearGradient></defs>
<rect x="1" y="1" width="118" height="118" rx="16" fill="url(#g1)"/><rect x="7" y="7" width="106" height="106" rx="11" fill="#fff"/>
<g transform="translate(46 26)"><rect x="6" y="0" width="16" height="30" rx="8" fill="url(#g2)"/><path d="M0 20q0 15 14 15t14-15" fill="none" stroke="#1F3F7A" stroke-width="3.4" stroke-linecap="round"/><rect x="12" y="35" width="4" height="9" fill="#1F3F7A"/><rect x="4" y="44" width="20" height="4" rx="2" fill="#1F3F7A"/></g>
<g stroke-width="3.4" stroke-linecap="round" fill="none"><path d="M82 34q6 8 0 16" stroke="#FFB300"/><path d="M89 28q11 14 0 28" stroke="#26A69A"/><path d="M38 34q-6 8 0 16" stroke="#FFB300"/><path d="M31 28q-11 14 0 28" stroke="#26A69A"/></g>
<rect x="28" y="86" width="64" height="18" rx="9" fill="#D32F2F"/><text x="60" y="99" font-family="Montserrat,Arial" font-size="10" font-weight="800" fill="#fff" text-anchor="middle">▶ 4 MIN</text></svg>"""

JS = r"""
(function(){
  var synth=window.speechSynthesis, paras=[].slice.call(document.querySelectorAll('#script p')), idx=0, state='idle', voices=[], chosen=null, timer=null;
  var $=function(i){return document.getElementById(i)};
  var btn=$('play'), ico=$('ico'), st=$('status'), prog=$('prog'), sel=$('voice'), vlab=$('vname'), sndBtn=$('snd');
  var intro=$('s-intro'), soundOn=true;
  var PLAY='M7 4l13 8-13 8z', PAUSE='M6 4h4v16H6zM14 4h4v16h-4z';
  // Preference order: Microsoft Ravi first, then other Indian English male voices, then any Indian English voice, then English.
  function score(v){var n=v.name||'',l=(v.lang||'').toLowerCase();
    if(/ravi/i.test(n)) return 100;
    if(/en[-_]in/.test(l)&&/(prabhat|kunal|aarav|hemant|rishi|male)/i.test(n)) return 80;
    if(/en[-_]in/.test(l)) return 60;
    if(/^en/.test(l)) return 20; return 0}
  function loadVoices(){
    if(!synth) return;
    voices=synth.getVoices().filter(function(v){return score(v)>0}).sort(function(a,b){return score(b)-score(a)});
    sel.innerHTML='';
    voices.forEach(function(v,i){var o=document.createElement('option');o.value=i;o.textContent=v.name+' ('+v.lang+')';sel.appendChild(o)});
    if(!voices.length){var o=document.createElement('option');o.value='';o.textContent='Device default';sel.appendChild(o)}
    pick();
  }
  function pick(){chosen=voices[+sel.value]||voices[0]||null;
    vlab.textContent=chosen?(/ravi/i.test(chosen.name)?'Voice: Ravi (English, India)':'Voice: '+chosen.name+' — Ravi not found on this device'):'Voice: device default';}
  if(synth){loadVoices(); if(synth.onvoiceschanged!==undefined) synth.onvoiceschanged=loadVoices;}
  sel.onchange=pick;
  function mark(){paras.forEach(function(p,i){p.classList.toggle('on',i===idx)}); prog.style.width=Math.round(idx/paras.length*100)+'%';}
  function txt(p){var c=p.cloneNode(true);[].forEach.call(c.querySelectorAll('a.dn'),function(a){a.remove()});var s=c.querySelector('.sec');var head=s?s.textContent+'. ':'';if(s)s.remove();return head+c.textContent.trim()}
  function setIcon(play){ico.querySelector('path').setAttribute('d',play?PLAY:PAUSE);btn.setAttribute('aria-label',play?'Play the bulletin':'Pause the bulletin')}
  function playSound(a,cb){if(!soundOn||!a){cb();return} a.currentTime=0; a.onended=function(){a.onended=null;cb()}; var p=a.play(); if(p&&p.catch)p.catch(function(){a.onended=null;st.textContent='Sound was blocked by the browser — tap play again';cb()});}
  function speak(){
    if(state!=='playing') return;
    if(idx>=paras.length){finish();return}
    mark(); paras[idx].scrollIntoView({block:'nearest',behavior:'smooth'});
    if(!synth){st.textContent='Read-aloud is not supported in this browser';return}
    var u=new SpeechSynthesisUtterance(txt(paras[idx]));
    if(chosen){u.voice=chosen;u.lang=chosen.lang}else{u.lang='en-IN'}
    u.rate=0.98; u.pitch=1;
    u.onend=function(){ if(state!=='playing') return; var wasSection=!!paras[idx].querySelector('.sec'); idx++;
      speak(); };
    st.textContent='Reading '+(idx+1)+' of '+paras.length;
    synth.speak(u);
    clearInterval(timer); timer=setInterval(function(){ if(synth.speaking&&!synth.paused){synth.pause();synth.resume();} },10000); // Chrome long-utterance guard
  }
  function start(){state='playing';setIcon(false);
    if(idx===0){st.textContent='♪ Pringital signature tune…'; playSound(intro,function(){setTimeout(speak,500)})} else speak();}
  function finish(){clearInterval(timer);prog.style.width='100%';paras.forEach(function(p){p.classList.remove('on')});
    st.textContent='♪ Pringital signature tune…';
    setTimeout(function(){playSound(intro,function(){state='idle';idx=0;setIcon(true);st.textContent='Finished · tap play to hear it again'})},500);}
  btn.onclick=function(){
    if(state==='playing'){state='paused'; if(synth) synth.pause(); intro.pause(); setIcon(true); st.textContent='Paused'; return}
    if(state==='paused'){state='playing'; setIcon(false); if(synth&&synth.paused){synth.resume();st.textContent='Reading '+(idx+1)+' of '+paras.length} else speak(); return}
    start();
  };
  $('stop').onclick=function(){state='idle'; if(synth) synth.cancel(); intro.pause();intro.currentTime=0; clearInterval(timer); idx=0; mark(); paras[0].classList.remove('on'); prog.style.width='0'; setIcon(true); st.textContent='Stopped · tap play to begin'};
  function jump(d){idx=Math.max(0,Math.min(paras.length-1,idx+d)); if(synth) synth.cancel(); if(state==='playing'){setTimeout(speak,60)} else mark()}
  $('back').onclick=function(){jump(-1)}; $('next').onclick=function(){jump(1)};
  sndBtn.onclick=function(){soundOn=!soundOn; sndBtn.setAttribute('aria-pressed',soundOn); sndBtn.textContent=soundOn?'♪ Signature on':'♪ Signature off'};
  $('preview').onclick=function(){intro.currentTime=0;intro.play()};
})();
"""


def page(B, mast_src, snd):
    heads = "".join(f"<li>{html.escape(h)}</li>" for h in B["heads"])
    ps = []
    for p in B["paras"]:
        sec = f'<span class="sec">{html.escape(p["s"])}</span>' if p.get("s") else ""
        dn = f'<a class="dn" href="{html.escape(p["url"])}" target="_blank" rel="noopener" aria-label="Full story">↗</a>' if p.get("url") else ""
        ps.append(f"<p>{sec}{html.escape(p['t'])}{dn}</p>")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Pringital News Bulletin · {B["dateline"]}</title>
<meta name="description" content="Pringital News four-minute bulletin, {B["dateline"]}.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="top"><span>{B["dateline"]}</span><span class="live">● New Delhi Edition</span></div>
  <img class="mast" src="{mast_src}" alt="Pringital News: Credible like Print, Fast like Digital">
  <div class="title">{ICON}<h1>NEWS <span>BULLETIN</span></h1></div>

  <section class="player" aria-label="Audio bulletin">
    <div class="prow">
      <button class="play" id="play" type="button" aria-label="Play the bulletin"><svg id="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4l13 8-13 8z" fill="#fff"/></svg></button>
      <div class="pmeta"><strong>Listen to today’s bulletin</strong><span id="status">About 4 minutes · tap play to begin</span></div>
    </div>
    <div class="bar" aria-hidden="true"><i id="prog"></i></div>
    <div class="ctls">
      <button class="ctl" id="stop" type="button">Stop</button>
      <button class="ctl" id="back" type="button">◂ Back</button>
      <button class="ctl" id="next" type="button">Next ▸</button>
      <button class="ctl" id="snd" type="button" aria-pressed="true">♪ Signature on</button>
      <button class="ctl" id="preview" type="button">Hear the signature tune</button>
    </div>
    <div class="ctls"><label for="voice">Voice <select id="voice"></select></label><span class="voice" id="vname"></span></div>
    <p class="note">Read in the Ravi voice (Microsoft Ravi, English – India), which is built into Windows. On devices without it, the closest Indian English voice is used. Opens and closes with the Pringital signature tune, an original composition.</p>
    <audio id="s-intro" preload="auto" src="{snd[0]}"></audio>
  </section>

  <section class="heads"><h2>The headlines</h2><ol>{heads}</ol></section>

  <section class="t" id="script" aria-label="Transcript"><h2>Transcript</h2>
{chr(10).join(ps)}
  </section>

  <div class="foot">
    <strong>A Journalism Initiative by <span>Sudhanshu Srivastava</span></strong>
    <span><a href="/today/">Today’s edition</a> · <a href="/archive/">Archive</a> · <a href="/">pringital.com</a></span>
  </div>
</div>
<script>{JS}</script>
</body>
</html>
"""


def write(B, outdir):
    os.makedirs(os.path.join(outdir, "img"), exist_ok=True)
    os.makedirs(os.path.join(outdir, "sounds"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "assets", "masthead.jpg"), os.path.join(outdir, "img", "masthead.jpg"))
    for s in SOUNDS:
        shutil.copy(os.path.join(ROOT, "assets", "sounds", s), os.path.join(outdir, "sounds", s))
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(
        page(B, "img/masthead.jpg", ["sounds/" + s for s in SOUNDS]))


def uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


if __name__ == "__main__":
    B = json.load(open(sys.argv[1], encoding="utf-8"))
    for d in ("bulletin", f"archive/{B['date']}/bulletin"):
        write(B, os.path.join(ROOT, d))
    if len(sys.argv) > 2:
        open(sys.argv[2], "w", encoding="utf-8").write(page(
            B, uri(os.path.join(ROOT, "assets", "masthead.jpg"), "image/jpeg"),
            [uri(os.path.join(ROOT, "assets", "sounds", s), "audio/mpeg") for s in SOUNDS]))
    print("paragraphs:", len(B["paras"]))
