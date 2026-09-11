# ScheduleFreeTime

A scoreboard-style calendar that answers one question: **when am I free?**

A moment counts as *busy* if any of these is on air:

* **any MLB game** (all 30 clubs, regular season + postseason placeholders)
* **49ers** — preseason and regular season
* **San Jose Earthquakes**
* **Stanford** NCAA football
* **Cal** NCAA football

Everything is shown in **America/Los_Angeles** time (PDT through Oct 31, 2026, then PST) for
**Aug 1, 2026 – Feb 28, 2027**.

**All NFL football is also listed** — all 272 regular-season games plus all 49 preseason games
plus the postseason / Pro Bowl / Super Bowl LXI placeholder days — but per the spec those rows are
*display-only and never block*: only 49ers games count against your free time. (The UI has an
opt-in toggle if you want the all-NFL list to block too. Times you won't see yet are shown as
**TBD until confirmed** — that includes NFL flex windows, MLS playoff days that depend on
San Jose qualifying, and any Stanford/Cal postseason.)

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
* **League toggles and editable durations** — turn a league off (or list All-NFL without
  blocking it), change an average game length, and every day recomputes instantly.
* **Flag panel** — every irregularity the pipeline found, grouped by type.

## Average durations used to block time (researched, not guessed)

| League | Default | Basis |
|---|---|---|
| MLB | 158 min (2:38) | MLB official 2025 season average (press release); 2026 in-progress tracks 2:43–2:44 |
| NFL (49ers and All-NFL) | 192 min (3:12) | Nielsen/league-wide reporting of 3:12 avg incl. 12-min halftime & stoppages |
| NCAA (Stanford/Cal) | 204 min (3:24) | 2025-data averages 3:24–3:27, 20-min halftimes |
| MLS (Earthquakes) | 120 min (2:00) | 90 min + 15-min halftime + stoppage |

Citations in `docs/VERIFICATION.md` §3; the UI inputs are editable if you prefer different
assumptions (e.g. your original 150-min MLB / 180-min NFL guesses).

## Data provenance

No manual entry anywhere. The pipeline reads hand-transcribed, source-attributed files:

| Path | Contents |
|---|---|
| `data/raw/teams_mlb.json` | all 30 MLB clubs (MLB Stats API) |
| `data/raw/mlb_2026_regseason.txt` | 417 MLB games, Aug 1–31 |
| `data/raw/mlb_2026_september.txt` | 361 MLB games, Sep 1–27 |
| `data/raw/mlb_2026_postseason_tbd.txt` | 55 postseason games, all TBD (official bracket calendar, last date Oct 31) |
| `data/raw/nfl_2026_pfr_regseason.txt` | **all 272 league-wide NFL regular-season games** (PFR league table, cross-checked vs nfl.com + 49ers.com) |
| `data/raw/nfl_2026_pfr_preseason.txt` | all 49 preseason games (times only where official sources publish one) |
| `data/raw/nfl_2027_postseason_tbd.txt` | WC Jan 16–18 / Div Jan 23–24 / CC Jan 31 / **Super Bowl LXI Feb 14, 2027 SoFi** + Pro Bowl Feb 9⚠(date conflict) |
| `data/raw/mls_2026_playoffs_conditional.txt` | MLS playoff windows (Nov 18 – Dec 18) as SJ-conditional UNCONFIRMED days |
| `data/raw/ncaa_2026_postseason_conditional.txt` | ACC title game Dec 5 + CFP days Dec 18 – Jan 25 (Stanford/Cal-conditional) |
| `data/games_local.json` | 49ers, Earthquakes, Stanford, Cal — with a source URL per game |
| `data/processed/free_time.json` | generated: per-day windows + flags (consumed by the UI) |

`docs/VERIFICATION.md` lists every source URL for manual review, the cross-checks that were run
(incl. the 2026-09-11 pass: 35/35 MLB games re-matched, 272-game/17-per-team NFL checks, and
three kickoff-time **corrections** found on 49ers rows: Dec 17 TNF = 5:15 PM PT, Nov 29 vs SEA =
1:25 PM PT, Dec 6 at NYG = 10:00 AM PT), the researched durations with citations, and every
irregularity found. `schedules.md` is generated (do not hand-edit) and contains the full master
list: every game of every tracked league, the All-NFL list with ET+PT times, the day-by-day free
windows, and the flag list.

## Rebuilding the data

The exact queries used are recorded in the header comment of each `data/raw/*.txt` file and in
`docs/VERIFICATION.md` §1. Re-run them, replace the files, then `python3 scripts/build.py`.
The build prints a verification report (per-team game counts, doubleheaders, days with no
games, days that are fully booked, flag totals) — read it before trusting a refresh.
Things that should be re-run later: after MLB's Oct 2026 playoff seeding is set (bracket times),
after NFL flex schedule drops (Tuesdays), after Decision Day Nov 7, 2026 (Earthquakes), after
bowl selection Sun Dec 6, 2026 (Stanford/Cal bowl games are deliberately not day-marked).
