/* Game 1024 - Samsung Tizen TV web app.
 * Tiles store exponents (1 => 2, 2 => 4, ... 10 => 1024), like the Python original. */
(function () {
  'use strict';
  var N = 4, WIN = 10;
  var board, score, best = 0, over, won, keepPlaying;
  var boardEl = document.getElementById('board');
  var scoreEl = document.getElementById('score');
  var bestEl = document.getElementById('best');
  var overlay = document.getElementById('overlay');
  var tiles = [];

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

  for (var i = 0; i < N * N; i++) {
    var d = document.createElement('div');
    d.className = 'tile';
    boardEl.appendChild(d);
    tiles.push(d);
  }

  function emptyCells() {
    var e = [];
    for (var r = 0; r < N; r++) for (var c = 0; c < N; c++) if (!board[r][c]) e.push([r, c]);
    return e;
  }

  function addRandom() {
    var e = emptyCells();
    if (!e.length) return null;
    var p = e[Math.floor(Math.random() * e.length)];
    board[p[0]][p[1]] = Math.random() < 0.5 ? 1 : 2;   // 2 or 4
    return p;
  }

  /* Slide and merge one row to the left. Returns {row, gained, reached} */
  function slideRow(row) {
    var s = row.filter(function (v) { return v; }), out = [], gained = 0, reached = false;
    for (var i = 0; i < s.length; i++) {
      if (i + 1 < s.length && s[i] === s[i + 1]) {
        var v = s[i] + 1;
        out.push(v); gained += Math.pow(2, v); if (v === WIN) reached = true; i++;
      } else out.push(s[i]);
    }
    while (out.length < N) out.push(0);
    return { row: out, gained: gained, reached: reached };
  }

  function move(dir) {
    var changed = false, gained = 0, reached = false, merged = false;
    for (var k = 0; k < N; k++) {
      var line = [];
      for (var j = 0; j < N; j++) {
        line.push(dir === 'left' ? board[k][j] : dir === 'right' ? board[k][N - 1 - j]
                : dir === 'up' ? board[j][k] : board[N - 1 - j][k]);
      }
      var res = slideRow(line);
      for (j = 0; j < N; j++) {
        var r = dir === 'left' ? k : dir === 'right' ? k : dir === 'up' ? j : N - 1 - j;
        var c = dir === 'left' ? j : dir === 'right' ? N - 1 - j : k;
        if (board[r][c] !== res.row[j]) { changed = true; board[r][c] = res.row[j]; }
      }
      if (res.gained) merged = true;
      gained += res.gained; reached = reached || res.reached;
    }
    return { changed: changed, gained: gained, reached: reached, merged: merged };
  }

  function canMove() {
    if (emptyCells().length) return true;
    for (var r = 0; r < N; r++) for (var c = 0; c < N; c++) {
      if (c + 1 < N && board[r][c] === board[r][c + 1]) return true;
      if (r + 1 < N && board[r][c] === board[r + 1][c]) return true;
    }
    return false;
  }

  function render(newPos) {
    for (var r = 0; r < N; r++) for (var c = 0; c < N; c++) {
      var v = board[r][c], t = tiles[r * N + c];
      t.textContent = v ? Math.pow(2, v) : '';
      t.className = 'tile' + (v ? ' v' + Math.min(v, 11) : '') + (v > 6 ? ' small' : '') +
        (newPos && newPos[0] === r && newPos[1] === c ? ' pop' : '');
    }
    scoreEl.textContent = score; bestEl.textContent = best;
  }

  function showOverlay(title, text) {
    document.getElementById('ov-title').textContent = title;
    document.getElementById('ov-text').textContent = text;
    overlay.classList.remove('hidden');
  }

  function newGame() {
    board = []; for (var r = 0; r < N; r++) board.push([0, 0, 0, 0]);
    score = 0; over = false; won = false; keepPlaying = false;
    overlay.classList.add('hidden');
    addRandom(); addRandom(); render();
  }

  function onDir(dir) {
    if (over || (won && !keepPlaying)) return;
    var res = move(dir);
    if (!res.changed) return;
    score += res.gained;
    if (score > best) { best = score; try { localStorage.setItem('best1024', best); } catch (e) {} }
    var p = addRandom();
    if (res.merged) snd('ting');   // start the sound first, then draw
    render(p);
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

  document.addEventListener('keydown', function (e) {
    switch (e.keyCode) {
      case 37: case 65: onDir('left'); break;
      case 38: case 87: onDir('up'); break;
      case 39: case 68: onDir('right'); break;
      case 40: case 83: onDir('down'); break;
      case 13:                                   // OK / Enter
        if (won && !keepPlaying) { keepPlaying = true; overlay.classList.add('hidden'); }
        else newGame();
        break;
      case 10009: case 27: exitApp(); break;     // Samsung RETURN key / Esc
    }
  });

  newGame();
})();
