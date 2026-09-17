# Limitations and Next Steps

This file answers the user's request: "Make suggestions for what work still needs to be done and any limitations that is in the way of a successful project. It should be worked on in this next session or the next session."

## Current status (2026-09-17 — two parallel verification passes, A + B, both merged)

- **MLB 2026 postseason resolution (new, 2026-09-17):** 4 of 12 berths are OFFICIALLY clinched per the
  mlb.com tracker (Rays 9/11, Brewers 9/11 + NL Central 9/15, Dodgers 9/14 + NL West 9/17, Yankees 9/14)
  and the current projected bracket is recorded in `data/raw/mlb_2026_postseason_resolution.txt`
  (projections labeled "as of 2026-09-17, NOT final"). The build attaches these notes to the 53 TBD
  placeholder rows and the day view shows the playoff picture for Sep 29 – Oct 31. **All 53 kickoff
  times remain officially TBD** (Stats API 07:33:00Z placeholders, re-verified live 2026-09-17).
- **Earthquakes correction (2026-09-17):** Oct 31 vs Real Salt Lake is 2:00 PM PT per the official club
  radio release (the transcribed PDF printed TBD) — row fixed (flag MLB_OCT31_QUIKES_2PM).
- **Radio visibility (new, 2026-09-17):** the day view has a "📻 On the radio in the Bay Area today"
  panel + per-game station badges (a `radio` field on 361 games: KNBR family, KSFO 810, KZSF 1370,
  KSAN 107.7, 95.7 The Game, KFOX/online); Cal's per-game radio rows verified (KSFO 810 for all games,
  KNBR 104.5/680 for the Nov 21 Big Game). A new UI invariant test (`scripts/ui_logic_test.js`, executed
  by the build) re-proves the football-day bug fix against the generated data AND the shipped JS.
- Window: Aug 1, 2026 – Feb 28, 2027 (212 days) in America/Los_Angeles (PDT through Oct 31, 2026, then PST)
- Data: 778 MLB regular-season games (all 30 clubs, 58 dates), 53 MLB postseason TBD placeholders
  (DATES now official + verified at gamePk level vs mlb.com/postseason on 2026-09-17; every start
  time still TBD; 54 estimated first-pitch windows from the documented 2025 postseason pattern;
  4 of 12 spots clinched - Rays, Brewers, Dodgers, Yankees; **Giants + Athletics ELIMINATED, so no
  Bay Area MLB club plays in October**; see data/raw/mlb_2026_playoff_picture.json; projected bracket + clinches also in data/raw/mlb_2026_postseason_resolution.txt, attached to the day view as playoff_note), 272 NFL regular-season games (all 32 clubs, 17 per team), 49 NFL preseason games (all times transcribed), 25 NFL postseason/Saturday/Wk18 window rows (1 official SB LXI 3:30 PM PT, 24 estimated), 61 local blocking games (49ers 20 incl. 3 preseason, Earthquakes 17 incl. Decision Day finale Nov 7 — Oct 31 vs RSL corrected to 2:00 PM PT by the official club radio release (pass A), Stanford 12, Cal 12), 63 Warriors (6 pre + 57 reg), 68 Sharks (4 pre info-only + 64 reg), 16 Valkyries regular season (9 on 95.7 The Game = blocking, 7 Audacy-app-only = info-only) + 3 playoff TBD + 37 conditional day markers (MLS playoffs, ACC/CFP/bowls, WNBA later rounds), 65 Westwood One NFL broadcasts matched 65/65 to league table + 8 TBA placeholders, **13 Westwood One NCAA football broadcasts** (19 rows: 7 with confirmed-or-reported official kickoffs — including the Nov 28 Michigan@Ohio State, Dec 5 SEC Championship and Dec 12 Army-Navy games found in pass B via the page's eventGrid endpoint — and 12 estimated showcase slots for the 6 still-TBD Saturdays).
- Build: `python3 scripts/build.py` → `data/processed/free_time.json` + `schedules.md` + verification report. `scripts/audit.py` independently recomputes everything and passes (212 days, 1481 day-view rows; new checks 11/11b/11c/11d/12/12b/12c cover the postseason EST windows and the playoff picture), and `scripts/ui_logic_test.js` (added in pass A, executed on every build) re-proves the football-day bug fix against the SHIPPED index.html helpers. 361 games now carry a `radio` field (Bay Area flagship station; see the radio panel in the UI).
- **Free-time rule (fixed in pass B after the user saw free time on football days; re-proven 2026-09-17 by the new UI invariant test):** a day whose status is NOT FREE — TIME TBD (a tracked game will definitely play/air, kickoff not official) or UNCONFIRMED (conditional markers) reports **no free time at all** — no free windows, no free minutes (Free min = 0 means "not asserted"), no green bands in the UI. Free time is asserted only on the 145 FREE/PARTIAL days. Status counts: 21 FREE, 124 PARTIAL, 45 NOT FREE — TIME TBD, 22 UNCONFIRMED, 0 FULLY BOOKED; 162 flags.- UI: scoreboard day view with Yesterday/Today/Tomorrow buttons (and ← → arrow keys), 24-hour timeline with red blocks (games) and green free bands, exact free windows (e.g. `12:00 AM – 10:05 AM (10h 5m)`), month calendar color-coded fully-free / partial / booked / not-free-TBD / unconfirmed with free hours per cell and ★ on high-priority days, league toggles and editable durations that recompute instantly, flag panel grouping every irregularity.
- Verification: All sources documented in `docs/VERIFICATION.md` §1 with links for manual review; durations researched in `docs/DURATION_RESEARCH_2026.md`; Bay Area radio research in `docs/BAY_AREA_RADIO_RESEARCH.md`.

## Known limitations (honest)

1. **Estimated windows are estimates.** NFL postseason/Saturday/Wk18 windows, WWO college showcase slots and - new 2026-09-17 - the 54 MLB postseason first-pitch slots use documented patterns (2025-26 NFL kickoffs, the actual 2025 MLB postseason start times, WWO air times, league Saturday windows), not official 2026-27 times. CAVEAT for MLB: the 2026 Wild Card round moves from ESPN/ABC to NBC/Peacock, so 2026 times may differ from the 2025 pattern. They are hatched + EST-tagged everywhere and replaced by real times as soon as announced. Re-run after Jan 3, 2027 slate, mid-December Saturday selection, and 6-12 days before each college game.

2. **Pro Bowl date conflict.** Feb 7 (sportbusy.com) vs Feb 9, 2027 (nflplayoffpass.com: "moved into Super Bowl week, Tuesday Feb 9, 8 PM ET"). No official NFL release. Both candidate days block with estimated windows and `PROBOWL_CONFLICT` flag. Remove loser once NFL announces.

3. **Flex scheduling.** NFL can move Sunday 1:00/4:05/4:25 PM ET games ~12 days ahead (125 games after 2026-09-11 in our rows). Flagged `FLEX_WINDOW`. 49ers.com re-checked weekly, but future SF games could be pulled to SNF.

4. **MLB rain postponements / rescheduling.** Times can move. Re-run `scripts/build.py` against fresh raw files; build prints arithmetic so silent drift fails checks.

5. **Durations are averages.** Real games run -30/+60 min (extra innings, overtime, weather delay). For past dates you can measure true overlap from `result` fields. WNBA default 125 min vs measured 128.2 min early 2026 — over-blocks slightly; edit sidebar if tighter fit needed.

6. **"Free" definition.** Means no listed game from blocking leagues is on air. Pre-game hype, watch parties, halftime overrun not modelled except via average duration (editable). Buffers default to 0.

7. **Conditional days.** MLS playoff windows (Nov 18 – Dec 18) depend on Earthquakes qualifying; ACC title Dec 5 + CFP days Dec 18 – Jan 25 depend on Stanford/Cal qualifying; WNBA later rounds depend on Valkyries advancing; Stanford/Cal bowls (Dec 12 – Jan 1) assigned after Selection Day Dec 6, 2026. Those days stay UNCONFIRMED and assert no free time at all (pass B). Note Dec 5 now also has the WWO SEC Championship (confirmed 1:00–4:24 PM PT block) on top of the ACC-title conditional marker.

8. **Sharks radio.** Historical flagship 98.5 KFOX (2000-2021) moved to Sharks Audio Network streaming-only Jan 2021. KFOX moved to HD2 July 2026 (Bay Country on 98.5 FM). Build still treats Sharks regular season as blocking on 98.5 KFOX history, but flagged `PRESEASON_INFO_ONLY` for 4 preseason games where KFOX carried only "select" games (unspecified). Warriors preseason all blocks (95.7 carries "all preseason and regular season games" per Inside Radio).

9. **Cal flagship.** KGO 810 carried Cal for 47 years through 2020, changed format Oct 2022 to The Spread (sports betting). 2026 schedule page now lists KSFO 810 AM for every game. Flagged but blocking unaffected (Cal games block regardless of flagship).

10. **Westwood One pre-emption.** KNBR can pre-empt any WWO feed due to local conflicts (e.g. 49ers noon game). Flagged `WWO_PREEMPTION`. Also WWO past broadcasts (Sep 9 Kickoff, Sep 10 Melbourne, Sep 13 SNF) are past-unverified — presumed per pattern but not individually verified on WWO page (JS-driven Past tab not fetchable). Flagged `WWO_PAST_UNVERIFIED`.

11. **WWO Rio excluded.** Sep 27 BAL@DAL (Rio) is 9th international but WWO package is 8 — absent from WWO page. Flagged `WWO_RIO_EXCLUDED`. Still blocks as NFL game.

12. **ESPN API limitations.** ESPN scoreboard JSON is ~25 chunks (odds/tickets embedded); rendered week-by-week pages (nfl.com by-week, PFR tables) used instead and agree wherever sampled. ESPN's API rejects date ranges through fetch proxy (single-date queries only).

## What still needs to be done — next session(s)

### Priority 1 — Refresh when official times drop (no code change, just data)
- [ ] **PARTIALLY DONE 2026-09-17 - finish after the MLB field is set (Sun Sep 27 -> Mon Sep 28, 2026):** dates + per-date counts + gamePks + TV networks are now official and verified (mlb.com/postseason); 4 of 12 spots clinched (Rays, Brewers, Dodgers, Yankees); Giants + Athletics eliminated. STILL TBD: all 53 start times and 8 team slots. When MLB announces Wild Card times (expected Mon-Tue Sep 28-29), re-run the MLB Stats API query `schedule?sportId=1&startDate=2026-09-28&endDate=2026-11-10`, replace the TBDxN rows with real games (keep the gamePk mapping in the file header), drop the EST rows for dates that become official, and re-run build + audit. Also update `data/raw/mlb_2026_postseason_resolution.txt` (clinches + projected bracket, shown in the day view as playoff_note) as more teams clinch and the bracket solidifies through Sep 27.- [ ] **After NFL flex schedule drops (Tuesdays):** Re-transcribe `data/raw/nfl_2026_pfr_regseason.txt` from PFR + nfl.com by-week pages (esp. weeks 16-18). Re-run build.
- [ ] **After Decision Day Nov 7, 2026:** If Earthquakes qualify, replace conditional MLS playoff windows (`data/raw/mls_2026_playoffs_conditional.txt`) with real dates/times from mlssoccer.com. If not, conditional markers disappear (day becomes FREE).
- [ ] **After bowl selection Sun Dec 6, 2026:** Add Stanford/Cal bowl games to `games_local.json` (currently deliberately not day-marked). Re-run build.
- [ ] **Mid-December 2026:** League names Wk-16/17 Saturday matchups (Dec 26, Jan 2) — replace estimated windows in `data/raw/nfl_2027_postseason_tbd.txt` with real games (2 games move off Dec 27 / Jan 3 Sunday slates). Also replace WWO TBA rows in `data/raw/westwoodone_nfl_2026.txt` once WWO names them.
- [ ] **After Jan 3, 2027 slate:** Real Wk-18 and playoff kickoffs replace estimated windows (re-transcribe PFR + nfl.com + ESPN events 401872910-921 + 401873270). Re-run build.
- [ ] **Weekly for WWO college:** Conferences announce kickoffs 6-12 days before each game — re-check https://www.westwoodonesports.com/ncaa-football/ **via its full eventGrid endpoint** (the page widget truncates at 10 events — see the URL in `docs/BAY_AREA_RADIO_RESEARCH.md` and the `WWO_NCAAF_EXPANDED` flag) and update `data/raw/westwoodone_ncaaf_2026.txt` (currently 6 still-TBD Saturdays each blocking two estimated slots + Nov 7 reported-not-official; Nov 28 / Dec 5 / Dec 12 are now official).
- [ ] **When NFL settles Pro Bowl date:** Remove losing day (Feb 7 vs Feb 9) from `nfl_2027_postseason_tbd.txt`.

### Priority 2 — Close known gaps
- [ ] **NEW (researched 2026-09-17) — Stanford men's basketball on KNBR 1050 AM:** the Cardinal Sports
      Network flagship carries ALL regular-season + postseason men's basketball games over the air
      (gostanford.com: "All Regular Season and Post-Season Men's Basketball Games") — that is ~30
      in-window games (Nov 2026–Feb 2027) on Bay Area radio that currently do NOT block. Transcribe
      from ESPN's team schedule pages exactly like the Warriors/Sharks passes (find the 2026-27
      Stanford MBB schedule URL on espn.com) + gostanford.com game-center times, add as a blocking
      high-priority league, and extend audit.py. Cal basketball: NO verified 2026-27 flagship found
      yet (KGO 810 carried Cal for 47 years through 2020; the football schedule page now lists
      KSFO 810) — verify at calbears.com BEFORE adding; do not assume.
- [ ] **NBA Cup and All-Star:** Warriors idle Dec 2-11 (NBA Cup window) and Feb 18-24 (All-Star break) — confirmed gaps, not missing rows. If you want Cup knockout or All-Star games to block, add them as conditional or blocking rows (currently deliberately not blocking — no Warriors game).
- [ ] **NHL postponements:** Re-transcribe ESPN team pages (`/nhl/team/schedule/_/name/sj/season/2027`) if Sharks schedule changes.
- [ ] **WNBA playoff radio carriage:** Per-game playoff radio carriage not published — currently blocks by date presuming Bay Area playoff game airs locally (flagged IRREGULARITY). Update `data/raw/wnba_valkyries_2026.txt` once club announces per-game radio split.
- [x] **Cal/Stanford radio (VERIFIED 2026-09-17):** Cal's 2026 schedule page prints "Radio: KSFO 810 AM" on all 12 games and "Radio: KNBR 104.5 FM / 680 AM" on the Nov 21 Big Game (per-game rows fetched live); Stanford 12/12 rows verified on gostanford.com. Re-check only if an official release changes a flagship.

### Priority 3 — Feature enhancements (code)
- [ ] **Add Westwood One NCAA Basketball (March Madness) for 2027 window extension:** If window extended past Feb 28 into March, add WWO NCAA Basketball (Final Four etc.) — currently out of scope.
- [ ] **Add buffer inputs:** Pre-game and post-game buffers currently 0 — UI already has inputs for durations, add buffers to sidebar (already in meta: pre_buffer/post_buffer).
- [ ] **Export free time:** Add "Export to Google Calendar / .ics" button that exports free windows as calendar events.
- [ ] **PST vs PDT label:** Currently shows "America/Los_Angeles - PDT through Oct 31, 2026; PST from Nov 1, 2026 to Mar 13, 2027" in meta. Add live label in UI header that shows current day's offset (PDT/PST) explicitly.
- [ ] **Notifications:** Add browser notification when free time changes after a refresh (e.g., after flex).
- [ ] **Mobile UX:** Calendar cells are small on mobile — improve tap targets and add swipe between days.
- [ ] **Accessibility:** Timeline currently uses color only — add patterns or labels for color-blind users.

### Priority 4 — Data automation (future)
- [ ] **Automate MLB Stats API fetch:** Currently hand-transcribed from API queries recorded in raw file headers. Build a script `scripts/fetch_mlb.py` that hits `https://statsapi.mlb.com/api/v1/schedule` and writes `data/raw/mlb_2026_regseason.txt` directly — requires handling UTC→PT conversion and placeholder times.
- [ ] **Automate NFL PFR fetch:** PFR tables are HTML — build scraper for `https://www.pro-football-reference.com/years/2026/games.htm` (regular season) and `.../preseason.htm`.
- [ ] **Automate Westwood One fetch:** WWO schedule page is JS-driven with 4 chunks and reCAPTCHA block — needs headless browser or API reverse-engineering (currently manual transcription with event IDs).
- [ ] **Automate ESPN NBA/NHL:** ESPN team pages are rendered HTML — scraper for `https://www.espn.com/nba/team/schedule/_/name/gs/season/2027` etc.

## Suggested next session agenda
1. **MLB postseason times drop after Sun Sep 27, 2026 (regular-season finale):** re-fetch
   mlb.com/postseason + the Stats API and replace the 53 TBDxN rows / 54 EST windows with real
   games + times (keep the gamePk mapping). This is the single biggest open item. NOTE: the
   Giants and Athletics are ELIMINATED — October will contain no Bay Area MLB club.
2. Re-run `python3 scripts/build.py` and `python3 scripts/audit.py` — confirm still PASS.
2. Check https://www.westwoodonesports.com/nfl-schedule/ and https://www.westwoodonesports.com/ncaa-football/ for any new air times — update raw files if changed. **For NCAAF, always use the widget's eventGrid endpoint** (the page only renders the first 10 events — that truncation is how three broadcasts were missed until 2026-09-16 pass B). For NFL, reconcile the page's two rendered lists (all upcoming events) plus the 8 TBA placeholders at event-id level.
3. Check 49ers.com/schedule, gostanford.com/sports/football/schedule, calbears.com/sports/football/schedule, sjearthquakes.com/news for any kickoff time announcements (especially the Oct/Nov Stanford + Cal TBDs that make Nov 28 and the other late-season days NOT FREE).
4. If any new times, replace in `data/raw/` and re-run build — audit should still PASS.
5. Re-check the WWO U.S. Soccer page (id=47032) if fall 2026 USMNT/USWNT windows are announced — "No upcoming events" as of 2026-09-16 pass B.
6. Re-check whether the NWSL San Francisco Deltas announce a Bay Area over-the-air radio partnership (none found 2026-09-16; NWSL radio is SiriusXM national) — if so, add as a high-priority blocking league.
7. Review `docs/LIMITATIONS_AND_NEXT_STEPS.md` and pick one Priority 2 or 3 item to implement.

## No hallucinations — verification method
- Every game row keeps a source URL for manual review (see `data/raw/*.txt` headers and `data/games_local.json` source fields).
- Every duration has a citation with link (see `docs/DURATION_RESEARCH_2026.md` and `docs/VERIFICATION.md` §2).
- Every Bay Area flagship has a citation (see `docs/BAY_AREA_RADIO_RESEARCH.md`).
- Build prints verification report with per-team counts, doubleheaders, days with no games, fully booked days, flag totals — read it before trusting a refresh.
- Audit script independently recomputes everything from raw files and fails on any mismatch.
