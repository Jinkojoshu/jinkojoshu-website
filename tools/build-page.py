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
    dict(logos=["nike"], title="Nike", sub="Member Days · 2023", thumb="nike", video="nike-member-days-dc-alt", clip="clip-nike-member-days-4x5",
         note="Production: Youthclub · Edit & direction: Camille Boumans · Movement direction: Lars Bothe, assisted by Leonarda Lovrkovic · Styling: Lissa Brandon · MUA: Kato Fierkens"),
    dict(logos=["samsung"], title="Samsung", sub="Galaxy Z Flip6 · global campaign", thumb="samsung", focus="50% 40%", video="samsung"),
    dict(logos=["bol", "jbl"], title="bol × JBL", sub="Sport Offsite · 2026", thumb="boljbl", video="bol-x-jbl"),
    dict(logos=["lavish"], title="Lavish", sub="Commercial · 2025", thumb="lavish", focus="38% 50%", video="lavish", clip="clip-lavish"),
    dict(logos=["philips"], title="Philips", sub="Commercial · 2025", thumb="philips", focus="50% 100%", video="philips"),
    dict(logos=["footathletes"], title="Foot Athletes", sub="Commercial · 2025", thumb="taf", focus="45% 40%", video="taf-2025"),
    dict(title="Lucid Dreaming", sub="Trailer · 2023", thumb="lucid", focus="41% 50%", video="lucid-dreaming-trailer",
         award="Gouden Kalf competition"),
    dict(logos=["nike"], title="Nike", sub="Behind the scenes · male model", thumb="nikebts", focus="50% 30%", video="nike-bts"),
]
# The big feature page of the commercials (vertical film on Vimeo)
WEMBY = dict(logos=["nike"], title="Nike × Wemby", sub="Basketball · 2025", thumb="wemby", vimeo="1175554062",
             note="Booked by I Could Never Be A Dancer as part of the main cast for Nike Basketball — together we created a dance-basketball film for Victor Wembanyama.")

# Last page of the commercials: the brands
BRANDS = [("Nike", ["nike"], "2023 · 2025"), ("Samsung", ["samsung"], "2024"), ("bol × JBL", ["bol", "jbl"], "2026"),
          ("Philips", ["philips"], "2025"), ("Lavish", ["lavish"], "2025"), ("The Athlete’s Foot", ["footathletes"], "2025"),
          ("Lucid Dreaming", [], "2023 · Award"), ("Madonna", [], "Film"), ("Eurovision", [], "2025")]

# ── Lookbook: a tight, editorial selection. (image slug, caption)
LB = {
    2: ("nike-member-days-look", "Nike — Member Days"),
    5: ("polaroid-03", "APL polaroid, photo by Kaj Lehner"),
    8: ("bol-jbl-03", "bol × JBL — campaign"),
    9: ("adidas-lookbook", "Adidas — lookbook"),
    10: ("pasqual-shoot", "Shoot with Pasqual Dominic"),
    11: ("editorial-01", "Editorial"),
    15: ("film-2025-02", "On film, 2025"),
    21: ("lucid-dreaming-group", "Lucid Dreaming — the cast"),
    22: ("lookbook-new-01", "Lucid Dreaming — on set"),
    23: ("lookbook-new-02", "Shay program, photo by Pasqual Dominic"),
    24: ("lookbook-new-03", "Editorial, shot by Megan Jane"),
    25: ("lookbook-new-04", "Editorial, shot by Megan Jane"),
    26: ("lookbook-new-05", "Portrait by Brandon Broodje"),
    27: ("lookbook-new-06", "Portrait for Levi’s"),
    28: ("lookbook-new-07", "In motion, shot by Veerle Haan"),
}
# Photographers whose name in a caption links to their site
CREDIT_LINKS = {"Pasqual Dominic": "https://www.pasqualdominic.com/"}

ONFILM = {i: (f"onfilm-{i:02d}", "On film, shot by Jinko") for i in range(1, 17)}
POLAS = [f"pola-{i:02d}" for i in range(1, 35) if i != 6]   # 6 is a near-copy of 5
HAIR = "".join(f'<button class="pola" data-full="assets/img/hair-{i:02d}.jpg" data-caption="Hair look">'
               f'<img src="assets/img/hair-{i:02d}-sm.jpg" alt="Hair look worn by Jinko Joshu" loading="lazy"></button>' for i in range(1, 13))

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
    aw = f'<span class="award">{e(c["award"])}</span>' if c.get("award") else ""
    cap = e(c.get("caption") or f'{c["title"]} — {c["sub"]}')
    return (f'<button class="card{" fill" if fill else ""}" {play} data-caption="{cap}">'
            f'<div class="cardimg {ratio_cls}">{media}<span class="no">{e(no)}</span><span class="play" aria-hidden="true"></span>{aw}</div>'
            f'<span class="c-brand">{e(c["title"])}</span><span class="c-sub">{e(c["sub"])}</span></button>')


def yt_card(yid, title, sub, no, caption, start=None, fill=True, stamp=None):
    st = f' data-start="{start}"' if start else ""
    ts = f'<span class="timestamp">From {stamp}</span>' if stamp else ""
    return (f'<button class="card{" fill" if fill else ""}" data-youtube="{yid}"{st} data-caption="{e(caption)}">'
            f'<div class="cardimg{"" if fill else " r-169"}"><img src="assets/yt/{yid}.jpg" alt="" loading="lazy"><span class="no">{e(no)}</span><span class="play" aria-hidden="true"></span>{ts}</div>'
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
    def __init__(self, html, section=None, cls="", band=None, art="", anchor=""):
        self.html, self.section, self.cls, self.band, self.art, self.anchor = html, section, cls, band, art, anchor


# photo layouts (lookbook + photography): clean, editorial — no pins
def photo(no, slug, cap, cls=""):
    return (f'<figure class="ph {cls}"><button class="ph-img" data-full="assets/img/{slug}.jpg" data-caption="{e(f"Nº{no:02d} — {cap}")}">'
            f'<img src="assets/img/{slug}-sm.jpg" srcset="assets/img/{slug}-sm.jpg 900w, assets/img/{slug}.jpg 2200w" sizes="(max-width: 760px) 100vw, 45vw" alt="{e(cap)}" loading="lazy"></button>'
            f'<figcaption><i>Nº{no:02d}</i> {credit_links(e(cap))}</figcaption></figure>')


def credit_links(cap):
    for name, url in CREDIT_LINKS.items():
        cap = cap.replace(name, f'<a href="{url}" target="_blank" rel="noopener">{name}</a>')
    return cap


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


def with_anchor(anchor, page):
    page.anchor = anchor
    return page


def feature_page(section, kicker, right, heading, deck, media, after=""):
    return Page(f'<div class="pg">{top(kicker, right)}<h3 class="pg-h">{heading}</h3><p class="pg-deck">{deck}</p>{media}{after}</div>', section)


REPRESENTED = '<a href="https://www.aplmodels.com/men" target="_blank" rel="noopener">APL</a> · The Movers'


def contact_page():
    return Page(f'''<div class="pg">{top("Back cover", "Bookings &amp; collabs")}
  <div class="contact-links">
    <a href="mailto:info@jinkojoshu.com">info@jinkojoshu.com</a>
    <a href="https://www.instagram.com/jinkojoshu/" target="_blank" rel="noopener">Instagram — @jinkojoshu</a>
    <span class="rep">Represented by {REPRESENTED}</span>
    <span class="jp">ジンコ・ジョシュ</span>
  </div>
</div>''' + giant(["Work", "with me"], "Work with me").replace('<div class="band">', '<a class="band band-link" href="mailto:info@jinkojoshu.com">', 1).replace("</h2></div>", "</h2></a>"), None, "dark", "52%")


# ───────────────────────── page shell ─────────────────────────
FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,800..900"
         "&family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400..700"
         "&family=Inter+Tight:ital,wght@0,400..700;1,400..600&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+JP:wght@500&display=swap")


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
  <div class="lb-bar"><span class="lb-cap"></span><a class="lb-yt" target="_blank" rel="noopener" hidden>Open on YouTube</a><button class="lb-close" aria-label="Close">Close ×</button></div>
  <div class="lb-body"></div>
  <p class="lb-note" hidden></p>
  <button class="lb-step lb-prev" aria-label="Previous film" hidden><span class="arrow-mark" aria-hidden="true"></span></button>
  <button class="lb-step lb-next" aria-label="Next film" hidden><span class="arrow-mark" aria-hidden="true"></span></button>
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


def magazine(filename, title, desc, pages, next_href, next_label, scripts="", hub=False):
    """Pairs pages into spreads; the reader shows one spread at a time (stacked on phones)."""
    if len(pages) % 2:
        pages.append(contact_page())
    seen, chips, spreads = set(), [], []
    for i in range(0, len(pages), 2):
        sides = []
        for side, p, n in (("page-l", pages[i], i + 1), ("page-r", pages[i + 1], i + 2)):
            anchor = f' id="{p.anchor}"' if p.anchor else ""
            if p.section and p.section[0] not in seen:
                seen.add(p.section[0])
                anchor = f' id="{p.section[0]}"'
                chips.append(f'<a href="#{p.section[0]}" data-chip="{p.section[0]}">{e(p.section[1])}</a>')
            style = f' style="--band:{p.band}"' if p.band else ""
            sides.append(f'<div class="page {side} {p.cls}"{anchor}{style}>{p.html}<span class="pno">{n:02d}</span></div>')
        section = (pages[i].section or pages[i + 1].section or ("",))[0]
        art = pages[i].art
        spreads.append(f'<article class="mag spread{" has-art" if art else ""}" id="s{i // 2 + 1}" data-section="{section}">\n{sides[0]}\n{sides[1]}\n{art}</article>')

    return head(title, desc, "inside") + topbar(filename) + f'''
<main class="reader{" hub" if hub else ""}" data-next="{next_href}" data-next-label="{e(next_label)}">
  <div class="stage">
    <button class="turn turn-prev"><span class="arrow" aria-hidden="true">←</span><span class="tl">Cover</span></button>
    <div class="spreads">
{chr(10).join(spreads)}
    </div>
    <button class="turn turn-next"><span class="arrow" aria-hidden="true">→</span><span class="tl">Next</span></button>
  </div>
  <div class="reader-foot">
    <nav class="chips" aria-label="In this issue">{"" if hub else "".join(chips)}</nav>
    <span class="count" aria-live="polite"></span>
  </div>
</main>
''' + scripts + LIGHTBOX


# ───────────────────────── Nº01 Commercials & Lookbook ─────────────────────────
C = ("commercials", "Commercials")
L = ("lookbook", "Lookbook")


def logo_img(name, cls):
    return f'<img class="{cls}" src="assets/logos/{name}.png" alt="{e(name)}">'


def strip_cell(c, no):
    """One frame in the commercials strip: still at rest, plays on hover (brand logo slides in), full film on click."""
    focus = f' style="object-position:{c["focus"]}"' if c.get("focus") else ""
    play = f'data-vimeo="{c["vimeo"]}" data-vertical="1"' if c.get("vimeo") else f'data-video="assets/video/{c["video"]}.mp4"'
    note = f' data-note="{e(c["note"])}"' if c.get("note") else ""
    preview = c.get("clip") or c.get("video")
    vid = (f'<video data-preview="assets/video/{preview}.mp4" muted loop playsinline preload="none"{focus}></video>'
           if preview else "")
    logos = "".join(logo_img(n, "strip-logo-img") for n in c.get("logos", []))
    brand = f'<span class="strip-logo">{logos or e(c["title"])}</span>'
    cap = e(c.get("caption") or f'{c["title"]} — {c["sub"]}')
    return (f'<button class="strip-cell" {play}{note} data-caption="{cap}">'
            f'<img src="assets/thumbs/{c["thumb"]}.jpg" alt="" loading="lazy"{focus}>{vid}{brand}'
            f'<span class="strip-cap"><b>{no}</b> {e(c["title"])} · {e(c["sub"])}</span></button>')


ORDER = [COMMERCIALS[0], WEMBY, COMMERCIALS[1], COMMERCIALS[2], COMMERCIALS[3],   # on the opener
         COMMERCIALS[4], COMMERCIALS[5], COMMERCIALS[6], COMMERCIALS[7]]            # on the next page
cells = [strip_cell(c, f"{i:02d}") for i, c in enumerate(ORDER, 1)]
strip = "".join(cells)
COMM_ART = f'''<div class="spread-art comm-art">
  <div class="art-top"><span>Issue Nº01</span><span>Commercials &amp; Lookbook</span></div>
  <h2 class="art-head">Commercials</h2>
  <img class="art-figure" src="assets/mag/commercials-cutout-2.png" alt="Jinko Joshu, mid-movement">
  <div class="strip-wrap">
    <div class="strip" data-group="commercials" aria-label="Commercials: hover to preview, click to watch">{strip}</div>
    <button class="strip-more" aria-label="More commercials"><span class="arrow-mark" aria-hidden="true"></span></button>
  </div>
  <span class="art-foot">Jinko Joshu, performer</span><span class="art-foot r">Hover to play · click for the full film</span>
</div>'''
brands = "".join(f'<div class="brand">{"".join(logo_img(n, "brand-logo") for n in lg) if lg else f"<b>{e(b)}</b>"}<span>{e(y)}</span></div>'
                 for b, lg, y in BRANDS)

issue1 = [
    Page("", C, "art-page", art=COMM_ART),
    Page("", C, "art-page"),
    Page(f'''<div class="pg">{top("Selected work", "2023 — 2026")}<h3 class="pg-h">Worked with</h3>
  <div class="brands brands-logos">{brands}</div>
  <span class="pg-note">Awards — Lucid Dreaming — Gouden Kalf competition · Coast Contra — Berlin Music Video Awards</span></div>''', C),
    opener_page(L, "Issue Nº01 · Lookbook", "Lookbook", "In front of the lens — campaigns, editorials and film.", 2, LB[2]),
    framed_page(L, "Lookbook", 5, LB[5]),
    bleed_page(L, 9, LB[9]),
    framed_page(L, "Lookbook", 8, LB[8]),
    bleed_page(L, 23, LB[23]),
    framed_page(L, "Lookbook", 10, LB[10]),
    bleed_page(L, 11, LB[11]),
    framed_page(L, "Lookbook", 24, LB[24]),
    bleed_page(L, 25, LB[25]),
    framed_page(L, "Lookbook", 26, LB[26]),
    bleed_page(L, 15, LB[15]),
    framed_page(L, "Lookbook", 22, LB[22]),
    bleed_page(L, 27, LB[27]),
    framed_page(L, "Lookbook", 28, LB[28]),
    framed_page(L, "Lookbook", 21, LB[21]),
    Page(f'<div class="pola-sheet hair-sheet"><div class="pola-grid">{HAIR}</div>'
         '<div class="pola-foot"><span>Hair looks<br>Colour &amp; cuts</span><span>Worn by Jinko Joshu<br>2019 · 2026</span>'
         '<span class="pola-mark">Hair</span></div></div>', ("hair", "Hair looks"), "pola-page"),
]


# ───────────────────────── hub issues (Dance, Styling) ─────────────────────────
# The first spread is the index; every project has its own spread that you only reach from the index.
def back_link(hub_id, label):
    return f'<a class="back-hub" href="#{hub_id}">← {e(label)}</a>'


def watch_media(kind, ident, caption, thumb, start=None):
    """Right page of a project: the film as a full page still with a play button."""
    attr = {"yt": f'data-youtube="{ident}"', "video": f'data-video="assets/video/{ident}.mp4"'}[kind]
    st = f' data-start="{start}"' if start else ""
    live = (f'<video class="autoplay" data-src="assets/video/{ident}.mp4" muted loop playsinline preload="none" poster="{thumb}"></video>'
            if kind == "video" else "")
    return (f'<button class="watch" {attr}{st} data-caption="{e(caption)}"><img src="{thumb}" alt="" loading="lazy">{live}'
            f'<span class="watch-play"><i aria-hidden="true"></i> Watch</span></button>')


def project(pid, hub, place, kind_label, title, deck, facts, right, right_cls="photo-page", extra_left=""):
    rows = "".join(f'<div class="fact"><span>{e(k)}</span><b>{e(v)}</b></div>' for k, v in facts)
    left = Page(f'<div class="pg">{top(e(place), e(kind_label))}<h2 class="pg-title pg-title-s">{title}</h2>'
                f'<p class="pg-deck">{deck}</p><div class="facts">{rows}</div>{extra_left}'
                f'{back_link(hub[0], hub[1])}</div>', anchor=pid)
    return [left, Page(right, cls=right_cls)]


def credits(rows):
    return '<dl class="credits">' + "".join(f'<div{" class=cast" if k == "Cast" else ""}><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in rows) + '</dl>'


def yt_thumb(yid):
    return f"assets/yt/{yid}.jpg"


# ───────────────────────── Nº02 Dance ─────────────────────────
DH = ("world", "Back to the globe")
# Where the dance work happened (lat, lon): the globe that opens the issue
PLACES = [
    dict(city="Amsterdam · Netherlands", lat=52.37, lon=4.90, dy=5, items=[
        ("Claude · C’est La Vie", "Music video", "#claude"),
        ("Yade Lauren", "Festival show", "#yade"),
        ("JMD", "Stage", "#jmd"),
        ("Hashna", "Collab", "#hashna"),
        ("Dam Square", "Street session", "#damsquare"),
        ("Short movie", "Film", "#shortmovie"),
        ("A$AP Rocky", "Tour", "#asap"),
        ("Lucid Dreaming", "Film", "commercials.html")]),
    dict(city="Lowlands · Biddinghuizen", lat=52.45, lon=5.69, dy=-15, items=[("Oh My: The Holy GraiLL", "Dance film", "#holygraill")]),
    dict(city="London", lat=51.51, lon=-0.13, side="left", dy=-8, items=[
        ("Madonna · Confessions II", "Music video", "#madonna"),
        ("Breakin’ Convention", "Ghetto Funk", "#ghettofunk"),
        ("Collab with Jan", "Dance video", "#janlondon")]),
    dict(city="Guilin · China", lat=25.27, lon=110.29, side="left", items=[("On the bridge", "Dance film", "#bridge")]),
    dict(city="Shanghai · China", lat=31.23, lon=121.47, items=[("The Greatest Show", "Ghetto Funk", "#tgs")]),
    dict(city="Barcelona", lat=41.39, lon=2.17, dy=8, items=[("Samsung", "Commercial", "commercials.html")]),
    dict(city="Mexico City", lat=19.43, lon=-99.13, dy=6, items=[("Despertares · 2×", "Ghetto Funk", "#ghettofunk")]),
    dict(city="Canada", lat=43.65, lon=-79.38, dy=-6, items=[("On tour", "Ghetto Funk", "#ghettofunk")]),
]
import json
EXT = ' target="_blank" rel="noopener"'
places_list = "".join(
    f'<li class="place" data-i="{n}"><span class="place-city">{e(pl["city"])}</span>'
    + "".join(f'<a href="{h}"{EXT if h.startswith("http") else ""}><b>{e(t)}</b><span>{e(k)}</span></a>' for t, k, h in pl["items"]) + '</li>'
    for n, pl in enumerate(PLACES))
GLOBE_DATA = e(json.dumps([dict(city=pl["city"], lat=pl["lat"], lon=pl["lon"], side=pl.get("side", "right"), dy=pl.get("dy", 0), home=pl.get("home", False),
                                items=[dict(t=t, k=k, h=h) for t, k, h in pl["items"]]) for pl in PLACES]))

GF_VIDEOS = [
    yt_card("0otuG_RO1mI", "“Just Feel”", "10 year anniversary", "GF/01", "“Just Feel” · 10 year anniversary, Ghetto Funk Collective"),
    yt_card("oVR1SJvekRw", "Damn Right", "We Are Somebody", "GF/02", "Ghetto Funk Collective · Damn Right We Are Somebody"),
    yt_card("CV84FmeBRbU", "Keep On Lovin’ Me", "The Whispers", "GF/03", "Ghetto Funk Collective · Keep On Lovin’ Me (The Whispers)"),
    card(dict(title="Mexico", sub="Teaser · Despertares", thumb="gf-mexico", video="gf-mexico", caption="Ghetto Funk Collective · Mexico teaser"), no="GF/04"),
    card(dict(title="James Brown", sub="Studio session", thumb="gf-james-brown", video="gf-james-brown", caption="Ghetto Funk Collective · James Brown session"), no="GF/05"),
    '<a class="card fill card-link" href="#tgs"><div class="cardimg"><img src="assets/img/tgs-01-sm.jpg" alt="" loading="lazy">'
    '<span class="no">On tour</span></div><span class="c-brand">The Greatest Show →</span><span class="c-sub">China · our two-hour show</span></a>',
]
TOURS = [("Breakin’ Convention", "UK", None), ("Canada", "Tour", None), ("Despertares", "Mexico City · 2×", None),
         ("The Greatest Show", "China", "#tgs")]
tours = "".join((f'<a class="tour" href="{h}"{EXT if h.startswith("http") else ""}>' if h else '<div class="tour">') + f'<b>{e(t)}</b><span>{e(w)}</span>'
                + ('</a>' if h else '</div>') for t, w, h in TOURS)

issue2 = [
    Page(f'<div class="pg">{top("Issue Nº02 · Dance", "Around the world")}<h2 class="pg-title">Dance</h2>'
         f'<p class="pg-deck">Where the work took me. Turn the globe, click a city or pick a project.</p>'
         f'<ol class="places">{places_list}</ol></div>', ("world", "Dance"), anchor="world"),
    Page(f'<div class="globe-wrap"><canvas class="globe" data-places="{GLOBE_DATA}" aria-label="Globe with the places Jinko danced"></canvas>'
         f'<div class="globe-pop" hidden></div><span class="globe-hint">Drag to turn · click a city</span>'
         f'<a class="home-base" href="#ghettofunk"><span class="home-ico" aria-hidden="true"></span><span><b>Home base</b>Ghetto Funk · Netherlands</span></a></div>', None, "globe-page"),
    # Ghetto Funk: its own home (JUMP-poster layout)
    Page(f'''<div class="gf-home">
  <span class="gf-word">Ghetto Funk</span>
  <button class="gf-photo" data-full="assets/img/gf-home.jpg" data-caption="Ghetto Funk Collective · on stage"><img src="assets/img/gf-home.jpg" alt="Ghetto Funk Collective dancers on stage"></button>
  <div class="gf-text">
    <span class="gf-kicker">Home base · Netherlands</span>
    <p>A dance collective that feels like family to me. I got the honour to become part of it, and to tour with them.</p>
    <div class="gf-crew"><p><span>Founders</span>Ruben Chi &amp; Roche Apinsa</p>
      <p><span>Dancers</span>Joshua Markiet, Imaury dos Santos (Kidlock), Ibrah, Juan Jose Markes, Rowley Silver</p></div>
    <div class="tours">{tours}</div>
  </div>
  {back_link("world", "Back to the globe")}
</div>''', anchor="ghettofunk", cls="gf-page"),
    Page(f'<div class="pg">{top("Ghetto Funk Collective", "All films")}{grid(GF_VIDEOS, 2, 3)}</div>'),
    *project("tgs", DH, "Ghetto Funk on tour · China", "Choreographer · Dancer", "The Greatest Show",
             "We were invited to create a two-hour show and to dance in it ourselves, alongside 170 guest dancers from China. A challenge both as choreographer and as dancer.",
             [("Where", "China"), ("With", "Ghetto Funk Collective"), ("Role", "Choreographer · dancer")],
             f'<div class="pg">{top("The Greatest Show", "Photos")}' + grid(
                 [tile(TGS_PHOTOS[0], "The Greatest Show · China").replace('class="tile"', 'class="tile span-all"')]
                 + [tile(s, "The Greatest Show · China") for s in TGS_PHOTOS[1:]], 2, tpl="3fr 2fr") + '</div>', "",
             extra_left='<a class="more-btn" href="#ghettofunk">Ghetto Funk Collective →</a>'),
    *project("madonna", DH, "London", "Music video", "Madonna · Confessions II",
             "Dancer in Madonna’s <i>Confessions II · The Film</i>. My part starts at 06:55; the player jumps straight there.",
             [("Where", "London"), ("Role", "Dancer"), ("Watch from", "06:55")],
             watch_media("yt", "yJtckcMHM2g", "Madonna · Confessions II, The Film · Jinko from 06:55", yt_thumb("yJtckcMHM2g"), start=415)),
    *project("claude", DH, "Amsterdam", "Music video · Eurovision 2025", "Claude · C’est La Vie",
             "Dancer in the official music video for Claude’s <i>C’est La Vie</i>, the Netherlands’ entry for Eurovision 2025.",
             [("Where", "Amsterdam"), ("Role", "Dancer"), ("Year", "2025")],
             watch_media("yt", "hEHwr5k9pd0", "Claude · C’est La Vie · Official Music Video", yt_thumb("hEHwr5k9pd0"))),
    *project("holygraill", DH, "Lowlands · Biddinghuizen", "Dance film", "Oh My: The Holy GraiLL",
             "A dance film by Linde Wagemakers, shot at Lowlands Festival in Biddinghuizen.",
             [("Where", "Lowlands Festival"), ("Role", "Dancer"), ("Choreography · Direction", "Linde Wagemakers")],
             watch_media("yt", "ulqwdGpfbvk", "Oh My: The Holy GraiLL · Lowlands", yt_thumb("ulqwdGpfbvk")),
             extra_left=credits([("Producer", "Linde Wagemakers"), ("Co-producer", "Lowlandstelevisie"), ("DoP", "Sem Geelen"),
                                 ("1st AC", "Bram van Dommelen"), ("Composer", "Tom van Wee"), ("Edit · Grading", "Sem Geelen"),
                                 ("Styling", "Nina Keijzer"), ("Rehearsal studio", "Chasse Dance Studio"),
                                 ("Cast", "Amber Veltman, Jack Butler, Jinko Joshu Emanuel Wu Adams, Lulu Verstegen, Linde Wagemakers, "
                                          "Maxime Abbenhues, Mees Meeuwsen, Niek Wagenaar, Nina Keijzer, Nikki Duin, Keanah Faith Simin, "
                                          "Sarah Khalay, Sem Houmes, Siena Verber, Winter Wieringa")])),
    *project("yade", DH, "Amsterdam", "Festival show", "Yade Lauren",
             "Yade Lauren asked me to join her show as a performer. We played a festival together and brought more of a fashion vibe to her set.",
             [("Where", "Amsterdam"), ("Role", "Performer")],
             f'<div class="pg">{top("Yade Lauren", "Photos")}' + grid([tile(s, "Yade Lauren · festival show") for s in YADE_PHOTOS], 2, 2) + '</div>', ""),
    *project("shortmovie", DH, "Amsterdam", "Film", "Short movie",
             "A short dance film, made in Amsterdam.",
             [("Where", "Amsterdam"), ("Role", "Dancer")],
             watch_media("video", "short-movie", "Short movie · Amsterdam", "assets/thumbs/short-movie.jpg")),
    *project("asap", DH, "Amsterdam", "Tour", "A$AP Rocky",
             "Dancer in the A$AP Rocky tour show in Amsterdam.",
             [("Where", "Amsterdam"), ("Role", "Dancer")],
             f'<div class="pg">{top("A$AP Rocky", "Tour")}' + grid([tile("asap-01", "A$AP Rocky tour · Amsterdam"), tile("asap-02", "A$AP Rocky tour · Amsterdam")], 1, 2) + '</div>', ""),
    *project("janlondon", DH, "London", "Dance video", "Collab with Jan",
             "A dance collab with Jan, filmed on the streets of London.",
             [("Where", "London"), ("Role", "Dancer")],
             watch_media("video", "dance-jan-london", "Collab with Jan · London", "assets/thumbs/dance-jan-london.jpg")),
    *project("bridge", DH, "Guilin · China", "Dance film", "On the bridge",
             "A dance film shot on a bridge in Guilin, China.",
             [("Where", "Guilin, China"), ("Role", "Dancer")],
             watch_media("video", "dance-performance", "On the bridge · Guilin, China", "assets/thumbs/dance-performance.jpg")),
    *project("jmd", DH, "Amsterdam", "Stage", "JMD",
             "On stage with JMD in Amsterdam.",
             [("Where", "Amsterdam"), ("Role", "Dancer")],
             watch_media("video", "dance-jmd", "JMD · stage, Amsterdam", "assets/thumbs/dance-jmd.jpg")),
    *project("hashna", DH, "Amsterdam", "Collab", "Hashna",
             "A dance collab with Hashna, made in Amsterdam.",
             [("Where", "Amsterdam"), ("Role", "Dancer")],
             watch_media("video", "dance-hashna", "Hashna · collab, Amsterdam", "assets/thumbs/dance-hashna.jpg")),
    *project("damsquare", DH, "Amsterdam", "Street session", "Dam Square",
             "A street session on Dam Square, Amsterdam.",
             [("Where", "Dam Square, Amsterdam"), ("Role", "Dancer")],
             watch_media("video", "dance-footage", "Dam Square · street session, Amsterdam", "assets/thumbs/dance-footage.jpg")),
]

# ───────────────────────── Nº03 Styling ─────────────────────────
SH = ("styling", "Back to styling")
STYLING_PROJECTS = [
    ("Coast Contra · Don’t Worry", "Music video · Berlin MVA", "#videos"),
    ("Groove, The Show", "Theatre · Ghetto Funk × The Ruggeds", "#videos"),
    ("Akyna", "My label · with Pasqual", "#akyna"),
]
styling_list = "".join(f'<a href="{h}"><b>{e(t)}</b><span>{e(k)}</span></a>' for t, k, h in STYLING_PROJECTS)

issue3 = [
    Page(f'<div class="pg">{top("Issue Nº03 · Styling", "Projects")}<h2 class="pg-title">Styling</h2>'
         f'<p class="pg-deck">My styling journey began with styling the Ghetto Funk videos. From there: music videos, the stage and Akyna, the label I run with Pasqual.</p>'
         f'<div class="places hub-list"><div class="place">{styling_list}</div></div></div>', ("styling", "Styling"), anchor="styling"),
    Page('<div class="hub-art hub-photo"><button data-full="assets/img/styling-cover.jpg" data-caption="Coast Contra, Don’t Worry · styled by Jinko Joshu"><img src="assets/img/styling-cover.jpg" alt="Coast Contra, styled by Jinko Joshu"></button>'
         '<span class="globe-hint">Coast Contra · Don’t Worry</span></div>', None, "hub-art-page"),
    Page(f'<div class="pg">{top("Music video", "Berlin Music Video Awards")}<h3 class="pg-h">Coast Contra · Don’t Worry</h3>'
         f'<p class="pg-deck">Styling for Coast Contra’s official music video “Don’t Worry”.</p>'
         + watch_media("yt", "NjRvXjSHze4", "Coast Contra · Don’t Worry (Official Music Video) · Styling", yt_thumb("NjRvXjSHze4")).replace('class="watch"', 'class="watch watch-in"')
         + back_link("styling", "Back to styling") + '</div>', anchor="videos"),
    Page(f'<div class="pg">{top("Theatre show", "Ghetto Funk Collective × The Ruggeds")}<h3 class="pg-h">Groove, The Show</h3>'
         '<p class="pg-deck pg-deck-s">The Ruggeds and Ghetto Funk Collective take the swinging dance concert <i>Groove</i> through the theatres: '
         'fifty years of James Brown, Aretha Franklin and Marvin Gaye, funk &amp; soul, hip-hop and house. Put on your best outfit, sitting still is not an option.</p>'
         + watch_media("yt", "WEawH7y-SRs", "An inside look behind Groove The Show · Ghetto Funk Collective × The Ruggeds", yt_thumb("WEawH7y-SRs")).replace('class="watch"', 'class="watch watch-in"')
         + '</div>'),
    Page(f'''<div class="pg">{top("The label", "AW26")}
  <p class="pg-deck">Akyna is the brand I started together with Pasqual. From production to design, we do everything ourselves.</p>
  <a class="more-btn" href="https://akyna-project.com/" target="_blank" rel="noopener">akyna-project.com</a>
  {grid([tile("akyna-02", "Akyna · AW26"), tile("akyna-03", "Akyna · AW26")], 2, 1)}
  {back_link("styling", "Back to styling")}
</div>''' + giant(["Akyna"], "Akyna", cls="wide"), None, "accent", "30%", anchor="akyna"),
    bleed_page(None, 1, ("akyna-01", "Akyna · AW26")),
]

# ───────────────────────── Nº04 On film ─────────────────────────
F = ("onfilm", "On film")
PL = ("polaroids", "Polaroids")
LANDSCAPE = {7, 9, 12}   # these sit framed on the page; the rest alternate full-bleed / framed
polas = "".join(f'<button class="pola" data-full="assets/img/{p}.jpg" data-caption="Polaroid — shot by Jinko">'
                f'<img src="assets/img/{p}-sm.jpg" alt="Polaroid shot by Jinko" loading="lazy"></button>' for p in POLAS)

issue4 = [opener_page(F, "Issue Nº04 · Photography", "On film", "My own photography — shot on film.", 1, ONFILM[1])]
for i in range(2, 17):
    framed = i in LANDSCAPE or i in {3, 6, 13, 15}
    issue4.append(framed_page(F, "On film", i, ONFILM[i]) if framed else bleed_page(F, i, ONFILM[i]))
issue4.append(Page(f'<div class="pola-sheet"><div class="pola-grid">{polas}</div>'
                   '<div class="pola-foot"><span>Polaroids<br>Instant film</span><span>Shot by Jinko Joshu<br>Amsterdam · 2024</span>'
                   '<span class="pola-mark">On film Nº04</span></div></div>', PL, "pola-page"))


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
      <a class="cover-contact" href="mailto:info@jinkojoshu.com">Contact me</a>
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
    <span class="rep">Represented by {REPRESENTED}</span>
    <a href="https://www.instagram.com/jinkojoshu/" target="_blank" rel="noopener">Instagram</a>
    <a href="https://akyna-project.com/" target="_blank" rel="noopener">Akyna</a>
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
                      issue2, "styling.html", "Nº03 Styling", hub=True,
                      scripts='<script src="assets/globe-land.js"></script>\n'),
    "styling": magazine("styling.html", "Styling — Jinko Joshu",
                        "Styling by Jinko Joshu: Coast Contra — Don’t Worry, and the label Akyna.", issue3, "photography.html", "Nº04 On film", hub=True),
    "photography": magazine("photography.html", "On film — Jinko Joshu",
                            "Photography by Jinko Joshu, shot on film.", issue4, "index.html", "Cover"),
}
for name, html in out.items():
    (site / f"{name}.html").write_text(html)
print(", ".join(f"{n}.html" for n in out), "written")
