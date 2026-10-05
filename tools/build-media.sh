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
vid "dans jobs/DANS JMD .mp4"                          dance-jmd
vid "dans jobs/IMG_9121.mp4"                           dance-performance
vid "dans jobs/Collab Hashna.mp4"                      dance-hashna
vid "dans jobs/Footage.mp4"                            dance-footage
vid "dans jobs/Ghettofunk James brown.MP4"             gf-james-brown
vid "dans jobs/GHETTO_FUNK_MEXICO_TEASER_FINAL_3.mp4"  gf-mexico

# Cover showreel: 2.4 s from the middle of each clip in "CLIPS - Showreel"
n=0
for f in "Nike - 1 clip showreel.mp4" "Madonna clips .MOV" "Lavish 2 clip showreel.mp4" "Ghettofunk clips.mp4" \
         "ESC_Claude_Cest-la-Vie_3x2_Fragment_04.mp4" "Lucid dream clip 6..mp4" "Clips - transendence 2.mp4" \
         "Bol x Jbl clip.mov" "voor clips showreel .mov" "Clip Ghettofunk showreel.MP4" "Lucid dreaming 3 clip showreel.mp4"; do
  n=$((n+1)); out=$R/reel-$(printf %02d $n).mp4; src="CLIPS - Showreel/$f"
  [[ -f $out ]] && continue
  d=$(mdls -raw -name kMDItemDurationSeconds "$src")
  st=$(python3 -c "d=$d; print(max(0, round((d-2.4)/2, 2)) if d > 2.6 else 0)")
  avconvert -s "$src" -p Preset1920x1080 -o $out --start $st --duration 2.4 --replace
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
n=0; for f in "dans jobs/The greatest show"/*;      do n=$((n+1)); img "$f" tgs-0$n; done
n=0; for f in "dans jobs/Yade Lauren - show"/*;     do n=$((n+1)); img "$f" yade-0$n; done
n=0; for f in "styling/Styling coast contra "/*;    do n=$((n+1)); img "$f" coast-contra-0$n; done
# Photography by Jinko (numbered in folder order)
n=0; for f in PHOTOGRAPHY/*;                        do n=$((n+1)); img "$f" photography-$(printf %02d $n); done

# YouTube thumbnails
for id in NjRvXjSHze4 yJtckcMHM2g oVR1SJvekRw CV84FmeBRbU 0otuG_RO1mI hEHwr5k9pd0; do
  [[ -f site/assets/yt/$id.jpg ]] || curl -s -o site/assets/yt/$id.jpg https://i.ytimg.com/vi/$id/maxresdefault.jpg
done

# Commercial/dance thumbnails in site/assets/thumbs are hand-picked frames (frames where Jinko is visible).
echo done
