#!/usr/bin/env python3
"""Phase E: Movable Units — Complete patch script.

Converts the entire unit system from tile-based (col/row) to position-based (x/y)
with selection, movement, pathfinding, auto-engagement, collision, and new rendering.
"""

import re, sys

FILE = 'index.html'

with open(FILE, 'r') as f:
    src = f.read()
lines = src.split('\n')

def find_line(pattern, start=0):
    """Find line number (0-indexed) containing pattern."""
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    raise ValueError(f"Pattern not found: {pattern}")

def find_line_exact(text, start=0):
    """Find line matching exact stripped text."""
    for i in range(start, len(lines)):
        if lines[i].strip() == text.strip():
            return i
    raise ValueError(f"Exact text not found: {text}")

def replace_line(idx, new_text):
    """Replace a single line."""
    lines[idx] = new_text

def replace_range(start, end, new_lines):
    """Replace lines[start:end+1] with new_lines list."""
    lines[start:end+1] = new_lines

def insert_after(idx, new_lines):
    """Insert new_lines after line idx."""
    for i, line in enumerate(new_lines):
        lines.insert(idx + 1 + i, line)

def insert_before(idx, new_lines):
    """Insert new_lines before line idx."""
    for i, line in enumerate(new_lines):
        lines.insert(idx + i, line)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 1: Update UNIT_TYPES with real speeds (per plan)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 1: Updating UNIT_TYPES speeds...")

# Militia speed: 3 t/s
idx = find_line("MILITIA:{name:'Militia'")
lines[idx] = lines[idx].replace("speed:0,", "speed:3,")

# Archer speed: 2.5 t/s
idx = find_line("ARCHER:{name:'Archer'")
lines[idx] = lines[idx].replace("speed:0,", "speed:2.5,")

# Spearman speed: 2.5 t/s
idx = find_line("SPEARMAN:{name:'Spearman'")
lines[idx] = lines[idx].replace("speed:0,", "speed:2.5,")

# Cavalry speed already 4.5 — update to 6
idx = find_line("CAVALRY:{name:'Cavalry'")
lines[idx] = lines[idx].replace("speed:4.5,", "speed:6,")

# Catapult speed: 1.5 t/s
idx = find_line("CATAPULT:{name:'Catapult'")
lines[idx] = lines[idx].replace("speed:0,", "speed:1.5,")

print("  ✓ Unit speeds updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 2: Update units array comment & add selection state
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 2: Adding selection state...")

idx = find_line("const units=[];")
replace_line(idx, "const units=[];      // army units: {type, x, y, hp, maxHP, dmg, range, speed, xp, morale, state, path, pathIdx, targetX, targetY}")

# Add selection state after units array
insert_after(idx, [
    "",
    "// ─── UNIT SELECTION STATE ───",
    "let selectedUnits = [];        // currently selected unit references",
    "let controlGroups = [null, null, null]; // Ctrl+1/2/3 saved groups",
    "let boxSelectStart = null;     // {sx, sy} screen coords for box select",
    "let boxSelectEnd = null;       // {sx, sy} screen coords",
    "let isBoxSelecting = false;",
    "const UNIT_RADIUS = 0.4;      // collision radius in tiles",
    "const UNIT_CIRCLE_PX = 12;    // visual radius in pixels (at zoom 1)",
])

print("  ✓ Selection state added")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 3: Update training queue spawn to use x/y
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 3: Updating training queue spawn...")

# Find the newUnit creation in updateTrainingQueues
idx = find_line("type: current.type, col: spawn.col, row: spawn.row,")
# Replace the entire unit creation block (lines idx to idx+5)
end_idx = find_line("units.push(newUnit);", idx)
replace_range(idx - 1, end_idx, [
    "        const newUnit = {",
    "          type: current.type,",
    "          x: spawn.col * TILE_SIZE + TILE_SIZE / 2,",
    "          y: spawn.row * TILE_SIZE + TILE_SIZE / 2,",
    "          hp: ud.hp, maxHP: ud.hp, dmg: ud.dmg, range: ud.range,",
    "          speed: ud.speed || 2.5,",
    "          xp: 0, _lastRank: 0, morale: MORALE_MAX, state: 'idle',",
    "          moraleState: 'normal', fleeTimer: 0, _fleeMoveTimer: 0,",
    "          atkCooldown: 0, path: null, pathIdx: 0,",
    "          targetX: null, targetY: null, engageTarget: null,",
    "        };",
    "        units.push(newUnit);",
])

# Update the float text after spawn to use unit x/y
idx = find_line("ud.name + ' trained!'", find_line("type: current.type,"))
lines[idx] = "        addFloat(ud.name + ' trained!', newUnit.x, newUnit.y - TILE_SIZE, '#8ac0e8');"

idx = find_line("addParticles(spawn.col * TILE_SIZE", find_line("ud.name + ' trained!'"))
lines[idx] = "        addParticles(newUnit.x, newUnit.y, 'rgba(' + ud.color[0] + ',' + ud.color[1] + ',' + ud.color[2] + ',0.7)', 8);"

print("  ✓ Training queue spawn updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 4: Rewrite updateUnits — position-based movement + auto-engage
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 4: Rewriting updateUnits...")

start_idx = find_line("function updateUnits(dt){")
# Find the end of updateUnits — it's followed by the spearman zone of control block
# which is followed by findAdjacentUnit
end_idx = find_line("function findAdjacentUnit(")
# Go back to find the closing of updateUnits (the line before findAdjacentUnit section)
# Actually, spearman ZoC passive is at end of updateUnits before the comment for findAdjacentUnit
end_comment = find_line("// ─── ENEMY RETARGETING", start_idx)
end_idx = end_comment - 1
# Trim trailing blank lines
while lines[end_idx].strip() == '':
    end_idx -= 1

# Also include the CATAPULT_AOE_RADIUS constant that's just above
aoe_line = find_line("const CATAPULT_AOE_RADIUS=")

new_update_units = [
    "const CATAPULT_AOE_RADIUS=1.5; // AOE radius in tiles (covers ~3×3)",
    "",
    "// ─── Helper: find nearest visible enemy within range (px) from world position ───",
    "function findNearestEnemy(wx, wy, rangePx) {",
    "  let nearest = null, nearDist = Infinity;",
    "  for (const e of enemies) {",
    "    const ec = Math.floor(e.x / TILE_SIZE), er = Math.floor(e.y / TILE_SIZE);",
    "    if (ec < 0 || ec >= COLS || er < 0 || er >= ROWS || fogMap[ec][er] !== FOG_VISIBLE) continue;",
    "    const dx = e.x - wx, dy = e.y - wy, dSq = dx * dx + dy * dy;",
    "    if (dSq <= rangePx * rangePx && dSq < nearDist) { nearDist = dSq; nearest = e; }",
    "  }",
    "  return nearest;",
    "}",
    "",
    "// ─── Unit pathfinding: A* then smooth walk ───",
    "function unitPathTo(u, goalX, goalY) {",
    "  const sc = Math.floor(u.x / TILE_SIZE), sr = Math.floor(u.y / TILE_SIZE);",
    "  const gc = Math.floor(goalX / TILE_SIZE), gr = Math.floor(goalY / TILE_SIZE);",
    "  if (sc === gc && sr === gr) { u.path = null; u.targetX = goalX; u.targetY = goalY; return; }",
    "  const path = findPath(sc, sr, gc, gr);",
    "  if (path && path.length > 0) {",
    "    u.path = path;",
    "    u.pathIdx = 0;",
    "    u.targetX = goalX;",
    "    u.targetY = goalY;",
    "    u.state = 'moving';",
    "  }",
    "}",
    "",
    "// ─── Collision: push units apart if overlapping ───",
    "function resolveUnitCollisions() {",
    "  const minDist = TILE_SIZE * UNIT_RADIUS * 2;",
    "  const minDistSq = minDist * minDist;",
    "  for (let i = 0; i < units.length; i++) {",
    "    for (let j = i + 1; j < units.length; j++) {",
    "      const a = units[i], b = units[j];",
    "      const dx = b.x - a.x, dy = b.y - a.y;",
    "      const dSq = dx * dx + dy * dy;",
    "      if (dSq < minDistSq && dSq > 0.01) {",
    "        const dist = Math.sqrt(dSq);",
    "        const overlap = (minDist - dist) / 2;",
    "        const nx = dx / dist, ny = dy / dist;",
    "        a.x -= nx * overlap; a.y -= ny * overlap;",
    "        b.x += nx * overlap; b.y += ny * overlap;",
    "        // Clamp to map",
    "        a.x = Math.max(TILE_SIZE / 2, Math.min(MAP_PX_W - TILE_SIZE / 2, a.x));",
    "        a.y = Math.max(TILE_SIZE / 2, Math.min(MAP_PX_H - TILE_SIZE / 2, a.y));",
    "        b.x = Math.max(TILE_SIZE / 2, Math.min(MAP_PX_W - TILE_SIZE / 2, b.x));",
    "        b.y = Math.max(TILE_SIZE / 2, Math.min(MAP_PX_H - TILE_SIZE / 2, b.y));",
    "      }",
    "    }",
    "  }",
    "}",
    "",
    "function updateUnits(dt) {",
    "  // Movement works in both BUILD and COMBAT; combat only in COMBAT",
    "  for (let i = units.length - 1; i >= 0; i--) {",
    "    const u = units[i];",
    "    if (u.hp <= 0) continue;",
    "    u.atkCooldown = Math.max(0, u.atkCooldown - dt);",
    "",
    "    // ── BROKEN MORALE: skip combat AI (handled by updateFleeingUnits) ──",
    "    if (u.moraleState === 'broken') continue;",
    "",
    "    // ── MOVEMENT along path ──",
    "    if (u.path && u.pathIdx < u.path.length) {",
    "      const wp = u.path[u.pathIdx];",
    "      const tx = wp.c * TILE_SIZE + TILE_SIZE / 2, ty = wp.r * TILE_SIZE + TILE_SIZE / 2;",
    "      const dx = tx - u.x, dy = ty - u.y;",
    "      const dist = Math.sqrt(dx * dx + dy * dy);",
    "      const speed = (u.speed || 2.5) * TILE_SIZE * dt;",
    "      if (dist <= speed) {",
    "        u.x = tx; u.y = ty;",
    "        u.pathIdx++;",
    "        if (u.pathIdx >= u.path.length) {",
    "          // Arrived at final waypoint — go to exact target",
    "          if (u.targetX !== null) { u.x = u.targetX; u.y = u.targetY; }",
    "          u.path = null; u.state = 'idle';",
    "        }",
    "      } else {",
    "        u.x += dx / dist * speed;",
    "        u.y += dy / dist * speed;",
    "      }",
    "    }",
    "",
    "    // ── COMBAT: auto-engage nearest enemy in range ──",
    "    if (game.phase !== 'COMBAT') continue;",
    "    if (u.atkCooldown > 0) continue;",
    "",
    "    const rangePx = u.range * TILE_SIZE;",
    "    const nearest = findNearestEnemy(u.x, u.y, rangePx);",
    "    if (!nearest) continue;",
    "",
    "    if (u.type === 'MILITIA') {",
    "      u.atkCooldown = getUnitAtkRate(u);",
    "      let dmg = u.dmg;",
    "      const isLastStand = unitRank(u.xp) >= 3 && u.hp / u.maxHP < 0.3;",
    "      nearest.hp -= dmg;",
    "      nearest.hitFlash = 1;",
    "      addFloat(`${isLastStand ? '🛡️ ' : ''}−${dmg}`, nearest.x, nearest.y - 14, '#7ab0d8');",
    "      addParticles(nearest.x, nearest.y, 'rgba(90,140,200,0.7)', 4);",
    "      if (nearest.hp <= 0) {",
    "        const idx = enemies.indexOf(nearest);",
    "        if (idx >= 0) { killEnemy(nearest, idx, 'unit', u); u.xp += 10; }",
    "      } else { u.xp += 1; const nr = checkRankUp(u); if (nr > 0) showRankUpEffect(u, nr); }",
    "    }",
    "    else if (u.type === 'ARCHER') {",
    "      u.atkCooldown = getUnitAtkRate(u);",
    "      projectiles.push({",
    "        x: u.x, y: u.y, tx: nearest.x, ty: nearest.y,",
    "        speed: 250, dmg: u.dmg, target: nearest, age: 0,",
    "        source: 'unit', sourceUnit: u,",
    "        color: 'rgba(80,180,110,0.9)', trailColor: 'rgba(80,180,110,0.3)',",
    "      });",
    "      if (unitRank(u.xp) >= 3) {",
    "        const spread = TILE_SIZE * 0.3;",
    "        projectiles.push({",
    "          x: u.x + spread * (Math.random() - 0.5), y: u.y + spread * (Math.random() - 0.5),",
    "          tx: nearest.x, ty: nearest.y,",
    "          speed: 260, dmg: u.dmg, target: nearest, age: 0,",
    "          source: 'unit', sourceUnit: u,",
    "          color: 'rgba(120,220,140,0.9)', trailColor: 'rgba(120,220,140,0.3)',",
    "        });",
    "      }",
    "      u.xp += 1; const nr = checkRankUp(u); if (nr > 0) showRankUpEffect(u, nr);",
    "    }",
    "    else if (u.type === 'SPEARMAN') {",
    "      u.atkCooldown = getUnitAtkRate(u);",
    "      const isChampion = unitRank(u.xp) >= 3;",
    "      const isFast = ENEMY_TYPES[nearest.type] && ENEMY_TYPES[nearest.type].speed >= 5;",
    "      const fastMult = isChampion ? 3.0 : SPEAR_FAST_MULT;",
    "      const dmg = isFast ? Math.round(u.dmg * fastMult) : u.dmg;",
    "      nearest.hp -= dmg; nearest.hitFlash = 1;",
    "      const impaleLabel = isChampion && isFast ? '⚔️ IMPALE ' : '';",
    "      addFloat(`${impaleLabel}${isFast ? '🔱 ' : ''}−${dmg}`, nearest.x, nearest.y - 14, isFast ? '#ffe040' : '#c0b040');",
    "      addParticles(nearest.x, nearest.y, isFast ? 'rgba(255,220,60,0.8)' : 'rgba(180,160,60,0.7)', isFast ? 6 : 4);",
    "      const zocMult = isChampion ? 1.5 : 1;",
    "      const zocPx = SPEAR_SLOW_RADIUS * TILE_SIZE * zocMult;",
    "      for (const e of enemies) {",
    "        const edx = e.x - u.x, edy = e.y - u.y;",
    "        if (edx * edx + edy * edy <= zocPx * zocPx) {",
    "          e.slowTimer = Math.max(e.slowTimer, isChampion ? SPEAR_SLOW_DUR * 1.5 : SPEAR_SLOW_DUR);",
    "        }",
    "      }",
    "      if (nearest.hp <= 0) {",
    "        const idx = enemies.indexOf(nearest);",
    "        if (idx >= 0) { killEnemy(nearest, idx, 'unit', u); u.xp += 10; }",
    "      } else { u.xp += isFast ? 2 : 1; const nr = checkRankUp(u); if (nr > 0) showRankUpEffect(u, nr); }",
    "    }",
    "    else if (u.type === 'CAVALRY') {",
    "      cavalryAttack(u, nearest);",
    "    }",
    "    else if (u.type === 'CATAPULT') {",
    "      const isFirestorm = unitRank(u.xp) >= 3;",
    "      u.atkCooldown = getUnitAtkRate(u);",
    "      projectiles.push({",
    "        x: u.x, y: u.y, tx: nearest.x, ty: nearest.y,",
    "        speed: 160, dmg: u.dmg, target: nearest, age: 0,",
    "        source: 'unit', sourceUnit: u, aoe: true,",
    "        aoeMultiplier: isFirestorm ? 2.0 : 1.0,",
    "        color: isFirestorm ? 'rgba(255,120,30,0.95)' : 'rgba(160,120,80,0.95)',",
    "        trailColor: isFirestorm ? 'rgba(255,80,20,0.5)' : 'rgba(140,100,60,0.4)',",
    "        size: isFirestorm ? 7 : 5,",
    "      });",
    "      u.xp += 2; const nr = checkRankUp(u); if (nr > 0) showRankUpEffect(u, nr);",
    "    }",
    "  }",
    "",
    "  // ── SPEARMAN ZONE OF CONTROL: passive slow aura each frame ──",
    "  for (const u of units) {",
    "    if (u.type !== 'SPEARMAN' || u.hp <= 0) continue;",
    "    const zocPx = SPEAR_SLOW_RADIUS * TILE_SIZE;",
    "    for (const e of enemies) {",
    "      const dx = e.x - u.x, dy = e.y - u.y;",
    "      if (dx * dx + dy * dy <= zocPx * zocPx) {",
    "        e.slowTimer = Math.max(e.slowTimer, 0.2);",
    "      }",
    "    }",
    "  }",
    "",
    "  // ── Resolve collisions between friendly units ──",
    "  resolveUnitCollisions();",
    "}",
]

replace_range(aoe_line, end_comment - 1, new_update_units)

print("  ✓ updateUnits rewritten with movement + auto-engage + collision")

# Save progress
with open(FILE, 'w') as f:
    f.write('\n'.join(lines))
print("  ✓ Saved intermediate (Step 4)")
