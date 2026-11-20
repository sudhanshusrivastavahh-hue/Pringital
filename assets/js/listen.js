/* Pringital: play the 4-minute bulletin on the front page itself, no page change. */
(function () {
  var links = [].slice.call(document.querySelectorAll('a[href$="/bulletin/"]'));
  if (!links.length) return;
  var href = links[0].getAttribute('href');
  var synth = window.speechSynthesis;
  var inIntro = false, paras = null, idx = 0, state = 'idle', voice = null, guard = null, loading = null;
  var intro = new Audio(href + 'sounds/signature_intro.mp3'); intro.preload = 'auto';

  function load() {
    if (loading) return loading;
    loading = fetch(href).then(function (r) { return r.text(); }).then(function (h) {
      var d = new DOMParser().parseFromString(h, 'text/html');
      paras = [].slice.call(d.querySelectorAll('#script p')).map(function (p) {
        [].forEach.call(p.querySelectorAll('a'), function (a) { a.remove(); });
        var s = p.querySelector('.sec'), head = s ? s.textContent + '. ' : '';
        if (s) s.remove();
        return head + p.textContent.trim();
      }).filter(Boolean);
    }).catch(function () { paras = null; loading = null; });
    return loading;
  }
  function score(v) { var n = v.name || '', l = (v.lang || '').toLowerCase();
    if (/ravi/i.test(n)) return 100; if (/en[-_]in/.test(l) && /(prabhat|kunal|aarav|hemant|rishi|male)/i.test(n)) return 80;
    if (/en[-_]in/.test(l)) return 60; if (/^en/.test(l)) return 20; return 0; }
  function pickVoice() { if (!synth) return; var v = synth.getVoices().filter(function (x) { return score(x) > 0; })
    .sort(function (a, b) { return score(b) - score(a); }); voice = v[0] || null; }
  if (synth) { pickVoice(); if ('onvoiceschanged' in synth) synth.addEventListener('voiceschanged', pickVoice); }
  // Fetch the transcript early so a tap starts straight away.
  (window.requestIdleCallback || function (f) { setTimeout(f, 1200); })(load);

  // Player bar
  var css = document.createElement('style');
  css.textContent = '.pn-player{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(14px + env(safe-area-inset-bottom,0px));z-index:50;display:flex;align-items:center;gap:10px;width:min(560px,calc(100% - 24px));padding:10px 12px;border-radius:14px;background:#0E2350;color:#fff;box-shadow:0 10px 30px rgba(0,0,0,.35);font:500 13px/1.3 Inter,system-ui,sans-serif}' +
    '.pn-player[hidden]{display:none!important}.pn-player button{flex:none;width:38px;height:38px;border-radius:50%;border:0;display:grid;place-items:center;cursor:pointer;background:#D2232A;color:#fff}' +
    '.pn-player button.pn-x{background:transparent;border:1px solid rgba(255,255,255,.35);width:32px;height:32px}.pn-player svg{width:16px;height:16px;fill:currentColor}' +
    '.pn-mid{flex:1;min-width:0;display:flex;flex-direction:column;gap:6px}.pn-top{display:flex;justify-content:space-between;gap:8px;white-space:nowrap}.pn-top b{font-weight:800;letter-spacing:.06em;font-size:11px;text-transform:uppercase}' +
    '.pn-top a{color:#BFD2F0;text-decoration:underline;font-size:12px}.pn-st{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;opacity:.85;font-size:12px}' +
    '.pn-bar{height:4px;border-radius:4px;background:rgba(255,255,255,.2);overflow:hidden}.pn-bar i{display:block;height:100%;width:0;background:#D2232A;transition:width .4s}' +
    '.pn-player button:focus-visible,.pn-top a:focus-visible{outline:2px solid #fff;outline-offset:2px}';
  document.head.appendChild(css);
  var bar = document.createElement('div'); bar.className = 'pn-player'; bar.hidden = true; bar.setAttribute('role', 'region'); bar.setAttribute('aria-label', 'Bulletin player');
  bar.innerHTML = '<button type="button" class="pn-pp" aria-label="Pause the bulletin"><svg viewBox="0 0 24 24"><path d="M6 4h4v16H6zM14 4h4v16h-4z"/></svg></button>' +
    '<div class="pn-mid"><div class="pn-top"><b>4-min bulletin</b><a href="' + href + '">Transcript</a></div><div class="pn-st" aria-live="polite">Starting…</div><div class="pn-bar"><i></i></div></div>' +
    '<button type="button" class="pn-x" aria-label="Stop and close"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.4" fill="none"/></svg></button>';
  document.body.appendChild(bar);
  var pp = bar.querySelector('.pn-pp'), st = bar.querySelector('.pn-st'), prog = bar.querySelector('.pn-bar i');
  function icon(play) { pp.querySelector('path').setAttribute('d', play ? 'M7 4l13 8-13 8z' : 'M6 4h4v16H6zM14 4h4v16h-4z');
    pp.setAttribute('aria-label', play ? 'Play the bulletin' : 'Pause the bulletin'); }

  function speak() {
    if (state !== 'playing') return;
    if (!paras || idx >= paras.length) { done(); return; }
    prog.style.width = Math.round(idx / paras.length * 100) + '%';
    st.textContent = 'Reading ' + (idx + 1) + ' of ' + paras.length;
    var u = new SpeechSynthesisUtterance(paras[idx]);
    if (voice) { u.voice = voice; u.lang = voice.lang; } else u.lang = 'en-IN';
    u.rate = 0.98;
    u.onend = function () { if (state === 'playing') { idx++; speak(); } };
    synth.speak(u);
    clearInterval(guard); guard = setInterval(function () { if (synth.speaking && !synth.paused) { synth.pause(); synth.resume(); } }, 10000);
  }
  function done() { clearInterval(guard); prog.style.width = '100%'; state = 'idle'; idx = 0; icon(true); st.textContent = 'Finished · tap play to hear it again'; }
  function begin() {
    state = 'playing'; icon(false); bar.hidden = false;
    if (!synth) { st.textContent = 'Read-aloud is not supported in this browser'; return; }
    // Unlock speech inside the tap (needed on iPhone), then play the signature tune.
    try { synth.cancel(); synth.speak(new SpeechSynthesisUtterance(' ')); } catch (e) {}
    st.textContent = '♪ Pringital signature tune…';
    inIntro = true;
    var next = function () { inIntro = false; intro.onended = null; load().then(function () {
      if (state !== 'playing') return;
      if (!paras) { st.textContent = 'Could not load the bulletin — open the transcript'; state = 'idle'; icon(true); return; }
      setTimeout(speak, 300); }); };
    intro.currentTime = 0; intro.onended = next;
    var p = intro.play(); if (p && p.catch) p.catch(next);
  }
  links.forEach(function (a) { a.addEventListener('click', function (e) {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
    e.preventDefault();
    if (state === 'idle') begin(); else pp.click();
  }); });
  pp.onclick = function () {
    if (state === 'playing') { state = 'paused'; intro.pause(); if (synth) synth.pause(); icon(true); st.textContent = 'Paused'; return; }
    if (state === 'paused') { state = 'playing'; icon(false);
      if (inIntro) { st.textContent = '♪ Pringital signature tune…'; intro.play(); return; }
      if (synth.paused) { synth.resume(); st.textContent = 'Reading ' + (idx + 1) + ' of ' + paras.length; } else speak(); return; }
    begin();
  };
  bar.querySelector('.pn-x').onclick = function () { state = 'idle'; inIntro = false; clearInterval(guard); intro.pause(); if (synth) synth.cancel(); idx = 0; prog.style.width = '0'; icon(true); bar.hidden = true; };
})();
