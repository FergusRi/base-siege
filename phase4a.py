#!/usr/bin/env python3
"""
Phase 4A: Squared Distance Elimination
Replace comparison-only Math.sqrt with squared distance checks.
Keep Math.sqrt where real distance is needed (movement normalization).
Bottom-to-top line processing to preserve line numbers.
"""

import sys

with open('index.html', 'r') as f:
    lines = f.readlines()

original_count = len(lines)
print(f"Starting: {original_count} lines")

# All replacements: (1-indexed line, exact old content, new content)
R = []

# ═══════════════════════════════════════════════════════════
# §4 FOG / VISION — modifyVision (line 795)
# ═══════════════════════════════════════════════════════════
R.append((795,
    '      const dist = Math.sqrt(dc * dc + dr * dr);',
    '      const distSq = dc * dc + dr * dr;'))
R.append((796,
    '      if (dist <= visRadius) {',
    '      if (distSq <= visRadius * visRadius) {'))
# The else if is on line 808, not 805
R.append((808,
    '      } else if (dist <= er && fogMap[nc][nr] < FOG_EXPLORED) {',
    '      } else if (distSq <= er * er && fogMap[nc][nr] < FOG_EXPLORED) {'))

# §4 FOG — updateHeroFog (line 823)
R.append((823,
    '      const dist = Math.sqrt(dc * dc + dr * dr);',
    '      const distSq = dc * dc + dr * dr;'))
R.append((824,
    '      if (dist <= visRadius) {',
    '      if (distSq <= visRadius * visRadius) {'))
R.append((827,
    '      } else if (dist <= er && fogMap[nc][nr] < FOG_EXPLORED) {',
    '      } else if (distSq <= er * er && fogMap[nc][nr] < FOG_EXPLORED) {'))

# §3 MAP GEN — placeHQ base clearing (line 983)
R.append((983,
    '      const dist=Math.sqrt(dc*dc+dr*dr);',
    '      const distSq=dc*dc+dr*dr;'))
R.append((984,
    '      if(dist<=BASE_CLEAR_RADIUS&&map[nc][nr]===T.WATER){',
    '      if(distSq<=BASE_CLEAR_RADIUS*BASE_CLEAR_RADIUS&&map[nc][nr]===T.WATER){'))
R.append((988,
    '      if(dist<=3&&nc!==col&&nr!==row){',
    '      if(distSq<=9&&nc!==col&&nr!==row){'))

# §4 FOG — spawn ring: nearestVisDist (line 1739)
R.append((1731,
    '      let nearestVisDist=Infinity;',
    '      let nearestVisDistSq=Infinity;'))
R.append((1739,
    '            const d=Math.sqrt(dc*dc+dr*dr);',
    '            const dSq=dc*dc+dr*dr;'))
R.append((1740,
    '            if(d<nearestVisDist) nearestVisDist=d;',
    '            if(dSq<nearestVisDistSq) nearestVisDistSq=dSq;'))
R.append((1746,
    '      if(nearestVisDist<SPAWN_RING_BUFFER) continue;',
    '      if(nearestVisDistSq<SPAWN_RING_BUFFER*SPAWN_RING_BUFFER) continue;'))
R.append((1747,
    '      if(nearestVisDist>SPAWN_RING_BUFFER+SPAWN_RING_DEPTH) continue;',
    '      if(nearestVisDistSq>(SPAWN_RING_BUFFER+SPAWN_RING_DEPTH)*(SPAWN_RING_BUFFER+SPAWN_RING_DEPTH)) continue;'))

# §4 FOG — spawn ring: dBase (line 1750)
R.append((1750,
    "      const dBase=Math.sqrt((c-BASE_CX)**2+(r-BASE_CY)**2);",
    "      const dBaseSq=(c-BASE_CX)**2+(r-BASE_CY)**2;"))
R.append((1751,
    '      if(dBase<SPAWN_MIN_DIST_TO_BASE) continue;',
    '      if(dBaseSq<SPAWN_MIN_DIST_TO_BASE*SPAWN_MIN_DIST_TO_BASE) continue;'))

# §8 ENEMY AI — findNearestStructure (line 2529)
# Returns {dist: dSq} — consumers must compare squared too
R.append((2529,
    "      const dx=c-ec, dy=r-er, d=Math.sqrt(dx*dx+dy*dy);",
    "      const dx=c-ec, dy=r-er, dSq=dx*dx+dy*dy;"))
R.append((2530,
    "      if(d<nearDist){nearDist=d;nearest={key,c,r,dist:d,struct:s};}",
    "      if(dSq<nearDist){nearDist=dSq;nearest={key,c,r,dist:dSq,struct:s};}"))
# Consumer: siege ram (line 2756) — 1.5 → 1.5*1.5=2.25
R.append((2756,
    "      if(nearStruct&&nearStruct.dist<=1.5){",
    "      if(nearStruct&&nearStruct.dist<=2.25){"))
# Consumer: brute (line 2778) — 1.5 → 2.25
R.append((2778,
    "      if(nearWall&&nearWall.dist<=1.5&&(nearWall.struct.type==='WALL'||nearWall.struct.type==='GATE'||nearWall.struct.type==='CITIZEN_BLOCK')){",
    "      if(nearWall&&nearWall.dist<=2.25&&(nearWall.struct.type==='WALL'||nearWall.struct.type==='GATE'||nearWall.struct.type==='CITIZEN_BLOCK')){"))
# Consumer: path blocked wall smash (line 2864) — 2.5 → 2.5*2.5=6.25
R.append((2864,
    "          if(nearWall&&nearWall.dist<=2.5){",
    "          if(nearWall&&nearWall.dist<=6.25){"))

# §9 COMBAT — heroAutoAttack: hero melee range check (line 2600)
R.append((2600,
    "    const dx=e.x-hero.x, dy=e.y-hero.y, d=Math.sqrt(dx*dx+dy*dy);",
    "    const dx=e.x-hero.x, dy=e.y-hero.y, dSq=dx*dx+dy*dy;"))
R.append((2601,
    "    if(d<=HERO_ATK_RANGE&&d<nearDist){nearDist=d;nearest=e;}",
    "    if(dSq<=HERO_ATK_RANGE*HERO_ATK_RANGE&&dSq<nearDist){nearDist=dSq;nearest=e;}"))

# §9 COMBAT — warchief buff radius (line 2667)
R.append((2667,
    "      if(Math.sqrt(dx*dx+dy*dy)<=def.buffRadius*TILE_SIZE){",
    "      if(dx*dx+dy*dy<=(def.buffRadius*TILE_SIZE)*(def.buffRadius*TILE_SIZE)){"))

# §9 COMBAT — enemy ranged: hero target (line 2683)
R.append((2683,
    "    const hdx=hero.x-e.x, hdy=hero.y-e.y, hd=Math.sqrt(hdx*hdx+hdy*hdy);",
    "    const hdx=hero.x-e.x, hdy=hero.y-e.y, hdSq=hdx*hdx+hdy*hdy;"))
R.append((2684,
    "    if(hd<=rangePx&&hd<targetDist){targetDist=hd;targetX=hero.x;targetY=hero.y;target='hero';}",
    "    if(hdSq<=rangePx*rangePx&&hdSq<targetDist){targetDist=hdSq;targetX=hero.x;targetY=hero.y;target='hero';}"))

# §9 COMBAT — enemy ranged: unit target (line 2690)
R.append((2690,
    "    const dx=ux-e.x, dy=uy-e.y, d=Math.sqrt(dx*dx+dy*dy);",
    "    const dx=ux-e.x, dy=uy-e.y, dSq=dx*dx+dy*dy;"))
R.append((2691,
    "    if(d<=rangePx&&d<targetDist){targetDist=d;targetX=ux;targetY=uy;target=u;}",
    "    if(dSq<=rangePx*rangePx&&dSq<targetDist){targetDist=dSq;targetX=ux;targetY=uy;target=u;}"))

# §9 COMBAT — enemy melee hero (line 2794)
R.append((2794,
    "      const heroDist=Math.sqrt(hdx*hdx+hdy*hdy);",
    "      const heroDistSq=hdx*hdx+hdy*hdy;"))
R.append((2795,
    "      if(heroDist<TILE_SIZE*1.3&&e.attackCooldown<=0){",
    "      if(heroDistSq<(TILE_SIZE*1.3)*(TILE_SIZE*1.3)&&e.attackCooldown<=0){"))

# §9 COMBAT — enemy kill citizen (line 2821)
R.append((2821,
    "        const citDist=Math.sqrt(cdx*cdx+cdy*cdy);",
    "        const citDistSq=cdx*cdx+cdy*cdy;"))
R.append((2822,
    "        if(citDist<TILE_SIZE*1.5){",
    "        if(citDistSq<(TILE_SIZE*1.5)*(TILE_SIZE*1.5)){"))

# §10 TOWERS — tower targeting (line 2960)
R.append((2960,
    "      const dx=e.x-tx, dy=e.y-ty, d=Math.sqrt(dx*dx+dy*dy);",
    "      const dx=e.x-tx, dy=e.y-ty, dSq=dx*dx+dy*dy;"))
R.append((2961,
    "      if(d<range&&d<nearDist){nearDist=d;nearest=e;}",
    "      if(dSq<range*range&&dSq<nearDist){nearDist=dSq;nearest=e;}"))

# §10 TOWERS — projectile hit (line 2985)
R.append((2985,
    "    const dist=Math.sqrt(dx*dx+dy*dy);",
    "    const distSq=dx*dx+dy*dy;"))
R.append((2986,
    "    if(dist<6){",
    "    if(distSq<36){"))

# §10 TOWERS — AOE damage radius (line 3013)
R.append((3013,
    "          const adist=Math.sqrt(adx*adx+ady*ady);",
    "          const adistSq=adx*adx+ady*ady;"))
R.append((3014,
    "          if(adist<=aoePx){",
    "          if(adistSq<=aoePx*aoePx){"))

# §11 UNIT AI — cavalry enemy search (line 3108)
R.append((3108,
    "        const edx=e.x-ux, edy=e.y-uy, ed=Math.sqrt(edx*edx+edy*edy);",
    "        const edx=e.x-ux, edy=e.y-uy, edSq=edx*edx+edy*edy;"))
R.append((3109,
    "        if(ed<=rangePx&&ed<nearDist){nearDist=ed;nearest=e;}",
    "        if(edSq<=rangePx*rangePx&&edSq<nearDist){nearDist=edSq;nearest=e;}"))

# §11 UNIT AI — thundercharge stun 1 (line 3130)
R.append((3130,
    "              if(Math.sqrt(sdx*sdx+sdy*sdy)<=2*TILE_SIZE){",
    "              if(sdx*sdx+sdy*sdy<=(2*TILE_SIZE)*(2*TILE_SIZE)){"))

# §11 UNIT AI — unit attack enemy search (line 3175)
R.append((3175,
    "      const dx=e.x-ux, dy=e.y-uy, d=Math.sqrt(dx*dx+dy*dy);",
    "      const dx=e.x-ux, dy=e.y-uy, dSq=dx*dx+dy*dy;"))
R.append((3176,
    "      if(d<=rangePx&&d<nearDist){nearDist=d;nearest=e;}",
    "      if(dSq<=rangePx*rangePx&&dSq<nearDist){nearDist=dSq;nearest=e;}"))

# §11 UNIT AI — spear ZoC (line 3239)
R.append((3239,
    "        if(Math.sqrt(edx*edx+edy*edy)<=zocPx){",
    "        if(edx*edx+edy*edy<=zocPx*zocPx){"))

# §11 UNIT AI — thundercharge stun 2 (line 3269)
R.append((3269,
    "            if(Math.sqrt(sdx*sdx+sdy*sdy)<=2*TILE_SIZE) se.slowTimer=Math.max(se.slowTimer,0.8);",
    "            if(sdx*sdx+sdy*sdy<=(2*TILE_SIZE)*(2*TILE_SIZE)) se.slowTimer=Math.max(se.slowTimer,0.8);"))

# §11 UNIT AI — spear passive slow (line 3308)
R.append((3308,
    "      if(Math.sqrt(dx*dx+dy*dy)<=zocPx){",
    "      if(dx*dx+dy*dy<=zocPx*zocPx){"))

# §12 MORALE — nearby enemies drain (line 3619)
R.append((3619,
    "      if(Math.sqrt(dx*dx+dy*dy)<=2*TILE_SIZE)nearbyEnemies++;",
    "      if(dx*dx+dy*dy<=(2*TILE_SIZE)*(2*TILE_SIZE))nearbyEnemies++;"))

# §12 MORALE — hero aura recovery (line 3629)
R.append((3629,
    "      if(Math.sqrt(hdx*hdx+hdy*hdy)<=HERO_MORALE_AURA*TILE_SIZE){",
    "      if(hdx*hdx+hdy*hdy<=(HERO_MORALE_AURA*TILE_SIZE)*(HERO_MORALE_AURA*TILE_SIZE)){"))

# §12 MORALE — enemy kill morale boost (line 3675)
R.append((3675,
    "    if(Math.sqrt(dx*dx+dy*dy)<=4*TILE_SIZE){",
    "    if(dx*dx+dy*dy<=(4*TILE_SIZE)*(4*TILE_SIZE)){"))


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
        lines[idx] = new + '\n'
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

final_count = len(lines)
print(f"\nFinal: {final_count} lines (same — replacements only)")

# Count remaining Math.sqrt
remaining = sum(1 for l in lines if 'Math.sqrt' in l)
print(f"Remaining Math.sqrt calls: {remaining}")
print("(These are movement normalization sites that need real distance)")
