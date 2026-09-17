#!/usr/bin/env python3
"""
ScheduleFreeTime build + verification pipeline.

Reads ONLY the hand-transcribed, source-attributed raw data in data/raw/ and
data/games_local.json, then:
  1. converts every game to America/Los_Angeles time,
  2. blocks [start, start + average duration] per BLOCKING game,
  3. computes the free (no game on) windows for each day,
  4. writes data/processed/free_time.json (+ mlb.json),
  5. regenerates schedules.md (the full master list),
  6. prints a verification report and flags every irregularity it finds.

Blocking rule (user spec, corrected 2026-09-11, extended 2026-09-14 and 2026-09-15): a
day is busy around EVERY game the site tracks - any MLB game (ALL 30 clubs, regular
season + postseason 2026), ALL NFL games (all 32 clubs: preseason, regular season,
postseason, Pro Bowl, Super Bowl - TBD until confirmed), San Jose Earthquakes games,
Stanford football games, Cal football games, Golden State Warriors games (NBA, 95.7 The
Game flagship), San Jose Sharks games (NHL, 98.5 KFOX flagship) and the Westwood One
national-radio NCAA football showcase (Bay Area: KNBR).
(Fix history: the all-NFL layer was display-only until 2026-09-11 - it wrongly reported
free time on days when non-49ers NFL games were on air. On 2026-09-15 the rule was
extended again: every game broadcast by Westwood One - which per the Cumulus press
release includes EVERY postseason game, the Super Bowl and the late-season Saturday
doubleheaders/tripleheader - marks its day "free time NOT available" even when the
kickoff is still TBD: the day gets a NOT FREE - TIME TBD status and, where the window
is predictable from documented patterns, an ESTIMATED blocking window that is labeled
as an estimate everywhere. Week 18's PFR "Sunday 1:00 PM" times were placeholders and
are now stored as TBD exactly as nfl.com prints them; the 49 preseason games now carry
kickoff times and block.)

"Conditional" rows (MLS playoff days if SJ qualifies, ACC/CFP/bowl days if Stanford or
Cal qualify) never block; they mark a day UNCONFIRMED so free time is honestly labeled,
not asserted. Games with a TBD kickoff that have no predictable window (MLB postseason
placeholders, individual Stanford/Cal/Earthquakes TBD games) never fabricate a window -
they mark the day NOT FREE - TIME TBD. Westwood One NFL rows do not duplicate the league
table: each WWO broadcast is cross-checked against the matching all-NFL row and marked
wwo=true (national-radio badge).


No manual input: run `python3 scripts/build.py`.
"""
import json, os, re, subprocess, sys, glob
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")

# --- analysis window -------------------------------------------------------
START, END = date(2026, 8, 1), date(2027, 2, 28)
TODAY = date(2026, 9, 17)   # date of the 2026-09-17 re-verification pass
GENERATED = "2026-09-17"
# US Pacific in the window: PDT (UTC-7) Mar 8 2026 -> Nov 1 2026; PST (UTC-8)
# Nov 1 2026 -> Mar 14 2027. DST starts again Mar 14, 2027 (after END).
PDT = timedelta(hours=-7)
PST = timedelta(hours=-8)

def pt_offset(d):
    """America/Los_Angeles UTC offset for a calendar date in the window."""
    if date(2026, 3, 8) <= d < date(2026, 11, 1):
        return PDT
    if date(2026, 11, 1) <= d < date(2027, 3, 14):
        return PST
    return PDT   # (not reached inside this window)

# --- average game durations (minutes), researched averages ------------------
# Sources + citations in docs/VERIFICATION.md sec. 2:
#   mlb   164 = 2:44, 2026 season-to-date average (BetMGM 2026-08-31: "2:44";
#                SBJ 2026-04-29: 2:43 through the first 421 games). MLB's official
#                2025 final was 2:38 (158 min). Postseason runs longer (~3:04-3:15)
#                but postseason rows are TBD and do not block.
#   nfl   192 = 3:12, widely reported 2025 average incl. 12-min halftime & stoppages
#   ncaa  204 = 3:24 (longer 20-min halftimes; 2025 data ranges 3:24-3:27)
#   mls   120 = 2:00 (90 min + ~15-min halftime + stoppage)
#   nba   138 = 2:18, 2025-26 measured average 2:18:32 tip-to-buzzer (NBA official
#                game-ops dashboard via independent broadcast-timing audit); secondary
#                guides converge on ~2:15
#   nhl   150 = 2:30, midpoint of the reported 2:20-2:40 range (~2.5h typical incl.
#                two 18-min intermissions, media timeouts and stoppages)
#   wnba  125 = 2:05, midpoint of the reported ~2:00-2:10 range for a WNBA game
#                (40 min of play + 15-min halftime; basketballgem 2026-05-13 "~2 hr 10 min",
#                sportsmonkie 2026-07-27 "about two hours", gametimehero 2026-05-02
#                "1 hour 45 minutes to 2 hours")
DURATIONS = {"mlb": 164, "nfl": 192, "ncaa": 204, "mls": 120, "nba": 138, "nhl": 150, "wnba": 125}
DUR_OF = lambda sport: DURATIONS[{"nfl_all": "nfl", "ncaaw": "ncaa"}.get(sport, sport)]
PRE_BUFFER = 0   # minutes of pre-game coverage counted as busy
POST_BUFFER = 0  # minutes of post-game coverage counted as busy
BLOCKING_SPORTS = {"mlb", "nfl", "ncaa", "mls", "nfl_all", "nba", "nhl", "ncaaw", "wnba"}   # user's free-time rule: every tracked league blocks
NFL_TEAM_NAMES = {
 "ARI":"Cardinals","ATL":"Falcons","BAL":"Ravens","BUF":"Bills","CAR":"Panthers",
 "CHI":"Bears","CIN":"Bengals","CLE":"Browns","DAL":"Cowboys","DEN":"Broncos",
 "DET":"Lions","GNB":"Packers","HTX":"Texans","IND":"Colts","JAX":"Jaguars",
 "KAN":"Chiefs","LV":"Raiders","LAC":"Chargers","LAR":"Rams","MIA":"Dolphins",
 "MIN":"Vikings","NE":"Patriots","NO":"Saints","NYG":"Giants","NYJ":"Jets",
 "PHI":"Eagles","PIT":"Steelers","SEA":"Seahawks","SF":"49ers","TB":"Buccaneers",
 "TEN":"Titans","WAS":"Commanders"}
# PFR abbreviations used in the raw files map to canonical ones
ABBR_ALIAS = {"CRD":"ARI","RAI":"LV","SDG":"LAC","CLT":"IND","SFO":"SF","RAM":"LAR",
              "NOR":"NO","NWE":"NE","OTI":"TEN","RAV":"BAL","TAM":"TB"}
# Westwood One schedule page uses a mix of canonical + legacy abbrs; normalize the same way
WWO_ALIAS = {"NWE":"NE","RAM":"LAR","CLT":"IND","SFO":"SF","TAM":"TB","NOR":"NO",
             "RAV":"BAL","OTI":"TEN","SDG":"LAC","RAI":"LV","CRD":"ARI",
             "KC":"KAN","GB":"GNB"}
NBA_TEAM_NAMES = {
 "ATL":"Hawks","BOS":"Celtics","BKN":"Nets","CHA":"Hornets","CHI":"Bulls","CLE":"Cavaliers",
 "DAL":"Mavericks","DEN":"Nuggets","DET":"Pistons","GS":"Warriors","HOU":"Rockets",
 "IND":"Pacers","LAC":"Clippers","LAL":"Lakers","MEM":"Grizzlies","MIA":"Heat","MIL":"Bucks",
 "MIN":"Timberwolves","NO":"Pelicans","NY":"Knicks","OKC":"Thunder","ORL":"Magic",
 "PHI":"76ers","PHX":"Suns","POR":"Trail Blazers","SAC":"Kings","SA":"Spurs","TOR":"Raptors",
 "UTAH":"Jazz","WSH":"Wizards"}
def _bigname(abbr, names, bay_abbr, bay_full):
    return bay_full if abbr == bay_abbr else names.get(abbr, abbr)
NHL_TEAM_NAMES = {
 "ANA":"Ducks","BOS":"Bruins","BUF":"Sabres","CGY":"Flames","CAR":"Hurricanes","CHI":"Blackhawks",
 "COL":"Avalanche","CBJ":"Blue Jackets","DAL":"Stars","DET":"Red Wings","EDM":"Oilers",
 "FLA":"Panthers","LA":"Kings","MIN":"Wild","MTL":"Canadiens","NSH":"Predators","NJ":"Devils",
 "NYI":"Islanders","NYR":"Rangers","OTT":"Senators","PHI":"Flyers","PIT":"Penguins",
 "SJ":"Sharks","SEA":"Kraken","STL":"Blues","TB":"Lightning","TOR":"Maple Leafs",
 "UTAH":"Mammoth","VAN":"Canucks","VGK":"Golden Knights","WSH":"Capitals","WPG":"Jets"}

TEAMS = {t["id"]: t for t in json.load(open(os.path.join(RAW, "teams_mlb.json")))["teams"]}
HI_PRIORITY = {137, 133}  # SF Giants, Athletics

flags = []
def flag(kind, msg):
    flags.append({"kind": kind, "msg": msg})

# --- MLB -------------------------------------------------------------------
def load_mlb():
    games = []
    for path in sorted(glob.glob(os.path.join(RAW, "mlb_2026_*.txt"))):
        if os.path.basename(path) == "mlb_2026_postseason_resolution.txt":
            continue   # annotations about the placeholders, not a game schedule
        for ln, line in enumerate(open(path), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            d, body = line.split("|")
            y, m, dd = map(int, d.split("-"))
            off = pt_offset(date(y, m, dd))
            if body.startswith("TBDx"):
                n = int(body[4:])
                games.append({"date": d, "sport": "mlb", "start_pt": None, "start_min": None, "tbd_count": n,
                              "label": f"MLB postseason - {n} game(s), teams & times UNCONFIRMED",
                              "source": os.path.basename(path)})
                flag("TBD_TIME", f"{d}: {n} MLB postseason game(s) have no confirmed time or teams "
                                 f"(MLB Stats API returns placeholder 07:33:00Z + placeholder team ids)")
                continue
            for item in body.split(","):
                hhmm, matchup = item.split(":")
                h, mi = int(hhmm[:2]), int(hhmm[2:])
                away, home = map(int, matchup.split("-"))
                # HHMM is minutes from midnight UTC of the *officialDate*; >2400 = after midnight UTC
                utc = datetime(y, m, dd, tzinfo=timezone.utc) + timedelta(hours=h, minutes=mi)
                pt = utc + off
                for tid in (away, home):
                    if tid not in TEAMS:
                        flag("UNKNOWN_TEAM", f"{os.path.basename(path)}:{ln} unknown teamId {tid}")
                games.append({
                    "date": d, "sport": "mlb",
                    "start_pt": pt.strftime("%H:%M"),
                    "start_min": pt.hour * 60 + pt.minute,
                    "utc": utc.strftime("%Y-%m-%dT%H:%MZ"),
                    "pt_date": pt.strftime("%Y-%m-%d"),
                    "away": TEAMS.get(away, {}).get("abbr", str(away)),
                    "home": TEAMS.get(home, {}).get("abbr", str(home)),
                    "away_id": away, "home_id": home,
                    "label": f"{TEAMS.get(away,{}).get('name',away)} @ {TEAMS.get(home,{}).get('name',home)}",
                    "priority": any(t in HI_PRIORITY for t in (away, home)),
                    "source": os.path.basename(path),
                })
    return games

# --- NFL league-wide (all 32 clubs; LIST ONLY - does not block) ------------
def load_nfl_all():
    games = []
    # regular season: week|date|timeET|away|home|boxid|result
    path = os.path.join(RAW, "nfl_2026_pfr_regseason.txt")
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        wk, dt, t_et, aw, hm, box, res = (line.split("|") + [""])[:7]
        y, m, dd = map(int, dt.split("-"))
        aw2, hm2 = ABBR_ALIAS.get(aw, aw), ABBR_ALIAS.get(hm, hm)
        rec = {"date": dt, "sport": "nfl_all", "week": f"Wk {wk}",
               "away": aw2, "home": hm2,
               "label": f"{NFL_TEAM_NAMES[aw2]} at {NFL_TEAM_NAMES[hm2]}",
               "result": res.replace(" FINAL", "") if res else "",
               "review": f"https://www.pro-football-reference.com/boxscores/{box}.htm",
               "source": "nfl_2026_pfr_regseason.txt",
               "is_sf": "SF" in (aw2, hm2),
               "priority": "SF" in (aw2, hm2)}
        if t_et in ("TBD", "-"):
            # Wk 18: nfl.com officially lists every game as TBD; PFR's 1:00 PM ET is a
            # placeholder. Real game, no time -> NOT FREE day + estimated Sunday windows
            # from data/raw/nfl_2027_postseason_tbd.txt (see file header for sources).
            rec["start_pt"] = "TBD"; rec["start_min"] = None; rec["tbd_time"] = True
            if t_et == "TBD":
                rec["note"] = "nfl.com lists all Week 18 games as TBD (PFR's 1:00 PM ET was a placeholder)"
        else:
            et_h, et_m = map(int, t_et.split(":"))
            # ET->PT is exactly -3h for every NFL 2026-27 date (both zones change DST together)
            pt_dt = datetime(y, m, dd, et_h, et_m) - timedelta(hours=3)
            assert pt_dt.date() == date(y, m, dd), f"{dt}: PT date crossed midnight, check transcription"
            rec["start_pt"] = pt_dt.strftime("%H:%M")
            rec["start_min"] = pt_dt.hour*60 + pt_dt.minute
            rec["start_et"] = t_et
        games.append(rec)
    # preseason: wk|date|timeET|away|home|score|note  (times mostly not printed on the source)
    path = os.path.join(RAW, "nfl_2026_pfr_preseason.txt")
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        wk, dt, t_et, aw, hm, score, note = (line.split("|") + [""])[:7]
        y, m, dd = map(int, dt.split("-"))
        rec = {"date": dt, "sport": "nfl_all", "week": f"Pre {wk}", "away": ABBR_ALIAS.get(aw,aw),
               "home": ABBR_ALIAS.get(hm,hm), "result": score, "label": "",
               "source": "nfl_2026_pfr_preseason.txt", "review": "https://www.pro-football-reference.com/years/2026/preseason.htm"}
        rec["label"] = f"{NFL_TEAM_NAMES[rec['away']]} at {NFL_TEAM_NAMES[rec['home']]}"
        if t_et != "-":
            et_h, et_m = map(int, t_et.split(":"))
            pt_dt = datetime(y, m, dd, et_h, et_m) - timedelta(hours=3)
            rec["start_pt"] = pt_dt.strftime("%H:%M"); rec["start_min"] = pt_dt.hour*60+pt_dt.minute
            rec["start_et"] = t_et
        else:
            rec["start_pt"] = None; rec["start_min"] = None; rec["info_only"] = True
        if "TIE" in score:
            flag("IRREGULARITY", f"{dt} NFL preseason {rec['label']}: game ended {score} (tie)")
        rec["is_sf"] = "SF" in (rec["away"], rec["home"])
        rec["priority"] = rec["is_sf"]
        games.append(rec)
    # NFL postseason / Pro Bowl / Super Bowl / late-season Saturday TBD windows.
    # New format (2026-09-15): date|kickoffPT|dur_min|status(OFFICIAL/EST/CONFLICT)|count|label|review
    # OFFICIAL rows (Super Bowl LXI, 3:30 PM PT per ESPN event 401873270) block as real
    # games; EST/CONFLICT rows block as clearly-labeled ESTIMATED windows derived from
    # documented patterns (2025-26 postseason actuals, WWO air times, the league's
    # standard Saturday windows). Per the Cumulus 2026-09-09 press release every one of
    # these broadcasts airs on Westwood One national radio -> wwo badge + priority.
    path = os.path.join(RAW, "nfl_2027_postseason_tbd.txt")
    n_windows = n_est = n_official = 0
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        dt, kick, dur, status, cnt, label, review = (line.split("|") + [""])[:7]
        y, m, dd = map(int, dt.split("-"))
        h, mi = map(int, kick.split(":"))
        start_min = h * 60 + mi
        assert 0 <= start_min < 1440 and 30 <= int(dur) <= 300, f"bad window row: {line}"
        rec = {"date": dt, "sport": "nfl_all", "week": "Post",
               "start_pt": kick, "start_min": start_min, "dur_override": int(dur),
               "away": "TBD", "home": "TBD", "label": label,
               "review": review, "source": "nfl_2027_postseason_tbd.txt",
               "wwo": True, "wwo_slot": "Westwood One (national radio)",
               "is_sf": False, "priority": True}
        if status == "OFFICIAL":
            rec["official"] = True
            n_official += 1
        else:
            rec["estimated"] = True
            rec["est_kind"] = status
            n_est += 1
        if int(cnt):
            rec["tbd_count"] = int(cnt)
        n_windows += 1
        games.append(rec)
    return games

# --- other sports (blocking: 49ers 'nfl', Earthquakes 'mls', Stanford/Cal 'ncaa')
def load_local():
    data = json.load(open(os.path.join(ROOT, "data", "games_local.json")))
    games, seen_big = [], set()
    for g in data["games"]:
        rec = dict(g)
        if g["sport"] == "nfl":      # 49ers are high-priority per spec
            rec["priority"] = True
        if g.get("start_pt") and g["start_pt"] != "TBD":
            h, m = map(int, g["start_pt"].split(":"))
            rec["start_min"] = h * 60 + m
        else:
            rec["start_min"] = None
            flag("TBD_TIME", f"{g['date']} {g['label']}: kickoff time TBD/unconfirmed")
        if g.get("flag"):
            flag("IRREGULARITY", f"{g['date']} {g['label']}: {g['flag']}")
        rec["pt_date"] = g["date"]
        # Big Game dedupe: identical fixture listed under both schools
        if "big game" in g["label"].lower():
            k = g["date"]
            if k in seen_big:
                rec["dedup"] = True
            seen_big.add(k)
        games.append(rec)
    return games

# --- conditional windows (MLS playoffs / ACC / CFP): mark day UNCONFIRMED ----
def load_conditional():
    games = []
    for fn, sport, tag in (("mls_2026_playoffs_conditional.txt", "mls", "MLS"),
                           ("ncaa_2026_postseason_conditional.txt", "ncaa", "NCAA"),
                           ("wnba_2026_playoffs_conditional.txt", "wnba", "WNBA")):
        path = os.path.join(RAW, fn)
        if not os.path.exists(path):
            continue
        for line in open(path):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            dt, n, label = line.split("|")
            games.append({"date": dt, "sport": sport, "start_pt": None, "start_min": None,
                          "tbd_count": 1, "label": f"[conditional] {label}", "conditional": True,
                          "source": fn, "review": ("https://www.mlssoccer.com/playoffs/2025/news/"
                              "audi-2026-mls-cup-playoffs-key-dates-schedule-information" if tag=="MLS"
                              else "https://www.espn.com/wnba/story/_/id/49882118/wnba-playoffs-2026-"
                              "schedule-games-first-round-semifinals-finals-scores-results-news-highlights"
                              if tag=="WNBA"
                              else "https://www.espn.com/college-football/story/_/id/48958840/"
                              "2026-college-football-playoff-bowl-schedule-46-games")})
    return games

# --- Warriors (NBA) + Sharks (NHL): Bay Area radio flagships -----------------
# 95.7 The Game carries ALL Warriors preseason + regular-season games (blocking);
# 98.5 KFOX carries ALL Sharks regular-season games (blocking) + SELECT preseason
# games (unspecified which -> info_only, flagged). Both files store ET as printed
# by ESPN; ET->PT is exactly -3h for every date (shared Nov 1 DST change).
def load_nba_nhl():
    games = []
    for fn, sport, names, bay, bay_full, pre_blocks in (
            ("nba_warriors_2026_27.txt", "nba", NBA_TEAM_NAMES, "GS", "Golden State Warriors", True),
            ("nhl_sharks_2026_27.txt", "nhl", NHL_TEAM_NAMES, "SJ", "San Jose Sharks", False)):
        path = os.path.join(RAW, fn)
        for ln, line in enumerate(open(path), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            phase, dt, t_et, aw, hm, eid, note = (line.split("|") + [""])[:7]
            y, m, dd = map(int, dt.split("-"))
            et_h, et_m = map(int, t_et.split(":"))
            pt_dt = datetime(y, m, dd, et_h, et_m) - timedelta(hours=3)
            assert pt_dt.date() == date(y, m, dd), f"{fn}:{ln}: PT date crossed midnight"
            for a in (aw, hm):
                if a not in names:
                    flag("UNKNOWN_TEAM", f"{fn}:{ln} unknown {sport} abbr {a}")
            rec = {"date": dt, "sport": sport,
                   "start_pt": pt_dt.strftime("%H:%M"), "start_min": pt_dt.hour * 60 + pt_dt.minute,
                   "start_et": t_et, "away": aw, "home": hm, "phase": ("Preseason" if phase == "PRE" else "Regular Season"),
                   "label": f"{_bigname(aw, names, bay, bay_full)} at {_bigname(hm, names, bay, bay_full)}",
                   "priority": True, "source": fn,
                   "review": f"https://www.espn.com/{'nba' if sport=='nba' else 'nhl'}/game/_/gameId/{eid}/x"}
            if phase == "PRE" and not pre_blocks:
                rec["info_only"] = True
                flag("PRESEASON_INFO_ONLY",
                     f"{dt} {rec['label']}: Sharks preseason airs only 'select' games on KFOX "
                     f"(unspecified which) - listed, never blocking.")
            if note:
                rec["note"] = note
            games.append(rec)
    return games

# --- Golden State Valkyries (WNBA, 95.7 The Game in the Bay Area) --------------
# 95.7 The Game (KGMZ-FM) carries ALL home games over the air plus select road games
# (all games on the Audacy app). Per the club's official 2026 broadcast schedule, only the
# rows whose radio column is 95.7 The Game block; the Audacy-app-only road games are
# info_only (same rule the repo uses for the Sharks' "select" preseason games). The
# Valkyries CLINCHED a playoff berth on 2026-08-17, so the published playoff dates in the
# first round block (time TBD) and every later round is a conditional marker.
def load_wnba():
    games = []
    path = os.path.join(RAW, "wnba_valkyries_2026.txt")
    if not os.path.exists(path):
        return games
    for ln, line in enumerate(open(path), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        phase, dt, t_pt, ha, opp, radio, note = (line.split("|") + [""])[:7]
        rec = {"date": dt, "sport": "wnba",
               "phase": "Regular Season" if phase == "REG" else "Playoffs",
               "label": (f"Valkyries vs {opp}" if ha == "H" else f"Valkyries at {opp}")
                        if phase == "REG" else f"WNBA playoffs - {opp}",
               "priority": True, "source": "wnba_valkyries_2026.txt",
               "review": ("https://www.oursportscentral.com/services/releases/"
                          "goldn-state-valkyries-announce-local-television-and-radio-broadcast-schedule/n-6353443"
                          if phase == "REG" else
                          "https://www.espn.com/wnba/story/_/id/49882118/wnba-playoffs-2026-schedule-games-"
                          "first-round-semifinals-finals-scores-results-news-highlights")}
        if radio == "957":
            rec["radio"] = "95.7 The Game (KGMZ-FM)"
        elif phase == "POST":
            # playoff rows: the club carries every game on the Audacy app and home games on
            # 95.7; the per-game column is not published yet, so the playoff dates BLOCK
            # (flagged IRREGULARITY below) rather than being listed-only.
            rec["radio"] = "presumed 95.7 The Game / Audacy (per-game carriage unpublished)"
        else:
            rec["info_only"] = True
            flag("PRESEASON_INFO_ONLY",
                 f"{dt} {rec['label']}: carried only on the Audacy app (95.7 The Game's 2026 "
                 f"column for this game does NOT list the over-the-air flagship) - listed, never blocking.")
        if t_pt in ("TBD", "", "-"):
            rec["start_pt"] = "TBD" if phase == "REG" else None
            rec["start_min"] = None
            if phase != "REG":
                flag("TBD_TIME", f"{dt} {rec['label']}: WNBA playoff game - the Valkyries clinched "
                                 f"2026-08-17 but the round dates lock in only as the bracket posts")
        else:
            h, m = map(int, t_pt.split(":"))
            rec["start_pt"] = t_pt
            rec["start_min"] = h * 60 + m
        if note:
            rec["note"] = note
        games.append(rec)
    # playoff radio carriage is not published per game: home playoff games are certain,
    # road playoff games are presumed (flag only, no data change)
    if any(g["phase"] == "Playoffs" and not g.get("info_only") for g in games):
        flag("IRREGULARITY", "WNBA playoffs: the club's radio partnership covers all games on the "
             "Audacy app and home games on 95.7 The Game; per-game playoff radio carriage is not "
             "published, so the Sep 27 / Sep 29-30 playoff rows are blocked on the presumption that "
             "a Bay Area playoff game airs locally. Re-check when the bracket is published.")
    return games

# --- MLB 2026 postseason resolution (clinches + current seeding) -------------
# data/raw/mlb_2026_postseason_resolution.txt records what is RESOLVED for the 53
# TBD postseason placeholder games, strictly from the official mlb.com clinch
# tracker + playoff picture (fetched live 2026-09-17) and the live Stats API
# re-query (53 games / 28 dates, zero delta; every time still 07:33:00Z = TBD).
def load_postseason_resolution():
    out = {"as_of": None, "clinched": [], "seedings": {"AL": [], "NL": []},
           "wcr_series": [], "races": [], "times_status": None, "sources": []}
    path = os.path.join(RAW, "mlb_2026_postseason_resolution.txt")
    if not os.path.exists(path):
        return out
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        k = parts[0]
        if k == "as_of":
            out["as_of"] = parts[1]
        elif k == "clinched":
            out["clinched"].append({"team": parts[1], "league": parts[2], "date": parts[3],
                                    "detail": parts[4], "url": parts[5]})
        elif k in ("seed_al", "seed_nl"):
            out["seedings"]["AL" if k == "seed_al" else "NL"] = parts[1:]
        elif k == "wcr_series":
            out["wcr_series"].append({"league": parts[1], "home": parts[2], "away": parts[3]})
        elif k == "races":
            out["races"].append(parts[1])
        elif k == "times_status":
            out["times_status"] = parts[1]
        elif k == "source":
            out["sources"].append(parts[1])
    return out

# --- Westwood One NCAA football showcase (national radio, Bay Area: KNBR) ----
# New format (2026-09-15): date|kickoffPT(HH:MM, EST-<HH:MM> = estimated slot)|dur_min|
# away|home|eventId|note[|customlabel]. Confirmed kickoffs block from kickoff; TBD
# kickoffs block two ESTIMATED showcase slots (3:30 / 7:30 PM ET = 12:30 / 4:30 PM PT)
# - the two windows the WWO showcase actually uses in 2026 (observed kickoffs Sep 19
# 7:30 PM ET and Oct 31 3:30 PM ET; Nov 7 reported 3:30 PM ET).
# 2026-09-16 (pass B): the page widget only renders its FIRST 10 events; the complete
# 2026 list (13 broadcasts) comes from the widget's eventGrid endpoint. The three
# later events (Nov 28 Michigan@Ohio State, Dec 5 SEC Championship, Dec 12 Army-Navy)
# were missing until this correction - see the raw-file header for the URLs.
def load_wwo_ncaaf():
    games = []
    path = os.path.join(RAW, "westwoodone_ncaaf_2026.txt")
    seen_slots = {}
    for ln, line in enumerate(open(path), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        dt, kick, dur, aw, hm, eid, note, custom = (line.split("|") + [""] * 8)[:8]
        rec = {"date": dt, "sport": "ncaaw", "away": aw, "home": hm,
               "label": custom or f"Westwood One: {aw} at {hm}",
               "priority": True, "source": "westwoodone_ncaaf_2026.txt",
               "review": f"https://www.westwoodonesports.com/events/{eid}",
               "wwo": True, "wwo_slot": "Westwood One (national radio)"}
        if int(dur):
            rec["dur_override"] = int(dur)
        if kick.startswith("EST-"):
            h, mi = map(int, kick[4:].split(":"))
            rec["start_pt"] = kick[4:]
            rec["start_min"] = h * 60 + mi
            rec["estimated"] = True
            k = (dt, aw, hm)
            seen_slots[k] = seen_slots.get(k, 0) + 1
            if seen_slots[k] == 1:
                flag("ESTIMATED_SLOT",
                     f"{dt} Westwood One: {aw} at {hm}: kickoff still TBD - blocking BOTH estimated "
                     f"showcase windows (3:30 / 7:30 PM ET = 12:30 / 4:30 PM PT). Day is NOT FREE; "
                     f"replace with the real kickoff when the conference announces it (6-12 days out).")
        elif kick and kick != "TBD":
            h, mi = map(int, kick.split(":"))
            rec["start_pt"] = kick
            rec["start_min"] = h * 60 + mi
        else:
            rec["start_pt"] = None
            rec["start_min"] = None
            flag("TBD_TIME", f"{dt} Westwood One: {aw} at {hm}: no kickoff and no slot known - day NOT FREE, no window")
        if note:
            rec["note"] = note
            if "REPORTED" in note:
                flag("REPORTED_NOT_OFFICIAL", f"{dt} Westwood One: {aw} at {hm}: kickoff 3:30 PM ET is "
                     f"REPORTED (The Athletic via si.com/oregonlive.com) - official announcement expected Oct 26.")
        games.append(rec)
    # 2026-09-16 (pass B): the WWO page widget truncates at 10 events; the complete list
    # (eventGrid endpoint, ends "No more events") has 13 broadcasts. The three beyond
    # the first ten are added now (see raw-file header for the official kickoff sources).
    late = [g for g in games if g["date"] in ("2026-11-28", "2026-12-05", "2026-12-12")]
    if len(late) == 3:
        flag("WWO_NCAAF_EXPANDED",
             "CORRECTION 2026-09-16: the Westwood One NCAA football page's widget only renders its "
             "first 10 events, so the 2026-09-14 transcription missed 3 broadcasts. The widget's own "
             "eventGrid endpoint (westwoodonesports.com/more/eventGrid?id=47030..., fetched live "
             "2026-09-16; the list ends 'No more events') shows 13 total: added Nov 28 Michigan@Ohio "
             "State (kickoff 12:00 PM ET FOX, official), Dec 5 SEC Championship (kickoff 4:00 PM ET "
             "ABC, SEC official) and Dec 12 Army vs Navy (kickoff 3:00 PM ET CBS, official). These "
             "three days now block and assert NO free time.")
    if any(g["date"] == "2026-12-12" for g in games):
        flag("IRREGULARITY",
             "2026-12-12 Army vs Navy (WWO event 557132): WWO's own data conflicts - the schedule "
             "grid prints air time 2:00 PM ET while the event page prints the window '3:30 PM - "
             "7:30 PM EST'. The official CBS kickoff (3:00 PM ET per goarmywestpoint.com / "
             "navysports.com, 2026-05-27) is used as authoritative; the 2:00 PM ET air time is a "
             "long pregame show. Re-check when WWO updates the listing.")
    return games

# --- Westwood One NFL: cross-check vs the league table, mark wwo=true --------
def load_wwo_nfl(nfl_all):
    """Transcribed WWO broadcasts; every matchup row must match an nfl_all row
    (date + teams). TBA rows become info_only placeholders (the underlying
    Saturday/SNF games already block via the league table)."""
    wwo_rows, tba_rows = [], []
    path = os.path.join(RAW, "westwoodone_nfl_2026.txt")
    for ln, line in enumerate(open(path), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        dt, air_et, aw, hm, slot, eid, note = (line.split("|") + [""])[:7]
        if aw == "TBA":
            tba_rows.append({"date": dt, "sport": "nfl_all", "week": slot,
                             "start_pt": None, "start_min": None, "info_only": True,
                             "label": f"Westwood One {slot} broadcast - matchup TBA (air {air_et} ET)",
                             "source": "westwoodone_nfl_2026.txt",
                             "review": f"https://www.westwoodonesports.com/events/{eid}"})
            continue
        aw2, hm2 = WWO_ALIAS.get(aw, aw), WWO_ALIAS.get(hm, hm)
        for a in (aw2, hm2):
            if a not in NFL_TEAM_NAMES:
                flag("UNKNOWN_TEAM", f"westwoodone_nfl_2026.txt:{ln} unknown NFL abbr {a}")
        wwo_rows.append({"date": dt, "air_et": air_et, "away": aw2, "home": hm2,
                         "slot": slot, "eid": eid, "note": note})
    reg = [g for g in nfl_all if g["week"].startswith("Wk")]
    matched, missed = 0, []
    for w in wwo_rows:
        hit = [g for g in reg if g["date"] == w["date"] and g["away"] == w["away"] and g["home"] == w["home"]]
        if hit:
            matched += 1
            for g in hit:
                g["wwo"] = True
                g["wwo_slot"] = w["slot"]
                g["wwo_event"] = ("https://www.westwoodonesports.com/events/" + w["eid"]
                                  if w["eid"] != "press-release"
                                  else "https://www.globenewswire.com/news-release/2026/09/09/3358684/9032/en/cumulus-media-s-westwood-one-official-network-audio-partner-of-the-nfl-celebrates-40th-consecutive-season-and-reveals-2026-nfl-lineup-and-programming-highlights-from-nfl-kickoff-to.html")
        else:
            missed.append(f"{w['date']} {w['away']}@{w['home']} ({w['slot']})")
    for m in missed:
        flag("IRREGULARITY", f"Westwood One broadcast {m} has NO matching row in the league-wide NFL table - check for a flex/schedule change")
    # The Rio international game must NOT be marked (WWO carries 8 of 9 by its own release)
    rio = [g for g in reg if g["date"] == "2026-09-27" and {g["away"], g["home"]} == {"BAL", "DAL"}]
    if rio and any(g.get("wwo") for g in rio):
        flag("IRREGULARITY", "2026-09-27 BAL@DAL (Rio) unexpectedly marked as a WWO broadcast")
    else:
        flag("WWO_RIO_EXCLUDED",
             "2026-09-27 Ravens @ Cowboys (Rio de Janeiro, 4:25 PM ET) does NOT appear on the "
             "Westwood One schedule page: WWO's 2026 package is 'eight International Games' but "
             "the league scheduled nine. Presumed NOT on national radio (still blocks as an NFL game).")
    if tba_rows:
        flag("WWO_TBA", f"{len(tba_rows)} Westwood One NFL broadcasts have TBA matchups "
             f"(Dec 26 x2, Jan 2 x2, Jan 9 x3, Jan 10 SNF); the underlying Saturday/Week-18 games "
             f"already block via the league table - re-check after the league names them.")
    flag("WWO_PAST_UNVERIFIED",
         "Westwood One broadcasts before Sep 14 (Sep 10 SFO@LAR Melbourne, Sep 13 SNF DAL@NYG) "
         "are presumed carried per WWO's all-primetime/all-international pattern but the page's "
         "Past tab is JS-driven and not fetchable - deliberately NOT marked wwo. Only the Sep 9 "
         "Kickoff is verified (Cumulus press release 2026-09-09).")
    flag("WWO_PREEMPTION",
         "Westwood One's own station-finder caveat: 'Because of local blackouts and/or programming "
         "conflicts, not every affiliate can air every Westwood One Sports broadcast' - a 49ers noon "
         "game on KNBR could pre-empt a WWO broadcast in the Bay Area.")
    return matched, len(wwo_rows), tba_rows

# --- free-time computation -------------------------------------------------
def free_windows(blocks, day_start=0, day_end=1440):
    free, cur = [], day_start
    for s, e in blocks:
        s, e = max(s, day_start), min(e, day_end)
        if e <= cur:
            continue
        if s > cur:
            free.append((cur, min(s, day_end)))
        cur = max(cur, e)
    if cur < day_end:
        free.append((cur, day_end))
    return free

def fmt(m):
    m = int(m)
    if m >= 1440:
        return "12:00 AM (midnight)"
    h, mi = divmod(m, 60)
    ap = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{mi:02d} {ap}"

def main():
    mlb = load_mlb()
    nfl_all = load_nfl_all()
    local = load_local()
    cond = load_conditional()
    nba_nhl = load_nba_nhl()
    wnba = load_wnba()
    wwo_ncaaf = load_wwo_ncaaf()
    wwo_matched, wwo_total, wwo_tba = load_wwo_nfl(nfl_all)
    nfl_all = nfl_all + wwo_tba

    # 49ers appear in BOTH games_local.json (club list = source of truth for
    # kickoff times) and the league-wide NFL table. Keep the club row and drop the
    # duplicate league row from the per-day view so a 49ers game is not listed or
    # blocked twice. The master All-NFL table in schedules.md still shows all 272.
    sf_local_dates = {g["date"] for g in local if g["sport"] == "nfl"}
    for g in nfl_all:
        if g.get("is_sf") and g["date"] in sf_local_dates:
            g["dedup"] = True

    allg = mlb + nfl_all + local + cond + nba_nhl + wnba + wwo_ncaaf

    # ---- MLB 2026 postseason resolution (as of 2026-09-17, official mlb.com) --
    # 4 of 12 berths are clinched; the current projected bracket is attached to the
    # 53 TBD placeholder rows (playoff_note) so the day view shows what IS resolved
    # (clinched teams + current seeding) while every kickoff time stays TBD.
    psg = load_postseason_resolution()
    if psg.get("as_of"):
        clinched_names = ", ".join(c["team"] for c in psg["clinched"])
        series_txt = "; ".join(f"{s['league']} {s['home']} vs {s['away']}" for s in psg["wcr_series"])
        wcr_dates = {"2026-09-29", "2026-09-30", "2026-10-01"}
        for g in mlb:
            if not g.get("tbd_count"):
                continue
            if g["date"] in wcr_dates:
                g["playoff_note"] = (
                    f"MLB Wild Card Series (best-of-3; 4 series, {g['tbd_count']} games each day). "
                    f"RESOLVED as of {psg['as_of']} (mlb.com official): {len(psg['clinched'])} of 12 berths "
                    f"clinched - {clinched_names}. Current projected matchups (NOT final; seeds move "
                    f"through Sep 27): {series_txt}. Kickoff times officially TBD (none announced).")
            elif g["date"] <= "2026-10-10":
                g["playoff_note"] = ("MLB Division Series (best-of-5) - matchups resolve after the Wild "
                                     f"Card round (Sep 29 - Oct 1). Clinched as of {psg['as_of']}: "
                                     f"{clinched_names}. Kickoff times officially TBD (none announced).")
            elif g["date"] <= "2026-10-20":
                g["playoff_note"] = ("MLB League Championship Series (best-of-7) - matchups resolve after "
                                     "the Division Series. Kickoff times officially TBD (none announced).")
            else:
                g["playoff_note"] = ("MLB World Series (best-of-7) - matchups resolve after the League "
                                     "Championship Series. Kickoff times officially TBD (none announced).")
    else:
        psg = None

    # ---- Bay Area live-radio labels (re-verified live 2026-09-17) -------------
    # Only games that actually air live on Bay Area radio get a `radio` field; the
    # UI badges them with a radio icon (station in the tooltip) and lists them in
    # the "On the radio in the Bay Area today" panel. Flagship citations:
    # docs/BAY_AREA_RADIO_RESEARCH.md (KNBR Wikipedia, sjearthquakes.com,
    # gostanford.com, calbears.com per-game radio rows, 49ers.com, ESPN/Audacy).
    WWO_RADIO = "Westwood One national radio - Bay Area: KNBR 680 AM / 104.5 FM / KTCT 1050 AM"
    wwo_dates = {g["date"] for g in nfl_all if g.get("wwo")}
    def radio_for(g):
        sp = g["sport"]
        if g.get("wwo"):
            return WWO_RADIO
        if sp == "mlb":
            if g.get("away_id") == 137 or g.get("home_id") == 137:
                return "KNBR 680 AM / 104.5 FM (Giants flagship since 1979)"
            # Athletics (133): no Bay Area flagship since 2024 (KSTE 650 Sacramento) - listed, not radio
            return None
        if sp == "nfl":  # local 49ers
            base = "KSAN 107.7 FM + KNBR 680/104.5 (weeks 1-3: KSFO 810 AM / KSAN 107.7)"
            if g.get("date") in wwo_dates:
                base += " + Westwood One national"
            return base
        if sp == "mls":
            return "KSFO 810 AM (English) / KZSF 1370 AM (Spanish)"
        if sp == "ncaa":
            lab = g.get("label", "")
            if "big game" in lab.lower():
                return "KNBR 104.5 FM / 680 AM (129th Big Game - verified 2026-09-17 on calbears.com)"
            if lab.startswith("Stanford"):
                return "KNBR / KTCT 1050 AM"
            if lab.startswith("Cal"):
                return "KSFO 810 AM"
            return None
        if sp == "nba":
            return "95.7 The Game (KGMZ-FM) - all games"
        if sp == "nhl":
            return "Sharks Audio Network (online); 98.5 KFOX flagship 2000-2021"
        if sp == "wnba":
            return g.get("radio")
        return None
    for g in allg:
        if g.get("conditional") or g.get("info_only"):
            continue
        r = radio_for(g)
        if r:
            g["radio"] = r

    # doubleheader / duplicate detection (same matchup twice on one official date)
    seen = {}
    for g in mlb:
        if "away_id" not in g:
            continue
        k = (g["date"], g["away_id"], g["home_id"])
        seen[k] = seen.get(k, 0) + 1
    for (d, a, h), n in sorted(seen.items()):
        if n > 1:
            flag("DOUBLEHEADER", f"{d}: {TEAMS[a]['abbr']} @ {TEAMS[h]['abbr']} appears {n}x (doubleheader)")

    # future Sunday-window NFL games may still flex (Wk 18 rows are TBD and excluded)
    flex = sum(1 for g in nfl_all if g.get("start_min") is not None
               and g["date"] > TODAY.isoformat() and g.get("start_et") in ("13:00", "16:05", "16:25"))
    if flex:
        flag("FLEX_WINDOW",
             f"{flex} league-wide NFL games after {TODAY.isoformat()} sit in the Sunday 1:00 PM / 4:05 PM / "
             f"4:25 PM ET windows and can still be moved by NFL flex scheduling (flex begins Week 5; times "
             f"as printed by the source on 2026-09-11 and re-verified 2026-09-15 vs the WWO page + nfl.com "
             f"week pages - no changes found). Thursday/Sunday/Monday night, international and scheduled "
             f"Saturday games are locked. Because ALL league-wide NFL games block free time, a flex move "
             f"shifts the affected day's free windows - re-run the build after each Tuesday announcement.")

    # ---- 2026-09-15 pass flags -------------------------------------------------
    flag("WK18_TBD",
         "All 16 Week 18 games (Sun Jan 10, 2027) are officially date/time TBD on nfl.com "
         "(https://www.nfl.com/schedules/2026/by-week/week-18); PFR's printed 'Sunday 1:00 PM ET' was a "
         "placeholder and is no longer used. The day is NOT FREE with three ESTIMATED Sunday windows "
         "(1:00 / 4:25 PM ET + the flex-selected SNF 8:20 PM ET, WWO event 548510). Westwood One also "
         "carries a Saturday TRIPLEHEADER on Jan 9 (air 12:30 / 4:15 / 8:00 PM ET): three Wk-18 games "
         "will move there - blocked as estimated windows 10:00 AM / 1:30 / 5:15 PM PT.")
    flag("SAT_WINDOWS",
         "Late-season Saturday TBD windows: WWO sells a Wk16 Saturday doubleheader on Sat Dec 26, 2026 "
         "(events 548519/548520) and a Wk17 doubleheader on Sat Jan 2, 2027 (events 548521/548522), but "
         "nfl.com/ESPN currently list ZERO games on those dates - the matchups are picked in-season and "
         "TWO games each will move off the Dec 27 / Jan 3 Sunday slates. Estimated windows 1:30 & 5:15 PM "
         "PT are blocked on both days; re-run the build after the league names the Saturday games.")
    flag("POSTSEASON_WWO",
         "Westwood One airs EVERY NFL postseason game + Super Bowl LXI (Cumulus press release 2026-09-09) "
         "in the Bay Area on KNBR/KTCT - so Wild Card (Jan 16-18), Divisional (Jan 23-24), Conference "
         "Championships (Jan 31) and Super Bowl Sunday (Feb 14, 2027) are all NOT FREE. Kickoffs are not "
         "official yet: estimated windows use the 2025-26 postseason pattern (WC Sat 4:30/8:00 PM ET, "
         "WC Sun 1:00/4:30/8:15, WC Mon 8:15, Div 4:30/8:20 & 3:00/6:30, CC 3:00/6:30 - "
         "https://en.wikipedia.org/wiki/2025%E2%80%9326_NFL_playoffs). Dates verified against ESPN's live "
         "event feed (2/3/1 WC games, 2+2 Div, 2 CC placeholder events).")
    flag("SB_OFFICIAL",
         "Super Bowl LXI kickoff is OFFICIAL: Sun Feb 14, 2027, 6:30 PM ET / 3:30 PM PT at SoFi Stadium "
         "(ESPN event 401873270, status detail 'Sun, February 14th at 6:30 PM EST'; ESPN/ABC TV, Westwood "
         "One radio - Harlan & Warner). Blocks 3:30-7:15 PM PT using the researched ~3h45m Super Bowl "
         "broadcast length (bolavip.com/en/nfl/super-bowl-timeouts-length-duration-breaks).")
    flag("PROBOWL_CONFLICT",
         "2027 Pro Bowl Games date is UNRESOLVED: nflplayoffpass.com (updated Sep 9, 2026) says Tuesday "
         "Feb 9, 8:00 PM ET at SoFi on ESPN (moved into Super Bowl week); sportbusy.com says Sunday Feb 7. "
         "ESPN's calendar puts Pro Bowl week Feb 3-9 but no event exists on either date yet. BOTH days "
         "carry an estimated window and are flagged - remove the loser when the NFL announces.")
    flag("PRESEASON_TIMES",
         "2026-09-15: kickoff times for ALL 49 preseason games added from Sporting News' full preseason "
         "TV schedule (cross-checked vs Yahoo/Fox News/CableTV week-1 listings and vs the officially "
         "sourced 49ers times). Preseason games now block free time in August; the previous build left "
         "~47 of them info-only, which understated August busy time.")
    flag("VERIFIED_PASS",
         "2026-09-15 re-verification: (1) MLB Stats API live query Sep 26-29 confirms the regular season "
         "ends Sun Sep 27 (15 games), Sep 28 is an off day, and the postseason starts Tue Sep 29 with 4 "
         "Wild Card placeholder games at 07:33Z (times TBD) - the raw files match. (2) The Westwood One "
         "NFL schedule page re-fetched and every dated broadcast matches the transcription (65 + 8 TBA). "
         "(3) nfl.com by-week pages for weeks 16/17/18 checked: Wk16 = Dec 24 TNF + Dec 25 tripleheader + "
         "Dec 27 slate + Dec 28 MNF (no Dec 26 games), Wk17 = Dec 31 + Jan 3 + Jan 4 (no Jan 2 games), "
         "Wk18 = all TBD. (4) ESPN postseason placeholder events verified on Jan 16 (2), Jan 17 (3), "
         "Jan 18 (1), Jan 23 (2), Jan 31 (NFC + AFC championships), Feb 14 (SB, official time). "
         "(5) 2025-26 playoff kickoff pattern sourced (Wikipedia).")

    # NBA / NHL schedule-shape notes (confirmed gaps, not missing rows)
    flag("SCHEDULE_GAP", "Warriors: no game Dec 2-11, 2026 (10 days, NBA Cup window) and none "
         "Feb 18-24, 2027 (7 days, All-Star break) - confirmed gaps on the ESPN schedule page, "
         "not missing rows. Neither the NBA Cup knockout nor All-Star Weekend blocks (no Warriors game).")
    flag("SCHEDULE_GAP", "Sharks: no game Jan 31 - Feb 9, 2027 (10 days) - confirmed gap on the ESPN "
         "schedule page, not missing rows.")
    flag("ODD_START", "Sharks Dec 22, 2026 @ Seattle printed as 9:40 PM ET - an unusual :40 start, "
         "kept exactly as printed by ESPN (per-game review link on the row).")
    flag("NEUTRAL_SITE", "Warriors preseason Oct 13, 2026 vs Lakers: the tickets link points to "
         "Golden 1 Center, Sacramento - neutral site, kept as a Warriors home-designated row.")
    # MLB scope boundary notes
    flag("SCOPE_NOTE", "MLB: the tracked 2026 season (regular + postseason) ends with the World Series "
         "placeholders on 2026-10-31 (last date in the official bracket calendar). No MLB games exist "
         "Nov 1, 2026 - Feb 28, 2027 EXCEPT 2027 Spring Training, which opens Fri Feb 19, 2027 (all 30 "
         "clubs) per MLB's press release of Sep 4, 2026 - out of scope per spec (2026 season only) and "
         "NOT blocked; re-run after the 2027 ST schedule files publish if you want them included.")
    # ---- 2026-09-16 independent-audit pass flags -------------------------------
    flag("VERIFIED_PASS_2026_09_16",
         "2026-09-16 independent audit + live re-verification pass: (1) scripts/audit.py (a second, "
         "independent implementation) recomputes every day from data/raw/* and matches the generated "
         "file on all 212 days (free windows, blocked merges, 24h partition, day status, per-day game "
         "census, UTC->PT and ET->PT conversions, priority rules) - AUDIT PASSED. (2) MLB live Stats API "
         "check: per-date game counts for 2026-08-01..2026-09-27 are identical to the raw files on all 58 "
         "dates (totalGames 778), and game-by-game (time + away/home team ids) spot-checks on Sep 16-26 "
         "match exactly. (3) WWO NCAA football page re-fetched: the same 10 broadcasts, zero deltas. "
         "(4) WWO NFL page re-fetched (all 4 chunks): every dated broadcast + 8 TBA rows match. "
         "(5) Local fixtures spot-checked vs live sources: Cal vs Wagner Sep 19 12:30 PM PT "
         "(iheart/ACC Network + visitberkeley '12:30 p.m. PT'), Stanford at Duke Sep 19 1:00 PM PT "
         "(= 4 PM ET, fayobserver/Yahoo Sep 14), Earthquakes vs LAFC Sep 19 4:30 PM PT at Levi's "
         "(sjearthquakes.com 2026 schedule release + VTA). (6) Pro Bowl 2027 date still unresolved "
         "(Feb 7 vs Tue Feb 9) - both candidate days remain blocked and flagged.")
    flag("MLB_POSTSEASON_CORRECTION",
         "CORRECTION 2026-09-16: the live MLB Stats API now reports 2026-10-04 as 2 postseason "
         "placeholder games (the 2026-08-28 transcription had 4); the postseason placeholder total is "
         "therefore 53, not 55. All other 27 postseason dates are unchanged and every date stays "
         "'NOT FREE - TIME TBD'. Raw file updated; see the file header for the exact query.")
    flag("VERIFIED_PASS_2026_09_16_B",
         "2026-09-16 pass B (this session): (1) WWO NFL page re-fetched live - the page renders two "
         "lists; combined they hold all 71 upcoming events and every one matches the transcription at "
         "event-id level (63 remaining dated matchups + 8 TBA; the Sep 14 MNF 548429 moved to the "
         "Past tab as it is now in the past). Zero deltas. (2) WWO NCAAF page re-fetched: the widget "
         "shows only 10 events, but the widget's own eventGrid endpoint (id=47030, list ends 'No more "
         "events' at offset 20) holds the complete 2026 list = 13 broadcasts - three were missing and "
         "are added: Nov 28 Michigan@Ohio State (official 12:00 PM ET FOX), Dec 5 SEC Championship "
         "(official 4:00 PM ET ABC, SEC), Dec 12 Army vs Navy (official 3:00 PM ET CBS). (3) WWO U.S. "
         "Soccer page: 'No upcoming events'. (4) Bay Area radio sweep: no further in-window live "
         "Bay Area radio sport found (NWSL Deltas have no verifiable Bay Area radio flagship; NWSL "
         "radio is SiriusXM national). (5) Fixed the remaining part of the reported bug: NOT FREE-TBD "
         "and UNCONFIRMED days no longer assert any free time (see FREE_TIME_NOT_ASSERTED).")
    flag("VERIFIED_PASS_2026_09_17",
         "2026-09-17 re-verification pass (this session): (1) WWO NFL schedule page re-fetched live "
         "(all 4 chunks): both rendered lists + the 8 TBA slots = 71 upcoming events, every one "
         "matching data/raw/westwoodone_nfl_2026.txt at event-id level (incl. Nov 2 CHI@SEA MNF = "
         "event 548540, re-confirmed on the page); the Sep 14 MNF (548429) is now in the Past tab as "
         "expected; the Sep 27 Rio game still absent (WWO_RIO_EXCLUDED unchanged). Zero deltas. "
         "(2) WWO NCAAF complete list re-fetched live via the widget's eventGrid endpoint (id=47030): "
         "the same 13 broadcasts, zero deltas (Nov 28 11:30am ET air, Dec 5 3:30pm ET, Dec 12 2:00pm "
         "ET air all unchanged). (3) MLB Stats API re-queried live: totalGames=53 across the same 28 "
         "postseason dates - zero delta vs data/raw/mlb_2026_postseason_tbd.txt; every placeholder "
         "gameDate is still 07:33:00Z (all kickoff times officially TBD). (4) MLB.com official clinch "
         "tracker + playoff picture fetched: 4 teams clinched (Rays 9/11, Brewers 9/11 + NL Central "
         "9/15, Dodgers 9/14 + NL West 9/17, Yankees 9/14) - recorded in the NEW file "
         "data/raw/mlb_2026_postseason_resolution.txt (clinches are official; the projected bracket "
         "is mlb.com's current seeding, not final). (5) Earthquakes official 2026 radio release "
         "re-fetched: 16 of 17 in-window games match the repo; ONE correction - Oct 31 vs Real Salt "
         "Lake is 2:00 PM PT (the transcribed PDF printed TBD; see MLB_OCT31_QUIKES_2PM). "
         "(6) Stanford official schedule re-fetched: 12/12 rows match, including the live TBA status "
         "for Oct 3 / Oct 31 / Nov 14 / Nov 21 (Big Game) / Nov 28. (7) Cal official schedule "
         "re-fetched: 12/12 rows match, including live no-time status Oct 10 - Nov 28; every game "
         "prints 'Radio: KSFO 810 AM' and the Nov 21 Big Game prints 'Radio: KNBR 104.5 FM / 680 AM' "
         "(new verified detail, CAL_BIGGAME_KNBR_RADIO). (8) 49ers 20/20 rows consistent with today's "
         "sources + the WWO page (MNF Oct 19 WAS@SF, TNF Dec 17 SF@LAC, SNF Jan 3 PHI@SF; the Nov 22 "
         "Mexico City game's WWO 7:30pm ET line is the pregame air - official kickoff 8:20 PM ET per "
         "the league table). (9) Cumulus press release + KNBR Wikipedia re-fetched: WWO scope (all "
         "primetime + 8 internationals + Saturdays + EVERY postseason game + SB LXI) and Bay Area "
         "carriage (KNBR family) unchanged. (10) scripts/audit.py re-run: ALL PASS. The new UI "
         "invariant test (scripts/ui_logic_test.js, executed by this build) re-proves the "
         "football-day bug fix against the generated data AND the shipped index.html code: no day "
         "with a tracked football game renders FREE, and no NOT FREE/UNCONFIRMED day asserts free "
         "time.")
    flag("MLB_OCT31_QUIKES_2PM",
         "CORRECTION 2026-09-17: the Earthquakes' official 2026 radio release (sjearthquakes.com, "
         "fetched live) lists Sat Oct 31 vs Real Salt Lake (home, PayPal Park) at 2:00 PM PT; the "
         "transcribed MLS schedule PDF printed TBD for this match. games_local.json updated - the "
         "game now blocks 2:00-4:00 PM PT on a day that is already NOT FREE - TIME TBD (Cal @ NC "
         "State + Stanford @ Louisville TBD, plus the confirmed WWO Florida@Georgia 12:30-3:34 PM "
         "PT block).")
    flag("MLB_POSTSEASON_RESOLVED",
         "MLB 2026 postseason resolution as of 2026-09-17 (official mlb.com, fetched today): 4 of 12 "
         "berths clinched - Rays (AL), Brewers (NL Central), Dodgers (NL West), Yankees (AL). "
         "Projected Wild Card matchups (mlb.com playoff picture; NOT final - seeds move through Sep "
         "27): AL (1) Rays vs (4) Yankees, (2) Guardians vs (5) Red Sox, (3) Astros vs (6) White "
         "Sox; NL (1) Brewers vs (4) Cubs, (2) Dodgers vs (5) Phillies, (3) Braves vs (6) Padres. "
         "ALL 53 kickoff times remain officially TBD (Stats API 07:33:00Z placeholders, re-verified "
         "today; MLB releases times closer to each round). The 53 games / 28 dates are unchanged "
         "(zero delta). The build attaches these notes to the placeholder rows (playoff_note) and "
         "shows the playoff picture in the day view for Sep 29 - Oct 31. Sources: "
         "data/raw/mlb_2026_postseason_resolution.txt (with URLs).")
    flag("CAL_BIGGAME_KNBR_RADIO",
         "VERIFIED 2026-09-17 (calbears.com, per-game radio rows): every 2026 Cal game prints "
         "'Radio: KSFO 810 AM' EXCEPT the Nov 21 129th Big Game, which prints 'Radio: KNBR 104.5 FM "
         "/ 680 AM'. The radio badges/labels in the UI and schedules.md follow the per-game station.")
    flag("FREE_TIME_NOT_ASSERTED",
         "RULE CHANGE 2026-09-16 (pass B) - the second half of the reported bug 'the site says I have "
         "free time on days when there are football games on'. Days with status NOT FREE - TIME TBD or "
         "UNCONFIRMED no longer report ANY free windows or free minutes: free=[] and free_minutes=0 in "
         "free_time.json (the arithmetic windows are kept in `provisional_free` for reference only), "
         "the UI draws no green free bands and shows no 'Xh Ym free' on them, and the day-by-day "
         "table prints Free min = 0, which means 'not asserted', not 'free'. Estimated windows still "
         "block their times; PARTIAL/FREE days with fully-official kickoffs still report their exact "
         "free gaps as before.")
    flag("VERIFIED_PASS_2026_09_11", "Superseded-pass note kept for the audit trail: 2026-09-11 MLB Stats "
         "API re-query for 2026-09-10/11/12 matched the raw file 35/35 games (dates, times, team ids). "
         "The 'sparse' Tue/Thu slate days (5 games on Sep 10, 3 on Sep 21) are genuine scheduled light "
         "days, not data gaps.")

    days = []
    d = START
    while d <= END:
        ds = d.isoformat()
        todays = [g for g in allg if g["date"] == ds or g.get("pt_date") == ds]
        blocking = [g for g in todays if g["sport"] in BLOCKING_SPORTS and not g.get("dedup")]
        nfla = [g for g in todays if g["sport"] == "nfl_all"]
        blocks = []
        for g in blocking:
            if g.get("start_min") is None:
                continue
            dur = g.get("dur_override", DUR_OF(g["sport"]))
            blocks.append([g["start_min"] - PRE_BUFFER, g["start_min"] + dur + POST_BUFFER])
        blocks.sort()
        merged = []
        for s, e in blocks:
            if merged and s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        fw = free_windows(merged)
        # blocking already contains nfl_all now (and excludes dedup'd rows), so no
        # separate + nfla term is needed (that double-counted the all-NFL layer).
        # Real TBD games: scheduled games that WILL be played but have no announced
        # kickoff (Week 18, MLB postseason placeholders, individual Stanford/Cal/
        # Earthquakes/49ers TBD rows). NOT info_only and NOT conditional.
        tbd = [g for g in blocking
               if g.get("start_min") is None and not g.get("info_only") and not g.get("conditional")]
        tbd_n = len([g for g in tbd if not g.get("tbd_count")]) + sum(g.get("tbd_count", 0) for g in tbd)
        est_n = len([g for g in blocking if g.get("start_min") is not None and g.get("estimated")])
        cond_n = len([g for g in todays if g.get("conditional")])
        # Status model (2026-09-15, per the user's rule that any Westwood One-covered /
        # tracked game means free time NOT available):
        #   NOT FREE - TIME TBD : a tracked game will definitely be played/aired but its
        #                          kickoff (or matchup) is not official yet. Estimated
        #                          windows block where a documented pattern exists; the
        #                          computed free windows are PROVISIONAL, never asserted.
        #   UNCONFIRMED         : only conditional markers (MLS/ACC/CFP qualification).
        #   FREE / PARTIAL / FULLY BOOKED : all games have known times.
        if tbd_n or est_n:
            status = "NOT FREE — TIME TBD"
        elif cond_n:
            status = "UNCONFIRMED"
        elif not blocks:
            status = "FREE"
        elif sum(e - s for s, e in fw) == 0:
            status = "FULLY BOOKED"
        else:
            status = "PARTIAL"
        # Free-time assertion rule (2026-09-16 pass B, per the user's rule "any games that
        # are covered on this site should be marked as free time NOT available"): a day
        # whose status is NOT FREE - TIME TBD (a tracked game will definitely play/air but
        # its kickoff is not official) or UNCONFIRMED (conditional markers may add games)
        # asserts NO free time at all. The arithmetic free windows are still computed and
        # kept in `provisional_free` for reference ONLY - they are never presented to the
        # user as free time (no green bands, no "Xh Ym free", Free min = 0 in the table).
        # This is the second part of the fix for the reported bug "the site says I have
        # free time on days when there are football games on": the first part (2026-09-15)
        # introduced the NOT FREE - TIME TBD status, but the data/UI still reported
        # windows + free minutes on those days.
        if status in ("NOT FREE — TIME TBD", "UNCONFIRMED"):
            free_out, free_min_out, prov_out = [], 0, \
                [{"start": s, "end": e, "start_t": fmt(s), "end_t": fmt(e), "minutes": e - s} for s, e in fw]
        else:
            free_out, free_min_out, prov_out = \
                [{"start": s, "end": e, "start_t": fmt(s), "end_t": fmt(e), "minutes": e - s} for s, e in fw], \
                sum(e - s for s, e in fw), []
        days.append({
            "date": ds, "weekday": d.strftime("%a"), "status": status,
            "games": [dict(g) for g in
                      sorted(todays, key=lambda x: (x.get("start_min") is None, x.get("start_min") or 0))],
            "blocked": [{"start": s, "end": e, "start_t": fmt(s), "end_t": fmt(e)} for s, e in merged],
            "free": free_out,
            "free_minutes": free_min_out,
            "provisional_free": prov_out,
            "game_count": len([g for g in blocking if g.get("start_min") is not None]),
            "nfl_all_count": len([g for g in nfla if g.get("start_min") is not None and not g.get("dedup")]),
            "tbd_count": tbd_n,
            "estimated_count": est_n,
            "conditional_count": cond_n,
            "has_priority": any(g.get("priority") for g in todays),
            "has_sf": any(g.get("is_sf") for g in nfla) or any(g["sport"]=="nfl" for g in blocking),
        })
        for g in tbd:
            if g.get("tbd_count"):
                continue
            flag("UNBLOCKED_TBD", f"{ds}: '{g['label']}' has no confirmed start time - the day is "
                                  f"marked NOT FREE (TIME TBD) and its free windows (if any are shown) "
                                  f"are provisional; the game itself does not block a specific window yet.")
        d += timedelta(days=1)

    os.makedirs(OUT, exist_ok=True)
    reg = [g for g in nfl_all if g["week"].startswith("Wk")]
    pre = [g for g in nfl_all if g["week"].startswith("Pre")]
    post_windows = [g for g in nfl_all if g["week"] == "Post"]
    nba = [g for g in nba_nhl if g["sport"] == "nba"]
    nhl = [g for g in nba_nhl if g["sport"] == "nhl"]
    wnba_games = [g for g in wnba if g["phase"] == "Regular Season"]
    wnba_po = [g for g in wnba if g["phase"] == "Playoffs"]
    meta = {
        "generated_utc": GENERATED, "window": {"start": START.isoformat(), "end": END.isoformat()},
        "timezone": "America/Los_Angeles - PDT (UTC-7) through Oct 31, 2026; PST (UTC-8) from Nov 1, 2026 to Mar 13, 2027",
        "durations_minutes": DURATIONS, "pre_buffer_minutes": PRE_BUFFER, "post_buffer_minutes": POST_BUFFER,
        "blocking_sports": sorted(BLOCKING_SPORTS),
        "totals": {"mlb_games": len([g for g in mlb if "away_id" in g]),
                   "mlb_postseason_tbd": sum(g.get("tbd_count", 0) for g in mlb),
                   "local_games": len(local),
                   "nfl_reg_games": len(reg), "nfl_pre_games": len(pre),
                   "nfl_reg_tbd_games": len([g for g in reg if g.get("tbd_time")]),
                   "nfl_window_rows": len(post_windows),
                   "nfl_windows_estimated": len([g for g in post_windows if g.get("estimated")]),
                   "nfl_windows_official": len([g for g in post_windows if g.get("official")]),
                   "nfl_all_tbd_days": len({g["date"] for g in nfl_all if g.get("conditional")}),
                   "conditional_days": len({g["date"] for g in cond}),
                   "nba_games": len(nba), "nhl_games": len(nhl),
                   "wnba_games": len(wnba_games),
                   "wnba_blocking": len([g for g in wnba_games if not g.get("info_only")]),
                   "wnba_playoff_rows": len(wnba_po),
                   "wwo_nfl_matched": wwo_matched, "wwo_nfl_total": wwo_total,
                   "wwo_nfl_tba": len(wwo_tba),
                   "wwo_ncaaf": len({(g["date"], g["away"], g["home"]) for g in wwo_ncaaf}),
                   "wwo_ncaaf_rows": len(wwo_ncaaf),
                   "wwo_ncaaf_est_rows": len([g for g in wwo_ncaaf if g.get("estimated")]),
                   "mlb_clinched": len(psg["clinched"]) if psg else 0,
                   "radio_games": len([g for g in allg if g.get("radio") and not g.get("conditional")])},
        "postseason_resolution": psg,
        "radio_bay_area": [
            "KNBR 680 AM / 104.5 FM / KTCT 1050 AM - Westwood One (every primetime NFL game, all 8 WWO internationals, every NFL playoff game, WWO college football) + Giants flagship (since 1979) + 49ers co-flagship + Stanford football + the Nov 21 Big Game (verified 2026-09-17)",
            "KSFO 810 AM - Earthquakes English flagship (2026) + Cal football (every 2026 game except the Big Game, verified 2026-09-17 on calbears.com)",
            "KZSF 1370 AM La Kaliente - Earthquakes Spanish-language flagship (2026)",
            "KSAN 107.7 FM - 49ers co-flagship",
            "95.7 The Game (KGMZ-FM) - Warriors (all games) + Valkyries (home games over the air, all games on the Audacy app)",
            "98.5 KFOX - Sharks flagship 2000-2021; Jan 2021 onward all Sharks audio is the Sharks Audio Network (online)"],
    }
    json.dump({"meta": meta, "games": mlb}, open(os.path.join(OUT, "mlb.json"), "w"), indent=1)
    json.dump({"meta": meta, "days": days, "flags": flags}, open(os.path.join(OUT, "free_time.json"), "w"), indent=1)

    # ---- verification report ----
    print("=" * 78); print("VERIFICATION REPORT"); print("=" * 78)
    print(f"Window            : {START} .. {END} ({(END-START).days+1} days), America/Los_Angeles")
    print(f"MLB games parsed  : {meta['totals']['mlb_games']} across "
          f"{len(set(g['date'] for g in mlb if 'away_id' in g))} official dates")
    print(f"MLB postseason TBD: {meta['totals']['mlb_postseason_tbd']} games (times/teams unconfirmed)")
    print(f"49ers/Quakes/NCAA : {len(local)} blocking games (+{len(cond)} conditional day markers)")
    print(f"NFL league-wide   : {len(reg)} regular-season games + {len(pre)} preseason games "
          f"(ALL block; 49ers rows dedup against the club list in games_local.json)")
    print(f"NFL Wk18 TBD      : {meta['totals']['nfl_reg_tbd_games']} Wk-18 games stored TBD (nfl.com official); "
          f"estimated Sunday windows applied")
    print(f"NFL TBD windows   : {len(post_windows)} window rows "
          f"({meta['totals']['nfl_windows_official']} OFFICIAL, "
          f"{meta['totals']['nfl_windows_estimated']} ESTIMATED: postseason + Sat Dec 26/Jan 2/Jan 9 + Wk18 + Pro Bowl)")
    print(f"Warriors (NBA)    : {len(nba)} games "
          f"({len([g for g in nba if g['phase']=='Preseason'])} pre + "
          f"{len([g for g in nba if g['phase']=='Regular Season'])} reg; all block on 95.7 The Game)")
    print(f"Valkyries (WNBA)  : {len(wnba_games)} regular-season games in window "
          f"({meta['totals']['wnba_blocking']} on 95.7 The Game = blocking; "
          f"{len([g for g in wnba_games if g.get('info_only')])} Audacy-app-only = listed) "
          f"+ {len(wnba_po)} playoff TBD rows (clinched 2026-08-17)")
    print(f"Sharks (NHL)      : {len(nhl)} games "
          f"({len([g for g in nhl if g.get('info_only')])} pre info-only + "
          f"{len([g for g in nhl if g['phase']=='Regular Season'])} reg blocking on 98.5 KFOX)")
    print(f"Westwood One NFL  : {wwo_matched}/{wwo_total} broadcasts matched to league rows "
          f"+ {len(wwo_tba)} TBA placeholders (marked wwo, Bay Area: KNBR)")
    print(f"Westwood One NCAAF: {meta['totals']['wwo_ncaaf']} broadcasts / {len(wwo_ncaaf)} rows "
          f"({len([g for g in wwo_ncaaf if g['start_min'] is not None and not g.get('estimated')])} confirmed kickoff, "
          f"{len([g for g in wwo_ncaaf if g.get('estimated')])} estimated showcase slots (incl. Nov 7 reported-not-official), "
          f"{len([g for g in wwo_ncaaf if g['start_min'] is None])} no window)")

    # NFL arithmetic checks
    ok = True
    if len(nba) != 63:
        ok = False; print(f"!! Warriors count {len(nba)} != 63 (6 pre + 57 reg expected)")
    if len(nhl) != 68:
        ok = False; print(f"!! Sharks count {len(nhl)} != 68 (4 pre + 64 reg expected)")
    if len(wnba_games) != 16 or meta["totals"]["wnba_blocking"] != 9:
        ok = False; print(f"!! Valkyries count {len(wnba_games)} (expect 16) / blocking "
                          f"{meta['totals']['wnba_blocking']} (expect 9)")
    if len(wwo_ncaaf) != 19 or meta["totals"]["wwo_ncaaf"] != 13:
        ok = False; print(f"!! WWO NCAAF count {len(wwo_ncaaf)} rows / {meta['totals']['wwo_ncaaf']} broadcasts != 19/13")
    if wwo_matched != wwo_total:
        ok = False; print(f"!! WWO NFL matched {wwo_matched}/{wwo_total} (see IRREGULARITY flags)")
    if len(reg) != 272:
        ok = False; print(f"!! NFL regular-season count {len(reg)} != 272")
    cnt = {}
    for g in reg:
        cnt[g["away"]] = cnt.get(g["away"], 0) + 1
        cnt[g["home"]] = cnt.get(g["home"], 0) + 1
    bad = {t: n for t, n in cnt.items() if n != 17}
    print(f"NFL per-team games: {len(cnt)} teams seen, "
          f"{'ALL exactly 17' if not bad else '!! off-17: ' + str(bad)}")
    if bad: ok = False
    pre_cnt = {}
    for g in pre:
        pre_cnt[g["away"]] = pre_cnt.get(g["away"], 0) + 1
        pre_cnt[g["home"]] = pre_cnt.get(g["home"], 0) + 1
    pre_bad = {t: n for t, n in pre_cnt.items() if n not in (3, 4)}
    print(f"NFL preseason     : {len(pre)} games, per-team 3 (49 clubs) +4 (ARI/CAR)"
          f"{'' if not pre_bad else '  !! ' + str(pre_bad)}")
    if pre_bad: ok = False
    wk = {}
    for g in reg: wk[g["week"]] = wk.get(g["week"], 0) + 1
    print(f"NFL games per wk  : " + " ".join(f"{k.split()[1]}:{v}" for k, v in sorted(wk.items(), key=lambda kv: int(kv[0].split()[1]))))
    print(f"  weeks 1-18 sums : {sum(wk.values())}")

    # cross-check: every 49ers game in games_local must equal the NFL-wide row (date + PT time)
    sf_local = {(g["date"], g["start_pt"]) for g in local if g["sport"] == "nfl"}
    sf_all = {(g["date"], g["start_pt"]) for g in nfl_all if g.get("is_sf") and g.get("start_min") is not None}
    match = sf_local & sf_all
    only_local = sorted(d_ for d_, t in sf_local if (d_, t) not in sf_all)
    only_all = sorted(d_ for d_, t in sf_all if not any(dl == d_ for dl, _ in sf_local))
    print(f"49ers cross-check : {len(match)}/{len(sf_all)} league rows match club rows exactly; "
          f"club rows w/o league-time match: {only_local or 'none'} | league rows w/o club match: {only_all or 'none'}")
    # expected non-matches: 2027-01-10 (both club and league rows are now TBD - Wk 18 games
    # have no official time yet, so no timed row to match) and 2026-08-13 (preseason league
    # row time added from Sporting News 21:00 ET = 18:00 PT; club time from ESPN event data)
    if set(only_local) - {'2027-01-10', '2026-08-13'}:
        flag("IRREGULARITY", f"49ers rows whose times disagree between 49ers.com and the league table: {only_local}")
    if only_all:
        flag("IRREGULARITY", f"league 49ers rows missing from the club list: {only_all}")


    per = {}
    for g in mlb:
        if "away_id" not in g:
            continue
        for t in (g["away_id"], g["home_id"]):
            per[t] = per.get(t, 0) + 1
    missing = [t for t in TEAMS if t not in per]
    print(f"MLB teams seen    : {len(per)}/30  missing: {missing or 'none'}")
    lo, hi = min(per.values()), max(per.values())
    expect = 2 * meta['totals']['mlb_games'] / len(TEAMS)
    print(f"Games per team    : min {lo}, max {hi}; exact mean {expect:.1f}")
    odd = {TEAMS[t]['abbr']: n for t, n in per.items() if abs(n - expect) > 3}
    print(f"Teams >3 from mean: {odd or 'none'}")
    print(f"Giants (137)      : {per.get(137)} games | Athletics (133): {per.get(133)} games")
    early = [g for g in mlb if g.get("start_min") is not None and g["start_min"] < 360]
    print(f"MLB starts <6AM PT: {len(early)}  {[g['date'] for g in early][:5]}")
    fully_free = [x for x in days if x["status"] == "FREE"]
    unconf = [x for x in days if x["status"] == "UNCONFIRMED"]
    notfree_tbd = [x for x in days if x["status"] == "NOT FREE — TIME TBD"]
    print(f"Days fully FREE   : {len(fully_free)}")
    print(f"Days NOT FREE(TBD): {len(notfree_tbd)} (game will play/air, kickoff TBD or estimated windows)")
    print(f"Days UNCONFIRMED  : {len(unconf)} (conditional playoff/qualification markers only)")
    no_free = [x for x in days if x["status"] == "FULLY BOOKED"]
    print(f"Days FULLY BOOKED : {len(no_free)}")
    partial = [x for x in days if x["status"] == "PARTIAL"]
    print(f"Days PARTIAL      : {len(partial)}; avg free on those days "
          f"{sum(x['free_minutes'] for x in partial)/max(1,len(partial)):.0f} min")
    not_asserted = [x for x in days if x["status"] in ("NOT FREE — TIME TBD", "UNCONFIRMED")]
    print(f"NO free time asserted on {len(not_asserted)} days "
          f"({len(notfree_tbd)} NOT FREE-TBD + {len(unconf)} UNCONFIRMED) - the site reports no free "
          f"windows and 0 free minutes there (user rule: WWO-covered / TBD days are NOT free)")
    print(f"Flags raised      : {len(flags)}")
    kinds = {}
    for f in flags:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    print(f"  by kind         : {kinds}")
    print(f"Verification checks: {'PASS' if ok else 'SEE !! LINES ABOVE'}")

    # ---- index.html JS syntax check (added 2026-09-15) --------------------------
    # The 2026-09-14 deploy shipped a fatal JS syntax error (a missing closing backtick
    # in the games-table template literal) that made the whole site load no data.
    # Parse the inline script with node --check when node is available.
    html = open(os.path.join(ROOT, "index.html")).read()
    m = re.search(r"<script>([\s\S]*)</script>", html)
    js_path = os.path.join(ROOT, "data", "processed", "_app_check.js")
    if m:
        open(js_path, "w").write(m.group(1))
        try:
            subprocess.run(["node", "--check", js_path], check=True, capture_output=True)
            print("index.html JS   : syntax OK (node --check)")
        except FileNotFoundError:
            print("index.html JS   : node not installed - SKIPPED syntax check (install node!)")
        except subprocess.CalledProcessError as e:
            ok = False
            print("!! index.html inline JavaScript has a SYNTAX ERROR - the deployed site would show no data:")
            print("   " + e.stderr.decode()[:800].replace("\n", "\n   "))
        finally:
            if os.path.exists(js_path):
                os.remove(js_path)

    # ---- UI logic invariant test (added 2026-09-17) ----------------------------
    # Executes the SHIPPED index.html helpers (windows() + status rule, extracted
    # verbatim) against the generated data and re-asserts the invariants behind the
    # user's reported bug fix: no day with a tracked football game renders FREE, and
    # no NOT FREE / UNCONFIRMED day asserts any free time.
    ui_test = os.path.join(ROOT, "scripts", "ui_logic_test.js")
    try:
        r = subprocess.run(["node", ui_test], check=True, capture_output=True)
        line = r.stdout.decode().strip().splitlines()
        print("UI logic test   : " + (line[-1] if line else "PASS"))
    except FileNotFoundError:
        print("UI logic test   : node not installed - SKIPPED (install node!)")
    except subprocess.CalledProcessError as e:
        ok = False
        print("!! UI LOGIC TEST FAILED - the football-day bug may be back:")
        print("   " + ((e.stdout or b"").decode() + (e.stderr or b"").decode())[:1500].replace("\n", "\n   "))

    write_markdown(days, meta, flags, mlb, nfl_all, local, cond, per, nba_nhl, wwo_ncaaf, wnba)
    return days, flags


def write_markdown(days, meta, flags, mlb, nfl_all, local, cond, per, nba_nhl, wwo_ncaaf, wnba_all=()):
    L = []; A = L.append
    A("# ScheduleFreeTime - Verified Master Schedule (Aug 1, 2026 - Feb 28, 2027)")
    A("")
    A("Every line below is transcribed from a documented source; see `docs/VERIFICATION.md` for the")
    A("source list, the manual-review links, and every irregularity that was flagged.")
    A("")
    A(f"- Generated by `scripts/build.py` (no manual entry). Data snapshot: **{meta['generated_utc']}**.")
    A(f"- Timezone: **{meta['timezone']}**")
    t = meta["totals"]
    A(f"- Counts: **{t['mlb_games']} MLB games** (all 30 clubs, regular season), "
      f"**{t['mlb_postseason_tbd']} MLB postseason games with unconfirmed times**, "
      f"**{t['local_games']}** blocking 49ers / Earthquakes / Stanford / Cal games, "
      f"**{t['nba_games']} Warriors (NBA)** + **{t['nhl_games']} Sharks (NHL)** games, "
      f"**{t['nfl_reg_games']} + {t['nfl_pre_games']} league-wide NFL games** (all block; "
      f"{t['wwo_nfl_matched']} carry the Westwood One national-radio badge; all "
      f"{t['nfl_pre_games']} preseason games now have kickoff times), "
      f"**{t.get('wnba_games',0)} Valkyries (WNBA) games** ({t.get('wnba_blocking',0)} on 95.7 The Game), "
      f"**{t['wwo_ncaaf']} Westwood One NCAA football broadcasts**, "
      f"**{t['nfl_window_rows']} NFL TBD/estimated broadcast windows** "
      f"({t['nfl_windows_official']} official incl. Super Bowl LXI, "
      f"{t['nfl_windows_estimated']} estimated: every playoff game + Sat Dec 26 / Jan 2 / "
      f"Jan 9 + Wk-18 Sunday + Pro Bowl), "
      f"**{t['conditional_days']} conditional playoff/ACC/CFP day markers**.")
    A(f"- Average durations used to block time: MLB {meta['durations_minutes']['mlb']}m, "
      f"NFL {meta['durations_minutes']['nfl']}m, NCAA {meta['durations_minutes']['ncaa']}m, "
      f"MLS {meta['durations_minutes']['mls']}m, NBA {meta['durations_minutes']['nba']}m, "
      f"NHL {meta['durations_minutes']['nhl']}m (research sources in docs/VERIFICATION.md; "
      f"the UI lets you change them and recompute). The Super Bowl blocks 225m "
      f"(~3h45m researched broadcast length); the Pro Bowl flag-football game 120m.")
    A(f"- Free-time rule: a game blocks if it is in ANY tracked league - MLB (any club, incl. "
      f"postseason), NFL (all 32 clubs: preseason, regular season, postseason, Pro Bowl, "
      f"Super Bowl - TBD until confirmed), Earthquakes, Stanford, Cal, Warriors (NBA), "
      f"Sharks (NHL) or the Westwood One NCAA football showcase. A day on which any tracked "
      f"game WILL be played/aired but its kickoff is not official is marked **NOT FREE - TIME "
      f"TBD**: estimated windows (clearly labeled, from documented 2025-26 postseason / "
      f"WWO-air-time / league-window patterns) block where predictable, and **no free time is "
      f"asserted or reported on that day at all** (Free min = 0 means 'not asserted', not "
      f"'free'). Days carrying only conditional qualification markers (MLS playoffs, "
      f"ACC/CFP/bowls) stay UNCONFIRMED and likewise assert no free time.")
    A("")
    A("## High-priority clubs: San Francisco Giants + Athletics + 49ers + Warriors + Sharks")
    A("")
    A("### Giants & Athletics (MLB)")
    A("")
    A("| Date | PT start | Matchup |")
    A("|---|---|---|")
    for g in sorted([g for g in mlb if g.get("priority")], key=lambda x: (x["date"], x["start_min"])):
        star = " **(home)**" if g["home_id"] in HI_PRIORITY else ""
        A(f"| {g['date']} | {g['start_pt']} PT | {g['away']} @ {g['home']}{star} |")
    A("")
    A(f"Giants: {per.get(137)} games in window - Athletics: {per.get(133)} games in window.")
    A("")
    A("### 49ers (every game, preseason + regular season)")
    A("")
    A("| Date | PT start | Game | Phase |")
    A("|---|---|---|---|")
    for g in sorted([g for g in local if g["sport"] == "nfl"], key=lambda x: (x["date"], x.get("start_min") or 0)):
        st = (g.get("start_pt") or "TBD") + (" PT" if g.get("start_pt") and g.get("start_pt") != "TBD" else "")
        A(f"| {g['date']} | {st} | {g['label']} | {g.get('phase','')} |")
    A("")
    A(f"49ers: {len([g for g in local if g['sport'] == 'nfl'])} games in window (preseason + regular "
      f"season; the Week 18 game @ Arizona is officially TBD along with every other Wk-18 game). "
      f"49ers playoff games would fall on the Jan/Feb postseason days, which are already NOT FREE "
      f"with estimated windows because Westwood One airs every playoff game.")
    A("")
    A("### Warriors (NBA, every game - all on 95.7 The Game)")
    A("")
    A("| Date | PT start | Game | Phase | Review |")
    A("|---|---|---|---|---|")
    for g in sorted([g for g in nba_nhl if g["sport"] == "nba"], key=lambda x: (x["date"], x["start_min"])):
        A(f"| {g['date']} | {g['start_pt']} PT ({g['start_et']} ET) | {g['label']} | {g['phase']} | [espn]({g['review']}) |")
    A("")
    A("### Sharks (NHL, every game - regular season on 98.5 KFOX; preseason select/unknown)")
    A("")
    A("| Date | PT start | Game | Phase | Blocks? | Review |")
    A("|---|---|---|---|---|---|")
    for g in sorted([g for g in nba_nhl if g["sport"] == "nhl"], key=lambda x: (x["date"], x["start_min"])):
        A(f"| {g['date']} | {g['start_pt']} PT ({g['start_et']} ET) | {g['label']} | {g['phase']} | "
          f"{'listed only' if g.get('info_only') else 'yes'} | [espn]({g['review']}) |")
    A("")
    A("### Golden State Valkyries (WNBA - all games on the Audacy app; 95.7 The Game over the air)")
    A("")
    A("| Date | PT start | Game | Phase | Blocks? | Review |")
    A("|---|---|---|---|---|---|")
    for g in sorted([g for g in nba_nhl if False] + wnba_all, key=lambda x: (x["date"], x.get("start_min") or 0)):
        A(f"| {g['date']} | {g.get('start_pt') or '**TBD**'} | {g['label']} | {g['phase']} | "
          f"{'listed only (Audacy app)' if g.get('info_only') else 'yes (95.7 The Game)'} | [review]({g['review']}) |")
    A("")
    A("## 49ers / Earthquakes / Stanford / Cal - every blocking game")
    A("")
    A("| Date | PT start | Game | Phase | Radio (Bay Area) | Source |")
    A("|---|---|---|---|---|---|")
    for g in sorted(local, key=lambda x: (x["date"], x.get("start_min") or 0)):
        st = (g.get("start_pt") or "TBD") + (" PT" if g.get("start_pt") and g.get("start_pt") != "TBD" else "")
        A(f"| {g['date']} | {st or '**TBD**'} | {g['label']} | {g.get('phase','')} | {g.get('radio', '-')} | [link]({g.get('source', '')}) |")
    A("")
    A("## All-NFL, every game (league-wide; BLOCKS free time)")
    A("")
    A("Regular season from the official week-by-week table "
      "(https://www.pro-football-reference.com/years/2026/games.htm, fetched 2026-09-11, weeks 2-17 "
      "re-verified 2026-09-15 vs nfl.com + the WWO page); preseason matchups from "
      "https://www.pro-football-reference.com/years/2026/preseason.htm with kickoff times from "
      "Sporting News' full preseason schedule (cross-checked vs Yahoo/Fox News/CableTV, and vs the "
      "officially sourced 49ers times). Week 18 is stored as TBD exactly as nfl.com prints it. "
      "Postseason/Saturday window rows (marked 'estimated window' / 'official') come from "
      "data/raw/nfl_2027_postseason_tbd.txt - dates verified against ESPN's live event feed, "
      "windows estimated from the 2025-26 postseason pattern and WWO air times, Super Bowl LXI "
      "kickoff OFFICIAL via ESPN event 401873270. Times after 2026-09-15 are subject to NFL flex "
      "scheduling for Sunday-window games. Every row with a kickoff time blocks free time; TBD "
      "rows and estimated windows mark the day NOT FREE - TIME TBD instead of asserting free time.")
    A("")
    A("| Date | PT | ET | Game | Status | Review link |")
    A("|---|---|---|---|---|---|")
    for g in sorted(nfl_all, key=lambda x: (x["date"], x.get("start_min") is None, x.get("start_min") or 0)):
        pt = (g.get("start_pt") + " PT") if g.get("start_pt") and g.get("start_pt") != "TBD" else "**TBD**"
        et = g.get("start_et", "-")
        if g.get("official"):
            st = g.get("result") or "official kickoff (ESPN)"
        elif g.get("estimated"):
            st = "estimated window - NOT FREE"
        elif g.get("tbd_time"):
            st = g.get("result") or "TBD kickoff (nfl.com)"
        else:
            st = g.get("result") or "scheduled"
        radio = f" 📻 WWO {g['wwo_slot']}" if g.get("wwo") else ""
        A(f"| {g['date']} ({g['week']}) | {pt} | {et} ET | {g['label']}{radio} | {st} | [box]({g.get('review','')}) |")
    A("")
    A("## Westwood One national radio (Bay Area: KNBR 680 AM / 104.5 FM + KTCT 1050 AM)")
    A("")
    A("Every primetime NFL game (TNF/SNF/MNF), 8 of the 9 international games (all except the "
      "Sep 27 Rio game - see the WWO_RIO_EXCLUDED flag), Thanksgiving + Black Friday + Christmas, "
      "late-season Saturday games, every playoff game and Super Bowl LXI air nationally on Westwood "
      "One and in the Bay Area on KNBR (subject to WWO's own pre-emption caveat for local conflicts). "
      "WWO NFL broadcasts do NOT duplicate the league rows: the matching league-table rows carry the "
      "📻 badge, and the TBD Saturday/Week-18/postseason broadcasts block through the estimated "
      "window rows above. WWO air times are the pregame-show start (MNF 7:00 PM ET, SNF/TNF 7:30 PM "
      "ET, internationals 9:15 AM ET); blocking always uses the league kickoff + the 192-min NFL "
      "average (225 min for the Super Bowl). "
      "Source for every broadcast: https://www.westwoodonesports.com/nfl-schedule/ (transcribed "
      "2026-09-14 into data/raw/westwoodone_nfl_2026.txt, re-verified row-for-row 2026-09-15; "
      "per-event links below).")
    A("")
    A("| Date | PT kickoff | Game | WWO slot | WWO event |")
    A("|---|---|---|---|---|")
    for g in sorted([g for g in nfl_all if g.get("wwo")], key=lambda x: (x["date"], x.get("start_min") or 0)):
        A(f"| {g['date']} | {g.get('start_pt','TBD')} PT | {g['label']} | {g.get('wwo_slot','')} | "
          f"[event]({g.get('wwo_event','')}) |")
    A("")
    A("### Westwood One NCAA football showcase (Saturdays; blocks free time)")
    A("")
    A("| Date | PT block start | Game | Kickoff status | Review |")
    A("|---|---|---|---|---|")
    for g in sorted(wwo_ncaaf, key=lambda x: (x["date"], x.get("start_min") or 0)):
        pt = (g.get("start_pt") + " PT") if g.get("start_pt") and g.get("start_pt") != "TBD" else "**TBD**"
        if g.get("estimated"):
            ks = "TBD - estimated showcase slot (day NOT FREE)"
        elif g.get("start_pt"):
            ks = "confirmed/reported kickoff"
        else:
            ks = "TBD - no window"
        A(f"| {g['date']} | {pt} | {g['label']} | {ks} | [event]({g['review']}) |")
    A("")
    A("## Conditional days (unconfirmed; never block)")
    A("")
    A("MLS playoff days apply to the San Jose Earthquakes only if they qualify (Decision Day Nov 7, "
      "2026 decides it; SJ's Decision Day match itself is a real scheduled game in games_local.json). "
      "ACC/CFP days apply to Stanford or Cal only if they qualify. Bowl games for Stanford/Cal could "
      "fall on any bowl date Dec 12, 2026 - Jan 1, 2027 once selected on Dec 6 - not day-marked; "
      "re-run the build after Dec 7, 2026 for those. (The NFL postseason days, by contrast, are NOT "
      "conditional - Westwood One airs every playoff game regardless of who plays, so those days are "
      "already NOT FREE with estimated windows; once real kickoffs are announced, replace the "
      "estimates and re-run.)")
    A("")
    A("| Date | League | Conditional entry |")
    A("|---|---|---|")
    for g in sorted(cond, key=lambda x: (x["date"], x["sport"])):
        A(f"| {g['date']} | {g['sport']} | {g['label']} |")
    A("")
    A("## Day-by-day free time (America/Los_Angeles)")
    A("")
    A("| Date | Day | Status | Blocking games | NFL-all games | Free windows (PT) | Free min | Flags |")
    A("|---|---|---|---|---|---|---|---|")
    for x in days:
        fw = "; ".join(f"{w['start_t']}-{w['end_t']}" for w in x["free"]) or "none"
        if x["status"] == "NOT FREE — TIME TBD":
            fw = (f"NOT AVAILABLE - {x['tbd_count']} TBD game(s) + {x['estimated_count']} estimated "
                  f"window(s); free time NOT asserted")
        elif x["status"] == "UNCONFIRMED":
            fw = "NOT ASSERTED - conditional marker(s) may add games; free time NOT asserted"
        A(f"| {x['date']} | {x['weekday']} | {x['status']} | {x['game_count']} | {x['nfl_all_count']} | {fw} | "
          f"{x['free_minutes']} | {'YES' if x['tbd_count'] or x['estimated_count'] else ''} |")
    A("")
    A("Legend for the Free min column: **0 on a NOT FREE - TIME TBD or UNCONFIRMED day means 'free time")
    A("not asserted', not 'free'**. On those days a tracked game will definitely be played/aired (its")
    A("kickoff or matchup is not official yet) or a conditional playoff/qualification event may add a")
    A("game, so the site reports NO free windows there - per the rule that any covered game means free")
    A("time NOT available. The arithmetic windows are kept in `provisional_free` in")
    A("`data/processed/free_time.json` for reference only and never shown as free time.")
    A("")
    A("## Every MLB game, by date (all 30 clubs)")
    A("")
    A("Format: `PT start - AWAY @ HOME` (times are America/Los_Angeles; **bold** = Giants or Athletics).")
    A("")
    bydate = {}
    for g in mlb:
        bydate.setdefault(g["date"], []).append(g)
    for d in sorted(bydate):
        gs = sorted(bydate[d], key=lambda x: x.get("start_min") or 0)
        A(f"### {d} ({len(gs)} game{'s' if len(gs)!=1 else ''})")
        for g in gs:
            if g.get("tbd_count"):
                A(f"- **TBD** - {g['tbd_count']} MLB postseason game(s); teams and start times unconfirmed")
                continue
            b = "**" if g.get("priority") else ""
            A(f"- {g['start_pt']} PT - {b}{g['away']} @ {g['home']}{b}")
        A("")
    pr = meta.get("postseason_resolution")
    if pr and pr.get("as_of"):
        A(f"## 2026 MLB postseason resolution (as of {pr['as_of']}; clinches OFFICIAL, projections NOT final)")
        A("")
        A(f"Resolves part of the 53 TBD postseason placeholder games from {meta['totals'].get('mlb_clinched', 0)} official clinches.")
        A("")
        A("Clinched (mlb.com official tracker, fetched live " + pr["as_of"] + "):")
        A("")
        for c in pr["clinched"]:
            A(f"- **{c['team']}** ({c['league']}) - {c['detail']} ([source]({c['url']}))")
        A("")
        if pr["wcr_series"]:
            A("Projected Wild Card matchups (mlb.com playoff picture, " + pr["as_of"] +
              " - listed in seeding order; seeds can still move through Sep 27):")
            A("")
            for s in pr["wcr_series"]:
                A(f"- {s['league']}: {s['home']} vs {s['away']}")
            A("")
        if pr["races"]:
            A("Tight races that keep the projections open:")
            A("")
            for r_ in pr["races"]:
                A(f"- {r_}")
            A("")
        A("**Kickoff times: all 53 remain officially TBD** - the MLB Stats API returns the 07:33:00Z "
          "placeholder for every one (re-verified live " + pr["as_of"] + "); MLB announces postseason "
          "times closer to each round (typically ~1 week out). The 53 games / 28 dates are unchanged.")
        A("")
        A("Sources: " + " · ".join(f"[source {i+1}]({u})" for i, u in enumerate(pr["sources"])))
        A("")
    A("## Irregularities flagged for review")
    A("")
    for f in flags:
        A(f"- **{f['kind']}** - {f['msg']}")
    A("")
    open(os.path.join(ROOT, "schedules.md"), "w").write("\n".join(L) + "\n")
    print(f"wrote schedules.md ({len(L)} lines)")


if __name__ == "__main__":
    main()
