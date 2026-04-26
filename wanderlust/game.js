// ── DATA ────────────────────────────────────────────────────────────────────

const COLORS = {
  terracotta: '#C1440E',
  gold:       '#D4A017',
  blue:       '#1B4F8A',
  brown:      '#6B3A2A',
  green:      '#2D6A4F',
  rose:       '#B5445A',
  sand:       '#C9A96E',
};

const COLOR_KEYS = Object.keys(COLORS);

// Each window: { name, cols, rows, active (flat array, 1=active 0=inactive), pieces }
// pieces: { shape: [[row,col],...], color }
const WINDOWS = [
  {
    name: 'Side Gallery Window',
    cols: 4, rows: 4,
    active: [
      1,1,1,1,
      1,1,1,1,
      1,1,1,1,
      1,1,1,1,
    ],
    pieces: [
      { id:'p1', shape:[[0,0],[0,1],[1,0],[1,1]], color:'gold'       }, // 2x2
      { id:'p2', shape:[[0,0],[1,0],[2,0],[2,1]], color:'terracotta' }, // L
      { id:'p3', shape:[[0,0],[0,1],[1,1],[2,1]], color:'blue'       }, // reverse-L
      { id:'p4', shape:[[0,0],[0,1]],             color:'brown'      }, // domino
      { id:'p5', shape:[[0,0]],                   color:'sand'       }, // single
    ],
  },
  {
    name: 'Left Tower Arch',
    cols: 4, rows: 5,
    active: [
      0,1,1,0,
      1,1,1,1,
      1,1,1,1,
      1,1,1,1,
      1,1,1,1,
    ],
    pieces: [
      { id:'p1', shape:[[0,0],[0,1],[1,0],[1,1]], color:'gold'       },
      { id:'p2', shape:[[0,0],[1,0],[2,0],[2,1]], color:'terracotta' },
      { id:'p3', shape:[[0,0],[0,1],[1,1],[2,1]], color:'blue'       },
      { id:'p4', shape:[[0,0],[1,0],[1,1],[2,1]], color:'rose'       }, // S
      { id:'p5', shape:[[0,0],[0,1]],             color:'brown'      },
      { id:'p6', shape:[[0,0]],                   color:'sand'       },
    ],
  },
  {
    name: 'Central Royal Arch',
    cols: 5, rows: 5,
    active: [
      0,1,1,1,0,
      1,1,1,1,1,
      1,1,1,1,1,
      1,1,1,1,1,
      1,1,1,1,1,
    ],
    pieces: [
      { id:'p1', shape:[[0,0],[0,1],[1,0],[1,1]], color:'gold'       },
      { id:'p2', shape:[[0,0],[1,0],[2,0],[2,1]], color:'terracotta' },
      { id:'p3', shape:[[0,0],[0,1],[1,1],[2,1]], color:'blue'       },
      { id:'p4', shape:[[0,0],[1,0],[1,1],[2,1]], color:'rose'       },
      { id:'p5', shape:[[0,0],[0,1],[0,2],[1,1]], color:'green'      }, // T
      { id:'p6', shape:[[0,0],[0,1]],             color:'brown'      },
      { id:'p7', shape:[[0,0]],                   color:'sand'       },
    ],
  },
  {
    name: 'Right Tower Arch',
    cols: 4, rows: 5,
    active: [
      0,1,1,0,
      1,1,1,1,
      1,1,1,1,
      1,1,1,1,
      1,1,1,1,
    ],
    pieces: [
      { id:'p1', shape:[[0,0],[0,1],[1,0],[1,1]], color:'gold'       },
      { id:'p2', shape:[[0,0],[1,0],[2,0],[1,1]], color:'terracotta' }, // T variant
      { id:'p3', shape:[[0,0],[0,1],[1,0],[2,0]], color:'blue'       },
      { id:'p4', shape:[[0,0],[1,0],[1,1],[2,1]], color:'rose'       },
      { id:'p5', shape:[[0,0],[0,1]],             color:'brown'      },
      { id:'p6', shape:[[0,0]],                   color:'sand'       },
    ],
  },
  {
    name: 'Grand Entrance',
    cols: 4, rows: 6,
    active: [
      0,1,1,0,
      1,1,1,1,
      1,1,1,1,
      1,1,1,1,
      1,1,1,1,
      1,1,1,1,
    ],
    pieces: [
      { id:'p1', shape:[[0,0],[0,1],[1,0],[1,1]], color:'gold'       },
      { id:'p2', shape:[[0,0],[1,0],[2,0],[2,1]], color:'terracotta' },
      { id:'p3', shape:[[0,0],[0,1],[1,1],[2,1]], color:'blue'       },
      { id:'p4', shape:[[0,0],[1,0],[1,1],[2,1]], color:'rose'       },
      { id:'p5', shape:[[0,0],[0,1],[0,2],[1,1]], color:'green'      },
      { id:'p6', shape:[[0,0],[0,1]],             color:'brown'      },
      { id:'p7', shape:[[0,0]],                   color:'sand'       },
    ],
  },
];

const STORY = [
  { chapter:'Outer Gallery', text:'I am the wind of the Thar desert. Every morning I arrive at Hawa Mahal\'s gates. Every morning the frames are empty. Fill them. Let me in.' },
  { chapter:'Left Tower',    text:'I slipped through the outer gallery. But the three great towers still sleep. Their arched eyes are shut. I must go higher.' },
  { chapter:'Central Arch',  text:'The royal arch. The grandest window. No wind has passed through in two centuries. Today that changes.' },
  { chapter:'Right Tower',   text:'I move symmetrically, as the architect intended. The right tower mirrors the left. Balance restored.' },
  { chapter:'Grand Entrance',text:'The deepest chamber. The queen\'s entrance. One last frame to fill. Guide me home.' },
];

const SKY_COLORS = [
  '#0A0603', '#1A0E08', '#2D1A0A', '#5C3010', '#8B5020',
  '#F0C840',
];

// ── STATE ────────────────────────────────────────────────────────────────────

const state = {
  windowIdx: 0,
  selectedPiece: null,        // piece id
  grid: [],                   // flat array: null | pieceId
  pieces: [],                 // copy of current window pieces with placed flag
  wrongPlacements: 0,
  completedWindows: [],
};

// ── HELPERS ──────────────────────────────────────────────────────────────────

function idx(row, col, cols) { return row * cols + col; }

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2200);
}

function setSky(level) {
  document.getElementById('sky').style.background = SKY_COLORS[Math.min(level, SKY_COLORS.length - 1)];
}

function lightPalaceWindow(idx) {
  const el = document.getElementById('pal-w' + (idx + 1));
  if (!el) return;
  el.style.transition = 'opacity 1.2s';
  el.style.opacity = '1';
  // Make window glow gold
  el.querySelectorAll('rect').forEach(r => {
    r.setAttribute('fill', '#F0C840');
    r.style.filter = 'drop-shadow(0 0 8px #F0C840)';
  });
}

function getPiece(id) { return state.pieces.find(p => p.id === id); }

// ── GRID RENDERING ───────────────────────────────────────────────────────────

function renderGrid() {
  const win = WINDOWS[state.windowIdx];
  const grid = document.getElementById('grid');
  grid.style.gridTemplateColumns = `repeat(${win.cols}, 48px)`;
  grid.innerHTML = '';

  for (let r = 0; r < win.rows; r++) {
    for (let c = 0; c < win.cols; c++) {
      const i = idx(r, c, win.cols);
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.dataset.row = r;
      cell.dataset.col = c;

      if (!win.active[i]) {
        cell.classList.add('inactive');
      } else if (state.grid[i]) {
        const pieceId = state.grid[i];
        const piece = getPiece(pieceId);
        cell.classList.add('filled');
        cell.style.background = COLORS[piece.color];
        cell.style.border = '1px solid rgba(0,0,0,0.3)';
        cell.addEventListener('click', () => liftPiece(r, c));
      } else {
        cell.classList.add('empty');
        cell.addEventListener('click', () => placePiece(r, c));
      }

      // highlight valid targets
      if (state.selectedPiece && !win.active[i] === false && !state.grid[i]) {
        if (canPlace(state.selectedPiece, r, c)) {
          cell.classList.add('valid-target');
        }
      }

      grid.appendChild(cell);
    }
  }
}

function renderTray() {
  const tray = document.getElementById('tray');
  tray.innerHTML = '';
  state.pieces.forEach(piece => {
    if (piece.placed) return;
    const btn = buildPieceButton(piece);
    tray.appendChild(btn);
  });
}

function buildPieceButton(piece) {
  const rows = Math.max(...piece.shape.map(([r]) => r)) + 1;
  const cols = Math.max(...piece.shape.map(([, c]) => c)) + 1;
  const btn = document.createElement('div');
  btn.className = 'piece-btn' + (state.selectedPiece === piece.id ? ' selected' : '');
  btn.dataset.pieceId = piece.id;
  btn.style.gridTemplateColumns = `repeat(${cols}, 16px)`;
  btn.style.gridTemplateRows = `repeat(${rows}, 16px)`;
  btn.style.display = 'grid';

  const cells = Array.from({ length: rows * cols }, () => {
    const d = document.createElement('div');
    d.className = 'piece-cell';
    d.style.background = 'transparent';
    return d;
  });

  piece.shape.forEach(([r, c]) => {
    cells[r * cols + c].style.background = COLORS[piece.color];
    cells[r * cols + c].style.borderRadius = '2px';
  });

  cells.forEach(c => btn.appendChild(c));
  btn.addEventListener('click', () => selectPiece(piece.id));
  return btn;
}

// ── PIECE LOGIC ───────────────────────────────────────────────────────────────

function selectPiece(id) {
  state.selectedPiece = state.selectedPiece === id ? null : id;
  renderGrid();
  renderTray();
}

function canPlace(pieceId, row, col) {
  const win = WINDOWS[state.windowIdx];
  const piece = getPiece(pieceId);
  return piece.shape.every(([dr, dc]) => {
    const r = row + dr, c = col + dc;
    if (r < 0 || r >= win.rows || c < 0 || c >= win.cols) return false;
    const i = idx(r, c, win.cols);
    return win.active[i] && !state.grid[i];
  });
}

function placePiece(row, col) {
  if (!state.selectedPiece) return;
  if (!canPlace(state.selectedPiece, row, col)) {
    // wrong placement flash
    state.wrongPlacements++;
    const win = WINDOWS[state.windowIdx];
    const i = idx(row, col, win.cols);
    const cells = document.getElementById('grid').querySelectorAll('.cell');
    cells[i].classList.add('wrong');
    setTimeout(() => cells[i].classList.remove('wrong'), 400);
    return;
  }
  const win = WINDOWS[state.windowIdx];
  const piece = getPiece(state.selectedPiece);
  piece.shape.forEach(([dr, dc]) => {
    state.grid[idx(row + dr, col + dc, win.cols)] = piece.id;
  });
  piece.placed = true;
  state.selectedPiece = null;
  renderGrid();
  renderTray();
  checkCompletion();
}

function liftPiece(row, col) {
  const win = WINDOWS[state.windowIdx];
  const i = idx(row, col, win.cols);
  const pieceId = state.grid[i];
  if (!pieceId) return;
  const piece = getPiece(pieceId);
  // remove all cells of this piece from grid
  piece.shape.forEach(([dr, dc]) => {
    const pr = row + dr, pc = col + dc;
    // find anchor
  });
  // Find anchor row/col by scanning grid for this piece
  for (let r = 0; r < win.rows; r++) {
    for (let c = 0; c < win.cols; c++) {
      if (state.grid[idx(r, c, win.cols)] === pieceId) {
        state.grid[idx(r, c, win.cols)] = null;
      }
    }
  }
  piece.placed = false;
  state.selectedPiece = pieceId;
  renderGrid();
  renderTray();
}

function checkCompletion() {
  const win = WINDOWS[state.windowIdx];
  const done = win.active.every((active, i) => !active || state.grid[i]);
  if (!done) return;

  const stars = state.wrongPlacements === 0 ? 3 : state.wrongPlacements <= 3 ? 2 : 1;
  state.completedWindows.push({ idx: state.windowIdx, stars });

  lightPalaceWindow(state.windowIdx);
  setSky(state.completedWindows.length);
  showToast(`✨ ${win.name} restored!`);

  if (state.windowIdx < WINDOWS.length - 1) {
    setTimeout(() => {
      state.windowIdx++;
      loadWindow(state.windowIdx);
      showScreen('story-screen');
      loadStory(state.windowIdx);
    }, 1800);
  } else {
    setTimeout(() => showWin(), 1800);
  }
}

// ── HINT ─────────────────────────────────────────────────────────────────────

document.getElementById('hint-btn').addEventListener('click', () => {
  const unplaced = state.pieces.filter(p => !p.placed);
  if (!unplaced.length) return;
  const next = unplaced[0];
  showToast(`Try the ${next.color} piece next`);
  selectPiece(next.id);
});

document.getElementById('reset-btn').addEventListener('click', () => {
  loadWindow(state.windowIdx);
});

// ── WINDOW LOADER ─────────────────────────────────────────────────────────────

function loadWindow(i) {
  const win = WINDOWS[i];
  state.grid = win.active.map(() => null);
  state.pieces = win.pieces.map(p => ({ ...p, shape: p.shape.map(s => [...s]), placed: false }));
  state.selectedPiece = null;
  state.wrongPlacements = 0;

  document.getElementById('window-name').textContent = win.name;
  document.getElementById('window-sub').textContent = `Fill the frame · Window ${i + 1} of ${WINDOWS.length}`;
  document.getElementById('progress-text').textContent = `Window ${i + 1} of ${WINDOWS.length}`;
  renderGrid();
  renderTray();
}

// ── STORY ─────────────────────────────────────────────────────────────────────

function loadStory(i) {
  const s = STORY[i];
  document.getElementById('story-chapter').textContent = s.chapter;
  document.getElementById('story-text').textContent = s.text;
  document.getElementById('story-btn').textContent = i === 0 ? 'Begin Puzzle' : 'Continue';
}

document.getElementById('story-btn').addEventListener('click', () => {
  showScreen('puzzle-screen');
});

// ── WIN SCREEN ────────────────────────────────────────────────────────────────

function showWin() {
  const totalStars = state.completedWindows.reduce((s, w) => s + w.stars, 0);
  const maxStars = WINDOWS.length * 3;
  const pct = totalStars / maxStars;
  const starEl = document.getElementById('win-stars');
  const filled = Math.round(pct * 3);
  starEl.innerHTML = ['⭐','⭐','⭐'].map((s, i) => i < filled ? s : '☆').join('');
  showScreen('win-screen');
}

document.getElementById('next-city-btn').addEventListener('click', () => {
  showToast('More cities coming soon! 🌍');
});

// ── BOOT ──────────────────────────────────────────────────────────────────────

loadStory(0);
loadWindow(0);
setSky(0);
