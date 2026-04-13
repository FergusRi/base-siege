#!/usr/bin/env python3
"""
Step 1 — Natural Biome Map Generation
Replace generateMap() and placeResourceClusters() with biome-based system.
Lines 943–1002 (inclusive) replaced.
edgeDist and centerDist kept as-is.
"""

import sys

FILE = '/home/user/base-siege/index.html'

# The new code that replaces lines 943–1002
NEW_CODE = r'''function generateMap(){
  map=[];tileVariant=[];depositHP=[];
  initFogMap();

  // ─── BIOME NOISE LAYERS ───
  // Layer 1: elevation (base terrain — water vs land)
  // Layer 2: moisture (forest vs dry)
  // Layer 3: rockiness (mountain vs plains)
  // Layer 4: river paths (thin winding waterways)

  // Pass 1: Base terrain + biome assignment
  for(let c=0;c<COLS;c++){map[c]=[];tileVariant[c]=[];depositHP[c]=[];
    for(let r=0;r<ROWS;r++){
      tileVariant[c][r]=(hash(c*7+31,r*13+47)-0.5)*2;
      depositHP[c][r]=0;

      const ed=edgeDist(c,r);
      const cd=centerDist(c,r);

      // Elevation — controls water placement
      const elev=fbm(c,r,4,0.01,2,0.5);

      // River noise — thin winding channels using high-freq noise
      const riverRaw=fbm(c+500,r+500,3,0.008,2.2,0.45);
      const riverWidth=0.015+cd*0.008; // slightly wider toward edges
      const isRiver=Math.abs(riverRaw-0.45)<riverWidth && ed>6;

      // Ocean/lake water
      if(elev<0.26&&ed>10){map[c][r]=T.WATER;continue;}
      // River water
      if(isRiver){map[c][r]=T.WATER;continue;}

      map[c][r]=T.GRASS;
    }
  }

  // Pass 2: Biome-based resource placement
  placeBiomeResources();
}

// ─── BIOME RESOURCE PLACEMENT ───
// Uses noise layers to create distinct biome zones with natural resource clusters
function placeBiomeResources(){
  // Biome noise channels (offset from base to get independent patterns)
  // moisture: high = forest, low = dry plains
  // rockiness: high = mountains, low = flatlands

  for(let c=0;c<COLS;c++) for(let r=0;r<ROWS;r++){
    if(map[c][r]!==T.GRASS) continue;

    const cd=centerDist(c,r);
    const ed=edgeDist(c,r);

    // Biome noise values
    const moisture=fbm(c+1000,r+1000,3,0.006,2,0.5);
    const rockiness=fbm(c+2000,r+2000,3,0.005,2.2,0.5);
    // Detail noise for micro-variation within biomes
    const detail=hash(c*131+7,r*173+13);
    const detail2=hash(c*37+997,r*53+853);

    // ─── BIOME CLASSIFICATION ───
    // Mountains: high rockiness + further from center
    const isMountain=rockiness>0.52 && cd>0.2;
    const isMountainCore=rockiness>0.58 && cd>0.25;
    // Forest: high moisture, not mountain
    const isForest=moisture>0.50 && !isMountain;
    const isDenseForest=moisture>0.58 && !isMountain;
    // Meadow: moderate moisture near center (berry-rich)
    const isMeadow=moisture>0.38 && moisture<0.52 && cd<0.5 && !isMountain;
    // Gold zone: map edges only (dangerous, far from base)
    const isGoldZone=cd>0.75 && isMountainCore;

    // ─── RESOURCE PLACEMENT BY BIOME ───

    // GOLD — rare, only in mountain cores at map edges
    if(isGoldZone && detail<0.04){
      map[c][r]=T.GOLD; continue;
    }

    // MOUNTAINS — stone and ore clusters on rocky terrain
    if(isMountainCore){
      // Dense stone + ore in mountain cores
      if(detail<0.18){
        map[c][r]=T.STONE; continue;
      }
      if(detail<0.28 && detail2>0.4){
        map[c][r]=T.ORE; continue;
      }
      // Scattered trees in mountain passes
      if(detail>0.85 && moisture>0.45){
        map[c][r]=T.TREE; continue;
      }
      continue;
    }
    if(isMountain){
      // Outer mountain slopes — moderate stone, less ore
      if(detail<0.08){
        map[c][r]=T.STONE; continue;
      }
      if(detail<0.12 && cd>0.35){
        map[c][r]=T.ORE; continue;
      }
      // Mountain edge trees
      if(detail>0.82 && moisture>0.48){
        map[c][r]=T.TREE; continue;
      }
      continue;
    }

    // DENSE FOREST — thick tree clusters with occasional berries
    if(isDenseForest){
      if(detail<0.45){
        map[c][r]=T.TREE; continue;
      }
      // Berry bushes in forest clearings
      if(detail>0.88){
        map[c][r]=T.BERRY; continue;
      }
      continue;
    }

    // FOREST — moderate tree coverage
    if(isForest){
      if(detail<0.25){
        map[c][r]=T.TREE; continue;
      }
      // Occasional berries at forest edges
      if(detail>0.92){
        map[c][r]=T.BERRY; continue;
      }
      continue;
    }

    // MEADOW — berry-rich grassland near center (ideal for early farms)
    if(isMeadow){
      // Berry patches in meadows
      if(detail<0.12){
        map[c][r]=T.BERRY; continue;
      }
      // Light tree scattering
      if(detail>0.90){
        map[c][r]=T.TREE; continue;
      }
      continue;
    }

    // PLAINS (default) — sparse resources, mostly open grass
    // Light tree scattering
    if(detail<0.03+cd*0.02){
      map[c][r]=T.TREE; continue;
    }
    // Very rare berries in open plains
    if(detail>0.96 && cd<0.4){
      map[c][r]=T.BERRY; continue;
    }
    // Occasional stone outcrops in outer plains
    if(detail2<0.015 && cd>0.45){
      map[c][r]=T.STONE; continue;
    }
  }

  // Initialize depositHP for all resource tiles
  for(let c=0;c<COLS;c++) for(let r=0;r<ROWS;r++){
    const dep=DEPOSITS[map[c][r]];
    if(dep) depositHP[c][r]=dep.maxHP;
  }
}
'''

# Read file
with open(FILE, 'r') as f:
    lines = f.readlines()

total = len(lines)
print(f"File has {total} lines")

# Verify anchor lines (1-indexed in editor, 0-indexed in list)
# Line 943 should start with "function generateMap(){"
# Line 1002 should end with "}" closing placeResourceClusters
line_943 = lines[942].strip()
line_1002 = lines[1001].strip()
print(f"Line 943: '{line_943}'")
print(f"Line 1002: '{line_1002}'")

assert line_943 == 'function generateMap(){', f"Line 943 mismatch: {line_943}"
assert line_1002 == '}', f"Line 1002 mismatch: {line_1002}"

# Also verify line 942 is blank or comment (before generateMap)
line_942 = lines[941].strip()
print(f"Line 942: '{line_942}'")

# Verify line 1003 starts the placeHQ comment
line_1003 = lines[1002].strip()
print(f"Line 1003: '{line_1003}'")
assert 'Place first Settlement' in line_1003 or 'placeHQ' in line_1003.lower() or line_1003.startswith('//'), \
    f"Line 1003 doesn't look like placeHQ comment: {line_1003}"

# Replace lines 943-1002 (indices 942-1001)
new_lines = lines[:942] + [NEW_CODE + '\n'] + lines[1002:]
print(f"Old line count: {total}")
print(f"New line count: {len(new_lines)}")

with open(FILE, 'w') as f:
    f.writelines(new_lines)

print("✅ Biome map generation patched successfully!")

# Verify key markers still exist
with open(FILE, 'r') as f:
    content = f.read()

checks = [
    ('function generateMap()', 'generateMap'),
    ('function placeBiomeResources()', 'placeBiomeResources'),
    ('function placeHQ(', 'placeHQ'),
    ('function edgeDist(', 'edgeDist'),
    ('function centerDist(', 'centerDist'),
    ('kill-hud', 'kill-hud HTML'),
    ('function renderTile(', 'renderTile'),
    ('T.GOLD', 'gold tile type'),
    ('initFogMap()', 'fog init'),
]

all_ok = True
for marker, name in checks:
    if marker not in content:
        print(f"❌ MISSING: {name} ({marker})")
        all_ok = False
    else:
        print(f"  ✓ {name}")

if all_ok:
    print("\n✅ All integrity checks passed!")
else:
    print("\n❌ Some checks FAILED — review needed!")
    sys.exit(1)
