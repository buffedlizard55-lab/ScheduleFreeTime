#!/usr/bin/env node
/*
 * UI-level invariant test (added 2026-09-17).
 *
 * The user reported: "the site says that I have free time on days when there are
 * football games on". The fix lives in two places: (a) the generated data
 * (data/processed/free_time.json — NOT FREE / UNCONFIRMED days store free=[] with
 * free_minutes=0), and (b) the shipped UI (index.html renderDay() recomputes the
 * same status rule client-side). This test executes the ACTUAL shipped JS helpers
 * (windows() and the status rule, extracted verbatim from index.html) against the
 * generated data and re-asserts the invariants:
 *
 *   INV1  no day with any tracked football game (NFL / all-NFL / WWO college /
 *         Stanford / Cal) ever renders the status FREE;
 *   INV2  on NOT FREE — TIME TBD and UNCONFIRMED days the stored data asserts NO
 *         free time (free == [] and free_minutes == 0) — so the UI (which renders
 *         exactly the stored data) cannot show free time there;
 *   INV3  the shipped status rule reproduces the stored status for all 212 days
 *         with every league toggled ON (the default UI state);
 *   INV4  on FREE / PARTIAL days the free + blocked windows partition 1440 minutes
 *         and the stored free_minutes equals the recomputed value.
 *
 * Run: node scripts/ui_logic_test.js   (exit 0 = PASS, 1 = FAIL)
 */
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');

const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/processed/free_time.json'), 'utf8'));
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');

const FOOTBALL = new Set(['nfl', 'nfl_all', 'ncaaw', 'ncaa']);
let fail = 0;
const bad = [];
const assert = (cond, msg) => { if (!cond) { fail++; bad.push(msg); } };

// ---- extract the SHIPPED UI code (verbatim) and execute it ----------------
const mWin = html.match(/function windows\(gs\)\{[\s\S]*?\n\}/);
assert(!!mWin, 'could not extract windows() from index.html');
// Same environment index.html provides at call time:
const DUR = { mlb: 164, nfl: 192, ncaa: 204, mls: 120, nba: 138, nhl: 150, wnba: 125 };
const BLOCK = { mlb: 1, nfl: 1, mls: 1, ncaa: 1, nfl_all: 1, nba: 1, nhl: 1, ncaaw: 1, wnba: 1 };
const dur = (s) => (s === 'nfl_all' ? DUR.nfl : (s === 'ncaaw' ? DUR.ncaa : (DUR[s] || 120)));
const isBlocking = (g) => BLOCK[g.sport] && g.start_min != null;
// eslint-disable-next-line no-eval
const windows = eval('(' + mWin[0] + ')');

const mSt = html.match(/const st=\(tbdN\|\|est\.length\)\?'NOT FREE — TIME TBD'[^;]*;/);
assert(!!mSt, 'could not extract the status rule from index.html renderDay()');
// eslint-disable-next-line no-new-func
const statusRule = new Function('tbdN', 'est', 'cond', 'merged', 'fm',
  mSt[0].replace(/^const st\s*=\s*/, 'return ') + ';');

// ---- per-day invariants ------------------------------------------------------
for (const d of DATA.days) {
  // The UI's dayGames() with every league toggled ON (the default state).
  const gs = d.games.filter((g) => !g.dedup);
  const tbd = gs.filter((g) => g.start_min == null && !g.info_only && !g.conditional);
  const tbdN = tbd.reduce((a, g) => a + (g.tbd_count || 1), 0);
  const est = gs.filter((g) => g.estimated && g.start_min != null);
  const cond = gs.filter((g) => g.conditional);
  const w = windows(gs);
  const fm = w.free.reduce((a, b) => a + b[1] - b[0], 0);
  const st = statusRule(tbdN, est, cond, w.merged, fm);

  // INV3: shipped rule == stored status
  assert(st === d.status, `status mismatch ${d.date}: stored '${d.status}' vs shipped-rule '${st}'`);

  // INV1: the reported bug — no football day may render FREE
  const hasFootball = gs.some((g) => FOOTBALL.has(g.sport) && !g.conditional && !g.info_only);
  if (hasFootball) assert(st !== 'FREE', `BUG REPRODUCED: football day ${d.date} renders FREE`);

  // INV2: NOT FREE / UNCONFIRMED days assert no free time in the data the UI renders
  if (st === 'NOT FREE — TIME TBD' || st === 'UNCONFIRMED') {
    assert(d.free.length === 0, `${d.date}: ${d.free.length} free window(s) stored on a ${st} day`);
    assert(d.free_minutes === 0, `${d.date}: ${d.free_minutes} free minute(s) stored on a ${st} day`);
  }

  // INV4: FREE / PARTIAL days partition the day exactly
  if (st === 'FREE' || st === 'PARTIAL') {
    const mTot = w.merged.reduce((a, b) => a + Math.max(0, Math.min(b[1], 1440) - Math.max(b[0], 0)), 0);
    assert(fm + mTot === 1440, `${d.date}: free+blocked = ${fm + mTot} != 1440`);
    assert(d.free_minutes === fm, `${d.date}: stored free_minutes ${d.free_minutes} != recomputed ${fm}`);
    assert(d.free.length > 0 || st === 'FULLY BOOKED', `${d.date}: FREE/PARTIAL day with no free windows`);
  }
}

if (fail) {
  console.error(`UI LOGIC TEST FAIL — ${fail} invariant violation(s):`);
  bad.slice(0, 25).forEach((x) => console.error('  - ' + x));
  process.exit(1);
}
console.log(`UI LOGIC TEST PASS: ${DATA.days.length} days — shipped windows() + status rule match the stored data everywhere; no day with a tracked football game renders FREE; no NOT FREE/UNCONFIRMED day asserts free time; FREE/PARTIAL days partition 24h exactly.`);
