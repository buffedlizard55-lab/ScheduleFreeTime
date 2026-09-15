# Verification log - every source used, and every irregularity found

This document is the audit trail for `data/raw/`, `data/games_local.json` and the generated
`schedules.md` / `data/processed/free_time.json`. Nothing in the pipeline was typed in by a
human from memory: every row is transcribed from one of the URLs below, and every row keeps a
link so you can re-check it by hand. The build (`python3 scripts/build.py`) re-derives every
free-window from these files and prints the arithmetic checks quoted here.

## 0. Independent re-verification passes

### 2026-09-14 pass (Westwood One + Bay Area radio + Warriors/Sharks; current snapshot)

| Check | Method | Result |
|---|---|---|
| WWO NFL transcription | `https://www.westwoodonesports.com/nfl-schedule/` Upcoming tab, all 4 page chunks read | **73 rows** (65 with matchups + 8 TBA) with air times, slots and event ids. Air times are pregame-show starts, not kickoffs (MNF 7:00 PM, SNF/TNF 7:30 PM, internationals 9:15 AM ET) - blocking still uses league kickoff + 192 min. |
| WWO NFL vs league table | build cross-check on date + away + home (alias-normalized) | **65/65 match**; matched rows carry the 📻 badge. 8 TBA rows (Dec 26 x2, Jan 2 x2, Jan 9 x3, Jan 10 SNF) are info-only placeholders - the underlying Saturday/Week-18 games already block via the league table. |
| WWO internationals ⚠ | page vs the league's 9 international games | 7 upcoming listed (Oct 4/11/18, Oct 25 Paris, Nov 8 Madrid, Nov 15 Munich, Nov 22 Mexico City); Sep 10 Melbourne presumed past-carried (unverified); **Sep 27 Rio (BAL@DAL 4:25 PM ET) is NOT on the WWO page** - WWO's package is "eight International Games" per its own press release, so Rio is presumed not carried (still blocks as an NFL game). |
| WWO past broadcasts | Cumulus press release 2026-09-09 | Sep 9 Kickoff (NWE@SEA) verified and marked; Sep 10 Melbourne + Sep 13 SNF (DAL@NYG) presumed per pattern but the Past tab is JS-driven and unfetchable - deliberately NOT marked (flagged). |
| WWO NCAA football | `https://www.westwoodonesports.com/ncaa-football/` | **10 Saturday broadcasts**, 2 with air times (Sep 19 7 PM, Oct 31 3 PM ET), 8 officially TBD -> UNCONFIRMED days. Michigan@Oregon shows date range "NOV 14 - NOV 21" - kept Nov 14 + flagged. |
| WWO other properties | us-soccer, golf, ncaa-mcws, ncaa-basketball pages (all read) | All show **"No upcoming events"**; the Masters, College World Series, Frozen Four and March Madness all fall outside Aug-Feb anyway. Nothing else to track in-window. |
| Bay Area WWO carriage | station-finder NFL table + KNBR-FM Wikipedia | SF affiliate = **KNBR-AM / KNBR-FM / KTCT-AM**. WWO's own caveat applies: local conflicts (e.g. a 49ers noon game on KNBR) can pre-empt any broadcast. |
| Warriors 2026-27 | ESPN rendered preseason page + regular-season page (`seasontype/2`, 5 chunks) | **63 rows (6 pre + 57 reg)** with per-game ESPN gameIds. Opener cross-checked vs ESPN API event 401918010 (2026-10-04T23:00Z = 7 PM ET ✓); March rows match the sportsbrackets.net March table. Flagship: 95.7 The Game carries ALL games (insideRadio 2025-09) -> all block. |
| Sharks 2026-27 | ESPN rendered preseason page + regular-season page (6 chunks) + ESPN API event 401891823 | **68 rows (4 pre + 64 reg)** with per-game gameIds. Oct 1/3/5/8/10/13/15 match sportsmediawatch exactly; all 7 in-window back-to-backs match the r/SanJoseSharks schedule thread. Flagship: 98.5 KFOX carries all regular-season games (nhl.com) -> reg blocks; preseason is "select" (unspecified) -> info-only. |
| NBA/NHL durations | product-insights 2026 guide (NBA dashboard audit), sportsgeardaily, nhltraderumorstalk, icehockeyguide | NBA **138 min (2:18)** from the measured 2025-26 avg 2:18:32; NHL **150 min (2:30)** midpoint of the 2:20-2:40 range. See §2. |
| Bay Area radio landscape | flagship source per team (see §1) | Giants KNBR 680/104.5; 49ers KSAN 107.7 + KNBR; Stanford KNBR/KTCT 1050 (gostanford.com 2026-07-30); Earthquakes KSFO 810 (sjearthquakes.com); Warriors 95.7; Sharks KFOX 98.5. **Cal's current flagship is uncertain** (KGO 810's 2022 format change; KNBR aired at least one 2025 Cal game) - flagged, does not affect blocking. |

### 2026-09-11 pass (superseded snapshot)

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

### 2026-09-11 pass #2 — blocking-rule correction + independent re-verification (this session)

| Check | Method | Result |
|---|---|---|
| **Blocking rule (the reported bug)** | The all-NFL layer was display-only, so the site reported free time on days when non-49ers NFL games were on air. | **FIXED**: `BLOCKING_SPORTS` now includes `nfl_all`; every tracked league blocks. Fully-free days 87 -> 62. A full NFL+MLB Sunday (e.g. 2026-09-13) now blocks 9:10 AM-8:32 PM PT instead of showing "free". |
| MLB Sep 10-12 | Live `statsapi.mlb.com/api/v1/schedule?...` fetched this session | **15 + 5 + 15 games match** the raw files on date, UTC minute and team ids (independent re-check of the earlier 35/35 pass). |
| MLB postseason, all 28 dates | Live API `startDate=2026-09-28&endDate=2026-11-01` fetched this session | **28/28 dates match** `data/raw/mlb_2026_postseason_tbd.txt` exactly (Sep 29 - Oct 31, 1-4 games/day, every row `startTimeTBD=true`, placeholder `07:33:00Z` + placeholder team ids 4944-4947 / 4612-4619 / 5525-5533 / 2710-2711). Sep 28 confirmed as an off day. |
| 49ers full schedule | nfl-sports.com, nflplayoffpass.com, footballnationusa.com, usagametime.com (all fetched this session) | **18/18 timed rows match** `games_local.json` (Wk1 5:35 PM PT Melbourne, Wk6 Mon 5:15 PM PT, Wk7 10:00 AM PT, Wk9 1:05, Wk10 1:25, Wk11 5:20 Mexico City, Wk12 1:25, Wk13 10:00 AM, Wk15 Thu 5:15 PM, Wk16 1:25, Wk17 5:20). The three prior corrections (Nov 29 1:25, Dec 6 10:00 AM, Dec 17 5:15 PM) are reconfirmed; Wk18 stays TBD on the club page. |
| NFL Week 1 + Week 12 (Thanksgiving) | nfl.com "2026 NFL Schedule Announced", SI, CBS, nflplayoffpass | Week 1 (16 games: Sep 9 SEA-NE opener, Sep 10 SFO-LAR Melbourne, Sep 14 DEN-KAN MNF) and Week 12 (Nov 25 GNB-LAR 8 PM ET; Nov 26 CHI-DET 1 PM / PHI-DAL 4:30 PM / KAN-BUF 8:20 PM; Nov 27 DEN-PIT 3 PM; Nov 29 SEA-SFO 4:25 PM) **match the raw file row-for-row**. |
| **NFL all 9 international games** | Official NFL international slate (`operations.nfl.com/programs-initiatives/international-growth/nfl-international-games` + the league PDF + profootballhof.com) | **9/9 match exactly**: Sep 10 SFO-LAR 8:35 PM ET (Melbourne); Sep 27 RAV-DAL 4:25 PM (Rio); Oct 4 CLT-WAS 9:30 AM (London); Oct 11 PHI-JAX 9:30 AM (London); Oct 18 HTX-JAX 9:30 AM (Wembley); Oct 25 PIT-NOR 9:30 AM (Paris); Nov 8 CIN-ATL 9:30 AM (Madrid); Nov 15 NWE-DET 9:30 AM (Munich); Nov 22 MIN-SFO 8:20 PM (Mexico City). |
| **Seahawks full season (17 + Wk18)** | CBS Sports by-team, FOX13 Seattle, The Athletic, printablepedia (4 independent, mutually consistent) | **17/17 games + Wk18 matchup match exactly**, incl. the unusual Sat Dec 19 5:00 PM ET kickoff (`15|2026-12-19|17:00|SEA@PHI`) and Mon Nov 2 MNF. Note: the CBS team-by-team BEARS table has scrambled week numbers (lists "Wk8 Nov 29") and is NOT used. |
| Christmas (Dec 25) + Saturday (Dec 19) slates | sportsmediawatch + CBSSports week-by-week | Dec 25: GNB-CHI 1:00 PM / BUF-DEN 4:30 PM / LAR-SEA 8:15 PM ET **all match**; Dec 19: SEA-PHI 5:00 PM ET + CHI-BUF 8:20 PM ET **both match**. |
| ESPN cross-check (independent) | `site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=...` | First event of 2026-09-13 (TB@CIN 1:00 PM ET) and 2026-11-29 (NO@CIN 1:00 PM ET) match the raw rows; ESPN season calendar windows confirm Wk1=Sep 6-15, Wk12=Nov 25-Dec 1, Wk17=Dec 30-Jan 5, Wk18=Jan 6-12, and postseason weeks (WC Jan 13-19, Div Jan 20-26, CC Jan 27-Feb 2, Pro Bowl Feb 3-9, SB Feb 10-15) that contain the repo's specific dates (WC Jan 16-18, Div Jan 23-24, CC Jan 31, SB Feb 14). |
| Pro Bowl 2027 ⚠ | nflplayoffpass (Tue Feb 9, 8 PM ET, SoFi) vs sportbusy (Sun Feb 7, SoFi) vs ESPN calendar (Pro Bowl week Feb 3-9) | Still **unresolved** - no official NFL announcement reachable. Kept as an UNCONFIRMED placeholder on Feb 9 with the conflict documented; that day is not asserted as free. |
| Stanford (12 games) | gostanford.com official release (2026-01-26) + Wikipedia + 247sports | **12/12 dates/opponents match**; set kickoffs match (Aug 29 4:00 PM, Sep 4 6:00 PM, Sep 19 1:00 PM, Sep 26 7:30 PM, Oct 10 12:30 PM, Oct 17 4:30 PM, Oct 23 7:30 PM PT). |
| Cal (12 games) | calbears.com + Wikipedia + sportsbrackets + CBS | **12/12 dates/opponents match**; set kickoffs match (Sep 5 7:30 PM, Sep 12 12:30 PM, Sep 19 12:30 PM, Sep 25 7:30 PM, Oct 3 12:30 PM PT). |
| **Earthquakes (17 games)** | sjearthquakes.com official 2026 schedule release + ESPN + Wikipedia | **17/17 in-window games match — and this pass found the repo was missing the Nov 7 Decision Day finale @ Minnesota United (4:00 PM PT, game 34/34)**, which had been mis-labelled "conditional". ADDED to `games_local.json`; the conditional Nov 7 row was removed. |
| Durations | BetMGM (2026-08-31), SBJ (2026-04-29), Under Armour, sportssurge | MLB default updated 158 -> **164 min (2:44, 2026 season)**; NFL 192 / NCAA 204 / MLS 120 reconfirmed. |

Caveat: the Wikipedia Earthquakes page prints several kickoffs that differ from the club's own
release (e.g. Sep 9 as 5:30 PM, Sep 26 as 4:00 PM, Oct 10 as 5:30 PM). The repo keeps the official
club-release times (7:30 PM / 7:30 PM / 6:30 PM PT) which ESPN also matches; Wikipedia's rows appear
to carry stale/placeholder times and are NOT used.

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
| Warriors 2026-27 | `https://www.espn.com/nba/team/schedule/_/name/gs/season/2027/seasontype/2` + `.../name/gs/golden-state-warriors` (preseason) | 63 games; per-game review `https://www.espn.com/nba/game/_/gameId/<id>/x`. Flagship proof: `https://www.insideradio.com/free/nba-s-warriors-95-7-the-game-extend-flagship-partnership/article_8c79d479-424c-408d-9753-f353f7e18a57.html` |
| Sharks 2026-27 | `https://www.espn.com/nhl/team/schedule/_/name/sj/season/2027/seasontype/2` + `.../name/sj/san-jose-sharks` (preseason) | 68 games; per-game review `https://www.espn.com/nhl/game/_/gameId/<id>/x`. Flagship proof: `https://www.nhl.com/sharks/news/sharks-and-kfox-announce-multi-year-extension/c-782397` |
| Westwood One NFL | `https://www.westwoodonesports.com/nfl-schedule/` (+ `.../station-finder/` for Bay Area carriage) | 65 broadcasts + 8 TBA; per-event review `https://www.westwoodonesports.com/events/<id>`. Kickoff proof: Cumulus press release 2026-09-09 (globenewswire). |
| Westwood One NCAAF | `https://www.westwoodonesports.com/ncaa-football/` | 10 Saturday broadcasts; per-event review links. |
| Bay Area radio flagships | `https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced` (Stanford/KNBR-1050), `https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season` (Quakes/KSFO-810), `https://bearinsider.com/s/2255/cal-extends-partnership-with-kgo-radio` (Cal/KGO-810, 2020 - current status uncertain, flagged) | Proves which station carries which team; see §3 item 19. |

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
| MLB | **164 min** = 2:44 | 2026 season average. `https://sports.betmgm.com/en/blog/mlb/average-game-time-in-mlb-bm23/` (Aug 31, 2026: "MLB's average game time for the 2026 season is two hours and 44 minutes"); SBJ `https://www.sportsbusinessjournal.com/Articles/2026/04/29/mlb-pace-of-play-slows-game-lengths-rise-despite-pitch-timer/` (first 421 games: 2:43). MLB's official 2025 final was 2:38 (`https://www.mlb.com/press-release/press-release-mlb-attendance-reaches-71-4-million-three-straight-years-of-growth-for-first-time-since-2007`). Postseason runs ~3:04-3:15 but postseason rows are TBD and do not block. |
| NFL (also applied to the All-NFL layer) | **192 min** = 3:12 | Widely reported average incl. 12-min halftime, timeouts, reviews: `https://underarmour.com/en-us/t/playbooks/football/the-real-length-of-a-football-game/` ("in 2025, NFL games averaged three hours and 12 minutes"), `https://sportssurge.alibaba.com/football/how-long-is-an-average-football-game` (Nielsen & NFL statistics). Secondary: `https://www.theringer.com/2024-09-05/nfl/...` uses 3:15 as a modeling assumption. Super Bowl days in our data are placeholders, so ceremonial extra length (~3:45) does not affect windows. |
| NCAA (Stanford/Cal) | **204 min** = 3:24 | Same sportssurge/lines tables ("college averages 3:24 with 20-min halftimes"); Under Armour says 3:27 for 2025 - we ship 3:24 and let you edit. |
| MLS (Earthquakes) | **120 min** = 2:00 | `https://www.tickpick.com/blog/how-long-are-mls-games/`, `https://authoritysoccer.com/how-long-are-mls-games-and-seasons/` (90 min + ~15-min halftime + stoppage). Playoffs may run over 2:00 with extra time - conditional days are not blocked anyway. |
| NBA (Warriors) | **138 min** = 2:18 | Measured 2025-26 average **2:18:32** tip-to-buzzer (`https://www.alibaba.com/product-insights/how-long-is-the-average-basketball-game-2026-guide.html`, citing the NBA official game-ops dashboard + broadcast-timing audits; includes 15-min halftime, 20+ timeouts). Secondary: `https://sportsgeardaily.com/basketball/how-long-are-basketball-games` (~2:15 avg; stabilized 2:10-2:14 over five seasons). |
| NHL (Sharks) | **150 min** = 2:30 | Midpoint of the reported **2:20-2:40** range: `https://nhltraderumorstalk.com/how-long-is-a-hockey-game` ("averages roughly 2h20 to 2h40"; 60 min play + two 18-min intermissions + TV timeouts); `https://icehockeyguide.com/hockey-game-length/` ("typically 2.5 to 3 hours" incl. intermissions/stoppages/OT). |

Original user guidance ("MLB ~150 min; football 180 + 15–30 halftime") is superseded by the
researched figures above; set the UI inputs back to 150/180+ to compare.

## 3. Irregularities flagged for your review

The build re-emits all of these as machine-readable `flags` in `data/processed/free_time.json`
and `schedules.md`. Status counts with the current data (2026-09-14 pass): 212 days in window ->
**22 FREE, 130 PARTIAL, 60 UNCONFIRMED, 0 FULLY BOOKED**; 120 flags. (The drop from 62 FREE is the
Warriors + Sharks evening slate - most Nov-Feb weeknights now have a Bay Area radio game on.)

### Added / changed in the 2026-09-14 pass

- **ADDED — Warriors (NBA) + Sharks (NHL) as high-priority blocking leagues.** 63 + 68 games
  from ESPN's rendered team pages with per-game review links; 65/65 WWO NFL broadcasts matched.
- **ADDED — Westwood One layers.** NFL broadcasts badge the matching league rows (📻); the NCAA
  football showcase (10 Saturdays) blocks as its own league (8 TBD -> UNCONFIRMED days).
- **ADDED — NBA 138 min / NHL 150 min durations** (researched, §2); UI inputs editable.
- **KNOWN GAP (new) — WWO TBA matchups.** Dec 26 (x2), Jan 2 (x2), Jan 9 (x3) and Jan 10 SNF are
  announced by WWO with "Teams TBA". The underlying games already block via the league table, but
  re-transcribe `data/raw/westwoodone_nfl_2026.txt` once WWO names them.
- **KNOWN GAP (new) — Cal radio flagship uncertain.** KGO 810 AM carried Cal for 47 years through
  2020, but KGO changed format in Oct 2022 and KNBR aired at least one 2025 Cal game. No 2026
  flagship announcement was reachable. Flagged; blocking is unaffected (Cal games block regardless).

### Fixed / changed in the 2026-09-11 pass #2

- **FIXED — all-NFL was non-blocking.** The reported bug ("it says I have free time on days when
  there are football games on") was exactly this: the league-wide NFL table was display-only.
  `BLOCKING_SPORTS` now includes `nfl_all`, so all 272 regular-season games, the preseason rows
  that have a published time, and the postseason/pro-bowl placeholder days (via UNCONFIRMED) all
  count against free time. The old "block all-NFL" opt-in toggle was removed from the UI.
- **FIXED — missing Earthquakes Decision Day finale.** The club's 2026 schedule release lists game
  34/34 as **Sat Nov 7, 2026 @ Minnesota United, 4:00 PM PT** (Decision Day). The repo's PDF
  transcription had ended at the Oct 31 home finale and mis-labelled Nov 7 as "conditional".
  Added to `games_local.json`; removed the conditional Nov 7 row.
- **CHANGED — MLB duration default** 158 -> 164 min (2:44, the 2026 season average) per §2.
- **KNOWN GAP (unchanged) — non-49ers preseason kickoff times.** The PFR preseason table prints no
  kickoff times, so ~47 non-SF preseason games remain `info_only` (listed, never blocking, never
  marked UNCONFIRMED). Those games are all in the past (Aug 2026), so they do not affect future
  free time, but August's free windows ignore them. To close the gap, transcribe nfl.com preseason
  scores pages into `data/raw/nfl_2026_pfr_preseason.txt` and re-run.

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
8. **PRO BOWL DATE CONFLICT** - Feb 7 (sportbusy.com; ESPN's "Pro Bowl Feb 3-9" week window also
   allows it) vs Feb 9, 2027 (nflplayoffpass.com: "moved into Super Bowl week, Tuesday Feb 9, 8 PM ET").
   No official NFL announcement reachable from the proxy as of 2026-09-11. Placeholder row on Feb 9
   + flag until an official source publishes the date; the day is UNCONFIRMED, never asserted free.
9. **NFL preseason ties** - Aug 13 CLT@NWE 13-13 and Aug 28 SEA@KAN 9-9 are real ties (preseason); flagged
   by the build so nobody "fixes" them into winners.
10. **Doubleheaders (5)** - MLB days where the same matchup appears twice on one `officialDate` (split
    nights/rescheduled); both rows block, so the merged window is still correct.
11. **Earthquakes vs Decision Day (RESOLVED 2026-09-11 pass #2)** - the club's official release lists
    the Decision Day finale **@ Minnesota United, Sat Nov 7, 2026, 4:00 PM PT** as game 34/34. This was
    missing from the earlier PDF transcription (which ended Oct 31) and is now a real blocking game.
    Remaining playoff windows (Nov 18 - Dec 18) stay conditional on SJ qualifying.
12. **Stanford/Cal bowls are deliberately NOT day-marked** - bowls (Dec 12 - Jan 1) are assigned after
    Selection Day Dec 6, 2026; the README tells you to re-run the build afterwards. Same for any
    Stanford/Cal CFP appearance beyond the conditional markers we do list.
13. **README/data mismatch (resolved 2026-09-11)** - README now states Aug 1, 2026 - Feb 28, 2027 and the
    All-NFL display layer matches `schedules.md`.
14. **Preseason times not transcribed for ~47 non-SF games** - the official PFR preseason table prints no
    kickoff times; those rows are display-only ("info_only"), never blocking, never set UNCONFIRMED.
15. **WWO_RIO_EXCLUDED** - Sep 27 BAL@DAL (Rio, 4:25 PM ET) is absent from the WWO page: 8 of 9
    internationals carried. Re-check if WWO adds it.
16. **WWO_TBA / WWO_PAST_UNVERIFIED / WWO_PREEMPTION** - 8 TBA matchups (re-check Dec/Jan); Sep 10
    Melbourne + Sep 13 SNF presumed but unverified (not badged); KNBR can pre-empt any WWO feed.
17. **SCHEDULE_GAP (2)** - Warriors idle Dec 2-11 (NBA Cup window) + Feb 18-24 (All-Star break);
    Sharks idle Jan 31-Feb 9. Confirmed ESPN gaps, not missing rows. Cup/All-Star games don't block.
18. **ODD_START + NEUTRAL_SITE** - Sharks Dec 22 @SEA 9:40 PM ET kept as printed; Warriors Oct 13
    preseason vs LAL is at Golden 1 Center Sacramento (neutral).
19. **Cal flagship uncertain** - see "Added / changed" above. Stanford (KNBR/KTCT 1050) and
    Earthquakes (KSFO 810) flagships are confirmed by 2026 club announcements.
20. **PRESEASON_INFO_ONLY (4)** - Sharks Sep 20/22/24/26: KFOX carries only "select" preseason
    games (unspecified which), so all four are listed but never block. Warriors preseason all
    blocks (95.7 carries "all preseason and regular season games").

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
