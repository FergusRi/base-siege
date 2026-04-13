#!/usr/bin/env python3
"""
Phase 3 v2: All edits as a single unified bottom-to-top pass.
Every operation is either:
  - REPLACE(start, end, new_text)  — replace lines[start:end+1]
  - INSERT(after, new_text)        — insert new_text after lines[after]

All line numbers are 1-indexed (matching the file). We convert to 0-indexed internally.
Operations are sorted by position descending so earlier positions stay valid.
"""

FILE = 'index.html'

with open(FILE, 'r') as f:
    lines = f.readlines()

original_count = len(lines)
print(f"Read {original_count} lines from {FILE}")

# ============================================================
# NEW FUNCTION BODIES
# ============================================================

MODIFY_VISION = '''\
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

MODIFY_VISION_TRACKED = '''\
function modifyVisionTracked(cx, cy, visRadius, expRadius) {
  // Hero vision — tracks newly-visible tiles for decay
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

CREATE_CITIZEN = '''\
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

FIND_NEAREST_SETTLEMENT = '''\
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

# ============================================================
# ALL OPERATIONS — line numbers are 1-indexed
# Each op: ('replace', start_line, end_line, new_text, desc)
#       or ('insert', after_line, new_text, desc)
# ============================================================
ops = []

# --- 3A: Vision replacements ---

# 1. revealFog (L815-830) → thin wrapper
ops.append(('replace', 815, 830,
    'function revealFog(cx,cy,visRadius,expRadius){\n  modifyVision(cx, cy, visRadius, 0, expRadius);\n}\n',
    'revealFog → modifyVision wrapper'))

# 2. revealFogTracked (L841-857) → thin wrapper
ops.append(('replace', 841, 857,
    'function revealFogTracked(cx,cy,visRadius,expRadius){\n  modifyVisionTracked(cx, cy, visRadius, expRadius);\n}\n',
    'revealFogTracked → modifyVisionTracked wrapper'))

# 3. addCitizenBlockVision (L859-878) → modifyVision call
ops.append(('replace', 859, 878,
    'function addCitizenBlockVision(col,row){\n  const s=structures[col+\',\'+row];\n  const tier=(s&&s.tier)||1;\n  const td=getSettlementTierData(tier);\n  modifyVision(col, row, td.visRadius, +1, td.visExp||td.visRadius+2);\n}\n',
    'addCitizenBlockVision → modifyVision'))

# 4. removeCitizenBlockVision (L879-898) → modifyVision call
ops.append(('replace', 879, 898,
    'function removeCitizenBlockVision(col,row){\n  const s=structures[col+\',\'+row];\n  const tier=(s&&s.tier)||1;\n  const td=getSettlementTierData(tier);\n  modifyVision(col, row, td.visRadius, -1, td.visExp||td.visRadius+2);\n}\n',
    'removeCitizenBlockVision → modifyVision'))

# 5. addStructureVision (L900-918) → one-liner (includes comment lines)
ops.append(('replace', 900, 918,
    '// ─── PERMANENT BUILDING VISION ───\n// Called when a building is placed — permanently reveals fog and increments visionCount\nfunction addStructureVision(col,row){\n  modifyVision(col, row, STRUCT_VIS_RADIUS, +1, STRUCT_EXP_RADIUS);\n}\n',
    'addStructureVision → modifyVision'))

# 6. removeStructureVision (L919-937) → one-liner (includes comment line)
ops.append(('replace', 919, 937,
    '// Called when a building is destroyed — decrements visionCount and re-fogs uncovered tiles\nfunction removeStructureVision(col,row){\n  modifyVision(col, row, STRUCT_VIS_RADIUS, -1, STRUCT_EXP_RADIUS);\n}\n',
    'removeStructureVision → modifyVision'))

# 7. upgradeSettlement old vision removal loop (L626-636)
ops.append(('replace', 626, 636,
    '  modifyVision(col, row, oldVR, -1, oldER);\n',
    'upgradeSettlement old vision loop → modifyVision'))

# 8. upgradeSettlement new vision add loop + markSpawnRingDirty (L638-652)
ops.append(('replace', 638, 652,
    '  const newVR=tierDef.visRadius, newER=tierDef.visExp;\n  modifyVision(col, row, newVR, +1, newER);\n',
    'upgradeSettlement new vision loop → modifyVision'))

# --- 3A: Insert modifyVision + modifyVisionTracked after initFogMap closing brace (L814) ---
ops.append(('insert', 814, MODIFY_VISION + MODIFY_VISION_TRACKED,
    'Insert modifyVision() + modifyVisionTracked()'))

# --- 3B: Citizen factory replacements ---

# Citizen literal at L668-674 (upgradeSettlement)
ops.append(('replace', 668, 674,
    '      citizens.push(createCitizen(sc, sr, sk));\n',
    'upgradeSettlement citizen literal → createCitizen'))

# Citizen literal at L1107-1120 (spawnCitizensForBlock)
ops.append(('replace', 1107, 1120,
    '    citizens.push(createCitizen(sc, sr, blockKey));\n',
    'spawnCitizensForBlock citizen literal → createCitizen'))

# Citizen literal at L2533-2539 (closeAftermath)
ops.append(('replace', 2533, 2539,
    '        citizens.push(createCitizen(sc, sr, k));\n',
    'closeAftermath citizen literal → createCitizen'))

# --- 3B: Insert createCitizen() before spawnCitizensForBlock ---
# spawnCitizensForBlock starts at L1097, insert after L1096 (the section header line)
# Actually let's insert after L1095 (the ═══ line) so it's between header and first function
ops.append(('insert', 1096, CREATE_CITIZEN,
    'Insert createCitizen() factory'))

# --- 3C: Settlement finder ---

# Replace nearestSettlement (L949-958) with wrapper
ops.append(('replace', 949, 958,
    'function nearestSettlement(ec,er){\n  const result = findNearestSettlement(ec, er);\n  return result ? {c:result.c, r:result.r} : {c:BASE_CX, r:BASE_CY};\n}\n',
    'nearestSettlement → findNearestSettlement wrapper'))

# Replace findNearestSettlementTile (L1193-1202) with wrapper
ops.append(('replace', 1193, 1202,
    '// Find nearest CITIZEN_BLOCK tile to a given position\nfunction findNearestSettlementTile(col,row){\n  return findNearestSettlement(col, row);\n}\n',
    'findNearestSettlementTile → findNearestSettlement wrapper'))

# Insert findNearestSettlement before nearestSettlement (after L948 = the comment line)
ops.append(('insert', 948, FIND_NEAREST_SETTLEMENT,
    'Insert findNearestSettlement() unified function'))

# ============================================================
# Sort ALL ops by position descending, then apply
# For 'replace': sort key = end line (highest affected line)
# For 'insert': sort key = after line
# We need inserts at a given position to come BEFORE replacements
# at that same position (so the insert happens first in bottom-to-top)
# ============================================================

def sort_key(op):
    if op[0] == 'replace':
        return (op[2], 1)  # end line, then 1 (replace after insert at same spot)
    else:  # insert
        return (op[1], 0)  # after line, then 0 (insert before replace)

ops.sort(key=sort_key, reverse=True)

print(f"\nApplying {len(ops)} operations bottom-to-top:\n")

for op in ops:
    if op[0] == 'replace':
        _, start, end, new_text, desc = op
        s = start - 1  # 0-indexed
        e = end - 1
        old_count = e - s + 1
        new_lines = new_text.splitlines(True)
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] += '\n'
        lines[s:e+1] = new_lines
        delta = len(new_lines) - old_count
        print(f"  REPLACE L{start}-L{end} ({old_count}→{len(new_lines)}, Δ{delta:+d}): {desc}")
    else:  # insert
        _, after, new_text, desc = op
        a = after - 1  # 0-indexed: insert after this line
        new_lines = new_text.splitlines(True)
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] += '\n'
        lines[a+1:a+1] = new_lines
        print(f"  INSERT after L{after} (+{len(new_lines)} lines): {desc}")

new_count = len(lines)
print(f"\nTotal: {original_count} → {new_count} (Δ{new_count - original_count:+d})")

with open(FILE, 'w') as f:
    f.writelines(lines)

print(f"Wrote {new_count} lines to {FILE}")
