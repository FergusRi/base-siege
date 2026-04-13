#!/usr/bin/env python3
"""
Phase 4C: Minimap Selective Redraw
- Add fogChangeVersion counter that increments when fog tile state actually changes
- Add lastMmFogVersion to track when minimap last rebuilt
- Replace frame-counter-based rebuild with version-based (only rebuild when fog changed)
- Throttle: at most once per 10 frames AND only if fog version changed
Bottom-to-top processing.
"""

import sys

with open('index.html', 'r') as f:
    lines = f.readlines()

print(f"Starting: {len(lines)} lines")

# Replacements: (1-indexed line, old_stripped, new_stripped)
R = []

# ── Add fogChangeVersion after fogFrameCounter ──
# Line 874: let fogFrameCounter=0;
R.append((874,
    'let fogFrameCounter=0;',
    'let fogFrameCounter=0;\nlet fogChangeVersion=0;'))

# ── Increment in modifyVision fog state changes ──
# Only increment when fog VALUE actually changes (check before setting)
# Line 799: fogMap[nc][nr] = FOG_VISIBLE; (delta > 0 branch)
# This is inside: if (distSq <= visRadius * visRadius) { if (delta > 0) {
# fogMap could already be FOG_VISIBLE, so only count real changes
R.append((799,
    '          fogMap[nc][nr] = FOG_VISIBLE;',
    '          if(fogMap[nc][nr]!==FOG_VISIBLE){fogMap[nc][nr]=FOG_VISIBLE;fogChangeVersion++;}'))

# Line 803: fogMap[nc][nr] = FOG_EXPLORED; (delta < 0, visionCount dropped to 0)
R.append((803,
    '            fogMap[nc][nr] = FOG_EXPLORED;',
    '            fogMap[nc][nr]=FOG_EXPLORED;fogChangeVersion++;'))

# Line 806: fogMap[nc][nr] = FOG_VISIBLE; (delta === 0 branch, non-tracked reveal)
R.append((806,
    '          fogMap[nc][nr] = FOG_VISIBLE;',
    '          if(fogMap[nc][nr]!==FOG_VISIBLE){fogMap[nc][nr]=FOG_VISIBLE;fogChangeVersion++;}'))

# Line 809: fogMap[nc][nr] = FOG_EXPLORED; (explored ring)
# Only if it was FOG_UNEXPLORED (the if condition already checks fogMap < FOG_EXPLORED)
R.append((809,
    '        fogMap[nc][nr] = FOG_EXPLORED;',
    '        fogMap[nc][nr]=FOG_EXPLORED;fogChangeVersion++;'))

# ── Increment in updateHeroFog ──
# Line 826: fogMap[nc][nr] = FOG_VISIBLE; (hero dynamic vision)
# The line before already checks: if (fogMap[nc][nr] !== FOG_VISIBLE)
R.append((826,
    '        fogMap[nc][nr] = FOG_VISIBLE;',
    '        fogMap[nc][nr]=FOG_VISIBLE;fogChangeVersion++;'))

# Line 828: fogMap[nc][nr] = FOG_EXPLORED;
R.append((828,
    '        fogMap[nc][nr] = FOG_EXPLORED;',
    '        fogMap[nc][nr]=FOG_EXPLORED;fogChangeVersion++;'))

# ── Increment in decayFogVisible ──
# Line 842: if(fogMap[c][r]===FOG_VISIBLE&&visionCount[c][r]===0) fogMap[c][r]=FOG_EXPLORED;
R.append((842,
    '    if(fogMap[c][r]===FOG_VISIBLE&&visionCount[c][r]===0) fogMap[c][r]=FOG_EXPLORED;',
    '    if(fogMap[c][r]===FOG_VISIBLE&&visionCount[c][r]===0){fogMap[c][r]=FOG_EXPLORED;fogChangeVersion++;}'))

# ── Add lastMmFogVersion near mmTerrainDirty ──
# Line 5175: let mmTerrainDirty=true;
R.append((5175,
    'let mmTerrainDirty=true;',
    'let mmTerrainDirty=true;\nlet lastMmFogVersion=-1;'))

# ── Replace game loop trigger ──
# Line 5501: if(hqPlaced||game.phase==='PLACE_HQ'){refreshFogVision();if(fogFrameCounter%10===0)mmTerrainDirty=true;}
# New: only dirty minimap when fog has actually changed, and still throttle to every 10 frames
R.append((5501,
    "  if(hqPlaced||game.phase==='PLACE_HQ'){refreshFogVision();if(fogFrameCounter%10===0)mmTerrainDirty=true;}",
    "  if(hqPlaced||game.phase==='PLACE_HQ'){refreshFogVision();if(fogFrameCounter%10===0&&fogChangeVersion!==lastMmFogVersion){mmTerrainDirty=true;lastMmFogVersion=fogChangeVersion;}}"))


# ═══════════════════════════════════════════════════════════
# APPLY — bottom-to-top
# ═══════════════════════════════════════════════════════════
R.sort(key=lambda x: x[0], reverse=True)

applied = 0
skipped = 0
for (line_num, old, new) in R:
    idx = line_num - 1
    actual = lines[idx].rstrip('\n')
    if actual == old:
        new_lines = [l + '\n' for l in new.split('\n')]
        lines[idx:idx+1] = new_lines
        applied += 1
    else:
        print(f"MISMATCH line {line_num}:")
        print(f"  Expected: {repr(old)}")
        print(f"  Actual:   {repr(actual)}")
        skipped += 1

print(f"\nApplied: {applied} replacements")
print(f"Skipped: {skipped} mismatches")

if skipped > 0:
    print("\n*** ABORTING — mismatches found ***")
    sys.exit(1)

with open('index.html', 'w') as f:
    f.writelines(lines)

print(f"Final: {len(lines)} lines (delta: {len(lines) - 5688})")
