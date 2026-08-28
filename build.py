#!/usr/bin/env python3
"""
ScheduleFreeTime - single source of truth generator.

Builds:
  - schedule-data.js   (canonical data consumed by the web app)
  - schedules.md       (human-readable verified master list w/ official source links)

All game data below was researched line-by-line from OFFICIAL sources and
cross-checked. See FLAGS at the bottom for assumptions / irregularities.

Time zone: Pacific Time (PT). Aug-Oct 2026 = Pacific Daylight Time (UTC-7).
"""
import json
from datetime import date, timedelta

# ---- research-based average durations (minutes) ----
DUR = {
    "MLB": 158,      # 2025 MLB avg = 2:38 (158 min) per ESPN / lines.com (pitch-clock era)
    "NFL": 192,      # 2025 NFL avg = 3:12 (192 min) per sportsgeardaily / ESPN
    "Stanford": 200, # 2025 CFB avg = 3:24 (204 min); using 200 (3h20m) estimate
    "Cal": 200,      # same as CFB
    "MLS": 120,      # MLS match = 90' + ~15' HT + stoppage ~ 2h (per lines.com)
}

SOURCE = {
    "MLB":      ("MLB Stats API (statsapi.mlb.com) + mlb.com Giants schedule",
                 "https://www.mlb.com/giants/schedule"),
    "NFL":      ("49ers.com official schedule (preseason per 49ers.com news release)",
                 "https://www.49ers.com/schedule"),
    "Stanford": ("Stanford Athletics official football schedule (gostanford.com)",
                 "https://gostanford.com/sports/football/schedule"),
    "Cal":      ("California Athletics official football schedule (calbears.com)",
                 "https://calbears.com/sports/football/schedule"),
    "MLS":      ("San Jose Earthquakes official 2026 schedule announcement (sjearthquakes.com)",
                 "https://www.sjearthquakes.com/news/news-earthquakes-announce-2026-major-league-soccer-schedule"),
}

games = []

def add(date, league, team, matchup, homeAway, startPT, tbd=False):
    games.append({
        "date": date,
        "league": league,
        "team": team,
        "matchup": matchup,
        "homeAway": homeAway,
        "startPT": (None if tbd else startPT),
        "durationMin": DUR[league],
        "tbd": tbd,
    })

# ========================= 49ers (NFL) =========================
# Preseason times from 49ers.com official news release
# Regular season from 49ers.com/schedule (all PT)
add("2026-08-13", "NFL", "49ers", "49ers vs Tennessee Titans (Preseason Wk1)", "home", "6:00 PM")
add("2026-08-20", "NFL", "49ers", "49ers at Los Angeles Chargers (Preseason Wk2)", "away", "7:00 PM")
add("2026-08-27", "NFL", "49ers", "49ers vs Las Vegas Raiders (Preseason Wk3)", "home", "5:00 PM")
add("2026-09-10", "NFL", "49ers", "49ers at Los Angeles Rams (Wk1, Melbourne AUS)", "away", "5:35 PM")
add("2026-09-20", "NFL", "49ers", "49ers vs Miami Dolphins (Wk2)", "home", "1:25 PM")
add("2026-09-27", "NFL", "49ers", "49ers vs Arizona Cardinals (Wk3)", "home", "1:05 PM")
add("2026-10-04", "NFL", "49ers", "49ers vs Denver Broncos (Wk4)", "home", "1:25 PM")
add("2026-10-11", "NFL", "49ers", "49ers at Seattle Seahawks (Wk5)", "away", "1:25 PM")
add("2026-10-19", "NFL", "49ers", "49ers vs Washington Commanders (Wk6, MNF)", "home", "5:15 PM")
add("2026-10-25", "NFL", "49ers", "49ers at Atlanta Falcons (Wk7)", "away", "10:00 AM")

# ========================= Stanford (CFB) =========================
# ESPN 2026 schedule (times shown in ET) -> converted to PT.
# Aug 29 7:00 PM ET = 4:00 PM PT; Sep 4 9:00 PM ET = 6:00 PM PT;
# Sep 19 4:00 PM ET = 1:00 PM PT; Sep 26 10:30 PM ET = 7:30 PM PT;
# Oct 10 3:30 PM ET = 12:30 PM PT; Oct 17 7:30 PM ET = 4:30 PM PT;
# Oct 23 10:30 PM ET = 7:30 PM PT. (Matches gostanford.com PT listings.)
add("2026-08-29", "Stanford", "Stanford", "Stanford vs Hawai'i Rainbow Warriors", "home", "4:00 PM")
add("2026-09-04", "Stanford", "Stanford", "Stanford vs Miami Hurricanes", "home", "6:00 PM")
add("2026-09-19", "Stanford", "Stanford", "Stanford at Duke Blue Devils", "away", "1:00 PM")
add("2026-09-26", "Stanford", "Stanford", "Stanford vs Georgia Tech Yellow Jackets", "home", "7:30 PM")
add("2026-10-03", "Stanford", "Stanford", "Stanford at Wake Forest Demon Deacons", "away", None, tbd=True)
add("2026-10-10", "Stanford", "Stanford", "Stanford at Notre Dame Fighting Irish", "away", "12:30 PM")
add("2026-10-17", "Stanford", "Stanford", "Stanford vs Elon Phoenix", "home", "4:30 PM")
add("2026-10-23", "Stanford", "Stanford", "Stanford vs NC State Wolfpack", "home", "7:30 PM")
add("2026-10-31", "Stanford", "Stanford", "Stanford at Louisville Cardinals", "away", None, tbd=True)

# ========================= Cal (CFB) =========================
# All times from calbears.com official schedule, listed in PT (school-local).
add("2026-09-05", "Cal", "Cal", "Cal vs UCLA Bruins", "home", "7:30 PM")
add("2026-09-12", "Cal", "Cal", "Cal at Syracuse Orange", "away", "12:30 PM")
add("2026-09-19", "Cal", "Cal", "Cal vs Wagner Seahawks", "home", "12:30 PM")
add("2026-09-25", "Cal", "Cal", "Cal vs Clemson Tigers", "home", "7:30 PM")
add("2026-10-03", "Cal", "Cal", "Cal at UNLV Rebels", "away", "12:30 PM")
add("2026-10-10", "Cal", "Cal", "Cal vs Virginia Tech Hokies", "home", None, tbd=True)
add("2026-10-17", "Cal", "Cal", "Cal vs Wake Forest Demon Deacons", "home", None, tbd=True)
add("2026-10-24", "Cal", "Cal", "Cal at SMU Mustangs", "away", None, tbd=True)
add("2026-10-31", "Cal", "Cal", "Cal at NC State Wolfpack", "away", None, tbd=True)

# ========================= Earthquakes (MLS) =========================
# Official sjearthquakes.com 2026 schedule announcement (all PT).
add("2026-08-01", "MLS", "Earthquakes", "Earthquakes at FC Cincinnati", "away", "4:30 PM")
add("2026-08-15", "MLS", "Earthquakes", "Earthquakes vs St. Louis CITY SC", "home", "7:30 PM")
add("2026-08-19", "MLS", "Earthquakes", "Earthquakes at LA Galaxy", "away", "7:30 PM")
add("2026-08-22", "MLS", "Earthquakes", "Earthquakes vs Minnesota United FC", "home", "7:30 PM")
add("2026-08-29", "MLS", "Earthquakes", "Earthquakes at Houston Dynamo FC", "away", "5:30 PM")
add("2026-09-05", "MLS", "Earthquakes", "Earthquakes at Austin FC", "away", "5:30 PM")
add("2026-09-09", "MLS", "Earthquakes", "Earthquakes at San Diego FC", "away", "7:30 PM")
add("2026-09-12", "MLS", "Earthquakes", "Earthquakes vs Houston Dynamo FC", "home", "7:30 PM")
add("2026-09-19", "MLS", "Earthquakes", "Earthquakes vs LAFC", "home", "4:30 PM")
add("2026-09-26", "MLS", "Earthquakes", "Earthquakes vs Portland Timbers", "home", "7:30 PM")
add("2026-10-10", "MLS", "Earthquakes", "Earthquakes at Colorado Rapids", "away", "6:30 PM")
add("2026-10-14", "MLS", "Earthquakes", "Earthquakes at Real Salt Lake", "away", "6:30 PM")
add("2026-10-17", "MLS", "Earthquakes", "Earthquakes vs Nashville SC", "home", "7:30 PM")
add("2026-10-24", "MLS", "Earthquakes", "Earthquakes at FC Dallas", "away", "5:30 PM")
add("2026-10-28", "MLS", "Earthquakes", "Earthquakes vs Colorado Rapids", "home", "7:30 PM")
add("2026-10-31", "MLS", "Earthquakes", "Earthquakes vs Real Salt Lake", "home", None, tbd=True)

# ========================= Giants (MLB) =========================
# Official MLB Stats API (teamId=137) Aug 1 - Oct 31, 2026.
# 52 games; 2026 regular season ends Sun Sep 27 (no Giants games Oct 1-27).
# gameDate (UTC) converted to PT (UTC-7). Doubleheader on Aug 29.
giants = [
    ("2026-08-01", "Giants at San Diego Padres",            "away", "5:40 PM"),
    ("2026-08-02", "Giants at San Diego Padres",            "away", "1:10 PM"),
    ("2026-08-03", "Giants at Texas Rangers",               "away", "5:05 PM"),
    ("2026-08-04", "Giants at Texas Rangers",               "away", "5:05 PM"),
    ("2026-08-05", "Giants at Texas Rangers",               "away", "11:35 AM"),
    ("2026-08-07", "Giants vs Detroit Tigers",             "home", "7:15 PM"),
    ("2026-08-08", "Giants vs Detroit Tigers",             "home", "4:15 PM"),
    ("2026-08-09", "Giants vs Detroit Tigers",             "home", "1:05 PM"),
    ("2026-08-10", "Giants vs Houston Astros",             "home", "6:45 PM"),
    ("2026-08-11", "Giants vs Houston Astros",             "home", "6:45 PM"),
    ("2026-08-12", "Giants vs Houston Astros",             "home", "12:45 PM"),
    ("2026-08-14", "Giants vs Colorado Rockies",           "home", "7:15 PM"),
    ("2026-08-15", "Giants vs Colorado Rockies",           "home", "1:05 PM"),
    ("2026-08-16", "Giants vs Colorado Rockies",           "home", "1:05 PM"),
    ("2026-08-18", "Giants at Cleveland Guardians",        "away", "3:40 PM"),
    ("2026-08-19", "Giants at Cleveland Guardians",        "away", "3:40 PM"),
    ("2026-08-20", "Giants at Cleveland Guardians",        "away", "10:10 AM"),
    ("2026-08-21", "Giants at Boston Red Sox",             "away", "4:10 PM"),
    ("2026-08-22", "Giants at Boston Red Sox",             "away", "4:15 PM"),
    ("2026-08-23", "Giants at Boston Red Sox",             "away", "12:15 PM"),
    ("2026-08-24", "Giants vs Cincinnati Reds",            "home", "6:45 PM"),
    ("2026-08-25", "Giants vs Cincinnati Reds",            "home", "6:45 PM"),
    ("2026-08-26", "Giants vs Cincinnati Reds",            "home", "12:45 PM"),
    ("2026-08-27", "Giants vs Arizona Diamondbacks",       "home", "6:45 PM"),
    ("2026-08-28", "Giants vs Arizona Diamondbacks",       "home", "7:15 PM"),
    ("2026-08-29", "Giants vs Arizona Diamondbacks (DH1)", "home", "1:05 PM"),
    ("2026-08-29", "Giants vs Arizona Diamondbacks (DH2)", "home", "7:05 PM"),
    ("2026-08-31", "Giants at Atlanta Braves",             "away", "3:05 PM"),
    ("2026-09-01", "Giants at Pittsburgh Pirates",         "away", "3:40 PM"),
    ("2026-09-02", "Giants at Pittsburgh Pirates",         "away", "3:40 PM"),
    ("2026-09-03", "Giants at Pittsburgh Pirates",         "away", "9:35 AM"),
    ("2026-09-04", "Giants at New York Mets",              "away", "4:10 PM"),
    ("2026-09-05", "Giants at New York Mets",              "away", "1:10 PM"),
    ("2026-09-06", "Giants at New York Mets",              "away", "10:40 AM"),
    ("2026-09-07", "Giants vs St. Louis Cardinals",        "home", "5:10 PM"),
    ("2026-09-08", "Giants vs St. Louis Cardinals",        "home", "6:45 PM"),
    ("2026-09-09", "Giants vs St. Louis Cardinals",        "home", "12:45 PM"),
    ("2026-09-11", "Giants vs San Diego Padres",           "home", "7:15 PM"),
    ("2026-09-12", "Giants vs San Diego Padres",           "home", "1:05 PM"),
    ("2026-09-13", "Giants vs San Diego Padres",           "home", "4:20 PM"),
    ("2026-09-14", "Giants at St. Louis Cardinals",        "away", "4:45 PM"),
    ("2026-09-15", "Giants at St. Louis Cardinals",        "away", "4:45 PM"),
    ("2026-09-16", "Giants at St. Louis Cardinals",        "away", "10:15 AM"),
    ("2026-09-18", "Giants at Los Angeles Dodgers",        "away", "7:15 PM"),
    ("2026-09-19", "Giants at Los Angeles Dodgers",        "away", "6:10 PM"),
    ("2026-09-20", "Giants at Los Angeles Dodgers",        "away", "1:10 PM"),
    ("2026-09-21", "Giants vs Minnesota Twins",            "home", "6:45 PM"),
    ("2026-09-22", "Giants vs Minnesota Twins",            "home", "6:45 PM"),
    ("2026-09-23", "Giants vs Minnesota Twins",            "home", "12:45 PM"),
    ("2026-09-25", "Giants vs Los Angeles Dodgers",        "home", "7:15 PM"),
    ("2026-09-26", "Giants vs Los Angeles Dodgers",        "home", "1:05 PM"),
    ("2026-09-27", "Giants vs Los Angeles Dodgers",        "home", "12:05 PM"),
]
for d, m, ha, t in giants:
    add(d, "MLB", "Giants", m, ha, t)

# ---- assemble ----
games.sort(key=lambda g: (g["date"], g["startPT"] or "12:00 AM"))

FLAGS = [
    "INTERPRETATION: 'no MLB games on' was interpreted as the San Francisco Giants (Bay Area MLB team) "
    "regular-season games only. If you meant ALL 30 MLB teams, or the Athletics, the scope is much larger "
    "(~15 MLB games/day). Flagged for your review.",
    "MLB POSTSEASON EXCLUDED: The 2026 MLB regular season ends Sun Sep 27, 2026 (official MLB). "
    "Postseason (Wild Card Sep 29, LDS, LCS, World Series through ~Oct 31) is NOT included because the "
    "Giants (standings: 4th NL West) are not in playoff contention; if you watch all postseason MLB, "
    "October would have many additional busy days.",
    "TBD GAME TIMES (free-time for these days is best-effort / excluded until confirmed): "
    "Stanford Oct 3 & Oct 31; Cal Oct 10, 17, 24, 31; Earthquakes Oct 31.",
    "AWAY-GAME TIMES: Cal & Stanford away games are shown in PT per the schools' official schedule sites "
    "(school-local time). Verified against ESPN (ET): e.g., Stanford @ Duke 4:00 PM ET = 1:00 PM PT.",
    "EARTHQUAKES TIMES are PT per the official sjearthquakes.com announcement; ESPN lists the same games "
    "in ET (e.g., 7:30 PM PT = 10:30 PM ET) - consistent.",
    "49ERS PRESEASON times are from the official 49ers.com news release (the schedule page lists them as "
    "FINAL without times). Regular-season times are from 49ers.com/schedule.",
    "DURATIONS are research-based ESTIMATES, not exact per-game: MLB 158 min (2025 avg 2:38), NFL 192 min "
    "(2025 avg 3:12), CFB 200 min (2025 avg ~3:24), MLS 120 min. Football durations include halftime "
    "(NFL 12 min, CFB 20 min).",
    "The prior schedules.md in this repo was largely hallucinated (wrong 49ers opener time, wrong Cal "
    "ET/PT conversions, fabricated MLB matchups, missing Earthquakes Aug 1). It has been fully replaced.",
]

DATA = {
    "meta": {
        "title": "ScheduleFreeTime - Free Time Scoreboard (Aug-Oct 2026)",
        "timezone": "America/Los_Angeles (PT; Aug-Oct 2026 = PDT, UTC-7)",
        "range": {"start": "2026-08-01", "end": "2026-10-31"},
        "durationsMin": DUR,
        "sources": {k: {"name": v[0], "url": v[1]} for k, v in SOURCE.items()},
        "flags": FLAGS,
        "generated": "2026-08-28",
    },
    "games": games,
}

# ---- write schedule-data.js ----
js = "// AUTO-GENERATED by build.py - do not edit by hand.\n"
js += "const SCHEDULE_DATA = " + json.dumps(DATA, indent=2, ensure_ascii=False) + ";\n"
with open("schedule-data.js", "w", encoding="utf-8") as f:
    f.write(js)

# ---- free-day computation for summary ----
def daterange(a, b):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)

start = date(2026, 8, 1)
end = date(2026, 10, 31)
game_days = set(g["date"] for g in games)
free_days = [d for d in daterange(start, end) if d.isoformat() not in game_days]

print("Total games:", len(games))
print("Free (no-game) days Aug1-Oct31:", len(free_days))
print("Wrote schedule-data.js")

# ---- write schedules.md ----
LEAGUE_ORDER = ["MLB", "NFL", "MLS", "Stanford", "Cal"]
LEAGUE_TITLE = {
    "MLB": "San Francisco Giants (MLB)",
    "NFL": "San Francisco 49ers (NFL)",
    "MLS": "San Jose Earthquakes (MLS)",
    "Stanford": "Stanford Cardinal (NCAA Football)",
    "Cal": "California Golden Bears (NCAA Football)",
}

lines = []
lines.append("# ScheduleFreeTime - Verified Master Game List (August - October 2026)\n")
lines.append("**Goal:** Identify free time (Pacific Time) when NONE of the following are playing: "
             "Giants (MLB), 49ers (NFL), Earthquakes (MLS), Stanford (CFB), Cal (CFB).\n")
lines.append(f"**Compiled:** 2026-08-28  |  **Time zone:** Pacific (PT; Aug-Oct = PDT, UTC-7)  |  "
             f"**Total verified entries:** {len(games)}\n")
lines.append("Every entry below was verified from an OFFICIAL source (linked). No manual/hallucinated "
             "entries. See FLAGS section for assumptions and irregularities.\n")
lines.append("")

# summary by league
lines.append("## Counts by league\n")
lines.append("| League | Games (Aug-Oct 2026) | Official source |")
lines.append("|--------|----------------------|----------------|")
for lg in LEAGUE_ORDER:
    cnt = sum(1 for g in games if g["league"] == lg)
    lines.append(f"| {LEAGUE_TITLE[lg]} | {cnt} | [{SOURCE[lg][0]}]({SOURCE[lg][1]}) |")
lines.append(f"| **TOTAL** | **{len(games)}** | |")
lines.append("")

# per-league tables
for lg in LEAGUE_ORDER:
    lg_games = [g for g in games if g["league"] == lg]
    lg_games.sort(key=lambda g: g["date"])
    lines.append(f"## {LEAGUE_TITLE[lg]}\n")
    lines.append(f"Source: [{SOURCE[lg][0]}]({SOURCE[lg][1]})\n")
    lines.append("| # | Date | Matchup | Time (PT) | Est. Duration | Status |")
    lines.append("|---|------|---------|-----------|---------------|--------|")
    for i, g in enumerate(lg_games, 1):
        t = g["startPT"] if g["startPT"] else "TBD"
        dur = f"{g['durationMin']} min" if not g["tbd"] else f"~{g['durationMin']} min (TBD time)"
        lines.append(f"| {i} | {g['date']} | {g['matchup']} | {t} | {dur} | "
                     f"[{SOURCE[lg][1]}]({SOURCE[lg][1]}) |")
    lines.append("")

# free days
lines.append("## Fully free days (zero games scheduled) - Aug 1 to Oct 31, 2026\n")
lines.append(f"**{len(free_days)} days** with no Giants/49ers/Earthquakes/Stanford/Cal games "
             f"(under the Giants = MLB interpretation):\n")
for d in free_days:
    lines.append(f"- {d.strftime('%a %Y-%m-%d')}")
lines.append("")

# methodology
lines.append("## Free-time calculation method\n")
lines.append("- For each day, every game is treated as a BUSY block from its PT start time for its "
             "estimated average duration.")
lines.append("- Free time = the complement of all busy blocks across the 24-hour day (12:00 AM - 11:59 PM).")
lines.append("- Durations (research-based averages): MLB 158 min, NFL 192 min, CFB 200 min, MLS 120 min. "
             "Football durations include halftime.")
lines.append("- Games with TBD times are shown but excluded from the busy-block estimate until the time is confirmed.")
lines.append("- Doubleheaders (Giants vs Diamondbacks, Aug 29) create two busy blocks with a free window between them.\n")

# flags
lines.append("## FLAGS / irregularities for review\n")
for i, f in enumerate(FLAGS, 1):
    lines.append(f"{i}. {f}")
lines.append("")

lines.append("---\n*Generated 2026-08-28 from official sources via automated research. "
             "Each entry links to its official product page for manual verification.*\n")

with open("schedules.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Wrote schedules.md")
