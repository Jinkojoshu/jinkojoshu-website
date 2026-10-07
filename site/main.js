// Typography option: add ?type=classic to the address for the earlier Bodoni version, ?type=new to go back.
(() => {
  const want = new URLSearchParams(location.search).get('type');
  try {
    if (want) sessionStorage.setItem('type', want);
    if ((want || sessionStorage.getItem('type')) === 'classic') document.body.classList.add('type-classic');
  } catch (_) { if (want === 'classic') document.body.classList.add('type-classic'); }
})();

// Cover showreel (index only): short cuts from the CLIPS - Showreel folder, played back to back.
const reel = document.getElementById('reel');
if (reel) {
  const reelClips = Array.from({ length: 14 }, (_, i) => `assets/reel/reel-${String(i + 1).padStart(2, '0')}.mp4`);
  // where to aim the crop per clip (default: centre) — clip 2 (Madonna) is aimed at Jinko turning on the right
  const reelFocus = { 1: '75% 40%' };
  // Two players take turns: while one plays, the next clip is already loaded in the other (no stutter between clips).
  const spare = reel.cloneNode();
  spare.removeAttribute('id');
  spare.removeAttribute('autoplay');
  spare.removeAttribute('poster');
  reel.after(spare);
  let front = reel, back = spare, reelIndex = 0;
  const load = (v, i) => {
    v.preload = 'auto';
    v.src = reelClips[i];
    v.style.objectPosition = reelFocus[i] || '';
  };
  load(front, 0);
  front.play().catch(() => {});
  load(back, 1);
  const next = (ev) => {
    if (ev.target !== front) return;
    reelIndex = (reelIndex + 1) % reelClips.length;
    back.play().catch(() => {});
    back.classList.add('front');
    front.classList.remove('front');
    [front, back] = [back, front];
    load(back, (reelIndex + 1) % reelClips.length);
  };
  front.classList.add('front');
  reel.addEventListener('ended', next);
  spare.addEventListener('ended', next);

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
  // hub issues (Dance, Styling): spread 1 is the index; projects are only reached from it and lead back to it
  const hub = reader.classList.contains('hub');
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
    const src = page.querySelectorAll('canvas');
    c.querySelectorAll('canvas').forEach((cv, i) => {
      cv.width = src[i].width; cv.height = src[i].height;
      cv.getContext('2d').drawImage(src[i], 0, 0);
    });
    const art = page.parentElement.querySelector(':scope > .spread-art');
    if (art) {
      const half = div('art-half', art.cloneNode(true));
      half.style.left = page.classList.contains('page-l') ? '0' : '-100%';
      half.querySelectorAll('video').forEach((v) => v.remove());
      c.append(half);
    }
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
    anim.finished.then(() => {
      layer.remove(); turning = false;
      if (queued >= 0) { const q = queued; queued = -1; if (q !== cur) show(q); }
    });
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
    prev.querySelector('.tl').textContent = cur === 0 ? 'Cover' : hub ? 'Back' : 'Previous';
    next.querySelector('.tl').textContent = last || (hub && cur === 0) ? reader.dataset.nextLabel : 'Next';
    reader.classList.toggle('on-project', hub && cur > 0);
    if (hub && !paged.matches && from !== cur) reader.scrollIntoView({ block: 'start' });
    count.textContent = `${cur + 1} / ${spreads.length}`;
    // highlight the section this spread belongs to
    let active = chips[0];
    for (const c of chips) if (indexOf(c.dataset.chip) < cur) active = c;
    active = chips.find((c) => indexOf(c.dataset.chip) === cur) || active;
    chips.forEach((c) => c.classList.toggle('on', c === active));
    if (paged.matches) history.replaceState(null, '', `#${spreads[cur].id}`);
  }

  let queued = -1;
  const go = (i) => { if (turning) queued = i; else show(i); };
  prev.addEventListener('click', () => (cur === 0 ? (location.href = 'index.html') : go(hub ? 0 : cur - 1)));
  next.addEventListener('click', () => (cur === spreads.length - 1 || hub ? (location.href = reader.dataset.next) : go(cur + 1)));
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
    document.body.classList.toggle('paged', paged.matches || hub);
    fitGiants();
  };
  paged.addEventListener('change', setMode);
  setMode();
  document.addEventListener('viewer-closed', (ev) => {
    const sp = ev.detail.closest('.spread');
    const i = sp ? spreads.indexOf(sp) : -1;
    if (i >= 0 && i !== cur) go(i);
  });
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

// Commercials strip: a still at rest, the film plays on hover, click opens the full commercial.
document.querySelectorAll('.strip-cell').forEach((cell) => {
  const v = cell.querySelector('video');
  if (!v) return;
  cell.addEventListener('mouseenter', () => {
    if (!v.src) v.src = v.dataset.preview;
    cell.classList.add('playing'); // visible first: Chrome pauses muted video it considers hidden
    v.play().catch(() => {});
  });
  cell.addEventListener('mouseleave', () => { v.pause(); cell.classList.remove('playing'); });
});

document.querySelectorAll('.strip-wrap').forEach((wrap) => {
  const strip = wrap.querySelector('.strip');
  const more = wrap.querySelector('.strip-more');
  if (!more) return;
  const atEnd = () => wrap.classList.toggle('at-end', strip.scrollLeft + strip.clientWidth >= strip.scrollWidth - 4);
  strip.addEventListener('scroll', atEnd, { passive: true });
  more.addEventListener('click', () => {
    strip.scrollBy({ left: (wrap.classList.contains('at-end') ? -1 : 1) * strip.clientWidth });
  });
});

// Globe (Dance): a dotted world you can turn with the mouse; click a city for its projects.
// Self-contained (no libraries): the land dots come from assets/globe-land.js.
const globe = document.querySelector('canvas.globe');
if (globe && window.GLOBE_LAND) {
  const places = JSON.parse(globe.dataset.places);
  const list = [...document.querySelectorAll('.place')];
  const pop = document.querySelector('.globe-pop');
  const ctx = globe.getContext('2d');
  const RAD = Math.PI / 180;
  const ink = '#141414', sheet = '#F5F3EE', mono = "500 10px 'IBM Plex Mono', monospace";
  let lon0 = 12, lat0 = 42;           // the point facing us (start over Europe)
  let size = 0, dpr = 1, R = 0, active = -1, popFor = -1, idleUntil = 0, tween = null, dirty = true;

  // land dots, unpacked once
  const dots = [];
  for (const [lat, step, runs] of window.GLOBE_LAND) {
    for (const [start, n] of runs) for (let k = 0; k < n; k++) dots.push([start + k * step, lat]);
  }
  const dotsRad = dots.map(([lo, la]) => [lo * RAD, Math.sin(la * RAD), Math.cos(la * RAD)]);

  // orthographic projection; returns null when the point is on the far side
  function project(lon, lat) {
    const l = (lon - lon0) * RAD, p = lat * RAD, p0 = lat0 * RAD;
    const cosc = Math.sin(p0) * Math.sin(p) + Math.cos(p0) * Math.cos(p) * Math.cos(l);
    if (cosc < 0.02) return null;
    return [size / 2 + R * Math.cos(p) * Math.sin(l),
            size / 2 - R * (Math.cos(p0) * Math.sin(p) - Math.sin(p0) * Math.cos(p) * Math.cos(l))];
  }

  function draw() {
    if (!size) return;
    dirty = false;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size, size);
    const c = size / 2;
    ctx.beginPath(); ctx.arc(c, c, R, 0, 2 * Math.PI); ctx.fillStyle = sheet; ctx.fill();
    // land
    const sp0 = Math.sin(lat0 * RAD), cp0 = Math.cos(lat0 * RAD), l0 = lon0 * RAD;
    const d = Math.max(1, size / 360);
    ctx.fillStyle = 'rgba(20,20,20,.78)';
    for (const [lr, sp, cp] of dotsRad) {
      const cl = Math.cos(lr - l0);
      if (sp0 * sp + cp0 * cp * cl < 0.02) continue;
      const x = c + R * cp * Math.sin(lr - l0), y = c - R * (cp0 * sp - sp0 * cp * cl);
      ctx.fillRect(x - d / 2, y - d / 2, d, d);
    }
    ctx.beginPath(); ctx.arc(c, c, R, 0, 2 * Math.PI); ctx.strokeStyle = ink; ctx.lineWidth = 1; ctx.stroke();
    // places
    ctx.font = mono; ctx.textBaseline = 'middle';
    places.forEach((pl, i) => {
      const pt = project(pl.lon, pl.lat);
      if (!pt) return;
      const [x, y] = pt, on = i === active;
      ctx.beginPath(); ctx.arc(x, y, on ? 5 : 3.5, 0, 2 * Math.PI); ctx.fillStyle = on ? '#8CCBEA' : ink; ctx.fill();
      ctx.lineWidth = 1.2; ctx.strokeStyle = ink; ctx.stroke();
      if (on) { ctx.beginPath(); ctx.arc(x, y, 11, 0, 2 * Math.PI); ctx.lineWidth = .8; ctx.stroke(); }
      const label = pl.city.split(' · ')[0].toUpperCase();
      const tw = ctx.measureText(label).width;
      let left = pl.side === 'left';
      if (!left && x + 15 + tw > size) left = true;
      if (left && x - 15 - tw < 0) left = false;
      ctx.fillStyle = ink;
      ctx.textAlign = left ? 'right' : 'left';
      ctx.fillText(label, x + (left ? -1 : 1) * (on ? 15 : 8), y + (pl.dy || 0));
    });
    placePop();
  }

  function resize() {
    const w = globe.getBoundingClientRect().width;
    if (!w) return;
    dpr = window.devicePixelRatio || 1;
    size = w; R = w / 2 - 2;
    globe.width = Math.round(w * dpr); globe.height = Math.round(w * dpr);
    draw();
  }
  new ResizeObserver(resize).observe(globe);

  const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  function focus(i) {
    active = i;
    list.forEach((li, k) => li.classList.toggle('on', k === i));
    const from = [lon0, lat0], to = [places[i].lon, places[i].lat * 0.8];
    if (to[0] - from[0] > 180) from[0] += 360;
    if (from[0] - to[0] > 180) from[0] -= 360;
    const t0 = performance.now();
    idleUntil = t0 + 6000;
    tween = (now) => {
      const k = Math.min(1, (now - t0) / 1000), e = ease(k);
      lon0 = from[0] + (to[0] - from[0]) * e;
      lat0 = from[1] + (to[1] - from[1]) * e;
      if (k === 1) tween = null;
    };
  }

  // drag to turn (mouse and touch)
  let drag = null;
  globe.addEventListener('pointerdown', (ev) => {
    drag = { x: ev.clientX, y: ev.clientY, moved: false };
    tween = null; idleUntil = Infinity;
  });
  addEventListener('pointermove', (ev) => {
    if (!drag) return;
    const dx = ev.clientX - drag.x, dy = ev.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) > 2) drag.moved = true;
    drag.x = ev.clientX; drag.y = ev.clientY;
    const k = 180 / (Math.PI * R);
    lon0 -= dx * k;
    lat0 = Math.max(-70, Math.min(70, lat0 + dy * k));
    dirty = true;
  });
  addEventListener('pointerup', () => {
    if (drag) idleUntil = performance.now() + 5000;
    setTimeout(() => { drag = null; }, 0);
  });

  // click a city: its projects appear next to it
  globe.addEventListener('click', (ev) => {
    if (drag && drag.moved) return;
    const b = globe.getBoundingClientRect();
    const mx = ev.clientX - b.left, my = ev.clientY - b.top;
    let hit = -1, best = 22;
    places.forEach((pl, i) => {
      const pt = project(pl.lon, pl.lat);
      if (!pt) return;
      const dist = Math.hypot(pt[0] - mx, pt[1] - my);
      if (dist < best) { best = dist; hit = i; }
    });
    if (hit >= 0) { focus(hit); openPop(hit); } else pop.hidden = true;
  });
  list.forEach((li, i) => li.addEventListener('mouseenter', () => focus(i)));
  globe.addEventListener('mouseenter', () => { if (!tween) idleUntil = Infinity; });
  globe.addEventListener('mouseleave', () => { if (!drag) idleUntil = performance.now() + 2500; });

  function openPop(i) {
    const pl = places[i];
    popFor = i;
    pop.replaceChildren();
    const city = document.createElement('b');
    city.className = 'city';
    city.textContent = pl.city;
    pop.append(city);
    for (const it of pl.items) {
      const a = document.createElement('a');
      a.href = it.h;
      if (it.h.startsWith('http')) { a.target = '_blank'; a.rel = 'noopener'; }
      a.innerHTML = '<b></b><span></span>';
      a.firstChild.textContent = it.t;
      a.lastChild.textContent = it.k;
      a.addEventListener('click', () => { pop.hidden = true; });
      pop.append(a);
    }
    pop.hidden = false;
    placePop();
  }
  function placePop() {
    if (!pop || pop.hidden || popFor < 0) return;
    const pl = places[popFor], pt = project(pl.lon, pl.lat);
    pop.style.visibility = pt ? '' : 'hidden';
    if (!pt) return;
    pop.style.left = `${globe.offsetLeft + pt[0]}px`;
    pop.style.top = `${globe.offsetTop + pt[1]}px`;
  }

  // gentle spin while nobody is touching it; only drawn when something changed and the globe is on screen
  const loop = (now) => {
    if (globe.offsetParent) {
      if (tween) { tween(now); dirty = true; }
      else if (!drag && now > idleUntil) { lon0 -= 0.06; dirty = true; }
      if (dirty) draw();
    }
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
}

// Lightbox: full films with sound, full-size photos.
const lb = document.getElementById('lightbox');
const lbBody = lb.querySelector('.lb-body');
const lbCap = lb.querySelector('.lb-cap');
const lbYt = lb.querySelector('.lb-yt');

const lbNote = lb.querySelector('.lb-note');
let lastNote = '';
document.addEventListener('click', (ev) => { const b = ev.target.closest('[data-note]'); lastNote = b ? b.dataset.note : ''; }, true);
// films in a group (the commercials) get arrows to step to the one next to it
let currentBtn = null;
document.addEventListener('click', (ev) => {
  const b = ev.target.closest('[data-video], [data-youtube], [data-vimeo], [data-full]');
  if (b && !lb.contains(b)) currentBtn = b;
}, true);
const lbPrev = lb.querySelector('.lb-prev'), lbNext = lb.querySelector('.lb-next');
const groupOf = () => {
  if (!currentBtn) return [];
  const g = currentBtn.closest('[data-group]');
  if (g) return [...g.querySelectorAll('.strip-cell')];
  // photos: every photo of the magazine in page order (lookbook, hair looks, on film, polaroids)
  if (currentBtn.matches('.ph-img, .pola')) return [...document.querySelectorAll('.spreads .ph-img, .spreads .pola')];
  // project photos: the ones on the same spread
  const spread = currentBtn.closest('.spread');
  if (spread && currentBtn.matches('.tile')) return [...spread.querySelectorAll('.tile')];
  return [];
};
const step = (dir) => {
  const items = groupOf();
  const i = items.indexOf(currentBtn);
  if (i < 0) return;
  items[(i + dir + items.length) % items.length].click();
};
lbPrev.addEventListener('click', () => step(-1));
lbNext.addEventListener('click', () => step(1));
addEventListener('keydown', (ev) => {
  if (!lb.open || lbNext.hidden) return;
  if (ev.key === 'ArrowRight') step(1);
  if (ev.key === 'ArrowLeft') step(-1);
});

function open(el, caption, youtubeUrl) {
  lbCap.textContent = caption || '';
  lbNote.textContent = lastNote;
  lbNote.hidden = !lastNote;
  lbYt.hidden = !youtubeUrl;
  if (youtubeUrl) lbYt.href = youtubeUrl;
  lbBody.replaceChildren(el);
  const grouped = groupOf().length > 1;
  lbPrev.hidden = lbNext.hidden = !grouped;
  if (!lb.open) lb.showModal();
}
lb.addEventListener('close', () => {
  lbBody.replaceChildren();
  // the magazine follows to the page of the last photo you looked at
  if (currentBtn) document.dispatchEvent(new CustomEvent('viewer-closed', { detail: currentBtn }));
});
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
    img.className = 'zoomable';
    open(img, btn.dataset.caption);
    zoomable(img);
  });
});

// Photos in the viewer can be zoomed: pinch or double-tap on a phone, double-click or scroll wheel on a computer;
// drag to look around. Not zoomed in, a sideways swipe goes to the next photo.
function zoomable(img) {
  let s = 1, x = 0, y = 0;
  const pts = new Map();
  let pinch = null, pan = null, swipe = null, lastTap = 0;
  const apply = (smooth) => {
    const maxX = Math.max(0, (img.offsetWidth * s - lbBody.clientWidth) / 2);
    const maxY = Math.max(0, (img.offsetHeight * s - lbBody.clientHeight) / 2);
    x = Math.max(-maxX, Math.min(maxX, x)); y = Math.max(-maxY, Math.min(maxY, y));
    img.style.transition = smooth ? 'transform .25s ease' : 'none';
    img.style.transform = `translate(${x}px, ${y}px) scale(${s})`;
    img.classList.toggle('zoomed', s > 1.01);
  };
  // zoom to scale ns, keeping the point (cx, cy) on the screen where it is
  const zoomAt = (ns, cx, cy, smooth) => {
    ns = Math.max(1, Math.min(5, ns));
    const r = lbBody.getBoundingClientRect();
    const px = cx - (r.left + r.width / 2), py = cy - (r.top + r.height / 2);
    x = px - (px - x) * (ns / s); y = py - (py - y) * (ns / s); s = ns;
    if (s === 1) { x = 0; y = 0; }
    apply(smooth);
  };
  const toggle = (cx, cy) => zoomAt(s > 1.01 ? 1 : 2.5, cx, cy, true);

  let lastType = 'mouse';
  img.addEventListener('dblclick', (ev) => { if (lastType !== 'touch') toggle(ev.clientX, ev.clientY); });
  img.addEventListener('wheel', (ev) => { ev.preventDefault(); zoomAt(s * Math.exp(-ev.deltaY / 300), ev.clientX, ev.clientY); }, { passive: false });
  img.addEventListener('pointerdown', (ev) => {
    lastType = ev.pointerType;
    try { img.setPointerCapture(ev.pointerId); } catch (e) { /* not a live pointer */ }
    pts.set(ev.pointerId, [ev.clientX, ev.clientY]);
    if (pts.size === 2) {
      const [[ax, ay], [bx, by]] = [...pts.values()];
      pinch = { d: Math.hypot(ax - bx, ay - by), s }; pan = swipe = null;
    } else if (pts.size === 1) {
      pan = { x0: ev.clientX - x, y0: ev.clientY - y };
      swipe = { x: ev.clientX, y: ev.clientY, t: Date.now() };
    }
  });
  img.addEventListener('pointermove', (ev) => {
    if (!pts.has(ev.pointerId)) return;
    pts.set(ev.pointerId, [ev.clientX, ev.clientY]);
    if (pinch && pts.size === 2) {
      const [[ax, ay], [bx, by]] = [...pts.values()];
      zoomAt(pinch.s * Math.hypot(ax - bx, ay - by) / pinch.d, (ax + bx) / 2, (ay + by) / 2);
    } else if (pan && s > 1.01) {
      x = ev.clientX - pan.x0; y = ev.clientY - pan.y0; apply();
    }
  });
  const up = (ev) => {
    if (!pts.has(ev.pointerId)) return;
    pts.delete(ev.pointerId);
    if (pts.size < 2) pinch = null;
    if (pts.size === 1) { const [[px, py]] = [...pts.values()]; pan = { x0: px - x, y0: py - y }; }
    if (pts.size) return;
    if (swipe && ev.type === 'pointerup') {
      const dx = ev.clientX - swipe.x, dy = ev.clientY - swipe.y, quick = Date.now() - swipe.t < 300;
      if (s <= 1.01 && Math.abs(dx) > 60 && Math.abs(dx) > 1.5 * Math.abs(dy) && !lbNext.hidden) step(dx < 0 ? 1 : -1);
      else if (ev.pointerType === 'touch' && quick && Math.hypot(dx, dy) < 12) {
        if (Date.now() - lastTap < 320) { toggle(ev.clientX, ev.clientY); lastTap = 0; } else lastTap = Date.now();
      }
    }
    swipe = pan = null;
  };
  img.addEventListener('pointerup', up);
  img.addEventListener('pointercancel', up);
}
