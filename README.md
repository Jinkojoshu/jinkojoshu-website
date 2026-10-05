# Jinko Joshu — website

Static one-page portfolio ("Magazine Nº01"). Everything that goes online lives in `site/`.

## Update the content
1. Put new media in the original folders (PHOTOS, Full commercials, dans jobs, …).
2. Add it to `tools/build-media.sh` and run `zsh tools/build-media.sh` (makes web-sized copies in `site/assets/`).
3. Edit the lists/text in `tools/build-page.py` and run `python3 tools/build-page.py` (rewrites `site/index.html`).
4. Preview: `cd site && python3 -m http.server 8080` → http://localhost:8080

## Publish
- Quick: drag the `site` folder onto https://app.netlify.com/drop
- Ongoing: push this repo to GitHub and connect it in Netlify — `netlify.toml` already says to publish `site/`. Every push goes live automatically.

Raw media folders are not in git (see `.gitignore`); unused old assets were moved to `_archive/`.
