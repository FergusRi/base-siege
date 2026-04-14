#!/usr/bin/env python3
"""Phase I: Economy Rework — Patch Script
1. Convert unit upkeep from food-only to multi-resource objects
2. Remove free wave bonus
3. Update starting resources
4. Rewrite getTotalUpkeep() and payUpkeep() for multi-resource
5. Update HUD upkeep display for multi-resource
6. Update aftermath screen with comprehensive income/expense summary
"""

import re

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

src = ''.join(lines)

# ══════════════════════════════════════════════════════════════
# 1. Convert UNIT_TYPES upkeep from number to object
# ══════════════════════════════════════════════════════════════

# Militia: upkeep:1 → upkeep:{food:1}
src = src.replace(
    "MILITIA:{name:'Militia',hp:22,dmg:4,range:1.2,speed:3,cost:{wood:5,food:2},upkeep:1,",
    "MILITIA:{name:'Militia',hp:22,dmg:4,range:1.2,speed:3,cost:{wood:5,food:2},upkeep:{food:1},"
)

# Archer: upkeep:1 → upkeep:{food:1,metal:1}
src = src.replace(
    "ARCHER:{name:'Archer',hp:12,dmg:5,range:4,speed:2.5,cost:{wood:5,metal:3},upkeep:1,",
    "ARCHER:{name:'Archer',hp:12,dmg:5,range:4,speed:2.5,cost:{wood:5,metal:3},upkeep:{food:1,metal:1},"
)

# Spearman: upkeep:1 → upkeep:{food:1,metal:1}
src = src.replace(
    "SPEARMAN:{name:'Spearman',hp:16,dmg:3,range:1.5,speed:2.5,cost:{wood:4,food:3},upkeep:1,",
    "SPEARMAN:{name:'Spearman',hp:16,dmg:3,range:1.5,speed:2.5,cost:{wood:4,food:3},upkeep:{food:1,metal:1},"
)

# Cavalry: upkeep:2 → upkeep:{food:2,metal:2}
src = src.replace(
    "CAVALRY:{name:'Cavalry',hp:18,dmg:6,range:1.3,speed:6,cost:{wood:8,food:5},upkeep:2,",
    "CAVALRY:{name:'Cavalry',hp:18,dmg:6,range:1.3,speed:6,cost:{wood:8,food:5},upkeep:{food:2,metal:2},"
)

# Catapult: upkeep:2 → upkeep:{food:1,metal:3}
src = src.replace(
    "CATAPULT:{name:'Catapult',hp:8,dmg:12,range:6,speed:1.5,cost:{wood:12,stone:5,metal:4},upkeep:2,",
    "CATAPULT:{name:'Catapult',hp:8,dmg:12,range:6,speed:1.5,cost:{wood:12,stone:5,metal:4},upkeep:{food:1,metal:3},"
)

# ══════════════════════════════════════════════════════════════
# 2. Update INITIAL_RESOURCES
# ══════════════════════════════════════════════════════════════

src = src.replace(
    "const INITIAL_RESOURCES={wood:80,stone:45,metal:25,food:35,gold:0};",
    "const INITIAL_RESOURCES={wood:100,stone:50,metal:30,food:50,gold:0};"
)

# ══════════════════════════════════════════════════════════════
# 3. Remove free wave bonus in endWave()
# ══════════════════════════════════════════════════════════════

# Remove the 3 lines: comment + bonus calc + wood add + food add
src = src.replace(
    """  // Bonus resources (awarded before upkeep)
  const bonus=2+game.wave;
  game.resources.wood+=bonus;
  game.resources.food+=bonus;""",
    "  // Wave bonus removed — income only from buildings + citizen harvesting"
)

# ══════════════════════════════════════════════════════════════
# 4. Rewrite getTotalUpkeep() for multi-resource
# ══════════════════════════════════════════════════════════════

old_getTotalUpkeep = """function getTotalUpkeep(){
  let total=0;
  for(const u of units) total+=(UNIT_TYPES[u.type].upkeep||0);
  return total;
}"""

new_getTotalUpkeep = """function getTotalUpkeep(){
  const total={food:0,wood:0,stone:0,metal:0,gold:0};
  for(const u of units){
    const up=UNIT_TYPES[u.type].upkeep;
    if(!up) continue;
    if(typeof up==='number'){total.food+=up;} // legacy fallback
    else { for(const[r,a] of Object.entries(up)) total[r]=(total[r]||0)+a; }
  }
  return total;
}"""

src = src.replace(old_getTotalUpkeep, new_getTotalUpkeep)

# ══════════════════════════════════════════════════════════════
# 5. Rewrite payUpkeep() for multi-resource
# ══════════════════════════════════════════════════════════════

old_payUpkeep = """// Pay upkeep — returns array of unfed units (starving)
function payUpkeep(){
  // Sort units by value: highest upkeep / highest rank first get fed
  const sorted=[...units].sort((a,b)=>{
    const rA=unitRank(a.xp), rB=unitRank(b.xp);
    if(rB!==rA) return rB-rA; // higher rank fed first
    return (UNIT_TYPES[b.type].upkeep||0)-(UNIT_TYPES[a.type].upkeep||0);
  });
  let available=game.resources.food;
  const unfed=[];
  const fed=[];
  for(const u of sorted){
    const cost=UNIT_TYPES[u.type].upkeep||0;
    if(available>=cost){
      available-=cost;
      fed.push(u);
    } else {
      unfed.push(u);
    }
  }
  game.resources.food=available;
  return {fed,unfed};
}"""

new_payUpkeep = """// Pay upkeep — multi-resource, applies Granary/Storehouse modifiers
function payUpkeep(){
  const mods=game._upkeepModifiers||{foodUpkeepMult:1,allUpkeepMult:1};
  // Sort units by value: highest rank first get paid
  const sorted=[...units].sort((a,b)=>{
    const rA=unitRank(a.xp), rB=unitRank(b.xp);
    if(rB!==rA) return rB-rA;
    const aTotal=getUnitUpkeepTotal(a.type), bTotal=getUnitUpkeepTotal(b.type);
    return bTotal-aTotal;
  });
  const unfed=[];
  const fed=[];
  const paid={food:0,wood:0,stone:0,metal:0,gold:0};
  for(const u of sorted){
    const up=UNIT_TYPES[u.type].upkeep;
    if(!up){fed.push(u);continue;}
    const costs=typeof up==='number'?{food:up}:{...up};
    // Apply modifiers to each resource
    let canPay=true;
    const adjusted={};
    for(const[res,amt] of Object.entries(costs)){
      let c=amt;
      if(res==='food') c=Math.ceil(c*mods.foodUpkeepMult*mods.allUpkeepMult);
      else c=Math.ceil(c*mods.allUpkeepMult);
      adjusted[res]=c;
      if((game.resources[res]||0)<c) canPay=false;
    }
    if(canPay){
      for(const[res,c] of Object.entries(adjusted)){
        game.resources[res]-=c;
        paid[res]=(paid[res]||0)+c;
      }
      fed.push(u);
    } else {
      unfed.push(u);
    }
  }
  return {fed,unfed,paid};
}

// Helper: total upkeep cost for sorting
function getUnitUpkeepTotal(type){
  const up=UNIT_TYPES[type].upkeep;
  if(!up) return 0;
  if(typeof up==='number') return up;
  let t=0; for(const v of Object.values(up)) t+=v; return t;
}"""

src = src.replace(old_payUpkeep, new_payUpkeep)

# ══════════════════════════════════════════════════════════════
# 6. Update endWave() army upkeep section to capture multi-resource info
# ══════════════════════════════════════════════════════════════

old_army_upkeep = """  // ── ARMY UPKEEP: deduct food, penalize unfed ──
  const totalUpkeep=getTotalUpkeep();
  const foodBeforeUpkeep=game.resources.food;
  const {fed,unfed}=payUpkeep();
  const foodPaid=foodBeforeUpkeep-game.resources.food;
  game._upkeepInfo={totalUpkeep,foodPaid,foodBefore:foodBeforeUpkeep,fed:fed.length,unfed:unfed.length,unfedUnits:unfed.map(u=>({type:u.type,name:UNIT_TYPES[u.type].name}))};"""

new_army_upkeep = """  // ── ARMY UPKEEP: deduct multi-resource, penalize unfed ──
  const totalUpkeep=getTotalUpkeep();
  const resBefore={...game.resources};
  const {fed,unfed,paid}=payUpkeep();
  game._upkeepInfo={totalUpkeep,paid,resBefore,fed:fed.length,unfed:unfed.length,unfedUnits:unfed.map(u=>({type:u.type,name:UNIT_TYPES[u.type].name}))};"""

src = src.replace(old_army_upkeep, new_army_upkeep)

# ══════════════════════════════════════════════════════════════
# 7. Update HUD upkeep display (line ~7114) for multi-resource
# ══════════════════════════════════════════════════════════════

old_hud_upkeep = """  if(units.length>0){
    upkeepWrap.style.display='flex';
    const totalUpkeep=getTotalUpkeep();
    const food=game.resources.food;
    upkeepVal.textContent=`${totalUpkeep}/${food}`;
    upkeepVal.className='upkeep-val '+(food>=totalUpkeep?'upkeep-ok':food>=totalUpkeep*0.5?'upkeep-warn':'upkeep-danger');
  } else {
    upkeepWrap.style.display='none';
  }"""

new_hud_upkeep = """  if(units.length>0){
    upkeepWrap.style.display='flex';
    const totalUpkeep=getTotalUpkeep();
    // Show multi-resource upkeep summary
    const parts=[];
    for(const[r,a] of Object.entries(totalUpkeep)){
      if(a>0){
        const icon=r==='food'?'🍖':r==='metal'?'⚙':r==='wood'?'🪵':r==='stone'?'🪨':r==='gold'?'🪙':'';
        parts.push(`${icon}${a}`);
      }
    }
    const canFeed=Object.entries(totalUpkeep).every(([r,a])=>(game.resources[r]||0)>=a);
    const halfFeed=Object.entries(totalUpkeep).every(([r,a])=>(game.resources[r]||0)>=a*0.5);
    upkeepVal.textContent=parts.join(' ')||'0';
    upkeepVal.className='upkeep-val '+(canFeed?'upkeep-ok':halfFeed?'upkeep-warn':'upkeep-danger');
  } else {
    upkeepWrap.style.display='none';
  }"""

src = src.replace(old_hud_upkeep, new_hud_upkeep)

# ══════════════════════════════════════════════════════════════
# 8. Update canvas upkeep warning for multi-resource
# ══════════════════════════════════════════════════════════════

old_canvas_upkeep = """    if(units.length>0){
      const totalUp=getTotalUpkeep();
      const food=game.resources.food;
      const canFeed=food>=totalUp;
      ctx.font='bold 14px system-ui';
      ctx.shadowBlur=8;
      if(canFeed){
        ctx.fillStyle=`rgba(120,200,120,${pulse*0.7})`;
        ctx.shadowColor='rgba(90,180,90,0.4)';
        ctx.fillText(`🍖 Upkeep: ${totalUp} food (${food} available) ✓`, canvas.width/2, canvas.height-45);
      } else {
        ctx.fillStyle=`rgba(232,100,80,${pulse*0.9})`;
        ctx.shadowColor='rgba(220,60,40,0.5)';
        const deficit=totalUp-food;
        ctx.fillText(`⚠ Upkeep: ${totalUp} food — ${deficit} short! Units will starve!`, canvas.width/2, canvas.height-45);
      }
    }"""

new_canvas_upkeep = """    if(units.length>0){
      const totalUp=getTotalUpkeep();
      const parts=[];
      let canFeed=true;
      for(const[r,a] of Object.entries(totalUp)){
        if(a>0){
          const icon=r==='food'?'🍖':r==='metal'?'⚙':r==='wood'?'🪵':r==='stone'?'🪨':'';
          const have=game.resources[r]||0;
          parts.push(`${icon}${a}`);
          if(have<a) canFeed=false;
        }
      }
      const upkeepStr=parts.join(' ')||'0';
      ctx.font='bold 14px system-ui';
      ctx.shadowBlur=8;
      if(canFeed){
        ctx.fillStyle=`rgba(120,200,120,${pulse*0.7})`;
        ctx.shadowColor='rgba(90,180,90,0.4)';
        ctx.fillText(`Upkeep: ${upkeepStr} ✓`, canvas.width/2, canvas.height-45);
      } else {
        ctx.fillStyle=`rgba(232,100,80,${pulse*0.9})`;
        ctx.shadowColor='rgba(220,60,40,0.5)';
        ctx.fillText(`⚠ Upkeep: ${upkeepStr} — not enough resources!`, canvas.width/2, canvas.height-45);
      }
    }"""

src = src.replace(old_canvas_upkeep, new_canvas_upkeep)

# ══════════════════════════════════════════════════════════════
# 9. Update aftermath screen — replace bonus display + army upkeep section
# ══════════════════════════════════════════════════════════════

# Remove the old wave bonus line
old_bonus_line = """  // Bonus resources
  html+=`<div style="margin-top:14px;font-size:13px;color:rgba(200,200,210,0.6)">+${bonus} Wood, +${bonus} Food wave bonus</div>`;"""

new_bonus_line = """  // No wave bonus — income only from buildings + citizens"""

src = src.replace(old_bonus_line, new_bonus_line)

# Also remove the `const bonus=2+game.wave;` in showAftermathScreen
src = src.replace(
    "  const bonus=2+game.wave;\n\n  let html=`<h2>⚔️ WAVE ${game.wave} CLEARED</h2>`;",
    "\n  let html=`<h2>⚔️ WAVE ${game.wave} CLEARED</h2>`;"
)

# Replace army upkeep section in aftermath
old_aftermath_army = """  // ── UPKEEP & ECONOMY SECTION ──
  const info=game._upkeepInfo;
  if(info&&info.totalUpkeep>0){
    html+=`<div class="aftermath-section"><h3>🍖 Army Upkeep</h3>`;
    html+=`<div style="padding:6px 10px;font-size:13px;background:rgba(255,255,255,0.03);border-radius:8px;margin:3px 0;">`;
    html+=`<span style="opacity:0.6">Food cost:</span> <span style="font-weight:700;color:#e8c56a">${info.foodPaid}/${info.totalUpkeep}</span> food paid`;
    if(info.unfed>0){
      html+=`<br><span style="color:#e87a6a;font-weight:700">⚠ ${info.unfed} unit${info.unfed>1?'s':''} unfed!</span> <span style="opacity:0.5">(-${STARVATION_MORALE_PENALTY} morale each)</span>`;
      for(const u of info.unfedUnits){
        html+=`<br><span style="opacity:0.5;margin-left:12px;">• ${u.name} — starving</span>`;
      }
    } else {
      html+=`<br><span style="color:#7aca7a">✓ All units fed</span>`;
    }
    html+=`<br><span style="opacity:0.5">Remaining food: ${game.resources.food}</span>`;
    html+=`</div></div>`;
  }"""

new_aftermath_army = """  // ── ECONOMY SUMMARY SECTION ──
  const bProd=game._buildingProduction||{};
  const bProdEntries=Object.entries(bProd).filter(([r,a])=>a>0);
  if(bProdEntries.length>0){
    html+=`<div class="aftermath-section"><h3>📦 Building Production</h3>`;
    html+=`<div style="padding:6px 10px;font-size:13px;background:rgba(255,255,255,0.03);border-radius:8px;margin:3px 0;">`;
    const resIcon={food:'🍖',wood:'🪵',stone:'🪨',metal:'⚙',gold:'🪙'};
    for(const[r,a] of bProdEntries){
      html+=`<span style="color:#7aca7a;font-weight:700">+${a}</span> ${resIcon[r]||''} ${r} `;
    }
    html+=`</div></div>`;
  }

  // Building upkeep summary
  const bUp=game._buildingUpkeepInfo;
  if(bUp&&Object.values(bUp.total).some(v=>v>0)){
    html+=`<div class="aftermath-section"><h3>🏗️ Building Upkeep</h3>`;
    html+=`<div style="padding:6px 10px;font-size:13px;background:rgba(255,255,255,0.03);border-radius:8px;margin:3px 0;">`;
    const resIcon={food:'🍖',wood:'🪵',stone:'🪨',metal:'⚙',gold:'🪙'};
    for(const[r,a] of Object.entries(bUp.total)){
      if(a>0) html+=`<span style="color:#e8c56a;font-weight:700">-${a}</span> ${resIcon[r]||''} ${r} `;
    }
    if(bUp.short>0) html+=`<br><span style="color:#e87a6a">⚠ ${bUp.short} resources short</span>`;
    html+=`</div></div>`;
  }

  // ── ARMY UPKEEP (multi-resource) ──
  const info=game._upkeepInfo;
  if(info){
    const hasUpkeep=Object.values(info.totalUpkeep).some(v=>v>0);
    if(hasUpkeep){
      html+=`<div class="aftermath-section"><h3>⚔️ Army Upkeep</h3>`;
      html+=`<div style="padding:6px 10px;font-size:13px;background:rgba(255,255,255,0.03);border-radius:8px;margin:3px 0;">`;
      const resIcon={food:'🍖',wood:'🪵',stone:'🪨',metal:'⚙',gold:'🪙'};
      // Show cost per resource
      for(const[r,a] of Object.entries(info.totalUpkeep)){
        if(a>0){
          const paidAmt=(info.paid&&info.paid[r])||0;
          html+=`${resIcon[r]||''} <span style="font-weight:700;color:#e8c56a">${paidAmt}/${a}</span> ${r} `;
        }
      }
      if(info.unfed>0){
        html+=`<br><span style="color:#e87a6a;font-weight:700">⚠ ${info.unfed} unit${info.unfed>1?'s':''} unfed!</span> <span style="opacity:0.5">(-${STARVATION_MORALE_PENALTY} morale each)</span>`;
        for(const u of info.unfedUnits){
          html+=`<br><span style="opacity:0.5;margin-left:12px;">• ${u.name} — starving</span>`;
        }
      } else {
        html+=`<br><span style="color:#7aca7a">✓ All units fed & supplied</span>`;
      }
      html+=`</div></div>`;
    }
  }

  // ── GRANARY / STOREHOUSE MODIFIERS ──
  const mods=game._upkeepModifiers;
  if(mods&&(mods.granaryCount>0||mods.storehouseCount>0)){
    html+=`<div style="margin-top:6px;font-size:12px;color:rgba(200,200,210,0.6)">`;
    if(mods.granaryCount>0) html+=`🌾 Granary: -${Math.round((1-mods.foodUpkeepMult)*100)}% food upkeep `;
    if(mods.storehouseCount>0) html+=`📦 Storehouse: -${Math.round((1-mods.allUpkeepMult)*100)}% all upkeep`;
    html+=`</div>`;
  }

  // ── RESOURCE TOTALS ──
  html+=`<div style="margin-top:10px;padding:6px 10px;font-size:13px;background:rgba(255,255,255,0.05);border-radius:8px;">`;
  html+=`<span style="opacity:0.7">Resources:</span> `;
  const resIcon2={food:'🍖',wood:'🪵',stone:'🪨',metal:'⚙',gold:'🪙'};
  for(const r of ['food','wood','stone','metal','gold']){
    if(game.resources[r]>0||r==='food') html+=`${resIcon2[r]}${game.resources[r]} `;
  }
  html+=`</div>`;"""

src = src.replace(old_aftermath_army, new_aftermath_army)

# ══════════════════════════════════════════════════════════════
# Write the patched file
# ══════════════════════════════════════════════════════════════

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print("✅ Phase I patch applied successfully!")
print("Changes made:")
print("  1. UNIT_TYPES upkeep → multi-resource objects")
print("  2. INITIAL_RESOURCES → {wood:100, stone:50, metal:30, food:50, gold:0}")
print("  3. Removed free wave bonus")
print("  4. getTotalUpkeep() → returns multi-resource object")
print("  5. payUpkeep() → multi-resource deduction with Granary/Storehouse modifiers")
print("  6. endWave() army upkeep → captures multi-resource paid info")
print("  7. HUD upkeep display → multi-resource icons")
print("  8. Canvas upkeep warning → multi-resource")
print("  9. Aftermath screen → comprehensive economy summary")
