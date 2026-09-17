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
other game in the leagues above still blocks. **📻 marks every game that is live on Bay Area radio** —
hover the icon for the station, and the day view has an **"On the radio in the Bay Area today"** panel
listing them: Westwood One on KNBR 680 AM / 104.5 FM / KTCT 1050 AM (all 65 dated NFL broadcasts matched
65/65 against the league table; per the Cumulus press release (Sep 9, 2026) WWO also airs the
**late-season Saturday games and every NFL postseason game** through Super Bowl LXI), the Giants on
KNBR, the 49ers on KSAN/KNBR, the Earthquakes on KSFO 810 / KZSF 1370, Stanford on KNBR/KTCT 1050,
Cal on KSFO 810 (the Nov 21 Big Game on KNBR — verified per-game 2026-09-17), the Warriors and
Valkyries on 95.7 The Game, and the Sharks on the Sharks Audio Network (online; 98.5 KFOX 2000–2021).
Everything is shown in
**America/Los_Angeles** time (PDT through Oct 31, 2026, then PST) for **Aug 1, 2026 – Feb 28,
2027**.

**MLB postseason 2026 (resolved 2026-09-17):** every date and per-date game count is now verified
against the official mlb.com/postseason bracket at gamePk level (Wild Card on NBC/Peacock — NBC's
first postseason baseball in a generation; ALDS/ALCS on TBS; NLDS/NLCS and the World Series on
FOX). No start time is official yet — all 53 games print TBD — so **54 EST first-pitch windows
from the actual 2025 postseason pattern** (WC 1:08/3:08/6:08/9:08 PM ET, DS 2:08–9:08 PM ET, LCS
5:03–8:08 PM ET, WS 8:00 PM ET) block as clearly-labeled estimates. 4 of 12 spots are clinched
(Rays, Brewers, Dodgers, Yankees — see `data/raw/mlb_2026_playoff_picture.json` with per-claim
sources), and **the Giants and Athletics are both eliminated — no Bay Area MLB club plays in
October**; the days still block (all MLB games block).

Times you won't see yet are shown as **TBD until confirmed** — that includes the MLB postseason
start times (dates are official; times drop after the field is set Sep 27–28) and NFL postseason kickoffs, NFL flex windows, MLS playoff days that depend on San Jose
qualifying, and any Stanford/Cal postseason. Per the site's rule (2026-09-15), a day on which a
tracked game will definitely be played or aired without an official kickoff is **NOT FREE —
TIME TBD**: where a documented pattern exists (2025-26 NFL playoff kickoffs, the league's
standard Saturday windows, Westwood One air times) a clearly-labeled **estimated window**
(hatched on the timeline, EST tag in the tables) blocks the time, and **no free time is
reported on the day at all** (the day shows no free windows and 0 free minutes — "0" means
"not asserted", not "free"; fixed 2026-09-16 pass B after the site was seen reporting free
time on football days). Super Bowl LXI's 3:30 PM PT kickoff is official (ESPN event 401873270).
Days that depend on a team qualifying (MLS playoffs, ACC/CFP/bowls) stay **UNCONFIRMED** —
free time is not asserted there either.

**MLB postseason, partially resolved (2026-09-17):** per MLB's official tracker, **4 of 12 berths
are clinched** — Rays (9/11), Brewers (9/11; NL Central 9/15), Dodgers (9/14; NL West 9/17), Yankees
(9/14) — and the current projected Wild Card bracket is shown on every MLB postseason day
(Sep 29 – Oct 31): AL (1) Rays vs (4) Yankees, (2) Guardians vs (5) Red Sox, (3) Astros vs (6) White
Sox; NL (1) Brewers vs (4) Cubs, (2) Dodgers vs (5) Phillies, (3) Braves vs (6) Padres. Projections
are labeled "as of 2026-09-17, not final" (seeds move through Sep 27), and **all 53 kickoff times
remain officially TBD** (the Stats API still returns 07:33:00Z placeholders — re-verified twice on
2026-09-17; NBC's own Wild Card explainer also still prints "Times and teams are still TBD").
**When the field is set (Sep 27–28), run `python3 scripts/fetch_mlb.py`** — it diffs the live API
against the raw file at gamePk level and prints the exact replacement rows for any game whose time
became official.

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

## Bay Area radio research (new 2026-09-17, updated with Outer Sunset 94122 reception)

Every team above is on Bay Area radio — verified line-by-line with official sources — and **every flagship is receivable on a standard AM/FM radio in Outer Sunset, SF 94122** (see `docs/BAY_AREA_RADIO_RESEARCH.md` § “Reception in Outer Sunset” for the 94122-specific RF analysis):

* **Giants:** KNBR 680 AM / 104.5 FM — flagship since 1979 — [KNBR (AM)](https://en.wikipedia.org/wiki/KNBR_(AM)), [KNBR-FM](https://en.wikipedia.org/wiki/KNBR-FM)
* **49ers:** KSAN 107.7 FM + KNBR 680/104.5 FM — [49ers.com/schedule](https://www.49ers.com/schedule/)
* **Warriors:** 95.7 The Game (KGMZ-FM) — all preseason + regular season — [KTVU](https://www.ktvu.com/sports/warriors-switching-radio-partners-to-95-7-the-game), [Inside Radio](https://www.insideradio.com/free/nba-s-warriors-95-7-the-game-extend-flagship-partnership/article_8c79d479-424c-408d-9753-f353f7e18a57.html)
* **Valkyries:** 95.7 The Game (home games over air, all on Audacy app) — [Audacy Inc press](https://audacyinc.com/press/95-7-the-game-will-be-the-valkyries-flagship-radio-station/)
* **Sharks:** 98.5 KFOX (KUFX-FM) flagship 2000-2021, now Sharks Audio Network — [East Bay Times](https://www.eastbaytimes.com/2005/09/28/sharks-announce-radio-network/), [Mercury News](https://www.mercurynews.com/2021/01/07/san-jose-sharks-move-all-audio-broadcasts-online-end-20-year-relationship-with-kfox/)
* **Earthquakes:** KSFO 810 AM / KZSF 1370 AM — [sjearthquakes.com 2026 release](https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season)
* **Stanford:** KNBR/KTCT 1050 AM — [gostanford.com 2026 broadcast team](https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced)
* **Cal:** KSFO 810 AM in 2026 (KGO 810 AM for 47 years through 2020) — [calbears.com/schedule/2026](https://calbears.com/sports/football/schedule/2026), [bearinsider.com KGO extension](https://bearinsider.com/s/2255/cal-extends-partnership-with-kgo-radio)
* **Westwood One sweep 2026-09-17:** NFL page re-verified (zero deltas, 65 + 8 TBA); NCAAF grid re-verified (13 broadcasts; Sep 26 air time now 3:00 PM ET); NCAA Basketball / U.S. Soccer / Golf pages all "No upcoming events" — **NFL + NCAA football are the only in-window Westwood One sports**; MCWS/WCWS (June), lacrosse (May) and NCAA hockey (April) fall outside the window
* **Westwood One NFL + NCAAF:** Bay Area affiliate KNBR 680/104.5 — [KNBR (AM)](https://en.wikipedia.org/wiki/KNBR_(AM)), [Cumulus press release Sep 9 2026](https://www.globenewswire.com/news-release/2026/09/09/3358684/9032/en/cumulus-media-s-westwood-one-official-network-audio-partner-of-the-nfl-celebrates-40th-consecutive-season-and-reveals-2026-nfl-lineup-and-programming-highlights-from-nfl-kickoff-to.html) — 65/65 NFL broadcasts matched, 13 NCAAF broadcasts (10 Saturday showcases + Nov 28 Michigan@Ohio State, Dec 5 SEC Championship, Dec 12 Army–Navy — the page widget truncates at 10 events; the full list comes from its eventGrid endpoint, verified 2026-09-16 pass B)

Full citations in `docs/BAY_AREA_RADIO_RESEARCH.md` and `docs/VERIFICATION.md` §1.

## Duration research (new 2026-09-17)

Every average duration is researched with official sources — see `docs/DURATION_RESEARCH_2026.md` for line-by-line citations:

* MLB 2:44 — [BetMGM](https://sports.betmgm.com/en/blog/mlb/average-game-time-in-mlb-bm23/), [SBJ](https://www.sportsbusinessjournal.com/Articles/2026/07/14/mlb-game-duration-up-for-the-second-straight-year/)
* NFL 3:12 — [SportsSurge](https://sportssurge.alibaba.com/football/how-long-is-an-average-football-game), [Under Armour](https://www.underarmour.com/en-us/t/playbooks/football/the-real-length-of-a-football-game/)
* NCAA 3:24-3:26 — [SportsEnthusiasts final 3:26](https://sportsenthusiasts.net/2025/08/27/college-football-game-length-in-2025/), [SportsGearDaily table 3:24](https://sportsgeardaily.com/football/how-long-are-football-games)
* MLS ~2:00 — [MLS Multiplex](https://mlsmultiplex.com/2017/01/23/mls-101-explaining-regular-season-match/)
* NBA 2:18:32 measured — [Alibaba 2026 Guide](https://www.alibaba.com/product-insights/how-long-is-the-average-basketball-game-2026-guide.html)
* NHL ~2:30 — [SHOC](https://shoc.com/blogs/chalk-talk/how-long-is-a-nhl-hockey-game)
* WNBA ~2:05 — [SportsMonkie](https://sportsmonkie.com/how-long-are-wnba-games/), [GameTimeHero 1:45-2h](https://www.gametimehero.com/blog/how-long-is-a-wnba-game)

All are editable in the UI sidebar.

## Limitations and next steps

See `docs/LIMITATIONS_AND_NEXT_STEPS.md` for known limitations (estimated windows, flex, Pro Bowl conflict, conditional days) and a checklist of what to re-run when official times drop.

## Data provenance

No manual entry anywhere. The pipeline reads hand-transcribed, source-attributed files:

| Path | Contents |
|---|---|
| `data/raw/teams_mlb.json` | all 30 MLB clubs (MLB Stats API) |
| `data/raw/mlb_2026_regseason.txt` | 417 MLB games, Aug 1–31 |
| `data/raw/mlb_2026_september.txt` | 361 MLB games, Sep 1–27 |
| `data/raw/mlb_2026_postseason_tbd.txt` | 53 postseason games, all times TBD — **dates + counts verified at gamePk level vs mlb.com/postseason (2026-09-17; gamePks + TV recorded)** + 54 estimated first-pitch windows (2025 pattern) |
| `data/raw/mlb_2026_playoff_picture.json` | 2026 clinch/elimination picture with per-claim sources: Rays/Brewers/Dodgers/Yankees clinched; **Giants + Athletics eliminated**; official gamePk bracket |
| `data/raw/mlb_2026_postseason_resolution.txt` | **new 2026-09-17:** the MLB postseason resolution layer — 4 official clinches (mlb.com tracker) + current projected bracket (mlb.com playoff picture) + times-still-TBD status; attached to the TBD rows as `playoff_note` |
| `data/raw/nfl_2026_pfr_regseason.txt` | **all 272 league-wide NFL regular-season games** (PFR league table, cross-checked vs nfl.com + 49ers.com) |
| `data/raw/nfl_2026_pfr_preseason.txt` | all 49 preseason games (times only where official sources publish one) |
| `data/raw/nfl_2027_postseason_tbd.txt` | WC Jan 16–18 / Div Jan 23–24 / CC Jan 31 / **Super Bowl LXI Feb 14, 2027 SoFi** + Pro Bowl Feb 9⚠(date conflict) |
| `data/raw/nba_warriors_2026_27.txt` | 63 Warriors games (6 pre + 57 reg, ESPN rendered pages, per-game review links) |
| `data/raw/nhl_sharks_2026_27.txt` | 68 Sharks games (4 pre info-only + 64 reg, ESPN rendered pages, per-game review links) |
| `data/raw/wnba_valkyries_2026.txt` | 16 Valkyries games in window (9 blocking on 95.7 The Game, 7 Audacy-app-only) + 3 playoff TBD rows (berth clinched 2026-08-17) |
| `data/raw/wnba_2026_playoffs_conditional.txt` | WNBA playoff round dates (Sep 27 – Oct 31) that depend on series outcomes |
| `data/raw/westwoodone_nfl_2026.txt` | 65 WWO NFL broadcasts + 8 TBA placeholders (matched 65/65 vs the league table) |
| `data/raw/westwoodone_ncaaf_2026.txt` | 13 WWO NCAA football broadcasts / 19 rows (7 with confirmed-or-reported official kickoffs incl. Nov 28 / Dec 5 / Dec 12; 12 estimated showcase slots for the 6 still-TBD Saturdays) — full list via the page's eventGrid endpoint (the widget truncates at 10) |
| `data/raw/mls_2026_playoffs_conditional.txt` | MLS playoff windows (Nov 18 – Dec 18) as SJ-conditional UNCONFIRMED days |
| `scripts/fetch_mlb.py` | **new 2026-09-17 pass D:** one-command live re-check of the MLB postseason (gamePk + per-date diff vs the raw file, official-time detection, replacement-row printer, snapshot JSON, offline-safe) |
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
checks for Cal / Stanford / the Earthquakes, and the Valkyries (WNBA, 95.7 The Game) added;
**2026-09-17 pass**: WWO NFL page re-verified 71/71 upcoming events at event-id level (zero deltas),
WWO NCAAF full list re-verified 13/13 via the eventGrid endpoint, MLB Stats API re-queried (53 games /
28 dates, zero delta; all times still 07:33:00Z), MLB.com official clinch tracker + playoff picture
fetched (4 teams clinched — recorded in the new resolution file), the Earthquakes' official 2026 table
re-fetched (Oct 31 vs RSL 2:00 PM PT correction), Stanford 12/12 + Cal 12/12 rows live-verified (incl.
Cal's per-game radio rows: KSFO 810 AM for all games, KNBR 104.5/680 for the Nov 21 Big Game), 49ers
20/20, and the football-day bug fix re-proved by the new UI invariant test (`scripts/ui_logic_test.js`);
the 2026-09-14 pass: 65/65 Westwood One NFL broadcasts matched
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
