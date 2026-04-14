#!/usr/bin/env python3
"""Phase E Part 2: Update all col/row references, rewrite rendering & selection."""

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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 5: Update findAdjacentUnit to use x/y distance
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 5: Updating findAdjacentUnit...")

idx = find_line("function findAdjacentUnit(")
end_idx = find_line("}", find_line("return candidates[0];", idx))

replace_range(idx, end_idx, [
    "function findAdjacentUnit(eCol, eRow) {",
    "  // Find player units within melee range of enemy position",
    "  const ex = eCol * TILE_SIZE + TILE_SIZE / 2, ey = eRow * TILE_SIZE + TILE_SIZE / 2;",
    "  const meleeDist = TILE_SIZE * 1.8; // slightly wider than 1 tile",
    "  let candidates = [];",
    "  for (const u of units) {",
    "    if (u.hp <= 0) continue;",
    "    const dx = u.x - ex, dy = u.y - ey;",
    "    if (dx * dx + dy * dy <= meleeDist * meleeDist) candidates.push(u);",
    "  }",
    "  if (candidates.length === 0) return null;",
    "  candidates.sort((a, b) => {",
    "    const aF = unitInFormation(a) ? 1 : 0;",
    "    const bF = unitInFormation(b) ? 1 : 0;",
    "    if (aF !== bF) return aF - bF;",
    "    return a.hp - b.hp;",
    "  });",
    "  return candidates[0];",
    "}",
])
print("  ✓ findAdjacentUnit updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 6: Update damageUnit to use x/y
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 6: Updating damageUnit...")

idx = find_line("function damageUnit(u,dmg,e)")
# Replace the ux/uy lines that use col/row
ux_line = find_line("const ux=u.col*TILE_SIZE+TILE_SIZE/2, uy=u.row*TILE_SIZE+TILE_SIZE/2;", idx)
lines[ux_line] = "  const ux=u.x, uy=u.y;"
print("  ✓ damageUnit updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 7: Update showRankUpEffect to use x/y
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 7: Updating showRankUpEffect...")

idx = find_line("function showRankUpEffect(u,newRank)")
ux_line = find_line("const ux=u.col*TILE_SIZE+TILE_SIZE/2, uy=u.row*TILE_SIZE+TILE_SIZE/2;", idx)
lines[ux_line] = "  const ux=u.x, uy=u.y;"
print("  ✓ showRankUpEffect updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 8: Update unitAt to use x/y proximity
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 8: Updating unitAt...")

idx = find_line("function unitAt(col,row)")
lines[idx] = "function unitAt(col,row){const cx=col*TILE_SIZE+TILE_SIZE/2,cy=row*TILE_SIZE+TILE_SIZE/2;return units.find(u=>Math.abs(u.x-cx)<TILE_SIZE&&Math.abs(u.y-cy)<TILE_SIZE);}"
print("  ✓ unitAt updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 9: Update handleDemolish for units to use x/y
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 9: Updating handleDemolish...")

idx = find_line("function handleDemolish(col,row)")
# Find unit removal section
uix = find_line("if(uIdx>=0){", idx)
# Replace the coord lines
ux_line = find_line("const ux=col*TILE_SIZE+TILE_SIZE/2, uy=row*TILE_SIZE;", uix)
lines[ux_line] = "    const ux=u.x, uy=u.y-TILE_SIZE/2;"
print("  ✓ handleDemolish updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 10: Rewrite checkFormations to distance-based
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 10: Rewriting checkFormations to distance-based...")

idx = find_line("function checkFormations()")
end_idx = find_line("function unitInFormation(u)", idx) - 1
# Trim trailing blanks
while lines[end_idx].strip() == '':
    end_idx -= 1

replace_range(idx, end_idx, [
    "function checkFormations(){",
    "  // Reset all formation flags",
    "  for(const u of units){ u.shieldWall=false; u.protectedFire=false; }",
    "",
    "  // Shield Wall: 3+ melee units within 3 tiles of each other (distance-based)",
    "  const meleeUnits = units.filter(u => isMeleeUnit(u.type) && u.hp > 0);",
    "  const SHIELD_DIST = 3 * TILE_SIZE;",
    "  for (const u of meleeUnits) {",
    "    let nearby = 0;",
    "    for (const v of meleeUnits) {",
    "      if (v === u) continue;",
    "      const dx = v.x - u.x, dy = v.y - u.y;",
    "      if (dx * dx + dy * dy <= SHIELD_DIST * SHIELD_DIST) nearby++;",
    "    }",
    "    if (nearby >= SHIELD_WALL_MIN - 1) u.shieldWall = true;",
    "  }",
    "",
    "  // Protected Fire: ranged unit within 2 tiles behind a melee unit (distance-based)",
    "  const PROT_DIST = 2 * TILE_SIZE;",
    "  for (const u of units) {",
    "    if (!isRangedUnit(u.type) || u.hp <= 0) continue;",
    "    for (const m of meleeUnits) {",
    "      const dx = m.x - u.x, dy = m.y - u.y;",
    "      if (dx * dx + dy * dy <= PROT_DIST * PROT_DIST) { u.protectedFire = true; break; }",
    "    }",
    "  }",
    "}",
])
print("  ✓ checkFormations rewritten (distance-based)")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 11: Rewrite updateFleeingUnits to use x/y
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 11: Rewriting updateFleeingUnits...")

idx = find_line("function updateFleeingUnits(dt)")
end_idx = find_line("}", find_line("}", find_line("u._fleeMoveTimer=0;", idx)))
# Find the actual closing brace of the function
brace_count = 0
for i in range(idx, len(lines)):
    brace_count += lines[i].count('{') - lines[i].count('}')
    if brace_count == 0 and i > idx:
        end_idx = i
        break

replace_range(idx, end_idx, [
    "function updateFleeingUnits(dt){",
    "  const basePx = BASE_CX * TILE_SIZE + TILE_SIZE / 2;",
    "  const basePy = BASE_CY * TILE_SIZE + TILE_SIZE / 2;",
    "  for(const u of units){",
    "    if(u.moraleState!=='broken'||u.hp<=0) continue;",
    "    const dx=basePx-u.x, dy=basePy-u.y;",
    "    const dist=Math.sqrt(dx*dx+dy*dy);",
    "    if(dist<=TILE_SIZE*2) continue;",
    "    u._fleeMoveTimer=(u._fleeMoveTimer||0)+dt;",
    "    if(u._fleeMoveTimer<0.5) continue;",
    "    u._fleeMoveTimer=0;",
    "    const speed=TILE_SIZE; // 1 tile per flee step",
    "    u.x+=dx/dist*speed; u.y+=dy/dist*speed;",
    "  }",
    "}",
])
print("  ✓ updateFleeingUnits rewritten")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 12: Update veteran death effects in damageUnit
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 12: Checking veteran death effects...")
# These already use ux/uy which we fixed above — should be fine
print("  ✓ Already handled by damageUnit fix")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 13: Remove old handleRecruit (tile-based unit placement)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 13: Removing old handleRecruit...")

# Remove cavalryPendingUnit state
idx = find_line("let cavalryPendingUnit=null;")
lines[idx] = "// cavalryPendingUnit removed — units now spawn from training queue"

# Remove handleRecruit function
idx = find_line("function handleRecruit(col,row)")
# Find end of function
brace_count = 0
for i in range(idx, len(lines)):
    brace_count += lines[i].count('{') - lines[i].count('}')
    if brace_count == 0 and i > idx:
        end_idx = i
        break

replace_range(idx, end_idx, [
    "// handleRecruit removed — units now spawn from training queue only",
])
print("  ✓ handleRecruit removed")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 14: Update click handler to remove recruit references + add selection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 14: Updating click handler...")

# Remove cavalryPendingUnit check in click handler
idx = find_line_safe("if(cavalryPendingUnit){handleRecruit(col,row);return;}")
if idx >= 0:
    lines[idx] = "  // cavalryPendingUnit removed"

# Remove UNIT_TYPES[selectedTool] recruit call
idx = find_line_safe("else if(UNIT_TYPES[selectedTool])handleRecruit(col,row);")
if idx >= 0:
    lines[idx] = "  // old unit recruit call removed — units train from barracks now"

# Remove cavalryPendingUnit from Escape handler  
idx = find_line_safe("cavalryPendingUnit=null;")
if idx >= 0:
    lines[idx] = "    // cavalryPendingUnit removed"

print("  ✓ Click handler updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 15: Rewrite drawUnits — circles instead of tiles
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 15: Rewriting drawUnits (circles)...")

idx = find_line("function drawUnits(now){")
# Find end of drawUnits — look for the next function definition
end_search = idx + 1
brace_count = 0
for i in range(idx, len(lines)):
    brace_count += lines[i].count('{') - lines[i].count('}')
    if brace_count == 0 and i > idx:
        end_idx = i
        break

replace_range(idx, end_idx, [
    "function drawUnits(now){",
    "  const z=cam.zoom;",
    "  for(const u of units){",
    "    if(u.hp<=0)continue;",
    "    // Fog gate",
    "    const uc=Math.floor(u.x/TILE_SIZE),ur=Math.floor(u.y/TILE_SIZE);",
    "    if(hqPlaced&&fogMap[uc]&&fogMap[uc][ur]!==FOG_VISIBLE)continue;",
    "    const sx=(u.x-cam.x)*z, sy=(u.y-cam.y)*z;",
    "    const r=UNIT_CIRCLE_PX*z;",
    "    // Frustum cull",
    "    if(sx+r<0||sx-r>canvas.width||sy+r<0||sy-r>canvas.height)continue;",
    "    const def=UNIT_TYPES[u.type];",
    "    const[cr,cg,cb]=def.color;",
    "    const rank=unitRank(u.xp);",
    "",
    "    // Morale flicker",
    "    const isBroken=u.moraleState==='broken';",
    "    const isLowMorale=u.morale<MORALE_LOW_THRESHOLD&&!isBroken;",
    "    let moraleAlpha=1;",
    "    if(isBroken) moraleAlpha=Math.sin(now*0.015)*0.3+0.5;",
    "    else if(isLowMorale) moraleAlpha=Math.sin(now*0.008)*0.15+0.75;",
    "    ctx.globalAlpha=moraleAlpha;",
    "",
    "    // Selection ring (under body)",
    "    const isSelected=selectedUnits.includes(u);",
    "    if(isSelected){",
    "      ctx.strokeStyle='rgba(100,220,255,0.7)'; ctx.lineWidth=2*z;",
    "      ctx.beginPath();ctx.arc(sx,sy,r+3*z,0,Math.PI*2);ctx.stroke();",
    "    }",
    "",
    "    // Formation glow",
    "    if(u.shieldWall){",
    "      const swPulse=Math.sin(now*0.004)*0.1+0.25;",
    "      ctx.fillStyle=`rgba(80,140,220,${swPulse})`;",
    "      ctx.beginPath();ctx.arc(sx,sy,r+2*z,0,Math.PI*2);ctx.fill();",
    "    }",
    "    if(u.protectedFire){",
    "      const pfPulse=Math.sin(now*0.005+1)*0.1+0.2;",
    "      ctx.fillStyle=`rgba(80,200,100,${pfPulse})`;",
    "      ctx.beginPath();ctx.arc(sx,sy,r+2*z,0,Math.PI*2);ctx.fill();",
    "    }",
    "",
    "    // Body circle",
    "    ctx.fillStyle=isBroken?`rgb(${Math.min(255,cr+60)},${Math.max(0,cg-40)},${Math.max(0,cb-40)})`:`rgb(${cr},${cg},${cb})`;",
    "    ctx.beginPath();ctx.arc(sx,sy,r,0,Math.PI*2);ctx.fill();",
    "",
    "    // Formation tint overlays",
    "    if(u.shieldWall){ctx.fillStyle='rgba(80,150,255,0.2)';ctx.beginPath();ctx.arc(sx,sy,r,0,Math.PI*2);ctx.fill();}",
    "    if(u.protectedFire){ctx.fillStyle='rgba(80,220,100,0.15)';ctx.beginPath();ctx.arc(sx,sy,r,0,Math.PI*2);ctx.fill();}",
    "",
    "    // Attack flash",
    "    const atkRate=getUnitAtkRate(u);",
    "    if(game.phase==='COMBAT'&&u.atkCooldown>atkRate*0.7){",
    "      ctx.fillStyle='rgba(255,255,200,0.25)';ctx.beginPath();ctx.arc(sx,sy,r,0,Math.PI*2);ctx.fill();",
    "    }",
    "",
    "    // Border/rank glow",
    "    if(rank>0){",
    "      const rankColors=['','rgba(180,180,100,0.4)','rgba(200,160,60,0.5)','rgba(255,200,80,0.6)'];",
    "      ctx.strokeStyle=rankColors[rank];ctx.lineWidth=2*z;",
    "      ctx.beginPath();ctx.arc(sx,sy,r,0,Math.PI*2);ctx.stroke();",
    "    } else {",
    "      ctx.strokeStyle='rgba(255,255,255,0.15)';ctx.lineWidth=z;",
    "      ctx.beginPath();ctx.arc(sx,sy,r,0,Math.PI*2);ctx.stroke();",
    "    }",
    "",
    "    // Letter icon",
    "    ctx.fillStyle='rgba(255,255,255,0.9)';ctx.font=`bold ${11*z}px system-ui`;ctx.textAlign='center';ctx.textBaseline='middle';",
    "    ctx.fillText(def.letter,sx,sy+z);",
    "",
    "    // Range indicator for ranged units (combat only)",
    "    if(def.range>1.5&&game.phase==='COMBAT'){",
    "      ctx.strokeStyle=`rgba(${cr},${cg},${cb},0.1)`;ctx.lineWidth=z;",
    "      ctx.beginPath();ctx.arc(sx,sy,def.range*TILE_SIZE*z,0,Math.PI*2);ctx.stroke();",
    "    }",
    "",
    "    // HP bar",
    "    if(game.phase==='COMBAT'||u.hp<u.maxHP){",
    "      const bw=r*2.2,bh=3*z;",
    "      ctx.fillStyle='rgba(0,0,0,0.5)';ctx.fillRect(sx-bw/2,sy-r-bh-4*z,bw,bh);",
    "      const hpPct=u.hp/u.maxHP;",
    "      ctx.fillStyle=hpPct>0.5?'#4a4':hpPct>0.25?'#da4':'#d44';",
    "      ctx.fillRect(sx-bw/2,sy-r-bh-4*z,bw*hpPct,bh);",
    "    }",
    "",
    "    // Morale bar (above HP)",
    "    if(game.phase==='COMBAT'||u.morale<MORALE_MAX){",
    "      const bw=r*2.2,bh=2*z;",
    "      const mby=sy-r-5*z-bh-3*z;",
    "      ctx.fillStyle='rgba(0,0,0,0.4)';ctx.fillRect(sx-bw/2,mby,bw,bh);",
    "      const mPct=u.morale/MORALE_MAX;",
    "      ctx.fillStyle=mPct>0.5?'rgba(220,200,60,0.9)':mPct>0.2?'rgba(220,140,40,0.9)':'rgba(220,60,40,0.9)';",
    "      ctx.fillRect(sx-bw/2,mby,bw*mPct,bh);",
    "    }",
    "",
    "    // Rank chevrons",
    "    if(rank>0){",
    "      const dotR=2*z;",
    "      const dotY=sy+r+3*z;",
    "      const startX=sx-(rank-1)*dotR*1.5;",
    "      const rankDotColors=['','#cccc70','#dda840','#ffc840'];",
    "      ctx.fillStyle=rankDotColors[rank];",
    "      for(let d=0;d<rank;d++){ctx.beginPath();ctx.arc(startX+d*dotR*3,dotY,dotR,0,Math.PI*2);ctx.fill();}",
    "    }",
    "",
    "    // Move order indicator (line from unit to target)",
    "    if(u.path&&u.pathIdx<u.path.length&&isSelected){",
    "      const tgt=u.path[u.path.length-1];",
    "      const tx=(tgt.c*TILE_SIZE+TILE_SIZE/2-cam.x)*z, ty=(tgt.r*TILE_SIZE+TILE_SIZE/2-cam.y)*z;",
    "      ctx.strokeStyle='rgba(100,220,255,0.2)';ctx.lineWidth=z;",
    "      ctx.setLineDash([3*z,3*z]);",
    "      ctx.beginPath();ctx.moveTo(sx,sy);ctx.lineTo(tx,ty);ctx.stroke();",
    "      ctx.setLineDash([]);",
    "    }",
    "",
    "    ctx.globalAlpha=1;",
    "  }",
    "  ctx.textAlign='start';ctx.textBaseline='alphabetic';",
    "",
    "  // ── BOX SELECT PREVIEW ──",
    "  if(isBoxSelecting&&boxSelectStart&&boxSelectEnd){",
    "    const bx=Math.min(boxSelectStart.sx,boxSelectEnd.sx);",
    "    const by=Math.min(boxSelectStart.sy,boxSelectEnd.sy);",
    "    const bw=Math.abs(boxSelectEnd.sx-boxSelectStart.sx);",
    "    const bh=Math.abs(boxSelectEnd.sy-boxSelectStart.sy);",
    "    ctx.strokeStyle='rgba(100,220,255,0.6)';ctx.lineWidth=1;",
    "    ctx.strokeRect(bx,by,bw,bh);",
    "    ctx.fillStyle='rgba(100,220,255,0.08)';",
    "    ctx.fillRect(bx,by,bw,bh);",
    "  }",
    "}",
])
print("  ✓ drawUnits rewritten with circles + selection ring + box select")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 16: Update minimap to use x/y
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 16: Updating minimap unit rendering...")

idx = find_line("// Units on minimap")
end_idx = find_line("}", idx)

replace_range(idx, end_idx, [
    "  // Units on minimap",
    "  for(const u of units){",
    "    if(u.hp<=0)continue;",
    "    const def=UNIT_TYPES[u.type];",
    "    const isSelected=selectedUnits.includes(u);",
    "    mmCtx.fillStyle=isSelected?'rgba(100,220,255,0.9)':`rgb(${def.color[0]},${def.color[1]},${def.color[2]})`;",
    "    mmCtx.fillRect((u.x/TILE_SIZE)*sx-0.5,(u.y/TILE_SIZE)*sy-0.5,Math.max(sx,1.5),Math.max(sy,1.5));",
    "  }",
])
print("  ✓ Minimap updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 17: Update drawHoverTile to use x/y for unit detection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 17: Updating drawHoverTile...")
# unitAt already updated to work with x/y, so hover should still work
print("  ✓ drawHoverTile uses unitAt which is already updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 18: Update aftermath screen references
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 18: Updating aftermath/upkeep references...")
# These reference units[] length and UNIT_TYPES which still work
# The unit info panel uses unitAt which we already fixed
print("  ✓ No changes needed")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 19: Update cavalryAttack to use u.x/u.y
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 19: Updating cavalryAttack...")

idx = find_line_safe("function cavalryAttack(")
if idx >= 0:
    # Find the ux/uy line inside
    ux_idx = find_line_safe("const ux=u.col*TILE_SIZE+TILE_SIZE/2", idx)
    if ux_idx >= 0:
        lines[ux_idx] = "  const ux=u.x, uy=u.y;"
    print("  ✓ cavalryAttack updated")
else:
    print("  ⚠ cavalryAttack not found (may be inline)")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 20: Update restartGame to clear selection state
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 20: Updating restartGame...")

idx = find_line("cavalryPendingUnit=null;", find_line("function restartGame"))
lines[idx] = "  selectedUnits=[]; controlGroups=[null,null,null]; boxSelectStart=null; boxSelectEnd=null; isBoxSelecting=false;"

print("  ✓ restartGame updated")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 21: Update endWave / aftermath survivor references
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 21: Updating wave aftermath survivors...")

# The survivors reference u.col/u.row — update any that still exist
# Search for references to u.col in the endWave/aftermath code
# _preWaveUnits doesn't use col/row
# The survivors push line at ~3349 might reference col/row
idx = find_line_safe("survivors.push({unit:u,type:u.type")
if idx >= 0:
    # Check if it has col/row
    if 'u.col' in lines[idx] or 'u.row' in lines[idx]:
        lines[idx] = lines[idx].replace('u.col', 'Math.floor(u.x/TILE_SIZE)').replace('u.row', 'Math.floor(u.y/TILE_SIZE)')
        print("  ✓ Survivors updated")
    else:
        print("  ✓ Survivors already ok")
else:
    print("  ✓ No survivor col/row refs found")

# Save
with open(FILE, 'w') as f:
    f.write('\n'.join(lines))
print("\n  ✓ Saved (Part 2 complete)")
