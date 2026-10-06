#!/bin/zsh
# Rebuilds web-optimized media in site/assets from the original folders.
# Originals are never modified; existing outputs are skipped (delete one to rebuild it).
# Run from the WEBSITE folder: zsh tools/build-media.sh   — then: python3 tools/build-page.py
set -e
cd "${0:A:h}/.."
V=site/assets/video; I=site/assets/img; R=site/assets/reel
mkdir -p $V $I $R site/assets/yt

vid() { [[ -f "$V/$2.mp4" ]] || avconvert -s "$1" -p Preset1920x1080 -o "$V/$2.mp4" --replace; }
img() {
  [[ -f "$I/$2.jpg" ]] && return
  sips -s format jpeg -s formatOptions 82 -Z 2200 "$1" --out "$I/$2.jpg" >/dev/null
  sips -s format jpeg -s formatOptions 75 -Z 900  "$1" --out "$I/$2-sm.jpg" >/dev/null
}

# Commercials (full films)
vid "Full commercials/Nike - Member Days - DC ALT 2.MP4"            nike-member-days-dc-alt
vid "Full commercials/Samsung global campaign.MP4"                  samsung
vid "Full commercials/Bol X JBL/BOL_JBL_Sport_Offsite_1x1.mov"      bol-x-jbl
vid "Full commercials/NIKE BTS - MALE MODEL 1080x1350.mov"          nike-bts
vid "Full commercials/Full commercial Lavish.mp4"                   lavish
vid "Full commercials/Full trailer Lucid Dreaming.mp4"              lucid-dreaming-trailer
vid "Full commercials/Phillips commercial visuals.mp4"              philips
vid "Full commercials/foot athletes .mov"                           taf-2025
# (nike-member-days.mp4 was converted from a file no longer in the folder — keep it.)

# Dance
vid "Dance clips/DANS JMD .mp4"                          dance-jmd
vid "Dance clips/IMG_9121.mp4"                           dance-performance
vid "Dance clips/Collab video with Hashna.mp4"                      dance-hashna
vid "Dance clips/Footage.mp4"                            dance-footage
vid "Dance clips/Ghettofunk James brown.MP4"             gf-james-brown
vid "Dance clips/GHETTO_FUNK_MEXICO_TEASER_FINAL_3.mp4"  gf-mexico

# Cover showreel: up to 6 s from the middle of each clip in "CLIPS - Showreel" (short clips play whole)
n=0
for f in "Nike - 1 clip showreel.mp4" "Madonna clips .MOV" "Lavish 2 clip showreel.mp4" "Ghettofunk clips.mp4" \
         "ESC_Claude_Cest-la-Vie_3x2_Fragment_04.mp4" "Lucid dream clip 6..mp4" "Clips - transendence 2.mp4" \
         "Bol x Jbl clip.mov" "voor clips showreel .mov" "Clip Ghettofunk showreel.MP4" "Lucid dreaming 3 clip showreel.mp4" \
         "For clips .mp4" "Showreel clip .MP4" "VOor showreel clip brug.mp4"; do
  n=$((n+1)); out=$R/reel-$(printf %02d $n).mp4; src="CLIPS - Showreel/$f"
  [[ -f $out ]] && continue
  d=$(mdls -raw -name kMDItemDurationSeconds "$src")
  read st du <<< "$(python3 -c "d=$d; du=min(d, 6); print(round((d-du)/2, 2), round(du, 2))")"
  avconvert -s "$src" -p Preset1920x1080 -o $out --start $st --duration $du --replace
done

# Photos of Jinko (lookbook)
img "PHOTOS/JINKO 1 FINAL.jpg"                                     jinko-portrait
img "PHOTOS/Nike_MemberDays_Look_12_Jinko_4350_final_crop.jpg"     nike-member-days-look
img "PHOTOS/Adidas Lookbook.JPG"                                   adidas-lookbook
img "PHOTOS/High res - pasqual shoot.jpg"                          pasqual-shoot
img "PHOTOS/9A2A4095.jpg"                                          editorial-01
img "PHOTOS/IMG_5736.jpg"                                          editorial-02
img "PHOTOS/9A2A4230 highlights copy.jpg"                          editorial-03
img "PHOTOS/IMG_3845.jpg"                                          editorial-04
img "PHOTOS/IMG_3846.jpg"                                          editorial-05
img "PHOTOS/IMG_6305.JPG"                                          editorial-06
img "PHOTOS/05.08.2022 DSC_0904 . Nath Martin - Full size.jpg"     nath-martin
img "PHOTOS/21_09_2025_0001.jpg"                                   film-2025-01
img "PHOTOS/21_09_2025_0008.jpg"                                   film-2025-02
img "PHOTOS/21_09_2025_0012.jpg"                                   film-2025-03
img "PHOTOS/Lucid dream group photo.jpeg"                          lucid-dreaming-group
img "PHOTOS/Ghettofunk/Ghetto Funk Collective Salih Kilic.jpg"     ghetto-funk-01
img "PHOTOS/Ghettofunk/Ghetto Funk Collective Salih Kilic (1).jpg" ghetto-funk-02
n=0; for f in Polaroids/*;                          do n=$((n+1)); img "$f" polaroid-0$n; done
n=0; for f in "Full commercials/Bol X JBL"/*.jpg;   do n=$((n+1)); img "$f" bol-jbl-0$n; done
n=0; for f in "Dance clips/The greatest show"/*;      do n=$((n+1)); img "$f" tgs-0$n; done
n=0; for f in "Dance clips/Yade Lauren - show"/*;     do n=$((n+1)); img "$f" yade-0$n; done
n=0; for f in "styling/Styling coast contra "/*;    do n=$((n+1)); img "$f" coast-contra-0$n; done
# Photography by Jinko (numbered in folder order)

# Added 2026-10-06 (named explicitly so new files never shift the numbering above)
img "styling/Styling coast contra /Cover styling.JPEG"             styling-cover
n=0; for f in Akyna/*.jpg;                          do n=$((n+1)); img "$f" akyna-0$n; done
# "On film" magazine: every photo in PHOTOGRAPHY (files only) + the polaroids in their own folder
img "PHOTOGRAPHY/569769000020.jpg"                             onfilm-01
img "PHOTOGRAPHY/61330037.jpg"                                 onfilm-02
img "PHOTOGRAPHY/782104020030.jpg"                             onfilm-03
img "PHOTOGRAPHY/84d19c96-8127-4e34-9a54-f31ffc4abbb6.JPG"     onfilm-04
img "PHOTOGRAPHY/R1-09324-032A.JPG"                            onfilm-05
img "PHOTOGRAPHY/img0010-3.jpg"                                onfilm-06
img "PHOTOGRAPHY/img0010.jpg"                                  onfilm-07
img "PHOTOGRAPHY/img0024.jpg"                                  onfilm-08
img "PHOTOGRAPHY/img0025.jpg"                                  onfilm-09
img "PHOTOGRAPHY/img0028.jpg"                                  onfilm-10
img "PHOTOGRAPHY/img0030-2.jpg"                                onfilm-11
img "PHOTOGRAPHY/img0030.jpg"                                  onfilm-12
img "PHOTOGRAPHY/img0036.jpg"                                  onfilm-13
n=0; for f in "PHOTOGRAPHY/Polaroids one page"/*;   do n=$((n+1)); img "$f" pola-$(printf %02d $n); done
# Brand logos (white silhouettes, shown when you hover a commercial)
S=$(mktemp -d); swiftc -O tools/logo.swift -o $S/logo 2>/dev/null
L="Logo's Commercials"; mkdir -p site/assets/logos
for pair in "nike PNG .webp:nike" "phillips logo PNG.jpeg:philips" "Samsung PNG .webp:samsung" "Bol PNG .png:bol" \
            "foot atletes PNG.png:footathletes" "JBL PNG.avif:jbl" "Lavish PNG.png:lavish"; do
  out=site/assets/logos/${pair##*:}.png
  [[ -f $out ]] || { sips -s format png -Z 360 "$L/${pair%%:*}" --out $out >/dev/null && $S/logo $out $out; }
done
# Halftone cut-outs (black dots, like the cover silhouette)
[[ -f site/assets/mag/commercials-cutout-2.png ]] || swift tools/cutout.swift "Layout inspiration/Commercial object.jpg" site/assets/mag/commercials-cutout-2.png 1800 0
[[ -f site/assets/mag/styling-cutout.png ]] || swift tools/cutout.swift "styling/Styling coast contra /Cover styling.JPEG" site/assets/mag/styling-cutout.png 1800 0

# Showreel soundtrack
mkdir -p site/assets/audio
[[ -f site/assets/audio/showreel.m4a ]] || avconvert -s "Showreel track website  .mp3" -p PresetAppleM4A -o site/assets/audio/showreel.m4a --replace

# Added 2026-10-07
img "PHOTOS/_DSF41084108.jpg"                                      lookbook-new-01
img "PHOTOS/IMG_2903.JPG"                                          lookbook-new-02
img "PHOTOS/3CAA4E35-76EB-4FB2-ABFC-03359399DFB4 2.JPG"            lookbook-new-03
img "PHOTOS/000044650020.JPG"                                      lookbook-new-04
img "PHOTOS/E963CE75-9FFB-4BA5-AF55-8FCA685B1322.JPG"              lookbook-new-05
img "PHOTOS/39EB9F48-D7D8-4596-8A50-0528098D1C29.JPG"              lookbook-new-06
img "PHOTOS/4AAB75E4-3927-4A44-9DFD-3BEB0FC9F838.JPG"              lookbook-new-07
img "PHOTOGRAPHY/img0010 2.JPG"                                    onfilm-14
img "PHOTOGRAPHY/R1-06651-014A.JPG"                                onfilm-15
img "PHOTOGRAPHY/R1-06651-027A.JPG"                                onfilm-16
n=0; for f in "Hair looks "/*;                      do n=$((n+1)); img "$f" hair-$(printf %02d $n); done
img "Dance clips/Asap rocky tour.jpg"                              asap-01
img "Dance clips/Asap rocky tour .jpg"                             asap-02
vid "Dance clips/Short movie .MOV"                                 short-movie
vid "Dance clips/Collab Jan London.MOV"                            dance-jan-london

# YouTube thumbnails
for id in WEawH7y-SRs NjRvXjSHze4 yJtckcMHM2g oVR1SJvekRw CV84FmeBRbU 0otuG_RO1mI hEHwr5k9pd0; do
  [[ -f site/assets/yt/$id.jpg ]] || curl -s -o site/assets/yt/$id.jpg https://i.ytimg.com/vi/$id/maxresdefault.jpg
done

# Commercial/dance thumbnails in site/assets/thumbs are hand-picked frames where Jinko is visible.
# To change one, pick a time from a contact sheet and grab that frame:
#   swift tools/frames.swift sheet site/assets/video/samsung.mp4 /tmp/sheet.jpg 24
#   swift tools/frames.swift frame site/assets/video/samsung.mp4 site/assets/thumbs/samsung.jpg 3.6
# Current picks (seconds): samsung 3.6 · lavish 20.6 · philips 2.3 · taf 69.8 · lucid 6.4 · nikebts 2.8
# wemby.jpg is the Vimeo poster of video 1175554062.
echo done
