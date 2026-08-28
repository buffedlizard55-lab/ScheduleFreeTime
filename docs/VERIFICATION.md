# Verification log - every source used, and every irregularity found

Snapshot date: **2026-08-28** (UTC). Everything below was read directly from the listed
source on that date and transcribed by hand into `data/`. Nothing was inferred, estimated
from memory, or taken from a secondary aggregator unless explicitly marked.

## 0. Independent re-verification (running again on 2026-08-28 by the site build)

A second, independent pass was run while building the GitHub Pages site. What it checked and found:

* **Pipeline reproducibility.** `python3 scripts/build.py` was run from a clean working tree.
  Output was byte-for-byte identical to the committed `data/processed/free_time.json`,
  `data/processed/mlb.json`, and `schedules.md`. `git status` stayed clean.
* **MLB clubs.** `https://statsapi.mlb.com/api/v1/teams?sportId=1&season=2026` returned
  exactly the same 30 clubs (id, abbr, league, division) as `data/raw/teams_mlb.json`.
* **MLB game records.** The official schedule endpoint matched the repo byte-exactly on every
  date re-pulled: 2026-08-28 (15 games), 2026-08-29 (17 games; both AZ@SF and BOS@NYY
  doubleheaders), 2026-09-01 (15), 2026-09-02 (15), 2026-09-04 (16; DET@CLE doubleheader),
  and 2026-09-27 (15 games, all 19:05-19:20Z). 2026-09-28 returned no MLB games, matching the
  "Sep 28 off day" irregularity.
* **Raw totals.** Parsing the raw files directly gives 778 MLB regular-season games over 58
  dates (per-team range 51-53 = 51.9 mean), 55 postseason placeholders over 28 dates, and 44
  49ers/Earthquakes/Stanford/Cal games. These equal the build report values.
* **Official club/sport pages.** The 49ers schedule page matched all 10 window games, the
  Earthquakes 2026 PDF matched all 16 window games, the Stanford schedule page matched all 9
  window games, and the Cal schedule page matched all 9 window games.
* **Sandbox limitation (flagged).** The build sandbox could not open `statsapi.mlb.com` or
  `github.io` directly (TLS handshake was dropped for outbound `curl`/`urllib`). Those two
  hosts were reached instead through the page-fetch proxy, which returned the raw API JSON.
  As a result, the full 778-game list was NOT re-downloaded inside the sandbox; verification of
  the MLB list was done on the dates above plus a deterministic re-parse of the committed raw
  files. This is an environment limitation, not a data error found in the repo.

## 1. Primary sources (open each link to re-verify manually)

| Dataset | Source | Status |
|---|---|---|
| All 30 MLB clubs (id, name, abbr, league, division) | `https://statsapi.mlb.com/api/v1/teams?sportId=1&season=2026` | Fetched, 30/30 clubs parsed |
| Every MLB game Aug 1 - Sep 27, 2026 (all clubs) | `https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-08-01&endDate=2026-08-31&fields=dates,date,games,gameDate,teams,away,home,team,id` (same query with `2026-09-02`..`2026-11-08`) | Fetched in full; **778 games / 58 dates** |
| MLB postseason placeholders (Sep 29 - Oct 31) | same query, Oct/Nov range | **55 games, all TBD** |
| 49ers preseason + regular season | `https://www.49ers.com/schedule/` (official club site) | Fetched, Weeks 1-18 read |
| 49ers preseason week 2 date cross-check | `https://www.nfl.com/scores/2026/preseason-week-2` | Confirms "Thursday, August 20th", 49ers at Chargers |
| Earthquakes full 2026 schedule | `https://images.mlssoccer.com/image/upload/v1766018474/assets/sje/schedule/2026%20Schedule.pdf` (official club PDF, linked from `sjearthquakes.com/schedule/printable`) | Fetched; 34 MLS games listed |
| Stanford 2026 football | `https://gostanford.com/sports/football/schedule` | Fetched (times in PDT) |
| Stanford schedule announcement | `https://gostanford.com/news/2026/1/26/complete-2026-schedule-unveiled` | Fetched (dates/venues) |
| Cal 2026 football | `https://calbears.com/sports/football/schedule` | Fetched (scoreboard + schedule table) |

### Cross-checks performed
* **Aug 28 MLB slate** was fetched twice - once at full fidelity (with venue/score/status) and
  once through the compact pipeline. Both returned the same 15 games with identical
  `gameDate` values (CIN@CHC 18:20Z, LAD@DET 22:40Z, MIA@WSH 22:45Z, KC@CLE 23:10Z,
  HOU@NYM 23:10Z, SD@TB 23:10Z, ...). No discrepancy.
* **Sep 1** was fetched independently before the September batch; the Aug 31 batch's
  after-midnight-UTC games (ATH@TEX 00:05Z, CWS@HOU 00:10Z, BAL@COL 00:40Z, NYY@LAA 01:38Z,
  PHI@AZ 01:40Z) line up exactly with the Sep 1 batch. No overlap, no gap.
* **Stanford times**: gostanford.com prints PDT; CBS Sports prints the same games in ET
  (Aug 29 7:00pm ET, Sep 4 9:00pm ET, Sep 19 4:00pm ET, Sep 26 10:30pm ET, Oct 10 3:30pm ET,
  Oct 17 7:30pm ET, Oct 23 10:30pm ET). Every pair converts to the same instant, which
  confirms the Pacific reading. The same PDT convention is used for Cal.
* **Weekday check**: every date in the Earthquakes PDF was checked against the real 2026
  calendar (SAT 8.01, WED 8.19, SAT 9.05, WED 9.09, SAT 10.10, WED 10.14 ...). All 17 match.
* **Per-team balance**: 778 games x 2 slots / 30 clubs = 51.9 games per club; actual range
  51-53. No club is missing games.

## 2. Average durations used (researched, with sources)

The blocked window for each game is `[kickoff, kickoff + duration]`.

| League | Value used | Source |
|---|---|---|
| MLB | **164 min (2:44)** | 2026 in-season average reported by BetMGM (`https://sports.betmgm.com/en/blog/mlb/average-game-time-in-mlb-bm23/`, Aug 25 2026), which attributes the figure to MLB pace-of-play data; 2025 finished at 2:38-2:40 per MLB's official pace-of-play report |
| NFL (49ers) | **192 min (3:12)**, 12-min halftime | Nielsen / NFL statistics, via `https://sportssurge.alibaba.com/football/how-long-is-an-average-football-game` |
| NCAA (Stanford, Cal) | **204 min (3:24)**, 20-min halftime | same source; college games run longer than NFL because of the 20-minute halftime |
| MLS (Earthquakes) | **120 min (2:00)** | league-average comparison table, `https://www.lines.com/guides/how-long-is-baseball-game/1523` |

**Source-quality caveat (flagged):** the sandbox could not open `mlb.com`'s own press-release
page directly, so the MLB figure comes from secondary sources that quote MLB's pace-of-play
report. The other three come from secondary aggregations of Nielsen/league data. All four are
editable in the UI, and `scripts/build.py` has them as constants, so you can swap in an
official number without touching anything else. Your own estimates (MLB 150, football 180 +
15-30 min halftime) are in the same range; the researched values are what ship as defaults.

## 3. Irregularities flagged for your review

The complete machine-generated list is at the bottom of `schedules.md`. The material ones:

1. **The 2026 MLB regular season ends Sunday Sep 27** - all 15 games start within a 15-minute
   band (19:05-19:20Z = 12:05-12:20 PM PT), the traditional simultaneous finish.
2. **Sep 28 has zero MLB games** - a genuine fully-free day (no other tracked sport plays either).
3. **All 55 postseason games are placeholders.** The MLB Stats API returns `07:33:00Z` and
   placeholder team ids (4612-4947, 5513-5533, 2710/2711) for every one of them. That timestamp
   is **not** a real start time; it is treated as TBD and does not block any window. 18 days in
   late Sep/Oct are therefore marked `UNCONFIRMED`, not `FREE`.
4. **49ers Week 1 is an international game.** Official site lists Thu 09/10, 5:35 PM PDT,
   **vs** the Rams at the **Melbourne Cricket Ground** - a "home" game played in Australia.
5. **49ers Week 6 is a Monday** (10/19, 5:15 PM PDT vs Washington) and **Week 7 kicks off at
   10:00 AM PDT** in Atlanta - both unusual, both exactly as the official club schedule prints them.
6. **49ers Week 8 is a BYE** (Nov 1), just outside the window.
7. **Kickoff times could not be confirmed for two completed 49ers preseason games**
   (Aug 20 at Chargers, Aug 27 at Raiders). 49ers.com shows them as FINAL without a time.
   They are recorded with `start_pt = null` and flagged rather than guessed. Manual review:
   `https://www.nfl.com/games/49ers-at-chargers-2026-pre-2` and
   `https://www.nfl.com/games/49ers-at-raiders-2026-pre-2`. The Aug 13 Titans game *is*
   confirmed at 6:00 PM PT via ESPN's UTC timestamp `2026-08-14T01:00Z`.
8. **Earthquakes vs LAFC on Sep 19 is at Levi's Stadium**, not PayPal Park (official PDF).
9. **Five MLB split doubleheaders** in the window (Aug 17 STL@CIN, Aug 29 BOS@NYY and AZ@SF,
   Sep 4 DET@CLE, Sep 22 TB@NYY). Both games of each pair are in the data, so they block two
   separate windows rather than one.
10. **Nine unconfirmed kickoffs**: Earthquakes Oct 31 (PDF prints "TBD"), Stanford Oct 3 and
    Oct 31 (TBA), Cal Oct 10/17/24/31 (no time listed). None of these block time, so the free
    windows on those days are **optimistic** until the times are announced.
11. **Stanford's NC State game was date-ambiguous.** The Jan 26 official release said
    "Friday, Oct. 23 OR Saturday, Oct. 24"; the live schedule page now lists Fri Oct 23,
    7:30 PM PDT. Recorded as Oct 23 and flagged.
12. **The MLB duration figure is contested across the cited sources.** The shipped default
    is 164 min (2:44), from BetMGM's Aug 25 2026 post. On the same re-check date, another
    sports-data page said MLB was "trending near 2:38" and cited official MLB pace-of-play
    data for 2025 (2:38). Neither is an MLB.com press release, and the value is editable in
    the UI and in `scripts/build.py`. Treat 164 min as a reasonable-but-not-official 2026
    default.
13. **README wording contradiction.** README says "No manual entry anywhere," but the raw
    files are explicitly described as "hand-transcribed" (the only way to snapshot the
    source URLs). The data is source-attributed and reproducible, but transcription is
    manual and should be re-verified against the URLs in this file.

## 4. Known limitations (stated plainly)

* **Game status (postponed / cancelled / suspended) was not captured** for the bulk of the
  regular season, to keep the dataset small. A postponed game would still block its slot in
  the snapshot. This affects historical accuracy on individual days, never the schedule shape.
* **Static snapshot.** The data is frozen at 2026-08-28. Re-run the fetches documented above
  and `python3 scripts/build.py` to refresh.
* **Free time = "no game on air".** Broadcast lead-in/post-game coverage is not counted
  (buffers default to 0 and are documented in `scripts/build.py`).
* **Earthquakes playoff games are not in the window** - the MLS regular season ends Oct 31 and
  the club's 2026 PDF lists 34 regular-season games only. If San Jose qualifies, playoff games
  would start in November.
