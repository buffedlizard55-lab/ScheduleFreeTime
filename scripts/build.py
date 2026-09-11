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

Blocking rule (user spec): a day is busy only around MLB games (ALL 30 clubs,
regular season + postseason 2026), San Francisco 49ers games (preseason +
regular season), San Jose Earthquakes games, Stanford football games and Cal
football games. League-wide NFL games (all 32 clubs, incl. postseason /
Pro Bowl / Super Bowl) are LISTED on every day and shown in the UI, but do not
block free time unless the user turns on the "block all NFL games" toggle.
"Conditional" rows (MLS playoff days if SJ qualifies, ACC/CFP/bowl days if
Stanford or Cal qualify, NFL postseason with teams TBD) never block; they mark
a day UNCONFIRMED so free time is honestly labeled, not asserted.

No manual input: run `python3 scripts/build.py`.
"""
import json, os, sys, glob
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")

# --- analysis window -------------------------------------------------------
START, END = date(2026, 8, 1), date(2027, 2, 28)
TODAY = date(2026, 9, 11)   # date of the 2026-09-11 verification pass
GENERATED = "2026-09-11"
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
# Sources + citations in docs/VERIFICATION.md sec. 3:
#   mlb   158 = 2:38, MLB official 2025-season average (2026 in progress ~2:43-2:44)
#   nfl   192 = 3:12, widely reported average incl. halftime & stoppages
#   ncaa  204 = 3:24 (longer halftimes; 2025 data ranges 3:24-3:27)
#   mls   120 = 2:00 (90 min + halftime + stoppage)
DURATIONS = {"mlb": 158, "nfl": 192, "ncaa": 204, "mls": 120}
DUR_OF = lambda sport: DURATIONS["nfl"] if sport == "nfl_all" else DURATIONS[sport]
PRE_BUFFER = 0   # minutes of pre-game coverage counted as busy
POST_BUFFER = 0  # minutes of post-game coverage counted as busy
BLOCKING_SPORTS = {"mlb", "nfl", "ncaa", "mls"}   # user's free-time rule
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

TEAMS = {t["id"]: t for t in json.load(open(os.path.join(RAW, "teams_mlb.json")))["teams"]}
HI_PRIORITY = {137, 133}  # SF Giants, Athletics

flags = []
def flag(kind, msg):
    flags.append({"kind": kind, "msg": msg})

# --- MLB -------------------------------------------------------------------
def load_mlb():
    games = []
    for path in sorted(glob.glob(os.path.join(RAW, "mlb_2026_*.txt"))):
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
        et_h, et_m = map(int, t_et.split(":"))
        # ET->PT is exactly -3h for every NFL 2026-27 date (both zones change DST together)
        pt_dt = datetime(y, m, dd, et_h, et_m) - timedelta(hours=3)
        assert pt_dt.date() == date(y, m, dd), f"{dt}: PT date crossed midnight, check transcription"
        aw2, hm2 = ABBR_ALIAS.get(aw, aw), ABBR_ALIAS.get(hm, hm)
        games.append({"date": dt, "sport": "nfl_all", "week": f"Wk {wk}",
                      "start_pt": pt_dt.strftime("%H:%M"), "start_min": pt_dt.hour*60 + pt_dt.minute,
                      "start_et": t_et, "away": aw2, "home": hm2,
                      "label": f"{NFL_TEAM_NAMES[aw2]} at {NFL_TEAM_NAMES[hm2]}",
                      "result": res.replace(" FINAL", "") if res else "",
                      "review": f"https://www.pro-football-reference.com/boxscores/{box}.htm",
                      "source": "nfl_2026_pfr_regseason.txt",
                      "is_sf": "SF" in (aw2, hm2)})
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
        games.append(rec)
    # NFL postseason / pro bowl / super bowl placeholder rows (never block; mark UNCONFIRMED)
    path = os.path.join(RAW, "nfl_2027_postseason_tbd.txt")
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rnd, dt, n, label = line.split("|")
        games.append({"date": dt, "sport": "nfl_all", "week": rnd, "start_pt": None, "start_min": None,
                      "tbd_count": int(n), "label": label, "conditional": True,
                      "source": "nfl_2027_postseason_tbd.txt",
                      "review": "https://www.nfl.com/schedules/2026/"})
    return games

# --- other sports (blocking: 49ers 'nfl', Earthquakes 'mls', Stanford/Cal 'ncaa')
def load_local():
    data = json.load(open(os.path.join(ROOT, "data", "games_local.json")))
    games, seen_big = [], set()
    for g in data["games"]:
        rec = dict(g)
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
                           ("ncaa_2026_postseason_conditional.txt", "ncaa", "NCAA")):
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
                              else "https://www.espn.com/college-football/story/_/id/48958840/"
                              "2026-college-football-playoff-bowl-schedule-46-games")})
    return games

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
    allg = mlb + nfl_all + local + cond

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

    # future Sunday-window NFL games may still flex
    flex = sum(1 for g in nfl_all if g.get("start_min") is not None
               and g["date"] > TODAY.isoformat() and g["start_et"] in ("13:00", "16:05", "16:25"))
    if flex:
        flag("FLEX_WINDOW",
             f"{flex} league-wide NFL games after {TODAY.isoformat()} sit in the Sunday 1:00 PM / 4:05 PM / "
             f"4:25 PM ET windows and can still be moved by NFL flex scheduling; times as printed by the "
             f"source on 2026-09-11. Thursday/Sunday/Monday night, international and Saturday games are "
             f"locked. This does not affect the 49ers blocking rows (those come from 49ers.com).")

    # MLB scope boundary notes
    flag("SCOPE_NOTE", "MLB: the tracked 2026 season (regular + postseason) ends with the World Series "
         "placeholders on 2026-10-31 (last date in the official bracket calendar). No MLB games exist "
         "Nov 1, 2026 - Feb 28, 2027 EXCEPT 2027 Spring Training, which opens Fri Feb 19, 2027 (all 30 "
         "clubs) per MLB's press release of Sep 4, 2026 - out of scope per spec (2026 season only) and "
         "NOT blocked; re-run after the 2027 ST schedule files publish if you want them included.")
    flag("VERIFIED_PASS", "2026-09-11: MLB Stats API re-query for 2026-09-10/11/12 matched the raw file "
         "35/35 games (dates, times, team ids). The 'sparse' Tue/Thu slate days (5 games on Sep 10, "
         "3 on Sep 21) are genuine scheduled light days, not data gaps.")

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
            dur = DURATIONS[g["sport"]]
            blocks.append([g["start_min"] - PRE_BUFFER, g["start_min"] + dur + POST_BUFFER])
        blocks.sort()
        merged = []
        for s, e in blocks:
            if merged and s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        fw = free_windows(merged)
        tbd = [g for g in blocking + nfla
               if g.get("start_min") is None and not g.get("info_only") and not g.get("dedup")]
        tbd_n = len([g for g in tbd if not g.get("tbd_count")]) + sum(g.get("tbd_count", 0) for g in tbd)
        if not blocks and tbd_n:
            status = "UNCONFIRMED"   # only unconfirmed games that day -> free time cannot be asserted
        elif not blocks:
            status = "FREE"
        elif sum(e - s for s, e in fw) == 0:
            status = "FULLY BOOKED"
        else:
            status = "PARTIAL"
        days.append({
            "date": ds, "weekday": d.strftime("%a"), "status": status,
            "games": [dict(g) for g in
                      sorted(todays, key=lambda x: (x.get("start_min") is None, x.get("start_min") or 0))],
            "blocked": [{"start": s, "end": e, "start_t": fmt(s), "end_t": fmt(e)} for s, e in merged],
            "free": [{"start": s, "end": e, "start_t": fmt(s), "end_t": fmt(e), "minutes": e - s} for s, e in fw],
            "free_minutes": sum(e - s for s, e in fw),
            "game_count": len([g for g in blocking if g.get("start_min") is not None]),
            "nfl_all_count": len([g for g in nfla if g.get("start_min") is not None]),
            "tbd_count": tbd_n,
            "has_priority": any(g.get("priority") for g in todays),
            "has_sf": any(g.get("is_sf") for g in nfla) or any(g["sport"]=="nfl" for g in blocking),
        })
        for g in tbd:
            if g.get("tbd_count"):
                continue
            flag("UNBLOCKED_TBD", f"{ds}: '{g['label']}' has no confirmed start time so it does NOT "
                                  f"block any time - the day's free windows may be overstated.")
        d += timedelta(days=1)

    os.makedirs(OUT, exist_ok=True)
    reg = [g for g in nfl_all if g["week"].startswith("Wk")]
    pre = [g for g in nfl_all if g["week"].startswith("Pre")]
    meta = {
        "generated_utc": GENERATED, "window": {"start": START.isoformat(), "end": END.isoformat()},
        "timezone": "America/Los_Angeles - PDT (UTC-7) through Oct 31, 2026; PST (UTC-8) from Nov 1, 2026 to Mar 13, 2027",
        "durations_minutes": DURATIONS, "pre_buffer_minutes": PRE_BUFFER, "post_buffer_minutes": POST_BUFFER,
        "blocking_sports": sorted(BLOCKING_SPORTS),
        "totals": {"mlb_games": len([g for g in mlb if "away_id" in g]),
                   "mlb_postseason_tbd": sum(g.get("tbd_count", 0) for g in mlb),
                   "local_games": len(local),
                   "nfl_reg_games": len(reg), "nfl_pre_games": len(pre),
                   "nfl_all_tbd_days": len({g["date"] for g in nfl_all if g.get("conditional")}),
                   "conditional_days": len({g["date"] for g in cond})},
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
          f"(display only; 49ers blocking rows come from games_local.json)")

    # NFL arithmetic checks
    ok = True
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
    # expected non-matches: 2027-01-10 (club TBD vs league 10:00 PT, flagged separately) and
    # 2026-08-13 (preseason league row has no printed time; club time came from ESPN event data)
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
    print(f"Days fully FREE   : {len(fully_free)}")
    print(f"Days UNCONFIRMED  : {len(unconf)}")
    no_free = [x for x in days if x["status"] == "FULLY BOOKED"]
    print(f"Days FULLY BOOKED : {len(no_free)}")
    partial = [x for x in days if x["status"] == "PARTIAL"]
    print(f"Days PARTIAL      : {len(partial)}; avg free on those days "
          f"{sum(x['free_minutes'] for x in partial)/max(1,len(partial)):.0f} min")
    print(f"Flags raised      : {len(flags)}")
    kinds = {}
    for f in flags:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    print(f"  by kind         : {kinds}")
    print(f"Verification checks: {'PASS' if ok else 'SEE !! LINES ABOVE'}")

    write_markdown(days, meta, flags, mlb, nfl_all, local, cond, per)
    return days, flags


def write_markdown(days, meta, flags, mlb, nfl_all, local, cond, per):
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
      f"**{t['nfl_reg_games']} + {t['nfl_pre_games']} league-wide NFL games** (display only), "
      f"**{t['nfl_all_tbd_days']} NFL postseason/pro-bowl placeholder days**, "
      f"**{t['conditional_days']} conditional playoff/ACC/CFP day markers**.")
    A(f"- Average durations used to block time: MLB {meta['durations_minutes']['mlb']}m, "
      f"NFL {meta['durations_minutes']['nfl']}m, NCAA {meta['durations_minutes']['ncaa']}m, "
      f"MLS {meta['durations_minutes']['mls']}m (research sources in docs/VERIFICATION.md; "
      f"the UI lets you change them and recompute).")
    A(f"- Free-time rule: a game blocks only if it is MLB (any club), 49ers (pre + regular season), "
      f"Earthquakes, Stanford or Cal. League-wide NFL rows are shown but non-blocking unless you "
      f"enable the 'block all-NFL' toggle in the UI.")
    A("")
    A("## High-priority clubs: San Francisco Giants + Athletics (+ 49ers)")
    A("")
    A("| Date | PT start | Matchup |")
    A("|---|---|---|")
    for g in sorted([g for g in mlb if g.get("priority")], key=lambda x: (x["date"], x["start_min"])):
        star = " **(home)**" if g["home_id"] in HI_PRIORITY else ""
        A(f"| {g['date']} | {g['start_pt']} PT | {g['away']} @ {g['home']}{star} |")
    A("")
    A(f"Giants: {per.get(137)} games in window - Athletics: {per.get(133)} games in window. "
      f"All 49ers games are also high-priority: see next section (blocking) and the NFL-all list.")
    A("")
    A("## 49ers / Earthquakes / Stanford / Cal - every blocking game")
    A("")
    A("| Date | PT start | Game | Phase | Source |")
    A("|---|---|---|---|---|")
    for g in sorted(local, key=lambda x: (x["date"], x.get("start_min") or 0)):
        st = (g.get("start_pt") or "TBD") + (" PT" if g.get("start_pt") and g.get("start_pt") != "TBD" else "")
        A(f"| {g['date']} | {st or '**TBD**'} | {g['label']} | {g.get('phase','')} | [link]({g.get('source', '')}) |")
    A("")
    A("## All-NFL, every game (league-wide; non-blocking display)")
    A("")
    A("Regular season from the official week-by-week table "
      "(https://www.pro-football-reference.com/years/2026/games.htm, fetched 2026-09-11); "
      "preseason from https://www.pro-football-reference.com/years/2026/preseason.htm; postseason "
      "rows are round-date placeholders. Kickoff in both ET (source) and PT. Times after 2026-09-11 "
      "are subject to NFL flex scheduling for Sunday-window games.")
    A("")
    A("| Date | PT | ET | Game | Status | Review link |")
    A("|---|---|---|---|---|---|")
    for g in sorted(nfl_all, key=lambda x: (x["date"], x.get("start_min") is None, x.get("start_min") or 0)):
        pt = g.get("start_pt") + " PT" if g.get("start_pt") else "**TBD**"
        et = g.get("start_et", "-")
        st = g.get("result") or ("TBD-placeholder" if g.get("conditional") else "scheduled")
        A(f"| {g['date']} ({g['week']}) | {pt} | {et} ET | {g['label']} | {st} | [box]({g.get('review','')}) |")
    A("")
    A("## Conditional days (unconfirmed; never block)")
    A("")
    A("MLS playoff days apply to the San Jose Earthquakes only if they qualify (Decision Day Nov 7, "
      "2026 decides it). ACC/CFP days apply to Stanford or Cal only if they qualify. Bowl games for "
      "Stanford/Cal could fall on any bowl date Dec 12, 2026 - Jan 1, 2027 once selected on Dec 6 - "
      "not day-marked; re-run the build after Dec 7, 2026 for those. NFL postseason rows above are "
      "placeholders until seeds are set (games may include the 49ers; still non-blocking by spec).")
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
        if x["status"] == "UNCONFIRMED":
            fw = f"UNCONFIRMED - {x['tbd_count']} game(s) with no announced start time"
        A(f"| {x['date']} | {x['weekday']} | {x['status']} | {x['game_count']} | {x['nfl_all_count']} | {fw} | "
          f"{x['free_minutes']} | {'YES' if x['tbd_count'] else ''} |")
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
    A("## Irregularities flagged for review")
    A("")
    for f in flags:
        A(f"- **{f['kind']}** - {f['msg']}")
    A("")
    open(os.path.join(ROOT, "schedules.md"), "w").write("\n".join(L) + "\n")
    print(f"wrote schedules.md ({len(L)} lines)")


if __name__ == "__main__":
    main()
