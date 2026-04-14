#!/usr/bin/env python3
"""Phase F: Formation Drag System (~150 lines)
Adds right-click drag-to-formation (Total War style):
  - Drag detection (right-click hold + drag)
  - Line/double-line/blob calculation
  - Position assignment per unit
  - Formation preview ghosts while dragging
"""
import re

FILE = 'index.html'
with open(FILE, 'r') as f:
    lines = f.readlines()

def find_line(pattern, start=0):
    """Find first line index containing pattern (0-based)."""
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    raise ValueError(f"Pattern not found: {pattern}")

def insert_after(line_idx, new_code):
    """Insert lines after line_idx."""
    new_lines = [l + '\n' for l in new_code.split('\n')]
    lines[line_idx+1:line_idx+1] = new_lines

def replace_range(start, end, new_code):
    """Replace lines[start:end+1] with new_code."""
    new_lines = [l + '\n' for l in new_code.split('\n')]
    lines[start:end+1] = new_lines

# ──────────────────────────────────────────────────────────────
# 1. Add formation drag state variables after existing selection state
# ──────────────────────────────────────────────────────────────
idx = find_line("const UNIT_CIRCLE_PX")
insert_after(idx, """
// ─── FORMATION DRAG STATE ───
let formDragStart = null;   // {wx, wy} world coords where right-click began
let formDragEnd = null;     // {wx, wy} world coords of current drag position
let isFormDragging = false;  // true when right-click drag exceeds threshold
let formGhosts = [];         // [{x,y}] preview positions during drag
const FORM_DRAG_THRESHOLD = 8; // pixels before counted as drag (not click)""")

# ──────────────────────────────────────────────────────────────
# 2. Add formation calculation helper functions before checkFormations
# ──────────────────────────────────────────────────────────────
idx = find_line("// Is this unit type considered melee for formation purposes?")
insert_code = """// ─── FORMATION POSITION CALCULATOR ───
// Given drag start/end and unit count, returns [{x,y}] positions
function calcFormationPositions(sx, sy, ex, ey, count) {
  if (count === 0) return [];
  const ddx = ex - sx, ddy = ey - sy;
  const dragLen = Math.sqrt(ddx * ddx + ddy * ddy);
  const spacing = TILE_SIZE * UNIT_RADIUS * 2.5;

  // Perpendicular direction (formation line is perpendicular to drag)
  let perpX, perpY;
  if (dragLen > 1) {
    perpX = -ddy / dragLen;
    perpY = ddx / dragLen;
  } else {
    perpX = 1; perpY = 0;
  }
  // Forward direction (along drag)
  const fwdX = dragLen > 1 ? ddx / dragLen : 0;
  const fwdY = dragLen > 1 ? ddy / dragLen : 1;

  const threshold = count * spacing;
  const positions = [];

  if (dragLen > threshold * 0.8) {
    // ── SINGLE LINE: perpendicular to drag direction ──
    const lineLen = (count - 1) * spacing;
    const startOff = -lineLen / 2;
    for (let i = 0; i < count; i++) {
      positions.push({
        x: ex + perpX * (startOff + i * spacing),
        y: ey + perpY * (startOff + i * spacing)
      });
    }
  } else if (dragLen > threshold * 0.4) {
    // ── DOUBLE LINE: front + back rank ──
    const frontCount = Math.ceil(count / 2);
    const backCount = count - frontCount;
    const rowGap = spacing * 1.2;
    // Front row (at drag end)
    const fLineLen = (frontCount - 1) * spacing;
    for (let i = 0; i < frontCount; i++) {
      positions.push({
        x: ex + perpX * (-fLineLen / 2 + i * spacing),
        y: ey + perpY * (-fLineLen / 2 + i * spacing)
      });
    }
    // Back row (behind front, away from drag direction)
    const bLineLen = (backCount - 1) * spacing;
    for (let i = 0; i < backCount; i++) {
      positions.push({
        x: ex - fwdX * rowGap + perpX * (-bLineLen / 2 + i * spacing),
        y: ey - fwdY * rowGap + perpY * (-bLineLen / 2 + i * spacing)
      });
    }
  } else {
    // ── BLOB: cluster at click point (current behavior) ──
    const cols = Math.ceil(Math.sqrt(count));
    for (let i = 0; i < count; i++) {
      const oc = (i % cols) - Math.floor(cols / 2);
      const or2 = Math.floor(i / cols) - Math.floor(Math.ceil(count / cols) / 2);
      positions.push({
        x: ex + oc * spacing,
        y: ey + or2 * spacing
      });
    }
  }
  return positions;
}

"""
lines.insert(idx, insert_code + '\n')

# ──────────────────────────────────────────────────────────────
# 3. Replace the right-click mousedown handler with drag-aware version
# ──────────────────────────────────────────────────────────────
rc_start = find_line("// ─── Right-click: move selected units ───")
rc_end = find_line("addParticles(wx, wy, clickedEnemy", rc_start)
# Find the closing of that handler — 2 more lines (the }); closing)
rc_end = find_line("});", rc_end) 

replace_range(rc_start, rc_end, """// ─── Right-click: formation drag & move ───
document.getElementById('game-canvas').addEventListener('mousedown', e => {
  if (e.button !== 2) return;
  if (game.phase !== 'BUILD' && game.phase !== 'COMBAT') return;
  if (selectedUnits.length === 0) return;
  e.preventDefault();
  const z = cam.zoom;
  const wx = cam.x + e.clientX / z;
  const wy = cam.y + e.clientY / z;
  formDragStart = { wx, wy, sx: e.clientX, sy: e.clientY };
  formDragEnd = null;
  isFormDragging = false;
  formGhosts = [];
});

// ─── Right-click drag: update formation preview ───
document.getElementById('game-canvas').addEventListener('mousemove', e => {
  if (!formDragStart) return;
  if (!(e.buttons & 2)) { formDragStart = null; isFormDragging = false; formGhosts = []; return; }
  const dx = e.clientX - formDragStart.sx, dy = e.clientY - formDragStart.sy;
  if (dx * dx + dy * dy > FORM_DRAG_THRESHOLD * FORM_DRAG_THRESHOLD) {
    isFormDragging = true;
    const z = cam.zoom;
    const wx = cam.x + e.clientX / z;
    const wy = cam.y + e.clientY / z;
    formDragEnd = { wx, wy };
    // Calculate ghost preview positions
    const alive = selectedUnits.filter(u => u.hp > 0 && u.moraleState !== 'broken');
    formGhosts = calcFormationPositions(formDragStart.wx, formDragStart.wy, wx, wy, alive.length);
  }
});

// ─── Right-click release: assign formation positions or simple move ───
document.getElementById('game-canvas').addEventListener('mouseup', e => {
  if (e.button !== 2) return;
  if (!formDragStart) return;
  const z = cam.zoom;
  const wx = cam.x + e.clientX / z;
  const wy = cam.y + e.clientY / z;
  const col = Math.floor(wx / TILE_SIZE), row = Math.floor(wy / TILE_SIZE);
  if (col < 0 || col >= COLS || row < 0 || row >= ROWS) { formDragStart = null; formGhosts = []; return; }

  // Check if clicking on enemy — attack-move
  let clickedEnemy = null;
  if (game.phase === 'COMBAT') {
    for (const en of enemies) {
      const edx = en.x - wx, edy = en.y - wy;
      if (edx * edx + edy * edy < (TILE_SIZE * 0.8) * (TILE_SIZE * 0.8)) { clickedEnemy = en; break; }
    }
  }

  const alive = selectedUnits.filter(u => u.hp > 0 && u.moraleState !== 'broken');

  if (isFormDragging && formDragEnd) {
    // ── FORMATION MOVE: assign each unit to its calculated position ──
    const positions = calcFormationPositions(formDragStart.wx, formDragStart.wy, formDragEnd.wx, formDragEnd.wy, alive.length);
    for (let i = 0; i < alive.length; i++) {
      unitPathTo(alive[i], positions[i].x, positions[i].y);
    }
    addFloat('⚔ Formation', wx, wy - 10, '#64dcff');
    addParticles(wx, wy, 'rgba(100,220,255,0.4)', 6);
  } else {
    // ── SIMPLE CLICK MOVE: blob spread like before ──
    const n = alive.length;
    const spacing = TILE_SIZE * UNIT_RADIUS * 2.5;
    const cols = Math.ceil(Math.sqrt(n));
    for (let i = 0; i < n; i++) {
      const u = alive[i];
      const offsetCol = (i % cols) - Math.floor(cols / 2);
      const offsetRow = Math.floor(i / cols) - Math.floor(Math.ceil(n / cols) / 2);
      unitPathTo(u, wx + offsetCol * spacing, wy + offsetRow * spacing);
    }
    addFloat('⚔', wx, wy - 10, clickedEnemy ? '#ff6644' : '#64dcff');
    addParticles(wx, wy, clickedEnemy ? 'rgba(255,100,60,0.5)' : 'rgba(100,220,255,0.4)', 4);
  }

  formDragStart = null;
  formDragEnd = null;
  isFormDragging = false;
  formGhosts = [];
});""")

# ──────────────────────────────────────────────────────────────
# 4. Add formation ghost preview rendering in drawUnits, after box select preview
# ──────────────────────────────────────────────────────────────
idx = find_line("ctx.fillRect(bx,by,bw,bh);", find_line("BOX SELECT PREVIEW"))
# Find closing brace of that if-block
idx = find_line("}", idx)
insert_after(idx, """
  // ── FORMATION DRAG PREVIEW ──
  if (isFormDragging && formGhosts.length > 0 && formDragStart) {
    const z = cam.zoom;
    const r = UNIT_CIRCLE_PX * z;
    // Draw drag direction line
    const dsx = (formDragStart.wx - cam.x) * z, dsy = (formDragStart.wy - cam.y) * z;
    const dex = (formDragEnd.wx - cam.x) * z, dey = (formDragEnd.wy - cam.y) * z;
    ctx.strokeStyle = 'rgba(100,220,255,0.3)'; ctx.lineWidth = 2;
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(dsx, dsy); ctx.lineTo(dex, dey); ctx.stroke();
    ctx.setLineDash([]);
    // Draw ghost circles at formation positions
    for (let i = 0; i < formGhosts.length; i++) {
      const gx = (formGhosts[i].x - cam.x) * z;
      const gy = (formGhosts[i].y - cam.y) * z;
      // Ghost circle
      ctx.fillStyle = 'rgba(100,220,255,0.12)';
      ctx.beginPath(); ctx.arc(gx, gy, r, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = 'rgba(100,220,255,0.35)'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(gx, gy, r, 0, Math.PI * 2); ctx.stroke();
    }
    // Formation type label
    const alive = selectedUnits.filter(u => u.hp > 0 && u.moraleState !== 'broken');
    const ddx = formDragEnd.wx - formDragStart.wx, ddy = formDragEnd.wy - formDragStart.wy;
    const dragLen = Math.sqrt(ddx * ddx + ddy * ddy);
    const spacing = TILE_SIZE * UNIT_RADIUS * 2.5;
    const threshold = alive.length * spacing;
    let formLabel = 'Cluster';
    if (dragLen > threshold * 0.8) formLabel = 'Line';
    else if (dragLen > threshold * 0.4) formLabel = 'Double Line';
    ctx.fillStyle = 'rgba(100,220,255,0.8)'; ctx.font = `bold ${13 * z}px system-ui`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
    ctx.fillText(formLabel + ' (' + alive.length + ')', dex, dey - r - 6 * z);
    ctx.textAlign = 'start'; ctx.textBaseline = 'alphabetic';
  }""")

# ──────────────────────────────────────────────────────────────
# Write out
# ──────────────────────────────────────────────────────────────
with open(FILE, 'w') as f:
    f.writelines(lines)

print("✅ Phase F patched successfully!")
print(f"   File now has {len(lines)} lines")
