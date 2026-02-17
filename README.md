# joplin_notes_page

![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)

**Live site → [https://jaca230.github.io/joplin_notes_page/](https://jaca230.github.io/joplin_notes_page/)**

Vite + React + TypeScript site that surfaces exported Joplin work logs and Google Slides/PDF decks.

## What's inside

- `src/` – React app (bundled by Vite) styled with Tailwind.
- `public/resources/work_logs/` – exported Joplin HTML files; linked assets live under `public/resources/_resources/`.
- `public/resources/presentations/` – downloaded Google Slides/PDF decks.
- `scripts/` – helper scripts:
  - `build_site_data.py` writes `src/data/content.json` (metadata).
  - `build_search_index.py` writes `src/data/search-index.json` (full-text search).
  - `download_presentations/` fetches Google Slides (`credentials.json`/`token.json` stay local).
- `docs/` – GitHub Pages output from `npm run build-docs`.

## Prerequisites

- Node.js 18+ and Python 3.10+.
- Install JS deps: `npm install`.
- Install script deps: `pip install -r scripts/requirements.txt`.

## Refresh the data (work logs + presentations)

1. Export Joplin Work Logs into `public/resources/work_logs/` (their linked files stay in `public/resources/_resources/`).
2. Configure Google API credentials in `scripts/download_presentations/credentials.json` + `token.json`, then run `python scripts/download_presentations/download_presentations.py` (add `--overwrite` to force refresh).
3. Rebuild metadata: `python scripts/build_site_data.py` (updates `src/data/content.json`).
4. Rebuild the search index: `python scripts/build_search_index.py` (updates `src/data/search-index.json`).
5. Commit `src/data/*.json` so the deployed site stays in sync.

## Run the app locally

- `npm run dev` – start the Vite dev server (http://localhost:5173 by default; pass `--host`/`--port` if needed).
- `npm run build` – production build to `dist/`.
- `npm run build-docs` – production build to `docs/` for GitHub Pages.

## Deployment notes

- GitHub Pages serves from `docs/`; the build includes `.nojekyll` so `_resources/` assets load correctly.
- Publish the contents of `docs/` (from `npm run build-docs`) to the `gh-pages` branch or enable Pages from `/docs` on `main`.
