# joplin_notes_page

A React + TypeScript dashboard that surfaces exported Joplin work logs and Google Drive presentations.

## Repository layout

- Frontend app (Vite + React + Tailwind) lives at the repo root (`index.html`, `src/`, `package.json`, etc.). Everything under `src/` is bundled by Vite.
- `public/resources/`
  - `public/resources/work_logs/` – exported Joplin HTML files (served as static assets).
  - `public/resources/presentations/` – PDF copies from Google Drive (also served statically).
- `scripts/`
  - `scripts/build_site_data.py` – scans the `public/resources` folders and emits `src/data/content.json`.
  - `scripts/download_presentations/` – contains `download_presentations.py` plus the local `credentials.json`/`token.json` secrets needed to hit the Google Drive API. (The secrets stay gitignored.)

## Development workflow

1. **Gather the raw files**
   - Export Joplin Work Logs into `public/resources/work_logs/`.
   - Configure Google API credentials inside `scripts/download_presentations/` (`credentials.json` + valid `token.json`).
   - Run `python3 scripts/download_presentations/download_presentations.py` to refresh `public/resources/presentations/`.
2. **Generate structured data**
   - Run `python3 scripts/build_site_data.py` whenever the Work Logs or Presentations folders change.
   - The script reports how many entries were captured and rewrites `src/data/content.json`.
3. **Work on the frontend**
   - Install Node.js 18+ if it is not already available.
   - From the repo root run `npm install` once, then `npm run dev` for local development or `npm run build` to produce the static site in `dist/`.
   - The Vite config uses `base: "/joplin_notes_page/"` so the build output can be hosted on GitHub Pages at https://jaca230.github.io/joplin_notes_page/.

## Deployment notes

- Commit the updated `src/data/content.json` whenever you regenerate the dataset so the site stays in sync.
- Publish the Vite build output (e.g., copy `dist` to the `gh-pages` branch or configure GitHub Actions) to update the live site.
