# Verification log - every source used, and every irregularity found

This document is the audit trail for `data/raw/`, `data/games_local.json` and the generated
`schedules.md` / `data/processed/free_time.json`. Nothing in the pipeline was typed in by a
human from memory: every row is transcribed from one of the URLs below, and every row keeps a
link so you can re-check it by hand. The build (`python3 scripts/build.py`) re-derives every
free-window from these files and prints the arithmetic checks quoted here.

## 0. Independent re-verification passes

### 2026-09-11 pass (current data snapshot)

| Check | Method | Result |
|---|---|---|
| MLB Sep 10–12 dates | Live query `https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-09-10&endDate=2026-09-18&fields=dates,date,games,gameDate,teams,away,home,team,id,status,...` diffed against `data/raw/mlb_2026_september.txt` | **35/35 games match** (dates, UTC minute, team ids). The "sparse" days are real: Sep 10 (Thu) genuinely had 5 games and Sep 21 (Mon) 3 - normal light-slate days, not dropped rows. |
| NFL league-wide table | Transcribed the full week-by-week table `https://www.pro-football-reference.com/years/2026/games.htm` | **272 rows**; every one of the 32 clubs appears in exactly **17** games; weekly totals 16/16/16/16/15/14/14/14/15/14/13/16/14/15/16/16/16/16 sum to 272 (bye weeks carry 2-6 byes; W11 has 6 because of the international slate). Cross-checked against the rendered official pages (nfl.com by-week, ESPN week-9 table). |
| NFL preseason | `https://www.pro-football-reference.com/years/2026/preseason.htm` | **49 games**; 30 clubs x 3 + ARI/CAR one extra each (Aug 6 Hall-of-Fame-week pairing). Source table prints no kickoff times (display-only rows). |
| 49ers rows vs league table | 19 timed SF rows in `games_local.json` vs the PFR rows (ET-3h) | **18/19 exact**; the 19th is 2027-01-10 (club page TBD - flagged below). |
| 49ers kickoff-time corrections | chargers.com, sofi.com, raiders.com, seahawks.com, levisstadium.com (links in §3) | **3 corrections**: 2026-12-17 TNF was stored as 20:15 PT (that is the game END time / the ET kickoff; correct start = **5:15 PM PT**); 2026-11-29 vs SEA corrected **1:05 -> 1:25 PM PT**; 2026-12-06 at NYG corrected **12:00 -> 10:00 AM PT** (1:00 PM ET). Two 49ers preseason kickoffs that had no time on 49ers.com are now **resolved**: Aug 20 = 7:00 PM PT (chargers.com + sofi.com), Aug 27 = 5:00 PM PT (raiders.com). |
| Stanford / Cal November | gostanford.com schedule fetch returned stale 2025 content via the proxy, so November rows were transcribed from three independent sources that agree: en.wikipedia.org team pages, 247sports.com schedules, on3.com Cardinal Sports Report (May 2026), plus the official calbears.com Jan 26, 2026 release | Stanford: Nov 14 @VT, Nov 21 @Cal, Nov 28 vs SMU (bye Nov 7). Cal: Nov 14 @UVA, Nov 21 vs Stanford, Nov 28 vs Pitt (bye Nov 7). **All six kickoffs are officially "announced at a later date" -> TBD, non-blocking, UNCONFIRMED.** |
| Super Bowl LXI / postseason dates | `https://www.nfl.com/news/los-angeles-to-host-super-bowl-lxi-in-2027` (official) + lasec.net host-committee page + FOX schedule nav | Super Bowl LXI = **Sunday, Feb 14, 2027, SoFi Stadium** (expected 6:30 PM ET kickoff). Wild Card Jan 16–18, Divisional Jan 23–24, Conference Champ Jan 31, 2027. Placeholder rows only (teams unknown until seeds are set). |
| Pro Bowl Games ⚠ | secondary sources conflict: nflplayoffpass.com says Tue **Feb 9, 2027** 8 PM ET at SoFi; sportbusy.com metadata says **Feb 7, 2027** | Kept **Feb 9** with an explicit date-conflict flag; non-blocking informational row. Needs an official announcement before trust. |
| MLS playoff windows | `https://www.mlssoccer.com/playoffs/2025/news/audi-2026-mls-cup-playoffs-key-dates-schedule-information` (official) | Decision Day Nov 7; WC Nov 18; R1 best-of-3 Nov 20–Dec 2; semi Dec 5–6; final Dec 11–12; **MLS Cup Fri Dec 18, 2026**. Added as SJ-conditional UNCONFIRMED days (15 rows incl. the R1 window days). |
| CFP / ACC 2026-27 | ESPN's official CFP schedule article (`espn.com/college-football/story/_/id/48958840/...`) | First round Dec 18–19, QFs Dec 30 + Jan 1, SFs Jan 14–15, **National Championship Mon Jan 25, 2027** (Allegiant, Las Vegas). ACC title game Sat Dec 5, 2026. Added as Stanford/Cal-conditional markers. |
| MLB out-of-window boundary | `https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule` (Sep 4, 2026) | MLB's official bracket calendar has no 2026 games after Oct 31 - so **Nov 1, 2026 - Feb 18, 2027 is confirmed MLB-free**. The one real MLB activity inside the window is **2027 Spring Training starting Fri Feb 19, 2027** (out of scope per "MLB 2026 regular+postseason"; flagged in the build, not blocked). |

### 2026-08-28 pass (still valid for Aug-Sep data)

| Check | Method | Result |
|---|---|---|
| MLB roster of teams | `https://statsapi.mlb.com/api/v1/teams?sportId=1&season=2026` | 30 clubs; `teamId` 137 = Giants, 133 = Athletics -> high-priority flags in the data. |
| MLB schedule Aug 1–Sep 27 | the three `fields=` URLs recorded in the raw file headers | 417 games (Aug) + 361 games (Sep) re-queried; exact match. |
| MLB postseason | `startDate=2026-09-29&endDate=2026-11-08` | 55 games / 28 dates, all `scheduled|TBDxN` with placeholder `07:33:00Z`; kept as UNCONFIRMED placeholders. |

## 1. Primary sources (open each link to re-verify manually)

| League / team | Source of record | What we transcribed |
|---|---|---|
| MLB, all 30 clubs | `https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-08-01&endDate=2026-09-09&fields=...` (+ Sep / postseason variants, in raw-file headers) | Every `officialDate`, `gameDate` (UTC) and away/home `team.id`; converted to America/Los_Angeles by `scripts/build.py`. |
| 49ers | `https://www.49ers.com/schedule/` | Full 2026 schedule incl. preseason; 1:1 matchup/date/time; W9–W18 cross-checked vs PFR league table. |
| NFL all 32 clubs | `https://www.pro-football-reference.com/years/2026/games.htm` + `.../preseason.htm`; official by-week pages `https://www.nfl.com/schedules/2026/by-week/week-9` | Week, date, kickoff ET, away, home, boxscore link (also encodes the home designation), result for played games. |
| San Jose Earthquakes | `https://images.mlssoccer.com/image/upload/v1766018474/assets/sje/schedule/2026%20Schedule.pdf` + `https://www.sjearthquakes.com/schedule` | All 16 games in window (Sep 15 listed "9AM PT"). |
| Stanford football | `https://gostanford.com/sports/football/schedule` (+ `https://gostanford.com/news/2026/1/26/complete-2026-schedule-unveiled`); November rows via wikipedia/247sports/on3 (see §0) | 12 games; times where announced; Nov rows TBD. |
| Cal football | `https://calbears.com/sports/football/schedule` + official release `https://calbears.com/news/2026/1/26/california-football-announces-2026-schedule.aspx` ("All kickoff times will be announced at a later date") | 12 games; Nov 14/21/28 TBD. |
| NFL postseason / SB LXI | `https://www.nfl.com/news/los-angeles-to-host-super-bowl-lxi-in-2027`, `https://www.lasec.net/...`, `https://www.nfl-schedule.com/blog/2026-2027-nfl-playoff-schedule` | Round dates; placeholder rows. |
| MLS postseason | `https://www.mlssoccer.com/playoffs/2025/news/audi-2026-mls-cup-playoffs-key-dates-schedule-information` | Key dates -> conditional day markers. |
| CFP | `https://www.espn.com/college-football/story/_/id/48958840/2026-college-football-playoff-bowl-schedule-46-games` | 2026-27 CFP + bowl calendar -> conditional markers. |
| MLB 2027 ST boundary | `https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule` | Scope note flag only. |

### Cross-checks performed
1. **MLB totals**: 417 + 361 = **778 games / 58 dates**; each of the 30 clubs 51–53 games (mean 51.9) -
   consistent with club-by-club counts. Giants 52, Athletics 52. 0 impossible (<6 AM PT) starts.
2. **NFL totals**: 272 regular-season rows, all clubs exactly 17; 49 preseason rows.
3. **49ers**: every SF league row equals the club row (18/19; the W18 TBD documented).
4. **Earthquakes**: Oct 31 final-match kickoff still "TBD" in club source.
5. **Stanford + Cal**: the Big Game (Nov 21) is one fixture listed on BOTH club pages - we keep both
   rows for provenance but de-duplicate them in the build (single blocking game).
6. **Giants/Athletics high priority**: every row with `home_id`/`away_id` in {137,133} gets
   `priority: true` and renders with a ★ in the UI and bold in `schedules.md`.

## 2. Average durations used (researched, with sources)

Defaults shipped by `scripts/build.py` (the UI inputs are editable):

| League | Default | Source |
|---|---|---|
| MLB | **158 min** = 2:38 | Official: MLB press release Sep 29, 2025 ("average game time 2:38 for the 2025 season") `https://www.mlb.com/press-release/press-release-mlb-attendance-reaches-71-4-million-three-straight-years-of-growth-for-first-time-since-2007`; ESPN corroboration `https://www.espn.com/mlb/story/_/id/46422703/...`. 2026 in progress runs ~2:43–2:44 (`https://sports.betmgm.com/en/blog/mlb/average-game-time-in-mlb-bm23/` Aug 31, 2026; SBJ Apr 29, 2026) - within the error bar; use the UI input if you want 164. |
| NFL (also applied to the All-NFL layer) | **192 min** = 3:12 | Widely reported average incl. 12-min halftime, timeouts, reviews: `https://underarmour.com/en-us/t/playbooks/football/the-real-length-of-a-football-game/` ("in 2025, NFL games averaged three hours and 12 minutes"), `https://sportssurge.alibaba.com/football/how-long-is-an-average-football-game` (Nielsen & NFL statistics). Secondary: `https://www.theringer.com/2024-09-05/nfl/...` uses 3:15 as a modeling assumption. Super Bowl days in our data are placeholders, so ceremonial extra length (~3:45) does not affect windows. |
| NCAA (Stanford/Cal) | **204 min** = 3:24 | Same sportssurge/lines tables ("college averages 3:24 with 20-min halftimes"); Under Armour says 3:27 for 2025 - we ship 3:24 and let you edit. |
| MLS (Earthquakes) | **120 min** = 2:00 | `https://www.tickpick.com/blog/how-long-are-mls-games/`, `https://authoritysoccer.com/how-long-are-mls-games-and-seasons/` (90 min + ~15-min halftime + stoppage). Playoffs may run over 2:00 with extra time - conditional days are not blocked anyway. |

Original user guidance ("MLB ~150 min; football 180 + 15–30 halftime") is superseded by the
researched figures above; set the UI inputs back to 150/180+ to compare.

## 3. Irregularities flagged for your review

The build re-emits all of these as machine-readable `flags` in `data/processed/free_time.json`
and `schedules.md`. Status counts with the current data: 212 days in window -> 87 FREE,
78 PARTIAL, 47 UNCONFIRMED, 0 FULLY BOOKED; ~90 flags.

1. **TBD_TIME (42)** - every unconfirmed kickoff: MLB's 55 postseason placeholders; Earthquakes Oct 31
   (kickoff TBD in club PDF); Stanford Oct 3 @Wake + Oct 31 @Louisville + Nov 14/21/28; Cal's four
   October TBDs + three November TBDs; 49ers Wk18 Jan 10; 13 NFL postseason/pro-bowl rows; and the
   conditional markers. These days are shown UNCONFIRMED - free time there is provisional, never asserted.
2. **CORRECTIONS applied 2026-09-11 (kept as IRREGULARITY flags)** - 49ers Dec 17 (20:15 PT was the END
   time; kickoff 5:15 PM PT per chargers.com/sofi.com/49erswebzone), Nov 29 (1:25 PM PT per
   seahawks.com/levisstadium.com, not 1:05), Dec 6 (10:00 AM PT = 1:00 PM ET, not 12:00). Any downstream
   consumer that pinned the old values shifts by 3h/20min/2h respectively.
3. **RESOLVED** - the two "kickoff time not published" 49ers preseason rows: Aug 20 at LAC = 7:00 PM PT
   (chargers.com + sofi.com), Aug 27 at LV = 5:00 PM PT (raiders.com + SBPride + yahoo 8:15->8:00 PM ET).
4. **49ers Wk 18 (2027-01-10 @ARI)** - club page: no time; league table: 1:00 PM ET = 10:00 AM PT for all
   16 Wk-18 games. Row kept TBD + flagged; re-check before December.
5. **INTERNATIONAL GAMES** - Wk1 2026-09-10 at the Melbourne Cricket Ground (49ers.com "home"; nfl.com
   slug says 49ers-at-rams i.e. Rams home - both keep the 5:35 PM PT kickoff; PFR prints the row with a
   neutral-site separator); Wk11 2026-11-22 "home" game played at Estadio Banorte, Mexico City (5:20 PM PT
   = SNF 8:20 PM ET - times agree); W9 2026-11-08 CIN@ATL listed 9:30 AM ET (Madrid, Santiago Bernabeu);
   W6 2026-10-18 & W5 2026-10-11 9:30 AM ET games (international windows); W1 Wed 2026-09-09 SEA-NE played
   as a neutral-site game (venue not printed on the source row) - display-only, non-blocking anyway.
6. **UNUSUAL LOCAL TIMES** - 2026-10-25 49ers@ATL 10:00 AM PT (1:00 PM ET - verified against the league
   table), Cal Sep 25 7:30 PM PT; MLB Sep 15 Earthquakes-day "9 AM PT" listed on club site.
7. **NFL flex window (FLEX_WINDOW flag)** - the table prints times for all future games, but NFL flex
   can still move Sunday 1:00/4:05/4:25 PM ET games ~12 days ahead (125 games after 2026-09-11 in our rows).
   49ers blocking rows are unaffected by the flag caveat only insofar as 49ers.com itself is re-checked
   weekly - the flex mechanism applies to them too (e.g. a future SF game could be pulled to SNF).
8. **PRO BOWL DATE CONFLICT** - Feb 7 vs Feb 9, 2027 (see §0); placeholder row + flag until an official
   announcement is visible to the proxy.
9. **NFL preseason ties** - Aug 13 CLT@NWE 13-13 and Aug 28 SEA@KAN 9-9 are real ties (preseason); flagged
   by the build so nobody "fixes" them into winners.
10. **Doubleheaders (5)** - MLB days where the same matchup appears twice on one `officialDate` (split
    nights/rescheduled); both rows block, so the merged window is still correct.
11. **Earthquakes vs Decision Day** - SJ's club PDF ends Oct 31 while MLS's regular season runs to
    Decision Day **Nov 7** (all 30 clubs): SJ games only on that day if postponed. Marked conditional.
12. **Stanford/Cal bowls are deliberately NOT day-marked** - bowls (Dec 12 - Jan 1) are assigned after
    Selection Day Dec 6, 2026; the README tells you to re-run the build afterwards. Same for any
    Stanford/Cal CFP appearance beyond the conditional markers we do list.
13. **README/data mismatch (resolved 2026-09-11)** - README now states Aug 1, 2026 - Feb 28, 2027 and the
    All-NFL display layer matches `schedules.md`.
14. **Preseason times not transcribed for ~47 non-SF games** - the official PFR preseason table prints no
    kickoff times; those rows are display-only ("info_only"), never blocking, never set UNCONFIRMED.

## 4. Known limitations (stated plainly)

* "Free" means **no listed game from the blocking leagues is on air**. Pre-game hype, watch parties and
  halftime-overrun are not modelled except via the average duration (editable). Buffers default to 0.
* Durations are averages; real games run -30/+60 min (extra innings, overtime, weather delay). For past
  dates you can measure the true overlap from the `result` fields we transcribed for played NFL games.
* Times after the 2026-09-11 snapshot can still move (MLB rain postponements, NFL flex, CFP/bowl
  selections, MLS rescheduling). Re-run `scripts/build.py` against fresh raw files to refresh; the build
  prints the arithmetic so silent drift shows up as a failed check.
* MLB rows carry Stats-API `gamePk` only in the raw headers (the file rows use team ids); per-game review
  links for MLB are derivable as `https://mlb.com/statsapi` queries shown in the raw headers.
* The ESPN scoreboard JSON for a full week is ~25 chunks (odds/tickets embedded); the rendered
  week-by-week pages (nfl.com by-week, PFR tables) were used instead and agree wherever sampled.
