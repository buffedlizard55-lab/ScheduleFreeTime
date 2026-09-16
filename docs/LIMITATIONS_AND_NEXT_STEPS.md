# Limitations and Next Steps

This file answers the user's request: "Make suggestions for what work still needs to be done and any limitations that is in the way of a successful project. It should be worked on in this next session or the next session."

## Current status (2026-09-17)

- Window: Aug 1, 2026 – Feb 28, 2027 (212 days) in America/Los_Angeles (PDT through Oct 31, 2026, then PST)
- Data: 778 MLB regular-season games (all 30 clubs, 58 dates), 53 MLB postseason TBD placeholders, 272 NFL regular-season games (all 32 clubs, 17 per team), 49 NFL preseason games (all times transcribed), 25 NFL postseason/Saturday/Wk18 window rows (1 official SB LXI 3:30 PM PT, 24 estimated), 61 local blocking games (49ers 20 incl. 3 preseason, Earthquakes 17 incl. Decision Day finale Nov 7, Stanford 12, Cal 12), 63 Warriors (6 pre + 57 reg), 68 Sharks (4 pre info-only + 64 reg), 16 Valkyries regular season (9 on 95.7 The Game = blocking, 7 Audacy-app-only = info-only) + 3 playoff TBD + 35 conditional day markers (MLS playoffs, ACC/CFP/bowls, WNBA later rounds), 65 Westwood One NFL broadcasts matched 65/65 to league table + 8 TBA placeholders, 10 Westwood One NCAA football broadcasts (16 rows with estimated showcase slots).
- Build: `python3 scripts/build.py` → `data/processed/free_time.json` + `schedules.md` + verification report. `scripts/audit.py` independently recomputes everything and passes (212 days, 1424 day-view rows).
- UI: scoreboard day view with Yesterday/Today/Tomorrow buttons (and ← → arrow keys), 24-hour timeline with red blocks (games) and green free bands, exact free windows (e.g. `12:00 AM – 10:05 AM (10h 5m)`), month calendar color-coded fully-free / partial / booked / not-free-TBD / unconfirmed with free hours per cell and ★ on high-priority days, league toggles and editable durations that recompute instantly, flag panel grouping every irregularity.
- Verification: All sources documented in `docs/VERIFICATION.md` §1 with links for manual review; durations researched in `docs/DURATION_RESEARCH_2026.md`; Bay Area radio research in `docs/BAY_AREA_RADIO_RESEARCH.md`.

## Known limitations (honest)

1. **Estimated windows are estimates.** NFL postseason/Saturday/Wk18 windows and WWO college showcase slots use documented patterns (2025-26 kickoffs, WWO air times, league Saturday windows), not official 2026-27 times. They are hatched + EST-tagged everywhere and replaced by real times as soon as announced. Re-run after Jan 3, 2027 slate, mid-December Saturday selection, and 6-12 days before each college game.

2. **Pro Bowl date conflict.** Feb 7 (sportbusy.com) vs Feb 9, 2027 (nflplayoffpass.com: "moved into Super Bowl week, Tuesday Feb 9, 8 PM ET"). No official NFL release. Both candidate days block with estimated windows and `PROBOWL_CONFLICT` flag. Remove loser once NFL announces.

3. **Flex scheduling.** NFL can move Sunday 1:00/4:05/4:25 PM ET games ~12 days ahead (125 games after 2026-09-11 in our rows). Flagged `FLEX_WINDOW`. 49ers.com re-checked weekly, but future SF games could be pulled to SNF.

4. **MLB rain postponements / rescheduling.** Times can move. Re-run `scripts/build.py` against fresh raw files; build prints arithmetic so silent drift fails checks.

5. **Durations are averages.** Real games run -30/+60 min (extra innings, overtime, weather delay). For past dates you can measure true overlap from `result` fields. WNBA default 125 min vs measured 128.2 min early 2026 — over-blocks slightly; edit sidebar if tighter fit needed.

6. **"Free" definition.** Means no listed game from blocking leagues is on air. Pre-game hype, watch parties, halftime overrun not modelled except via average duration (editable). Buffers default to 0.

7. **Conditional days.** MLS playoff windows (Nov 18 – Dec 18) depend on Earthquakes qualifying; ACC title Dec 5 + CFP days Dec 18 – Jan 25 depend on Stanford/Cal qualifying; WNBA later rounds depend on Valkyries advancing; Stanford/Cal bowls (Dec 12 – Jan 1) assigned after Selection Day Dec 6, 2026. Those days stay UNCONFIRMED — free time provisional, never asserted.

8. **Sharks radio.** Historical flagship 98.5 KFOX (2000-2021) moved to Sharks Audio Network streaming-only Jan 2021. KFOX moved to HD2 July 2026 (Bay Country on 98.5 FM). Build still treats Sharks regular season as blocking on 98.5 KFOX history, but flagged `PRESEASON_INFO_ONLY` for 4 preseason games where KFOX carried only "select" games (unspecified). Warriors preseason all blocks (95.7 carries "all preseason and regular season games" per Inside Radio).

9. **Cal flagship.** KGO 810 carried Cal for 47 years through 2020, changed format Oct 2022 to The Spread (sports betting). 2026 schedule page now lists KSFO 810 AM for every game. Flagged but blocking unaffected (Cal games block regardless of flagship).

10. **Westwood One pre-emption.** KNBR can pre-empt any WWO feed due to local conflicts (e.g. 49ers noon game). Flagged `WWO_PREEMPTION`. Also WWO past broadcasts (Sep 9 Kickoff, Sep 10 Melbourne, Sep 13 SNF) are past-unverified — presumed per pattern but not individually verified on WWO page (JS-driven Past tab not fetchable). Flagged `WWO_PAST_UNVERIFIED`.

11. **WWO Rio excluded.** Sep 27 BAL@DAL (Rio) is 9th international but WWO package is 8 — absent from WWO page. Flagged `WWO_RIO_EXCLUDED`. Still blocks as NFL game.

12. **ESPN API limitations.** ESPN scoreboard JSON is ~25 chunks (odds/tickets embedded); rendered week-by-week pages (nfl.com by-week, PFR tables) used instead and agree wherever sampled. ESPN's API rejects date ranges through fetch proxy (single-date queries only).

## What still needs to be done — next session(s)

### Priority 1 — Refresh when official times drop (no code change, just data)
- [ ] **After MLB postseason seeding (early Oct 2026):** Re-run MLB Stats API query `schedule?sportId=1&startDate=2026-09-28&endDate=2026-11-10` and replace `data/raw/mlb_2026_postseason_tbd.txt` — 53 placeholder rows become real times/teams. Re-run build.
- [ ] **After NFL flex schedule drops (Tuesdays):** Re-transcribe `data/raw/nfl_2026_pfr_regseason.txt` from PFR + nfl.com by-week pages (esp. weeks 16-18). Re-run build.
- [ ] **After Decision Day Nov 7, 2026:** If Earthquakes qualify, replace conditional MLS playoff windows (`data/raw/mls_2026_playoffs_conditional.txt`) with real dates/times from mlssoccer.com. If not, conditional markers disappear (day becomes FREE).
- [ ] **After bowl selection Sun Dec 6, 2026:** Add Stanford/Cal bowl games to `games_local.json` (currently deliberately not day-marked). Re-run build.
- [ ] **Mid-December 2026:** League names Wk-16/17 Saturday matchups (Dec 26, Jan 2) — replace estimated windows in `data/raw/nfl_2027_postseason_tbd.txt` with real games (2 games move off Dec 27 / Jan 3 Sunday slates). Also replace WWO TBA rows in `data/raw/westwoodone_nfl_2026.txt` once WWO names them.
- [ ] **After Jan 3, 2027 slate:** Real Wk-18 and playoff kickoffs replace estimated windows (re-transcribe PFR + nfl.com + ESPN events 401872910-921 + 401873270). Re-run build.
- [ ] **Weekly for WWO college:** Conferences announce kickoffs 6-12 days before each game — re-check https://www.westwoodonesports.com/ncaa-football/ and update `data/raw/westwoodone_ncaaf_2026.txt` (currently 8 TBD).
- [ ] **When NFL settles Pro Bowl date:** Remove losing day (Feb 7 vs Feb 9) from `nfl_2027_postseason_tbd.txt`.

### Priority 2 — Close known gaps
- [ ] **NBA Cup and All-Star:** Warriors idle Dec 2-11 (NBA Cup window) and Feb 18-24 (All-Star break) — confirmed gaps, not missing rows. If you want Cup knockout or All-Star games to block, add them as conditional or blocking rows (currently deliberately not blocking — no Warriors game).
- [ ] **NHL postponements:** Re-transcribe ESPN team pages (`/nhl/team/schedule/_/name/sj/season/2027`) if Sharks schedule changes.
- [ ] **WNBA playoff radio carriage:** Per-game playoff radio carriage not published — currently blocks by date presuming Bay Area playoff game airs locally (flagged IRREGULARITY). Update `data/raw/wnba_valkyries_2026.txt` once club announces per-game radio split.
- [ ] **Cal/Stanford radio:** Verify 2026-27 flagship announcements (Cal now KSFO 810 per schedule page, Stanford KNBR/KTCT 1050 per gostanford.com) — update `docs/VERIFICATION.md` flagship table if official release changes.

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
1. Re-run `python3 scripts/build.py` and `python3 scripts/audit.py` — confirm still PASS.
2. Check https://www.westwoodonesports.com/nfl-schedule/ and https://www.westwoodonesports.com/ncaa-football/ for any new air times — update raw files if changed.
3. Check 49ers.com/schedule, gostanford.com/sports/football/schedule, calbears.com/sports/football/schedule, sjearthquakes.com/news for any kickoff time announcements (especially Oct/Nov TBDs).
4. If any new times, replace in `data/raw/` and re-run build — audit should still PASS.
5. Review `docs/LIMITATIONS_AND_NEXT_STEPS.md` and pick one Priority 2 or 3 item to implement.

## No hallucinations — verification method
- Every game row keeps a source URL for manual review (see `data/raw/*.txt` headers and `data/games_local.json` source fields).
- Every duration has a citation with link (see `docs/DURATION_RESEARCH_2026.md` and `docs/VERIFICATION.md` §2).
- Every Bay Area flagship has a citation (see `docs/BAY_AREA_RADIO_RESEARCH.md`).
- Build prints verification report with per-team counts, doubleheaders, days with no games, fully booked days, flag totals — read it before trusting a refresh.
- Audit script independently recomputes everything from raw files and fails on any mismatch.
