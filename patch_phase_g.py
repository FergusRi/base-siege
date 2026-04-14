#!/usr/bin/env python3
"""Phase G: Hero Guard System
Adds hero guard upgrades, assign-to-guard, follow behavior, auto-attack, dismiss, and UI.
"""

FILE = '/home/user/base-siege/index.html'

with open(FILE, 'r') as f:
    src = f.read()

def safe_replace(old, new, label):
    global src
    assert old in src, f"FAILED to find anchor for: {label}\nSearching for:\n{repr(old[:200])}"
    count = src.count(old)
    assert count == 1, f"AMBIGUOUS: found {count} matches for: {label}"
    src = src.replace(old, new, 1)
    print(f"  ✓ {label}")

print("Phase G: Hero Guard System")
print("=" * 50)

# ═══════════════════════════════════════════════════════════
#  1. GUARD STATE — extend hero object + add constants
# ═══════════════════════════════════════════════════════════

safe_replace(
    '  kills:0,           // hero kill count\n};',
    '''  kills:0,           // hero kill count
  guardLevel:0,      // 0=none, 1/2/3 = Guard I/II/III
};

// ─── HERO GUARD SYSTEM (Phase G) ───
const GUARD_UPGRADES = [
  null, // index 0 unused
  { name:'Guard I',   maxGuards:2, cost:{metal:10} },
  { name:'Guard II',  maxGuards:4, cost:{metal:20, gold:5} },
  { name:'Guard III', maxGuards:6, cost:{metal:30, gold:10} },
];
let heroGuards = []; // references to units currently guarding the hero''',
    "1. Hero guard state + constants"
)

# ═══════════════════════════════════════════════════════════
#  2. GUARD UPGRADE BUTTON — add to settlement panel HTML
# ═══════════════════════════════════════════════════════════

safe_replace(
    '    <button class="sp-btn" id="sp-priority" onclick="panelCyclePriority()">⚖️ Priority: All</button>\n    <button class="sp-btn sp-close" onclick="closeSettlementPanel()">✕ Close</button>',
    '    <button class="sp-btn" id="sp-priority" onclick="panelCyclePriority()">⚖️ Priority: All</button>\n    <button class="sp-btn" id="sp-guard" onclick="panelGuardUpgrade()">🛡️ Guard I (10M)</button>\n    <button class="sp-btn sp-close" onclick="closeSettlementPanel()">✕ Close</button>',
    "2. Guard upgrade button in HTML"
)

# ═══════════════════════════════════════════════════════════
#  3. GUARD UPGRADE PURCHASE FUNCTION — after panelCyclePriority
# ═══════════════════════════════════════════════════════════

safe_replace(
    'function panelCyclePriority() {\n  if (!panelSettKey) return;\n  const [c, r] = panelSettKey.split(\',\').map(Number);\n  cycleSettlementPriority(c, r);\n  updateSettlementPanel();\n}',
    '''function panelCyclePriority() {
  if (!panelSettKey) return;
  const [c, r] = panelSettKey.split(',').map(Number);
  cycleSettlementPriority(c, r);
  updateSettlementPanel();
}

function panelGuardUpgrade() {
  if (!panelSettKey) return;
  const nextLvl = (hero.guardLevel || 0) + 1;
  if (nextLvl > 3) return;
  const upg = GUARD_UPGRADES[nextLvl];
  for (const [r, a] of Object.entries(upg.cost)) {
    if ((game.resources[r] || 0) < a) {
      addFloat("Can't afford!", hero.x, hero.y - TILE_SIZE, '#ff6666');
      return;
    }
  }
  for (const [r, a] of Object.entries(upg.cost)) game.resources[r] -= a;
  hero.guardLevel = nextLvl;
  addFloat('🛡️ ' + upg.name + ' unlocked!', hero.x, hero.y - TILE_SIZE, '#ffd700');
  addParticles(hero.x, hero.y, 'rgba(255,215,0,0.7)', 8);
  updateSettlementPanel();
}''',
    "3. Guard upgrade purchase function"
)

# ═══════════════════════════════════════════════════════════
#  4. UPDATE SETTLEMENT PANEL — add guard button update
# ═══════════════════════════════════════════════════════════

# The end of updateSettlementPanel — find the priority line then }
safe_replace(
    "  document.getElementById('sp-priority').textContent = priIcon + ' Priority: ' + pri.charAt(0).toUpperCase() + pri.slice(1);\n}",
    """  document.getElementById('sp-priority').textContent = priIcon + ' Priority: ' + pri.charAt(0).toUpperCase() + pri.slice(1);
  // Guard upgrade button
  const guardBtn = document.getElementById('sp-guard');
  const gLvl = hero.guardLevel || 0;
  if (gLvl >= 3) {
    guardBtn.textContent = '🛡️ Guard III (MAX)';
    guardBtn.classList.add('disabled');
  } else {
    const nextG = GUARD_UPGRADES[gLvl + 1];
    const gCostStr = Object.entries(nextG.cost).map(([r, a]) => a + r[0].toUpperCase()).join('+');
    const gAfford = Object.entries(nextG.cost).every(([r, a]) => (game.resources[r] || 0) >= a);
    guardBtn.textContent = '🛡️ ' + nextG.name + ' (' + gCostStr + ')';
    guardBtn.classList.toggle('disabled', !gAfford);
  }
}""",
    "4. Guard button update in settlement panel"
)

# ═══════════════════════════════════════════════════════════
#  5. ASSIGN TO GUARD — right-click on hero detection
# ═══════════════════════════════════════════════════════════

safe_replace(
    "  // Check if clicking on enemy — attack-move\n  let clickedEnemy = null;\n  if (game.phase === 'COMBAT') {",
    """  // Check if right-clicking on hero — assign to guard
  if (hero.guardLevel > 0 && selectedUnits.length > 0 && !isFormDragging) {
    const hdx = hero.x - wx, hdy = hero.y - wy;
    if (hdx * hdx + hdy * hdy < (TILE_SIZE * 1.2) * (TILE_SIZE * 1.2)) {
      assignGuards(selectedUnits.filter(u => u.hp > 0 && u.moraleState !== 'broken'));
      formDragStart = null; formDragEnd = null; isFormDragging = false; formGhosts = [];
      return;
    }
  }

  // Check if clicking on enemy — attack-move
  let clickedEnemy = null;
  if (game.phase === 'COMBAT') {""",
    "5. Assign-to-guard on right-click hero"
)

# ═══════════════════════════════════════════════════════════
#  6. GUARD CORE FUNCTIONS — before left-click selection
# ═══════════════════════════════════════════════════════════

safe_replace(
    '// ─── Left-click unit selection (mousedown for box select start) ───',
    '''// ─── HERO GUARD FUNCTIONS (Phase G) ───
function assignGuards(unitsToAssign) {
  const maxG = GUARD_UPGRADES[hero.guardLevel] ? GUARD_UPGRADES[hero.guardLevel].maxGuards : 0;
  if (maxG <= 0) { addFloat('No guard upgrade!', hero.x, hero.y - TILE_SIZE, '#ff6666'); return; }
  let added = 0;
  for (const u of unitsToAssign) {
    if (heroGuards.length >= maxG) break;
    if (u.isGuard) continue;
    u.isGuard = true;
    u.path = null; u.state = 'guard';
    heroGuards.push(u);
    added++;
  }
  heroGuards = heroGuards.filter(g => g.hp > 0 && units.includes(g));
  if (added > 0) {
    addFloat('🛡️ +' + added + ' Guard' + (added > 1 ? 's' : ''), hero.x, hero.y - TILE_SIZE, '#ffd700');
    addParticles(hero.x, hero.y, 'rgba(255,215,0,0.6)', 6);
  } else if (heroGuards.length >= maxG) {
    addFloat('Guard full! (' + maxG + '/' + maxG + ')', hero.x, hero.y - TILE_SIZE, '#ffaa44');
  }
}

function dismissGuards(unitsToDismiss) {
  let removed = 0;
  for (const u of unitsToDismiss) {
    if (!u.isGuard) continue;
    u.isGuard = false;
    u.state = 'idle';
    removed++;
  }
  heroGuards = heroGuards.filter(g => g.hp > 0 && g.isGuard && units.includes(g));
  if (removed > 0) {
    addFloat('🛡️ -' + removed + ' dismissed', hero.x, hero.y - TILE_SIZE, '#aaaacc');
  }
}

function updateHeroGuards(dt) {
  heroGuards = heroGuards.filter(g => g.hp > 0 && g.isGuard && units.includes(g));
  if (heroGuards.length === 0) return;
  const n = heroGuards.length;
  const guardRadius = TILE_SIZE * 1.8;
  for (let i = 0; i < n; i++) {
    const g = heroGuards[i];
    if (g.moraleState === 'broken') continue;
    const angle = (Math.PI * 2 * i) / n;
    const tx = hero.x + Math.cos(angle) * guardRadius;
    const ty = hero.y + Math.sin(angle) * guardRadius;
    const dx = tx - g.x, dy = ty - g.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > TILE_SIZE * 0.5) {
      const speed = (g.speed || 2.5) * TILE_SIZE * dt * 0.85;
      if (dist <= speed) { g.x = tx; g.y = ty; }
      else { g.x += (dx / dist) * speed; g.y += (dy / dist) * speed; }
      g.path = null;
    }
  }
}

// ─── Left-click unit selection (mousedown for box select start) ───''',
    "6. Guard assign/dismiss/follow functions"
)

# ═══════════════════════════════════════════════════════════
#  7. CALL updateHeroGuards FROM updateHero
# ═══════════════════════════════════════════════════════════

safe_replace(
    '  if(heroCanWalkTo(nx,hero.y))hero.x=nx;\n  if(heroCanWalkTo(hero.x,ny))hero.y=ny;\n  clampHero();\n}',
    '  if(heroCanWalkTo(nx,hero.y))hero.x=nx;\n  if(heroCanWalkTo(hero.x,ny))hero.y=ny;\n  clampHero();\n  updateHeroGuards(dt);\n}',
    "7. Call updateHeroGuards in updateHero"
)

# ═══════════════════════════════════════════════════════════
#  8. GUARD UNITS SKIP PATH MOVEMENT (follow hero instead)
# ═══════════════════════════════════════════════════════════

safe_replace(
    '    // ── MOVEMENT along path ──\n    if (u.path && u.pathIdx < u.path.length) {',
    '    // ── GUARD: skip path movement (handled by updateHeroGuards) ──\n    if (u.isGuard && u.state === \'guard\') {\n      // Combat still handled below — just skip movement\n    } else\n\n    // ── MOVEMENT along path ──\n    if (u.path && u.pathIdx < u.path.length) {',
    "8. Guard units skip path movement"
)

# ═══════════════════════════════════════════════════════════
#  9. DISMISS GUARD HOTKEY — 'G' key
# ═══════════════════════════════════════════════════════════

safe_replace(
    "window.addEventListener('touchstart',e=>{if(e.touches.length===1)",
    """// ─── DISMISS GUARD HOTKEY (G) ───
window.addEventListener('keydown', e => {
  if ((e.key === 'g' || e.key === 'G') && !e.ctrlKey && !e.altKey && !e.metaKey) {
    if (game.phase !== 'BUILD' && game.phase !== 'COMBAT') return;
    if (selectedUnits.length > 0) {
      const guards = selectedUnits.filter(u => u.isGuard);
      if (guards.length > 0) { dismissGuards(guards); e.preventDefault(); }
    }
  }
});

window.addEventListener('touchstart',e=>{if(e.touches.length===1)""",
    "9. Dismiss guard hotkey (G)"
)

# ═══════════════════════════════════════════════════════════
#  10. VISUAL: GOLD GUARD RING — in unit draw section
# ═══════════════════════════════════════════════════════════

safe_replace(
    "    // Selection ring (under body)\n    const isSelected=selectedUnits.includes(u);\n    if(isSelected){\n      ctx.strokeStyle='rgba(100,220,255,0.7)'; ctx.lineWidth=2*z;\n      ctx.beginPath();ctx.arc(sx,sy,r+3*z,0,Math.PI*2);ctx.stroke();\n    }",
    """    // Guard ring (gold, under selection ring)
    if(u.isGuard){
      const guardPulse=Math.sin(now*0.004)*0.15+0.55;
      ctx.strokeStyle=`rgba(255,215,0,${guardPulse})`;ctx.lineWidth=2.5*z;
      ctx.beginPath();ctx.arc(sx,sy,r+5*z,0,Math.PI*2);ctx.stroke();
    }

    // Selection ring (under body)
    const isSelected=selectedUnits.includes(u);
    if(isSelected){
      ctx.strokeStyle='rgba(100,220,255,0.7)'; ctx.lineWidth=2*z;
      ctx.beginPath();ctx.arc(sx,sy,r+3*z,0,Math.PI*2);ctx.stroke();
    }""",
    "10. Gold guard ring visual"
)

# ═══════════════════════════════════════════════════════════
#  11. GUARD INDICATOR ON MINIMAP
# ═══════════════════════════════════════════════════════════

safe_replace(
    "    mmCtx.fillStyle=isSelected?'rgba(100,220,255,0.9)':`rgb(${def.color[0]},${def.color[1]},${def.color[2]})`;\n    mmCtx.fillRect((u.x/TILE_SIZE)*sx-0.5,(u.y/TILE_SIZE)*sy-0.5,Math.max(sx,1.5),Math.max(sy,1.5));",
    "    mmCtx.fillStyle=u.isGuard?'rgba(255,215,0,0.9)':isSelected?'rgba(100,220,255,0.9)':`rgb(${def.color[0]},${def.color[1]},${def.color[2]})`;\n    mmCtx.fillRect((u.x/TILE_SIZE)*sx-0.5,(u.y/TILE_SIZE)*sy-0.5,Math.max(sx,1.5),Math.max(sy,1.5));",
    "11. Guard indicator on minimap"
)

# ═══════════════════════════════════════════════════════════
#  12. FIX PRE-EXISTING STRAY DUPLICATE LINE AT MINIMAP
#     Lines 6886-6887 are stray duplicates from a prior patch
# ═══════════════════════════════════════════════════════════

stray = "  }\n    mmCtx.fillRect((u.x/TILE_SIZE)*sx,(u.y/TILE_SIZE)*sy,Math.max(sx,1.5),Math.max(sy,1.5));\n  }\n  // Citizens on minimap"
if stray in src:
    safe_replace(stray, "  }\n  // Citizens on minimap", "12. Fix stray duplicate minimap lines")
else:
    print("  ⚠ Stray minimap lines not found (may already be clean)")

# ═══════════════════════════════════════════════════════════
#  13. GUARD COUNT IN COMBAT HINT
# ═══════════════════════════════════════════════════════════

safe_replace(
    "if(game.phase==='COMBAT'){h.textContent='⚔️ COMBAT — WASD move · Click attack · Tab cycle units · Defend your settlements!';return;}",
    "if(game.phase==='COMBAT'){const gC=heroGuards.length,gMax=hero.guardLevel>0?GUARD_UPGRADES[hero.guardLevel].maxGuards:0;h.textContent='⚔️ COMBAT — WASD move · Click attack · Tab cycle units'+(gMax>0?' · 🛡️'+gC+'/'+gMax+' guards':'')+' · G=dismiss guard';return;}",
    "13. Guard count in combat hint"
)

# ═══════════════════════════════════════════════════════════
#  14. CLEAN GUARD REFS WHEN UNIT HP <= 0 — in updateUnits death handling
#     Units aren't spliced, but we should clean isGuard flag when hp<=0
#     The filter in updateHeroGuards handles this already (filters hp>0)
#     So no additional code needed — just verify existing filter catches it
# ═══════════════════════════════════════════════════════════
print("  ✓ 14. Dead guard cleanup (handled by heroGuards filter in updateHeroGuards)")

# ═══════════════════════════════════════════════════════════
#  15. RESET GUARDS ON GAME RESTART
# ═══════════════════════════════════════════════════════════

safe_replace(
    '  hero.stunTimer=0; hero.hitFlash=0; hero.kills=0;',
    '  hero.stunTimer=0; hero.hitFlash=0; hero.kills=0; hero.guardLevel=0;\n  heroGuards=[];',
    "15. Reset guards on game restart"
)

# ═══════════════════════════════════════════════════════════
#  WRITE OUTPUT
# ═══════════════════════════════════════════════════════════

with open(FILE, 'w') as f:
    f.write(src)

print("=" * 50)
print("✅ Phase G: Hero Guard System applied successfully!")
print("  - Guard upgrades I/II/III (settlement panel)")  
print("  - Assign guard: select units → right-click hero")
print("  - Guard follow: circle formation around hero")
print("  - Guard auto-attack: uses normal combat system")
print("  - Dismiss: select guards → press G")
print("  - Visual: gold ring on guard units + minimap")
print("  - Guard count in combat HUD")
