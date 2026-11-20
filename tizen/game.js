/* Game 1024 - Samsung Tizen TV web app.
 * Tiles store exponents (1 => 2, 2 => 4, ... 10 => 1024), like the Python original. */
(function () {
  'use strict';
  var N = 4, WIN = 10;
  var score, best = 0, over, won, keepPlaying;
  var boardEl = document.getElementById('board');
  var scoreEl = document.getElementById('score');
  var bestEl = document.getElementById('best');
  var overlay = document.getElementById('overlay');

  // Sound: decode each file once with the Web Audio API and replay the buffer
  // (works for rapid, overlapping plays). Falls back to a pool of Audio elements.
  var FILES = { ting: 'ting.wav', cheer: 'cheer.mp3', gameover: 'gameover.mp3' };  // ting: raw PCM, no mp3 decoder delay
  var NAMES = Object.keys(FILES);
  var AC = window.AudioContext || window.webkitAudioContext;
  var ctx = null, buffers = {}, fallback = {};
  try { if (AC) ctx = new AC({ latencyHint: 'interactive' }); } catch (e) { ctx = null; }

  function loadFallback(n) {
    if (fallback[n]) return;
    var list = [];
    for (var k = 0; k < 3; k++) {
      try { var a = new Audio('sounds/' + FILES[n]); a.preload = 'auto'; list.push(a); } catch (e) {}
    }
    fallback[n] = { list: list, next: 0 };
  }

  NAMES.forEach(function (n) {
    if (!ctx) { loadFallback(n); return; }
    try {
      var x = new XMLHttpRequest();
      x.open('GET', 'sounds/' + FILES[n], true);
      x.responseType = 'arraybuffer';
      x.onload = function () {
        try {
          var ok = function (buf) { buffers[n] = buf; };
          var bad = function (e) { console.log('decode failed ' + n, e); loadFallback(n); };
          var p = ctx.decodeAudioData(x.response, ok, bad);
          if (p && p.catch) p.catch(bad);
        } catch (e) { console.log('decode error ' + n, e); loadFallback(n); }
      };
      x.onerror = function () { console.log('load failed ' + n); loadFallback(n); };
      x.send();
    } catch (e) { loadFallback(n); }
  });

  function snd(f) {
    try {
      if (ctx && buffers[f]) {
        if (ctx.state === 'suspended' && ctx.resume) ctx.resume();
        var src = ctx.createBufferSource();
        src.buffer = buffers[f];
        src.connect(ctx.destination);
        src.start ? src.start(0) : src.noteOn(0);
        return;
      }
      var fb = fallback[f];
      if (fb && fb.list.length) {
        var a = fb.list[fb.next++ % fb.list.length];
        try { a.currentTime = 0; } catch (e) {}
        var p = a.play();
        if (p && p.catch) p.catch(function (e) { console.log('play failed ' + f, e); });
      }
    } catch (e) { console.log('snd error', e); }
  }
  // Some TV browsers keep the AudioContext suspended until a key press.
  document.addEventListener('keydown', function () {
    if (ctx && ctx.state === 'suspended' && ctx.resume) ctx.resume();
  });
  try { best = parseInt(localStorage.getItem('best1024'), 10) || 0; } catch (e) {}

  /* ---- Board: static background cells + a layer of animated tile objects ---- */
  var SLIDE = 120;          // ms, must match the transform transition in style.css
  var grid, gen = 0;        // grid[r][c] = tile object or null; gen invalidates old timers
  var layer;

  for (var i = 0; i < N * N; i++) {
    var cell = document.createElement('div');
    cell.className = 'cell';
    boardEl.appendChild(cell);
  }
  layer = document.createElement('div');
  layer.id = 'tiles';
  boardEl.appendChild(layer);

  function emptyCells() {
    var e = [];
    for (var r = 0; r < N; r++) for (var c = 0; c < N; c++) if (!grid[r][c]) e.push([r, c]);
    return e;
  }

  function setPos(t) {
    t.el.style.setProperty('--r', t.r);
    t.el.style.setProperty('--c', t.c);
  }

  /* Update the visible number/colour of a tile. merged => colour fade + pulse. */
  function refresh(t, merged) {
    var v = t.v, inner = t.inner;
    inner.textContent = Math.pow(2, v);
    if (merged && v > 1) inner.style.setProperty('--from', 'var(--c' + Math.min(v - 1, 11) + ')');
    inner.className = 'inner v' + Math.min(v, 11) + (v > 6 ? ' small' : '') +
      (t.isNew ? ' pop' : '') + (merged ? ' merge' : '');
  }

  function makeTile(r, c, v, isNew) {
    var el = document.createElement('div'), inner = document.createElement('div');
    el.className = 'tile';
    el.appendChild(inner);
    var t = { el: el, inner: inner, r: r, c: c, v: v, isNew: !!isNew };
    setPos(t);
    refresh(t, false);
    t.isNew = false;
    layer.appendChild(el);
    grid[r][c] = t;
    return t;
  }

  function removeTile(t) { if (t.el.parentNode) t.el.parentNode.removeChild(t.el); }

  function addRandom() {
    var e = emptyCells();
    if (!e.length) return null;
    var p = e[Math.floor(Math.random() * e.length)];
    return makeTile(p[0], p[1], Math.random() < 0.5 ? 1 : 2, true);   // 2 or 4
  }

  /* Cell (row, col) of position j along line k for a given direction. */
  function lineCell(dir, k, j) {
    if (dir === 'left')  return [k, j];
    if (dir === 'right') return [k, N - 1 - j];
    if (dir === 'up')    return [j, k];
    return [N - 1 - j, k];
  }

  function move(dir) {
    var changed = false, gained = 0, reached = false, merged = false, pending = [];
    for (var k = 0; k < N; k++) {
      var line = [];
      for (var j = 0; j < N; j++) {
        var p = lineCell(dir, k, j), t = grid[p[0]][p[1]];
        if (t) line.push(t);
      }
      var slot = 0;
      for (var i = 0; i < line.length; i++) {
        var cur = line[i], pos = lineCell(dir, k, slot);
        if (i + 1 < line.length && line[i + 1].v === cur.v) {
          var other = line[i + 1];
          cur.v += 1;
          gained += Math.pow(2, cur.v); merged = true; if (cur.v === WIN) reached = true;
          other.r = pos[0]; other.c = pos[1]; setPos(other);   // slides onto cur, then vanishes
          pending.push([cur, other]);
          changed = true; i++;
        }
        if (cur.r !== pos[0] || cur.c !== pos[1]) changed = true;
        cur.r = pos[0]; cur.c = pos[1]; setPos(cur);
        slot++;
      }
    }
    // rebuild the grid from the surviving tiles
    var removed = pending.map(function (pr) { return pr[1]; });
    var old = grid;
    grid = []; for (var r = 0; r < N; r++) grid.push([null, null, null, null]);
    for (r = 0; r < N; r++) for (var c = 0; c < N; c++) {
      var tl = old[r][c];
      if (tl && removed.indexOf(tl) < 0) grid[tl.r][tl.c] = tl;
    }
    var myGen = gen;
    pending.forEach(function (pr) {                     // after the slide: drop the absorbed tile, show merge
      setTimeout(function () {
        removeTile(pr[1]);
        if (myGen === gen) refresh(pr[0], true);
      }, SLIDE);
    });
    return { changed: changed, gained: gained, reached: reached, merged: merged };
  }

  function canMove() {
    if (emptyCells().length) return true;
    for (var r = 0; r < N; r++) for (var c = 0; c < N; c++) {
      if (c + 1 < N && grid[r][c].v === grid[r][c + 1].v) return true;
      if (r + 1 < N && grid[r][c].v === grid[r + 1][c].v) return true;
    }
    return false;
  }

  function updateScore() { scoreEl.textContent = score; bestEl.textContent = best; }

  function showOverlay(title, text) {
    var myGen = gen;
    setTimeout(function () {                 // let the last move finish animating first
      if (myGen !== gen) return;
      document.getElementById('ov-title').textContent = title;
      document.getElementById('ov-text').textContent = text;
      overlay.classList.remove('hidden');
    }, SLIDE + 250);
  }

  function newGame() {
    gen++;
    while (layer.firstChild) layer.removeChild(layer.firstChild);
    grid = []; for (var r = 0; r < N; r++) grid.push([null, null, null, null]);
    score = 0; over = false; won = false; keepPlaying = false;
    overlay.classList.add('hidden');
    addRandom(); addRandom(); updateScore();
  }

  function onDir(dir) {
    if (over || (won && !keepPlaying)) return;
    var res = move(dir);
    if (!res.changed) return;
    score += res.gained;
    if (score > best) { best = score; try { localStorage.setItem('best1024', best); } catch (e) {} }
    if (res.merged) snd('ting');
    addRandom();
    updateScore();
    if (res.reached && !keepPlaying) {
      won = true; snd('cheer');
      showOverlay('YOU WIN!', 'You reached 1024!  Press OK to continue.');
    } else if (!canMove()) {
      over = true; snd('gameover');
      showOverlay('G A M E   O V E R', 'Score ' + score + '.  Press OK for a new game.');
    }
  }

  function exitApp() {
    try { tizen.application.getCurrentApplication().exit(); } catch (e) { window.close(); }
  }

  var exitEl = document.getElementById('exit'), exitAsk = false;
  function askExit(show) { exitAsk = show; exitEl.classList.toggle('hidden', !show); }

  document.addEventListener('keydown', function (e) {
    if (exitAsk) {                                // exit popup: OK = leave, RETURN = back to game
      if (e.keyCode === 13) exitApp();
      else if (e.keyCode === 10009 || e.keyCode === 27) askExit(false);
      return;
    }
    switch (e.keyCode) {
      case 37: case 65: onDir('left'); break;
      case 38: case 87: onDir('up'); break;
      case 39: case 68: onDir('right'); break;
      case 40: case 83: onDir('down'); break;
      case 13:                                   // OK / Enter
        if (won && !keepPlaying) { keepPlaying = true; overlay.classList.add('hidden'); }
        else newGame();
        break;
      case 10009: case 27: askExit(true); break;  // Samsung RETURN key / Esc: ask before exiting
    }
  });

  newGame();
})();
