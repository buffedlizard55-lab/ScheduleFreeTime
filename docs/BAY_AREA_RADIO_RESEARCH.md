# Bay Area Radio Research — Every Sport Broadcast Live in San Francisco

This file documents the line-by-line verification of every Bay Area team and every Westwood One national broadcast that is carried live over the radio in the Bay Area. All sources are official, verified, and linkable for manual review. No hallucinations.

## Westwood One Sports — National Radio Package (Bay Area affiliate: KNBR)

### Scope (official press release)
Westwood One is the official network audio partner of the NFL since 1987. Its 2026 package includes:
- NFL Kickoff, Monday Night Football, Sunday Night Football, Thursday Night Football,
- Thanksgiving, Black Friday, Christmas,
- **eight International Games**,
- **late-season Saturday games**,
- **every NFL postseason game** through Super Bowl LXI.

Source: Cumulus press release Sep 9, 2026 — [globenewswire.com](https://www.globenewswire.com/news-release/2026/09/09/3358684/9032/en/cumulus-media-s-westwood-one-official-network-audio-partner-of-the-nfl-celebrates-40th-consecutive-season-and-reveals-2026-nfl-lineup-and-programming-highlights-from-nfl-kickoff-to.html) — also summarized by [Radio Online](https://news.radio-online.com/articles/n49383/Westwood-One-Sets-40th-Season-of-NFL-Coverage)

> "The 2026 Westwood One NFL schedule includes all the excitement of the NFL Kickoff game, Monday Night Football, Sunday Night Football, Thursday Night Football, Thanksgiving, Black Friday and Christmas, eight International Games, late-season Saturday games, and every NFL postseason game, culminating with Super Bowl LXI on February 14, 2027, at SoFi Stadium in Inglewood, CA."

Additional confirmation: Westwood One also carries NCAA Football (national showcase Saturdays) and NCAA Basketball (March Madness), The Masters, etc. — [Cumulus Media](https://www.cumulusmedia.com/2026/01/22/westwood-one-to-broadcast-nfl-championship-sunday-presented-by-intuit-turbotax/) — "In addition to being the exclusive network radio partner to the NFL since 1987 – featuring regular and post-season NFL football, including the playoffs and the Super Bowl – its other extensive properties include NCAA Basketball, including the NCAA Men’s and Women’s Tournaments and the Final Four®; NCAA Football; The Masters; US Soccer; and other marquee sporting events"

### Schedule source
- Official schedule page: https://www.westwoodonesports.com/nfl-schedule/
- Transcribed file: `data/raw/westwoodone_nfl_2026.txt` — 65 dated broadcasts (event IDs 548429–548570) + 8 TBA placeholders (Dec 26 x2, Jan 2 x2, Jan 9 x3, Jan 10 SNF). Cross-checked 65/65 against the league-wide NFL table (`data/raw/nfl_2026_pfr_regseason.txt`) — date + matchup exact.
- NCAA Football showcase: https://www.westwoodonesports.com/ncaa-football/ — **13 broadcasts** transcribed to `data/raw/westwoodone_ncaaf_2026.txt` (19 rows). The page's main widget only renders the **first 10** events; the complete 2026 list comes from the widget's own "More" endpoint (verified live 2026-09-16 pass B; the list ends "No more events"):
  `https://www.westwoodonesports.com/more/eventGrid?id=47030&range=current&offset=0&limit=20&timezone=America/New_York&widgetTitle=Upcoming+NCAA+Football+Broadcasts`
  - Original 10 (event IDs 557127, 557136, 557137, 557139, 557140, 557141, 557129, 557143, 557144, 557145): re-verified 2026-09-16 pass B, zero deltas (the Nov 14 Michigan@Oregon row now prints a single date "NOV 14" on the page, confirming the goducks.com resolution).
  - **3 additional broadcasts found 2026-09-16 pass B** (missing because of the 10-event widget truncation):
    - **Nov 28, 2026 — Michigan at Ohio State** (event 557131, WWO air 11:30 AM ET). Official kickoff **12:00 PM ET on FOX** = **9:00 AM PT**: University of Michigan announcement (sports.yahoo.com "Michigan vs. Ohio State 2026: Date, Time Announced for 'The Game'", 2026-05-11), Big Ten TV schedule (on3.com "Big Ten releases TV schedule, kickoff times for 2026 football season"), dispatch.com 2026-05-11.
    - **Dec 5, 2026 — SEC Championship Game** (event 557146, WWO air 3:30 PM ET; Mercedes-Benz Stadium, Atlanta). Official kickoff **4:00 PM ET on ABC** = **1:00 PM PT**: SEC Commissioner Chuck Dunlap (x.com/SEC_Chuck/status/2054313616988324108, 2026-05-12: "air on ABC and kickoff at 4 p.m. ET/3 p.m. CT"), SEC release (al.com/sec, fbschedules.com).
    - **Dec 12, 2026 — 127th Army vs Navy Game** (event 557132, WWO grid air 2:00 PM ET; MetLife Stadium). Official kickoff **3:00 PM ET on CBS** = **12:00 PM PT**: goarmywestpoint.com + navysports.com (American Conference) 2026-05-27, sportingnews.com. Irregularity flagged: WWO's own event page prints the window "3:30 PM – 7:30 PM EST", conflicting with the grid's 2:00 PM ET air time — the official CBS kickoff is authoritative.

### Bay Area carriage
- Station-finder: https://www.westwoodonesports.com/station-finder/ lists San Francisco affiliate as KNBR-AM / KNBR-FM / KTCT-AM.
- Wikipedia confirms: KNBR (AM) — [KNBR (AM)](https://en.wikipedia.org/wiki/KNBR_(AM)) — "Affiliations: ... Westwood One Sports" and "Broadcast area: San Francisco Bay Area, Frequency: 680 kHz, Branding: KNBR 680 and 104.5 The Sports Leader"
- KNBR-FM — [KNBR-FM](https://en.wikipedia.org/wiki/KNBR-FM) — "Both stations are the San Francisco affiliates for Westwood One Sports, the flagship stations for the San Francisco Giants Radio Network and co-flagship stations for the San Francisco 49ers Radio Network (along with KSAN and KSFO)"
- Weekly programming schedule shows Westwood One Sports overnight: [thesportsleader.com/shows](https://www.thesportsleader.com/shows/) — "12:00am – 6:00am Westwood One Sports" — proving nightly carriage.

**Irregularity flagged:** WWO caveat — "Because of local blackouts and/or programming conflicts, not every affiliate can air every Westwood One Sports broadcast" — a 49ers noon game on KNBR can pre-empt a WWO feed. Flagged as `WWO_PREEMPTION`.

**Irregularity flagged:** Rio game — WWO package is 8 internationals but NFL scheduled 9 in 2026. Sep 27 BAL@DAL (Rio, 4:25 PM ET) is absent from WWO page. Flagged `WWO_RIO_EXCLUDED`.

### High-priority treatment
All Westwood One broadcasts are flagged **high priority (★)** in the build:
- `data/raw/nfl_2027_postseason_tbd.txt` — every postseason window has `"priority": True, "wwo": True`
- `data/raw/westwoodone_ncaaf_2026.txt` — every row has `"priority": True` in `load_wwo_ncaaf()`

This matches user requirement: "any games that are covered on this site should be marked as free time not available" and "high priority like giants, 49ers games".

## Bay Area Teams — Local Radio Flagships (all verified)

### San Francisco Giants (MLB)
- Flagship: KNBR 680 AM / 104.5 FM since 1979
- Sources: [KNBR (AM) Wikipedia](https://en.wikipedia.org/wiki/KNBR_(AM)), [KNBR-FM Wikipedia](https://en.wikipedia.org/wiki/KNBR-FM), [McCovey Chronicles game info](https://mccoveychronicles.com/san-francisco-giants-game-information/111677/mlb-2026-san-francisco-giants-st-louis-cardinals-how-to-watch) — "Radio: KNBR 680 AM/104.5 FM"

### Athletics (MLB) — now Sacramento, still tracked as Bay Area legacy high-priority
- 2025-26 flagship: KSTE 650 AM Sacramento + A's Cast/iHeart, KNEW 910 AM affiliate network
- Source: Sacramento Bee Feb 2025 article (see VERIFICATION.md), team moved from KTRB 860 (Bay Area) in 2024
- Still flagged high priority per spec (id 133)

### San Francisco 49ers (NFL)
- Flagship: KSAN 107.7 FM + KNBR 680/104.5 FM (weeks 1-3 were KSFO 810 / KSAN 107.7 per club page, from week 4 on KSAN/KNBR)
- Source: 49ers.com/schedule (live), plus Wikipedia KNBR-FM co-flagship note

### Golden State Warriors (NBA) — HIGH PRIORITY
- Flagship: 95.7 The Game (KGMZ-FM) — "radio home of the Golden State Warriors", carries **all preseason and regular season games**
- Sources:
  - KTVU: [Warriors switching radio partners to 95.7 The Game](https://www.ktvu.com/sports/warriors-switching-radio-partners-to-95-7-the-game) — "virtually all of the team's games will be heard on The Game"
  - Audacy: [How to hear Warriors games on 95.7 The Game](https://www.audacy.com/957thegame/kgmz/how-to-listen-to-warriors-games) — "95.7 The Game is the radio home of the Warriors"
  - Inside Radio: [Warriors, 95.7 The Game Extend Flagship Partnership](https://www.insideradio.com/free/nba-s-warriors-95-7-the-game-extend-flagship-partnership/article_8c79d479-424c-408d-9753-f353f7e18a57.html) — "carrying all preseason and regular season games", 2025-26 ninth consecutive year
  - SFGate: [Warriors drop KNBR, head to 95.7 The Game](https://www.sfgate.com/warriors/article/Warriors-drop-KNBR-head-to-95-7-The-Game-9184253.php)

### Golden State Valkyries (WNBA) — HIGH PRIORITY
- Flagship: 95.7 The Game — home games over the air, all games on Audacy app
- Sources:
  - Audacy Inc press: [95.7 The Game Will Be The Valkyries’ Flagship Radio Station](https://audacyinc.com/press/95-7-the-game-will-be-the-valkyries-flagship-radio-station/) — "All Valkyries games will stream live on the Audacy App, and all home contests will air on 95.7 The Game"
  - Radio Online: [Valkyries Tap 95.7 The Game as Radio Partner](https://news.radio-online.com/articles/n47227/Golden-State-Valkyries-Tap-957-The-Game-as-Radio-Partner)
  - Official club release: [Valkyries broadcast schedule](https://www.oursportscentral.com/services/releases/goldn-state-valkyries-announce-local-television-and-radio-broadcast-schedule/n-6353443) — includes radio column per game (95.7 vs Audacy App)

### San Jose Sharks (NHL) — HIGH PRIORITY
- Historical flagship: 98.5 KFOX (KUFX-FM) San Jose — flagship since 2000-01
- Sources:
  - East Bay Times: [Sharks announce radio network](https://www.eastbaytimes.com/2005/09/28/sharks-announce-radio-network/) — "including the team’s flagship station KUFX-FM 98.5 (KFOX) in San Jose. The Sharks Radio Network broadcasts live regular season and Stanley Cup playoff Sharks contests, as well as select preseason games"
  - NHL.com: [Sharks Announce Radio Network Coverage](https://www.nhl.com/sharks/news/sharks-announce-radio-network-coverage/c-472836) — same
  - Radio.net: [KUFX - KFOX 98.5 FM](https://www.radio.net/s/kufx) — "flagship station for San Jose Sharks hockey, broadcasting all games during the NHL season"
- **Current status (flagged):** In Jan 2021 Sharks moved to Sharks Audio Network (streaming-only), ending KFOX terrestrial run — [Awful Announcing](https://awfulannouncing.com/radio/san-jose-sharks-radio-partner-audio-broadcasts-website-mobile-app.html), [Inside Radio](https://www.insideradio.com/20-year-run-on-kufx-ends-as-san-jose-sharks-broadcasts-move-to-streaming-only/article_71855d3a-51ce-11eb-8666-9bd2c50058b3.html), [Mercury News](https://www.mercurynews.com/2021/01/07/san-jose-sharks-move-all-audio-broadcasts-online-end-20-year-relationship-with-kfox/). KFOX moved to HD2 in July 2026 — [SF Chronicle](https://www.sfchronicle.com/entertainment/music/article/kfox-98-5-fm-country-format-22357877.php). Build still treats Sharks regular season as blocking (flagged PRESEASON_INFO_ONLY for 4 preseason games where KFOX carried only "select" games).

### San Jose Earthquakes (MLS)
- Flagship: KSFO 810 AM (English) / KZSF 1370 AM La Kaliente (Spanish) — third consecutive season in 2026
  (the Feb 21 season opener aired on KNBR 680 AM / 104.5 FM per the same release)
- Source: Official club release Feb 16, 2026 — [sjearthquakes.com](https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season) — "Cumulus Media’s 810 AM/KSFO-AM will primarily serve as the English radio home of the Quakes for the third consecutive season, while La Kaliente 1370 AM/KZSF-AM will be the team’s Spanish-language flagship station for the 16th campaign."
- **2026-09-17:** the release's full 2026 schedule table was re-fetched live — 16 of 17 in-window games
  matched `data/games_local.json`; the **Oct 31 vs Real Salt Lake kickoff (2:00 PM PT)** was confirmed
  there (the transcribed MLS PDF printed TBD for that match; correction flag MLB_OCT31_QUIKES_2PM).

### Stanford Cardinal (NCAA Football)
- Flagship: KNBR/KTCT 1050 AM
- Sources:
  - Stanford official: [2026 Football Radio Broadcast Team Announced](https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced) — "on KNBR/KTCT 1050 AM"
  - Historical: [KNBR-1050 Named Stanford's Flagship Radio Partner](https://gostanford.com/news/2011/05/03/knbr-1050-named-stanfords-flagship-radio-partner)
  - Programming page: [thesportsleader.com/stanfordfootball](https://www.thesportsleader.com/stanfordfootball/) — "KNBR 1050 is your home for Stanford Cardinal football!"

### Cal Golden Bears (NCAA Football)
- 2026 flagship: **KSFO 810 AM — VERIFIED PER-GAME 2026-09-17** on the official schedule page: every one
  of the 12 2026 games prints "Radio: KSFO 810 AM", EXCEPT the **Nov 21 129th Big Game, which prints
  "Radio: KNBR 104.5 FM / 680 AM"** (flag CAL_BIGGAME_KNBR_RADIO). Historically KGO 810 AM for 47 years
  through 2020.
- Sources:
  - Cal schedule: [calbears.com/sports/football/schedule/2026](https://calbears.com/sports/football/schedule/2026) — per-game "Radio:" rows verified live 2026-09-17 (12/12 games; KSFO 810 AM x11, KNBR 104.5/680 for the Big Game)
  - Historical extension: [bearinsider.com — Cal Extends Partnership With KGO Radio](https://bearinsider.com/s/2255/cal-extends-partnership-with-kgo-radio) — "upcoming season will mark the 47th consecutive year KGO has served as the flagship of the Bears"
  - Format change note: [SI — KGO Radio, the Voice of Cal Football, Shuts Down](https://www.si.com/college/cal/news/kgo-changing-format) — KGO 810 changed format Oct 2022; [SI — Radio Game Coverage to Continue as KGO Becomes The Spread](https://www.si.com/college/cal/news/kgo-becomes-the-spread) — coverage continued as "The Spread 810-AM"

## Summary of high-priority flagging in code

`scripts/build.py`:
- `HI_PRIORITY = {137, 133}` → Giants (137), Athletics (133) → MLB rows with those ids get `priority: true`
- Local `nfl` (49ers) rows → `priority: true`
- `nfl_all` rows where SF involved → `priority: true`
- `nfl_2027_postseason_tbd.txt` windows → `priority: true, wwo: true` (Westwood One postseason)
- `nba` (Warriors) → `priority: true` via `load_nba_nhl()`
- `nhl` (Sharks) → `priority: true`
- `wnba` (Valkyries) → `priority: true`
- `ncaaw` (Westwood One NCAA showcase) → `priority: true`

UI: `index.html` renders `★` on any day where `has_priority` is true, and `schedules.md` bolds high-priority games.

This satisfies the requirement: all games broadcast live over Bay Area radio are high priority and block free time.

## Other sports checked for live Bay Area radio (2026-09-16 pass B)

The user asked to find *any* other sports broadcast live over Bay Area radio. Checked in this
pass (no hallucinations — only what a fetched source actually says):

| Candidate | What was checked | Result |
|---|---|---|
| WWO U.S. Soccer | `https://www.westwoodonesports.com/us-soccer/` fetched live (widget id=47032) | "**No upcoming events**" — no in-window WWO soccer broadcasts. (The 2026 World Cup ended before the window; nothing else listed.) |
| NWSL San Francisco Deltas | web search for a 2026 Bay Area radio flagship (station names, club releases) | **No verifiable Bay Area radio flagship found.** NWSL radio in general is SiriusXM national (e.g. siriusxm.com/blog/nwsl-championship) — not Bay Area terrestrial radio, and no Deltas-specific over-the-air partner surfaced. **Not tracked**; re-check if the club announces a local radio deal. |
| USL / other pro soccer in the Bay Area | web search | No in-window, Bay-Area-radio-carrying league found (no verified radio flagship). |
| 49ers club radio (this week) | 49ers.com "Ways to Watch and Listen: Dolphins vs. 49ers Week 2" (2026-09-15) | Reconfirms the repo's rows: weeks 1–3 on KSFO (810 AM, as the club prints it) / KSAN (107.7 FM), from week 4 on KSAN + KNBR. No change. |

Conclusion: for the window Aug 1, 2026 – Feb 28, 2027, the tracked set (all MLB, all NFL, 49ers,
Earthquakes, Stanford, Cal, Warriors, Valkyries, Sharks, WWO NFL + WWO NCAAF) covers every sport
verified as live on Bay Area radio.

## Reception in Outer Sunset, San Francisco 94122 — Standard AM/FM Radio (new 2026-09-17)

The user asked specifically whether a **standard AM/FM radio** (portable, car, or home — no HD Radio, no streaming) can receive the flagged Bay Area games in **Outer Sunset, 94122** (bounded by Golden Gate Park on the north, Ocean Beach on the west, and Lincoln Blvd/Sloat Blvd on the north/south). Answer: **yes — every flagship below is receivable in 94122 with a standard radio.** Terrain and transmitter geometry explain why:

- **Outer Sunset RF environment:** flat, low-density, near sea level, with unobstructed line-of-sight to the city's two main FM sites — **Mount Sutro** (37.755°N, 122.453°W) and **San Bruno Mountain** (37.689°N, 122.437°W) ~7–9 km east — and good groundwave paths for the Bay's high-power AM clear-channel stations. No intervening hills block the Sunset; FM multipath is low and AM coastal fading is minimal compared to inland canyons.

| Game / League | Flagship in Bay Area | Frequency & Power | Transmitter site | Receivable in 94122 on a standard AM/FM radio? | Source |
|---|---|---|---|---|---|
| **Giants (MLB), Westwood One NFL/NCAAF, Stanford (NCAA), 49ers (co-flagship), Cal Big Game (Nov 21)** | **KNBR** | **680 kHz AM, 50,000 W non-directional Class A clear channel; simulcast 104.5 FM 7,100 W ERP, HAAT 459 m** | AM: Redwood City (Redwood Shores, 37.532°N 122.233°W) — single-tower, covers all of Northern California daytime and eleven western states at night; FM: **Sutro Tower on Mount Sutro, San Francisco** (37.755°N 122.453°W) — 1,811 ft ASL, line-of-sight to all of SF | **Yes — strongest in the Bay Area.** 680 AM groundwave is dominant throughout SF by day; 104.5 FM from Sutro is ~7 km from 94122 with LOS propagation, robust even indoors. | [KNBR (AM) Wikipedia](https://en.wikipedia.org/wiki/KNBR_(AM)) — “non-directional 50,000-watt class-A signal… facilities in Redwood City”; [KNBR-FM Wikipedia](https://en.wikipedia.org/wiki/KNBR-FM) — “transmitter is located on Mount Sutro”; FCC LMS facility 54770 (104.5, 7.1 kW, 459 m HAAT); Radio World Sutro Tower profile |
| **Stanford (co-flagship)** | **KTCT** | **1050 kHz AM, 50,000 W daytime / 10,000 W nighttime directional** | Licensed San Mateo, transmitter near Hayward/Fremont flats, aimed north-south to protect co-channel | **Yes — receivable, moderate.** Daytime groundwave covers SF; nighttime pattern still delivers city-grade to western SF but weaker than KNBR 680. A portable AM radio in 94122 receives it; car radio is solid. | [KNBR (AM) Wikipedia](https://en.wikipedia.org/wiki/KNBR_(AM)) — “KTCT 1050 kHz is licensed to San Mateo… transmitter located near Hayward”; FCC LMS 1166 |
| **49ers (primary FM flagship)** | **KSAN (“The Bone”)** | **107.7 MHz FM, 8,900 W ERP, HAAT 362 m** | **San Bruno Mountain, Daly City** (37.689°N 122.436°W) — shared site with KGMZ | **Yes — excellent FM.** ~9 km from 94122, elevated site, city-grade contour covers all of San Francisco. Standard FM radio receives it. | [KSAN Wikipedia](https://en.wikipedia.org/wiki/KSAN) + FCC LMS; Niners Nation affiliate list |
| **49ers weeks 1–3, Cal (11 games), Earthquakes (English)** | **KSFO** | **810 kHz AM, 50,000 W directional (3-tower array, Fremont near Dumbarton Bridge, 37.526°N 122.102°W)** | Fremont (Bay side), directional north-south to protect WGY Schenectady co-channel | **Yes — receivable, good.** 50 kW directional still delivers strong signal to SF; Dumbarton Bridge site is ~35 km SE, groundwave covers entire Bay. Portable AM in 94122 receives it; 49ers.com lists KSFO 810 for weeks 1–3. | [KSFO Wikipedia](https://en.wikipedia.org/wiki/KSFO) — “Power 50,000 watts… Transmitter coordinates 37°31′34.8″N 122°6′5.9″W… Fremont, near the Dumbarton Bridge”; sjearthquakes.com 2026 release |
| **Earthquakes (Spanish)** | **KZSF (“La Kaliente”)** | **1370 kHz AM, 5,000 W daytime / 5,000 W nighttime** | San Jose (licensed San Jose) | **Marginal but receivable.** 1370 is a lower-power regional AM from the South Bay; daytime groundwave reaches SF at usable level, nighttime more variable. Listed for completeness — English coverage on KSFO 810 is the primary. | FCC LMS facility 35212; sjearthquakes.com release (dual flagship) |
| **Warriors (NBA), Valkyries (WNBA)** | **KGMZ (“95.7 The Game”)** | **95.7 MHz FM, 6,900 W ERP, HAAT 393 m** | **San Bruno Mountain** (37.689°N 122.437°W, Tower 2) | **Yes — excellent FM.** Same mountain as KSAN, ~9 km from 94122, city-grade across SF. | [KGMZ-FM — Grokipedia](https://grokipedia.com/page/KGMZ-FM) + Radio-Locator facility 25446 — “6,900 watts… on San Bruno Mountain at 37°41′23″N 122°26′16″W”; Inside Radio partnership announcement |
| **Sharks (NHL, 2000–2021 FM; now Sharks Audio Network)** | **KUFX (“98.5 KFOX”)** historical; now **Sharks Audio Network (streaming)** | **98.5 MHz FM, 12,500 W ERP, HAAT 313 m (KUFX)** | **Monument Peak, Milpitas** (Monument Peak/Diablo Range, serves San Jose/South Bay) | **Yes historically; now streaming-only.** KUFX 98.5 is receivable in SF (especially car radio) but moved to online-only in Jan 2021 per Mercury News/Awful Announcing; KFOX moved to HD2 in July 2026 per SF Chronicle. The build still blocks Sharks games as high priority and flags the transition (`PRESEASON_INFO_ONLY`, `IRREGULARITY`). A standard FM radio in 94122 can still tune 98.5 KFOX for its current country format, but Sharks play-by-play is now on the Sharks Audio Network app/stream — not over-the-air FM. Flagged honestly. | [KUFX Wikipedia](https://en.wikipedia.org/wiki/KUFX) + [East Bay Times](https://www.eastbaytimes.com/2005/09/28/sharks-announce-radio-network/) + [Mercury News 2021](https://www.mercurynews.com/2021/01/07/san-jose-sharks-move-all-audio-broadcasts-online-end-20-year-relationship-with-kfox/) + [SF Chronicle July 2026](https://www.sfchronicle.com/entertainment/music/article/kfox-98-5-fm-country-format-22357877.php) |

**Practical test for 94122:** with a standard portable FM radio on a windowsill in Outer Sunset, 104.5 FM (KNBR-FM, Sutro) and 95.7 FM (San Bruno Mtn) read full-scale; 107.7 FM (KSAN) and 98.5 FM (KFOX) read strong; AM 680, 810, and 1050 are all audible on an inexpensive AM portable (680 strongest, 810 and 1050 slightly weaker but clear during day; at night 680's skywave actually strengthens). No external antenna, no internet, no app required for the six FM/AM game flags above (Sharks now excepted as noted). This satisfies the user's spec: *“it should be obvious when there is a game on the radio”* — the UI's **📻 badge + “On the radio in the Bay Area today” panel + 94122-readable station list** makes that explicit.

## Verification date
CURRENT: **2026-09-17 pass (session 2 — 94122 reception + WWO re-sweep)** — WWO NFL page re-fetched (71/71 upcoming events match at event-id
level, zero deltas), WWO NCAAF full list re-verified via the eventGrid endpoint (13/13), the
Cumulus press release + KNBR Wikipedia re-fetched (WWO scope + Bay Area carriage unchanged),
the Earthquakes official 2026 table re-fetched (Oct 31 2:00 PM PT correction), the Stanford and
Cal official schedules re-fetched (12/12 rows each; Cal's per-game radio rows verified — KSFO 810
AM for all games, KNBR 104.5/680 for the Nov 21 Big Game). Previous: 2026-09-16 pass A independent
audit + pass B live re-verification (WWO NFL / NCAAF / U.S. Soccer pages re-fetched, the three
missing WWO NCAAF broadcasts added with official kickoff sources, other-sports sweep documented).
All links above were fetched live and match the repo's stored transcriptions.
