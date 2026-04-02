/**
 * Interactive hexagonal grid with brain logo silhouette.
 * Canvas-based rendering with mouse-proximity amber warmth effect.
 *
 * Only initializes if #hexGrid canvas is present (landing page).
 */
(() => {
  const canvas = document.getElementById('hexGrid');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // --- Brain cell data (from scripts/extract_brain_hex_grid.py) ---
  const BRAIN_GRID_COLS = 27;
  const BRAIN_GRID_ROWS = 27;
  const BRAIN_CELLS = [[0,9],[0,11],[0,13],[1,7],[1,8],[1,9],[1,10],[1,12],[1,13],[1,14],[1,15],[2,5],[2,6],[2,14],[2,15],[3,5],[3,6],[3,7],[3,8],[3,9],[3,16],[3,17],[4,4],[4,5],[4,8],[4,9],[4,10],[4,11],[4,16],[4,17],[5,3],[5,4],[5,9],[5,10],[5,12],[5,13],[5,16],[5,17],[6,3],[6,4],[6,8],[6,15],[6,16],[6,17],[6,18],[6,19],[7,3],[7,4],[7,13],[7,14],[7,15],[7,16],[7,18],[7,19],[8,2],[8,3],[8,7],[8,9],[8,12],[8,13],[8,14],[8,18],[8,19],[8,20],[9,2],[9,6],[9,7],[9,8],[9,9],[9,10],[9,11],[9,12],[9,13],[9,16],[9,17],[9,20],[10,2],[10,5],[10,6],[10,10],[10,11],[10,12],[10,15],[10,16],[10,19],[10,20],[11,1],[11,2],[11,3],[11,4],[11,5],[11,6],[11,12],[11,13],[11,15],[11,19],[11,20],[12,1],[12,2],[12,11],[12,12],[12,13],[12,15],[12,16],[12,17],[12,19],[12,20],[13,1],[13,2],[13,7],[13,8],[13,9],[13,11],[13,12],[13,15],[13,16],[13,19],[13,20],[13,21],[14,1],[14,5],[14,6],[14,8],[14,10],[14,11],[14,14],[14,15],[14,18],[14,19],[14,20],[14,21],[15,1],[15,2],[15,4],[15,5],[15,9],[15,10],[15,11],[15,13],[15,14],[15,18],[15,19],[15,20],[15,21],[15,22],[15,23],[16,1],[16,2],[16,4],[16,9],[16,10],[16,13],[16,14],[16,17],[16,18],[16,19],[16,20],[16,21],[16,22],[16,23],[17,1],[17,2],[17,9],[17,11],[17,13],[17,14],[17,17],[17,18],[17,22],[17,23],[17,24],[17,25],[18,2],[18,3],[18,8],[18,11],[18,12],[18,13],[18,17],[18,18],[18,23],[18,24],[18,25],[18,26],[19,2],[19,3],[19,11],[19,12],[19,13],[19,15],[19,17],[19,18],[19,23],[19,26],[20,2],[20,3],[20,7],[20,8],[20,9],[20,10],[20,14],[20,17],[20,23],[21,3],[21,4],[21,5],[21,7],[21,8],[21,16],[21,17],[21,23],[22,4],[22,5],[22,13],[22,14],[22,16],[22,17],[22,22],[23,6],[23,7],[23,13],[23,16],[23,17],[23,21],[23,22],[24,6],[24,7],[24,12],[24,13],[24,16],[24,17],[24,19],[24,20],[25,8],[25,9],[25,10],[25,11],[25,13],[25,15],[25,16],[25,18],[26,10],[26,12],[26,13],[26,14],[26,15],[26,16]];

  const brainSet = new Set(BRAIN_CELLS.map(([c, r]) => c + ',' + r));

  // --- Configuration ---
  const EFFECT_RADIUS = 190;
  const LERP_SPEED   = 0.065;
  const FILL_MAX_ALPHA = 0.13;
  const STROKE_BASE  = 224;      // #e0e0e0
  const STROKE_ACTIVE = 148;
  const STROKE_W_MIN = 0.5;
  const STROKE_W_MAX = 1.7;
  const AMBER = [212, 146, 11];

  // Brain cell rendering
  const BRAIN_FILL = [158, 158, 158];
  const BRAIN_FILL_ALPHA = 0.10;      // resting — barely visible watermark
  const BRAIN_FILL_ALPHA_LIT = 0.35;  // revealed on hover
  const BRAIN_INSET = 0.88;

  // Pointy-top hex vertex offsets
  function makeVerts(radius) {
    return Array.from({ length: 6 }, (_, i) => {
      const a = (Math.PI / 3) * i - Math.PI / 6;
      return [Math.cos(a) * radius, Math.sin(a) * radius];
    });
  }

  // --- State ---
  let hexes = [];
  let HEX_SIZE, VERTS, VERTS_INSET, hStep, vStep;
  let gridOriginX, gridOriginY;
  let mouse = { x: -9999, y: -9999 };
  let dpr, W, H;
  let useAmbient = window.matchMedia('(hover: none)').matches;
  let ambientT = Math.random() * 100;
  let canvasVisible = true;
  let rafId = null;

  // --- Text-zone fade (measured from DOM elements) ---
  let headerRect = null, navRect = null;
  function updateTextZones() {
    const hb = document.querySelector('.landing-header');
    const nb = document.getElementById('siteNav');
    if (hb) {
      const r = hb.getBoundingClientRect();
      headerRect = {
        cx: r.left + r.width / 2,
        cy: r.top + r.height / 2,
        hw: r.width * 0.7 + 60,
        hh: r.height * 0.7 + 40,
      };
    }
    if (nb && !nb.classList.contains('stuck')) {
      const r = nb.getBoundingClientRect();
      navRect = {
        cx: r.left + r.width / 2,
        cy: r.top + r.height / 2,
        hw: r.width * 0.6 + 60,
        hh: r.height * 0.7 + 40,
      };
    } else {
      navRect = null;
    }
  }

  function textZoneFade(x, y) {
    let fade = 1;
    if (headerRect) {
      const hdx = (x - headerRect.cx) / headerRect.hw;
      const hdy = (y - headerRect.cy) / headerRect.hh;
      const hd = hdx * hdx + hdy * hdy;
      if (hd < 1) fade = Math.min(fade, 0.1 + 0.9 * hd);
    }
    if (navRect) {
      const ndx = (x - navRect.cx) / navRect.hw;
      const ndy = (y - navRect.cy) / navRect.hh;
      const nd = ndx * ndx + ndy * ndy;
      if (nd < 1) fade = Math.min(fade, 0.1 + 0.9 * nd);
    }
    return fade;
  }

  // --- Grid geometry ---
  function computeHexSize() {
    // Size the hex so the brain fits in ~50% of viewport height
    const targetH = H * 0.50;
    HEX_SIZE = targetH / (BRAIN_GRID_ROWS * 1.5);
    HEX_SIZE = Math.max(8, Math.min(20, HEX_SIZE));

    VERTS = makeVerts(HEX_SIZE);
    VERTS_INSET = makeVerts(HEX_SIZE * BRAIN_INSET);
    hStep = Math.sqrt(3) * HEX_SIZE;
    vStep = HEX_SIZE * 1.5;

    // Center the brain between header text and nav bar
    // Header is position:fixed so getBoundingClientRect is always reliable.
    // Nav position is computed from viewport height (not measured) because
    // on mobile the nav may be stuck at top during resize from URL bar toggle.
    const brainPixelW = (BRAIN_GRID_COLS - 1) * hStep + hStep * 0.5;
    const brainPixelH = (BRAIN_GRID_ROWS - 1) * vStep;
    gridOriginX = (W - brainPixelW) / 2;

    const hdr = document.querySelector('.landing-header');
    const topBound = hdr ? hdr.getBoundingClientRect().bottom : H * 0.15;
    const bottomBound = H - 64; // nav height in px, matches $nav-height
    gridOriginY = (topBound + bottomBound) / 2 - brainPixelH / 2;
  }

  function buildGrid() {
    hexes = [];
    const cMin = Math.floor(-gridOriginX / hStep) - 2;
    const cMax = Math.ceil((W - gridOriginX) / hStep) + 2;
    const rMin = Math.floor(-gridOriginY / vStep) - 2;
    const rMax = Math.ceil((H - gridOriginY) / vStep) + 2;

    for (let r = rMin; r <= rMax; r++) {
      for (let c = cMin; c <= cMax; c++) {
        const x = gridOriginX + c * hStep + (r & 1 ? hStep * 0.5 : 0);
        const y = gridOriginY + r * vStep;
        const isBrain = (c >= 0 && c < BRAIN_GRID_COLS && r >= 0 && r < BRAIN_GRID_ROWS)
                        && brainSet.has(c + ',' + r);
        hexes.push({ x, y, t: 0, brain: isBrain });
      }
    }
  }

  function resize() {
    dpr = window.devicePixelRatio || 1;
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width  = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width  = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    computeHexSize();
    buildGrid();
    updateTextZones();
  }

  // --- Drawing ---
  function traceHex(cx, cy, verts) {
    ctx.moveTo(cx + verts[0][0], cy + verts[0][1]);
    for (let i = 1; i < 6; i++) ctx.lineTo(cx + verts[i][0], cy + verts[i][1]);
    ctx.closePath();
  }

  function frame() {
    if (useAmbient) {
      ambientT += 0.003;
      mouse.x = W * 0.5 + Math.cos(ambientT) * W * 0.28
                         + Math.sin(ambientT * 0.61) * W * 0.10;
      mouse.y = H * 0.5 + Math.sin(ambientT * 0.73) * H * 0.20
                         + Math.cos(ambientT * 0.47) * H * 0.08;
    }

    ctx.clearRect(0, 0, W, H);

    const mx = mouse.x, my = mouse.y;
    const rr = EFFECT_RADIUS * EFFECT_RADIUS;
    const idle = [];
    const idleBrain = [];
    const lit = [];

    for (let i = 0, n = hexes.length; i < n; i++) {
      const h = hexes[i];
      const dx = h.x - mx, dy = h.y - my;
      const d2 = dx * dx + dy * dy;

      let target = 0;
      if (d2 < rr) {
        const raw = 1 - Math.sqrt(d2) / EFFECT_RADIUS;
        target = raw * raw * textZoneFade(h.x, h.y);
      }

      h.t += (target - h.t) * LERP_SPEED;
      if (h.t < 0.003) {
        h.t = 0;
        if (h.brain) idleBrain.push(h);
        else idle.push(h);
      } else {
        lit.push(h);
      }
    }

    // Batch idle grid hexes
    if (idle.length) {
      ctx.beginPath();
      for (let i = 0, n = idle.length; i < n; i++) traceHex(idle[i].x, idle[i].y, VERTS);
      ctx.strokeStyle = '#e0e0e0';
      ctx.lineWidth = STROKE_W_MIN;
      ctx.stroke();
    }

    // Idle brain hexes: grid stroke + inset fill
    if (idleBrain.length) {
      ctx.beginPath();
      for (let i = 0, n = idleBrain.length; i < n; i++) traceHex(idleBrain[i].x, idleBrain[i].y, VERTS);
      ctx.strokeStyle = '#e0e0e0';
      ctx.lineWidth = STROKE_W_MIN;
      ctx.stroke();

      ctx.beginPath();
      for (let i = 0, n = idleBrain.length; i < n; i++) traceHex(idleBrain[i].x, idleBrain[i].y, VERTS_INSET);
      ctx.fillStyle = `rgba(${BRAIN_FILL[0]},${BRAIN_FILL[1]},${BRAIN_FILL[2]},${BRAIN_FILL_ALPHA})`;
      ctx.fill();
    }

    // Lit hexes (individually styled)
    for (let i = 0, n = lit.length; i < n; i++) {
      const h = lit[i];
      const t = h.t;

      ctx.beginPath();
      traceHex(h.x, h.y, VERTS);

      ctx.fillStyle = `rgba(${AMBER[0]},${AMBER[1]},${AMBER[2]},${(t * FILL_MAX_ALPHA).toFixed(4)})`;
      ctx.fill();

      const g = Math.round(STROKE_BASE - t * (STROKE_BASE - STROKE_ACTIVE));
      ctx.strokeStyle = `rgb(${g},${g},${g})`;
      ctx.lineWidth = STROKE_W_MIN + t * (STROKE_W_MAX - STROKE_W_MIN);
      ctx.stroke();

      // Brain cells: lerp fill from resting to revealed
      if (h.brain) {
        ctx.beginPath();
        traceHex(h.x, h.y, VERTS_INSET);
        const ba = BRAIN_FILL_ALPHA + t * (BRAIN_FILL_ALPHA_LIT - BRAIN_FILL_ALPHA);
        ctx.fillStyle = `rgba(${BRAIN_FILL[0]},${BRAIN_FILL[1]},${BRAIN_FILL[2]},${ba.toFixed(3)})`;
        ctx.fill();
      }
    }

    if (canvasVisible) rafId = requestAnimationFrame(frame);
  }

  function startLoop() {
    if (!rafId) rafId = requestAnimationFrame(frame);
  }

  function stopLoop() {
    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
  }

  // Pause rendering when canvas is scrolled out of view
  new IntersectionObserver(([entry]) => {
    canvasVisible = entry.isIntersecting;
    if (canvasVisible) startLoop(); else stopLoop();
  }).observe(canvas);

  // --- Scroll: fade overlay/canvas, toggle nav stuck state ---
  const overlay = document.querySelector('.landing-overlay');
  const nav = document.getElementById('siteNav');
  const spacer = document.querySelector('.landing-spacer');

  function onScroll() {
    const scrollY = window.scrollY;
    const fade = Math.max(0, 1 - scrollY / (H * 0.6));
    if (overlay) overlay.style.opacity = fade;
    canvas.style.opacity = fade;

    // Toggle stuck class when nav reaches the top
    if (spacer && nav) {
      const spacerBottom = spacer.getBoundingClientRect().bottom;
      const isStuck = spacerBottom <= 0;
      nav.classList.toggle('stuck', isStuck);
      updateTextZones();
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  // --- Input events ---
  window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
  window.addEventListener('mouseleave', () => { if (!useAmbient) { mouse.x = -9999; mouse.y = -9999; } });
  window.addEventListener('resize', resize);
  window.addEventListener('touchmove', e => {
    useAmbient = false;
    mouse.x = e.touches[0].clientX;
    mouse.y = e.touches[0].clientY;
  }, { passive: true });
  window.addEventListener('touchend', () => { setTimeout(() => { useAmbient = true; }, 2500); });

  // --- Text-zone size tracking ---
  const headerEl = document.querySelector('.landing-header');
  if (headerEl) {
    new ResizeObserver(() => updateTextZones()).observe(headerEl);
  }

  // --- Init ---
  resize();
  startLoop();
})();
