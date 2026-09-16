# ScheduleFreeTime

A scoreboard-style calendar that answers one question: **when am I free?**

A moment counts as *busy* if any of these is on air:

* **any MLB game** — all 30 clubs, regular season + postseason placeholders
* **any NFL game** — all 32 clubs: preseason, regular season, postseason, Pro Bowl, Super Bowl LXI
* **San Jose Earthquakes**
* **Stanford** NCAA football
* **Cal** NCAA football
* **Golden State Warriors** (NBA — every game is on 95.7 The Game)
* **Golden State Valkyries** (WNBA — every game on the Audacy app; the games that air over the
  air on 95.7 The Game block, the app-only road games are listed info-only)
* **San Jose Sharks** (NHL — every regular-season game is on 98.5 KFOX)
* **Westwood One NCAA football showcase** (national radio, Bay Area: KNBR)

The Giants, Athletics, 49ers, Warriors, Valkyries and Sharks are flagged **high priority** (★), but every
other game in the leagues above still blocks. 📻 marks the games on Westwood One national radio
in the Bay Area (KNBR 680 AM / 104.5 FM): all 65 dated NFL broadcasts were matched 65/65 against
the league table, and per the Cumulus press release (Sep 9, 2026) WWO also airs the **late-season
Saturday games and every NFL postseason game** through Super Bowl LXI. Everything is shown in
**America/Los_Angeles** time (PDT through Oct 31, 2026, then PST) for **Aug 1, 2026 – Feb 28,
2027**.

Times you won't see yet are shown as **TBD until confirmed** — that includes the MLB postseason
and NFL postseason kickoffs, NFL flex windows, MLS playoff days that depend on San Jose
qualifying, and any Stanford/Cal postseason. Per the site's rule (2026-09-15), a day on which a
tracked game will definitely be played or aired without an official kickoff is **NOT FREE —
TIME TBD**: where a documented pattern exists (2025-26 NFL playoff kickoffs, the league's
standard Saturday windows, Westwood One air times) a clearly-labeled **estimated window**
(hatched on the timeline, EST tag in the tables) blocks the time; otherwise no free time is
asserted at all. Super Bowl LXI's 3:30 PM PT kickoff is official (ESPN event 401873270).
Days that depend on a team qualifying (MLS playoffs, ACC/CFP/bowls) stay **UNCONFIRMED**.

## Run it

```bash
python3 scripts/build.py      # rebuild data + regenerate schedules.md + print the verification report
python3 scripts/audit.py      # independent audit: recomputes every day from data/raw/* and diffs
python3 -m http.server 8000   # then open the printed URL
```

`scripts/audit.py` is a deliberately separate implementation (it does not import `build.py`): it
re-reads the raw transcriptions, recomputes every blocked/free window, the day status, the per-day
game census, the UTC→PT and ET→PT conversions and the priority flags, and exits non-zero on any
mismatch. Run it after every build - the 2026-09-16 pass is what caught the MLB postseason
placeholder change (Oct 4: 4 games → 2).

The page needs HTTP (it fetches `data/processed/free_time.json`); opening `index.html`
straight off the filesystem will not work.

## What you get

* **Scoreboard day view** — Yesterday / Today / Tomorrow buttons (or the ← → arrow keys), a
  24-hour timeline with red blocks where games are on and green bands where you are free, and
  the exact free windows: `12:00 AM – 10:05 AM (10h 5m)`, `3:54 PM – 4:00 PM (0h 6m)`, ...
* **Month calendar** — every day colour-coded fully-free / partial / booked / not-free-TBD /
  unconfirmed, with free hours per cell and a ★ on high-priority days (Giants, Athletics,
  49ers, Warriors, Sharks, Westwood One broadcasts).
* **League toggles and editable durations** — turn a league off (it stops both showing and
  blocking), change an average game length, and every day recomputes instantly.
* **Flag panel** — every irregularity the pipeline found, grouped by type.

## Average durations used to block time (researched, not guessed)

| League | Default | Basis |
|---|---|---|
| MLB | 164 min (2:44) | 2026 season average (BetMGM 8/31/26: 2:44; SBJ 4/29/26: 2:43 thru first 421 games). MLB's official 2025 final was 2:38 |
| NFL (49ers and All-NFL) | 192 min (3:12) | Nielsen/league-wide reporting of 3:12 avg incl. 12-min halftime & stoppages |
| NCAA (Stanford/Cal + WWO showcase) | 204 min (3:24) | 2025-data averages 3:24–3:27, 20-min halftimes |
| MLS (Earthquakes) | 120 min (2:00) | 90 min + ~15-min halftime + stoppage |
| NBA (Warriors) | 138 min (2:18) | 2025-26 measured avg 2:18:32 tip-to-buzzer; guides converge ~2:15 |
| NHL (Sharks) | 150 min (2:30) | Midpoint of reported 2:20–2:40 range (~2.5h typical, two 18-min intermissions) |
| WNBA (Valkyries) | 125 min (2:05) | Midpoint of the reported ~2:00–2:10 range for a WNBA game (40 min of play + 15-min halftime) |

Citations in `docs/VERIFICATION.md` §2; the UI inputs are editable if you prefer different
assumptions (e.g. your original 150-min MLB / 180-min NFL guesses).

## Data provenance

No manual entry anywhere. The pipeline reads hand-transcribed, source-attributed files:

| Path | Contents |
|---|---|
| `data/raw/teams_mlb.json` | all 30 MLB clubs (MLB Stats API) |
| `data/raw/mlb_2026_regseason.txt` | 417 MLB games, Aug 1–31 |
| `data/raw/mlb_2026_september.txt` | 361 MLB games, Sep 1–27 |
| `data/raw/mlb_2026_postseason_tbd.txt` | 53 postseason games, all TBD (official bracket calendar, last date Oct 31; re-verified 2026-09-16) |
| `data/raw/nfl_2026_pfr_regseason.txt` | **all 272 league-wide NFL regular-season games** (PFR league table, cross-checked vs nfl.com + 49ers.com) |
| `data/raw/nfl_2026_pfr_preseason.txt` | all 49 preseason games (times only where official sources publish one) |
| `data/raw/nfl_2027_postseason_tbd.txt` | WC Jan 16–18 / Div Jan 23–24 / CC Jan 31 / **Super Bowl LXI Feb 14, 2027 SoFi** + Pro Bowl Feb 9⚠(date conflict) |
| `data/raw/nba_warriors_2026_27.txt` | 63 Warriors games (6 pre + 57 reg, ESPN rendered pages, per-game review links) |
| `data/raw/nhl_sharks_2026_27.txt` | 68 Sharks games (4 pre info-only + 64 reg, ESPN rendered pages, per-game review links) |
| `data/raw/wnba_valkyries_2026.txt` | 16 Valkyries games in window (9 blocking on 95.7 The Game, 7 Audacy-app-only) + 3 playoff TBD rows (berth clinched 2026-08-17) |
| `data/raw/wnba_2026_playoffs_conditional.txt` | WNBA playoff round dates (Sep 27 – Oct 31) that depend on series outcomes |
| `data/raw/westwoodone_nfl_2026.txt` | 65 WWO NFL broadcasts + 8 TBA placeholders (matched 65/65 vs the league table) |
| `data/raw/westwoodone_ncaaf_2026.txt` | 10 WWO NCAA football Saturday broadcasts (2 timed, 8 TBD) |
| `data/raw/mls_2026_playoffs_conditional.txt` | MLS playoff windows (Nov 18 – Dec 18) as SJ-conditional UNCONFIRMED days |
| `data/raw/ncaa_2026_postseason_conditional.txt` | ACC title game Dec 5 + CFP days Dec 18 – Jan 25 (Stanford/Cal-conditional) |
| `data/games_local.json` | 49ers (20 games), Earthquakes (17 games incl. the Nov 7 Decision Day finale), Stanford (12), Cal (12) — with a source URL per game |
| `data/processed/free_time.json` | generated: per-day windows + flags (consumed by the UI) |

`docs/VERIFICATION.md` lists every source URL for manual review, the cross-checks that were run
(incl. the 2026-09-11 passes: MLB re-matched against the live Stats API, 272-game/17-per-team
NFL checks, the 49ers/Stanford/Cal/Earthquakes schedules matched to their official releases, and
three 49ers kickoff-time **corrections** — Dec 17 TNF = 5:15 PM PT, Nov 29 vs SEA = 1:25 PM PT,
Dec 6 at NYG = 10:00 AM PT — plus the 2026-09-16 independent-audit pass: 778 MLB games' per-date counts matched the live Stats API on
all 58 dates with game-level spot checks, the WWO NFL and NCAA-football pages re-verified with zero
deltas, the postseason placeholder corrected (Oct 4: 4 → 2 games, total 55 → 53), next-game spot
checks for Cal / Stanford / the Earthquakes, and the Valkyries (WNBA, 95.7 The Game) added; the
2026-09-14 pass: 65/65 Westwood One NFL broadcasts matched
to the league table, 63 Warriors + 68 Sharks games transcribed from ESPN with per-game review
links, and the Bay Area radio flagship per team documented), the researched durations with
citations, and every irregularity found. `schedules.md` is generated (do not hand-edit) and
contains the full master list: every game of every tracked league, the All-NFL list with ET+PT
times, the Westwood One radio tables, the day-by-day free windows, and the flag list.

## Rebuilding the data

The exact queries used are recorded in the header comment of each `data/raw/*.txt` file and in
`docs/VERIFICATION.md` §1. Re-run them, replace the files, then `python3 scripts/build.py`.
The build prints a verification report (per-team game counts, doubleheaders, days with no
games, days that are fully booked, flag totals) — read it before trusting a refresh.
Things that should be re-run later: after MLB's Oct 2026 playoff seeding is set (bracket times),
after NFL flex schedule drops (Tuesdays), after Decision Day Nov 7, 2026 (Earthquakes), after
bowl selection Sun Dec 6, 2026 (Stanford/Cal bowl games are deliberately not day-marked), when
the league names the Wk-16/17 Saturday matchups (mid-December — replace the estimated Dec 26 /
Jan 2 windows with real games), after the Jan 3, 2027 slate (real Wk-18 and playoff kickoffs
replace the estimated windows), when college conferences announce the remaining WWO kickoff
times (6-12 days before each game), when the NFL settles the Pro Bowl date (Feb 7 vs Feb 9 —
remove the losing day), and after any NBA/NHL postponement (re-transcribe the ESPN team pages).

The build also syntax-checks `index.html`'s inline script with `node --check` — the 2026-09-14
deploy shipped a broken script that made the whole site load no data, so that check now prints
in the verification report (and fails it on error).
