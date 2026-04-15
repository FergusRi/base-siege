# 🏛️ HERO REMOVAL & GOD-MODE REWORK PLAN
## "You are the god. The empire is your body."

> **Goal**: Remove the hero entity entirely. The player becomes an omniscient god
> managing a settlement from above — selecting citizens, assigning guards,
> directing units, and expanding through fog of war via scouts and soldiers.

---

## TABLE OF CONTENTS

1. [Overview & Design Philosophy](#1-overview--design-philosophy)
2. [Phase 1: Camera & Controls (Free-Cam)](#phase-1-camera--controls)
3. [Phase 2: Remove Hero Entity](#phase-2-remove-hero-entity)
4. [Phase 3: Citizen Guard System](#phase-3-citizen-guard-system)
5. [Phase 4: Citizen Economy Rework](#phase-4-citizen-economy-rework)
6. [Phase 5: Unit-Based Fog of War](#phase-5-unit-based-fog-of-war)
7. [Phase 6: Soldier Size Decrease](#phase-6-soldier-size-decrease)
8. [Phase 7: UI & HUD Cleanup](#phase-7-ui--hud-cleanup)
9. [Phase 8: Combat Rework (No Hero Attacks)](#phase-8-combat-rework)
10. [Phase 9: Game Over Condition](#phase-9-game-over-condition)
11. [Full Hero Code Audit (Line-by-Line)](#full-hero-code-audit)
12. [Risk Assessment & Edge Cases](#risk-assessment--edge-cases)
13. [Build Order & Dependencies](#build-order--dependencies)

---

## 1. OVERVIEW & DESIGN PHILOSOPHY

### Before (Hero Mode)
- Player IS the hero — WASD to walk, click to attack/gather
- Camera locked to hero position
- Hero reveals fog of war (6-tile visible, 20-tile explored)
- Guards orbit the hero in a circle formation
- Building requires hero proximity (BUILD_RANGE=30)
- Gathering requires hero proximity (HARVEST_RANGE=14)
- Hero can be knocked down (10s) then revives at 25% HP
- No game over — hero always revives

### After (God Mode)
- Player IS the god — WASD/arrow keys pan camera freely
- Camera is free-roaming (edge-pan + WASD + minimap click)
- Units and structures reveal fog of war (scouts excel at this)
- Guards are assigned to individual citizens (G=assign, D=dismiss)
- Building requires settlement radius only (already exists as tier system)
- Gathering is citizen-only (auto-farm inside city, assignable mining outside)
- Citizens are the lifeblood — lose all settlements = game over
- No hero entity at all

### Key Vibe Shift
| Aspect | Hero Mode | God Mode |
|--------|-----------|----------|
| Camera | Locked to hero | Free pan (RTS style) |
| Combat | Click to swing sword | Direct units, watch battles |
| Building | Must be near hero | Must be in settlement radius |
| Gathering | Hero clicks deposits | Citizens auto-gather |
| Exploration | Hero walks into fog | Send scouts/soldiers |
| Guards | Protect hero | Protect citizens |
| Danger | Hero knockdown | Settlement destruction |
| Feel | Action RPG | City builder / RTS |

---

## PHASE 1: CAMERA & CONTROLS (Free-Cam)
> **Priority: CRITICAL — everything else depends on this**
> **Estimated lines changed: ~60**

### What Changes

The camera currently hard-locks to `hero.x / hero.y` every frame (line 3007-3008).
We replace this with a free-roaming RTS camera.

### Current Code (lines 3000-3015)
```javascript
function updateCamera(){
  const c=document.getElementById('game-canvas');
  cam.tx=hero.x-c.width/(2*cam.tZoom);  // ← REMOVE
  cam.ty=hero.y-c.height/(2*cam.tZoom);  // ← REMOVE
  clampCam();
  cam.x+=(cam.tx-cam.x)*CAM_LERP;
  // ...
}
```

### New Code
```javascript
const CAM_PAN_SPEED = 12 * TILE_SIZE; // pixels/sec — fast RTS scroll

function updateCamera(dt){
  const c=document.getElementById('game-canvas');
  // WASD / Arrow key panning
  let pdx=0, pdy=0;
  if(keys['w']||keys['W']||keys['ArrowUp'])    pdy=-1;
  if(keys['s']||keys['S']||keys['ArrowDown'])   pdy=1;
  if(keys['a']||keys['A']||keys['ArrowLeft'])   pdx=-1;
  if(keys['d']||keys['D']||keys['ArrowRight'])  pdx=1;
  if(pdx!==0&&pdy!==0){pdx*=0.707;pdy*=0.707;}
  cam.tx += pdx * CAM_PAN_SPEED * dt;
  cam.ty += pdy * CAM_PAN_SPEED * dt;
  // Edge-of-screen panning (optional, nice for RTS feel)
  const edgeZone = 30; // px from edge
  const mx=lastMouseX, my=lastMouseY;
  if(mx<edgeZone)       cam.tx -= CAM_PAN_SPEED*dt*0.5;
  if(mx>c.width-edgeZone) cam.tx += CAM_PAN_SPEED*dt*0.5;
  if(my<edgeZone)       cam.ty -= CAM_PAN_SPEED*dt*0.5;
  if(my>c.height-edgeZone) cam.ty += CAM_PAN_SPEED*dt*0.5;
  clampCam();
  cam.x+=(cam.tx-cam.x)*CAM_LERP;
  cam.y+=(cam.ty-cam.y)*CAM_LERP;
  cam.zoom+=(cam.tZoom-cam.zoom)*CAM_LERP;
  if(cam.shake>0){cam.shake*=0.88;cam.x+=Math.random()*cam.shake-cam.shake/2;cam.y+=Math.random()*cam.shake-cam.shake/2;}
}
```

### Minimap Click (line 5577-5578)
Currently teleports hero: `hero.x=...; hero.y=...;`
**Replace**: Set `cam.tx` and `cam.ty` directly (camera jump to clicked location).

```javascript
// OLD: hero.x=(e.clientX-rect.left)/mmCanvas.width*MAP_PX_W;
// NEW:
cam.tx = (e.clientX-rect.left)/mmCanvas.width*MAP_PX_W - canvas.width/(2*cam.tZoom);
cam.ty = (e.clientY-rect.top)/mmCanvas.height*MAP_PX_H - canvas.height/(2*cam.tZoom);
```

### Touch Controls (lines 5016-5017)
Currently drags hero position on mobile. **Replace**: Pan camera on touch drag.

### PLACE_HQ Phase
Currently hero spawns at random location and walks around to explore.
**Replace**: Camera starts centered on map, player can pan freely. Fog starts
partially revealed in center area. Click to place settlement.

### New Keybind: Space = Center on Settlement
Press SPACE (outside of wave start) to snap camera to main settlement.
Provides a "home" button for the god.

---

## PHASE 2: REMOVE HERO ENTITY
> **Priority: CRITICAL**
> **Estimated lines removed: ~200, modified: ~80**

### What Gets Deleted

| Code | Lines | Description |
|------|-------|-------------|
| `const hero={...}` | 2683-2693 | Hero object declaration |
| `heroCol()`, `heroRow()` | 5020-5021 | Hero tile position helpers |
| `clampHero()` | 5024-5027 | Keep hero in bounds |
| `heroCanWalkTo()` | 5029-5042 | Hero walkability check |
| `updateHero(dt)` | 5046-5062 | Hero WASD movement |
| `heroAttack()` | 3781-3805 | Hero melee attack |
| `damageHero(dmg)` | 3824-3837 | Hero taking damage |
| Hero combat tick | 3806-3819 | Cooldown/stun/flash timers |
| `drawHero()` | 6675-6755 | Hero rendering (body, sword, HP, aura) |
| Hero HP bar update | 7181-7186 | HUD HP bar fill |
| Hero on minimap | 7154 | Yellow dot on minimap |
| Hero constants | 658-661 | HERO_SPEED, ATK_DMG, ATK_RATE, ATK_RANGE, KNOCKDOWN_TIME, REVIVE_PCT |
| Hero fog constants | 1343-1344 | HERO_FOG_RADIUS, HERO_EXPLORE_RADIUS |
| Touch hero drag | 5016-5017 | Mobile hero movement |
| Hero spawn | 7222-7234 | Random spawn + camera center |
| Hero reset | 7272-7276 | Reset on game restart |
| Kill counter display | 7251 | "Hero Kills" on game over screen |
| Kill counter update | 7341 | `kh-hero` stat display |

### What Gets Modified (Not Deleted)

| Code | Lines | Current | New |
|------|-------|---------|-----|
| `refreshFogVision()` | 1452-1462 | Reveals fog around hero position | Remove hero vision call; unit vision added in Phase 5 |
| Camera update | 3007-3008 | `cam.tx=hero.x-...` | Free-cam (Phase 1) |
| Spawn ring calc | 2771-2773 | Uses `heroDist` for boundary | Use settlement position only |
| Enemy targeting | 3864-3890 | Targets hero as option | Remove hero from target list |
| Enemy melee | 3980-3984 | Attacks hero if adjacent | Remove hero attack code |
| Projectile hit | 4169-4171 | `heroTarget` hit check | Remove hero hit path |
| Projectile tracking | 4257 | Updates `p.tx/ty` to hero pos | Remove hero tracking |
| Morale recovery | 4841-4843 | Recover near hero (3 tiles) | Recover near settlement instead |
| Click handler | 5298 | `if(COMBAT) heroAttack()` | Remove; combat clicks select/direct units |
| Guard right-click | 5397-5399 | Right-click hero to assign guard | Replaced by citizen guard (Phase 3) |
| Wave start banner | 3239 | Float text at hero position | Float at camera center or settlement |
| Wave end floats | 3622-3627 | Float text at hero position | Float at camera center |
| Guard upgrade | 925-968 | `hero.guardLevel` | Rework for citizen guard tiers |
| Build hint | 2952 | "WASD move · Click attack" | "WASD pan · Click to build" |
| HTML | 417-420 | Hero HP bar in HUD | Remove or replace with settlement HP |
| HTML | 575 | Hero kills stat row | Remove or replace with "Units Lost" |
| CSS | 40, 300, 326 | `.hero-hp-wrap`, `.kh-hero`, `#hero-hp-fill` | Remove |

### Constants to Remove
```javascript
// DELETE these:
const HERO_SPEED=8*TILE_SIZE;
const HERO_ATK_DMG=8, HERO_ATK_RATE=0.4, HERO_ATK_RANGE=1.2*TILE_SIZE;
const HERO_KNOCKDOWN_TIME=10, HERO_REVIVE_PCT=0.25;
const HERO_FOG_RADIUS=6;
const HERO_EXPLORE_RADIUS=20;

// KEEP but repurpose:
const HARVEST_RANGE=14;  // → becomes citizen gather radius
const BUILD_RANGE=30;    // → replaced by settlement.buildRadius (already exists per tier)
```

---

## PHASE 3: CITIZEN GUARD SYSTEM
> **Priority: HIGH — core new mechanic**
> **Estimated lines added: ~120**

### Design

Guards are no longer assigned to the hero. Instead, individual citizens can have
guards assigned to them. Guards follow their assigned citizen, defend them from
enemies, and escort them on gathering trips outside the walls.

### Controls
| Key | Action |
|-----|--------|
| **Click citizen** | Select citizen (highlight, show info panel) |
| **G** | Assign selected idle military unit(s) to the selected citizen as guards |
| **D** | Dismiss guards from the selected citizen |
| **Shift+G** | Assign guards to ALL citizens (distribute evenly) |

### Data Model Changes

```javascript
// REMOVE:
// hero.guardLevel, GUARD_UPGRADES[], heroGuards[]

// ADD to citizen object:
citizen.guards = [];       // array of unit refs guarding this citizen
citizen.maxGuards = 2;     // base limit (upgradeable via research?)
citizen.selected = false;  // whether player has clicked this citizen

// ADD to unit object:
unit.guardTarget = null;   // ref to citizen being guarded (replaces unit.isGuard → hero)
```

### Guard Behavior
1. **Follow Phase**: Guards orbit their assigned citizen in a circle (reuse existing
   `updateHeroGuards` circle logic but targeting `citizen.x/y` instead of `hero.x/y`)
2. **Defend Phase**: When enemies enter within 3 tiles of their citizen, guards
   break formation and engage (existing unit combat AI handles this)
3. **Return Phase**: After combat, guards return to orbit around their citizen
4. **Citizen Dies**: If the citizen's settlement is destroyed, guards become idle units
5. **Guard Dies**: Remove from citizen's guard list, citizen continues without

### Functions to Modify/Create
```
assignGuards()       → assignGuardsToCitizen(citizen, units)
dismissGuards()      → dismissCitizenGuards(citizen)
updateHeroGuards()   → updateCitizenGuards(dt)  // loops all citizens with guards
```

### Guard Circle Positioning (reuse existing logic)
```javascript
function updateCitizenGuards(dt) {
  for (const cit of citizens) {
    if (!cit.guards || cit.guards.length === 0) continue;
    // Clean dead/missing guards
    cit.guards = cit.guards.filter(g => g.hp > 0 && units.includes(g));
    const n = cit.guards.length;
    const guardRadius = TILE_SIZE * 1.5; // slightly tighter than hero guards
    for (let i = 0; i < n; i++) {
      const g = cit.guards[i];
      if (g.state === 'attacking' || g.moraleState === 'broken') continue;
      const angle = (Math.PI * 2 * i) / n;
      const tx = cit.x + Math.cos(angle) * guardRadius;
      const ty = cit.y + Math.sin(angle) * guardRadius;
      // Move toward target position (same smooth movement as before)
      const dx = tx - g.x, dy = ty - g.y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist > TILE_SIZE * 0.5) {
        const speed = (g.speed || 2.5) * TILE_SIZE * dt * 0.85;
        if (dist <= speed) { g.x = tx; g.y = ty; }
        else { g.x += (dx/dist)*speed; g.y += (dy/dist)*speed; }
      }
    }
  }
}
```

### Citizen Selection UI
- Clicking a citizen during BUILD phase shows a small info panel:
  - Citizen name (auto-generated: "Citizen #3")
  - Current task: "Idle", "Farming food", "Mining stone at (45,120)"
  - Guards: "🛡️ 1/2 guards" with guard unit names
  - [Assign Guard] [Dismiss All] buttons (or G/D hotkeys)
- Selected citizen gets a highlight ring (gold border, like unit selection)

### Visual Indicators
- Citizens with guards show a small 🛡️ icon floating above them
- Guard units have a faint golden tether line to their citizen
- When guards engage enemies, the tether turns red briefly

---

## PHASE 4: CITIZEN ECONOMY REWORK
> **Priority: HIGH — gathering must work without hero**
> **Estimated lines modified: ~100**

### Current System
- Citizens auto-gather resources within `CITIZEN_GATHER_RADIUS` (10 tiles) of their settlement
- Hero can manually click deposits to gather (uses `HARVEST_RANGE` from hero)
- Citizens only gather inside settlement radius

### New System: Two Gathering Modes

#### Mode A: Auto-Farm (Inside City Limits)
- **No change needed** — citizens already auto-gather within settlement radius
- Remove the hero manual-click gathering entirely (`handleGather()` at line 5063)
- Citizens continue to gather wood/stone/food/metal from deposits near their settlement
- Priority cycling (click settlement → cycle resource priority) remains unchanged

#### Mode B: Assigned Mining (Outside City Limits)
- Player can **right-click a visible deposit** outside the settlement radius
- A citizen is dispatched to walk to that deposit and mine it
- The citizen will path through gates, walk to the deposit, mine it, then return
- Citizens assigned to external mining are **vulnerable** — guards recommended!

### Mining Assignment Flow
1. Player sees a metal deposit 40 tiles from base (revealed by scout)
2. Player right-clicks the deposit → "Assign miner" prompt
3. Nearest idle citizen gets `state='mining_external'` and paths to the deposit
4. Citizen mines the deposit (same gather timer as normal)
5. Citizen auto-returns to settlement with resources when deposit depleted or recall triggered
6. If enemies approach, citizen flees back (or guards defend)

### Data Model Changes
```javascript
// ADD to citizen:
citizen.externalTarget = null;     // {col, row} of assigned external deposit
citizen.carryingResources = {};    // resources gathered but not yet delivered
citizen.returnTrip = false;        // true when heading home with resources

// New citizen states:
// 'mining_external' — walking to / gathering at external deposit
// 'returning'       — carrying resources back to settlement
```

### handleGather() Rework
```javascript
// OLD: Hero clicks deposit within HARVEST_RANGE → instant gather
// NEW: Right-click deposit → assign citizen to mine it

function handleAssignMining(col, row) {
  const tile = map[col][row];
  const dep = DEPOSITS[tile];
  if (!dep) return;
  // Find nearest idle citizen
  const cit = findNearestIdleCitizen(col, row);
  if (!cit) { addFloat('No idle citizens!', col*TILE_SIZE, row*TILE_SIZE, '#ff6666'); return; }
  cit.externalTarget = {col, row};
  cit.state = 'mining_external';
  // Path citizen to target (full A* pathfinding)
  const path = findPath(cit.col, cit.row, col, row, true);
  if (!path) { addFloat('No path!', col*TILE_SIZE, row*TILE_SIZE, '#ff6666'); cit.state='idle'; cit.externalTarget=null; return; }
  cit.path = path;
  cit.pathIdx = 0;
  addFloat('⛏ Miner assigned', col*TILE_SIZE+TILE_SIZE/2, row*TILE_SIZE, '#7ab0d8');
}
```

### Resource Carrying & Delivery
- External miners carry resources in `citizen.carryingResources`
- Resources are only added to `game.resources` when the citizen returns to settlement
- This creates risk/reward: external mining is more productive but dangerous
- If a citizen dies while carrying, resources are lost (dropped as a small loot pile?)

---

## PHASE 5: UNIT-BASED FOG OF WAR
> **Priority: HIGH — exploration must work without hero**
> **Estimated lines modified: ~60**

### Current System
- `refreshFogVision()` runs every frame (line 1452)
- Calls `revealFogTracked(heroCol, heroRow, HERO_FOG_RADIUS, HERO_EXPLORE_RADIUS)`
- Hero has 6-tile VISIBLE radius, 20-tile EXPLORED radius
- Buildings have permanent `visionCount` (addStructureVision/removeStructureVision)
- Buildings use STRUCT_VIS_RADIUS (default 4) or per-building `visRadius`

### New System
- **Remove hero vision entirely** from `refreshFogVision()`
- **Add unit vision**: Each military unit reveals fog around its position
- Scouts excel at vision (large radius), soldiers have moderate vision
- Buildings remain unchanged (permanent visionCount system works great)

### Unit Vision Radii
```javascript
// ADD to UNIT_TYPES definitions:
const UNIT_VISION = {
  MILITIA:    { visRadius: 3, exploreRadius: 5 },
  ARCHER:     { visRadius: 4, exploreRadius: 6 },   // archers see further
  SPEARMAN:   { visRadius: 3, exploreRadius: 5 },
  CAVALRY:    { visRadius: 5, exploreRadius: 8 },   // mounted = better view
  CATAPULT:   { visRadius: 2, exploreRadius: 4 },   // slow, limited vision
  SCOUT:      { visRadius: 7, exploreRadius: 14 },  // future unit type — best explorer
};
```

### refreshFogVision() Rework
```javascript
function refreshFogVision() {
  fogFrameCounter++;
  decayFogVisible();
  
  // Unit vision (dynamic, moves with units)
  for (const u of units) {
    if (u.hp <= 0) continue;
    const uc = Math.floor(u.x / TILE_SIZE);
    const ur = Math.floor(u.y / TILE_SIZE);
    const vis = UNIT_VISION[u.type] || { visRadius: 3, exploreRadius: 5 };
    revealFogTracked(uc, ur, vis.visRadius, vis.exploreRadius);
  }
  
  // Citizen vision (very small — they can see what's right around them)
  for (const cit of citizens) {
    if (cit.safe) continue;
    const cc = Math.floor(cit.x / TILE_SIZE);
    const cr = Math.floor(cit.y / TILE_SIZE);
    revealFogTracked(cc, cr, 2, 3); // tiny radius
  }
}
```

### Performance Consideration
- Currently: 1 hero vision call per frame ✓
- New: N unit vision calls per frame (N = number of alive units)
- With 20 units, that's 20 calls to `revealFogTracked` per frame
- `revealFogTracked` iterates a circle of radius R → ~πR² tiles per call
- For radius 5: ~78 tiles × 20 units = ~1,560 tile checks per frame — **totally fine**
- For 50+ units, consider batching: only update unit vision every 3-5 frames

### Optimization: Stagger Unit Vision Updates
```javascript
let unitVisionFrame = 0;
function refreshFogVision() {
  fogFrameCounter++;
  decayFogVisible();
  
  // Stagger: update ~1/3 of units per frame for performance
  const STAGGER = 3;
  for (let i = unitVisionFrame % STAGGER; i < units.length; i += STAGGER) {
    const u = units[i];
    if (u.hp <= 0) continue;
    const uc = Math.floor(u.x / TILE_SIZE), ur = Math.floor(u.y / TILE_SIZE);
    const vis = UNIT_VISION[u.type] || { visRadius: 3, exploreRadius: 5 };
    revealFogTracked(uc, ur, vis.visRadius, vis.exploreRadius);
  }
  unitVisionFrame++;
}
```

### PLACE_HQ Phase (Map Exploration Before Settlement)
- Without hero, how does the player explore the map to choose a settlement spot?
- **Solution**: Start with a large revealed area (radius ~30 tiles from map center)
  and let the player pan around the revealed zone to pick their settlement location.
- After placing settlement, player must train scouts/units to explore further.

```javascript
// In init(), after map generation:
// Reveal starting area for settlement placement
const cx = Math.floor(COLS/2), cy = Math.floor(ROWS/2);
revealFog(cx, cy, 30); // large starting reveal
```

### Gameplay Impact
- **Early game**: Player can only see near their settlement + building vision
- **Must train scouts** to find distant resource deposits (metal, gold)
- **Lost units = lost vision** — if your forward patrol dies, fog returns
- Creates real strategic tension: do you send units out to explore or keep them home?

---

## PHASE 6: SOLDIER SIZE DECREASE
> **Priority: MEDIUM — quality of life fix**
> **Estimated lines modified: ~10**

### Problem
Soldiers are currently too big to easily pass through gates (1-tile wide).
Citizens pass through fine, but military units often get stuck.

### Current Constants (need to find exact values)
```javascript
// Unit rendering — these control visual + collision size:
const UNIT_CIRCLE_PX = 10;  // drawn circle radius in pixels
const UNIT_RADIUS = 0.35;   // collision radius as fraction of TILE_SIZE
```

### Proposed Changes
```javascript
// Decrease both visual and collision radius by ~20%
const UNIT_CIRCLE_PX = 8;     // was 10 → slightly smaller circle
const UNIT_RADIUS = 0.28;     // was 0.35 → fits through gates more easily

// Citizen size for reference (should remain unchanged):
// Citizens are drawn at ~6px radius — already small enough
```

### Gate Passthrough Fix
The real issue may be in `resolveUnitCollisions()` — when multiple units try to
pass through a gate simultaneously, they push each other into walls. Solutions:

1. **Reduce collision radius** (above) — units physically smaller
2. **Gate queue system**: Units approaching a gate single-file instead of bunching
3. **Temporarily disable collision** when inside a gate tile:
```javascript
function resolveUnitCollisions() {
  const minDist = TILE_SIZE * UNIT_RADIUS * 2;
  for (let i = 0; i < units.length; i++) {
    // Skip collision resolution if unit is on a gate tile
    const uCol = Math.floor(units[i].x / TILE_SIZE);
    const uRow = Math.floor(units[i].y / TILE_SIZE);
    const sk = uCol + ',' + uRow;
    if (structures[sk] && structures[sk].type === 'GATE') continue; // no pushing on gates
    // ... existing collision logic
  }
}
```

---

## PHASE 7: UI & HUD CLEANUP
> **Priority: MEDIUM — visual polish**
> **Estimated lines modified: ~50**

### HTML Elements to Remove
```html
<!-- DELETE: Hero HP bar -->
<div class="hero-hp-wrap">
  <span class="hero-hp-label">🤺</span>
  <div class="hp-bar"><div class="hp-fill" id="hero-hp-fill"></div></div>
  <span class="hp-text" id="hero-hp-text">50/50</span>
</div>

<!-- DELETE: Hero kills stat -->
<div class="kh-row kh-hero">
  <span class="kh-icon">⚔️</span>
  <span class="kh-label">Hero</span>
  <span class="kh-val" id="kh-hero">0</span>
</div>
```

### CSS to Remove
```css
.hero-hp-wrap { ... }  /* line 40 */
.kh-hero { ... }       /* line 300 */
#hero-hp-fill { ... }  /* line 326 */
```

### HUD Replacements
| Old Element | New Element |
|-------------|-------------|
| Hero HP bar | Settlement HP bar (or population count) |
| Hero kills stat | "Units Lost" or "Citizens Saved" counter |
| "⚔️ COMBAT — WASD move · Click attack" | "⚔️ COMBAT — Select & direct units · G=guard citizen" |
| "🏗️ BUILD — WASD move · Click to build" | "🏗️ BUILD — Click to build · Right-click assign miner" |

### New HUD Elements
```html
<!-- Population counter -->
<div class="pop-wrap">
  <span>👥</span>
  <span id="pop-count">0/0</span> <!-- citizens alive / total -->
</div>

<!-- Selected citizen info (shows when citizen clicked) -->
<div id="citizen-panel" style="display:none">
  <div class="panel-title">Citizen #3</div>
  <div>Task: Gathering wood</div>
  <div>Guards: 🛡️ 1/2</div>
  <button onclick="assignGuardToSelected()">G: Assign Guard</button>
  <button onclick="dismissSelectedGuards()">D: Dismiss</button>
</div>
```

### Hint Bar Updates (line 2952)
```javascript
// BUILD phase hint:
if(game.phase==='BUILD') {
  h.textContent = '🏗️ BUILD — Click build · Right-click mine · G=guard citizen · Space=start wave';
}
// COMBAT phase hint:
if(game.phase==='COMBAT') {
  const totalGuards = citizens.reduce((sum,c) => sum + (c.guards?c.guards.length:0), 0);
  h.textContent = '⚔️ COMBAT — Select units · Right-click move · G=guard · D=dismiss · ' + totalGuards + ' guards active';
}
```

### Game Over Screen (line 7251)
```javascript
// OLD: Hero Kills stat
// NEW: Replace with more god-game-relevant stats
`<div class="go-stat"><div class="go-stat-val">${game.citizensSaved||0}</div><div class="go-stat-label">Citizens Saved</div></div>`
`<div class="go-stat"><div class="go-stat-val">${game.unitsLost||0}</div><div class="go-stat-label">Units Lost</div></div>`
```

### Minimap Changes
```javascript
// OLD (line 7154): Draw hero as yellow dot
// mmCtx.fillStyle='#ffe066'; mmCtx.fillRect(hmc-2, hmr-2, 4, 4);

// NEW: Draw selected units as small blue dots, citizens as white dots
for (const u of units) {
  const ux = (u.x/TILE_SIZE)*sx, uy = (u.y/TILE_SIZE)*sy;
  mmCtx.fillStyle = u.selected ? '#64dcff' : '#88aacc';
  mmCtx.fillRect(ux-1, uy-1, 2, 2);
}
```

---

## PHASE 8: COMBAT REWORK (No Hero Attacks)
> **Priority: HIGH — game must be playable during waves**
> **Estimated lines modified: ~80**

### Current Combat Flow
1. Wave starts → enemies spawn from fog boundary
2. Player moves hero toward enemies
3. Player clicks → `heroAttack()` damages nearest enemy
4. Towers auto-fire, guards orbit hero and fight
5. Player manages hero survival (knockdown/revive)

### New Combat Flow (God Mode)
1. Wave starts → enemies spawn from fog boundary
2. Player watches from above, directs units via right-click
3. **NO player attack input** — all combat is automated (units, towers, guards)
4. Player's job: positioning units, assigning guards, managing formations
5. Danger: enemies reaching citizens/buildings, not hero

### Click Handler During Combat (line 5298)
```javascript
// OLD:
if(game.phase==='COMBAT'){heroAttack();return;}

// NEW: During combat, left-click selects units (like BUILD phase)
// Remove the heroAttack() call entirely.
// The existing unit selection (mousedown box-select) already works in COMBAT.
if(game.phase==='COMBAT'){
  // Click-select single unit, or click terrain to deselect
  // (existing box-select mousedown handler already works)
  return;
}
```

### Enemy Targeting (lines 3864-3890)
```javascript
// OLD: Enemies check hero as potential target
if(hero.stunTimer<=0){
  const hdx=hero.x-e.x, hdy=hero.y-e.y, hdSq=hdx*hdx+hdy*hdy;
  if(hdSq<=rangePx*rangePx&&hdSq<targetDist){targetDist=hdSq;targetX=hero.x;targetY=hero.y;target='hero';}
}

// NEW: Remove all hero targeting. Enemies target:
// 1. Nearest player unit (soldier)
// 2. Nearest citizen (if no soldiers nearby)
// 3. Nearest building/wall (if nothing else)
// The existing unit-targeting code already handles #1.
// ADD: citizen targeting for enemies that reach the base
```

### Enemy Attacks Hero (lines 3980-3984)
```javascript
// DELETE entirely — no hero to attack
if(hero.stunTimer<=0&&e.type!=='siegeRam'){
  const hdx=hero.x-e.x, hdy=hero.y-e.y;
  const heroDistSq=hdx*hdx+hdy*hdy;
  if(heroDistSq<(TILE_SIZE*1.3)*(TILE_SIZE*1.3)&&e.attackCooldown<=0){
    damageHero(eDef.dmg||3); e.attackCooldown=1/((eDef.atkRate||0.8));
  }
}
```

### Projectile Hero-Targeting (lines 4169-4171, 4257)
```javascript
// DELETE: heroTarget hit detection
if(p.heroTarget){
  if(hero.stunTimer<=0) damageHero(p.dmg);
}

// DELETE: projectile tracking to hero
if(p.heroTarget&&hero.stunTimer<=0){p.tx=hero.x;p.ty=hero.y;}
```

### Morale System: Hero Aura Replacement (lines 4679-4683, 4841-4843)
```javascript
// OLD: Units recover morale near hero (3-tile aura)
const MORALE_RECOVER_NEAR_HERO=10;
const HERO_MORALE_AURA=3;
if(hero.stunTimer<=0){
  const hdx=hero.x-ux, hdy=hero.y-uy;
  // recover morale if near hero
}

// NEW: Units recover morale near settlements (acts as "safe zone" aura)
const MORALE_RECOVER_NEAR_SETTLEMENT = 8;
const SETTLEMENT_MORALE_AURA = 5; // tiles
// Check distance to nearest settlement instead of hero
for (const k in structures) {
  if (structures[k].type !== 'CITIZEN_BLOCK') continue;
  const [sc, sr] = k.split(',').map(Number);
  const sdx = sc*TILE_SIZE - ux, sdy = sr*TILE_SIZE - uy;
  if (sdx*sdx + sdy*sdy < (SETTLEMENT_MORALE_AURA*TILE_SIZE)**2) {
    u.morale = Math.min(100, u.morale + MORALE_RECOVER_NEAR_SETTLEMENT * dt);
    break;
  }
}
```

### New: Enemies Can Attack Citizens
Since the hero is gone, enemies need something vulnerable to threaten.
Citizens become the high-value targets:

```javascript
// In updateEnemies():
// After checking for unit targets, also check for citizen targets
if (!target) {
  for (const cit of citizens) {
    if (cit.safe) continue; // inside settlement, invulnerable
    const cdx = cit.x - e.x, cdy = cit.y - e.y;
    const cDistSq = cdx*cdx + cdy*cdy;
    if (cDistSq < targetDist) {
      targetDist = cDistSq;
      targetX = cit.x; targetY = cit.y;
      target = cit; // track for damage
    }
  }
}

// Citizens can be killed (new mechanic!)
// When hit: citizen.hp -= dmg; if (citizen.hp <= 0) removeCitizen(cit);
// This makes guard assignment meaningful — unguarded citizens die.
```

### Citizen HP (New)
```javascript
// ADD to createCitizen():
citizen.hp = 10;
citizen.maxHP = 10;
citizen.hitFlash = 0;
```

---

## PHASE 9: GAME OVER CONDITION
> **Priority: MEDIUM — needed for playability**
> **Estimated lines added: ~20**

### Current System
- No game over — hero revives after 10s knockdown
- Game technically runs forever (infinite survival)

### New System: Settlement Destruction = Game Over
- Each settlement (CITIZEN_BLOCK) has HP (already exists: `s.hp`)
- When ALL settlements are destroyed → **GAME OVER**
- Losing one settlement is a major blow (lose citizens, lose build radius)
- But as long as one settlement survives, the empire lives

```javascript
function checkGameOver() {
  // Count surviving settlements
  let settlements = 0;
  for (const k in structures) {
    if (structures[k].type === 'CITIZEN_BLOCK') settlements++;
  }
  if (settlements === 0 && hqPlaced) {
    // All settlements destroyed — GAME OVER
    game.phase = 'GAMEOVER';
    showGameOverScreen();
  }
}

// Call in game loop after updateEnemies()
// Also call when a structure is destroyed
```

### Alternative: Population-Based Game Over
- Track total living citizens
- If ALL citizens die → game over (even if buildings stand, no one's home)
- This is more thematic for god-game: "Your people have perished"

```javascript
function checkGameOver() {
  if (!hqPlaced) return;
  const aliveCitizens = citizens.filter(c => !c.dead).length;
  const settlements = Object.values(structures).filter(s => s.type === 'CITIZEN_BLOCK').length;
  if (settlements === 0 || aliveCitizens === 0) {
    game.phase = 'GAMEOVER';
    showGameOverScreen();
  }
}
```

### Recommendation: Use BOTH conditions
- All settlements destroyed OR all citizens dead = game over
- This gives two failure paths that both feel meaningful

---

## FULL HERO CODE AUDIT (Every Reference)
> Complete line-by-line listing of every hero reference in the codebase.

### CSS (lines 1-600)
| Line | Code | Action |
|------|------|--------|
| 40 | `.hero-hp-wrap { display: flex; ... }` | DELETE |
| 300 | `.kh-hero { color: #ffe066; }` | DELETE |
| 326 | `#hero-hp-fill { width: 100%; ... }` | DELETE |

### HTML (lines 400-620)
| Line | Code | Action |
|------|------|--------|
| 417-420 | Hero HP bar div (`hero-hp-wrap`) | DELETE — replace with population counter |
| 575 | Hero kills stat row (`kh-hero`) | DELETE — replace with "Citizens Saved" |

### Constants (lines 640-720)
| Line | Code | Action |
|------|------|--------|
| 658 | `HERO_SPEED=8*TILE_SIZE` | DELETE |
| 659 | `HARVEST_RANGE=14, BUILD_RANGE=30` | KEEP `HARVEST_RANGE` as citizen gather radius; REPLACE `BUILD_RANGE` with settlement tier system |
| 660 | `HERO_ATK_DMG=8, HERO_ATK_RATE=0.4, HERO_ATK_RANGE=1.2*TILE_SIZE` | DELETE |
| 661 | `HERO_KNOCKDOWN_TIME=10, HERO_REVIVE_PCT=0.25` | DELETE |

### Fog of War (lines 1340-1465)
| Line | Code | Action |
|------|------|--------|
| 1343 | `HERO_FOG_RADIUS=6` | DELETE |
| 1344 | `HERO_EXPLORE_RADIUS=20` | DELETE |
| 1349 | Comment: "hero/HQ vision decay" | UPDATE comment |
| 1452 | Comment: "hero only" | UPDATE to "units only" |
| 1459-1461 | `const hc=heroCol()...revealFogTracked(hc,hr,...)` | REPLACE with unit vision loop (Phase 5) |

### Settlement Panel / Guard Upgrade (lines 920-970)
| Line | Code | Action |
|------|------|--------|
| 925 | `const gLvl = hero.guardLevel \|\| 0` | REWORK — guard tier system on settlement |
| 956 | `const nextLvl = (hero.guardLevel \|\| 0) + 1` | REWORK |
| 961 | `addFloat("Can't afford!", hero.x, hero.y...)` | CHANGE to settlement position |
| 966 | `hero.guardLevel = nextLvl` | REWORK — store on settlement |
| 967-968 | Float + particles at hero pos | CHANGE to settlement position |

### Game State (lines 2680-2710)
| Line | Code | Action |
|------|------|--------|
| 2683-2693 | `const hero={x, y, hp, maxHP, ...}` | DELETE entire object |
| 2702 | `let heroGuards = []` | DELETE |

### Spawn Ring (lines 2770-2775)
| Line | Code | Action |
|------|------|--------|
| 2771-2773 | `heroDist` calculation for spawn boundary | DELETE — use settlement distance only |

### Hint Bar (line 2952)
| Line | Code | Action |
|------|------|--------|
| 2952 | COMBAT hint: "WASD move · Click attack · G=dismiss guard" | REWRITE for god mode |

### Camera (lines 3000-3015)
| Line | Code | Action |
|------|------|--------|
| 3002 | Comment: "hero walks around" | UPDATE |
| 3005 | Comment: "Camera follows hero" | DELETE |
| 3007-3008 | `cam.tx=hero.x-...; cam.ty=hero.y-...` | REPLACE with free-cam (Phase 1) |

### Wave System (lines 3230-3630)
| Line | Code | Action |
|------|------|--------|
| 3239 | `addFloat('exposed citizens', hero.x, hero.y...)` | CHANGE to settlement/camera center |
| 3289-3290 | `hero.hp=hero.maxHP; hero.stunTimer=0` | DELETE (hero reset between waves) |
| 3622 | `addFloat('respawned', hero.x, hero.y...)` | CHANGE to settlement position |
| 3626-3627 | `addFloat('resources', hero.x, hero.y...)` | CHANGE to settlement/camera center |

### Combat System (lines 3780-3840)
| Line | Code | Action |
|------|------|--------|
| 3781-3805 | `heroAttack()` function | DELETE entirely |
| 3806-3819 | Hero cooldown/stun/flash tick | DELETE entirely |
| 3824-3837 | `damageHero(dmg)` function | DELETE entirely |

### Enemy AI (lines 3860-3990)
| Line | Code | Action |
|------|------|--------|
| 3864-3870 | Enemy target check: hero as target | DELETE hero check |
| 3887 | `heroTarget: target==='hero'` | DELETE |
| 3889 | `target==='hero'?null:target` | SIMPLIFY |
| 3980-3984 | Enemy melee attack on hero | DELETE |

### Projectile System (lines 4160-4260)
| Line | Code | Action |
|------|------|--------|
| 4169-4171 | `if(p.heroTarget) damageHero(p.dmg)` | DELETE |
| 4257 | Projectile tracking to hero position | DELETE |

### Morale System (lines 4679-4850)
| Line | Code | Action |
|------|------|--------|
| 4679 | `MORALE_RECOVER_NEAR_HERO=10` | REPLACE with `MORALE_RECOVER_NEAR_SETTLEMENT` |
| 4683 | `HERO_MORALE_AURA=3` | REPLACE with `SETTLEMENT_MORALE_AURA=5` |
| 4841-4843 | Morale recovery near hero check | REPLACE with settlement proximity check |

### Input / Control Groups (lines 4960-4970)
| Line | Code | Action |
|------|------|--------|
| 4964 | `addFloat('Group saved', hero.x, hero.y...)` | CHANGE to camera center |

### Touch Controls (lines 5016-5017)
| Line | Code | Action |
|------|------|--------|
| 5016 | `touchHeroX=hero.x; touchHeroY=hero.y` | REPLACE with camera pan |
| 5017 | `hero.x=touchHeroX+...; hero.y=touchHeroY+...` | REPLACE with camera pan |

### Hero Movement (lines 5020-5062)
| Line | Code | Action |
|------|------|--------|
| 5020-5021 | `heroCol()`, `heroRow()` | DELETE |
| 5024-5027 | `clampHero()` | DELETE |
| 5029-5042 | `heroCanWalkTo()` | DELETE |
| 5046-5062 | `updateHero(dt)` | DELETE (WASD now moves camera) |

### Gather / Build Range Checks (lines 5070-5270)
| Line | Code | Action |
|------|------|--------|
| 5071 | `dist=Math.abs(col-heroCol())+Math.abs(row-heroRow()); if(dist>HARVEST_RANGE)` | REWORK — citizen auto-gather, no hero range |
| 5161 | `dist=Math.abs(col-heroCol())+Math.abs(row-heroRow())` in handleBuild | REPLACE with settlement radius check |
| 5267-5268 | "Must be in hero range" + distance check | REPLACE with settlement radius |

### Click Handler (lines 5280-5335)
| Line | Code | Action |
|------|------|--------|
| 5298 | `if(game.phase==='COMBAT'){heroAttack();return;}` | DELETE heroAttack; allow unit selection in combat |

### Right-Click / Guard Assignment (lines 5395-5510)
| Line | Code | Action |
|------|------|--------|
| 5397-5399 | Right-click hero to assign guards | REPLACE with citizen guard system |
| 5447-5465 | `assignGuards()` function | REWORK → `assignGuardsToCitizen()` |
| 5469-5479 | `dismissGuards()` function | REWORK → `dismissCitizenGuards()` |
| 5482-5498 | `updateHeroGuards(dt)` | REWORK → `updateCitizenGuards(dt)` |

### Minimap Click (lines 5575-5580)
| Line | Code | Action |
|------|------|--------|
| 5577-5578 | `hero.x=...; hero.y=...; clampHero()` | REPLACE with camera jump |

### Hero Rendering (lines 6675-6760)
| Line | Code | Action |
|------|------|--------|
| 6675-6760 | Entire `drawHero` section (~85 lines) | DELETE entirely |

### Ghost Preview Build Range (line 6832)
| Line | Code | Action |
|------|------|--------|
| 6832 | `Math.abs(col-heroCol())+Math.abs(row-heroRow()))<=BUILD_RANGE` | REPLACE with settlement radius check |

### Minimap Hero Dot (line 7154)
| Line | Code | Action |
|------|------|--------|
| 7154 | `const hmc=(hero.x/TILE_SIZE)*sx, hmr=(hero.y/TILE_SIZE)*sy` | DELETE hero dot; add unit dots |

### HUD Update (lines 7180-7190)
| Line | Code | Action |
|------|------|--------|
| 7181-7186 | Hero HP bar fill + text update | DELETE |

### Game Init (lines 7220-7240)
| Line | Code | Action |
|------|------|--------|
| 7222-7234 | Hero spawn at random location + camera center | REPLACE: camera starts at map center, reveal starting area |

### Game Over Screen (line 7251)
| Line | Code | Action |
|------|------|--------|
| 7251 | `"Hero Kills"` stat | REPLACE with "Citizens Saved" or "Units Lost" |

### Game Reset (lines 7270-7280)
| Line | Code | Action |
|------|------|--------|
| 7272-7276 | Reset hero position, HP, stats, guardLevel, heroGuards | DELETE entirely |

### Kill Counter HUD (line 7341)
| Line | Code | Action |
|------|------|--------|
| 7341 | `document.getElementById('kh-hero').textContent=hero.kills` | DELETE |

### Fog Overlay Comment (line 7449)
| Line | Code | Action |
|------|------|--------|
| 7449 | Comment: "hero always visible" | UPDATE comment |

### Camera Init (line 7563)
| Line | Code | Action |
|------|------|--------|
| 7563 | Comment: "hero will be repositioned when HQ placed" | UPDATE comment |

### PLACE_HQ Comment (line 7578)
| Line | Code | Action |
|------|------|--------|
| 7578 | Comment: "hero is exploring" | UPDATE comment |

---

**TOTAL: ~130 lines of hero references across 65+ locations**
- **~200 lines to DELETE** (hero object, functions, rendering, combat)
- **~80 lines to MODIFY** (camera, fog, guards, range checks, UI, hints)
- **~180 lines to ADD** (free-cam, citizen guards, unit vision, citizen HP, mining)

---

## RISK ASSESSMENT & EDGE CASES

### 🔴 High Risk
1. **Camera system during PLACE_HQ**: Currently hero walks around to scout.
   Without hero, player needs enough revealed terrain + free cam to choose a spot.
   → Mitigation: Large starting reveal (30 tiles), free camera from start.

2. **Enemy pathfinding with no hero target**: Enemies currently path to hero as
   fallback when no structures in range. Without hero, enemies with nothing to
   target may idle in the field.
   → Mitigation: Enemies should path to nearest visible building or citizen.
   Fallback: path toward settlement center (BASE_CX, BASE_CY).

3. **Guard system complexity**: Citizens move, gather, flee, recall. Guards must
   follow through all these states. If citizen enters a gate, guard must fit too.
   → Mitigation: Guards use same pathfinding as units (A*, friendly=true).
   When citizen recalls, guards also return to settlement.

4. **Combat without player input may feel passive**: Player has nothing to click
   during waves except watch and reposition units.
   → Mitigation: Allow unit commands during combat (right-click move, formation
   drag). Make wave management more tactical: assign guards, send reinforcements,
   micro formations. Could add rally point mechanics later.

### 🟡 Medium Risk
5. **Fog of war with 0 units**: If player loses all military units, they have no
   dynamic vision at all. Buildings still provide permanent vision, but no exploration.
   → Mitigation: Settlement buildings provide decent vision. Player can train new
   scouts. Worst case: fog slowly reclaims but buildings prevent total blindness.

6. **External mining danger**: Citizens outside walls are extremely vulnerable.
   Without guards they will die in combat phases.
   → Mitigation: Auto-recall still triggers before waves. Players learn quickly
   to assign guards to external miners.

7. **Touch/mobile controls**: Hero drag was the only mobile input. Free camera
   pan via touch needs to work well.
   → Mitigation: Touch drag = camera pan. Pinch = zoom. Tap = select/build.

### 🟢 Low Risk
8. **Performance of unit vision**: 20-50 units updating fog each frame is fine.
   Stagger optimization available if needed.

9. **Build range change**: Settlement tier system already exists with buildRadius
   per tier. Just wire it up instead of hero BUILD_RANGE.

10. **Minimap changes**: Simple swap from hero dot to unit/citizen dots.

---

## BUILD ORDER & DEPENDENCIES

### Implementation Sequence (must be this order):

```
Phase 1: Free Camera ──────────────────────── [DO FIRST]
  │  Camera works independently of everything else.
  │  Game is playable (but weird) with free cam + hero still existing.
  │
Phase 2: Remove Hero Entity ───────────────── [DO SECOND]
  │  Delete hero object, movement, rendering, combat.
  │  Game will be "broken" momentarily (no vision, no gathering).
  │  This is intentional — phases 3-5 restore functionality.
  │
  ├── Phase 5: Unit-Based Fog ─────────────── [DO WITH Phase 2]
  │     Must be done alongside Phase 2 or the map goes dark.
  │     Restores exploration capability.
  │
  ├── Phase 8: Combat Rework ──────────────── [DO WITH Phase 2]
  │     Must be done alongside Phase 2 or combat breaks.
  │     Removes hero targeting from enemies.
  │
  └── Phase 9: Game Over ──────────────────── [DO WITH Phase 2]
        Need a new lose condition since hero can't die anymore.
        Simple check: all settlements destroyed = game over.

Phase 4: Citizen Economy ──────────────────── [DO THIRD]
  │  Rework gathering to be citizen-only.
  │  External mining assignment is the new "active" mechanic.
  │
Phase 3: Citizen Guard System ─────────────── [DO FOURTH]
  │  Requires citizen economy to be stable first.
  │  G/D keybinds, citizen selection, guard following.
  │
Phase 6: Soldier Size ────────────────────── [DO FIFTH]
  │  Quick constant tweak + gate collision fix.
  │  Independent of other phases but nice to do here.
  │
Phase 7: UI & HUD ────────────────────────── [DO LAST]
        Polish pass: remove hero UI, add population counter,
        update hints, clean up game over screen.
```

### Grouped Build Steps (for implementation)

**Step 1** (~2 hours): Phases 1 + 2 + 5 + 8 + 9
- Free camera + delete hero + unit fog + combat rework + game over
- These MUST be done together or the game breaks between steps
- After this step: game is playable as a god-mode RTS with basic functionality

**Step 2** (~1 hour): Phase 4
- Citizen economy rework (external mining)
- After this step: gathering works fully without hero

**Step 3** (~1.5 hours): Phase 3
- Citizen guard system (G/D assign, guard following, defend)
- After this step: guards protect citizens instead of hero

**Step 4** (~30 min): Phases 6 + 7
- Soldier size decrease + UI cleanup
- After this step: polished god-mode experience

### Total Estimated Effort: ~5 hours of implementation

---

## SUMMARY

| Metric | Value |
|--------|-------|
| Lines to DELETE | ~200 |
| Lines to MODIFY | ~80 |
| Lines to ADD | ~180 |
| Net line change | ~-40 (slightly smaller codebase) |
| Phases | 9 |
| Build steps | 4 |
| Critical path | Camera → Hero removal + Fog + Combat + GameOver |
| Biggest risk | Combat feeling too passive |
| Biggest win | True RTS/god-game feel, more strategic depth |

---

*Plan created: 2026-04-14*
*Game file: `/home/user/base-siege/index.html` (~7,600 lines)*
*GitHub: `FergusRi/base-siege`*
