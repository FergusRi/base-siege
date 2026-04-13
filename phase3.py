#!/usr/bin/env python3
"""
Phase 3: Shared Helper Functions
  3A: Unified modifyVision() replacing 8 duplicate vision loop patterns
  3B: createCitizen() factory replacing 3 duplicate object literals
  3C: Merge nearestSettlement() + findNearestSettlementTile() into one function

Strategy: Read all lines, apply surgical replacements by line number,
working bottom-to-top so line numbers stay valid.
"""
import sys

FILE = 'index.html'

with open(FILE, 'r') as f:
    lines = f.readlines()

original_count = len(lines)
print(f"Read {original_count} lines from {FILE}")

# ============================================================
# PHASE 3A: Unified modifyVision() helper
# ============================================================
# We'll insert modifyVision() right after initFogMap() (line 814),
# then replace all 8 vision loop patterns with calls to it.

# The new function handles both permanent (visionCount-tracked) and
# non-tracked (hero reveal) vision, plus explore radius.
MODIFY_VISION_FUNC = '''\
function modifyVision(cx, cy, visRadius, delta, expRadius) {
  // Unified vision helper — handles add/remove vision + optional explore ring
  // delta: +1 to add permanent vision, -1 to remove, 0 for non-tracked reveal
  const er = expRadius || visRadius;
  const maxR = Math.max(visRadius, er);
  for (let dc = -maxR; dc <= maxR; dc++) {
    for (let dr = -maxR; dr <= maxR; dr++) {
      const nc = cx + dc, nr = cy + dr;
      if (nc < 0 || nc >= COLS || nr < 0 || nr >= ROWS) continue;
      const dist = Math.sqrt(dc * dc + dr * dr);
      if (dist <= visRadius) {
        if (delta > 0) {
          visionCount[nc][nr]++;
          fogMap[nc][nr] = FOG_VISIBLE;
        } else if (delta < 0) {
          visionCount[nc][nr] = Math.max(0, visionCount[nc][nr] - 1);
          if (visionCount[nc][nr] === 0 && fogMap[nc][nr] === FOG_VISIBLE) {
            fogMap[nc][nr] = FOG_EXPLORED;
          }
        } else {
          // delta === 0: non-tracked reveal (hero vision)
          fogMap[nc][nr] = FOG_VISIBLE;
        }
      } else if (dist <= er && fogMap[nc][nr] < FOG_EXPLORED) {
        fogMap[nc][nr] = FOG_EXPLORED;
      }
    }
  }
  markSpawnRingDirty();
}
'''

# Also need a tracked variant for hero vision that pushes to visibleTiles
MODIFY_VISION_TRACKED_FUNC = '''\
function modifyVisionTracked(cx, cy, visRadius, expRadius) {
  // Hero vision — like modifyVision but tracks newly-visible tiles for decay
  const er = expRadius || visRadius;
  const maxR = Math.max(visRadius, er);
  for (let dc = -maxR; dc <= maxR; dc++) {
    for (let dr = -maxR; dr <= maxR; dr++) {
      const nc = cx + dc, nr = cy + dr;
      if (nc < 0 || nc >= COLS || nr < 0 || nr >= ROWS) continue;
      const dist = Math.sqrt(dc * dc + dr * dr);
      if (dist <= visRadius) {
        if (fogMap[nc][nr] !== FOG_VISIBLE) visibleTiles.push([nc, nr]);
        fogMap[nc][nr] = FOG_VISIBLE;
      } else if (dist <= er && fogMap[nc][nr] < FOG_EXPLORED) {
        fogMap[nc][nr] = FOG_EXPLORED;
      }
    }
  }
}
'''

# ============================================================
# PHASE 3B: createCitizen() factory
# ============================================================
CREATE_CITIZEN_FUNC = '''\
function createCitizen(col, row, blockKey) {
  return {
    x: col * TILE_SIZE + TILE_SIZE / 2,
    y: row * TILE_SIZE + TILE_SIZE / 2,
    col: col, row: row, blockKey: blockKey,
    state: 'idle', targetCol: -1, targetRow: -1,
    path: null, pathIdx: 0, gatherTimer: 0, gatherRes: null,
    idleTimer: 0, bobPhase: Math.random() * Math.PI * 2, safe: false,
  };
}
'''

# ============================================================
# Now apply all changes bottom-to-top
# ============================================================

# Collect all edit operations as (line_start_0indexed, line_end_0indexed, replacement_text)
edits = []

# --- 3A REPLACEMENTS (line numbers are 1-indexed in the file, convert to 0-indexed) ---

# 1. revealFog (L815-830): replace with one-liner call
#    function revealFog(cx,cy,visRadius,expRadius){...}
edits.append({
    'start': 814,  # 0-indexed for line 815
    'end': 829,    # 0-indexed for line 830 (inclusive)
    'replacement': 'function revealFog(cx,cy,visRadius,expRadius){\n  modifyVision(cx, cy, visRadius, 0, expRadius);\n}\n',
    'desc': '3A: Replace revealFog body with modifyVision call'
})

# 2. revealFogTracked (L841-857): replace with one-liner call
edits.append({
    'start': 840,
    'end': 856,
    'replacement': 'function revealFogTracked(cx,cy,visRadius,expRadius){\n  modifyVisionTracked(cx, cy, visRadius, expRadius);\n}\n',
    'desc': '3A: Replace revealFogTracked body with modifyVisionTracked call'
})

# 3. addCitizenBlockVision (L859-878): replace body with modifyVision call
edits.append({
    'start': 858,
    'end': 877,
    'replacement': '''function addCitizenBlockVision(col,row){
  const s=structures[col+','+row];
  const tier=(s&&s.tier)||1;
  const td=getSettlementTierData(tier);
  modifyVision(col, row, td.visRadius, +1, td.visExp||td.visRadius+2);
}
''',
    'desc': '3A: Replace addCitizenBlockVision body with modifyVision call'
})

# 4. removeCitizenBlockVision (L879-898): replace body with modifyVision call
edits.append({
    'start': 878,
    'end': 897,
    'replacement': '''function removeCitizenBlockVision(col,row){
  const s=structures[col+','+row];
  const tier=(s&&s.tier)||1;
  const td=getSettlementTierData(tier);
  modifyVision(col, row, td.visRadius, -1, td.visExp||td.visRadius+2);
}
''',
    'desc': '3A: Replace removeCitizenBlockVision body with modifyVision call'
})

# 5. addStructureVision (L902-918): replace body
edits.append({
    'start': 899,
    'end': 917,
    'replacement': '''// ─── PERMANENT BUILDING VISION ───
// Called when a building is placed — permanently reveals fog and increments visionCount
function addStructureVision(col,row){
  modifyVision(col, row, STRUCT_VIS_RADIUS, +1, STRUCT_EXP_RADIUS);
}
''',
    'desc': '3A: Replace addStructureVision body with modifyVision call'
})

# 6. removeStructureVision (L920-937): replace body
edits.append({
    'start': 919,
    'end': 936,
    'replacement': '''// Called when a building is destroyed — decrements visionCount and re-fogs uncovered tiles
function removeStructureVision(col,row){
  modifyVision(col, row, STRUCT_VIS_RADIUS, -1, STRUCT_EXP_RADIUS);
}
''',
    'desc': '3A: Replace removeStructureVision body with modifyVision call'
})

# 7. upgradeSettlement inline vision remove (L626-636) — old vision removal loop
edits.append({
    'start': 625,  # line 626
    'end': 635,    # line 636
    'replacement': '  modifyVision(col, row, oldVR, -1, oldER);\n',
    'desc': '3A: Replace upgradeSettlement old vision removal loop with modifyVision call'
})

# 8. upgradeSettlement inline vision add (L638-651) — new vision add loop + markSpawnRingDirty
edits.append({
    'start': 637,  # line 638
    'end': 651,    # line 652 (markSpawnRingDirty is inside modifyVision now)
    'replacement': '''  const newVR=tierDef.visRadius, newER=tierDef.visExp;
  modifyVision(col, row, newVR, +1, newER);
''',
    'desc': '3A: Replace upgradeSettlement new vision add loop with modifyVision call'
})

# --- 3A INSERTION: Insert modifyVision + modifyVisionTracked after initFogMap (after line 814) ---
edits.append({
    'start': 814,  # insert AFTER line 814 (after closing brace of initFogMap)
    'end': 813,    # end < start means "insert after start"
    'replacement': MODIFY_VISION_FUNC + MODIFY_VISION_TRACKED_FUNC,
    'desc': '3A: Insert modifyVision() and modifyVisionTracked() after initFogMap()',
    'insert_after': True
})

# --- 3B REPLACEMENTS: Replace citizen object literals with createCitizen() ---

# Citizen push at L668-674 (upgradeSettlement)
edits.append({
    'start': 667,  # line 668
    'end': 673,    # line 674
    'replacement': '      citizens.push(createCitizen(sc, sr, sk));\n',
    'desc': '3B: Replace citizen literal in upgradeSettlement with createCitizen()'
})

# Citizen push at L1107-1120 (spawnCitizensForBlock)
edits.append({
    'start': 1106,  # line 1107
    'end': 1119,    # line 1120
    'replacement': '    citizens.push(createCitizen(sc, sr, blockKey));\n',
    'desc': '3B: Replace citizen literal in spawnCitizensForBlock with createCitizen()'
})

# Citizen push at L2533-2539 (closeAftermath)
edits.append({
    'start': 2532,  # line 2533
    'end': 2538,    # line 2539
    'replacement': '        citizens.push(createCitizen(sc, sr, k));\n',
    'desc': '3B: Replace citizen literal in closeAftermath with createCitizen()'
})

# --- 3B INSERTION: Insert createCitizen() function ---
# Insert right before spawnCitizensForBlock (line 1097)
edits.append({
    'start': 1096,  # right before line 1097
    'end': 1095,
    'replacement': CREATE_CITIZEN_FUNC + '\n',
    'desc': '3B: Insert createCitizen() factory before spawnCitizensForBlock()',
    'insert_after': True
})

# --- 3C: Merge nearestSettlement + findNearestSettlementTile ---
# nearestSettlement (L949-958): replace with call to unified function
edits.append({
    'start': 948,  # line 949
    'end': 957,    # line 958
    'replacement': '''function nearestSettlement(ec,er){
  const result = findNearestSettlement(ec, er);
  return result ? {c:result.c, r:result.r} : {c:BASE_CX, r:BASE_CY};
}
''',
    'desc': '3C: Replace nearestSettlement with wrapper around findNearestSettlement'
})

# findNearestSettlementTile (L1193-1202): replace with unified version
edits.append({
    'start': 1192,  # line 1193
    'end': 1201,    # line 1202
    'replacement': '''function findNearestSettlementTile(col,row){
  return findNearestSettlement(col, row);
}
''',
    'desc': '3C: Replace findNearestSettlementTile with wrapper around findNearestSettlement'
})

# Insert the unified function right before nearestSettlement (line 949)
UNIFIED_SETTLEMENT_FUNC = '''\
// Unified settlement finder — returns {c, r, dist, key} or null
function findNearestSettlement(ec, er) {
  let best = null, bestDist = Infinity;
  for (const k in structures) {
    if (structures[k].type !== 'CITIZEN_BLOCK') continue;
    const [sc, sr] = k.split(',').map(Number);
    const d = Math.abs(ec - sc) + Math.abs(er - sr);
    if (d < bestDist) { bestDist = d; best = {c: sc, r: sr, dist: d, key: k}; }
  }
  return best;
}
'''

edits.append({
    'start': 948,
    'end': 947,
    'replacement': UNIFIED_SETTLEMENT_FUNC,
    'desc': '3C: Insert findNearestSettlement() before nearestSettlement()',
    'insert_after': True
})


# ============================================================
# Apply edits bottom-to-top (sort by start descending)
# ============================================================

# Separate inserts from replacements for correct ordering
inserts = [e for e in edits if e.get('insert_after')]
replacements = [e for e in edits if not e.get('insert_after')]

# Sort replacements by start descending (bottom-to-top)
replacements.sort(key=lambda e: e['start'], reverse=True)

# Sort inserts by start descending
inserts.sort(key=lambda e: e['start'], reverse=True)

# Apply replacements first (bottom to top)
for edit in replacements:
    s, e = edit['start'], edit['end']
    desc = edit['desc']
    old_count = e - s + 1
    new_lines = edit['replacement'].splitlines(True)
    # Ensure trailing newline
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'
    lines[s:e+1] = new_lines
    diff = len(new_lines) - old_count
    print(f"  {desc}: replaced lines {s+1}-{e+1} ({old_count} lines) with {len(new_lines)} lines (delta: {diff:+d})")

# Now apply inserts (bottom to top) — these insert AFTER the given line
for edit in inserts:
    s = edit['start']
    desc = edit['desc']
    new_lines = edit['replacement'].splitlines(True)
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'
    # Insert after line s (0-indexed), i.e. at position s+1
    lines[s+1:s+1] = new_lines
    print(f"  {desc}: inserted {len(new_lines)} lines after line {s+1}")

new_count = len(lines)
print(f"\nTotal lines: {original_count} → {new_count} (delta: {new_count - original_count:+d})")

with open(FILE, 'w') as f:
    f.writelines(lines)

print(f"Wrote {new_count} lines to {FILE}")
