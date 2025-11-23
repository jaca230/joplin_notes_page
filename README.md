# joplin_notes_page

![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)

**Live site → [https://jaca230.github.io/joplin_notes_page/](https://jaca230.github.io/joplin_notes_page/)**

A React + TypeScript dashboard that surfaces exported Joplin work logs and Google Drive presentations.

## Repository layout

- Frontend app (Vite + React + Tailwind) lives at the repo root (`index.html`, `src/`, `package.json`, etc.). Everything under `src/` is bundled by Vite.
- `public/resources/`
  - `public/resources/work_logs/` – exported Joplin HTML files (served as static assets).
  - `public/resources/presentations/` – PDF copies from Google Drive (also served statically).
- `scripts/`
  - `scripts/build_site_data.py` – scans the `public/resources` folders and emits `src/data/content.json`.
  - `scripts/build_search_index.py` – parses Work Log HTML + presentation PDFs into `src/data/search-index.json` so the frontend can do full-text search.
  - `scripts/download_presentations/` – contains `download_presentations.py` plus the local `credentials.json`/`token.json` secrets needed to hit the Google Drive API. (The secrets stay gitignored.)
  - `scripts/requirements.txt` – Python dependencies (`PyPDF2`, `beautifulsoup4`) used by the helper scripts.

## Scripts & automation order

0. **Install script dependencies** – `pip install -r scripts/requirements.txt`
1. **Install script dependencies** – `pip install -r scripts/requirements.txt`
2. **Download presentations** – `python3 scripts/download_presentations/download_presentations.py`
3. **Generate metadata** – `python3 scripts/build_site_data.py`
4. **Build the search index** – `python3 scripts/build_search_index.py`

## Development workflow

1. **Install script dependencies**
   - Run `pip install -r scripts/requirements.txt` (first time or whenever dependencies change).
2. **Gather the raw files**
   - Export Joplin Work Logs into `public/resources/work_logs/`.
   - Configure Google API credentials inside `scripts/download_presentations/` (`credentials.json` + valid `token.json`).
   - Run `python3 scripts/download_presentations/download_presentations.py` to refresh `public/resources/presentations/`.
3. **Generate structured data**
   - Run `python3 scripts/build_site_data.py` whenever the Work Logs or Presentations folders change.
   - The script reports how many entries were captured and rewrites `src/data/content.json`.
4. **Build the full-text search index**
   - Run `python3 scripts/build_search_index.py` to regenerate `src/data/search-index.json` after updating any Work Logs or presentations.
5. **Work on the frontend**
   - Install Node.js 18+ if it is not already available.
   - From the repo root run `npm install` once, then `npm run dev` for local development, `npm run build` for the default production bundle, or `npm run build-docs` to emit a GitHub Pages-ready bundle into `docs/`.
   - The Vite config uses `base: "/joplin_notes_page/"` so the build output can be hosted on GitHub Pages at https://jaca230.github.io/joplin_notes_page/.

## Deployment notes

- Commit the updated `src/data/content.json` whenever you regenerate the dataset so the site stays in sync.
- Publish the Vite build output (e.g., copy `dist` or `docs` produced by `npm run build-docs` to the `gh-pages` branch or configure GitHub Actions) to update the live site.
