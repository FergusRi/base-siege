# Base Siege — Complete Game Overhaul Plan
**Date:** 2026-04-13
**Status:** 🔒 FINAL — Implementation ready

---

## Table of Contents
1. [Overview](#overview)
2. [Map Generation](#map-generation)
3. [Settlement System](#settlement-system)
4. [Complete Building Roster](#complete-building-roster)
5. [Movable Unit System](#movable-unit-system)
6. [Training Queue System](#training-queue-system)
7. [Formation & Drag System](#formation--drag-system)
8. [Hero Guard System](#hero-guard-system)
9. [Economy & Resource Flow](#economy--resource-flow)
10. [Citizen System Changes](#citizen-system-changes)
11. [Combat Changes](#combat-changes)
12. [UI & Controls](#ui--controls)
13. [Implementation Phases](#implementation-phases)
14. [Code Impact Analysis](#code-impact-analysis)

---

## 1. Overview

Transform Base Siege from a tower-defense hybrid into a proper RTS with:
- Movable units (select, move, attack-move, formation drag)
- Settlement-based building zones with tier progression
- Training queue at military buildings (barracks, archery range, stable)
- Passive economy buildings (farms, mills, forges) + citizen harvesting
- Hero guard system
- Natural biome map (already implemented in Step 1)

---

## 2. Map Generation

**Status: ✅ Step 1 DONE** — biome noise system implemented.

**Still needed:**
- Reduce density further (target 80%+ open grass)
- Remove center-to-edge gradient — pure random biome placement
- Lower frequency noise for bigger biome blobs (100-200 tile regions)
- Hard biome boundaries (in forest or not, no gradient)
- Forests: dense trees inside (~70%), zero outside
- Mountains: clearly grey rocky areas
- Berry meadows: small distinct patches
- Gold: 2-3 tiny deposits, random location

---

## 3. Settlement System

### Settlement Tiers

| Tier | Name | Upgrade Cost | Build Radius | Max Houses | Base Citizens |
|------|------|-------------|-------------|-----------|--------------|
| 1 | Village | 50W 30S (first free) | 15 tiles | 3 | 2 |
| 2 | Town | 30S 10M | 20 tiles | 6 | +1 (3 total) |
| 3 | City | 20M 5G | 25 tiles | 9 | +1 (4 total) |

### Rules
- First settlement is FREE (placed at game start)
- Additional settlements cost 50W 30S (with scaling multiplier)
- Build radius = faint circle rendered on ground
- ALL buildings (except new settlements) must be inside a settlement radius
- Overlapping radii are fine — buildings count toward the settlement they're closest to
- Upgrading a settlement expands the circle visually
- Settlement HP: 80 (repairable, max 3 repairs)
- If all settlements destroyed → GAME OVER

### House Sub-system
- Houses are buildings placed inside settlement radius
- Each house: costs 5W 2S, upkeep 1 food/wave, provides +1 citizen
- House limits are TOTALS per settlement tier (3 at T1, 6 at T2, 9 at T3)
- House HP: 20 (repairable)

---

## 4. Complete Building Roster (19 buildings)

### 🏘️ Infrastructure (2)

| Building | Cost | Upkeep | HP | Effect | Tier |
|----------|------|--------|----|--------|------|
| **Settlement** | 50W 30S (scaling) | — | 80 | Build zone + 2 citizens | — |
| **House** | 5W 2S | 1F | 20 | +1 Citizen | T1 |

### 🌾 Economy (7)

| Building | Cost | Upkeep | HP | Produces | Tier |
|----------|------|--------|----|----------|------|
| **Farm** | 8W | — | 25 | +3 food/wave | T1 |
| **Lumber Mill** | 10F 5S | 2F | 30 | +3 wood/wave | T2 |
| **Quarry** | 8W 5F | 2F | 30 | +3 stone/wave | T2 |
| **Forge** | 15S 5W | 3F | 35 | +3 metal/wave | T3 |
| **Mint** | 20M 10S | 4F | 35 | +3 gold/wave | T3 |
| **Granary** | 12W 5S | — | 25 | -20% food upkeep (settlement) | T1 |
| **Storehouse** | 10W 8S | — | 30 | -15% all upkeep (settlement) | T2 |

**Granary destroyed** → lose 25% stored food
**Storehouse destroyed** → lose 15% of ALL stored resources

### ⚔️ Military (3)

| Building | Cost | Upkeep | HP | Trains | Tier |
|----------|------|--------|----|--------|------|
| **Barracks** | 15W 10S | 2F | 40 | Militia, Spearman | T1 |
| **Archery Range** | 12W 8S 3M | 2F | 40 | Archer, Catapult | T2 |
| **Stable** | 20W 10S 5M | 3F | 40 | Cavalry | T2 |

### 🛡️ Defense (7)

| Building | Cost | HP | Effect | Tier |
|----------|------|----|--------|------|
| **Palisade** | 3W | 25 | Cheap wood wall, blocks path | T1 |
| **Wall** | 5S | 60 | Stone wall, blocks path | T1 |
| **Gate** | 5W 2S | 30 | Friendly units + hero walk through, enemies take dmg + slow | T1 |
| **Tower** | 10W 5S 3M | 40 | Auto-fires, 6-tile range | T1 |
| **Watchtower** | 8W 3S | 25 | +8 tile vision, spots enemies 5s early | T1 |
| **Ballista Tower** | 15W 8S 5M | 50 | 10-tile range, piercing (hits 2 enemies in line) | T2 |
| **Gatehouse** | 12W 8S 3M | 50 | Upgraded gate: more HP + dmg + vision | T3 |

### Building Rules
- All buildings must be inside a settlement radius (except new settlements)
- All buildings are destroyable and repairable (full cost, max 3 repairs)
- After 3 repairs → next destruction = permanent (building gone)
- Defense buildings block pathing EXCEPT gates/gatehouses (friendly walkthrough)

---

## 5. Movable Unit System

### Core Behavior
- Units are **colored circles** with letter icon (like citizens but slightly larger)
- Units auto-attack any enemy within their engagement range
- Units stand ground where moved — they don't chase
- If enemy enters range, unit engages then returns to position
- Units fight to the death (no retreat, no fleeing)

### Unit Stats

| Unit | HP | DMG | Range | Speed | Train Time | Cost | Upkeep |
|------|-----|-----|-------|-------|-----------|------|--------|
| Militia | 20 | 4 | Melee (1.2) | 3 t/s | 10s | 5W 2F | 1F |
| Spearman | 25 | 5 | Melee (1.2) | 2.5 t/s | 15s | 4W 3F 2M | 1F 1M |
| Archer | 12 | 3 | 4 tiles | 2.5 t/s | 20s | 5W 3M | 1F 1M |
| Cavalry | 30 | 7 | Melee (1.5) | 6 t/s | 30s | 8W 5F 5M | 2F 2M |
| Catapult | 8 | 12 (AOE) | 6 tiles | 1.5 t/s | 40s | 12W 5S 4M | 1F 3M |

### Movement Speeds
- **Cavalry**: 6 tiles/s (fastest — flanking & scouting)
- **Militia/Archer/Spearman**: 2.5-3 tiles/s (standard infantry)
- **Catapult**: 1.5 tiles/s (slow siege)
- **Hero**: 4 tiles/s (fastest non-cavalry)

### Engagement Ranges (auto-attack trigger)
- **Melee**: 1.2 tiles (militia, spearman) / 1.5 tiles (cavalry)
- **Archer**: 4 tiles
- **Catapult**: 6 tiles (AOE 3×3)
- **Tower/Ballista**: 6/10 tiles

### Collision & Spreading
- Units CANNOT stack on same tile
- When multiple units move to same area, they spread out automatically
- Units occupy a circular area (~0.8 tile radius)
- Pathfinding avoids other friendly units

---

## 6. Training Queue System

### How It Works
1. Click a Barracks/Archery Range/Stable → opens training panel
2. Click unit type → cost deducted immediately → added to queue
3. Building trains ONE unit at a time (sequential)
4. Progress bar shown above building during training
5. When done, unit spawns on nearest empty tile to building
6. Queue can hold multiple units (all pre-paid)
7. Multiple barracks = parallel training (2 barracks = 2 militia at once)

### Training Panel UI
- Small panel appears near the building when clicked
- Shows available unit types (icon + name + cost + time)
- Shows current queue (unit icons in order)
- Cancel button removes last queued unit (refunds cost)
- Progress bar for currently training unit

### Edge Cases
- If barracks destroyed during training → all queued units lost, costs NOT refunded
- If no empty tile near building → unit waits in queue until space available
- Training continues during BUILD phase only (pauses during COMBAT)

---

## 7. Formation & Drag System (Total War Style)

### Drag-to-Formation
1. Select units (box select or shift+click)
2. Right-click and DRAG on ground
3. Drag direction + length determines formation shape:
   - **Long drag**: single line perpendicular to drag direction
   - **Medium drag**: double line (front rank + back rank)
   - **Short drag** (just click): blob/cluster (current behavior)
4. Units pathfind to their assigned position in the formation

### Line Calculation
```
dragLength = distance from click to release
unitCount = number of selected units

if dragLength > unitCount * 0.8:
    → Single line, units spaced evenly along drag line
elif dragLength > unitCount * 0.4:
    → Double line, front row + back row
else:
    → Blob (units cluster at point)
```

### Formation Bonuses (Updated)
- **Shield Wall**: 3+ melee units within 3 tiles of each other → +30% DR
- **Protected Fire**: ranged unit within 2 tiles behind a melee unit → +20% fire rate
- Formation checks are now DISTANCE-BASED, not tile-adjacency (since units move freely)

---

## 8. Hero Guard System

### Concept
- Hero can have a personal guard — units assigned to follow the hero
- Guard units move with the hero automatically (maintain formation around hero)
- Guard size limited by hero level/upgrade

### Hero Guard Upgrades
| Upgrade | Cost | Effect |
|---------|------|--------|
| Guard I | 10M | Hero can have 2 guard units |
| Guard II | 20M 5G | Hero can have 4 guard units |
| Guard III | 30M 10G | Hero can have 6 guard units |

### How It Works
1. Select unit(s) → right-click hero → "Assign to Guard"
2. Guard units form circle around hero
3. Guard units move when hero moves (with slight delay)
4. Guard units auto-attack enemies near hero
5. Can dismiss guard units (they stop following, stand where they are)
6. Guard upgrade purchased at settlement (click settlement → upgrade panel)

---

## 9. Economy & Resource Flow

### Income Sources

**Passive (buildings):**
- Farm: +3 food/wave
- Lumber Mill: +3 wood/wave
- Quarry: +3 stone/wave
- Forge: +3 metal/wave
- Mint: +3 gold/wave

**Active (citizen harvesting):**
- Citizens walk to map resources, harvest, bring back
- Same system as current — supplements building income
- More citizens = more active income (but more food drain)

### Expenses Per Wave

**Building upkeep:**
- Houses: 1F each
- Lumber Mill/Quarry: 2F each
- Forge: 3F
- Mint: 4F
- Barracks/Archery Range: 2F each
- Stable: 3F

**Unit upkeep:**
- Militia: 1F
- Spearman: 1F 1M
- Archer: 1F 1M
- Cavalry: 2F 2M
- Catapult: 1F 3M

### Starting Resources
```js
INITIAL_RESOURCES = {wood:100, stone:50, metal:30, food:50, gold:0}
```

### No Free Wave Bonus
All wave bonuses removed. Income comes ONLY from buildings + citizen harvesting.

### Granary/Storehouse Effects
- **Granary** in settlement: all food upkeep for buildings/units IN that settlement -20%
- **Storehouse** in settlement: all resource upkeep for that settlement -15%
- Effects don't stack (1 granary per settlement max? Or stackable?)

---

## 10. Citizen System Changes

### Unchanged
- Citizens spawn from settlements + houses
- Citizens walk to map resources and harvest
- Citizens pathfind using existing A* system
- Citizens are vulnerable outside settlement radius

### Changed
- **30-second recall**: when player presses SPACE, 30s countdown starts
  - Banner: "⚠️ ENEMIES APPROACHING — 30s"
  - Citizens pathfind back to their HOME settlement
  - After 30s → COMBAT begins
  - Citizens inside settlement radius during combat are SAFE
  - Citizens caught outside can be killed
- Citizens also walk to resource buildings to "work" them (visual only — production is automatic)
- Remove per-settlement gather priority (no longer relevant)

---

## 11. Combat Changes

### Enemy Targeting
Enemies pathfind to nearest player structure (not just settlements):
```
Priority:
1. If adjacent to player unit → attack it (30% chance)
2. If adjacent to hero → attack hero
3. Pathfind to NEAREST player structure (any type)
4. Re-evaluate target every 3-5 seconds
```

### Gate Passthrough
- **Friendly units + hero** can walk through Gates and Gatehouses
- **Enemies** take damage + slow when passing through (unchanged)
- Implementation: `isWalkable()` checks if the entity is friendly

### Watchtower Early Warning
- Watchtower provides 5-second early warning before normal wave start
- "Enemies spotted by watchtower!" notification
- Enemies appear on minimap 5s before they start moving

---

## 12. UI & Controls

### Unit Selection & Movement

| Action | Input |
|--------|-------|
| Select unit | Left-click |
| Add to selection | Shift + left-click |
| Box select | Left-click drag on ground |
| Move selected | Right-click ground |
| Attack-move | Right-click enemy |
| Assign to hero guard | Select unit → right-click hero |
| Save control group | Ctrl+1/2/3 |
| Recall control group | 1/2/3 (when not in build mode) |
| Deselect all | ESC |

### Building Interaction

| Action | Input |
|--------|-------|
| Open build mode | B |
| Category tabs | 1=Defense, 2=Economy, 3=Military, 4=Infrastructure |
| Quick-build shortcuts | Q/W/E/R/T within category |
| Click military building | Opens training queue panel |
| Click settlement | Opens upgrade panel |
| Place building | Left-click inside settlement radius |

### Toolbar Categories (Revised)

**1 — Defense**: Palisade, Wall, Gate, Tower, Watchtower, Ballista, Gatehouse
**2 — Economy**: Farm, Lumber Mill, Quarry, Forge, Mint, Granary, Storehouse
**3 — Military**: Barracks, Archery Range, Stable
**4 — Infrastructure**: Settlement, House

### HUD Updates
- **Selection panel** (bottom center): shows selected unit(s) info, HP, rank
- **Training queue** (right side): shows current training in progress
- **Settlement info** (on click): tier, houses, buildings, radius
- **Resource bar** (top): unchanged but add income/expense per wave summary on hover

---

## 13. Implementation Phases

### Phase A: Map Rework (Step 1: DONE ✅, density fix needed)
- Fix biome density (80%+ grass)
- Remove center-to-edge gradient
- Bigger biome blobs

### Phase B: Settlement System (~200 lines)
1. Settlement tier data + build radius
2. Build radius rendering (faint circle on ground)
3. Build zone validation (all buildings must be inside radius)
4. Settlement upgrade UI (click → panel)
5. House building + citizen spawning per house
6. House limit per tier (3/6/9)

### Phase C: Building System Rework (~400 lines)
1. Add all 19 building definitions to STRUCTS
2. Rework toolbar into 4 categories
3. Building placement validation (inside radius + tier check)
4. Building upkeep system in endWave()
5. Building HP + destruction + repair (3 max)
6. Granary/Storehouse effects
7. Rendering for all new building types
8. Building-under-attack minimap flash

### Phase D: Training Queue (~300 lines)
1. Training queue data structure per military building
2. Training panel UI (click barracks → see queue)
3. Queue management (add/cancel/progress)
4. Unit spawning at building on completion
5. Training progress bar rendering
6. Multiple barracks parallel training

### Phase E: Movable Units (~500 lines — BIGGEST PHASE)
1. Convert unit data model from tile-based to position-based
2. Unit selection system (click, shift-click, box select)
3. Unit movement (right-click → pathfind → walk)
4. Attack-move behavior
5. Auto-engagement when enemy enters range
6. Unit collision + spreading
7. New unit rendering (circles instead of tile squares)
8. Selection ring + HP bar + rank display
9. Control groups (Ctrl+1/2/3)
10. Update formation detection to distance-based
11. Remove old tile-based unit placement system

### Phase F: Formation Drag (~150 lines)
1. Drag detection (right-click hold + drag)
2. Line/double-line/blob calculation
3. Position assignment for each unit
4. Formation preview while dragging (ghost positions)
5. Updated formation bonuses (distance-based)

### Phase G: Hero Guard (~100 lines)
1. Hero guard upgrade data + cost
2. Assign-to-guard interaction (select → right-click hero)
3. Guard follow behavior (move with hero, slight delay)
4. Guard auto-attack behavior
5. Dismiss guard command
6. Guard upgrade UI at settlement

### Phase H: Gate Passthrough + Citizen Recall (~100 lines)
1. Modify isWalkable() to accept entity type parameter
2. Friendly units + hero can pass through gates
3. 30-second recall countdown system
4. Citizen pathfind-to-home behavior
5. Warning banner + timer display

### Phase I: Economy Rework (~150 lines)
1. Building production in endWave()
2. Building upkeep deduction
3. Multi-resource unit upkeep
4. Granary/Storehouse percentage modifiers
5. Remove free wave bonus
6. Update starting resources
7. Update aftermath screen with income/expense summary

### Phase J: Balance Pass (~50 lines)
1. Playtest waves 1-20
2. Tune all costs, HP, production rates, upkeep
3. Tune enemy wave scaling
4. Tune training times
5. Ensure strategic triangle works

---

## 14. Code Impact Analysis

### Files Changed
- `index.html` — only file (single-file game)

### Sections Heavily Modified
| Section (§) | Changes |
|-------------|---------|
| §1 Constants | New building defs, unit stats, training times |
| §2 Tile Types & Structs | 19 buildings added, old STRUCTS reworked |
| §3 Map Generation | Density fix, remove gradient |
| §5 Citizen System | Add recall countdown, remove gather priority |
| §7 Game State | Training queues, selection state, guard state |
| §9 UI & Mode System | 4-cat toolbar, training panel, selection panel |
| §10 Combat | Gate passthrough, enemy retargeting |
| §11 Unit AI | COMPLETE REWRITE — movable units, auto-engage, attack-move |
| §12 Economy | Building production, multi-resource upkeep |
| §14 Input & Camera | Box select, right-click move, drag-formation |
| §15 Rendering | Circle units, building radius, training progress bars |

### Sections Unchanged
| Section (§) | Notes |
|-------------|-------|
| §4 Fog of War | Works as-is |
| §6 Pathfinding | A* reused for unit movement |
| §8 Spawn Ring | Works as-is |
| §13 Morale & Veterancy | Minor tweaks (distance-based) |
| §16 Minimap | Minor updates (show movable units) |
| §17 Screens & Game Loop | Minor updates |

### Estimated Total Lines Changed
- New code: ~1,800 lines
- Removed code: ~400 lines (old static unit system)
- Modified code: ~300 lines
- **Net change: ~+1,400 lines** (5,800 → ~7,200)

### Risk Mitigation
- Implement in phases A→J, each producing a playable build
- Git commit after each phase
- Test each phase before moving to next
- Keep backup of pre-overhaul code (tag in git)

---

## Resolved Decisions Summary

| Decision | Answer |
|----------|--------|
| Squads? | No formal squads — blob selection |
| Combat AI? | Option A + attack-move |
| Movement speed? | Type-based (cavalry fastest, catapult slowest) |
| Collision? | Units spread, no stacking |
| Formation drag? | Total War style — line/double/blob based on drag length |
| Hero guard? | Yes, upgradeable (2/4/6 units) |
| Retreat? | No — fight to the death |
| Idle engagement? | Auto-engage enemies in range |
| Gate passthrough? | Yes for friendly units + hero |
| Moat? | Backburner (not in this overhaul) |
| Trap? | Removed |
| House limit? | 3/6/9 total per settlement tier |
| Barracks limit? | Limited by physical space only |
| Training queue? | Sequential (one at a time per building), can queue multiple |
| Map resources? | Random placement, no center-edge gradient |
| Wave bonus? | Removed |
