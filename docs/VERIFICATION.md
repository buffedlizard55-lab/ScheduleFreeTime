# Verification log - every source used, and every irregularity found

This document is the audit trail for `data/raw/`, `data/games_local.json` and the generated
`schedules.md` / `data/processed/free_time.json`. Nothing in the pipeline was typed in by a
human from memory: every row is transcribed from one of the URLs below, and every row keeps a
link so you can re-check it by hand. The build (`python3 scripts/build.py`) re-derives every
free-window from these files and prints the arithmetic checks quoted here.

## 0. Independent re-verification passes

### 2026-09-16 pass (independent audit + full live re-verification; CURRENT snapshot)

Two independent things were done this pass: (a) `scripts/audit.py`, a second implementation that
re-derives the whole dataset from `data/raw/*` and diffs it against the generated file, and
(b) a live re-fetch of every source that could have changed since 2026-09-15.

| Source re-checked | What was compared | Result |
|---|---|---|
| **Independent auditor** `scripts/audit.py` (new) | Never imports `build.py`; re-reads the raw transcriptions + `games_local.json`; recomputes the merged blocked list, the free windows, the 1440-min partition, the day status, the per-day game census, MLB UTC→PT and NFL ET→PT conversions, the priority rules and the club censuses | **AUDIT PASSED** — 212 days, 1,424 day-view rows: recomputed free windows == stored on every day; blocked merges == stored; free + blocked == 1440 min; status rule matches; census matches league by league; conversions exact. Three audit-side gaps were fixed in the audit itself (MLS/NCAA/WNBA conditional markers and the WWO TBA rows must be counted; team-less MLB postseason placeholders can never carry a club priority flag) — the data was correct in all three cases. |
| **MLB Stats API (regular season)** | `schedule?sportId=1&startDate=2026-08-01&endDate=2026-09-27&fields=dates,date,totalGames`, plus game-level reads for Sep 16–20 and Sep 22–27 | **58/58 dates match the raw files exactly** (totalGames 778 = 778 transcribed; per-date counts identical date for date, including the light days Sep 10 = 5, Sep 21 = 3, Aug 27 = 7, and the Sep 12/13/19/20 15-game Saturdays/Sundays). Game-level rows (start time + away/home team ids) match for every game on Sep 16–26, including the odd UTC-derived slots 24:05 / 24:10 / 25:38 / 25:40. |
| **MLB postseason placeholders** | `schedule?...startDate=2026-09-28&endDate=2026-11-10&fields=dates,date,totalGames` + a game-level read | **One change since 2026-08-28: 2026-10-04 now has 2 placeholder games, not 4** → postseason total **53, not 55**. All 27 other dates identical; every date still has placeholder team ids and `T07:33:00Z` placeholder times and still renders as **NOT FREE — TIME TBD**. Raw file corrected; `MLB_POSTSEASON_CORRECTION` flag emitted. |
| **Westwood One NFL** | `https://www.westwoodonesports.com/nfl-schedule/` all four chunks (chunk 3 = last; page ends in a reCAPTCHA block) | Every dated broadcast and every TBA row matches `data/raw/westwoodone_nfl_2026.txt` at event-id level (Sep 17 548433 … Jan 10 548510, incl. the 8 TBA placeholders). The page's two render lists slice differently between fetches — a fetch artefact, not a data delta. **Zero deltas.** |
| **Westwood One NCAA football** | `https://www.westwoodonesports.com/ncaa-football/` | Same 10 broadcasts / same event ids: SEP 19 LSU@Ole Miss 557127 (7:00 pm ET, Danny Reed & Derek Rackley), SEP 26 Oklahoma@Georgia 557136 ("3p ET"), OCT 31 Florida@Georgia 557129 ("3:00 pm ET"), the other seven "Air time TBD". WWO lists *air* times, consistently 30 min before the kickoffs stored here. Also noted and deliberately not tracked: event 557048 "Sep 19 UNC Charlotte at Georgia State" appears on the page's schedule API but is **not** a listed national WWO broadcast (no air time, no announcers). **Zero deltas.** |
| **NFL week 2 (league-wide)** | `https://www.nfl.com/schedules/2026/by-week/week-2` — every listed game and network | All 16 rows match the PFR transcription: TNF Sep 17 8:15 PM; Sun Sep 20 at 1:00 PM (CAR-ATL, NO-BAL, MIN-CHI, CIN-HOU, PIT-NE, GB-NYJ, CLE-TB, PHI-TEN), 4:05 PM (JAX-DEN, LV-LAC), 4:25 PM (SEA-ARI, MIA-SF, WAS-DAL), SNF 8:20 PM (CLT-KAN); MNF Sep 21 8:15 PM (NYG-LAR). |
| **49ers (club page)** | `https://www.49ers.com/schedule/` — every remaining game with PT time, TV and radio | **All rows match the repo** — Wk2 Sep 20 1:25 PM vs MIA, Wk3 Sep 27 1:05 PM vs ARI, Wk4 Oct 4 1:25 PM vs DEN, Wk5 Oct 11 1:25 PM @SEA, Wk6 Mon Oct 19 5:15 PM vs WAS, Wk7 Oct 25 10:00 AM @ATL, Wk9 Nov 8 1:05 PM vs LV, Wk10 Nov 15 1:25 PM @DAL, Wk11 Nov 22 5:20 PM vs MIN (Estadio Banorte, Mexico City), Wk12 Nov 29 1:25 PM vs SEA, Wk13 Dec 6 10:00 AM @NYG, Wk14 Dec 13 1:25 PM vs LA, Wk15 Thu Dec 17 5:15 PM @LAC, Wk16 Dec 27 1:25 PM @KC, Wk17 Sun Jan 3 5:20 PM vs PHI (NBC flex window, already flagged), **Wk18 TBD @ARI**. Radio per the club: Wk1–3 "KSFO 810 AM / KSAN 107.7 FM", from Wk4 on "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM" — the repo's flagship row now says exactly that. |
| **Warriors (NBA)** | `https://www.espn.com/nba/team/schedule/_/name/gs/season/2027/seasontype/1` + `/seasontype/2` | Preseason Oct 4 @LAC 10:00 PM ET, Oct 6 vs LAL, Oct 7 @POR, Oct 10 vs SAC, Oct 13 vs LAL (Golden 1 Center — the repo's NEUTRAL SITE flag), Oct 16 vs POR; regular season Oct 21 @LAL (10:00 PM ET) through Nov 19 @MEM — **all 22 rows checked match** the raw file, times included. |
| **Sharks (NHL)** | `https://www.espn.com/nhl/team/schedule/_/name/sj/season/2027` | Oct 1 vs FLA 10:00 PM ET … Oct 31 vs OTT 4:00 PM ET — **all 15 October rows match** (incl. the Oct 10 4:00 PM matinee and the Oct 13 11:00 PM start). |
| **Local fixtures (next games)** | Cal vs Wagner Sep 19 12:30 PM PT (`visitberkeley.com`, ACC Network via iHeart); Stanford at Duke Sep 19 1:00 PM PT = 4:00 PM ET (`fayobserver.com`); Earthquakes vs LAFC Sep 19 4:30 PM PT at Levi's (club 2026 schedule release + VTA) | All three match `games_local.json`. (`gostanford.com/sports/football/schedule` still serves the 2025 season through this proxy — the 2026 rows are verified from the two sources above.) |
| **WNBA Valkyries (new league)** | official club broadcast schedule (2026-04-25), Audacy flagship release, the club's playoff-clinch release (2026-08-17), ESPN's 2026 playoff schedule (2026-09-09), ~2:00–2:10 game-length sources | A Bay Area team on Bay Area radio was missing from the tracker and has been added — see the README/stats panel: 16 in-window regular-season games (9 on 95.7 The Game → blocking + ★; 7 Audacy-app-only → listed info-only), the **playoff berth (clinched 2026-08-17)**, the first-round dates that block (Sep 27; Sep 29 **and** Sep 30, because the club's Game-2 date is one of the two) and every later round as CONDITIONAL markers (Oct 1 → Oct 31). Duration default **125 min (2:05)**. |
| **Pro Bowl 2027** ⚠ still unresolved | sportbusy.com (Feb 7) vs nflplayoffpass.com (Tue Feb 9, 8:00 PM ET) | No official NFL release found; **both candidate days stay blocked** with estimated windows and the `PROBOWL_CONFLICT` flag. Re-check closer to the date. |

Current status counts (2026-09-16 build): 212 days → **21 fully FREE, 124 PARTIAL, 45 NOT FREE — TIME
TBD, 22 UNCONFIRMED, 0 FULLY BOOKED**; 149 flags; 172 days contain at least one high-priority game.
The 2026-09-16 build is the first snapshot where the Valkyries' Sep 27 playoff game (time TBD) turns
that day NOT FREE — Sep 27 also has the final day of the MLB regular season.

### 2026-09-15 pass (football-TBD blocking fix + live re-verification; previous snapshot)

Triggered by the user's bug report: *the site showed free time on days when football games
are on.* Root causes found and fixed (see §3 "Added 2026-09-15"):

| Check | Method | Result |
|---|---|---|
| **Deployed-site JS** ⚠⚠ | `gh api repos/.../contents/index.html?ref=main` → `node --check` on the inline script | **The deployed `main` (merge 2446f62) shipped a fatal JavaScript syntax error** — a missing closing backtick in the games-table template literal (`${g.wwo?`…never closed). The whole app failed to boot, so the deployed page showed the static skeleton with NO data. Fixed in this pass; `build.py` now runs `node --check` on `index.html` every build so a broken script can never ship silently again. |
| WWO package scope (postseason) | Cumulus press release 2026-09-09 (globenewswire.com, fetched live) | "**…eight International Games, late-season Saturday games, and every NFL postseason game, culminating with Super Bowl LXI on February 14, 2027, at SoFi Stadium**." → every playoff day must be NOT FREE. Kevin Harlan & Kurt Warner call MNF + SB LXI. |
| WWO page re-fetch | `westwoodonesports.com/nfl-schedule/` re-read (all 4 chunks) | Every dated broadcast matches the 2026-09-14 transcription row-for-row (date, matchup, air time, slot, event id): 65 dated + 8 TBA. Upcoming list now starts Sep 17 (Sep 14 MNF past). No changes since the last pass. |
| Late-season Saturdays ⚠ | nfl.com by-week pages (week-16, week-17, week-18 read in full) + ESPN scoreboard API (dates=20261226 / 20270102 / 20270109) | **nfl.com and ESPN list ZERO games on Sat Dec 26, Sat Jan 2 and Sat Jan 9** — but WWO sells a Wk16 doubleheader (Dec 26, events 548519/548520, air 4:00/8:00 PM ET), a Wk17 doubleheader (Jan 2, 548521/548522) and a Wk18 **tripleheader** (Jan 9, 548523/548524/548526, air 12:30/4:15/8:00 PM ET). The matchups are picked in-season (2+2 games move off the Dec 27/Jan 3 Sunday slates; 3 Wk-18 games move to Jan 9 + 1 to SNF). → both days now block with ESTIMATED windows 1:30/5:15 PM PT (standard Saturday windows; Wk15 2026 anchor: air 4:30→kick 5:00 PM ET, air 8:00→kick 8:20 PM ET). |
| Week 18 placeholder times ⚠ | `nfl.com/schedules/2026/by-week/week-18` read in full | **All 16 Wk-18 games are officially date/time TBD** (e.g. 49ers at Cardinals shows "TBD / TBD"). PFR's printed "Sunday 1:00 PM ET" was a placeholder; all 16 rows re-stored as TBD. Jan 10 blocks with three ESTIMATED Sunday windows (1:00 / 4:25 PM ET + flex SNF 8:20 PM ET, WWO event 548510). |
| NFL postseason dates | ESPN scoreboard API per date (placeholder events exist on exactly these dates) | **Jan 16 = 2 games** (401872910/11), **Jan 17 = 3** (401872912+), **Jan 18 = 1** (401872915), **Jan 23 = 2** (401872916/17), **Jan 24 = 2** (round dates per nfl-schedule.com + ESPN Div window), **Jan 31 = 2** (401872920 NFC + 401872921 AFC). All TBD times → estimated windows. |
| Super Bowl LXI kickoff | ESPN event 401873270 (fetched live) | **OFFICIAL: Sun Feb 14, 2027, 6:30 PM ET = 3:30 PM PT, SoFi Stadium** ("timeValid": true, detail "Sun, February 14th at 6:30 PM EST", ESPN/ABC broadcast). Blocks 3:30–7:15 PM PT using the researched ~3h45m SB broadcast length (bolavip: "average broadcast length of a Super Bowl settles around 3 hours 40–45 minutes"). |
| Estimated-window basis | 2025–26 postseason actuals (Wikipedia "2025–26 NFL playoffs", schedule table read) | WC Sat 4:30 + 8:00 PM ET; WC Sun 1:00 / 4:30 / 8:15; WC Mon 8:15; Div Sat 4:30 + 8:20; Div Sun 3:00 + 6:30; CC Sun 3:00 + 6:30; SB 6:30 PM ET. These patterns drive the EST-tagged windows (kickoff pattern identical since 2021's 14-team format). |
| Pro Bowl 2027 ⚠ | re-checked: no ESPN event exists on Feb 7 or Feb 9; ESPN season calendar places Pro Bowl week Feb 3–9 | Still unresolved. nflplayoffpass.com (updated Sep 9, 2026; specific: "moved into Super Bowl week for the first time… Tuesday, February 9, 2027… 8:00 PM ET on ESPN") vs sportbusy.com (Feb 7). **Both days now block with an estimated window** (Feb 7 ~12:00–2:00 PM PT, Feb 9 ~5:00–7:00 PM PT, 120-min flag game) and both are flagged; remove the loser when the NFL announces. |
| NFL preseason kickoff times | Sporting News full preseason TV schedule (read in full) + week-1 cross-checks: Yahoo Sports, Fox News, CableTV (all agree on every Week-1 row) + the two officially sourced 49ers times (chargers.com/sofi.com 7:00 PM PT; raiders.com 5:00 PM PT) + HOF game 8:00 PM ET on NBC | **All 49 preseason kickoff times added** (Aug 6 HOF 8:00 PM ET; Wk1 Aug 13–15; Wk2 Aug 20–23; Wk3 Aug 27–29). Consistency checks passed (49ers' three games match club-sourced times exactly; SN's "Home vs Away" orientation mapped to PFR's away|home per row). Preseason now blocks in August. |
| MLB season/postseason boundary | Live Stats API query `startDate=2026-09-26&endDate=2026-09-29&fields=…gameType…` | **Sep 26: 15 "R" games; Sep 27: 15 "R" games (regular season ends); Sep 28: zero games (off day); Sep 29: four "F" Wild Card placeholders at 07:33Z with placeholder team ids 4944–4947 (times TBD)** — matches the raw files exactly. |
| WWO college kickoffs | SEC/Big Ten/club announcements (all fetched live 2026-09-15) | Sep 19 LSU@Ole Miss **7:30 PM ET** (olemissports.com "6:30 p.m. CT on ABC"); Sep 26 Oklahoma@Georgia **3:30 PM ET** (SEC announcement Sep 14, si.com/college/georgia + Yahoo); Oct 31 Florida@Georgia **3:30 PM ET, ABC, Mercedes-Benz Stadium Atlanta** (official gafljax.com FAQ + ajc.com — game moved from Jacksonville during EverBank construction); Nov 7 Oregon@Ohio State **REPORTED 3:30 PM ET on CBS** (The Athletic via si.com + oregonlive.com; official announcement expected Oct 26 — stored as an estimated slot until then); Nov 14 Michigan@Oregon **date confirmed Sat Nov 14** at Autzen (goducks.com game-center 24386; resolves the WWO page's "NOV 14 – NOV 21" range), kickoff TBD. Oct 3 ND@UNC, Oct 10 IND@NEB, Oct 17 PSU@MICH, Oct 24 MISS@TEX, Nov 21 LSU@TEN still TBD in conference/ESPN listings → each blocks BOTH estimated showcase windows (3:30 / 7:30 PM ET = 12:30 / 4:30 PM PT — the two windows WWO's showcase actually uses in 2026). |
| A's radio (documentation) | mlb.com press release 2023 (KTRB), sacbee.com Feb 2025, mercurynews 2019 | A's left Bay Area flagship KTRB 860 (2024); since the West Sacramento move games air on **KSTE 650 AM Sacramento ("Talk 650") + A's Cast on iHeart**, with **KNEW 910** among network affiliates. The A's remain a high-priority club per spec (they already star); no blocking change. |
| Reg-season freshness | WWO page (weeks 2–5 entries) vs league table; nfl.com week-16/17 pages vs table rows | No flex/time changes since 2026-09-11 (Sunday flex starts Week 5; first flex-eligible Tuesday announcements come ~Sep 22 for Week 7). Dec 27 SF@KC 4:25 PM CBS confirmed on nfl.com. |
| **Status model change** | user spec: "any games that are covered on this site should be marked as free time not available" | New day status **NOT FREE — TIME TBD** (red, hatched) for days where a tracked game definitely plays/airs but the kickoff is unofficial: 44 days (NFL playoff days, Sat Dec 26/Jan 2/Jan 9, Wk-18 Sunday, Pro Bowl candidates, MLB postseason dates, WWO college TBD days, Stanford/Cal/Quakes TBD-game days). Free windows on those days are labeled PROVISIONAL and EST windows are hatched + EST-tagged; when a TBD game has no predictable window (e.g. MLB postseason) NO free time is asserted at all. UNCONFIRMED (orange) is now reserved for conditional-qualification days only (MLS playoffs, ACC/CFP/bowls): 18 days. Totals: 22 FREE / 128 PARTIAL / 44 NOT FREE–TBD / 18 UNCONFIRMED / 0 FULLY BOOKED. |

### 2026-09-14 pass (Westwood One + Bay Area radio + Warriors/Sharks; previous snapshot)

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
| NFL all 32 clubs | `https://www.pro-football-reference.com/years/2026/games.htm` + `.../preseason.htm`; official by-week pages `https://www.nfl.com/schedules/2026/by-week/week-9` (wk 16/17/18 read 2026-09-15); preseason kickoff times via `sportingnews.com/us/nfl/news/nfl-preseason-schedule-2026-times-tv-channels-streams-watch/c2141fa9adb0a760d8d02485` (cross-checked Yahoo/Fox/CableTV) | Week, date, kickoff ET, away, home, boxscore link (also encodes the home designation), result for played games. Wk 18 stored TBD (nfl.com official). |
| NFL postseason + late-season Saturday windows | `data/raw/nfl_2027_postseason_tbd.txt` (fully re-written 2026-09-15): ESPN placeholder events 401872910–921 (dates) + 401873270 (SB LXI, OFFICIAL 3:30 PM PT); Cumulus press release 2026-09-09 (every postseason game on WWO); WWO events 548510/519/520/521/522/523/524/526 (Saturday slots + air times); 2025–26 pattern from `en.wikipedia.org/wiki/2025–26_NFL_playoffs`; SB length ~3h45m per `bolavip.com/en/nfl/super-bowl-timeouts-length-duration-breaks` | 25 window rows (1 OFFICIAL + 24 ESTIMATED) blocking every playoff day, Sat Dec 26 / Jan 2 / Jan 9, the Wk-18 Sunday windows and both Pro Bowl candidate dates. |
| WWO NCAA football kickoffs | `olemisssports.com` (Sep 19 6:30 PM CT), SEC announcement via `si.com/college/georgia` + Yahoo (Sep 26 3:30 PM ET), `gafljax.com/faq` + `ajc.com` (Oct 31 3:30 PM ET, Atlanta), The Athletic via `si.com`/`oregonlive.com` (Nov 7 3:30 PM ET, reported), `goducks.com/game-center/24386` (Nov 14 date) | Kickoffs for 3 confirmed + 1 reported WWO showcase games; the 6 still-TBD games block two estimated showcase slots each (12:30 / 4:30 PM PT). |
| San Jose Earthquakes | `https://images.mlssoccer.com/image/upload/v1766018474/assets/sje/schedule/2026%20Schedule.pdf` + `https://www.sjearthquakes.com/schedule` | All 16 games in window (Sep 15 listed "9AM PT"). |
| Stanford football | `https://gostanford.com/sports/football/schedule` (+ `https://gostanford.com/news/2026/1/26/complete-2026-schedule-unveiled`); November rows via wikipedia/247sports/on3 (see §0) | 12 games; times where announced; Nov rows TBD. |
| Cal football | `https://calbears.com/sports/football/schedule` + official release `https://calbears.com/news/2026/1/26/california-football-announces-2026-schedule.aspx` ("All kickoff times will be announced at a later date") | 12 games; Nov 14/21/28 TBD. |
| NFL postseason / SB LXI | `https://www.nfl.com/news/los-angeles-to-host-super-bowl-lxi-in-2027`, `https://www.lasec.net/...`, `https://www.nfl-schedule.com/blog/2026-2027-nfl-playoff-schedule` | Round dates; placeholder rows. |
| MLS postseason | `https://www.mlssoccer.com/playoffs/2025/news/audi-2026-mls-cup-playoffs-key-dates-schedule-information` | Key dates -> conditional day markers. |
| CFP | `https://www.espn.com/college-football/story/_/id/48958840/2026-college-football-playoff-bowl-schedule-46-games` | 2026-27 CFP + bowl calendar -> conditional markers. |
| MLB 2027 ST boundary | `https://www.mlb.com/press-release/press-release-mlb-announces-2027-spring-training-schedule` | Scope note flag only. |
| Warriors 2026-27 | `https://www.espn.com/nba/team/schedule/_/name/gs/season/2027/seasontype/2` + `.../name/gs/golden-state-warriors` (preseason) | 63 games; per-game review `https://www.espn.com/nba/game/_/gameId/<id>/x`. Flagship proof: `https://www.insideradio.com/free/nba-s-warriors-95-7-the-game-extend-flagship-partnership/article_8c79d479-424c-408d-9753-f353f7e18a57.html` |
| Valkyries 2026 (WNBA) | `https://www.oursportscentral.com/services/releases/goldn-state-valkyries-announce-local-television-and-radio-broadcast-schedule/n-6353443` (official club release 2026-04-25: date, PT time AND radio column per game) + flagship `https://audacyinc.com/press/95-7-the-game-will-be-the-valkyries-flagship-radio-station/` + playoff clinch `https://valkyries.wnba.com/news/valkyries-clinch-postseason-berth-for-second-straight-season` + round dates `https://www.espn.com/wnba/story/_/id/49882118/wnba-playoffs-2026-schedule-games-first-round-semifinals-finals-scores-results-news-highlights` | 16 regular-season games in window + 3 playoff TBD rows + 15 conditional playoff-day markers |
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
| WNBA (Valkyries) | **125 min** = 2:05 | Midpoint of the reported range for a WNBA game (40 min of play + 15-min halftime): `https://basketballgem.com/how-long-is-a-basketball-game/` ("~2 hr. 10 min"), `https://sportsmonkie.com/how-long-are-wnba-games/` ("about two hours"), `https://www.gametimehero.com/blog/how-long-is-a-wnba-game` ("1 hour 45 minutes to 2 hours") |
| NHL (Sharks) | **150 min** = 2:30 | Midpoint of the reported **2:20-2:40** range: `https://nhltraderumorstalk.com/how-long-is-a-hockey-game` ("averages roughly 2h20 to 2h40"; 60 min play + two 18-min intermissions + TV timeouts); `https://icehockeyguide.com/hockey-game-length/` ("typically 2.5 to 3 hours" incl. intermissions/stoppages/OT). |

Original user guidance ("MLB ~150 min; football 180 + 15–30 halftime") is superseded by the
researched figures above; set the UI inputs back to 150/180+ to compare.

## 3. Irregularities flagged for your review

The build re-emits all of these as machine-readable `flags` in `data/processed/free_time.json`
and `schedules.md`. Status counts with the current data (**2026-09-16 pass**): 212 days in window ->
**21 FREE, 124 PARTIAL, 45 NOT FREE - TIME TBD, 22 UNCONFIRMED, 0 FULLY BOOKED**; 149 flags; 172 days
contain at least one high-priority game. (The drop from 62 FREE two passes ago is the Warriors +
Sharks + Valkyries evening slate - most Nov-Feb weeknights now have a Bay Area radio game on.)

### Added / changed in the 2026-09-16 pass (current)

- **CORRECTED - MLB postseason placeholder count.** The live Stats API now reports **2** games on
  2026-10-04 (the 2026-08-28 transcription had 4), so the postseason placeholder total is **53**,
  not 55. No free-time change (the day stays NOT FREE - TIME TBD either way); the raw file, the
  README totals and the audit were updated, and the `MLB_POSTSEASON_CORRECTION` flag carries the
  before/after and the URL. Re-check the whole bracket when MLB publishes real times.
- **ADDED - Golden State Valkyries (WNBA) were missing from the tracker.** A Bay Area team on Bay
  Area radio: all games on the Audacy app, home games over the air on **95.7 The Game (KGMZ-FM)**.
  16 in-window regular-season games (9 on 95.7 → blocking + ★; 7 app-only → listed info-only; the
  split comes straight from the club's own radio column), the clinched playoff berth (2026-08-17),
  the first-round dates blocked (Sep 27; Sep 29 **and** Sep 30 - the club's Game-2 date is one of
  the two, so both days say "game will air, time TBD") and all later rounds as CONDITIONAL markers
  (Oct 1 → Oct 31). Duration default 125 min (2:05).
- **NOTED - 49ers radio.** The club page lists "KSFO 810 AM / KSAN 107.7 FM" for weeks 1-3 and
  "KSAN 107.7 FM / KNBR 104.5 FM / 680 AM" from week 4 on; the flagship row and the sources panel
  now say exactly that. (No blocking change - every NFL game blocks anyway.)
- **NOTED - WWO page contains one non-national event.** `ncaa-football/` event 557048
  "Sep 19 UNC Charlotte at Georgia State" has no air time and no announcers - it is not a national
  Westwood One broadcast and is deliberately not tracked (documented so a reviewer does not read it
  as a missed row).
- **RE-VERIFIED (no deltas)** - MLB regular season (58/58 dates, 778 games, game-level checks),
  WWO NFL page, WWO NCAA football page, NFL week 2, the full 49ers schedule, Warriors preseason +
  Oct/Nov, Sharks October, and the next Cal / Stanford / Earthquakes games. Table in §0.

### Added / changed in the 2026-09-15 pass (previous)

- **FIXED — deployed-site JavaScript was fatally broken.** The `main` branch (merge 2446f62)
  shipped `index.html` with a missing closing backtick inside the games-table template literal,
  so the entire app failed to parse: no data loaded, no calendar, no day view. This was the
  primary reason the site misbehaved for the user. Fixed; `build.py` now syntax-checks the
  inline script with `node --check` on every run and fails the verification report on error.
- **FIXED — NFL postseason days showed ~24h free time.** Westwood One airs *every* postseason
  game (Cumulus 2026-09-09 release), so Wild Card (Jan 16–18), Divisional (Jan 23–24),
  Conference Championships (Jan 31) and Super Bowl Sunday (Feb 14) are now **NOT FREE** with
  EST-tagged estimated windows from the 2025–26 kickoff pattern; the Super Bowl has an
  OFFICIAL 3:30 PM PT kickoff (ESPN 401873270) and blocks 3:30–7:15 PM PT (225 min).
- **FIXED — late-season Saturdays (Dec 26, Jan 2, Jan 9) had no games at all.** WWO's
  doubleheader/doubleheader/tripleheader placeholders are now blocking estimated windows
  (1:30/5:15 PM PT; Jan 9 also 10:00 AM PT). The matchups will be picked in-season; re-run then.
- **FIXED — Week 18's "Sunday 1:00 PM ET" was a PFR placeholder.** nfl.com officially lists all
  16 games TBD; the rows are re-stored as TBD and Jan 10 blocks via three estimated Sunday
  windows (1:00/4:25 PM ET + flex SNF 8:20 PM ET). The 49ers' Wk-18 row (@ARI) is TBD on both
  club and league sides now (cross-check 19/19 timed + the one expected TBD non-match).
- **FIXED — 47 of 49 preseason games had no kickoff times and never blocked.** All 49 times
  added from Sporting News (cross-checked vs Yahoo/Fox/CableTV and the officially sourced
  49ers times). August days now block correctly (e.g. Sat Aug 15: NFL preseason 10:00 AM–9:00 PM
  PT windows now block in addition to MLB).
- **FIXED — WWO college-football TBD days showed free time.** Confirmed kickoffs added where
  announced (Sep 19 7:30 PM ET, Sep 26 3:30 PM ET, Oct 31 3:30 PM ET; Nov 7 3:30 PM ET
  reported); the still-TBD games block both estimated showcase windows (12:30/4:30 PM PT).
- **CHANGED — day-status model** per the user's rule: NOT FREE — TIME TBD (44 days) vs
  UNCONFIRMED for conditional-only days (18). See the 2026-09-15 pass table.
- **DOCUMENTED — A's radio** (KSTE 650 Sacramento + A's Cast, KNEW 910 affiliate; KTRB era
  ended 2024) and the Pro Bowl date conflict now blocks BOTH candidate dates (Feb 7 + Feb 9).

### Added / changed in the 2026-09-14 pass (previous)

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
20. **MLB_POSTSEASON_CORRECTION (new 2026-09-16)** - see "Added / changed" above: 2026-10-04 went
    from 4 placeholder games to 2, postseason total 53. Day status unchanged.
21. **WNBA playoff timing/carriage (new 2026-09-16)** - the Valkyries clinched on 2026-08-17, but
    (a) their first-round Game 2 falls on Tue Sep 29 **or** Wed Sep 30 and the club has not said
    which, so both days block; (b) per-game playoff radio carriage is not published, so those days
    block on the presumption that a Bay Area playoff game airs locally (flagged IRREGULARITY);
    (c) if they lose in the first round, the Oct 1 - Oct 31 conditional markers simply disappear -
    re-run the build when the bracket and results are known.
22. **PRESEASON_INFO_ONLY (4)** - Sharks Sep 20/22/24/26: KFOX carries only "select" preseason
    games (unspecified which), so all four are listed but never block. Warriors preseason all
    blocks (95.7 carries "all preseason and regular season games").

## 4. Known limitations (stated plainly)

* The WNBA (Valkyries) default duration is 125 min, the midpoint of a reported ~2:00-2:10 range -
  shorter games will over-block slightly; edit it in the sidebar if you want a tighter fit.
* The Valkyries' playoff rows block **by date** (team qualified) with the start time TBD; the exact
  tip-off is filled in when the league announces it, and Sep 29/30 double-blocks the Game-2 window.
* "Free" means **no listed game from the blocking leagues is on air**. Pre-game hype, watch parties and
  halftime-overrun are not modelled except via the average duration (editable). Buffers default to 0.
* Durations are averages; real games run -30/+60 min (extra innings, overtime, weather delay). For past
  dates you can measure the true overlap from the `result` fields we transcribed for played NFL games.
* **Estimated windows are estimates.** NFL postseason/Saturday/Wk-18 windows and the WWO college
  showcase slots use documented patterns (2025–26 kickoffs, WWO air times, league windows), not
  official 2026-27 times. They are hatched + EST-tagged everywhere and are replaced by real times
  as soon as they are announced (postseason after the Jan 3, 2027 slate; Wk-16/17 Saturday
  matchups mid-December; Wk-18 after Jan 3; college kickoffs 6–12 days before each game).
* The Pro Bowl date is genuinely unresolved (Feb 7 vs Feb 9, 2027): BOTH candidate days block
  with estimated windows and both carry flags. Remove the loser once the NFL announces.
* Times after the 2026-09-15 snapshot can still move (MLB rain postponements, NFL flex, CFP/bowl
  selections, MLS rescheduling). Re-run `scripts/build.py` against fresh raw files to refresh; the build
  prints the arithmetic so silent drift shows up as a failed check.
* MLB rows carry Stats-API `gamePk` only in the raw headers (the file rows use team ids); per-game review
  links for MLB are derivable as `https://mlb.com/statsapi` queries shown in the raw headers.
* The ESPN scoreboard JSON for a full week is ~25 chunks (odds/tickets embedded); the rendered
  week-by-week pages (nfl.com by-week, PFR tables) were used instead and agree wherever sampled.
  ESPN's API rejects date ranges through the fetch proxy used here (single-date queries only).
