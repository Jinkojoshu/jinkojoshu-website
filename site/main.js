// Cover showreel (index only): short cuts from the CLIPS - Showreel folder, played back to back.
const reel = document.getElementById('reel');
if (reel) {
  const reelClips = Array.from({ length: 11 }, (_, i) => `assets/reel/reel-${String(i + 1).padStart(2, '0')}.mp4`);
  // where to aim the crop per clip (default: centre) — clip 2 (Madonna) is aimed at Jinko turning on the right
  const reelFocus = { 1: '75% 40%' };
  let reelIndex = 0;
  const playReel = () => {
    reel.src = reelClips[reelIndex];
    reel.style.objectPosition = reelFocus[reelIndex] || '';
    reel.play().catch(() => {});
  };
  reel.addEventListener('ended', () => {
    reelIndex = (reelIndex + 1) % reelClips.length;
    playReel();
  });
  playReel();

  // Sound: the showreel track. Browsers never autoplay with sound, so the visitor switches it on.
  const track = document.getElementById('reel-audio');
  const sound = document.querySelector('.sound');
  sound.addEventListener('click', () => {
    const on = track.paused;
    if (on) track.play().catch(() => {}); else track.pause();
    sound.setAttribute('aria-pressed', String(on));
    sound.querySelector('.sound-txt').textContent = on ? 'Sound off' : 'Sound on';
  });

  // Opening the issue: the cover's right page turns over before the magazine opens.
  const coverMag = document.querySelector('.cover-mag');
  document.querySelectorAll('.open-issue').forEach((link) => link.addEventListener('click', (ev) => {
    if (matchMedia('(max-width: 760px), (prefers-reduced-motion: reduce)').matches) return;
    ev.preventDefault();
    const right = coverMag.querySelector('.page-r').cloneNode(true);
    right.querySelectorAll('video, audio').forEach((m) => m.removeAttribute('src'));
    const blank = document.createElement('div');
    blank.className = 'page page-l';
    const mk = (cls, ...kids) => { const d = document.createElement('div'); d.className = cls; d.append(...kids); return d; };
    const front = mk('face front', right, mk('shade'));
    const back = mk('face back', blank, mk('shade'));
    const leaf = mk('flipper from-r', front, back);
    coverMag.append(mk('flip-layer', leaf));
    const t = { duration: 850, easing: 'cubic-bezier(.42,.02,.28,1)', fill: 'forwards' };
    leaf.animate([{ transform: 'rotateY(0deg)' }, { transform: 'rotateY(-90deg) translateZ(30px)', offset: .5 }, { transform: 'rotateY(-180deg)' }], t);
    front.lastChild.animate([{ opacity: 0 }, { opacity: 1, offset: .5 }, { opacity: 1 }], t);
    back.lastChild.animate([{ opacity: 1 }, { opacity: 1, offset: .5 }, { opacity: 0 }], t);
    try { sessionStorage.setItem('arrive', '1'); } catch (_) { /* private mode */ }
    setTimeout(() => { location.href = link.href; }, 800);
  }));
}

// Giant stacked letters: scale them to the band's width, then stretch them tall to fill its height.
function fitGiants() {
  document.querySelectorAll('.band').forEach((band) => {
    const g = band.querySelector('.giant');
    if (!band.clientWidth) return; // on a hidden spread; fitted when shown
    g.style.setProperty('--stretch', 1);
    g.style.fontSize = '100px';
    let widest = 0;
    for (const row of g.children) {
      const r = document.createRange();
      r.selectNodeContents(row);
      widest = Math.max(widest, r.getBoundingClientRect().width);
    }
    let size = (100 * band.clientWidth) / widest;
    g.style.fontSize = `${size}px`;
    let stretch = band.clientHeight / g.offsetHeight;
    if (stretch < 1) {
      size *= stretch;
      g.style.fontSize = `${size}px`;
      stretch = 1;
    }
    g.style.setProperty('--stretch', Math.min(stretch, 1.7).toFixed(3));
  });
}
function fitMasts() {
  document.querySelectorAll('.mini-mast .fit').forEach((t) => {
    t.style.fontSize = '100px';
    t.style.fontSize = `${(100 * t.parentElement.clientWidth) / t.getBoundingClientRect().width}px`;
  });
}
const fitAll = () => { fitGiants(); fitMasts(); };
document.fonts.ready.then(fitAll);
addEventListener('resize', fitAll);

// Magazine reader: one spread at a time; Next / Previous turns a page like a real magazine.
// (Phones just scroll through the stacked pages.)
const reader = document.querySelector('.reader');
if (reader) {
  const spreads = [...reader.querySelectorAll('.spread')];
  const prev = reader.querySelector('.turn-prev');
  const next = reader.querySelector('.turn-next');
  const count = reader.querySelector('.count');
  const chips = [...reader.querySelectorAll('[data-chip]')];
  const paged = matchMedia('(min-width: 761px)');
  const calm = matchMedia('(prefers-reduced-motion: reduce)');
  let cur = 0;
  let turning = false;

  const indexOf = (id) => {
    const el = id && document.getElementById(id);
    const sp = el && el.closest('.spread');
    return sp ? spreads.indexOf(sp) : -1;
  };

  // a still copy of a page for the turning leaf (no ids, no playing video)
  const copy = (page) => {
    const c = page.cloneNode(true);
    c.removeAttribute('id');
    c.querySelectorAll('[id]').forEach((n) => n.removeAttribute('id'));
    c.querySelectorAll('video').forEach((v) => { v.removeAttribute('src'); v.removeAttribute('autoplay'); });
    return c;
  };
  const div = (cls, ...kids) => {
    const d = document.createElement('div');
    d.className = cls;
    d.append(...kids);
    return d;
  };

  function turnPage(from, to, dir) {
    const [oldL, oldR] = spreads[from].querySelectorAll(':scope > .page');
    const [newL, newR] = spreads[to].querySelectorAll(':scope > .page');
    const fwd = dir > 0;
    // the page that stays put, the leaf that turns (old page on its front, new page on its back), and its shadow
    const still = div('flip-static', copy(fwd ? oldL : oldR));
    still.style.left = fwd ? '0' : '50%';
    const front = div('face front', copy(fwd ? oldR : oldL), div('shade'));
    const back = div('face back', copy(fwd ? newL : newR), div('shade'));
    const leaf = div(`flipper ${fwd ? 'from-r' : 'from-l'}`, front, back);
    const cast = div(`flip-cast ${fwd ? 'on-r' : 'on-l'}`);
    const layer = div('flip-layer', still, cast, leaf);
    spreads[to].append(layer);

    const timing = { duration: 950, easing: 'cubic-bezier(.42,.02,.28,1)', fill: 'forwards' };
    const end = fwd ? -180 : 180;
    const lift = fwd ? -8 : 8;
    turning = true;
    const anim = leaf.animate([
      { transform: 'rotateY(0deg)' },
      { transform: `rotateY(${end / 2}deg) rotateX(${lift / 4}deg) translateZ(30px)`, offset: 0.5 },
      { transform: `rotateY(${end}deg)` },
    ], timing);
    front.lastChild.animate([{ opacity: 0 }, { opacity: 1, offset: 0.5 }, { opacity: 1 }], timing);
    back.lastChild.animate([{ opacity: 1 }, { opacity: 1, offset: 0.5 }, { opacity: 0 }], timing);
    cast.animate([{ opacity: 0.9 }, { opacity: 0.4, offset: 0.5 }, { opacity: 0 }], timing);
    anim.finished.then(() => { layer.remove(); turning = false; });
  }

  function show(i) {
    const from = cur;
    cur = Math.max(0, Math.min(spreads.length - 1, i));
    spreads.forEach((sp, k) => {
      sp.classList.toggle('on', k === cur);
      if (k !== cur) sp.querySelectorAll('video').forEach((v) => v.pause());
    });
    fitGiants();
    if (from !== cur && paged.matches && !calm.matches) turnPage(from, cur, cur > from ? 1 : -1);

    const last = cur === spreads.length - 1;
    prev.querySelector('.tl').textContent = cur === 0 ? 'Cover' : 'Previous';
    next.querySelector('.tl').textContent = last ? reader.dataset.nextLabel : 'Next';
    count.textContent = `${cur + 1} / ${spreads.length}`;
    // highlight the section this spread belongs to
    let active = chips[0];
    for (const c of chips) if (indexOf(c.dataset.chip) < cur) active = c;
    active = chips.find((c) => indexOf(c.dataset.chip) === cur) || active;
    chips.forEach((c) => c.classList.toggle('on', c === active));
    if (paged.matches) history.replaceState(null, '', `#${spreads[cur].id}`);
  }

  const go = (i) => { if (!turning) show(i); };
  prev.addEventListener('click', () => (cur === 0 ? (location.href = 'index.html') : go(cur - 1)));
  next.addEventListener('click', () => (cur === spreads.length - 1 ? (location.href = reader.dataset.next) : go(cur + 1)));
  chips.forEach((c) => c.addEventListener('click', (ev) => {
    if (!paged.matches) return; // phones: normal jump-scroll
    ev.preventDefault();
    go(indexOf(c.dataset.chip));
  }));
  addEventListener('keydown', (ev) => {
    if (!paged.matches || document.getElementById('lightbox').open) return;
    if (ev.key === 'ArrowRight') next.click();
    if (ev.key === 'ArrowLeft') prev.click();
  });

  const setMode = () => {
    document.body.classList.toggle('paged', paged.matches);
    fitGiants();
  };
  paged.addEventListener('change', setMode);
  setMode();
  addEventListener('hashchange', () => { const i = indexOf(location.hash.slice(1)); if (i >= 0 && i !== cur) go(i); });
  try {
    if (sessionStorage.getItem('arrive')) { sessionStorage.removeItem('arrive'); reader.classList.add('arrive'); }
  } catch (_) { /* private mode */ }
  cur = Math.max(0, indexOf(location.hash.slice(1)));
  show(cur);
}

// Lazy-load preview videos; loops autoplay on screen, cards preview on hover.
const io = new IntersectionObserver((entries) => {
  for (const { target: v, isIntersecting } of entries) {
    if (isIntersecting) {
      if (!v.src) v.src = v.dataset.src;
      if (v.classList.contains('autoplay')) v.play().catch(() => {});
    } else {
      v.pause();
    }
  }
}, { rootMargin: '200px' });
document.querySelectorAll('video[data-src]').forEach((v) => io.observe(v));

document.querySelectorAll('.card').forEach((card) => {
  const v = card.querySelector('video');
  if (!v) return;
  card.addEventListener('mouseenter', () => v.play().catch(() => {}));
  card.addEventListener('mouseleave', () => { if (!v.classList.contains('autoplay')) v.pause(); });
});

// Lightbox: full films with sound, full-size photos.
const lb = document.getElementById('lightbox');
const lbBody = lb.querySelector('.lb-body');
const lbCap = lb.querySelector('.lb-cap');
const lbYt = lb.querySelector('.lb-yt');

function open(el, caption, youtubeUrl) {
  lbCap.textContent = caption || '';
  lbYt.hidden = !youtubeUrl;
  if (youtubeUrl) lbYt.href = youtubeUrl;
  lbBody.replaceChildren(el);
  lb.showModal();
}
lb.addEventListener('close', () => lbBody.replaceChildren());
lb.querySelector('.lb-close').addEventListener('click', () => lb.close());
lb.addEventListener('click', (e) => { if (e.target === lbBody) lb.close(); });

document.querySelectorAll('[data-video]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const v = document.createElement('video');
    v.src = btn.dataset.video;
    v.controls = true;
    v.autoplay = true;
    v.playsInline = true;
    open(v, btn.dataset.caption);
  });
});

document.querySelectorAll('[data-youtube]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const f = document.createElement('iframe');
    const start = btn.dataset.start ? `&start=${btn.dataset.start}` : '';
    f.src = `https://www.youtube-nocookie.com/embed/${btn.dataset.youtube}?autoplay=1&rel=0${start}`;
    f.title = btn.dataset.caption || 'YouTube video';
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    const t = btn.dataset.start ? `&t=${btn.dataset.start}s` : '';
    open(f, btn.dataset.caption, `https://www.youtube.com/watch?v=${btn.dataset.youtube}${t}`);
  });
});

document.querySelectorAll('[data-vimeo]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = `https://player.vimeo.com/video/${btn.dataset.vimeo}?autoplay=1&dnt=1`;
    f.title = btn.dataset.caption || 'Vimeo video';
    f.allow = 'autoplay; fullscreen; picture-in-picture';
    f.allowFullscreen = true;
    if (btn.dataset.vertical) f.className = 'vertical';
    open(f, btn.dataset.caption);
  });
});

document.querySelectorAll('[data-full]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const img = document.createElement('img');
    img.src = btn.dataset.full;
    img.alt = btn.querySelector('img').alt;
    open(img, btn.dataset.caption);
  });
});
