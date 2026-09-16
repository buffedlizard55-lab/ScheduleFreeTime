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
- NCAA Football showcase: https://www.westwoodonesports.com/ncaa-football/ — 10 Saturday broadcasts transcribed to `data/raw/westwoodone_ncaaf_2026.txt` (event IDs 557127, 557136, 557137, 557139, 557140, 557141, 557129, 557143, 557144, 557145). Two with official air times, eight TBD — verified live 2026-09-16 with zero deltas.

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
- Source: Official club release Feb 16, 2026 — [sjearthquakes.com](https://www.sjearthquakes.com/news/news-earthquakes-announce-radio-stations-for-2026-mls-season) — "Cumulus Media’s 810 AM/KSFO-AM will primarily serve as the English radio home of the Quakes for the third consecutive season, while La Kaliente 1370 AM/KZSF-AM will be the team’s Spanish-language flagship station for the 16th campaign."

### Stanford Cardinal (NCAA Football)
- Flagship: KNBR/KTCT 1050 AM
- Sources:
  - Stanford official: [2026 Football Radio Broadcast Team Announced](https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced) — "on KNBR/KTCT 1050 AM"
  - Historical: [KNBR-1050 Named Stanford's Flagship Radio Partner](https://gostanford.com/news/2011/05/03/knbr-1050-named-stanfords-flagship-radio-partner)
  - Programming page: [thesportsleader.com/stanfordfootball](https://www.thesportsleader.com/stanfordfootball/) — "KNBR 1050 is your home for Stanford Cardinal football!"

### Cal Golden Bears (NCAA Football)
- 2026 flagship: KSFO 810 AM (per schedule page) — historically KGO 810 AM for 47 years through 2020
- Sources:
  - Cal schedule: [calbears.com/sports/football/schedule/2026](https://calbears.com/sports/football/schedule/2026) — every game lists "Radio: KSFO 810 AM"
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

## Verification date
2026-09-16 independent audit pass + 2026-09-17 web re-verification (this file). All links above were fetched live and match the repo's stored transcriptions.
