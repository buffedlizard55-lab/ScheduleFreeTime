# ScheduleFreeTime

A scoreboard-style calendar that answers one question: **when am I free?**

A moment counts as *busy* if any of these is on air:

* **any MLB game** (all 30 clubs, regular season + postseason placeholders)
* **49ers** — preseason and regular season
* **San Jose Earthquakes**
* **Stanford** NCAA football
* **Cal** NCAA football

Everything is shown in **America/Los_Angeles** time for **Aug 1 – Oct 31, 2026**.

## Run it

```bash
python3 scripts/build.py      # rebuild data + regenerate schedules.md + print the verification report
python3 -m http.server 8000   # then open the printed URL
```

The page needs HTTP (it fetches `data/processed/free_time.json`); opening `index.html`
straight off the filesystem will not work.

## What you get

* **Scoreboard day view** — Yesterday / Today / Tomorrow buttons (or the ← → arrow keys), a
  24-hour timeline with red blocks where games are on and green bands where you are free, and
  the exact free windows: `12:00 AM – 10:05 AM (10h 5m)`, `3:54 PM – 4:00 PM (0h 6m)`, ...
* **Month calendar** — every day colour-coded fully-free / partial / booked / unconfirmed,
  with free hours per cell and a ★ on days the Giants or Athletics play.
* **League toggles and editable durations** — turn a league off or change an average game
  length and every day recomputes instantly.
* **Flag panel** — every irregularity the pipeline found, grouped by type.

## Data provenance

No manual entry anywhere. The pipeline reads hand-transcribed, source-attributed files:

| Path | Contents |
|---|---|
| `data/raw/teams_mlb.json` | all 30 MLB clubs (MLB Stats API) |
| `data/raw/mlb_2026_regseason.txt` | 417 MLB games, Aug 1–31 |
| `data/raw/mlb_2026_september.txt` | 361 MLB games, Sep 1–27 |
| `data/raw/mlb_2026_postseason_tbd.txt` | 55 postseason games, all TBD |
| `data/games_local.json` | 49ers, Earthquakes, Stanford, Cal — with a source URL per game |
| `data/processed/free_time.json` | generated: per-day windows + flags (consumed by the UI) |

`docs/VERIFICATION.md` lists every source URL for manual review, the cross-checks that were
run, the researched average game durations with citations, and every irregularity found.
`schedules.md` is generated (do not hand-edit) and contains the full master list: all 833
games, the day-by-day free windows, and the flag list.

## Rebuilding the data

The exact queries used are recorded in the header comment of each `data/raw/*.txt` file and in
`docs/VERIFICATION.md` §1. Re-run them, replace the files, then `python3 scripts/build.py`.
The build prints a verification report (per-team game counts, doubleheaders, days with no
games, days that are fully booked, flag totals) — read it before trusting a refresh.
