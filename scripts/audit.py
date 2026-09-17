#!/usr/bin/env python3
"""
Independent audit of data/processed/free_time.json ("second opinion" checker).

WHY THIS EXISTS
---------------
`scripts/build.py` both produces and verifies the free-time data, so a bug in its
window math or in its option handling would be invisible to its own report.  This
script re-implements the arithmetic from scratch (different code path, no import of
build.py), re-reads the raw transcriptions independently, and compares every day
against the generated file.  Run it after every `python3 scripts/build.py`:

    python3 scripts/build.py && python3 scripts/audit.py

It prints one line per check and exits non-zero if anything disagrees.

WHAT IT CHECKS
--------------
 1. day coverage          - 212 days Aug 1 2026 .. Feb 28 2027, no gaps/dupes
 2. window arithmetic     - recomputed free windows == stored free windows
 3. partition             - blocked + free == exactly 24h on every day
 4. overlap/order         - windows sorted, non-overlapping, inside 00:00-24:00
 5. status rule           - status matches the documented day-status model
 6. game census           - every raw row appears on its own day, once, no extras
 7. time conversion       - MLB UTC->PT and NFL/NBA/NHL ET->PT recomputed
 8. durations             - documented table == audit table; each game's interval fits its block
 9. priority flags        - Giants/A's/49ers/Quakes/NCAA/radio priority rules
10. high-priority census  - Giants/A's/49ers counts vs the raw files
11. MLB postseason        - 2026-09-17 resolved pass: per-date TBDxN counts vs the raw
                            file, EST estimated-window slots == raw slots (2025 pattern),
                            53 games / 28 dates, Oct 18 double-slot exception
12. playoff picture       - meta clinched/eliminated vs data/raw/mlb_2026_playoff_picture.json;
                            no Giants/Athletics row may exist on any postseason date
"""
import json, os, re, sys
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")

DUR = {"mlb": 164, "nfl": 192, "ncaa": 204, "mls": 120, "nba": 138, "nhl": 150, "wnba": 125}
DUR_OF = lambda s: DUR[{"nfl_all": "nfl", "ncaaw": "ncaa"}.get(s, s)]
BLOCKING = {"mlb", "nfl", "ncaa", "mls", "nfl_all", "nba", "nhl", "ncaaw", "wnba"}
PRIORITY_MLB_TEAMS = {137, 133}      # SF Giants, Athletics

problems, notes = [], []
def check(ok, label, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"   {detail}" if detail and not ok else ""))
    if not ok:
        problems.append(f"{label}: {detail}")
    return ok

def read_rows(fn):
    path = os.path.join(RAW, fn)
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line.split("|"))
    return out

def pt_offset(d):
    """America/Los_Angeles UTC offset (PDT before Nov 1 2026, PST after)."""
    return timedelta(hours=-7) if date(2026, 3, 8) <= d < date(2026, 11, 1) else timedelta(hours=-8)

def hhmm_to_min(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)

# ---------------------------------------------------------------- load output
data = json.load(open(os.path.join(PROC, "free_time.json")))
days = data["days"]
meta = data["meta"]
by_date = {d["date"]: d for d in days}

# ------------------------------------------------- 1. coverage / uniqueness
d0, d1 = date(2026, 8, 1), date(2027, 2, 28)
expect = [(d0 + timedelta(days=i)).isoformat() for i in range((d1 - d0).days + 1)]
check([d["date"] for d in days] == expect, "1. day coverage 212 consecutive days",
      f"got {len(days)} days")
check(len(by_date) == len(days), "1b. no duplicate dates")

# ------------------------------------ 2/3/4/5/8. per-day window arithmetic
bad_free = bad_part = bad_overlap = bad_dur = bad_status = []
for d in days:
    ds = d["date"]
    gs = [g for g in d["games"] if g["sport"] in BLOCKING and not g.get("dedup")]
    blocks = []
    for g in gs:
        if g.get("start_min") is None:
            continue
        dur = g.get("dur_override", DUR_OF(g["sport"]))
        if not (30 <= dur <= 300):
            bad_dur.append(f"{ds}:{g['sport']} dur={dur}")
        blocks.append((g["start_min"], g["start_min"] + dur))
    # every game's own interval must be fully inside the stored blocked windows
    for g in gs:
        if g.get("start_min") is None:
            continue
        dur = g.get("dur_override", DUR_OF(g["sport"]))
        s0, e0 = g["start_min"], g["start_min"] + dur
        if not any(b["start"] <= s0 and e0 <= b["end"] for b in d["blocked"]):
            bad_dur.append(f"{ds}:{g['sport']} {s0}-{e0} outside stored blocks")
    blocks.sort()
    merged = []
    for s, e in blocks:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    # free windows, recomputed independently (arithmetic windows of the day)
    free, cur = [], 0
    for s, e in merged:
        if s > cur:
            free.append((cur, min(s, 1440)))
        cur = max(cur, e)
    if cur < 1440:
        free.append((cur, 1440))
    if [(b["start"], b["end"]) for b in d["blocked"]] != [tuple(m) for m in merged]:
        bad_overlap.append(ds)
    # status model
    tbd = [g for g in gs if g.get("start_min") is None and not g.get("info_only")
           and not g.get("conditional")]
    tbd_n = len([g for g in tbd if not g.get("tbd_count")]) + sum(g.get("tbd_count", 0) for g in tbd)
    est_n = len([g for g in gs if g.get("start_min") is not None and g.get("estimated")])
    cond_n = len([g for g in d["games"] if g.get("conditional")])
    if tbd_n or est_n:
        want = "NOT FREE — TIME TBD"
    elif cond_n:
        want = "UNCONFIRMED"
    elif not merged:
        want = "FREE"
    elif sum(e - s for s, e in free) == 0:
        want = "FULLY BOOKED"
    else:
        want = "PARTIAL"
    if d["status"] != want:
        bad_status.append(f"{ds}: {d['status']} != {want}")
    # free-time assertion rule (2026-09-16 pass B): NOT FREE - TIME TBD and UNCONFIRMED
    # days assert NO free time - stored free must be [] with 0 minutes, and the
    # arithmetic windows must be preserved in `provisional_free`. Asserted days must
    # store the arithmetic windows in `free` (and no provisional_free).
    prov = [(p["start"], p["end"]) for p in d.get("provisional_free", [])]
    if want in ("NOT FREE — TIME TBD", "UNCONFIRMED"):
        if d["free"] != [] or d["free_minutes"] != 0:
            bad_free.append(ds + "/asserted-but-not-free")
        if prov != free:
            bad_free.append(ds + "/provisional")
        total = sum(e - s for s, e in prov) + sum(e - s for s, e in merged)
    else:
        if [(f["start"], f["end"]) for f in d["free"]] != free:
            bad_free.append(ds)
        if prov:
            bad_free.append(ds + "/provisional-on-asserted-day")
        if d["free_minutes"] != sum(e - s for s, e in free):
            bad_free.append(ds + "/minutes")
        total = sum(e - s for s, e in free) + sum(e - s for s, e in merged)
    if total != 1440:
        bad_part.append(f"{ds}={total}")

check(not bad_free, "2. recomputed free windows == stored (all 212 days)", str(bad_free[:6]))
check(not bad_overlap, "3. stored blocked list == recomputed merge", str(bad_overlap[:6]))
check(not bad_part, "4. blocked + free partition each day exactly 24h", str(bad_part[:6]))
check(not bad_status, "5. day status matches the documented rule", str(bad_status[:6]))

check(meta["durations_minutes"] == DUR, "8. documented durations (meta + UI defaults) == audit table",
      f'{meta["durations_minutes"]} vs {DUR}')
check(not bad_dur, "8b. every game interval fits its stored block; durations in range", str(bad_dur[:6]))

# ------------------------------------------------- 6. census of raw -> days
raw_rows = {}    # (date, sport) -> list of (label-ish key, start_min or None)

def add(ds, sport, k, start):
    raw_rows.setdefault((ds, sport), []).append((k, start))

# MLB: date|HHMM-away-home[,...]  or  date|TBDxN[|EST-hh:mm,hh:mm|round|tv]
mlb_ids = set()
mlb_post_tbd = {}    # date -> TBDxN (postseason placeholder games)
mlb_post_est = {}    # date -> [start_min,...] (estimated 2025-pattern slots, PT)
for fn in sorted(os.listdir(RAW)):
    if not fn.startswith("mlb_2026_") or not fn.endswith(".txt"):
        continue
    if fn == "mlb_2026_postseason_resolution.txt":
        continue   # annotations about the placeholders, not a game schedule
    for parts in read_rows(fn):
        ds, body = parts[0], parts[1]
        if body.startswith("TBDx"):
            add(ds, "mlb", ("postseason", int(body[4:])), None)
            mlb_post_tbd[ds] = int(body[4:])
            if len(parts) > 2 and parts[2].startswith("EST-"):
                for slot in [x for x in parts[2][4:].split(",") if x]:
                    add(ds, "mlb", ("postseason-est", slot), hhmm_to_min(slot))
                    mlb_post_est.setdefault(ds, []).append(hhmm_to_min(slot))
            continue
        y, m, dd = map(int, ds.split("-"))
        for item in body.split(","):
            hhmm, matchup = item.split(":")
            away, home = matchup.split("-")
            utc = datetime(y, m, dd, tzinfo=timezone.utc) + timedelta(
                hours=int(hhmm[:2]), minutes=int(hhmm[2:]))
            pt = utc + pt_offset(date(y, m, dd))
            mlb_ids.add(away); mlb_ids.add(home)
            add(ds, "mlb", (away, home), pt.hour * 60 + pt.minute)

# NFL league table + preseason + postseason windows
for parts in read_rows("nfl_2026_pfr_regseason.txt"):
    wk, ds, t_et = parts[0], parts[1], parts[2]
    add(ds, "nfl_all", (parts[3], parts[4], "reg"),
        None if t_et in ("TBD", "-") else hhmm_to_min(t_et) - 180)
for parts in read_rows("nfl_2026_pfr_preseason.txt"):
    wk, ds, t_et = parts[0], parts[1], parts[2]
    add(ds, "nfl_all", (parts[3], parts[4], "pre"),
        None if t_et == "-" else hhmm_to_min(t_et) - 180)
for parts in read_rows("nfl_2027_postseason_tbd.txt"):
    ds, kick, dur, status = parts[0], parts[1], parts[2], parts[3]
    add(ds, "nfl_all", ("window", kick, status), hhmm_to_min(kick))
# Westwood One NFL broadcasts: matched rows badge the league row (no extra row), TBA rows
# are extra info-only placeholders that appear in the day view next to the window rows.
for parts in read_rows("westwoodone_nfl_2026.txt"):
    ds, air, aw, hm = parts[0], parts[1], parts[2], parts[3]
    if aw == "TBA":
        add(ds, "nfl_all", ("wwo-tba", air), None)
# NBA / NHL
for fn, sport in (("nba_warriors_2026_27.txt", "nba"), ("nhl_sharks_2026_27.txt", "nhl")):
    for parts in read_rows(fn):
        phase, ds, t_et = parts[0], parts[1], parts[2]
        add(ds, sport, (parts[3], parts[4], phase), hhmm_to_min(t_et) - 180)
# WNBA Valkyries (regular season rows + playoff TBD rows)
for parts in read_rows("wnba_valkyries_2026.txt"):
    phase, ds, t_pt, ha, opp, radio = (parts + [""])[:6]
    add(ds, "wnba", (phase, opp, ha), None if t_pt in ("TBD", "", "-") else hhmm_to_min(t_pt))
# WWO NCAA football
for parts in read_rows("westwoodone_ncaaf_2026.txt"):
    ds, kick = parts[0], parts[1]
    add(ds, "ncaaw", (parts[3], parts[4], kick),
        None if kick in ("TBD", "") else hhmm_to_min(kick[4:] if kick.startswith("EST-")
                                                      else kick))
# local games (49ers / Quakes / Stanford / Cal)
local = json.load(open(os.path.join(ROOT, "data", "games_local.json")))["games"]
for g in local:
    st = g.get("start_pt")
    add(g["date"], g["sport"], (g["label"], g.get("phase", "")),
        None if not st or st == "TBD" else hhmm_to_min(st))
# conditional day markers (MLS playoffs / ACC / CFP) - listed, never blocking
for fn, sport in (("mls_2026_playoffs_conditional.txt", "mls"),
                  ("ncaa_2026_postseason_conditional.txt", "ncaa"),
                  ("wnba_2026_playoffs_conditional.txt", "wnba")):
    for parts in read_rows(fn):
        add(parts[0], sport, ("conditional", parts[1]), None)

mismatch = []
for d in days:
    ds = d["date"]
    for sport in BLOCKING:
        want = raw_rows.get((ds, sport), [])
        have = [g for g in d["games"] if g["sport"] == sport]
        # 49ers club rows and the league-wide table overlap by design (league row flagged dedup)
        if sport == "nfl":
            want = [w for w in want]
        n_want = len(want)
        if sport == "wnba":
            # info-only rows (Audacy-app-only games) are listed but never block: the census
            # still counts them, so compare the full row sets like every other league.
            n_have = len(have)
        elif sport == "nfl_all":
            # the same 49ers game exists in both the club list and the league table; the
            # league row is dedup'd out of the day view but still present in d['games']
            n_have = len([g for g in have if g["sport"] == "nfl_all"])
        else:
            n_have = len(have)
        if n_want != n_have:
            mismatch.append(f"{ds} {sport}: raw={n_want} day={n_have}")
check(not mismatch, "6. per-day game census matches the raw files", str(mismatch[:8]))

# ------------------------------------------------- 7. time conversions
tb = []
for d in days:
    for g in d["games"]:
        if g["sport"] == "mlb" and g.get("utc"):
            exp = datetime.strptime(g["utc"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc) \
                  + pt_offset(date(*map(int, g["pt_date"].split("-"))))
            if exp.strftime("%H:%M") != g["start_pt"] or g["start_min"] != exp.hour * 60 + exp.minute:
                tb.append(f"{g['date']} {g['label']}")
        if g.get("start_et") and g.get("start_pt") not in (None, "TBD"):
            if hhmm_to_min(g["start_et"]) - 180 != g["start_min"]:
                tb.append(f"{g['date']} {g['label']} ET->PT")
check(not tb, "7. MLB UTC->PT and ET->PT conversions recomputed", str(tb[:6]))

# ------------------------------------------------- 9/10. priority + census
pr = [f"{g['date']} {g.get('label')}" for d in days for g in d["games"]
      if g["sport"] == "mlb" and bool(g.get("priority")) !=
      bool(g.get("home_id") in PRIORITY_MLB_TEAMS or g.get("away_id") in PRIORITY_MLB_TEAMS)]
check(not pr, "9. MLB priority flag == Giants/Athletics involved", str(pr[:6]))
# postseason placeholders carry no team ids, so no club can be flagged: assert they are
# left unflagged AND that the day is still NOT FREE (never silently free).
post_free = []
for d in days:
    post = [g for g in d["games"] if g["sport"] == "mlb" and g.get("tbd_count")]
    if post:
        if any(g.get("priority") for g in post):
            post_free.append(d["date"] + "/flagged-without-teams")
        if d["status"] != "NOT FREE — TIME TBD":
            post_free.append(d["date"] + "/" + d["status"])
check(not post_free, "9d. postseason placeholder days are NOT FREE and never assert free time",
      str(post_free[:6]))

# ------------------------------------------------- 11. MLB postseason resolved pass (2026-09-17)
# (a) totals: 53 placeholder games on 28 dates, matching the official mlb.com/postseason
#     bracket and the Stats API totalGames=53 (see data/raw/mlb_2026_postseason_tbd.txt)
check(sum(mlb_post_tbd.values()) == 53 and len(mlb_post_tbd) == 28,
      "11. MLB postseason = 53 TBD games across 28 official dates",
      f"{sum(mlb_post_tbd.values())} games / {len(mlb_post_tbd)} dates")
# (b) every postseason day carries its TBDxN marker row AND its raw EST slots, and the
#     day is NOT FREE - TIME TBD with no asserted free time
bad_est = []
for ds in sorted(mlb_post_tbd):
    d = by_date.get(ds)
    if not d:
        bad_est.append(ds + "/missing-day"); continue
    markers = [g for g in d["games"] if g["sport"] == "mlb" and g.get("tbd_count")]
    if len(markers) != 1 or markers[0]["tbd_count"] != mlb_post_tbd[ds]:
        bad_est.append(ds + "/marker")
    est_rows = sorted(g["start_min"] for g in d["games"]
                      if g["sport"] == "mlb" and g.get("est_kind") == "MLB-2025-PATTERN")
    if est_rows != sorted(mlb_post_est.get(ds, [])):
        bad_est.append(ds + "/est-slots")
    if d["status"] != "NOT FREE — TIME TBD" or d["free"] != [] or d["free_minutes"] != 0:
        bad_est.append(ds + "/status")
    # every EST interval must sit inside the stored blocked windows (164-min MLB duration)
    for g in d["games"]:
        if g["sport"] == "mlb" and g.get("est_kind") == "MLB-2025-PATTERN":
            s0, e0 = g["start_min"], g["start_min"] + 164
            if not any(b["start"] <= s0 and e0 <= b["end"] for b in d["blocked"]):
                bad_est.append(f"{ds}/est-{g['start_pt']}-unblocked")
check(not bad_est, "11b. MLB postseason EST windows == raw slots, blocked + day NOT FREE",
      str(bad_est[:6]))
# (c) EST slot count == game count per date, EXCEPT Oct 18 (NLCS Gm6 blocks BOTH 2025
#     options: 2:08 and 5:08 PM ET); 54 EST rows total for 53 games
slot_mismatch = {ds: (mlb_post_tbd[ds], len(mlb_post_est.get(ds, [])))
                 for ds in mlb_post_tbd
                 if mlb_post_tbd[ds] != len(mlb_post_est.get(ds, [])) and ds != "2026-10-18"}
check(not slot_mismatch and sum(len(v) for v in mlb_post_est.values()) == 54
      and len(mlb_post_est.get("2026-10-18", [])) == 2,
      "11c. EST slot count == TBD game count (54 rows; only Oct 18 double-slotted)",
      str(slot_mismatch))
# (d) no postseason row may be flagged high-priority or carry real team ids
bad_pri = [f"{g['date']}" for d in days for g in d["games"]
           if g["sport"] == "mlb" and (g.get("tbd_count") or g.get("est_kind") == "MLB-2025-PATTERN")
           and (g.get("priority") or g.get("away_id") or g.get("home_id"))]
check(not bad_pri, "11d. postseason rows carry no teams and are never high priority", str(bad_pri[:4]))

# ------------------------------------------------- 12. playoff picture (2026-09-17)
pp_file = os.path.join(RAW, "mlb_2026_playoff_picture.json")
pp = json.load(open(pp_file)) if os.path.exists(pp_file) else {}
pp_meta = meta.get("mlb_playoff_picture", {})
check(pp.get("clinched") and pp_meta.get("clinched") == [c["abbr"] for c in pp.get("clinched", [])]
      and len(pp_meta.get("clinched", [])) == 4
      and not ({"SF", "ATH"} & set(pp_meta.get("clinched", []))),
      "12. meta playoff picture == raw JSON (4 clinched, no SF/ATH)",
      str(pp_meta))
elim = {e["abbr"] for e in pp.get("eliminated", [])}
check({"SF", "ATH"} <= elim and pp_meta.get("eliminated") == [e["abbr"] for e in pp.get("eliminated", [])],
      "12b. Giants + Athletics recorded ELIMINATED in meta (no Bay Area club in October)",
      str(sorted(elim)))
# structural guarantee: no Giants (137) / Athletics (133) game row on any postseason date
bay_post = [f"{g['date']} {g.get('label')}" for d in days for g in d["games"]
            if g["sport"] == "mlb" and g["date"] >= "2026-09-29"
            and (g.get("away_id") in PRIORITY_MLB_TEAMS or g.get("home_id") in PRIORITY_MLB_TEAMS)]
check(not bay_post, "12c. no Giants/Athletics row exists on any postseason date", str(bay_post[:4]))
sf_day = [g["date"] for d in days for g in d["games"] if g["sport"] == "nfl" and not g.get("priority")]
check(not sf_day, "9b. every 49ers (sport=nfl) row is high priority", str(sf_day[:6]))
nn = [g["date"] for d in days for g in d["games"]
      if g["sport"] in ("nba", "nhl", "ncaaw", "wnba") and not g.get("priority")
      and not g.get("conditional")]   # conditional markers are day notes, not games
check(not nn, "9c. every Warriors/Sharks/WWO-NCAAF row is high priority", str(nn[:6]))
giants = sum(1 for d in days for g in d["games"]
             if g["sport"] == "mlb" and 137 in (g.get("home_id"), g.get("away_id")))
ath = sum(1 for d in days for g in d["games"]
          if g["sport"] == "mlb" and 133 in (g.get("home_id"), g.get("away_id")))
sf = len([g for d in days for g in d["games"] if g["sport"] == "nfl"])
check((giants, ath, sf) == (52, 52, 20),
      "10. high-priority census (Giants 52 / A's 52 / 49ers 20)",
      f"Giants={giants} A's={ath} 49ers={sf}")
check(len(mlb_ids) == 30, "10b. all 30 MLB clubs appear in the raw schedule", f"{len(mlb_ids)} clubs")

# ------------------------------------------------- summary
print("-" * 78)
print(f"days audited: {len(days)}   games in day view: "
      f"{sum(len(d['games']) for d in days)}   flags in output: {len(data.get('flags', []))}")
hi_days = sorted({g["date"] for d in days for g in d["games"] if g.get("priority")})
print(f"high-priority days: {len(hi_days)}   first: {hi_days[:3]}")
if problems:
    print(f"\nAUDIT FAILED ({len(problems)} problem(s)):")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("\nAUDIT PASSED - generated free_time.json matches an independent recomputation.")
