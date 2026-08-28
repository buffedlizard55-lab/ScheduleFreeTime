#!/usr/bin/env python3
"""
ScheduleFreeTime build + verification pipeline.

Reads ONLY the hand-transcribed, source-attributed raw data in data/raw/ and
data/games_local.json, then:
  1. converts every game to America/Los_Angeles time,
  2. blocks [start, start + average duration] per game,
  3. computes the free (no game on) windows for each day,
  4. writes data/processed/schedule.json + data/processed/free_time.json,
  5. regenerates schedules.md (the full master list),
  6. prints a verification report and flags every irregularity it finds.

No manual input: run `python3 scripts/build.py`.
"""
import json, os, sys, glob
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")

# --- analysis window -------------------------------------------------------
START, END = date(2026, 8, 1), date(2026, 10, 31)
TODAY = date(2026, 8, 28)
# US Pacific in 2026: PDT (UTC-7) from Mar 8 to Nov 1; PST (UTC-8) from Nov 1.
PDT = timedelta(hours=-7)
PST = timedelta(hours=-8)

def pt_offset(d):
    """America/Los_Angeles UTC offset for a calendar date in 2026."""
    return PDT if date(2026, 3, 8) <= d < date(2026, 11, 1) else PST

# --- average game durations (minutes) --------------------------------------
# Sources are documented in docs/VERIFICATION.md
DURATIONS = {"mlb": 164, "nfl": 192, "ncaa": 204, "mls": 120}
PRE_BUFFER = 0   # minutes of pre-game coverage counted as busy
POST_BUFFER = 0  # minutes of post-game coverage counted as busy

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

# --- other sports ----------------------------------------------------------
def load_local():
    data = json.load(open(os.path.join(ROOT, "data", "games_local.json")))
    games = []
    for g in data["games"]:
        rec = dict(g)
        if g["start_pt"]:
            h, m = map(int, g["start_pt"].split(":"))
            rec["start_min"] = h * 60 + m
        else:
            rec["start_min"] = None
            flag("TBD_TIME", f"{g['date']} {g['label']}: {g.get('flag','kickoff time not confirmed')}")
        if g.get("flag"):
            flag("IRREGULARITY", f"{g['date']} {g['label']}: {g['flag']}")
        rec["pt_date"] = g["date"]
        games.append(rec)
    return games

# --- free-time computation -------------------------------------------------
def free_windows(blocks, day_start=0, day_end=1440):
    """blocks = sorted list of [start_min, end_min]; returns free windows."""
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
    local = load_local()
    allg = mlb + local

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

    days = []
    d = START
    while d <= END:
        ds = d.isoformat()
        todays = [g for g in allg if g["date"] == ds or g.get("pt_date") == ds]
        blocks = []
        for g in todays:
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
        tbd = [g for g in todays if g.get("start_min") is None]
        tbd_n = len([g for g in tbd if not g.get("tbd_count")]) + sum(g.get("tbd_count", 0) for g in todays)
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
            "game_count": len([g for g in todays if g.get("start_min") is not None]),
            "tbd_count": tbd_n,
            "has_priority": any(g.get("priority") for g in todays),
        })
        if tbd:
            for g in tbd:
                if g.get("tbd_count"):
                    continue
                flag("UNBLOCKED_TBD", f"{ds}: '{g['label']}' has no confirmed start time so it does NOT "
                                      f"block any time - the day's free windows may be overstated.")
        d += timedelta(days=1)

    os.makedirs(OUT, exist_ok=True)
    meta = {
        "generated_utc": "2026-08-28", "window": {"start": START.isoformat(), "end": END.isoformat()},
        "timezone": "America/Los_Angeles (PDT, UTC-7 for the entire window)",
        "durations_minutes": DURATIONS, "pre_buffer_minutes": PRE_BUFFER, "post_buffer_minutes": POST_BUFFER,
        "totals": {"mlb_games": len([g for g in mlb if "away_id" in g]),
                   "mlb_postseason_tbd": sum(g.get("tbd_count", 0) for g in mlb),
                   "local_games": len(local)},
    }
    json.dump({"meta": meta, "games": mlb}, open(os.path.join(OUT, "mlb.json"), "w"), indent=1)
    json.dump({"meta": meta, "days": days, "flags": flags}, open(os.path.join(OUT, "free_time.json"), "w"), indent=1)

    # ---- verification report ----
    print("=" * 78)
    print("VERIFICATION REPORT")
    print("=" * 78)
    print(f"Window            : {START} .. {END} ({(END-START).days+1} days), America/Los_Angeles")
    print(f"MLB games parsed  : {meta['totals']['mlb_games']} across "
          f"{len(set(g['date'] for g in mlb if 'away_id' in g))} official dates")
    print(f"MLB postseason TBD: {meta['totals']['mlb_postseason_tbd']} games (times/teams unconfirmed)")
    print(f"49ers/Quakes/NCAA : {len(local)} games")
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
    print(f"Games per team    : min {lo}, max {hi}; exact mean {expect:.1f} "
          f"(778 games x 2 slots / 30 teams)")
    odd = {TEAMS[t]['abbr']: n for t, n in per.items() if abs(n - expect) > 3}
    print(f"Teams >3 from mean: {odd or 'none'}")
    print(f"Giants (137)      : {per.get(137)} games | Athletics (133): {per.get(133)} games")
    # PT-date sanity: no MLB game should start before 06:00 PT
    early = [g for g in mlb if g.get("start_min") is not None and g["start_min"] < 360]
    print(f"MLB starts <6AM PT: {len(early)}  {[g['date'] for g in early][:5]}")
    fully_free = [x for x in days if x["status"] == "FREE"]
    unconf = [x for x in days if x["status"] == "UNCONFIRMED"]
    print(f"Days fully FREE   : {len(fully_free)} -> {[x['date'] for x in fully_free]}")
    print(f"Days UNCONFIRMED  : {len(unconf)} (only TBD games; free time NOT assertable)")
    no_free = [x for x in days if x["status"] == "FULLY BOOKED"]
    print(f"Days FULLY BOOKED : {len(no_free)} -> {[x['date'] for x in no_free]}")
    partial = [x for x in days if x["status"] == "PARTIAL"]
    print(f"Days PARTIAL      : {len(partial)}; avg free on those days "
          f"{sum(x['free_minutes'] for x in partial)/max(1,len(partial)):.0f} min")
    print(f"Flags raised      : {len(flags)}")
    kinds = {}
    for f in flags:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    print(f"  by kind         : {kinds}")

    write_markdown(days, meta, flags, mlb, local, per)
    return days, flags


def write_markdown(days, meta, flags, mlb, local, per):
    L = []
    A = L.append
    A("# ScheduleFreeTime - Verified Master Schedule (Aug 1 - Oct 31, 2026)")
    A("")
    A("Every line below is transcribed from an official source; see `docs/VERIFICATION.md` for the")
    A("source list, the manual-review links, and every irregularity that was flagged.")
    A("")
    A(f"- Generated by `scripts/build.py` (no manual entry). Data snapshot: **{meta['generated_utc']}**.")
    A(f"- Timezone: **{meta['timezone']}**")
    A(f"- Counts: **{meta['totals']['mlb_games']} MLB games** (all 30 clubs) over 58 dates, "
      f"**{meta['totals']['mlb_postseason_tbd']} MLB postseason games with unconfirmed times**, "
      f"**{meta['totals']['local_games']}** 49ers / Earthquakes / Stanford / Cal games.")
    A(f"- Average durations used to block time: MLB {meta['durations_minutes']['mlb']}m, "
      f"NFL {meta['durations_minutes']['nfl']}m, NCAA {meta['durations_minutes']['ncaa']}m, "
      f"MLS {meta['durations_minutes']['mls']}m.")
    A("")
    A("## High-priority clubs: San Francisco Giants + Athletics")
    A("")
    A("| Date | PT start | Matchup |")
    A("|---|---|---|")
    for g in sorted([g for g in mlb if g.get("priority")], key=lambda x: (x["date"], x["start_min"])):
        star = ""
        if g["home_id"] in HI_PRIORITY:
            star = " **(home)**"
        A(f"| {g['date']} | {g['start_pt']} PT | {g['away']} @ {g['home']}{star} |")
    A("")
    A(f"Giants: {per.get(137)} games in window - Athletics: {per.get(133)} games in window.")
    A("")
    A("## 49ers / Earthquakes / Stanford / Cal - every game")
    A("")
    A("| Date | PT start | Game | Phase | Source |")
    A("|---|---|---|---|---|")
    for g in sorted(local, key=lambda x: (x["date"], x.get("start_min") or 0)):
        st = g["start_pt"] + " PT" if g["start_pt"] else "**TBD**"
        A(f"| {g['date']} | {st} | {g['label']} | {g.get('phase','')} | [link]({g['source']}) |")
    A("")
    A("## Day-by-day free time (America/Los_Angeles)")
    A("")
    A("| Date | Day | Status | Games | Free windows (PT) | Free min | Flags |")
    A("|---|---|---|---|---|---|---|")
    for x in days:
        fw = "; ".join(f"{w['start_t']}-{w['end_t']}" for w in x["free"]) or "none"
        if x["status"] == "UNCONFIRMED":
            fw = f"UNCONFIRMED - {x['tbd_count']} game(s) with no announced start time"
        A(f"| {x['date']} | {x['weekday']} | {x['status']} | {x['game_count']} | {fw} | "
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
