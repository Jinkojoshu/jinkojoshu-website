// Cover showreel: short cuts from the CLIPS - Showreel folder, played back to back.
const reel = document.getElementById('reel');
const reelClips = Array.from({ length: 11 }, (_, i) => `assets/reel/reel-${String(i + 1).padStart(2, '0')}.mp4`);
let reelIndex = 0;
function playReel() {
  reel.src = reelClips[reelIndex];
  reel.play().catch(() => {});
}
reel.addEventListener('ended', () => {
  reelIndex = (reelIndex + 1) % reelClips.length;
  playReel();
});
playReel();

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
  card.addEventListener('mouseleave', () => v.pause());
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

document.querySelectorAll('[data-full]').forEach((btn) => {
  btn.addEventListener('click', () => {
    const img = document.createElement('img');
    img.src = btn.dataset.full;
    img.alt = btn.querySelector('img').alt;
    open(img, btn.dataset.caption);
  });
});

document.getElementById('year').textContent = new Date().getFullYear();
