/* ScheduleFreeTime - scoreboard + calendar logic (vanilla JS, no deps) */
(function () {
  "use strict";
  const DATA = window.SCHEDULE_DATA;
  const DUR = DATA.meta.durationsMin;
  const LEAGUES = {
    MLB:      { label: "Giants (MLB)",   short: "MLB", color: "#fd5a1e" },
    NFL:      { label: "49ers (NFL)",    short: "NFL", color: "#e4002b" },
    MLS:      { label: "Earthquakes",    short: "MLS", color: "#0a6cff" },
    Stanford: { label: "Stanford",       short: "STAN", color: "#8c1515" },
    Cal:      { label: "Cal",           short: "CAL", color: "#003262" },
  };
  const RANGE_START = new Date(2026, 7, 1);   // Aug 1 2026
  const RANGE_END   = new Date(2026, 9, 31);  // Oct 31 2026

  // ---- state ----
  const state = {
    year: 2026,
    month: 7, // 0-indexed: 7=Aug
    selected: null,
    filter: new Set(Object.keys(LEAGUES)), // all on
  };

  // ---- time helpers (PT) ----
  function parseTimeToMin(t) {
    if (!t) return null;
    const m = String(t).match(/(\d+):(\d+)\s*(AM|PM)/i);
    if (!m) return null;
    let h = parseInt(m[1], 10);
    const min = parseInt(m[2], 10);
    const ap = m[3].toUpperCase();
    if (ap === "PM" && h !== 12) h += 12;
    if (ap === "AM" && h === 12) h = 0;
    return h * 60 + min;
  }
  function minToTime(m) {
    m = ((m % 1440) + 1440) % 1440;
    let h = Math.floor(m / 60);
    const min = m % 60;
    const ap = h >= 12 ? "PM" : "AM";
    let hh = h % 12;
    if (hh === 0) hh = 12;
    return hh + ":" + (min < 10 ? "0" + min : min) + " " + ap;
  }
  function fmtDur(min) {
    const h = Math.floor(min / 60);
    const m = min % 60;
    if (h && m) return h + "h " + m + "m";
    if (h) return h + "h";
    return m + "m";
  }
  const ISO = (d) => d.toISOString().slice(0, 10);

  // ---- data helpers ----
  function gamesOn(dateStr) {
    return DATA.games.filter((g) => g.date === dateStr);
  }
  function activeGames(dateStr) {
    return gamesOn(dateStr).filter((g) => state.filter.has(g.league));
  }

  function computeFree(dateStr) {
    const games = activeGames(dateStr);
    const intervals = [];
    let tbd = 0;
    games.forEach((g) => {
      const start = parseTimeToMin(g.startPT);
      if (start === null) { tbd++; return; }
      const dur = g.durationMin || DUR[g.league] || 180;
      intervals.push([start, Math.min(start + dur, 1440), g]);
    });
    intervals.sort((a, b) => a[0] - b[0]);
    const merged = [];
    intervals.forEach((iv) => {
      const last = merged[merged.length - 1];
      if (last && iv[0] <= last[1]) last[1] = Math.max(last[1], iv[1]);
      else merged.push([iv[0], iv[1], iv[2]]);
    });
    const free = [];
    let cur = 0;
    merged.forEach((iv) => {
      if (iv[0] > cur) free.push([cur, iv[0]]);
      cur = Math.max(cur, iv[1]);
    });
    if (cur < 1440) free.push([cur, 1440]);
    return { games, busy: merged, free, tbd };
  }

  // ---- DOM refs ----
  const $ = (id) => document.getElementById(id);
  const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  const DAYS = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
  const MONTHS_SHORT = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

  // ---- render: header / nav ----
  function renderHeader() {
    const d = state.selected;
    $("hdr-date").textContent = DAYS[d.getDay()] + ", " + MONTHS[d.getMonth()] + " " + d.getDate() + ", " + d.getFullYear();
  }

  // ---- render: calendar ----
  function renderCalendar() {
    const grid = $("calendar-grid");
    grid.innerHTML = "";
    const y = state.year, m = state.month;
    const first = new Date(y, m, 1);
    const startOffset = first.getDay(); // 0=Sun
    const daysInMonth = new Date(y, m + 1, 0).getDate();

    // weekday header
    const wk = document.createElement("div");
    wk.className = "weekday-row";
    ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].forEach((w) => {
      const c = document.createElement("div");
      c.className = "weekday-cell";
      c.textContent = w;
      wk.appendChild(c);
    });
    grid.appendChild(wk);

    const total = startOffset + daysInMonth;
    const cells = Math.ceil(total / 7) * 7;
    for (let i = 0; i < cells; i++) {
      const dayNum = i - startOffset + 1;
      const cell = document.createElement("div");
      if (dayNum < 1 || dayNum > daysInMonth) {
        cell.className = "day-cell empty";
        grid.appendChild(cell);
        continue;
      }
      const d = new Date(y, m, dayNum);
      const ds = ISO(d);
      const g = activeGames(ds);
      const isSel = ds === ISO(state.selected);
      const isToday = ds === ISO(new Date()) && new Date().getFullYear() === 2026;
      cell.className = "day-cell " + (g.length ? "busy" : "free") +
        (isSel ? " selected" : "") + (isToday ? " today" : "");
      cell.innerHTML =
        '<span class="day-number">' + dayNum + "</span>" +
        '<span class="day-status">' + (g.length ? g.length + " game" + (g.length > 1 ? "s" : "") : "FREE") + "</span>";
      if (g.length) {
        const dots = document.createElement("div");
        dots.className = "league-dots";
        const seen = {};
        g.forEach((gg) => {
          if (seen[gg.league]) return;
          seen[gg.league] = 1;
          const dot = document.createElement("span");
          dot.className = "dot";
          dot.style.background = LEAGUES[gg.league].color;
          dots.appendChild(dot);
        });
        cell.appendChild(dots);
      }
      cell.addEventListener("click", () => {
        state.selected = d;
        renderHeader();
        renderCalendar();
        renderDay();
      });
      grid.appendChild(cell);
    }
    $("cal-month-label").textContent = MONTHS[m] + " " + y;
  }

  // ---- render: day detail ----
  function renderDay() {
    const d = state.selected;
    const ds = ISO(d);
    const res = computeFree(ds);
    const wrap = $("day-detail");
    wrap.innerHTML = "";

    const title = document.createElement("div");
    title.className = "detail-title";
    title.textContent = DAYS[d.getDay()] + ", " + MONTHS[d.getMonth()] + " " + d.getDate() + ", " + d.getFullYear() + "  (Pacific Time)";
    wrap.appendChild(title);

    if (res.games.length === 0) {
      const free = document.createElement("div");
      free.className = "free-banner";
      free.innerHTML = "✅ <b>FREE ALL DAY</b> — no Giants / 49ers / Earthquakes / Stanford / Cal games scheduled.";
      wrap.appendChild(free);
      wrap.appendChild(buildTimeline([], []));
      return;
    }

    // game cards
    const list = document.createElement("div");
    list.className = "game-list";
    res.games.slice().sort((a,b)=>(parseTimeToMin(a.startPT)||0)-(parseTimeToMin(b.startPT)||0)).forEach((g) => {
      const card = document.createElement("div");
      card.className = "game-card";
      const lg = LEAGUES[g.league];
      const homeAway = g.homeAway === "home" ? "vs" : "at";
      const timeStr = g.startPT ? g.startPT + " PT" : "TBD";
      card.innerHTML =
        '<span class="league-badge" style="background:' + lg.color + '">' + lg.short + "</span>" +
        '<div class="game-info"><div class="game-match">' + g.matchup + "</div>" +
        '<div class="game-sub">' + timeStr + " &middot; ~" + fmtDur(g.durationMin) +
        (g.tbd ? " (time TBD)" : "") + "</div></div>" +
        '<a class="game-src" href="' + DATA.meta.sources[g.league].url + '" target="_blank" rel="noopener">source ↗</a>';
      list.appendChild(card);
    });
    wrap.appendChild(list);

    // timeline
    wrap.appendChild(buildTimeline(res.busy, res.free));

    // free windows text
    const fw = document.createElement("div");
    fw.className = "free-windows";
    const totalFree = res.free.reduce((s, iv) => s + (iv[1] - iv[0]), 0);
    if (res.tbd > 0) {
      const note = document.createElement("div");
      note.className = "tbd-note";
      note.textContent = "⚠ " + res.tbd + " game time(s) TBD — free windows below exclude those (added once times are confirmed).";
      fw.appendChild(note);
    }
    const head = document.createElement("div");
    head.className = "fw-head";
    head.innerHTML = "FREE TIME WINDOWS &mdash; <b>" + fmtDur(totalFree) + "</b> free (" +
      (totalFree >= 60 ? (totalFree/60).toFixed(1) + " hrs" : totalFree + " min") + ")";
    fw.appendChild(head);
    if (res.free.length === 0) {
      const p = document.createElement("div");
      p.className = "fw-item";
      p.textContent = "No free time this day (games cover the full day).";
      fw.appendChild(p);
    } else {
      res.free.forEach((iv) => {
        const p = document.createElement("div");
        p.className = "fw-item";
        p.innerHTML = "🟢 " + minToTime(iv[0]) + " – " + minToTime(iv[1]) +
          ' <span class="fw-dur">(' + fmtDur(iv[1] - iv[0]) + ")</span>";
        fw.appendChild(p);
      });
    }
    wrap.appendChild(fw);
  }

  function buildTimeline(busy, free) {
    const box = document.createElement("div");
    box.className = "timeline-box";
    const bar = document.createElement("div");
    bar.className = "timeline";
    // free base
    const base = document.createElement("div");
    base.className = "tl-free";
    bar.appendChild(base);
    busy.forEach((iv) => {
      const seg = document.createElement("div");
      seg.className = "tl-busy";
      seg.style.left = (iv[0] / 1440 * 100) + "%";
      seg.style.width = ((iv[1] - iv[0]) / 1440 * 100) + "%";
      const g = iv[2];
      seg.style.background = LEAGUES[g.league].color;
      seg.title = g.matchup + "  " + (g.startPT || "TBD") + " PT";
      bar.appendChild(seg);
    });
    box.appendChild(bar);
    // tick labels
    const ticks = document.createElement("div");
    ticks.className = "tl-ticks";
    [0, 360, 720, 1080, 1440].forEach((t) => {
      const s = document.createElement("span");
      s.style.left = (t / 1440 * 100) + "%";
      s.textContent = t === 0 ? "12a" : t === 720 ? "12p" : t === 1440 ? "12a" : (t/60>=12? (t/60-12)+"p":(t/60)+"a");
      ticks.appendChild(s);
    });
    box.appendChild(ticks);
    return box;
  }

  // ---- filters ----
  function renderFilters() {
    const box = $("filter-bar");
    box.innerHTML = "";
    const mk = (key, label) => {
      const b = document.createElement("button");
      b.className = "chip" + (state.filter.has(key) ? " on" : "");
      b.textContent = label;
      if (key !== "ALL") b.style.borderColor = LEAGUES[key].color;
      b.addEventListener("click", () => {
        if (key === "ALL") {
          state.filter = new Set(Object.keys(LEAGUES));
        } else {
          if (state.filter.has(key) && state.filter.size === 1) return; // keep at least one
          if (state.filter.has(key)) state.filter.delete(key);
          else state.filter.add(key);
          if (state.filter.size === 0) state.filter = new Set(Object.keys(LEAGUES));
        }
        renderFilters();
        renderCalendar();
        renderDay();
      });
      box.appendChild(b);
    };
    mk("ALL", "ALL");
    Object.keys(LEAGUES).forEach((k) => mk(k, LEAGUES[k].short));
  }

  // ---- navigation ----
  function shiftDay(delta) {
    const d = new Date(state.selected);
    d.setDate(d.getDate() + delta);
    if (d < RANGE_START) d.setTime(RANGE_START.getTime());
    if (d > RANGE_END) d.setTime(RANGE_END.getTime());
    state.selected = d;
    state.year = d.getFullYear();
    state.month = d.getMonth();
    renderHeader();
    renderCalendar();
    renderDay();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  function shiftMonth(delta) {
    let m = state.month + delta;
    let y = state.year;
    if (m < 7) { m = 7; y = 2026; }
    if (m > 9) { m = 9; y = 2026; }
    state.month = m; state.year = y;
    renderCalendar();
  }

  function init() {
    // default selected: today if in range else Aug 28 2026
    const now = new Date();
    let sel;
    if (now >= RANGE_START && now <= RANGE_END) sel = now;
    else sel = new Date(2026, 7, 28);
    state.selected = sel;
    state.year = sel.getFullYear();
    state.month = sel.getMonth();

    $("prev-day").addEventListener("click", () => shiftDay(-1));
    $("next-day").addEventListener("click", () => shiftDay(1));
    $("today-btn").addEventListener("click", () => {
      const t = new Date();
      if (t >= RANGE_START && t <= RANGE_END) { state.selected = t; state.year = 2026; state.month = 7; }
      else { state.selected = new Date(2026, 7, 28); state.year = 2026; state.month = 7; }
      renderHeader(); renderCalendar(); renderDay();
    });
    $("prev-month").addEventListener("click", () => shiftMonth(-1));
    $("next-month").addEventListener("click", () => shiftMonth(1));

    renderHeader();
    renderFilters();
    renderCalendar();
    renderDay();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
