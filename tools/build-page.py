#!/usr/bin/env python3
"""Generates site/index.html from the content lists below.
Edit the lists (titles, captions, handwritten names, years) and run:  python3 tools/build-page.py
"""
from html import escape as e
from pathlib import Path

# ── Commercials: (title, sub, thumbnail, full video, hover clip or None, award or None)
COMMERCIALS = [
    ("Nike", "Member Days · 2023", "nike", "nike-member-days", "clip-nike-member-days-4x5", None),
    ("Samsung", "Galaxy Z Flip6 · global campaign", "samsung", "samsung", None, None),
    ("bol × JBL", "Sport Offsite · 2026", "boljbl", "bol-x-jbl", None, None),
    ("Lavish", "Commercial · 2025", "lavish", "lavish", "clip-lavish", None),
    ("Philips", "Commercial · 2025", "philips", "philips", None, None),
    ("Foot Athletes", "Commercial · 2025", "taf", "taf-2025", None, None),
    ("Lucid Dreaming", "Trailer · 2023", "lucid", "lucid-dreaming-trailer", "clip-lucid-dreaming", "Gouden Kalf competition"),
    ("Nike", "Behind the scenes · male model", "nikebts", "nike-bts", None, None),
]

# ── Lookbook prints: (image slug, handwritten name, caption)
LOOKBOOK = [
    ("jinko-portrait", "Portrait", "Portrait"),
    ("nike-member-days-look", "Nike", "Nike — Member Days"),
    ("polaroid-01", "Polas", "Polaroid"),
    ("polaroid-02", "Polas", "Polaroid"),
    ("polaroid-03", "Polas", "Polaroid"),
    ("bol-jbl-01", "bol × JBL", "bol × JBL — campaign still"),
    ("bol-jbl-02", "bol × JBL", "bol × JBL — campaign still"),
    ("bol-jbl-03", "bol × JBL", "bol × JBL — campaign still"),
    ("adidas-lookbook", "Adidas", "Adidas lookbook"),
    ("pasqual-shoot", "Pasqual", "Pasqual shoot"),
    ("editorial-01", "Editorial", "Editorial"),
    ("editorial-03", "Editorial", "Editorial"),
    ("nath-martin", "Nath Martin", "Photo: Nath Martin"),
    ("film-2025-01", "Film '25", "Film, 2025"),
    ("film-2025-02", "Film '25", "Film, 2025"),
    ("film-2025-03", "Film '25", "Film, 2025"),
    ("editorial-04", "Editorial", "Editorial"),
    ("editorial-05", "Editorial", "Editorial"),
    ("editorial-02", "Green", "Editorial"),
    ("editorial-06", "Editorial", "Editorial"),
    ("lucid-dreaming-group", "Lucid", "Lucid Dreaming — cast"),
]

PHOTOGRAPHY = [f"photography-{i:02d}" for i in range(1, 15)]

TGS_PHOTOS = ["tgs-01", "tgs-02", "tgs-03"]
YADE_PHOTOS = ["yade-01", "yade-02", "yade-03", "yade-04"]
STYLING_PHOTOS = [("coast-contra-01", "Coast Contra"), ("coast-contra-02", "Coast Contra"), ("coast-contra-03", "Coast Contra")]


def video_card(title, sub, thumb, video, clip=None, no="", ratio="r-45", award=None, caption=None):
    media = (f'<video data-src="assets/video/{clip}.mp4" poster="assets/thumbs/{thumb}.jpg" muted loop playsinline preload="none"></video>'
             if clip else f'<img src="assets/thumbs/{thumb}.jpg" alt="" loading="lazy">')
    aw = f'<span class="award">★ {e(award)}</span>' if award else ""
    return f'''      <button class="card" data-video="assets/video/{video}.mp4" data-caption="{e(caption or f'{title} — {sub}')}">
        <div class="cardimg {ratio}">{media}<span class="no">{e(no)}</span><span class="play">▶</span>{aw}</div>
        <span class="c-brand">{e(title)}</span><span class="c-sub">{e(sub)}</span>
      </button>'''


def yt_card(yid, title, sub, no, caption, start=None):
    st = f' data-start="{start}"' if start else ""
    return f'''      <button class="card" data-youtube="{yid}"{st} data-caption="{e(caption)}">
        <div class="cardimg r-169"><img src="assets/yt/{yid}.jpg" alt="" loading="lazy"><span class="no">{e(no)}</span><span class="play">▶</span></div>
        <span class="c-brand">{e(title)}</span><span class="c-sub">{e(sub)}</span>
      </button>'''


def photo_card(slug, title, sub, caption):
    return f'''      <button class="card" data-full="assets/img/{slug}.jpg" data-caption="{e(caption)}">
        <div class="cardimg r-32"><img src="assets/img/{slug}-sm.jpg" alt="{e(caption)}" loading="lazy"></div>
        <span class="c-brand">{e(title)}</span><span class="c-sub">{e(sub)}</span>
      </button>'''


def prints(items):
    out = []
    for i, (slug, name, cap) in enumerate(items, 1):
        out.append(f'    <button class="print" data-full="assets/img/{slug}.jpg" data-caption="{e(f"{i:02d} — {cap}")}">'
                   f'<img src="assets/img/{slug}-sm.jpg" alt="{e(cap)}" loading="lazy">'
                   f'<span class="hand no">{i}</span><span class="hand name">{e(name)}</span></button>')
    return "\n".join(out)


def media_grid(slugs, caption):
    return "\n".join(
        f'      <button class="tile" data-full="assets/img/{s}.jpg" data-caption="{e(caption)}"><img src="assets/img/{s}-sm.jpg" alt="{e(caption)}" loading="lazy"></button>'
        for s in slugs)


commercials_html = "\n".join(
    video_card(t, s, th, v, c, no=f"{i:02d}", award=a) for i, (t, s, th, v, c, a) in enumerate(COMMERCIALS, 1))

page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jinko Joshu — Magazine Nº01</title>
  <meta name="description" content="Jinko Joshu — Amsterdam-based performer. Commercials, lookbook, dance, styling and the label Akyna.">
  <meta property="og:title" content="Jinko Joshu — Nº01">
  <meta property="og:image" content="assets/img/jinko-portrait.jpg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=Noto+Sans+JP:wght@700&family=Reenie+Beanie&display=swap" rel="stylesheet">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="paper">

<!-- ───────── Cover ───────── -->
<section id="cover" class="wrap cover">
  <div class="kicker rule-b">
    <span>Issue Nº01 — Autumn 2026</span>
    <span class="hide-sm">Commercials · Lookbook · Dance · Styling · Akyna</span>
    <a class="kick-link" href="https://www.instagram.com/jinkojoshu/" target="_blank" rel="noopener">Amsterdam · @jinkojoshu</a>
  </div>

  <h1 class="masthead">Jinko Joshu</h1>

  <div class="cover-reel">
    <video id="reel" muted playsinline autoplay poster="assets/poster/reel.jpg" aria-label="Showreel: short moments from Jinko Joshu's work"></video>
    <span class="tag tag-accent"><span class="jp">創刊号</span>First issue</span>
  </div>

  <nav class="strip" aria-label="In this issue">
    <a class="cl" href="#commercials"><span class="no">01</span><span class="nm">Commercials</span><span class="sb">Nike · Samsung · bol × JBL</span></a>
    <a class="cl" href="#lookbook"><span class="no">02</span><span class="nm">Lookbook</span><span class="sb">In front of the lens</span></a>
    <a class="cl" href="#dance"><span class="no">03</span><span class="nm">Dance</span><span class="sb">Madonna · Ghetto Funk</span></a>
    <a class="cl" href="#styling"><span class="no">04</span><span class="nm">Styling</span><span class="sb">Coast Contra — Don’t Worry</span></a>
    <a class="cl" href="#akyna"><span class="no">05</span><span class="nm">Akyna</span><span class="sb">The label</span></a>
    <a class="cl" href="#contact"><span class="no">06</span><span class="nm">Work with me</span><span class="sb">Bookings &amp; collabs</span></a>
  </nav>

  <div class="cover-foot">
    <span class="jp jp-sign">ジンコ・ジョシュ</span>
    <div class="barcode" aria-hidden="true"></div>
  </div>
</section>

<!-- ───────── Contents ───────── -->
<section id="contents" class="wrap section">
  <div class="spread">
    <div class="col">
      <div class="head-row rule-b">
        <h2 class="h-sec">Contents</h2>
        <span class="meta">Nº01</span>
      </div>
      <div class="toc-list">
        <a class="toc" href="#commercials"><span>04</span><b>Commercials</b><span>Campaigns</span></a>
        <a class="toc" href="#lookbook"><span>12</span><b>Lookbook</b><span>In front of the lens</span></a>
        <a class="toc" href="#photography"><span>16</span><b>Through my lens</b><span>Photography</span></a>
        <a class="toc" href="#dance"><span>20</span><b>Dance</b><span>Madonna · Claude</span></a>
        <a class="toc" href="#tgs"><span>22</span><b>The Greatest Show</b><span>Nanjing, China</span></a>
        <a class="toc" href="#yade"><span>24</span><b>Yade Lauren</b><span>Festival show</span></a>
        <a class="toc" href="#ghettofunk"><span>26</span><b>Ghetto Funk</b><span>The collective</span></a>
        <a class="toc" href="#styling"><span>30</span><b>Styling</b><span>Projects</span></a>
        <a class="toc" href="#akyna"><span>36</span><b>Akyna</b><span>The label</span></a>
        <a class="toc" href="#contact"><span>40</span><b>Work with me</b><span>Contact</span></a>
      </div>
      <div class="who">
        <span class="who-h">Who is Jinko Joshu?</span>
        <p>An Amsterdam-based performer working in commercials and campaigns. Jinko also dances on stage and at events, choreographs, shoots photography, styles — and runs the clothing label Akyna.</p>
      </div>
      <div class="box awards">
        <span class="box-h">Awards</span>
        <div class="dl"><span>Lucid Dreaming</span><i></i><span>Gouden Kalf competition</span></div>
        <div class="dl"><span>Coast Contra — Don’t Worry</span><i></i><span>Berlin Music Video Awards</span></div>
      </div>
    </div>
    <figure class="look">
      <div class="look-frame">
        <img src="assets/mag/halftone-portrait.png" alt="Jinko Joshu, full-length halftone portrait">
        <span class="look-no">Look<br>01</span>
        <span class="jp look-jp">ジンコ・ジョシュ</span>
      </div>
      <figcaption class="meta-row"><span>Jinko Joshu</span><span>Look 01/21</span></figcaption>
    </figure>
  </div>
</section>

<!-- ───────── 01 · Commercials ───────── -->
<section id="commercials" class="wrap section">
  <div class="meta-row"><span>Feature 01</span><span>p. 04</span></div>
  <h2 class="h-feature">Commercials</h2>
  <div class="comm">
    <div class="cards">
{commercials_html}
    </div>
    <aside class="box">
      <span class="box-h">Selected work</span>
      <div class="dl"><span>Nike — Member Days</span><i></i><span>(2023)</span></div>
      <div class="dl"><span>Lucid Dreaming</span><i></i><span>(2023)</span></div>
      <div class="dl"><span>Samsung — Galaxy Z Flip6</span><i></i><span>(2024)</span></div>
      <div class="dl"><span>Philips</span><i></i><span>(2025)</span></div>
      <div class="dl"><span>Lavish</span><i></i><span>(2025)</span></div>
      <div class="dl"><span>Foot Athletes</span><i></i><span>(2025)</span></div>
      <div class="dl"><span>Claude — C’est La Vie</span><i></i><span>(2025)</span></div>
      <div class="dl"><span>bol × JBL</span><i></i><span>(2026)</span></div>
      <div class="dl"><span>Madonna — Confessions II</span><i></i><span>(Film)</span></div>
      <span class="box-note">★ Lucid Dreaming — Gouden Kalf competition.</span>
    </aside>
  </div>
</section>

<!-- ───────── 02 · Lookbook ───────── -->
<section id="lookbook" class="wrap section">
  <div class="meta-row"><span>Feature 02</span><span>p. 12</span></div>
  <h2 class="h-feature">Lookbook</h2>
  <p class="deck deck-wide">In front of the lens — campaigns, editorials and polaroids.</p>
  <div class="wall">
{prints(LOOKBOOK)}
  </div>

  <div id="photography" class="sub">
    <div class="meta-row"><span>Feature 02.1</span><span>p. 16</span></div>
    <div class="head-row rule-b"><h3 class="h-sec">Through my lens</h3><span class="meta">Shot by Jinko · film</span></div>
    <div class="wall">
{prints([(s, "Film", "Shot by Jinko Joshu") for s in PHOTOGRAPHY])}
    </div>
  </div>
</section>

<!-- ───────── 03 · Dance ───────── -->
<section id="dance" class="wrap section">
  <div class="meta-row"><span>Feature 03</span><span>p. 20</span></div>
  <h2 class="h-feature">Dance</h2>

  <div class="highlight">
    <button class="card" data-youtube="yJtckcMHM2g" data-start="415" data-caption="Madonna — Confessions II, The Film · Jinko from 06:55">
      <div class="cardimg r-169">
        <img src="assets/yt/yJtckcMHM2g.jpg" alt="" loading="lazy">
        <span class="no">Highlight</span><span class="play">▶</span>
        <span class="timestamp">▶ 06:55</span>
      </div>
    </button>
    <div class="highlight-text">
      <span class="meta">Music video · Madonna</span>
      <span class="feat-h">Confessions II</span>
      <p class="deck">Dancer in Madonna’s <i>Confessions II — The Film</i>. My part starts at 06:55; the player jumps straight there.</p>
      <button class="more-btn" data-youtube="yJtckcMHM2g" data-start="415" data-caption="Madonna — Confessions II, The Film · Jinko from 06:55">Watch from 06:55 →</button>
    </div>
  </div>

  <div class="highlight highlight-rev">
    <div class="highlight-text">
      <span class="meta">Music video · Eurovision 2025</span>
      <span class="feat-h">Claude — C’est La Vie</span>
      <p class="deck">Dancer in the official music video for Claude’s <i>C’est La Vie</i>, the Netherlands’ entry for Eurovision 2025.</p>
      <button class="more-btn" data-youtube="hEHwr5k9pd0" data-caption="Claude — C’est La Vie · Official Music Video · Eurovision 2025">Watch →</button>
    </div>
    <button class="card" data-youtube="hEHwr5k9pd0" data-caption="Claude — C’est La Vie · Official Music Video · Eurovision 2025">
      <div class="cardimg r-169"><img src="assets/yt/hEHwr5k9pd0.jpg" alt="" loading="lazy"><span class="no">Eurovision</span><span class="play">▶</span></div>
    </button>
  </div>

  <!-- Project: The Greatest Show -->
  <article id="tgs" class="project">
    <div class="project-text">
      <span class="meta">Project · Nanjing, China</span>
      <h3 class="feat-h">The Greatest Show</h3>
      <p class="deck">We were invited to Nanjing to create a two-hour show — and to dance in it ourselves, alongside 170 guest dancers from China. A challenge both as choreographer and as dancer.</p>
      <span class="roles"><span>Choreographer</span><span>Dancer</span></span>
    </div>
    <div class="project-media">
      <button class="card tile-wide" data-video="assets/video/dance-performance.mp4" data-caption="The Greatest Show — Nanjing">
        <div class="cardimg r-169"><img src="assets/thumbs/dance-performance.jpg" alt="" loading="lazy"><span class="no">Film</span><span class="play">▶</span></div>
      </button>
{media_grid(TGS_PHOTOS, "The Greatest Show — Nanjing, China")}
    </div>
  </article>

  <!-- Project: Yade Lauren -->
  <article id="yade" class="project">
    <div class="project-text">
      <span class="meta">Project · Festival show</span>
      <h3 class="feat-h">Yade Lauren</h3>
      <p class="deck">Yade Lauren asked me to join her show as a performer. We played a festival together and brought more of a fashion vibe to her set.</p>
      <span class="roles"><span>Performer</span></span>
    </div>
    <div class="project-media">
{media_grid(YADE_PHOTOS, "Yade Lauren — festival show")}
    </div>
  </article>

  <div class="sub">
    <div class="head-row rule-b"><h3 class="h-sec">More dance</h3><span class="meta">Stage · sessions · collabs</span></div>
    <div class="cards cards-3">
{video_card("JMD", "Stage", "dance-jmd", "dance-jmd", ratio="r-169", no="JMD")}
{video_card("Dam Square", "Street session · Amsterdam", "dance-footage", "dance-footage", ratio="r-169", no="Session")}
{video_card("Hashna", "Collab", "dance-hashna", "dance-hashna", ratio="r-169", no="Collab")}
    </div>
  </div>

  <!-- Sub-category: Ghetto Funk Collective -->
  <div id="ghettofunk" class="sub">
    <div class="meta-row"><span>Feature 03.1</span><span>p. 26</span></div>
    <div class="head-row rule-b">
      <h3 class="h-sec">Ghetto Funk Collective</h3>
      <span class="badge">Member of the collective</span>
    </div>
    <div class="gf">
{yt_card("0otuG_RO1mI", "“Just Feel”", "10 year anniversary", "GF/01", "“Just Feel” — 10 year anniversary, Ghetto Funk Collective")}
{yt_card("oVR1SJvekRw", "Damn Right", "We Are Somebody", "GF/02", "Ghetto Funk Collective — Damn Right We Are Somebody")}
{yt_card("CV84FmeBRbU", "Keep On Lovin’ Me", "The Whispers", "GF/03", "Ghetto Funk Collective — Keep On Lovin’ Me (The Whispers)")}
{video_card("Mexico", "Teaser", "gf-mexico", "gf-mexico", ratio="r-169", no="GF/04", caption="Ghetto Funk Collective — Mexico teaser")}
{video_card("James Brown", "Studio session", "gf-james-brown", "gf-james-brown", ratio="r-169", no="GF/05", caption="Ghetto Funk Collective — James Brown session")}
{photo_card("ghetto-funk-01", "On stage", "Photo: Salih Kilic", "Ghetto Funk Collective — photo: Salih Kilic")}
{photo_card("ghetto-funk-02", "On stage", "Photo: Salih Kilic", "Ghetto Funk Collective — photo: Salih Kilic")}
    </div>
  </div>
</section>

<!-- ───────── 04 · Styling ───────── -->
<section id="styling" class="wrap section">
  <div class="meta-row"><span>Feature 04</span><span>p. 30</span></div>
  <h2 class="h-feature">Styling</h2>
  <div class="highlight">
    <button class="card" data-youtube="NjRvXjSHze4" data-caption="Coast Contra — Don’t Worry (Official Music Video) · Styling">
      <div class="cardimg r-169"><img src="assets/yt/NjRvXjSHze4.jpg" alt="" loading="lazy"><span class="no">Music video</span><span class="play">▶</span><span class="award">★ Berlin Music Video Awards</span></div>
    </button>
    <div class="highlight-text">
      <span class="meta">Styling · Coast Contra</span>
      <span class="feat-h">Don’t Worry</span>
      <p class="deck">Styling for Coast Contra’s official music video “Don’t Worry”.</p>
      <button class="more-btn" data-youtube="NjRvXjSHze4" data-caption="Coast Contra — Don’t Worry (Official Music Video) · Styling">Watch →</button>
    </div>
  </div>
  <div class="wall wall-3">
{prints([(s, n, "Styling — Coast Contra, Don’t Worry") for s, n in STYLING_PHOTOS])}
  </div>
</section>

<!-- ───────── 05 · Akyna ───────── -->
<section class="wrap section">
  <a class="feat feat-accent feat-wide" id="akyna" href="https://akyna-project.com/" target="_blank" rel="noopener">
    <div class="feat-text">
      <span class="meta">Feature 05 · p. 36</span>
      <span class="feat-h">Akyna</span>
      <span class="feat-deck">Akyna is the brand I started together with Pasqual. From production to design, we do everything ourselves.</span>
      <span class="more">akyna-project.com ↗</span>
    </div>
    <div class="feat-img akyna-word"><span>AKYNA</span></div>
  </a>
</section>

<!-- ───────── Back cover · Work with me ───────── -->
<footer id="contact" class="back">
  <div class="wrap back-in">
    <div class="kicker rule-b-light"><span>Back cover</span><span>Bookings &amp; collabs</span></div>
    <a class="book" href="mailto:info@jinkojoshu.com">Work with me</a>
    <div class="back-foot">
      <div class="col-s">
        <a href="mailto:info@jinkojoshu.com">info@jinkojoshu.com</a>
        <a href="https://www.instagram.com/jinkojoshu/" target="_blank" rel="noopener">Instagram — @jinkojoshu ↗</a>
      </div>
      <span class="jp">ジンコ・ジョシュ</span>
      <div class="col-s right">
        <div class="barcode light" aria-hidden="true"></div>
        <span class="tiny">Nº01 · <span id="year">2026</span> · Amsterdam</span>
      </div>
    </div>
  </div>
</footer>

</div>

<dialog id="lightbox">
  <div class="lb-bar"><span class="lb-cap"></span><a class="lb-yt" target="_blank" rel="noopener" hidden>Open on YouTube ↗</a><button class="lb-close" aria-label="Close">Close ×</button></div>
  <div class="lb-body"></div>
</dialog>

<script src="main.js"></script>
</body>
</html>
'''

Path(__file__).resolve().parent.parent.joinpath("site", "index.html").write_text(page)
print("index.html written")
