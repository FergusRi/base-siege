#!/usr/bin/env python3
"""Phase E Part 3: Input handlers — selection, right-click move, control groups."""

import re, sys

FILE = 'index.html'

with open(FILE, 'r') as f:
    src = f.read()
lines = src.split('\n')

def find_line(pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    raise ValueError(f"Pattern not found from line {start}: {pattern}")

def find_line_safe(pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def replace_range(start, end, new_lines):
    lines[start:end+1] = new_lines

def insert_after(idx, new_lines):
    for i, line in enumerate(new_lines):
        lines.insert(idx + 1 + i, line)

def insert_before(idx, new_lines):
    for i, line in enumerate(new_lines):
        lines.insert(idx + i, line)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 22: Add right-click handler (contextmenu + mousedown)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 22: Adding right-click move + unit selection handlers...")

# Find the minimap event listener (after the main canvas click handler)
idx = find_line("document.getElementById('minimap').addEventListener('mousedown'")

# Insert the full selection + right-click system BEFORE the minimap listener
insert_before(idx, [
    "",
    "// ═══════════════════════════════════════════════════════",
    "//  UNIT SELECTION & MOVEMENT INPUT  ",
    "// ═══════════════════════════════════════════════════════",
    "",
    "// Prevent context menu on canvas (we use right-click for move)",
    "document.getElementById('game-canvas').addEventListener('contextmenu', e => e.preventDefault());",
    "",
    "// ─── Helper: find unit at world position ───",
    "function unitAtWorld(wx, wy) {",
    "  const clickR = TILE_SIZE * 0.6; // generous click radius",
    "  let best = null, bestDist = Infinity;",
    "  for (const u of units) {",
    "    if (u.hp <= 0) continue;",
    "    const dx = u.x - wx, dy = u.y - wy;",
    "    const d = dx * dx + dy * dy;",
    "    if (d < clickR * clickR && d < bestDist) { bestDist = d; best = u; }",
    "  }",
    "  return best;",
    "}",
    "",
    "// ─── Right-click: move selected units ───",
    "document.getElementById('game-canvas').addEventListener('mousedown', e => {",
    "  if (e.button !== 2) return; // right-click only",
    "  if (game.phase !== 'BUILD' && game.phase !== 'COMBAT') return;",
    "  if (selectedUnits.length === 0) return;",
    "  e.preventDefault();",
    "  const z = cam.zoom;",
    "  const wx = cam.x + e.clientX / z;",
    "  const wy = cam.y + e.clientY / z;",
    "  const col = Math.floor(wx / TILE_SIZE), row = Math.floor(wy / TILE_SIZE);",
    "  if (col < 0 || col >= COLS || row < 0 || row >= ROWS) return;",
    "",
    "  // Check if clicking on enemy — attack-move",
    "  let clickedEnemy = null;",
    "  if (game.phase === 'COMBAT') {",
    "    for (const en of enemies) {",
    "      const dx = en.x - wx, dy = en.y - wy;",
    "      if (dx * dx + dy * dy < (TILE_SIZE * 0.8) * (TILE_SIZE * 0.8)) { clickedEnemy = en; break; }",
    "    }",
    "  }",
    "",
    "  // Move each selected unit (spread out if multiple)",
    "  const n = selectedUnits.length;",
    "  const spacing = TILE_SIZE * UNIT_RADIUS * 2.5;",
    "  const cols = Math.ceil(Math.sqrt(n));",
    "  for (let i = 0; i < n; i++) {",
    "    const u = selectedUnits[i];",
    "    if (u.hp <= 0 || u.moraleState === 'broken') continue;",
    "    const offsetCol = (i % cols) - Math.floor(cols / 2);",
    "    const offsetRow = Math.floor(i / cols) - Math.floor(Math.ceil(n / cols) / 2);",
    "    const destX = wx + offsetCol * spacing;",
    "    const destY = wy + offsetRow * spacing;",
    "    unitPathTo(u, destX, destY);",
    "  }",
    "",
    "  // Move marker effect",
    "  addFloat('⚔', wx, wy - 10, clickedEnemy ? '#ff6644' : '#64dcff');",
    "  addParticles(wx, wy, clickedEnemy ? 'rgba(255,100,60,0.5)' : 'rgba(100,220,255,0.4)', 4);",
    "});",
    "",
    "// ─── Left-click unit selection (mousedown for box select start) ───",
    "let _leftDownForSelect = null; // track left-click for box vs click",
    "",
    "document.getElementById('game-canvas').addEventListener('mousedown', e => {",
    "  if (e.button !== 0) return; // left-click only",
    "  if (game.phase !== 'BUILD' && game.phase !== 'COMBAT') return;",
    "  // Don't interfere with build mode clicks",
    "  if (uiMode === 'build' && selectedTool !== 'gather' && selectedTool !== 'DEMOLISH') return;",
    "  if (e.clientY < 88) return; // skip toolbar area",
    "  _leftDownForSelect = { sx: e.clientX, sy: e.clientY, time: performance.now() };",
    "  boxSelectStart = { sx: e.clientX, sy: e.clientY };",
    "  boxSelectEnd = null;",
    "  isBoxSelecting = false;",
    "});",
    "",
    "document.getElementById('game-canvas').addEventListener('mousemove', e => {",
    "  if (!_leftDownForSelect) return;",
    "  if (e.buttons !== 1) { _leftDownForSelect = null; isBoxSelecting = false; return; }",
    "  const dx = e.clientX - _leftDownForSelect.sx, dy = e.clientY - _leftDownForSelect.sy;",
    "  if (dx * dx + dy * dy > 64) { // 8px threshold for drag",
    "    isBoxSelecting = true;",
    "    boxSelectEnd = { sx: e.clientX, sy: e.clientY };",
    "  }",
    "});",
    "",
    "document.getElementById('game-canvas').addEventListener('mouseup', e => {",
    "  if (e.button !== 0) return;",
    "  if (!_leftDownForSelect) return;",
    "  const z = cam.zoom;",
    "",
    "  if (isBoxSelecting && boxSelectStart && boxSelectEnd) {",
    "    // ── BOX SELECT: select all units within the box ──",
    "    const x1 = Math.min(boxSelectStart.sx, boxSelectEnd.sx);",
    "    const y1 = Math.min(boxSelectStart.sy, boxSelectEnd.sy);",
    "    const x2 = Math.max(boxSelectStart.sx, boxSelectEnd.sx);",
    "    const y2 = Math.max(boxSelectStart.sy, boxSelectEnd.sy);",
    "    if (!e.shiftKey) selectedUnits = [];",
    "    for (const u of units) {",
    "      if (u.hp <= 0) continue;",
    "      const sx = (u.x - cam.x) * z, sy = (u.y - cam.y) * z;",
    "      if (sx >= x1 && sx <= x2 && sy >= y1 && sy <= y2) {",
    "        if (!selectedUnits.includes(u)) selectedUnits.push(u);",
    "      }",
    "    }",
    "  } else {",
    "    // ── CLICK SELECT: single unit ──",
    "    const wx = cam.x + e.clientX / z;",
    "    const wy = cam.y + e.clientY / z;",
    "    const clicked = unitAtWorld(wx, wy);",
    "    if (clicked) {",
    "      if (e.shiftKey) {",
    "        // Toggle selection",
    "        const idx = selectedUnits.indexOf(clicked);",
    "        if (idx >= 0) selectedUnits.splice(idx, 1);",
    "        else selectedUnits.push(clicked);",
    "      } else {",
    "        selectedUnits = [clicked];",
    "      }",
    "    } else if (!e.shiftKey) {",
    "      // Click empty ground — only deselect if we're in gather mode",
    "      if (selectedTool === 'gather') selectedUnits = [];",
    "    }",
    "  }",
    "",
    "  _leftDownForSelect = null;",
    "  isBoxSelecting = false;",
    "  boxSelectStart = null;",
    "  boxSelectEnd = null;",
    "});",
    "",
])

print("  ✓ Selection + right-click move handlers added")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 23: Add control groups (Ctrl+1/2/3) and ESC deselect
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 23: Adding control groups + ESC deselect...")

# Find the keydown handler and add control group logic
# The Escape handler already exists — extend it
idx = find_line("if(e.key==='Escape'){")
# Insert a selectedUnits deselect before the cavalryPendingUnit line  
# The line after Escape is: cavalryPendingUnit removed
next_line = idx + 1
insert_after(idx, [
    "      selectedUnits = [];",
])

# Now add control group handling. Find the build mode key handlers
# Insert before the "In build mode: 1/2/3 switch categories" section
idx = find_line("// In build mode: 1/2/3 switch categories")

# Add Ctrl+1/2/3 control groups BEFORE the build mode key check
insert_before(idx, [
    "    // ── CONTROL GROUPS: Ctrl+1/2/3 to save, 1/2/3 to recall (in gather mode) ──",
    "    if(e.ctrlKey&&(e.key==='1'||e.key==='2'||e.key==='3')){",
    "      const gi=parseInt(e.key)-1;",
    "      controlGroups[gi]=selectedUnits.length>0?[...selectedUnits]:null;",
    "      addFloat(`Group ${e.key} saved (${selectedUnits.length})`,hero.x,hero.y-TILE_SIZE*2,'#64dcff');",
    "      e.preventDefault(); return;",
    "    }",
    "    if(!e.ctrlKey&&uiMode!=='build'&&(e.key==='1'||e.key==='2'||e.key==='3')){",
    "      const gi=parseInt(e.key)-1;",
    "      if(controlGroups[gi]&&controlGroups[gi].length>0){",
    "        selectedUnits=controlGroups[gi].filter(u=>u.hp>0);",
    "        if(selectedUnits.length>0){",
    "          // Center camera on group",
    "          let ax=0,ay=0;",
    "          for(const u of selectedUnits){ax+=u.x;ay+=u.y;}",
    "          cam.tx=ax/selectedUnits.length-canvas.width/2;",
    "          cam.ty=ay/selectedUnits.length-canvas.height/2;",
    "        }",
    "      }",
    "      return;",
    "    }",
])

print("  ✓ Control groups + ESC deselect added")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 24: Add 'A' key for select-all units
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 24: Adding select-all (A key)...")

# Add after the gather mode G key handler
idx = find_line("// G: back to gather")
insert_before(idx, [
    "    // A: select all units",
    "    if((e.key==='a'||e.key==='A')&&e.ctrlKey){",
    "      e.preventDefault();",
    "      selectedUnits=units.filter(u=>u.hp>0);",
    "      return;",
    "    }",
])
print("  ✓ Select-all added")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 25: Update the game loop to also call updateUnits during BUILD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 25: Updating game loop for BUILD phase movement...")

# Find where updateUnits is called only during COMBAT
idx = find_line("updateUnits(dt);")
# Check if it's inside a COMBAT block — it should be at the line after updateTowers
# We need units to also move during BUILD phase (for right-click move orders)
# The current updateUnits already handles: movement in any phase, combat only in COMBAT
# But it's only called during COMBAT. Let's move it outside the COMBAT block.

# Find the COMBAT if block
combat_if = find_line("if(game.phase==='COMBAT'){")
# Read the block to understand structure
# Let's just add a separate updateUnits call before the COMBAT block
insert_before(combat_if, [
    "  // Unit movement (works during BUILD too for move orders)",
    "  if(game.phase==='BUILD') updateUnits(dt);",
])

print("  ✓ Game loop updated for BUILD-phase unit movement")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 26: Clean up any remaining u.col/u.row references
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 26: Scanning for remaining u.col/u.row references...")

remaining_refs = []
for i, line in enumerate(lines):
    # Skip comments and the old comment we left
    stripped = line.strip()
    if stripped.startswith('//') or stripped.startswith('*'):
        continue
    # Check for unit references that use .col or .row in unit context
    if 'u.col' in line or 'u.row' in line:
        # Skip if it's about structures or citizens or enemies (different u variable)
        if 'cit.' in line or 'enemy' in line.lower():
            continue
        remaining_refs.append((i+1, line.strip()[:100]))

if remaining_refs:
    print(f"  ⚠ Found {len(remaining_refs)} remaining u.col/u.row references:")
    for lnum, text in remaining_refs[:15]:
        print(f"    Line {lnum}: {text}")
else:
    print("  ✓ No remaining u.col/u.row references!")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 27: Update hover info panel for x/y
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 27: Updating unit info panel...")

# The updateUnitInfoPanel uses unitAt which is already updated
# But it might have references to u.col/u.row for display
idx = find_line("function updateUnitInfoPanel()")
# Check for col/row in the function
for i in range(idx, min(idx + 40, len(lines))):
    if 'u.col' in lines[i] or 'u.row' in lines[i]:
        lines[i] = lines[i].replace('u.col', 'Math.floor(u.x/TILE_SIZE)').replace('u.row', 'Math.floor(u.y/TILE_SIZE)')
        print(f"  Fixed line {i+1}")

print("  ✓ Unit info panel updated")

# Save
with open(FILE, 'w') as f:
    f.write('\n'.join(lines))
print("\n  ✓ Saved (Part 3 complete)")
