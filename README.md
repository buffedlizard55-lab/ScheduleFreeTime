# ScheduleFreeTime

A scoreboard-style calendar that answers one question: **when am I free?**

A moment counts as *busy* if any of these is on air:

* **any MLB game** — all 30 clubs, regular season + postseason placeholders
* **any NFL game** — all 32 clubs: preseason, regular season, postseason, Pro Bowl, Super Bowl LXI
* **San Jose Earthquakes**
* **Stanford** NCAA football
* **Cal** NCAA football

The Giants, Athletics and 49ers are flagged **high priority** (★), but every other game in the
leagues above still blocks. Everything is shown in **America/Los_Angeles** time (PDT through
Oct 31, 2026, then PST) for **Aug 1, 2026 – Feb 28, 2027**.

Times you won't see yet are shown as **TBD until confirmed** — that includes the MLB postseason
and NFL postseason kickoffs, NFL flex windows, MLS playoff days that depend on San Jose
qualifying, and any Stanford/Cal postseason. A day with any unconfirmed game is labeled
**UNCONFIRMED** rather than asserting a free-time window that might be wrong.

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
* **League toggles and editable durations** — turn a league off (it stops both showing and
  blocking), change an average game length, and every day recomputes instantly.
* **Flag panel** — every irregularity the pipeline found, grouped by type.

## Average durations used to block time (researched, not guessed)

| League | Default | Basis |
|---|---|---|
| MLB | 164 min (2:44) | 2026 season average (BetMGM 8/31/26: 2:44; SBJ 4/29/26: 2:43 thru first 421 games). MLB's official 2025 final was 2:38 |
| NFL (49ers and All-NFL) | 192 min (3:12) | Nielsen/league-wide reporting of 3:12 avg incl. 12-min halftime & stoppages |
| NCAA (Stanford/Cal) | 204 min (3:24) | 2025-data averages 3:24–3:27, 20-min halftimes |
| MLS (Earthquakes) | 120 min (2:00) | 90 min + ~15-min halftime + stoppage |

Citations in `docs/VERIFICATION.md` §2; the UI inputs are editable if you prefer different
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
| `data/games_local.json` | 49ers (20 games), Earthquakes (17 games incl. the Nov 7 Decision Day finale), Stanford (12), Cal (12) — with a source URL per game |
| `data/processed/free_time.json` | generated: per-day windows + flags (consumed by the UI) |

`docs/VERIFICATION.md` lists every source URL for manual review, the cross-checks that were run
(incl. the 2026-09-11 passes: MLB re-matched against the live Stats API, 272-game/17-per-team
NFL checks, the 49ers/Stanford/Cal/Earthquakes schedules matched to their official releases, and
three 49ers kickoff-time **corrections** — Dec 17 TNF = 5:15 PM PT, Nov 29 vs SEA = 1:25 PM PT,
Dec 6 at NYG = 10:00 AM PT), the researched durations with citations, and every irregularity
found. `schedules.md` is generated (do not hand-edit) and contains the full master list: every
game of every tracked league, the All-NFL list with ET+PT times, the day-by-day free windows, and
the flag list.

## Rebuilding the data

The exact queries used are recorded in the header comment of each `data/raw/*.txt` file and in
`docs/VERIFICATION.md` §1. Re-run them, replace the files, then `python3 scripts/build.py`.
The build prints a verification report (per-team game counts, doubleheaders, days with no
games, days that are fully booked, flag totals) — read it before trusting a refresh.
Things that should be re-run later: after MLB's Oct 2026 playoff seeding is set (bracket times),
after NFL flex schedule drops (Tuesdays), after Decision Day Nov 7, 2026 (Earthquakes), after
bowl selection Sun Dec 6, 2026 (Stanford/Cal bowl games are deliberately not day-marked).
