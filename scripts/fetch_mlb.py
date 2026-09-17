#!/usr/bin/env python3
"""
fetch_mlb.py - one-command MLB postseason refresh (Priority-1/Priority-4 item from
docs/LIMITATIONS_AND_NEXT_STEPS.md).

WHAT IT DOES (needs internet; the build sandbox has none - run it from any
connected machine):
  1. Fetches the official MLB Stats API postseason schedule:
       https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-09-28&endDate=2026-11-10
  2. Parses every game: gamePk, officialDate, seriesDescription, gameDate (UTC),
     startTimeTBD flag.
  3. Converts each gameDate to Pacific (America/Los_Angeles) - PDT through
     Oct 31 2026, PST from Nov 1 2026 - using the same zone rules as the build.
  4. Diffs the live data against data/raw/mlb_2026_postseason_tbd.txt
     (the 53 placeholder rows) at gamePk level and reports:
       - zero drift (the expected result until MLB sets the field Sep 27-28);
       - any game whose start time became OFFICIAL (startTimeTBD=false or a
         gameDate other than the 07:33:00Z placeholder) -> prints the exact
         replacement rows for the raw file in the build's format;
       - any added/removed game or date-count change (the 2026-09-16 pass
         caught exactly this kind of change: Oct 4 went 4 -> 2 games).
  5. Writes a machine-readable snapshot data/raw/mlb_postseason_live_snapshot.json
     (fetched_at + every game) for the audit trail. The file is advisory: the
     build keeps reading the hand-verified .txt until you deliberately replace
     rows (no hallucinations - nothing is auto-merged).

EXIT CODES: 0 = ran (incl. graceful offline no-op), 2 = live data conflicts with
the raw file (new times or count changes) -> review, then update the raw file.

Usage: python3 scripts/fetch_mlb.py
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

API = ("https://statsapi.mlb.com/api/v1/schedule?sportId=1"
       "&startDate=2026-09-28&endDate=2026-11-10")
RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
RAW_FILE = os.path.join(RAW_DIR, "mlb_2026_postseason_tbd.txt")
SNAPSHOT = os.path.join(RAW_DIR, "mlb_postseason_live_snapshot.json")
PLACEHOLDER_UTC = "07:33:00Z"          # MLB's universal TBD placeholder time
PT = ZoneInfo("America/Los_Angeles")

# gamePks expected in the raw file (transcribed + verified vs mlb.com/postseason
# on 2026-09-17) are recorded in the file's header comments, one per game, as
# "Gm<N> <gamePk> <Mon <day>>"; the data rows are per-DATE ("date|TBDxN|...").
# fetch_mlb re-derives both from the file so a deliberate raw-file update
# automatically becomes the new baseline.
def raw_gamepks():
    if not os.path.exists(RAW_FILE):
        return set()
    text = open(RAW_FILE, encoding="utf-8").read()
    return {int(pk) for pk in re.findall(r"Gm\d+ (\d{6,8})", text)}

def raw_date_counts():
    """{date: expected game count} parsed from the per-date data rows."""
    counts = {}
    if not os.path.exists(RAW_FILE):
        return counts
    for line in open(RAW_FILE, encoding="utf-8"):
        m = re.match(r"^(\d{4}-\d{2}-\d{2})\|TBDx(\d+)\|", line.strip())
        if m:
            counts[m.group(1)] = int(m.group(2))
    return counts

def utc_to_pt(iso_utc):
    dt = datetime.strptime(iso_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    local = dt.astimezone(PT)
    return local.strftime("%H:%M"), local.strftime("%Y-%m-%d")

def main():
    print(f"fetching {API}")
    try:
        req = urllib.request.Request(API, headers={"User-Agent": "ScheduleFreeTime/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:  # graceful offline no-op (e.g. sandbox without egress)
        print(f"OFFLINE: could not reach the MLB Stats API ({e}).")
        print("No data changed. Re-run from a machine with internet access:")
        print("  python3 scripts/fetch_mlb.py")
        return 0

    games = []
    for d in data.get("dates", []):
        for g in d.get("games", []):
            game_utc = g.get("gameDate", "")
            tbd = bool(g.get("status", {}).get("startTimeTBD")) or game_utc.endswith(PLACEHOLDER_UTC)
            pt_time, pt_date = utc_to_pt(game_utc)
            games.append({
                "gamePk": g["gamePk"],
                "officialDate": g.get("officialDate", d["date"]),
                "series": g.get("seriesDescription", ""),
                "description": g.get("description", ""),
                "utc": game_utc,
                "startTimeTBD": bool(g.get("status", {}).get("startTimeTBD")),
                "placeholder": tbd,
                "pt_date": pt_date,
                "pt_time": pt_time,
            })

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    snap = {"fetched_at_utc": now, "source": API, "totalGames": data.get("totalGames"),
            "games": games}
    with open(SNAPSHOT, "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=1)
    print(f"snapshot written: {os.path.relpath(SNAPSHOT)} ({len(games)} games)")

    live_pks = {g["gamePk"] for g in games}
    expected_pks = raw_gamepks()
    problems = []

    if expected_pks and live_pks != expected_pks:
        added, removed = live_pks - expected_pks, expected_pks - live_pks
        if added:
            problems.append(f"NEW postseason gamePk(s) not in the raw file: {sorted(added)}")
        if removed:
            problems.append(f"raw-file gamePk(s) no longer live: {sorted(removed)}")

    live_counts = {}
    for g in games:
        live_counts[g["officialDate"]] = live_counts.get(g["officialDate"], 0) + 1
    for date, n in sorted(raw_date_counts().items()):
        if live_counts.get(date, 0) != n:
            problems.append(f"per-date game count changed on {date}: "
                            f"raw file says {n}, live API says {live_counts.get(date, 0)}")
    extra_dates = sorted(set(live_counts) - set(raw_date_counts()))
    if extra_dates:
        problems.append(f"new postseason date(s) added by MLB: {extra_dates}")

    official = [g for g in games if not g["placeholder"]]
    if official:
        problems.append(f"{len(official)} game(s) now have OFFICIAL start times:")
        print("\nOFFICIAL TIMES FOUND - replacement rows for "
              "data/raw/mlb_2026_postseason_tbd.txt (build format):\n")
        for g in official:
            print(f"{g['officialDate']}|{g['pt_time']}|{g['series']}|gamePk={g['gamePk']}"
                  f"|{g['description']}|utc={g['utc']}|PT verified by fetch_mlb.py")
        print()

    for p in problems:
        print("DELTA:", p)
    if problems:
        print("\nACTION: review each delta, update the raw file by hand (no auto-merge),")
        print("then re-run python3 scripts/build.py && python3 scripts/audit.py")
        return 2

    print("ZERO DELTA: every live gamePk matches the raw file and every start")
    print("time is still the official TBD placeholder (07:33:00Z).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
