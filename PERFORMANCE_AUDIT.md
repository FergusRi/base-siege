# 🔍 BASE SIEGE — Performance Audit & Enemy AI Visual Overhaul Discussion

## Pre-Implementation Efficiency Audit
**Date**: 2026-04-15
**Context**: Before implementing Hero Removal (Phase 0) + AI Empire (Phase 2), audit the ~7,605-line codebase for performance bottlenecks that will compound with the addition of AI entities.

---

## PART 1: PERFORMANCE BOTTLENECKS (Critical → Minor)

---

### 🔴 CRITICAL #1: O(n²) Unit Collision Resolution (Line 4316)
```
resolveUnitCollisions() — nested loop: every unit vs every unit
```
**Current**: With 20 player units, this is 190 comparisons/frame. Manageable.
**After AI**: With 20 player + 30 AI units = 50 entities → **1,225 comparisons/frame**.
With 100+ total entities (late game) → **~5,000 comparisons/frame**.

**FIX**: Spatial hash grid. Divide the map into cells (e.g., 4×4 tiles). Only compare units in the same or adjacent cells. Reduces from O(n²) to ~O(n).

```javascript
// Proposed: Spatial hash (add before resolveUnitCollisions)
const CELL_SIZE = 4 * TILE_SIZE; // 128px cells
function buildSpatialHash(entities) {
  const grid = {};
  for (const e of entities) {
    const cx = Math.floor(e.x / CELL_SIZE);
    const cy = Math.floor(e.y / CELL_SIZE);
    const key = cx + ',' + cy;
    if (!grid[key]) grid[key] = [];
    grid[key].push(e);
  }
  return grid;
}
```

---

### 🔴 CRITICAL #2: O(n²) Spearman Zone of Control (Lines 4459-4468)
```
Every spearman checks every enemy every frame — another nested loop.
```
**Current**: 5 spearmen × 50 enemies = 250 checks/frame. OK.
**After AI**: If AI also has spearmen with ZoC, and there are 30+ enemies + 30+ AI units in range → this explodes.

**FIX**: Same spatial hash. Only check enemies in adjacent cells to each spearman.

---

### 🔴 CRITICAL #3: A* Pathfinding Called Per-Enemy on Repath (Lines 3643-3657, 3958, 4046-4048)
```
spawnEnemy() calls findPath() for every spawned enemy.
updateEnemies() calls findPath() when enemies reach end of path or need repath.
Siege Rams repath with 5% probability per frame.
```
**Current**: 50 enemies × findPath with 800,000 iteration cap = potential frame drops.
**After AI**: AI army of 30 units all pathfinding simultaneously = much worse.

**FIX**: 
1. **Path caching**: Enemies spawning from the same location heading to the same target can share a base path and offset slightly.
2. **Staggered repathing**: Don't repath all entities on the same frame. Spread across frames using modular index: `if (i % 10 === frameCount % 10) repath()`.
3. **Reduce iteration cap**: 800,000 is excessive. The map is 950×632 = ~600K tiles. Cap at 50,000 with a fallback "walk toward target" behavior.

---

### 🟡 IMPORTANT #4: Fog of War Recalculation (Lines 1456-1462)
```
refreshFogVision() runs EVERY frame:
  - decayFogVisible() iterates visibleTiles array
  - revealFogTracked() iterates a circle of (HERO_FOG_RADIUS)² tiles
```
**Current**: ~113 tiles checked per frame for hero vision. Fine.
**After AI**: If we add unit-based vision (replacing hero), and each of 30+ units reveals fog → 30 × 113 = **3,400+ tile checks/frame**.

**FIX**: 
1. **Throttle unit vision refresh** — every 5 frames, not every frame. Units move ~3px/frame, fog tiles are 32px. Vision doesn't need per-frame precision.
2. **Vision dirty flag per unit** — only recalculate when a unit moves to a new tile (integer position changed).
3. **Batch vision updates** — instead of per-unit fog loops, accumulate all unit positions and do one sweep.

---

### 🟡 IMPORTANT #5: findCitizenResource() — O(citizens × radius²) (Lines 2188-2233)
```
Each idle citizen scans a radius of up to 40 tiles (per-tier) every 0.5s.
Within that scan, checks ALL other citizens for "taken" status.
```
**Current**: 6 citizens × (80×80 tile area) × 6 citizen overlap checks = manageable.
**After AI**: AI doesn't have real citizens (abstract income), so this stays the same. BUT if we add more player settlements → more citizens → quadratic blowup.

**FIX**: Pre-compute a "claimed tiles" Set once per tick instead of checking all citizens per resource search.

---

### 🟡 IMPORTANT #6: checkFormations() Every Frame (Lines 4761-4787)
```
Shield Wall: For each melee unit, check distance to ALL other melee units.
Protected Fire: For each ranged unit, check ALL melee units.
```
**Current**: With 15 melee + 5 ranged = ~210 distance checks/frame.
**After AI**: If AI units also have formations, 30 melee + 10 ranged = ~900 checks/frame.

**FIX**: Only recalculate when units move to new tile positions (dirty flag), not every frame. Formations don't change at 60fps — they change when units reposition.

---

### 🟡 IMPORTANT #7: Morale System — O(units × enemies) (Lines 4807-4868)
```
updateMorale() loops all units, and for each unit counts nearby enemies (inner loop).
```
**Current**: 20 units × 50 enemies = 1,000 checks/frame.
**After AI**: 50 units × 80 enemies = 4,000 checks/frame.

**FIX**: Spatial hash (same one as collisions). Count enemies per cell, units query their cell.

---

### 🟢 MINOR #8: buildSpawnRing() — Heavy but Infrequent (Lines 2757-2819)
```
Scans a large radius around the base, checking fog + walkability + vision distance.
Inner loop: for each candidate tile, scans a checkR radius for visible tiles.
```
**Current**: Called when `spawnRingDirty` flag set (building placed/destroyed). Infrequent.
**After AI**: Could become more frequent if AI buildings trigger dirty flag. But still OK since it's event-driven, not per-frame.

**FIX**: No urgent fix needed. Already well-designed with caching + dirty flag.

---

### 🟢 MINOR #9: drawStructures() — Many Canvas API Calls (Lines ~5700-6500)
```
Every visible structure draws 5-15 canvas paths (fillRect, arc, beginPath, etc.)
With buildings scattered across the map, this is ~100+ draw calls per frame.
```
**After AI**: AI buildings add another ~15-20 structures → 30-50 more draw calls.

**FIX**: Not critical yet. Canvas can handle hundreds of draw calls. If it becomes an issue:
1. Cache building sprites to offscreen canvases (like tile chunks already do).
2. Only redraw buildings that changed (damage, construction).

---

### 🟢 MINOR #10: Minimap Terrain Cache — Good Pattern, Small Issue (Lines 7049-7081)
```
buildMinimapTerrain() rebuilds every time fog changes (fogChangeVersion).
Uses ImageData for fast pixel writes — good.
But iterates ALL 950×632 = 601,400 pixels.
```
**After AI**: Unit-based vision = more fog changes = more rebuilds.

**FIX**: Only rebuild the dirty region of the minimap, not the whole thing. Track fog change bounds.

---

### 🟢 MINOR #11: `structures` Object Iteration (Throughout)
```
for(const k in structures) — used ~20+ times across the codebase.
Object.entries(structures) — used ~10+ times.
```
**After AI**: AI structures add to this object. Every iteration scans all structures.

**FIX**: Maintain separate arrays/sets: `playerStructures`, `aiStructures`, `settlements`. O(1) lookup by faction.

---

### 🟢 MINOR #12: String Key Parsing — Micro-Optimization (Throughout)
```
key.split(',').map(Number) — used ~30+ times.
Creates garbage arrays every call.
```
**FIX**: Store col/row as properties on structure objects instead of parsing from keys.
```javascript
// Instead of: const [c, r] = key.split(',').map(Number);
// Store: structures[key] = { type, hp, ..., col: c, row: r };
```

---

## PART 2: DEAD CODE & CLEANUP TARGETS

### Code to DELETE (Hero Removal)
| Section | Lines | Description |
|---------|-------|-------------|
| Hero object | ~2683-2693 | `hero = { x, y, hp, ... }` |
| Hero combat | ~3780-3840 | `heroAttack()`, `updateHeroCombat()`, `damageHero()` |
| Hero movement | ~5020-5027 | `heroCol()`, `heroRow()`, `clampHero()` |
| Hero walk check | ~5029-5040 | `heroCanWalkTo()` |
| Hero rendering | ~6670-6760 | `drawHero()` (~85 lines) |
| Hero on minimap | ~7154 | White dot |
| Hero HP bar UI | ~7181-7186 | HP bar update |
| Hero guard system | ~2696-2702 | `GUARD_UPGRADES`, `heroGuards` |
| Camera hero-lock | ~3007-3008 | `cam.tx = hero.x - ...` |
| WASD hero movement | ~5920+ | `updateHero()` function |
| Hero fog reveal | ~1459-1461 | `refreshFogVision()` hero section |
| Hero morale aura | ~4842-4847 | Near-hero morale recovery |
| Hero targeting by enemies | ~3981-3990 | Adjacent hero attack checks |
| Hero targeting by archers | ~3868-3871 | Ranged hero targeting |
| Hero stats in game over | ~7251 | `hero.kills` display |

**Estimated savings**: ~200 lines deleted, reducing update loop work per frame.

### Redundant Code Patterns
1. **`updateHint()` calls `updateUnits(dt)`** (Line 2951) — This is a bug from earlier. `updateUnits` is called from the game loop; calling it from `updateHint` with an undefined `dt` is wrong. Should be removed.

2. **Duplicate `dismissStartScreen`** (Lines 7575-7586) — Overrides the original. Should be merged into one function.

3. **`findNearestSettlementTile()`** (Line 2157) — Just wraps `findNearestSettlement()`. Inline it.

4. **`nearestSettlement()`** (Line 1475) — Also wraps `findNearestSettlement()` with default fallback. Consolidate to one function.

5. **Double `keydown` listener for 'G' key** — One at line 4951, another at line 5006. Merge them.

6. **`waveSpawnSides` array** (Line 3079) — Only used for backward compat with preview text. Can be eliminated when refactoring spawn system.

---

## PART 3: ENEMY AI VISUAL OVERHAUL — Discussion

### Current State: Two Different Rendering Systems

**Player Units** (`drawUnits()` ~Lines 6400-6550):
- Rendered as **circles** with letter icons (M, A, S, C, K)
- Color-coded by unit type (blue=Militia, green=Archer, etc.)
- Selection ring, HP bar, morale bar, rank stars, formation glow
- Guard badge, starving indicator, charge-ready flash

**Wave Enemies** (`drawEnemies()` ~Lines 6560-6658):
- Rendered as **rectangles/squares** with letter icons
- Color from `ENEMY_TYPES[type].color` (all reds/browns)
- Hit flash, HP bar (wider/shorter), buff glow ring
- No rank, no morale, no selection

### Proposed: Unified Rendering for AI Military Units

AI military units should **look exactly like player units but in RED**:
```
Player Militia:  [Blue circle] M  → with blue selection ring
AI Militia:      [Red circle]  M  → with red faction ring

Player Archer:   [Green circle] A → green
AI Archer:       [Red-tinted circle] A → darker red-green

Player Cavalry:  [Brown circle] C → brown
AI Cavalry:      [Red circle] C → red-brown
```

### Implementation Approach: Faction Color System

Instead of hardcoded colors, add a **faction tint layer**:

```javascript
const FACTIONS = {
  PLAYER: { primary: [70, 130, 200], accent: [100, 200, 255], ring: 'rgba(100,200,255,0.5)' },
  AI:     { primary: [200, 60, 50],  accent: [255, 80, 60],  ring: 'rgba(255,80,60,0.5)' },
  FERAL:  { primary: [160, 100, 60], accent: [200, 120, 70], ring: 'rgba(200,120,70,0.5)' },
};
```

**Player units** use their `UNIT_TYPES[type].color` (no change).
**AI units** use the same `UNIT_TYPES[type].color` but with a red overlay/tint:
```javascript
function getFactionColor(baseColor, faction) {
  const [r, g, b] = baseColor;
  if (faction === 'AI') {
    // Shift toward red: boost R, reduce G/B
    return [Math.min(255, r + 80), Math.max(30, g - 40), Math.max(30, b - 40)];
  }
  return baseColor; // player: unchanged
}
```

### What Needs to Change for Unified Rendering

1. **Add `faction` property to all entities**:
   - Player units: `faction: 'PLAYER'`
   - AI units: `faction: 'AI'`
   - Wave enemies: `faction: 'FERAL'` (keep distinct look — wild horde, not organized army)

2. **Merge `drawUnits()` to handle both player and AI units**:
   - Same circle + letter rendering
   - Different faction ring color (blue vs red)
   - AI units get rank stars too (visual consistency)
   - AI units do NOT show selection ring (can't select enemy units)

3. **Keep `drawEnemies()` separate for wave enemies**:
   - Feral enemies stay as rectangles — they're a different threat type
   - This visual distinction helps players tell "wave threat" vs "AI threat" at a glance
   - Matches the plan: waves are feral hordes, AI is an organized empire

4. **Unified unit array with faction filtering**:
   ```javascript
   // Instead of separate arrays:
   const allUnits = [];  // player + AI units in one array
   // Filter by faction when needed:
   const playerUnits = allUnits.filter(u => u.faction === 'PLAYER');
   const aiUnits = allUnits.filter(u => u.faction === 'AI');
   ```
   BUT: Pre-filter once per frame, not per-function. Cache into `_playerUnits` / `_aiUnits`.

5. **Shared combat/pathfinding code**:
   - AI units use the same `findPath()`, same collision resolution
   - AI units fight player units using the same `damageUnit()` system
   - Formation bonuses only apply to same-faction groups

### Visual Differentiation Checklist
| Element | Player | AI | Wave (Feral) |
|---------|--------|----|--------------|
| Shape | Circle | Circle | Rectangle |
| Letter | Unit type letter | Same letter | Enemy type letter |
| Base color | Unit type color | Red-tinted | Red/brown |
| Selection ring | Blue glow | ❌ None | ❌ None |
| HP bar | Green-yellow-red | Same but above red ring | Simpler bar |
| Rank stars | ★ Gold | ★ Red | ❌ None |
| Morale bar | Yes | Hidden (AI doesn't show morale) | ❌ None |
| Faction ring | Blue halo | Red halo | None |
| Death effect | Blue particles | Red particles | Red-brown particles |
| Minimap dot | Unit type color | Red dot | Red dot (smaller) |

---

## PART 4: RECOMMENDED IMPLEMENTATION ORDER

Given the bottlenecks above, here's the optimal order:

### Pre-Phase 0: Performance Foundation (Do First!)
1. **Add spatial hash utility** — used by collisions, ZoC, morale, formation checks
2. **Add faction property to unit creation** — future-proof all units
3. **Throttle fog vision to tile-change events** — prepare for unit-based vision
4. **Stagger pathfinding across frames** — essential before adding 30+ AI units
5. **Cache `claimed tiles` set for citizens** — minor but easy win
6. **Fix `updateHint()` calling `updateUnits(dt)` bug** — remove it
7. **Store col/row on structure objects** — eliminate string parsing

### Phase 0: Hero Removal (As Planned)
- Delete ~200 lines of hero code
- Convert camera to free-move (WASD/edge pan)
- Convert fog to unit-based vision (with throttling from step 3)
- Net reduction: ~200 lines deleted, ~100 added = **~100 line reduction**

### Phase 1: Wave Enhancement (As Planned)
- New enemy types (reuse existing renderer — they stay as rectangles)
- Boss waves
- Endless scaling

### Phase 2: AI Empire (The Big One)
- AI units use unified renderer (circles, red tint)
- Shared `allUnits` array with faction filtering
- AI pathfinding uses staggered system
- AI buildings use separate `aiStructures` set for faster iteration

---

## PART 5: ENTITY COUNT BUDGET (Performance Targets)

| Entity Type | Current Max | Post-AI Target | 60fps Budget |
|-------------|-------------|----------------|--------------|
| Player units | ~20 | ~30 | ✅ |
| AI units | 0 | ~30-40 | ⚠️ Need spatial hash |
| Wave enemies | ~80 | ~100 | ⚠️ Need staggered pathing |
| Citizens | ~12 | ~15 | ✅ |
| AI citizens | 0 | 0 (abstract) | ✅ |
| Structures (player) | ~30 | ~40 | ✅ |
| Structures (AI) | 0 | ~15-20 | ✅ |
| Projectiles | ~20 | ~30 | ✅ |
| Particles | ~100 | ~150 | ✅ |
| **TOTAL ENTITIES** | **~270** | **~440** | **Need optimizations** |

### The 60fps Line
Canvas can typically handle ~500 draw calls/frame at 60fps on modern hardware.
With ~440 entities, each drawing 3-5 shapes = ~1,500-2,200 draw calls.
This is borderline. The spatial hash + staggered pathing are **required**, not optional.

---

## SUMMARY: Top 5 Actions Before Any Code Changes

1. 🔴 **Spatial hash grid** — eliminates ALL O(n²) loops (collisions, ZoC, morale, formations)
2. 🔴 **Stagger pathfinding** — spread A* calls across frames, reduce iteration cap
3. 🟡 **Throttle fog updates** — per-tile-change, not per-frame
4. 🟡 **Faction property on entities** — foundation for AI vs player rendering
5. 🟢 **Delete hero code** — ~200 lines of dead code gone, cleaner update loop
