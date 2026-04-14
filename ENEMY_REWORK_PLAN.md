# Base Siege — Enemy Rework Plan
**Date:** 2026-04-14
**Status:** 📋 DRAFT — For Discussion

---

## Table of Contents
1. [Current System Analysis](#1-current-system-analysis)
2. [Problems to Solve](#2-problems-to-solve)
3. [Design Pillars](#3-design-pillars)
4. [New Enemy Roster](#4-new-enemy-roster)
5. [Enemy Behavior Archetypes](#5-enemy-behavior-archetypes)
6. [Wave Progression System](#6-wave-progression-system)
7. [Enemy Camp System](#7-enemy-camp-system)
8. [Boss System](#8-boss-system)
9. [Enemy Scaling & Difficulty Curve](#9-enemy-scaling--difficulty-curve)
10. [Visual & Audio Identity](#10-visual--audio-identity)
11. [Implementation Phases](#11-implementation-phases)
12. [Open Questions](#12-open-questions)

---

## 1. Current System Analysis

### What We Have (7 types)
| Type | HP | DMG | Speed | Role | Special |
|------|-----|-----|-------|------|---------|
| Raider | 10 | 5 | 6 | Baseline grunt | — |
| Runner | 5 | 3 | 12 | Fast harasser | — |
| Brute | 45 | 8 | 4 | Tank | Smashes walls |
| Enemy Archer | 8 | 6 | 5 | Ranged DPS | 5-tile range |
| Warchief | 30 | 6 | 6 | Buffer | +30% dmg / +20% speed aura (4 tiles) |
| Siege Ram | 60 | 3 | 3 | Structure killer | 20 dmg to structures, targets buildings |
| Swarm | 3 | 2 | 11 | Fodder | Cheap, fast, overwhelming |

### Current Spawning
- Enemies spawn from ring just outside fog of war boundary
- Directional attack waves (1-3 compass directions per wave)
- Camp portals placed at directional spawn points
- Wave composition scales linearly with wave number
- Every 5th wave = siege wave (bonus heavies + swarm flood)

### Current AI
- All enemies pathfind to nearest settlement (CITIZEN_BLOCK)
- Siege Ram → targets nearest structure
- Brute → smashes walls when path blocked
- Enemy Archer → stops to shoot at units/hero in range
- Enemies attack hero/units if adjacent (30% chance)
- Warchief buff aura applied each frame
- Enemies take damage passing through gates
- Traps deal damage + slow

---

## 2. Problems to Solve

### P1: Lack of Strategic Variety
Every wave currently feels the same — blob of melee running to base with occasional ranged/siege mixed in. Player doesn't need to change tactics between waves.

### P2: No Counter-Play Loop
There's no "rock-paper-scissors" between enemy types and player units. The player's optimal strategy is always the same: walls + archers + hero.

### P3: Linear Scaling is Boring
Enemies just get more numerous. No curveballs. No "oh shit, what IS that?" moments.

### P4: Camps Are Purely Visual
Enemy camps spawn at the start of a wave and do nothing. They're decoration.

### P5: No Late-Game Threats
After wave 10, everything is just "more of the same." Boss waves every 5th feel identical to regular waves but with extra brutes.

### P6: Enemies Don't React to Player Strategy
Enemies don't adapt to player's defense layout. They walk into walls of archers repeatedly.

---

## 3. Design Pillars

1. **Each Enemy Type Forces a Different Response** — The player should NEED different unit compositions per wave
2. **Escalating Complexity, Not Just Numbers** — New mechanics, not just bigger HP pools
3. **Readable Threats** — Each enemy should be instantly recognizable and its danger obvious
4. **Strategic Counter-Play** — Clear strengths and weaknesses per enemy type
5. **"Oh Shit" Moments** — Special events/bosses that disrupt the player's plans
6. **Camps as Strategic Objectives** — Optional raiding for rewards

---

## 4. New Enemy Roster (12 types in 4 tiers)

### Tier 1: The Vanguard (Waves 1-4)
Basic enemies that teach the player core mechanics.

| Type | HP | DMG | Speed | Role | Counter |
|------|-----|-----|-------|------|---------|
| **Raider** | 12 | 4 | 5 | Baseline melee grunt | Any unit |
| **Runner** | 6 | 2 | 10 | Fast flanker — goes for exposed buildings | Spearman (zone of control), towers |
| **Swarm** | 3 | 1 | 9 | Overwhelm in numbers, distract defenses | AOE (catapult, hero sweep) |

### Tier 2: The Warband (Waves 3-7)
Specialists that force the player to diversify.

| Type | HP | DMG | Speed | Role | Counter |
|------|-----|-----|-------|------|---------|
| **Brute** | 50 | 8 | 3.5 | Wall smasher, absorbs damage | Focus fire, spearmen (2× bonus) |
| **Skirmisher** | 10 | 5 | 7 | Ranged harasser, kites your melee, 4-tile range | Cavalry (close gap fast), your archers |
| **Sapper** | 15 | 2 | 6 | Targets defenses, plants bomb (3s fuse, 30 AOE dmg to structures) | Hero/melee rush before bomb placed |

### Tier 3: The Horde (Waves 6-12)
Enemies with synergy mechanics — dangerous in combination.

| Type | HP | DMG | Speed | Role | Counter |
|------|-----|-----|-------|------|---------|
| **Warchief** | 35 | 6 | 5 | Aura: +30% dmg, +20% speed to nearby (4 tiles). Rallies broken morale | Kill priority — take out the chief |
| **Shieldbearer** | 40 | 3 | 4 | 60% DR from front (directional armor), escorts other enemies | Flank with cavalry, use catapult AOE |
| **Beastmaster** | 20 | 4 | 5 | Spawns 3 war dogs (fast melee minions) on death | Kill at range to deal with dogs separately |

### Tier 4: The Siege (Waves 8+)
Late-game threats that demand coordinated response.

| Type | HP | DMG | Speed | Role | Counter |
|------|-----|-----|-------|------|---------|
| **Siege Ram** | 70 | 3 | 2.5 | Massive structure damage (25/hit), ignores unit attacks (80% DR vs units) | Hero attack, catapult, sappers self-destruct near it |
| **War Shaman** | 18 | 3 | 5 | Heals nearby enemies (3 HP/s in 3-tile radius), resurrects 1 dead enemy every 8s | Absolute kill priority — ranged focus fire |
| **Ravager** | 25 | 10 | 8 | Charges in a straight line, deals 3× dmg on first hit, stuns target 1s | Walls to break charge, spearmen (brace counter) |

---

## 5. Enemy Behavior Archetypes

### A. Direct Assault (Raider, Brute, Ravager)
- Pathfind to nearest structure
- Attack anything in their path
- Brutes prioritize walls/gates
- Ravagers charge in straight lines toward targets

### B. Flanker/Harasser (Runner, Skirmisher)
- **NEW: Flank Pathing** — Instead of shortest path, these enemies pathfind to the LEAST DEFENDED side of the settlement
- Runners target exposed economy buildings (farms, mills)
- Skirmishers kite: attack, back up 2 tiles, attack again

### C. Specialist (Sapper, Siege Ram)
- Sapper: runs to nearest defense structure (wall/tower), plants bomb, runs away
- Siege Ram: pathfinds to highest-value structure, ignores units
- Both ignore hero/units unless cornered

### D. Support (Warchief, Shieldbearer, War Shaman, Beastmaster)
- Always spawn WITH other enemies (never alone)
- Warchief: stays mid-pack, buffs radius
- Shieldbearer: walks in FRONT of other enemies (escort AI)
- War Shaman: stays BEHIND the assault group, heals forward
- Beastmaster: rushes in, death triggers dog spawn

### E. Overwhelming (Swarm)
- Pure numbers, always 15+ per group
- No special AI — just flood the defenses
- Purpose: drain tower ammo economy, distract units

---

## 6. Wave Progression System

### Wave Structure Rework
Instead of linear scaling, waves follow a **narrative arc**:

```
Waves 1-3:   THE PROBING     — Small raider groups, teaching basics
Waves 4-6:   THE ESCALATION  — Specialists appear, player adapts
Waves 7-9:   THE WAR         — Full combined arms, multiple directions
Wave 10:     FIRST BOSS      — Named boss + honor guard
Waves 11-14: THE SIEGE        — Siege weapons, sappers, heavy assault
Wave 15:     SECOND BOSS     — Bigger boss + full army
Waves 16-19: THE ONSLAUGHT   — Everything at once, max pressure
Wave 20:     FINAL BOSS      — Ultimate enemy + everything thrown at you
```

### Wave Composition Examples

**Wave 1:** 8 Raiders from 1 direction
**Wave 2:** 10 Raiders + 6 Runners from 1 direction
**Wave 3:** 12 Raiders + 8 Runners + 15 Swarm from 2 directions
**Wave 4:** 10 Raiders + 3 Brutes + 1 Sapper from 1 direction
**Wave 5:** 15 Raiders + 8 Skirmishers + 4 Brutes + 20 Swarm from 2 directions (SIEGE WAVE)
**Wave 7:** 12 Raiders + 6 Skirmishers + 2 Warchiefs + 4 Shieldbearers + 20 Swarm from 2 directions
**Wave 10:** BOSS — "The Iron Warlord" + 20 Raiders + 6 Brutes + 3 Shieldbearers + 2 Warchiefs
**Wave 15:** BOSS — "The Dread Shaman" + 10 War Shamans (just kidding — 2) + full army
**Wave 20:** FINAL BOSS — "The Siege King" + everything

### Attack Direction Escalation
| Waves | Directions |
|-------|-----------|
| 1-3 | 1 direction |
| 4-7 | 1-2 directions |
| 8-12 | 2-3 directions |
| 13+ | 2-4 directions |

### NEW: Wave Preview
Before each wave, show a brief "scout report" panel:
```
⚠️ WAVE 7 APPROACHING — East & North
  Raider ×12  |  Skirmisher ×6  |  Warchief ×2  
  Shieldbearer ×4  |  Swarm ×20
  
  ⏱️ 45s to prepare
```
This lets players adjust their defenses tactically.

---

## 7. Enemy Camp System (Rework)

### Current: Camps are decorative portals
### Proposed: Camps are persistent strategic objectives

**Camp Types:**
| Camp | Spawns | Reward for Destroying |
|------|--------|----------------------|
| **Raider Outpost** | Raiders + Runners between waves | +50 gold, stops between-wave raids |
| **War Camp** | All wave enemies (standard) | +100 gold, reduces next wave enemy count by 25% |
| **Siege Workshop** | Siege Rams + Sappers | +80 gold + 20 metal, removes siege units from next 2 waves |
| **Dark Shrine** | War Shamans + buffs all camps | +120 gold, removes healing from next 3 waves |

**Camp Mechanics:**
- Camps spawn at wave start and PERSIST between waves
- Each camp has HP (100/150/200 based on type)
- Player can send units to attack camps during BUILD phase
- Destroying camps gives rewards AND weakens future waves
- Camps level up every 3 waves if not destroyed (+50% HP, stronger spawns)
- 1-3 camps active at a time

**Risk/Reward:** Sending units to raid camps means fewer defenders at base.

---

## 8. Boss System

### Boss Design Principles
- Bosses have unique mechanics (not just big HP bars)
- Bosses take reduced damage from towers/structures (50%)
- Bosses require player micro-management (hero engagement)
- Each boss has a "gimmick" the player must learn

### Boss Roster

#### Wave 10: "Ironclad Warlord"
- **HP:** 300
- **Speed:** 4
- **Mechanic:** Wears armor plates. Each plate absorbs 50 dmg before breaking (4 plates = 200 bonus HP). Plates visually break off. When all plates gone, takes 2× damage (vulnerable phase for 10s), then regenerates 2 plates.
- **Attack:** Cleave — hits all units in 2-tile frontal cone for 15 dmg
- **Special:** War cry every 20s — all enemies gain 50% speed for 5s
- **Counter:** Break plates with focus fire → burst during vulnerable window

#### Wave 15: "The Plague Herald"
- **HP:** 250
- **Speed:** 5
- **Mechanic:** Leaves toxic trail (2-tile wide) that deals 3 dmg/s to units standing in it. Trail lasts 15s.
- **Attack:** Plague bolt — ranged, 6 tiles, poisons target (2 dmg/s for 8s)
- **Special:** Every 15s, summons 10 plague swarm (buffed swarm with poison on hit)
- **Counter:** Kite with ranged, don't let units stand in trail, hero mobility key

#### Wave 20: "The Siege Colossus"
- **HP:** 500
- **Speed:** 2
- **Mechanic:** Massive unit (3×3 tiles). Crushes buildings by walking through them. Cannot be slowed.
- **Attack:** Ground slam — 4-tile radius AOE, 20 dmg to units, 40 dmg to structures, 3s cooldown
- **Special:** At 50% HP, splits into 2 "Half-Colossus" (200 HP each, 2×2, same attacks but weaker)
- **Counter:** Requires full army + hero coordinated assault. Cavalry charge bonus helps.

---

## 9. Enemy Scaling & Difficulty Curve

### Stat Scaling Per Wave
Instead of just adding more enemies, existing enemies get mild stat boosts:

```
After wave 5:   All enemy HP +10%, DMG +10%
After wave 10:  All enemy HP +25%, DMG +20%
After wave 15:  All enemy HP +40%, DMG +30%
After wave 20:  All enemy HP +60%, DMG +40%
```

### Enemy Event System (Between Waves)
Random events that shake up routine:

| Event | Effect | Frequency |
|-------|--------|-----------|
| **Raiding Party** | 5-8 Runners attack from unexpected direction during BUILD phase | 15% chance waves 5+ |
| **Fog of War Push** | Enemy scouts reduce your fog vision by 3 tiles for 1 wave | 10% chance waves 8+ |
| **Reinforcements** | Mid-wave, 50% more enemies spawn from a new direction | 10% chance waves 10+ |
| **Desperate Charge** | All remaining enemies gain 2× speed for 10s when <30% remain | Always after wave 5 |

### Difficulty Curve Target
```
Wave 1-3:   Trivial (learn controls)
Wave 4-6:   Easy (learn unit composition)
Wave 7-9:   Medium (requires planning)
Wave 10:    Hard (first boss test)
Wave 11-14: Medium-Hard (economy management)
Wave 15:    Hard (second boss + siege pressure)
Wave 16-19: Very Hard (constant pressure, multi-front)
Wave 20:    Extreme (final challenge)
```

---

## 10. Visual & Audio Identity

### Enemy Visual Language
Each enemy should be instantly readable at a glance:

| Type | Shape | Size | Color | Icon |
|------|-------|------|-------|------|
| Raider | Square | 0.9× | Dark Red `[180,50,50]` | `E` |
| Runner | Square | 0.75× | Orange `[200,120,60]` | `R` |
| Swarm | Square | 0.6× | Tan `[170,130,80]` | `z` |
| Brute | Square | 1.1× | Dark Crimson `[140,40,40]` | `B` |
| Skirmisher | Square | 0.85× | Purple `[160,80,160]` | `S` |
| Sapper | Square | 0.8× | Yellow-Green `[140,160,60]` | `💣` |
| Warchief | Square | 1.0× | Hot Pink `[200,40,80]` | `W` + 👑 |
| Shieldbearer | Square | 1.0× | Steel Blue `[80,100,140]` | `▣` |
| Beastmaster | Square | 0.9× | Brown `[140,100,50]` | `🐺` |
| Siege Ram | Square | 1.2× | Wood Brown `[100,70,50]` | `≡` |
| War Shaman | Square | 0.9× | Sickly Green `[80,160,80]` | `✚` |
| Ravager | Square | 0.95× | Bright Red `[220,50,30]` | `⚡` |
| **Bosses** | Square | 2.0-3.0× | Unique per boss | Unique |

### Enemy Death Effects
- **Regular**: Small particle burst in enemy color
- **Brute/Siege**: Large particle burst + screen shake
- **Warchief**: Gold burst + "👑 Warchief slain!" float
- **Boss**: Massive explosion, screen shake, victory fanfare float text, gold shower particles

### Buff/Debuff Indicators
- **Warchief buffed**: Red glow ring (existing)
- **Shieldbearer protected**: Blue shimmer on front
- **War Shaman heal**: Green pulse particles
- **Poison**: Green drip particles
- **Slowed**: Blue tint overlay

---

## 11. Implementation Phases

### Phase K1: Enemy Type Rework (~200 lines)
1. Update ENEMY_TYPES with all 12 types + stats
2. Replace `enemyArcher` with `skirmisher` (kiting AI)
3. Add `sapper` type + bomb mechanics
4. Add `shieldbearer` type + directional armor
5. Add `beastmaster` type + minion spawn on death
6. Add `warShaman` type + heal aura + resurrect
7. Add `ravager` type + charge mechanic
8. Update XP rewards per type

### Phase K2: Enemy AI Overhaul (~300 lines)
1. Flank pathing for Runners/Skirmishers (least-defended path)
2. Skirmisher kiting behavior (shoot → retreat → shoot)
3. Sapper bomb-plant AI (run to structure, plant, flee)
4. Shieldbearer escort AI (walk in front of pack)
5. War Shaman heal tick + resurrect logic
6. Beastmaster death → spawn war dogs
7. Ravager charge mechanic (straight line, bonus first-hit)
8. Enemy re-evaluation of targets every 3-5s

### Phase K3: Wave System Overhaul (~150 lines)
1. Rewrite getWaveComposition() with narrative arc structure
2. Wave preview panel (scout report)
3. Attack direction escalation (1→2→3→4 directions)
4. Stat scaling per wave milestone
5. Between-wave events (raiding party, fog push, etc.)
6. "Desperate Charge" mechanic for wave remnants

### Phase K4: Boss System (~200 lines)
1. Boss data definitions (3 bosses)
2. Boss-specific AI (armor plates, toxic trail, ground slam)
3. Boss rendering (larger sprites, unique effects)
4. Boss HP bar (persistent top-of-screen bar)
5. Boss phase transitions (Colossus split, Warlord armor regen)
6. Boss victory effects (gold shower, text, shake)

### Phase K5: Camp Rework (~150 lines)
1. Camp types (Outpost, War Camp, Siege Workshop, Dark Shrine)
2. Camp persistence between waves
3. Camp HP + destructibility
4. Camp rewards on destruction
5. Camp leveling (every 3 waves)
6. Player unit camp raiding during build phase

### Phase K6: Visual Polish (~100 lines)
1. Updated enemy rendering for all 12 types
2. Boss rendering (oversized sprites, unique effects)
3. New particle effects (poison, heal, charge trail)
4. Buff/debuff visual indicators
5. Wave preview panel styling
6. Boss HP bar UI

**Estimated total: ~1,100 new/modified lines across 6 sub-phases**

---

## 12. Open Questions

1. **Endless mode?** After wave 20 (final boss), does the game end or continue with escalating difficulty?
2. **Enemy loot drops?** Should killing enemies sometimes drop resources (gold, metal)?
3. **Difficulty settings?** Easy/Normal/Hard that scales enemy HP/count?
4. **Counter-play hints?** Should the wave preview include tips like "Skirmishers weak to Cavalry"?
5. **Camp raiding risk?** If player sends units to raid camps, should camps fight back? (Garrison mechanic)

---

## Quick Comparison: Before vs After

| Aspect | Current | Proposed |
|--------|---------|----------|
| Enemy types | 7 | 12 + 3 bosses |
| AI behaviors | 2 (melee rush, ranged stop) | 5 archetypes with unique logic |
| Wave variety | Linear scale | Narrative arc with phases |
| Camps | Decorative | Strategic objectives with rewards |
| Bosses | None | 3 unique bosses with mechanics |
| Counter-play | None | Rock-paper-scissors unit matching |
| Events | None | Random between-wave events |
| Difficulty curve | Flat escalation | Designed peaks and valleys |
