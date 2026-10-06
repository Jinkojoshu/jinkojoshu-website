#!/usr/bin/env python3
"""Generates the site pages from the content below:
  index.html        the cover — an open magazine with the showreel + small magazines
  commercials.html  Nº01 Commercials & Lookbook  (a magazine you page through)
  dance.html        Nº02 Dance
  styling.html      Nº03 Styling
  photography.html  Nº04 On film
Edit the lists / page text and run:  python3 tools/build-page.py
"""
from html import escape as e
from pathlib import Path

# ── Commercials, in order. Each: title, sub, thumbnail (assets/thumbs), focus of the thumbnail crop,
#    and what plays: video (assets/video file), clip (hover preview) or vimeo (id).
COMMERCIALS = [
    dict(title="Nike", sub="Member Days · 2023", thumb="nike", video="nike-member-days", clip="clip-nike-member-days-4x5"),
    dict(title="Samsung", sub="Galaxy Z Flip6 · global campaign", thumb="samsung", focus="50% 40%", video="samsung"),
    dict(title="bol × JBL", sub="Sport Offsite · 2026", thumb="boljbl", video="bol-x-jbl"),
    dict(title="Lavish", sub="Commercial · 2025", thumb="lavish", focus="38% 50%", video="lavish", clip="clip-lavish"),
    dict(title="Philips", sub="Commercial · 2025", thumb="philips", focus="50% 100%", video="philips"),
    dict(title="Foot Athletes", sub="Commercial · 2025", thumb="taf", focus="45% 40%", video="taf-2025"),
    dict(title="Lucid Dreaming", sub="Trailer · 2023", thumb="lucid", focus="41% 50%", video="lucid-dreaming-trailer",
         award="Gouden Kalf competition"),
    dict(title="Nike", sub="Behind the scenes · male model", thumb="nikebts", focus="50% 30%", video="nike-bts"),
]
# The big feature page of the commercials (vertical film on Vimeo)
WEMBY = dict(title="Nike × Wemby", sub="Basketball · 2025", thumb="wemby", vimeo="1175554062")

# Last page of the commercials: the brands
BRANDS = [("Nike", "2023 · 2025"), ("Samsung", "2024"), ("bol", "2026"), ("JBL", "2026"), ("Philips", "2025"),
          ("Lavish", "2025"), ("Foot Athletes", "2025"), ("Lucid Dreaming", "2023 ★"), ("Madonna", "Film"),
          ("Eurovision", "2025")]

# ── Lookbook: a tight, editorial selection. (image slug, caption)
LB = {
    2: ("nike-member-days-look", "Nike — Member Days"),
    5: ("polaroid-03", "Polaroid"),
    8: ("bol-jbl-03", "bol × JBL — campaign"),
    9: ("adidas-lookbook", "Adidas — lookbook"),
    10: ("pasqual-shoot", "Shot with Pasqual"),
    11: ("editorial-01", "Editorial"),
    15: ("film-2025-02", "On film, 2025"),
    17: ("editorial-04", "Editorial"),
    21: ("lucid-dreaming-group", "Lucid Dreaming — the cast"),
}

ONFILM = {i: (f"onfilm-{i:02d}", "On film — shot by Jinko") for i in range(1, 14)}
POLAS = [f"pola-{i:02d}" for i in range(1, 35)]

TGS_PHOTOS = ["tgs-01", "tgs-02", "tgs-03"]
YADE_PHOTOS = ["yade-01", "yade-02", "yade-03", "yade-04"]

# ── The magazines: (page, issue no, name, masthead, cover photo, photo focus, caption)
ISSUES = [
    ("commercials.html", "Nº01", "Commercials & Lookbook", None, None, None, None),
    ("dance.html", "Nº02", "Dance", "Dance", "ghetto-funk-01", "45% 40%", "Madonna · The Greatest Show · Ghetto Funk"),
    ("styling.html", "Nº03", "Styling", "Styling", "styling-cover", "50% 55%", "Coast Contra · Groove · Akyna"),
    ("photography.html", "Nº04", "On film", "On film", "onfilm-01", "50% 85%", "My photography"),
]


# ───────────────────────── building blocks ─────────────────────────
def card(c, no="", ratio_cls="", fill=True):
    """A commercial / film card. Plays a local film, a Vimeo film or (hover) a short clip."""
    focus = f' style="object-position:{c["focus"]}"' if c.get("focus") else ""
    if c.get("clip"):
        media = f'<video data-src="assets/video/{c["clip"]}.mp4" poster="assets/thumbs/{c["thumb"]}.jpg" muted loop playsinline preload="none"{focus}></video>'
    else:
        media = f'<img src="assets/thumbs/{c["thumb"]}.jpg" alt="" loading="lazy"{focus}>'
    play = f'data-vimeo="{c["vimeo"]}" data-vertical="1"' if c.get("vimeo") else f'data-video="assets/video/{c["video"]}.mp4"'
    aw = f'<span class="award">★ {e(c["award"])}</span>' if c.get("award") else ""
    cap = e(c.get("caption") or f'{c["title"]} — {c["sub"]}')
    return (f'<button class="card{" fill" if fill else ""}" {play} data-caption="{cap}">'
            f'<div class="cardimg {ratio_cls}">{media}<span class="no">{e(no)}</span><span class="play">▶</span>{aw}</div>'
            f'<span class="c-brand">{e(c["title"])}</span><span class="c-sub">{e(c["sub"])}</span></button>')


def yt_card(yid, title, sub, no, caption, start=None, fill=True, stamp=None):
    st = f' data-start="{start}"' if start else ""
    ts = f'<span class="timestamp">▶ {stamp}</span>' if stamp else ""
    return (f'<button class="card{" fill" if fill else ""}" data-youtube="{yid}"{st} data-caption="{e(caption)}">'
            f'<div class="cardimg{"" if fill else " r-169"}"><img src="assets/yt/{yid}.jpg" alt="" loading="lazy"><span class="no">{e(no)}</span><span class="play">▶</span>{ts}</div>'
            f'<span class="c-brand">{e(title)}</span><span class="c-sub">{e(sub)}</span></button>')


def photo_card(slug, title, sub, caption):
    return (f'<button class="card fill" data-full="assets/img/{slug}.jpg" data-caption="{e(caption)}">'
            f'<div class="cardimg"><img src="assets/img/{slug}-sm.jpg" alt="{e(caption)}" loading="lazy"></div>'
            f'<span class="c-brand">{e(title)}</span><span class="c-sub">{e(sub)}</span></button>')


def tile(slug, caption):
    return f'<button class="tile" data-full="assets/img/{slug}.jpg" data-caption="{e(caption)}"><img src="assets/img/{slug}-sm.jpg" alt="{e(caption)}" loading="lazy"></button>'


def grid(items, cols, rows=None, tpl=None):
    rows = rows or -(-len(items) // cols)
    style = f"--cols:{cols};--rows:{rows}" + (f";grid-template-rows:{tpl}" if tpl else "")
    return f'<div class="pg-grid" style="{style}">{"".join(items)}</div>'


def giant(rows, label, tag="h2", cls=""):
    """Huge stacked letters at the bottom of a page; main.js sizes them to fill the band exactly."""
    spans = "".join(f"<span>{e(r)}</span>" for r in rows)
    return f'<div class="band"><{tag} class="giant {cls}" aria-label="{e(label)}">{spans}</{tag}></div>'


def top(left, right=""):
    return f'<div class="pg-top"><span>{left}</span><span>{right}</span></div>'


class Page:
    def __init__(self, html, section=None, cls="", band=None):
        self.html, self.section, self.cls, self.band = html, section, cls, band


# photo layouts (lookbook + photography): clean, editorial — no pins
def photo(no, slug, cap, cls=""):
    return (f'<figure class="ph {cls}"><button class="ph-img" data-full="assets/img/{slug}.jpg" data-caption="{e(f"Nº{no:02d} — {cap}")}">'
            f'<img src="assets/img/{slug}-sm.jpg" srcset="assets/img/{slug}-sm.jpg 900w, assets/img/{slug}.jpg 2200w" sizes="(max-width: 760px) 100vw, 45vw" alt="{e(cap)}" loading="lazy"></button>'
            f'<figcaption><i>Nº{no:02d}</i> {e(cap)}</figcaption></figure>')


def bleed_page(section, no, item):
    return Page(photo(no, *item, "ph-bleed"), section, "photo-page")


def framed_page(section, label, no, item):
    return Page(f'<div class="pg">{top(label, f"Nº{no:02d}")}{photo(no, *item, "ph-framed")}</div>', section)


def pair_page(section, label, a, b, stack=False):
    (na, ia), (nb, ib) = a, b
    return Page(f'<div class="pg">{top(label, f"Nº{na:02d} — {nb:02d}")}'
                f'<div class="ph-pair{" ph-stack" if stack else ""}">{photo(na, *ia)}{photo(nb, *ib)}</div></div>', section)


def opener_page(section, kicker, title, deck, no, item):
    return Page(f'<div class="pg">{top(kicker, section[1])}<h2 class="pg-title">{title}</h2>'
                f'<p class="pg-deck">{deck}</p>{photo(no, *item, "ph-framed")}</div>', section)


def title_page(section, kicker, rows, deck, band="44%", body=""):
    return Page(f'<div class="pg">{top(kicker, section[1])}<p class="pg-deck">{deck}</p>{body}</div>'
                + giant(rows, section[1]), section, "", band)


def feature_page(section, kicker, right, heading, deck, media, after=""):
    return Page(f'<div class="pg">{top(kicker, right)}<h3 class="pg-h">{heading}</h3><p class="pg-deck">{deck}</p>{media}{after}</div>', section)


def contact_page():
    return Page(f'''<div class="pg">{top("Back cover", "Bookings &amp; collabs")}
  <div class="contact-links">
    <a href="mailto:info@jinkojoshu.com">info@jinkojoshu.com</a>
    <a href="https://www.instagram.com/jinkojoshu/" target="_blank" rel="noopener">Instagram — @jinkojoshu ↗</a>
    <span class="jp">ジンコ・ジョシュ</span>
  </div>
</div>''' + giant(["Work", "with me"], "Work with me"), None, "dark", "52%")


# ───────────────────────── page shell ─────────────────────────
FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,800..900"
         "&family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400..700"
         "&family=Inter+Tight:wght@400;500;600&family=Noto+Sans+JP:wght@500&display=swap")


def head(title, desc, body_class=""):
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:image" content="assets/img/jinko-portrait.jpg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{FONTS}" rel="stylesheet">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="styles.css">
</head>
<body class="{body_class}">
'''


LIGHTBOX = '''
<dialog id="lightbox">
  <div class="lb-bar"><span class="lb-cap"></span><a class="lb-yt" target="_blank" rel="noopener" hidden>Open on YouTube ↗</a><button class="lb-close" aria-label="Close">Close ×</button></div>
  <div class="lb-body"></div>
</dialog>

<script src="main.js"></script>
</body>
</html>
'''


def topbar(active):
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{h}"{cur if h == active else ""}>{no} {e(name)}</a>' for h, no, name, *_ in ISSUES)
    return f'''<header class="topbar">
  <a class="tb-home" href="index.html">← Cover</a>
  <a class="tb-name" href="index.html">Jinko Joshu</a>
  <nav class="tb-nav" aria-label="Issues">{nav}</nav>
  <a class="tb-mail" href="mailto:info@jinkojoshu.com">Work with me</a>
</header>
'''


def magazine(filename, title, desc, pages, next_href, next_label):
    """Pairs pages into spreads; the reader shows one spread at a time (stacked on phones)."""
    if len(pages) % 2:
        pages.append(contact_page())
    seen, chips, spreads = set(), [], []
    for i in range(0, len(pages), 2):
        sides = []
        for side, p, n in (("page-l", pages[i], i + 1), ("page-r", pages[i + 1], i + 2)):
            anchor = ""
            if p.section and p.section[0] not in seen:
                seen.add(p.section[0])
                anchor = f' id="{p.section[0]}"'
                chips.append(f'<a href="#{p.section[0]}" data-chip="{p.section[0]}">{e(p.section[1])}</a>')
            style = f' style="--band:{p.band}"' if p.band else ""
            sides.append(f'<div class="page {side} {p.cls}"{anchor}{style}>{p.html}<span class="pno">{n:02d}</span></div>')
        section = (pages[i].section or pages[i + 1].section or ("",))[0]
        spreads.append(f'<article class="mag spread" id="s{i // 2 + 1}" data-section="{section}">\n{sides[0]}\n{sides[1]}\n</article>')

    return head(title, desc, "inside") + topbar(filename) + f'''
<main class="reader" data-next="{next_href}" data-next-label="{e(next_label)}">
  <div class="stage">
    <button class="turn turn-prev"><span class="arrow" aria-hidden="true">←</span><span class="tl">Cover</span></button>
    <div class="spreads">
{chr(10).join(spreads)}
    </div>
    <button class="turn turn-next"><span class="arrow" aria-hidden="true">→</span><span class="tl">Next</span></button>
  </div>
  <div class="reader-foot">
    <nav class="chips" aria-label="In this issue">{"".join(chips)}</nav>
    <span class="count" aria-live="polite"></span>
  </div>
</main>
''' + LIGHTBOX


# ───────────────────────── Nº01 Commercials & Lookbook ─────────────────────────
C = ("commercials", "Commercials")
L = ("lookbook", "Lookbook")

cards = [card(c, no=f"{i:02d}") for i, c in enumerate(COMMERCIALS, 1)]
brands = "".join(f'<div class="brand"><b>{e(b)}</b><span>{e(y)}</span></div>' for b, y in BRANDS)

issue1 = [
    Page(f'<div class="pg">{top("Issue Nº01 · Commercials", "01 — 04")}<h2 class="pg-title">Commercials</h2>{grid(cards[:4], 2, 2)}</div>', C),
    Page(f'<div class="pg">{top("Commercials", "05 — 08")}{grid(cards[4:], 2, 2)}</div>', C),
    Page(f'<div class="pg">{top("Nike Basketball", "Main cast")}<h3 class="pg-h">Nike × Wemby</h3>'
         f'<p class="pg-deck">Booked by <i>I Could Never Be A Dancer</i> as part of the main cast for Nike Basketball — '
         f'together we created a dance-basketball film for Victor Wembanyama.</p>'
         f'<div class="feature-v">{card(WEMBY, no="09")}</div></div>', C),
    Page(f'''<div class="pg">{top("Selected work", "2023 — 2026")}<h3 class="pg-h">Worked with</h3>
  <div class="brands">{brands}</div>
  <span class="pg-note">★ Lucid Dreaming — Gouden Kalf competition · Coast Contra — Berlin Music Video Awards</span></div>''', C),
    opener_page(L, "Issue Nº01 · Lookbook", "Lookbook", "In front of the lens — campaigns, editorials and film.", 2, LB[2]),
    bleed_page(L, 5, LB[5]),
    bleed_page(L, 9, LB[9]),
    framed_page(L, "Lookbook", 8, LB[8]),
    framed_page(L, "Lookbook", 10, LB[10]),
    bleed_page(L, 11, LB[11]),
    bleed_page(L, 15, LB[15]),
    framed_page(L, "Lookbook", 17, LB[17]),
    framed_page(L, "Lookbook", 21, LB[21]),
]

# ───────────────────────── Nº02 Dance ─────────────────────────
MV = ("musicvideos", "Music videos")
Y = ("yade", "Yade Lauren")
M = ("moredance", "More dance")
G = ("ghettofunk", "Ghetto Funk")

TOURS = [("Breakin’ Convention", "UK"), ("Canada", "Tour"), ("Despertares", "Mexico City · 2×"), ("The Greatest Show", "China")]
tours = "".join(f'<div class="brand"><b>{e(t)}</b><span>{e(w)}</span></div>' for t, w in TOURS)

issue2 = [
    Page(f'<div class="pg">{top("Issue Nº02 · Dance", "Music videos")}<h2 class="pg-title">Music videos</h2>'
         + grid([yt_card("yJtckcMHM2g", "Madonna — Confessions II", "The Film · my part starts at 06:55", "Madonna",
                         "Madonna — Confessions II, The Film · Jinko from 06:55", start=415, stamp="06:55"),
                 yt_card("hEHwr5k9pd0", "Claude — C’est La Vie", "Official music video · Eurovision 2025", "Eurovision",
                         "Claude — C’est La Vie · Official Music Video · Eurovision 2025")], 1, 2) + '</div>', MV),
    Page(f'<div class="pg">{top("The collective", "<b class=badge>Member</b>")}<h3 class="pg-h">Ghetto Funk Collective</h3>'
         f'<p class="pg-deck">Ghetto Funk is a dance collective that feels like family to me, founded by Ruben Chi and Roche Apinsa. '
         f'I got the honour to become part of it — and to tour with them.</p>'
         f'<div class="brands tours">{tours}</div>'
         + grid([tile("ghetto-funk-01", "Ghetto Funk Collective — photo: Salih Kilic")], 1, 1) + '</div>', G),
    Page(f'<div class="pg">{top("Ghetto Funk Collective", "GF/01 — 03")}'
         + grid([yt_card("0otuG_RO1mI", "“Just Feel”", "10 year anniversary", "GF/01", "“Just Feel” — 10 year anniversary, Ghetto Funk Collective"),
                 yt_card("oVR1SJvekRw", "Damn Right", "We Are Somebody", "GF/02", "Ghetto Funk Collective — Damn Right We Are Somebody"),
                 yt_card("CV84FmeBRbU", "Keep On Lovin’ Me", "The Whispers", "GF/03", "Ghetto Funk Collective — Keep On Lovin’ Me (The Whispers)")], 1, 3) + '</div>', G),
    feature_page(G, "Ghetto Funk on tour · Nanjing, China", "Choreographer · Dancer", "The Greatest Show",
                 "We were invited to Nanjing to create a two-hour show — and to dance in it ourselves, alongside 170 guest dancers from China. A challenge both as choreographer and as dancer.",
                 grid([tile(TGS_PHOTOS[0], "The Greatest Show — Nanjing, China").replace('class="tile"', 'class="tile span-all"')]
                      + [tile(s, "The Greatest Show — Nanjing, China") for s in TGS_PHOTOS[1:]], 2, tpl="3fr 2fr")),
    Page(f'<div class="pg">{top("Ghetto Funk Collective", "GF/04 — 06")}'
         + grid([card(dict(title="Mexico", sub="Teaser", thumb="gf-mexico", video="gf-mexico", caption="Ghetto Funk Collective — Mexico teaser"), no="GF/04"),
                 card(dict(title="James Brown", sub="Studio session", thumb="gf-james-brown", video="gf-james-brown", caption="Ghetto Funk Collective — James Brown session"), no="GF/05"),
                 photo_card("ghetto-funk-02", "On stage", "Photo: Salih Kilic", "Ghetto Funk Collective — photo: Salih Kilic").replace('class="card fill"', 'class="card fill span-all"')],
                2, tpl="1fr 1fr") + '</div>', G),
    feature_page(Y, "Project · Festival show", "Performer", "Yade Lauren",
                 "Yade Lauren asked me to join her show as a performer. We played a festival together and brought more of a fashion vibe to her set.",
                 grid([tile(s, "Yade Lauren — festival show") for s in YADE_PHOTOS], 2, 2)),
    Page(f'<div class="pg">{top("More dance", "Films · stage · sessions")}<h3 class="pg-h">More dance</h3>'
         + grid([card(dict(title="On the bridge", sub="Dance film", thumb="dance-performance", video="dance-performance"), no="Film"),
                 card(dict(title="JMD", sub="Stage", thumb="dance-jmd", video="dance-jmd"), no="Stage"),
                 card(dict(title="Dam Square", sub="Street session · Amsterdam", thumb="dance-footage", video="dance-footage"), no="Session"),
                 card(dict(title="Hashna", sub="Collab", thumb="dance-hashna", video="dance-hashna"), no="Collab")], 2, 2) + '</div>', M),
]

# ───────────────────────── Nº03 Styling ─────────────────────────
S = ("styling", "Styling")
A = ("akyna", "Akyna")
GR = ("groove", "Groove")
GROOVE = dict(title="Groove", sub="Theatre show · on stage", thumb="groove", focus="50% 25%", video="groove",
              caption="Groove — The Ruggeds × Ghetto Funk Collective")
COAST = 'data-youtube="NjRvXjSHze4" data-caption="Coast Contra — Don’t Worry (Official Music Video) · Styling"'
CC = "Styling — Coast Contra, Don’t Worry"

issue3 = [
    title_page(S, "Issue Nº03", ["Styling"], "Styling for music videos and shoots — and Akyna, the label I run with Pasqual.", band="40%"),
    feature_page(S, "Styling · Coast Contra", "Music video", "Don’t Worry",
                 "Styling for Coast Contra’s official music video “Don’t Worry”.",
                 f'<button class="card" {COAST}><div class="cardimg r-169"><img src="assets/yt/NjRvXjSHze4.jpg" alt="" loading="lazy"><span class="no">Music video</span><span class="play">▶</span><span class="award">★ Berlin Music Video Awards</span></div></button>',
                 f'<button class="more-btn" {COAST}>Watch →</button>'),
    Page(f'<div class="pg">{top("Coast Contra — Don’t Worry", "On set")}'
         f'<div class="ph-pair ph-stack">{photo(1, "coast-contra-01", CC)}{photo(2, "coast-contra-03", CC)}</div></div>', S),
    Page(f'<div class="pg">{top("Theatre show · The Ruggeds × Ghetto Funk Collective", "Styling")}<h3 class="pg-h">Groove</h3>'
         '<p class="pg-deck pg-deck-s">The Ruggeds and Ghetto Funk Collective take the swinging dance concert <i>Groove</i> through the theatres. '
         'Travel fifty years back in time and experience the music of James Brown, Aretha Franklin and Marvin Gaye. Dancing musicians and '
         'musical dancers guide you through funk &amp; soul, hip-hop, house and everything in between. Put on your best outfit — '
         'sitting still is not an option.</p>'
         + grid([card(GROOVE, no="Show").replace('class="card fill"', 'class="card fill span-rows"'),
                 tile("groove-01", "Groove — The Ruggeds × Ghetto Funk Collective"),
                 tile("groove-02", "Groove — on stage")], 2, 2) + '</div>', GR),
    Page(f'''<div class="pg">{top("Feature 03.1", "The label")}
  <p class="pg-deck">Akyna is the brand I started together with Pasqual. From production to design, we do everything ourselves.</p>
  <a class="more-btn" href="https://akyna-project.com/" target="_blank" rel="noopener">akyna-project.com ↗</a>
  {grid([tile("akyna-02", "Akyna — AW26"), tile("akyna-03", "Akyna — AW26")], 2, 1)}
</div>''' + giant(["Akyna"], "Akyna", cls="wide"), A, "accent", "34%"),
    bleed_page(A, 1, ("akyna-01", "Akyna — AW26")),
]

# ───────────────────────── Nº04 On film ─────────────────────────
F = ("onfilm", "On film")
PL = ("polaroids", "Polaroids")
LANDSCAPE = {7, 9, 12}   # these sit framed on the page; the rest alternate full-bleed / framed
polas = "".join(f'<button class="pola" data-full="assets/img/{p}.jpg" data-caption="Polaroid — shot by Jinko">'
                f'<img src="assets/img/{p}-sm.jpg" alt="Polaroid shot by Jinko" loading="lazy"></button>' for p in POLAS)

issue4 = [opener_page(F, "Issue Nº04 · Photography", "On film", "My own photography — shot on film.", 1, ONFILM[1])]
for i in range(2, 14):
    framed = i in LANDSCAPE or i in {3, 6, 13}
    issue4.append(framed_page(F, "On film", i, ONFILM[i]) if framed else bleed_page(F, i, ONFILM[i]))
issue4.append(Page(f'<div class="pg">{top("On film", "Instant film")}<h3 class="pg-h">Polaroids</h3>'
                   f'<div class="pola-grid">{polas}</div></div>', PL))


# ───────────────────────── Cover (index.html) ─────────────────────────
def mini(href, no, name, mast, img, focus, cap):
    return f'''    <a class="mini" href="{href}">
      <div class="mini-cover">
        <span class="mini-mast"><span class="fit">{e(mast)}</span></span>
        <img src="assets/img/{img}-sm.jpg" alt="" style="object-position: {focus}">
        <span class="mini-no">{e(no)}</span>
      </div>
      <span class="mini-cap"><b>{e(name)}</b>{e(cap)}</span>
    </a>'''


index = head("Jinko Joshu — Magazine Nº01",
             "Jinko Joshu — Amsterdam-based performer. Commercials, dance, styling, photography and the label Akyna.", "home") + f'''
<main class="desk">
  <article class="mag cover-mag" aria-label="Issue Nº01 — showreel">
    <div class="page page-l" style="--band:50%">
      <span class="folio">Jinko Joshu — Issue Nº01</span>
      <span class="credit">Showreel · Autumn 2026</span>
      <img class="silhouette" src="assets/mag/halftone-portrait.png" alt="">
      {giant(["Jinko", "Joshu"], "Jinko Joshu", tag="h1")}
    </div>
    <div class="page page-r" style="--band:50%">
      <span class="folio folio-r">Amsterdam · @jinkojoshu</span>
      <a class="open-issue" href="commercials.html"><span>Open the issue</span><b>Commercials &amp; Lookbook →</b></a>
      <div class="reel-wrap">
        <video id="reel" muted playsinline autoplay poster="assets/poster/reel.jpg" aria-label="Showreel: short moments from Jinko Joshu's work"></video>
        <audio id="reel-audio" src="assets/audio/showreel.m4a" loop preload="none"></audio>
        <button class="sound" aria-pressed="false"><span class="sound-ico" aria-hidden="true"></span><span class="sound-txt">Sound on</span></button>
      </div>
    </div>
  </article>

  <nav class="shelf" aria-label="More issues">
{chr(10).join(mini(*m) for m in ISSUES[1:])}
  </nav>

  <footer class="desk-foot">
    <a href="mailto:info@jinkojoshu.com">Work with me — info@jinkojoshu.com</a>
    <a href="https://www.instagram.com/jinkojoshu/" target="_blank" rel="noopener">Instagram ↗</a>
    <a href="https://akyna-project.com/" target="_blank" rel="noopener">Akyna ↗</a>
  </footer>
</main>
''' + LIGHTBOX

site = Path(__file__).resolve().parent.parent / "site"
out = {
    "index": index,
    "commercials": magazine("commercials.html", "Commercials & Lookbook — Jinko Joshu",
                            "Commercials, campaigns and the lookbook of Jinko Joshu.", issue1, "dance.html", "Nº02 Dance"),
    "dance": magazine("dance.html", "Dance — Jinko Joshu",
                      "Jinko Joshu as dancer and choreographer: Madonna, Claude, The Greatest Show, Yade Lauren and Ghetto Funk Collective.",
                      issue2, "styling.html", "Nº03 Styling"),
    "styling": magazine("styling.html", "Styling — Jinko Joshu",
                        "Styling by Jinko Joshu: Coast Contra — Don’t Worry, and the label Akyna.", issue3, "photography.html", "Nº04 On film"),
    "photography": magazine("photography.html", "On film — Jinko Joshu",
                            "Photography by Jinko Joshu, shot on film.", issue4, "index.html", "Cover"),
}
for name, html in out.items():
    (site / f"{name}.html").write_text(html)
print(", ".join(f"{n}.html" for n in out), "written")
