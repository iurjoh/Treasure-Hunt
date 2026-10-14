# Treasure-Hunt - Python game in the browser

**English** | [Português (Brasil)](README.pt-BR.md)

## Demo

[![Open demo](https://img.shields.io/badge/demo-live-2ea44f)](https://treasure-hunt-due.pages.dev/web/)

Open in your browser. No installation or terminal required.

A Python treasure-grid game with a browser port using Pyodide. The terminal and browser share the game engine.

**Source / Código:** https://github.com/iurjoh/Treasure-Hunt

**Inspected commit / Commit inspecionado:** `e5d1f48d40cc936cab7f459922984a7839d461a2`

Mobile capture prepared on 2026-10-08; repository upload is pending. No image embed is included until the asset exists.

Mobile capture: 390x844, 2026-10-08. Repository upload remains pending.

## Idea and planning

Make the original PP3 terminal game accessible to portfolio visitors without a local Python installation. Retain the rules, add a web adapter and fix replay, invalid input and clean termination.

## Features and limits

Easy/Medium/Hard boards (3x3, 5x5, 9x9), 4/7/13 guesses, replay same map, new adventure and quit. Names and game state are local to the session.

## Architecture

treasure_hunt.py is the state engine; run.py is CLI; web/index.html and adapter load Python/WebAssembly from the Pyodide CDN. No custom server backend, but external runtime requests exist.

## Design and screenshots

Terminal-inspired dark page, colored text and bottom input. The new capture uses only invented name Ada. Do not label a screenshot as a full tested round.

## Build history

Original Code Institute PP3 Python CLI; September 2026 repair introduced explicit states, UTF-8 handling, clean EOF and shared-engine web adapter. October 1 documentation records the public URL. Earlier before/after screenshots remain historical until individually inspected.

## Performance

Python runtime loads over the network on first visit. No new runtime download/timing measurement or Lighthouse score was taken; first-load and CDN-failure handling need follow-up.

## Security and privacy

Use invented names only for public evidence. Browser gameplay is local, but fetching CDN assets contacts third parties. Do not claim no network activity or complete offline support without testing.

## Testing evidence

2026-10-08: 70 pytest tests passed on the inspected main. Live browser loaded Pyodide, accepted Ada and Easy, and reached the first row prompt. Mobile pixels inspected. Full win/loss/replay and desktop/browser regression suite not rerun today.

## Run locally

```sh
python3 run.py
python3 -m pytest -q
python3 -m http.server 8000
```

Install pytest only in a development environment; game runtime uses standard library. Static server opens /web/.

## Current stage and release identity

The Python engine and web port are present in `main`, not only a revival branch. The live `/web/` page opened on 2026-10-08. The exact deployed source SHA is unverified; the inspected source commit above is not proof of host parity. Record that mapping and a complete browser round before calling a new release verified. Pyodide is an external first-load dependency; CDN failure recovery and complete offline play remain unverified.

## Deployment and roadmap

Run complete web rounds and replay; test CDN failure/cold loading; inspect older screenshot rights/content; capture tablet/desktop; verify deploy matches source.

No hosting account/cost settings or deployment branch were changed or freshly verified. Reachable pages do not prove source/deployment parity.

## Credits and license

Code Institute PP3; original author Iuri Johansson; Pyodide runtime. Existing end-game quotations are credited to Doug Scott and Albert Einstein, not newly reverified.

No root LICENSE exists in the inspected checkout. Do not advertise MIT until original-code rights and third-party terms are checked and a license is approved. No license changed.

## Retained original attributions

### Credits

- Original project: Code Institute Portfolio Project 3 (Python CLI),
  by [iurjoh](https://github.com/iurjoh).
- Quotes in the end-game art: Doug Scott and Albert Einstein.
- Browser runtime: [Pyodide](https://pyodide.org) (CPython compiled to
  WebAssembly), loaded from the jsDelivr CDN.

## Technology and effort snapshot

Captured from repository sources on 2026-10-14. This is a source snapshot, not a claim about production versions or the technology available at the original launch.

- **Stack at this snapshot:** Python standard library for the game engine/CLI; Pyodide for the browser adapter. No exact browser runtime version is asserted by this snapshot.
- **Earlier record:** The repository was recreated for the 2026 revival; the initial retained snapshot is not the date of the original academic game.
- **Observed calendar window:** 2026-09-30 to 2026-10-09: surviving commits reachable from main. Calendar span, not continuous work or time to launch.
- **Pull requests:** 2 visible PRs: 0 open, 2 closed, captured 2026-10-14 before this documentation change. Closed does not mean merged. Deleted/recreated history is excluded.
- **Decision and reason:** One engine serves terminal and browser play, reducing duplicated rules; the web adapter removes the need for visitors to install Python.
- **Estimated active effort:** unavailable. No reliable time log or bounded work-session reconstruction was established. Commit count and elapsed calendar time are not converted into hours.

Evidence: current dependency/source files named above, retained Git history and the repository PR list. Versions and counts are fixed to this snapshot, not live counters.
