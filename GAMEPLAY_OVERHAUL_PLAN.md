# Base Siege — Gameplay Overhaul Plan
**Date:** 2026-04-13  
**Status:** ✅ APPROVED — ready for implementation

---

## Overview

Three interconnected changes that shift the game from "turtle & spam" to
"expand & defend":

| # | Change | One-liner |
|---|--------|-----------|
| A | **Resource Buildings** | Citizens build & repair mines/farms on resource tiles; resource chain gates progression |
| B | **Enemy Building Targeting** | Enemies attack the *nearest* player structure, not just the base |
| C | **Multi-Resource Upkeep** | Army upkeep costs multiple resources, forcing expansion |

These create a strategic triangle:
> You NEED resource buildings to fund an army →  
> resource buildings attract enemies →  
> you NEED an army to protect resource buildings.

---

## A — Resource Buildings

### A1. Resource Chain

Buildings unlock in a chain — each requires the *previous* resource to build:

| # | Structure | Built On | Build Cost | Production | Letter |
|---|-----------|----------|------------|------------|--------|
| 1 | **Farm** | `BERRY` tile | **Free** | +3 food/wave | `F` |
| 2 | **Lumber Camp** | `TREE` tile | `{food:10}` | +3 wood/wave | `L` |
| 3 | **Quarry** | `STONE` tile | `{wood:15}` | +3 stone/wave | `Q` |
| 4 | **Mine** | `ORE` tile | `{stone:20}` | +3 metal/wave | `M` |
| 5 | **Gold Mine** | `GOLD` tile | `{metal:25}` | +3 gold/wave | `$` |

> **Chain logic**: food is free → food buys wood → wood buys stone →
> stone buys metal → metal buys gold. Each tier requires expanding
> further from base to find the next resource.

All buildings produce **3 resources per wave** (uniform, easy to reason about).

### A2. Building HP & Damage Model

Resource buildings use a real HP system (not hit-count):

| Structure | HP |
|-----------|----|
| Farm | 25 |
| Lumber Camp | 30 |
| Quarry | 35 |
| Mine | 40 |
| Gold Mine | 40 |

- Enemies deal their normal damage to buildings (same as vs walls/towers).
- When HP reaches **0** → building is **destroyed**.
  - Production stops immediately.
  - Visual changes to **cracked/destroyed** sprite (darker, broken overlay).
  - Building remains on the tile in its destroyed state.

### A3. Repair System

- **Repairable up to 3 times**. Each building tracks `repairsUsed: 0` (max 3).
- **Repair cost = full original build cost** each time.
  - Farm repair: free (it was free to build).
  - Lumber Camp repair: `{food:10}`.
  - Quarry repair: `{wood:15}`.
  - Mine repair: `{stone:20}`.
  - Gold Mine repair: `{metal:25}`.
- After **3 repairs used**, the next time HP reaches 0 → building is
  **permanently destroyed**. Tile reverts to depleted variant
  (`T.TREE_DEPLETED`, etc.) — resource spot gone forever.
- **Citizens handle repairs** (see A4). Player schedules a repair job the
  same way they schedule a build job.

### A4. Citizen Builder & Repair System

Citizens shift from gatherers to **builders and repairers**:

**Build cycle:**
1. Player clicks a resource tile anywhere on the map → **build job is scheduled**
   (ghost/blueprint appears on the tile).
2. When a citizen becomes free, it **claims the nearest queued job** and walks
   to the site — no matter where on the map.
3. Citizen arrives → 3-second build timer → building complete.
4. Citizen returns to nearest settlement (or claims next job if queue isn't empty).

**Repair cycle:**
1. When a building is destroyed (HP=0, cracked visual), player can click it
   to **schedule a repair job** (if `repairsUsed < 3`).
2. A free citizen claims the repair job, walks to the building.
3. Citizen arrives → 3-second repair timer → HP fully restored,
   `repairsUsed++`.
4. Citizen returns to nearest settlement.

**Citizen rules:**
- Citizens still spawned by settlements (unchanged).
- `CITIZEN_UPKEEP_RATE` stays at 0.5 food/citizen/wave.
- Citizens can be killed if caught outside during a wave.
- Gather priority per settlement is **removed** (no longer relevant).
- **Job queue is global** — any free citizen from any settlement can claim
  any pending build/repair job.
- Jobs are claimed nearest-first (citizen picks the closest available job).

### A5. Building Walkability

- **Resource buildings are walkable** — they do NOT block pathing.
- Enemies target buildings (pathfind to them, attack when adjacent) but can
  walk through the tile.
- This prevents exploits where players use cheap farms as free walls.
- Walls, gates, towers, and settlements remain solid (block pathing as before).

### A6. Economy Rebalance

**No free wave bonus.** All resources come from buildings only.

| Resource | Old Source | New Source |
|----------|-----------|-----------|
| Food | Citizens + wave bonus | Farms only (+3/wave each) |
| Wood | Citizens + wave bonus | Lumber Camps only (+3/wave each) |
| Stone | Citizens | Quarries only (+3/wave each) |
| Metal | Citizens | Mines only (+3/wave each) |
| Gold | Citizens | Gold Mines only (+3/wave each) |

**Starting resources adjusted:**
```js
INITIAL_RESOURCES = {wood:100, stone:50, metal:30, food:50, gold:0};
```
Slightly more than current `{80, 45, 25, 35, 0}` to compensate for needing
to build farms/lumber camps before any income flows.

### A7. Map Rework — Natural Terrain

Complete overhaul of map generation to create natural-feeling terrain:

**Biome zones** (Perlin noise + distance from center):
- **Plains** (near center): Flat grass, scattered berry bushes → Farm sites.
- **Forests** (mid-range): Dense tree clusters with clearings → Lumber Camp sites.
- **Mountains** (outer ring): Rocky terrain with stone/ore deposits clustered
  on slopes → Quarry and Mine sites.
- **River/water features**: Winding rivers across the map (impassable, create
  natural chokepoints).
- **Gold deposits**: Rare, always far from center (map edges/corners), often
  in dangerous mountain passes → high risk/reward.

**Key design goals:**
- Resources naturally get rarer and further from center as you go up the chain.
- Mountain ranges create natural walls and chokepoints.
- Forests provide visual cover (fog-like feel even when explored).
- Berry bushes near spawn make early Farms easy to reach.
- Gold at edges forces maximum expansion for late-game economy.

---

## B — Enemy Building Targeting

### B1. New Targeting Priority

Currently enemies pathfind to `nearestSettlement()`. New priority chain:

```
1. If adjacent to a player unit → attack it (30% chance, unchanged)
2. If adjacent to hero → attack hero (unchanged)
3. Pathfind to NEAREST player structure (any type)
   - Resource buildings, walls, gates, towers, settlements
   - "Nearest" = shortest Manhattan distance from current position
```

### B2. Enemy Type Behavior Matrix

| Enemy Type | Primary Target | Structure Damage | Notes |
|------------|---------------|-----------------|-------|
| **Raider** | Nearest structure | `baseDmg` (5) | Generalist |
| **Runner** | Nearest structure | `baseDmg` (3) | Fast, will rush exposed farms |
| **Swarm** | Nearest structure | `baseDmg` (2) | Zerg rush on outer buildings |
| **Brute** | Nearest WALL/GATE → then nearest | `dmg*2` (16) vs walls, `baseDmg` (10) vs others | Wall smasher |
| **Siege Ram** | Nearest structure | `structDmg` (20) | Already targets structures |
| **Enemy Archer** | Nearest unit in range → nearest structure | `baseDmg` (3) | Ranged harass |
| **Warchief** | Nearest structure (buffs nearby) | `baseDmg` (7) | Buffs other enemies |

### B3. Pathfinding Changes

**Replace** `nearestSettlement()` with `nearestPlayerStructure()`:
```js
function nearestPlayerStructure(ec, er) {
  let best = null, bestDist = Infinity;
  for (const [key, s] of Object.entries(structures)) {
    const [c, r] = key.split(',').map(Number);
    const d = Math.abs(ec - c) + Math.abs(er - r);
    if (d < bestDist) { bestDist = d; best = {c, r}; }
  }
  return best || {c: BASE_CX, r: BASE_CY};
}
```

**Re-pathing**: Enemies re-evaluate target every 3–5 seconds (or when current
target is destroyed).

### B4. Spawn Ring + Vision Implications

Resource buildings grant a small vision radius (4 tiles). Outer buildings
extend the vision boundary → enemies spawn near them → natural risk/reward.

### B5. Wave Notification

When enemies target an outer building, flash a warning on the minimap +
"⚠ Building under attack!" message.

---

## C — Multi-Resource Unit Upkeep

### C1. Updated Unit Costs & Upkeep

Unit recruitment costs and upkeep reworked to use the resource chain:

| Unit | Recruit Cost | Upkeep/Wave | Role |
|------|-------------|-------------|------|
| **Militia** | `{food:5, wood:3}` | `{food:1}` | Cheap frontline, food-only upkeep |
| **Archer** | `{wood:8, metal:3}` | `{food:1, metal:1}` | Ranged DPS, needs metal |
| **Spearman** | `{food:5, wood:5, metal:2}` | `{food:1, metal:1}` | Anti-cavalry, needs metal |
| **Cavalry** | `{food:8, wood:5, metal:5}` | `{food:2, metal:2}` | Fast heavy hitter, expensive |
| **Catapult** | `{wood:15, stone:8, metal:6}` | `{food:1, metal:3}` | Siege, metal-hungry |

> Militia stays food-only upkeep (peasant levies). Everything else needs metal
> → forces players to build and defend Mines.

### C2. Upkeep Data Structure

```js
// OLD: upkeep: 1  (single number = food)
// NEW:
upkeep: { food: 1, metal: 1 }  // object with per-resource costs
```

### C3. Updated payUpkeep()

```js
function payUpkeep() {
  const sorted = [...units].sort((a,b) => {
    const ra = a._lastRank || 0, rb = b._lastRank || 0;
    if (rb !== ra) return rb - ra;
    return totalUpkeep(b) - totalUpkeep(a);
  });
  const unfed = [];
  for (const u of sorted) {
    const cost = UNIT_TYPES[u.type].upkeep;
    let canPay = true;
    for (const [res, amt] of Object.entries(cost)) {
      if (game.resources[res] < amt) { canPay = false; break; }
    }
    if (canPay) {
      for (const [res, amt] of Object.entries(cost))
        game.resources[res] -= amt;
    } else {
      unfed.push(u);
    }
  }
  return unfed;
}
```

### C4. Starvation (unchanged)

- Unfed units lose 30 morale/wave → flee at 0 → can die.
- Now also triggers on metal shortage.

### C5. UI: Upkeep Display

Between-wave overlay shows: `Army Upkeep: 8 🍖  5 ⛏️`

---

## Implementation Order

### Phase 1: Resource Buildings + Citizens + Map (~500 lines)
1. Add 5 new tile types + structure definitions
2. Add "Resources" category tab to Build mode UI
3. Implement resource chain build costs & placement validation
4. Implement citizen build queue (schedule → claim → walk → build)
5. Implement citizen repair queue (schedule → claim → walk → repair)
6. Implement production ticking in `endWave()` — 3 per building per wave
7. Implement HP damage model + cracked/destroyed visual state
8. Implement repair system (full cost, max 3 repairs, then permanent death)
9. Make resource buildings walkable (not blocking pathing)
10. Remove free wave bonus
11. Remove citizen gathering AI (replace with builder/repairer AI)
12. Rework map generation — biomes, mountains, forests, rivers, gold at edges
13. Add building rendering (colored squares with letters, cracked overlay when destroyed)
14. Adjust starting resources
15. Test: full build→produce→damage→repair→destroy lifecycle

### Phase 2: Enemy Building Targeting (~100 lines)
1. Replace `nearestSettlement()` with `nearestPlayerStructure()`
2. Update all enemy movement code
3. Add re-targeting timer (3–5s)
4. Add "building under attack" minimap flash + notification
5. Test: enemies path to outer buildings, re-target when destroyed

### Phase 3: Multi-Resource Upkeep (~60 lines)
1. Change `upkeep` from number to object in UNIT_TYPES
2. Update recruit costs per new table
3. Update `payUpkeep()` for multi-resource
4. Update `getTotalUpkeep()` display
5. Update between-wave overlay + recruit tooltips
6. Test: metal shortage → starvation → need mines

### Phase 4: Balance Pass (~50 lines)
1. Playtest waves 1–10
2. Tune building output rates, build costs, HP values
3. Tune repair costs (full cost feels right?)
4. Tune unit recruit costs and upkeep amounts
5. Verify strategic triangle: expand → defend → upgrade → expand
6. Ensure resource chain pacing feels natural

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Early game too hard (no income until farms built) | Medium | High | Generous starting resources + farms are free to build |
| All enemies rush one building | Medium | Medium | Re-target timer + multiple spawn points |
| Metal upkeep makes army impossible | Low | High | Militia stays food-only as fallback |
| Citizen pathing across huge map is slow | Medium | Medium | Citizens use BFS (fast), visual feedback on walk |
| 3-repair limit feels unfair | Low | Medium | Farm repairs are free; expensive buildings have more HP |
| Map rework breaks existing balance | Medium | High | Test biome generation separately before integrating |

---

## Resolved Decisions

All open questions from the draft have been answered by Fergus:

| Question | Decision |
|----------|----------|
| Citizens: keep or remove? | **Keep** — citizens build AND repair buildings |
| Repair: allowed? | **Yes** — full build cost, up to 3 repairs per building |
| Building HP model? | **Real HP** — destroyed at 0 HP, shows cracked visual |
| Buildings block pathing? | **No** — walkable, enemies target but walk through |
| Wave bonus? | **Removed entirely** — all resources from buildings only |
| Resource production rate? | **3 per building per wave** (uniform) |
| Resource chain? | **Yes** — food(free)→wood→stone→metal→gold |
| Map rework? | **Yes** — natural biomes with mountains, forests, rivers |
| Build cycle? | **Schedule anywhere** → citizen claims when free → walks there |
