# Base Siege — Gameplay Overhaul Plan
**Date:** 2026-04-13  
**Status:** Draft — awaiting approval before implementation

---

## Overview

Three interconnected changes that shift the game from "turtle & spam" to
"expand & defend":

| # | Change | One-liner |
|---|--------|-----------|
| A | **Resource Buildings** | Citizens build mines/farms/lumber camps instead of hand-gathering |
| B | **Enemy Building Targeting** | Enemies attack the *nearest* player structure, not just the base |
| C | **Metal Upkeep for Units** | Army upkeep costs metal too, forcing expansion to ore |

These create a strategic triangle:
> You NEED resource buildings to fund an army →  
> resource buildings attract enemies →  
> you NEED an army to protect resource buildings.

---

## A — Resource Buildings (Mine / Farm / Lumber Camp)

### A1. New Structure Definitions

| Structure | Built On | Build Cost | HP | Production per Wave | Letter |
|-----------|----------|------------|----|---------------------|--------|
| **Lumber Camp** | `TREE` tile | `{wood:15, food:5}` | 30 | +4 wood | `L` |
| **Farm** | `BERRY` tile | `{wood:10, food:3}` | 25 | +5 food | `F` |
| **Quarry** | `STONE` tile | `{wood:15, stone:5}` | 35 | +3 stone | `Q` |
| **Mine** | `ORE` tile | `{wood:20, stone:10}` | 40 | +2 metal | `M` |
| **Gold Mine** | `GOLD` tile | `{wood:25, stone:10, metal:5}` | 40 | +1 gold | `$` |

> Costs are intentionally front-loaded so losing a building *hurts*.

### A2. Building Mechanics

- **Placement**: Hero clicks resource tile in Build mode → new "Resources"
  category tab alongside Defenses / Army.
- **Tile replacement**: The resource tile becomes the building tile (new tile
  types: `T.LUMBER_CAMP`, `T.FARM`, `T.QUARRY`, `T.MINE`, `T.GOLD_MINE`).
  Stored in `structures{}` like walls/towers.
- **Production**: At end of each wave (`endWave()`), iterate all resource
  buildings and add their output to `game.resources`.
- **Destruction**: 3-hit system (details in A3).
- **Vision**: Each resource building grants a small vision radius (4 tiles)
  so you can see enemies approaching.
- **Build range**: Same as other structures (`BUILD_RANGE = 30` Manhattan
  from hero). This naturally gates early expansion.
- **No limit**: You can build as many as you can afford and defend.

### A3. 3-Hit Destruction System

Resource buildings use a simplified damage model:

```
hitsTaken: 0          // starts at 0
MAX_HITS: 3           // destroyed after 3 enemy attacks
```

- Any enemy attack on a resource building increments `hitsTaken` by 1
  (regardless of damage amount — a swarm and a brute each count as 1 hit).
- At `hitsTaken === 3`: building is **permanently destroyed**. The tile
  reverts to its depleted variant (`T.TREE_DEPLETED`, etc.). It does NOT
  regrow — the resource spot is gone forever.
- Between waves, buildings do NOT auto-repair (unlike settlements which
  heal +10). This means damage accumulates across waves.
- **Optional repair action**: Hero can spend resources to repair a damaged
  building (50% of original build cost per hit restored). This gives the
  player agency without making buildings invulnerable.

### A4. What Happens to Citizens?

Citizens shift from gatherers to **builders/couriers**:

- Citizens still exist and are spawned by settlements.
- Instead of wandering to gather, citizens now handle **construction
  delivery**: when you place a resource building, the nearest idle citizen
  walks to the site and "builds" it (visual: hammering animation timer of
  3 seconds). Building only completes when citizen arrives.
- Between waves, citizens are idle at their settlement (safe).
- Citizens can still be killed if caught outside during a wave (exposed
  state is unchanged).
- `CITIZEN_UPKEEP_RATE` stays at 0.5 food/citizen/wave.
- Gather priority per settlement is **removed** (no longer relevant).

> **Alternative (simpler)**: Remove citizens entirely. Buildings place
> instantly like walls. This is simpler to implement and removes an entire
> system. The downside is losing the "settler" feel.  
> **Recommendation**: Go with instant placement (simpler). Citizens were
> only interesting because of gathering — without that, they're just a
> delay mechanic. Settlements still provide vision and army recruitment
> range.

### A5. Economy Rebalance

| Resource | Current Sources | New Sources |
|----------|----------------|-------------|
| Wood | Citizens gather TREE (2/harvest) + wave bonus | Lumber Camps (+4/wave) + wave bonus |
| Food | Citizens gather BERRY (3/harvest) + wave bonus | Farms (+5/wave) + wave bonus |
| Stone | Citizens gather STONE (2/harvest) | Quarries (+3/wave) |
| Metal | Citizens gather ORE (1/harvest) | Mines (+2/wave) |
| Gold | Citizens gather GOLD (1/harvest) | Gold Mines (+1/wave) |

**Wave bonus stays**: `2 + game.wave` wood and food (represents foraging/scavenging).

**Starting resources adjusted**:
```js
INITIAL_RESOURCES = {wood:100, stone:50, metal:30, food:50, gold:0};
```
Slightly more than current `{80, 45, 25, 35, 0}` to compensate for no
immediate citizen gathering.

**First build time stays at 300s (5 min)** — plenty of time to place
initial resource buildings and defenses.

---

## B — Enemy Building Targeting

### B1. New Targeting Priority

Currently enemies pathfind to `nearestSettlement()` (falls back to HQ).
The new priority chain for **standard enemies** (raiders, runners, swarm,
warchiefs):

```
1. If adjacent to a player unit → attack it (30% chance, unchanged)
2. If adjacent to hero → attack hero (unchanged)
3. Pathfind to NEAREST player structure (any type)
   - Resource buildings, walls, gates, towers, settlements, HQ
   - "Nearest" = shortest Manhattan distance from spawn/current position
```

### B2. Enemy Type Behavior Matrix

| Enemy Type | Primary Target | Structure Damage | Notes |
|------------|---------------|-----------------|-------|
| **Raider** | Nearest structure | `baseDmg` (5) per hit | Generalist |
| **Runner** | Nearest structure | `baseDmg` (3) per hit | Fast, fragile — will rush exposed farms |
| **Swarm** | Nearest structure | `baseDmg` (2) per hit | Zerg rush on outer buildings |
| **Brute** | Nearest WALL/GATE → then nearest structure | `dmg*2` (16) vs walls, `baseDmg` (10) vs others | Wall smasher, will pivot to buildings if no walls |
| **Siege Ram** | Nearest structure (unchanged) | `structDmg` (20) | Already targets structures |
| **Enemy Archer** | Nearest unit/hero in range → nearest structure | `baseDmg` (3) per hit | Ranged harass |
| **Warchief** | Nearest structure (buffs nearby) | `baseDmg` (7) per hit | Buffs other enemies |

### B3. Pathfinding Changes

**Replace** `nearestSettlement(eCol, eRow)` with `nearestPlayerStructure(eCol, eRow)`:
```
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

**Re-pathing**: Enemies re-evaluate their target every 3-5 seconds (or when
their current target is destroyed). This prevents all enemies from
converging on one building after another is destroyed.

### B4. Spawn Ring Implications

The proximity spawn ring already spawns enemies near the player's vision
boundary. With resource buildings granting vision (4 tiles), outer buildings
will attract spawns nearby → natural risk/reward for expansion.

### B5. Wave Notification Enhancement

When enemies target an outer building, flash a warning icon on the minimap
at the targeted structure's location. Brief "⚠ Building under attack!"
message.

---

## C — Metal Upkeep for Units

### C1. Updated Upkeep Costs

Currently ALL units cost only food for upkeep (`upkeep: 1` or `2` = food
per wave). New system adds metal upkeep for armored/equipped units:

| Unit | Current Upkeep | New Upkeep |
|------|---------------|------------|
| **Militia** | 1 food | 1 food |
| **Archer** | 1 food | 1 food, **1 metal** |
| **Spearman** | 1 food | 1 food, **1 metal** |
| **Cavalry** | 2 food | 2 food, **2 metal** |
| **Catapult** | 2 food | 1 food, **3 metal** |

> Militia stays food-only (peasant levies, cheap to maintain).  
> Metal upkeep represents weapon/armor maintenance.

### C2. Upkeep Data Structure Change

```js
// OLD: upkeep: 1  (single number = food)
// NEW:
upkeep: { food: 1, metal: 1 }  // object with per-resource costs
```

### C3. Updated payUpkeep() Logic

```
function payUpkeep() {
  // Sort: highest rank first, then highest total upkeep
  const sorted = [...units].sort((a,b) => {
    const ra = a._lastRank || 0, rb = b._lastRank || 0;
    if (rb !== ra) return rb - ra;
    const ua = totalUpkeep(a), ub = totalUpkeep(b);
    return ub - ua;
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

### C4. Starvation Effects (keep existing)

- Unfed units lose 30 morale per wave.
- At 0 morale → fleeing state → cannot attack → can die.
- This already works; just now it triggers on metal shortage too.

### C5. UI: Upkeep Display

The between-wave overlay already shows upkeep info. Update to show:
```
Army Upkeep: 8 🍖  5 ⛏️
```
(food icon + metal icon with amounts)

---

## Implementation Order

Execute in this order because each phase builds on the previous:

### Phase 1: Resource Buildings (Change A) — ~400 lines
1. Add 5 new tile types + structure definitions to STRUCTS
2. Add "Resources" category tab to Build mode UI
3. Implement placement validation (must be on matching resource tile)
4. Implement production ticking in `endWave()`
5. Implement 3-hit destruction system
6. Add building rendering (colored squares with letters)
7. Add repair action (hero click on damaged building)
8. Decide: keep citizens as builders OR remove citizen gathering entirely
9. Adjust starting resources
10. Test: can place buildings, they produce, enemies destroy them

### Phase 2: Enemy Building Targeting (Change B) — ~100 lines
1. Replace `nearestSettlement()` with `nearestPlayerStructure()`
2. Update all enemy movement code to use new targeting
3. Add re-targeting timer (re-evaluate every 3-5s)
4. Add "building under attack" minimap flash + notification
5. Test: enemies path to outer buildings, re-target when destroyed

### Phase 3: Metal Upkeep (Change C) — ~60 lines
1. Change `upkeep` from number to object in UNIT_TYPES
2. Update `payUpkeep()` to handle multi-resource costs
3. Update `getTotalUpkeep()` display
4. Update between-wave overlay to show metal upkeep
5. Update recruit tooltip to show ongoing upkeep cost
6. Test: metal runs out → units starve → need mines to sustain army

### Phase 4: Balance Pass — ~50 lines
1. Playtest: Can you survive wave 5? Wave 10?
2. Tune: resource building output rates
3. Tune: build costs (too cheap = no tension, too expensive = frustrating)
4. Tune: 3-hit threshold (maybe 4 for quarries/mines since they're expensive?)
5. Tune: metal upkeep amounts
6. Verify strategic triangle works: expand → defend → upgrade → expand

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Early game too hard (no resources before first wave) | Medium | High | Generous starting resources + 5 min build time |
| All enemies rush one building | Medium | Medium | Re-target timer + multiple spawn ring points |
| Metal upkeep makes army impossible | Low | High | Militia stays food-only as fallback |
| Too many new tiles overwhelm map generation | Low | Low | Resource buildings replace existing resource tiles |
| Citizens become useless without gathering | High | Medium | Remove citizens OR repurpose as builders |
| Game becomes too complex for jam judges | Medium | Medium | Keep UI clean, add tooltips |

---

## Open Questions for Fergus

1. **Citizens**: Keep as builders (citizen walks to site, 3s build time) or
   remove gathering and make buildings place instantly like walls?
2. **Repair**: Should the hero be able to repair damaged resource buildings,
   or is "defend or lose it" the whole point?
3. **Resource building HP**: 3 hits flat, or scale by building cost (cheap
   lumber camp = 3 hits, expensive gold mine = 5 hits)?
4. **Do resource buildings block pathing?** (Walls do, settlements do.
   Should a farm block movement or can enemies walk through it?)
5. **Wave bonus scaling**: Keep the `2 + wave` free wood/food, or reduce
   it since resource buildings now exist?
