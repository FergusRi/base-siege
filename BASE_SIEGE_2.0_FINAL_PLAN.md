# BASE SIEGE 2.0 — FINAL IMPLEMENTATION PLAN
## Locked In: 2026-04-12

---

## CORE IDENTITY CHANGE
**From:** Static tower defense with a mobile hero
**To:** Expansion survival RTS — fog of war, citizen economy, multi-hero raids, infinite waves

**Tagline:** *"Expand your empire, defend your people, raid enemy camps — survive as long as you can."*

---

## MAP & WORLD

### Dimensions
- **150×100 tiles** (15,000 tiles) at 32px each
- Camera viewport renders only visible tiles (performance)
- Dynamic zoom: can't zoom out beyond map boundaries

### Fog of War (3 States — Civ 6 Style)
| State | Value | Rendering | Entities | Spawning |
|---|---|---|---|---|
| UNEXPLORED | 0 | Solid dark grey (#1a1a24) | Hidden | Enemy camps CAN spawn |
| EXPLORED | 1 | Desaturated terrain (grey-tinted) | Hidden | Enemy camps CAN spawn |
| VISIBLE | 2 | Full color | All shown | Camps CANNOT spawn |

- Hero movement reveals fog → EXPLORED (permanent, grey like Civ)
- Vision sources (HQ, citizen blocks) → VISIBLE (full color, real-time)
- When vision source destroyed → tiles revert to EXPLORED (re-fog)
- Fog stored as `fogMap[col][row]` parallel to `map[col][row]`

### Resource Distribution (Distance-Based)
```
┌──────────────────────────────────────────┐
│ ⚠️ CAMPS + 💰 GOLD + ⛏️ IRON            │  Edge strip (15 tiles)
│                                          │
│   🪨 Stone clusters + scattered trees    │  Outer ring (15-40 tiles)
│                                          │
│     🌲 Trees + 🫐 Berries (moderate)     │  Mid ring (10-25 tiles)
│                                          │
│        (sparse resources) Center zone    │  Inner (0-15 tiles from center)
│                                          │
│     🌲 Trees + 🫐 Berries               │
│                                          │
│   🪨 Stone clusters                      │
│                                          │
│ ⚠️ CAMPS + 💰 GOLD + ⛏️ IRON            │  Edge strip (15 tiles)
└──────────────────────────────────────────┘
```

### Resource Nodes (Multi-Harvest Deposits)
| Node Type | Yield/Harvest | Total Harvests | Regrowth | Location |
|---|---|---|---|---|
| Tree Cluster 🌲 | 2 wood | 5 | After 3 waves | Everywhere, dense mid |
| Berry Grove 🫐 | 3 food | 4 | After 2 waves | Scattered mid |
| Stone Quarry 🪨 | 2 stone | 8 | Never | Clustered outer |
| Iron Vein ⛏️ | 1 metal | 6 | Never | Rare, outer near camps |
| Gold Deposit 💰 | 1 gold | 3 | Never | Very rare, edge strip |

- Nodes cluster in veins/groves (3-6 tiles together)
- Depleted nodes show "spent" visual (cracked/empty)
- Center has sparse resources → HQ at center = safe but slow economy
- Edge has rich resources → HQ near edge = rich but dangerous

---

## HQ SYSTEM

### Placement Phase
- Game starts with full fog. "Place Your HQ" prompt.
- Player clicks any non-water tile (entire map available)
- Near center = safe start, sparse resources
- Near edge = risky, rich resources, close to enemy camps
- **This is the game's first strategic decision**

### HQ Stats
| Tier | Cost | Vision | HP | Bonus |
|---|---|---|---|---|
| Tier 1 | Free (start) | 4 tiles | 200 | — |
| Tier 2 | 50S + 20M | 5 tiles | 300 | +10% all gather speed |
| Tier 3 | 30M + 10G | 6 tiles | 450 | +20% gather, +1 citizen per block |

- HQ destroyed = **GAME OVER** (primary lose condition)
- Large golden fortress render (3×3 tile footprint visually, 1 tile for placement)

---

## CITIZEN SYSTEM

### Citizen Blocks (Structure)
- **Toolbar key:** C
- **Cost:** Scales: `50W + 30S × (1 + 0.3 × existing_blocks)`
- **HP:** 80 (Tier 1) → 120 (Tier 2) → 180 (Tier 3)
- **Vision radius:** 2 tiles (Tier 1) → 3 tiles (Tier 2-3)
- **Spawns:** 2 citizens (Tier 1) → 3 (Tier 2) → 4 (Tier 3)
- **Gather radius:** 3 tiles (Tier 1) → 4 (Tier 2) → 5 (Tier 3)
- **Placement:** Anywhere on VISIBLE (non-fog) tiles, any distance from HQ
- **Must leave path to HQ** (same validation as walls)

### Citizen Block Upgrades
| Tier | Upgrade Cost | Citizens | Vision | Gather Radius | Gather Speed | HP |
|---|---|---|---|---|---|---|
| 1 | Base cost | 2 | 2 tiles | 3 tiles | 1× | 80 |
| 2 | 30S + 10M | 3 | 3 tiles | 4 tiles | 1.3× | 120 |
| 3 | 20M + 5G | 4 | 3 tiles | 5 tiles | 1.6× | 180 |

### Citizen Block Adjacency Bonuses
- Next to resource node: +25% gather speed
- Next to another citizen block: +10% gather speed to both
- Next to HQ: +15% gather speed, +1 vision range
- Next to wall/tower: +5% citizen HP

### Citizens (AI Entities)
- **Autonomous** — not player-controlled
- **HP:** 8 (fragile!)
- **Speed:** 2 tiles/sec
- **Cannot fight** — pure civilians
- **BUILD phase behavior:**
  1. Path to nearest un-depleted resource within block's gather radius
  2. Stand on tile 1.5 seconds (gather animation)
  3. Resource added immediately (no return trip needed)
  4. Seek next resource, repeat
  5. Priority: food > wood > stone > metal > gold
- **30-Second Recall:**
  - 30 seconds before wave: warning horn + banner "⚠️ CITIZENS RETURNING"
  - Citizens auto-path to nearest citizen block or HQ
  - Citizens within 1-tile radius of block/HQ = "safe" (hidden during combat)
  - Citizens still outside when wave starts = VULNERABLE
  - Enemies target exposed citizens
- **Citizen death:** Lost citizens are replaced next BUILD phase by their block
- **Upkeep:** 1 food per 2 citizens per wave

### Citizen Rendering
- Small (60% tile size) pastel circles with "C" letter
- Carry animation: tiny resource icon floats above when gathering
- Flee animation: faster movement, panic particles
- Safe: fade out when inside block radius during combat

---

## MULTI-HERO SYSTEM

### Hero Roster (Max 4 — One of Each Type)
| Hero | Cost | HP | DMG | Speed | Range | Special |
|---|---|---|---|---|---|---|
| **Commander** ⚔️ | Free (start) | 50 | 8 | 5 | Melee | Morale aura (3 tiles, +30% recovery) |
| **Champion** 🛡️ | 20M + 5G | 70 | 12 | 4 | Melee | Cleave (hits 3 adjacent enemies) |
| **Ranger** 🏹 | 15M + 5G | 35 | 6 | 7 | 5 tiles | Ranged attack, fastest, great scout |
| **Siege Captain** 💣 | 25M + 10G | 45 | 15 | 3 | Melee | 2× damage to structures/camps |

### Controls
- **Tab** cycles active hero (camera snaps)
- **WASD** moves active hero
- **Click** attacks with active hero
- **H** key = recall active hero to HQ (auto-path)
- Hero portraits in top-left showing HP/status/class icon

### Permadeath System
- Heroes can **permanently die** (HP reaches 0 during combat)
- Death triggers dramatic effect: slow-mo moment, large particle burst, screen shake
- Dead hero's portrait greys out, "FALLEN" text
- **Lose ALL heroes = GAME OVER** (second lose condition alongside HQ destruction)
- Can recruit replacement heroes at HQ as long as ≥1 hero lives
- Replacement costs the same as original
- Lost hero's XP/veterancy is gone forever — real consequence

### Hero Scouting
- Hero walking into fog permanently reveals tiles to EXPLORED (grey)
- Hero's own vision radius (2 tiles) shows VISIBLE around them in real-time
- When hero moves away, those tiles revert to EXPLORED
- This means hero scouting reveals terrain/resources but not live enemy positions

### Hero Recruitment
- Click HQ during BUILD phase → hero recruitment menu
- Shows available hero types (greyed out if already alive)
- Each hero costs resources + 2 food upkeep per wave
- Recruited hero spawns at HQ

---

## ENEMY CAMP SYSTEM

### Camp Spawning
- **Spawn zone:** 15-tile strip around all 4 map edges
- **Initial camps:** 4 (one per edge) placed at game start in fog
- **New camps:** 1 additional camp every **10 waves** in fog tiles in the edge strip
- **Camps only spawn in UNEXPLORED or EXPLORED tiles** (NOT visible)
- **Min distance between camps:** 20 tiles

### Camp Stats
- **HP:** 40 (increases by +10 per camp level)
- **Level:** Starts at 1, increases every 10 waves globally
- **Guarded by:** 2-3 defender enemies (scale with level)
- **Invisible** until player explores within 3 tiles
- Rendered as dark red fortified icon when visible

### Camp Behavior
- Every 45 seconds: spawns a **Scout** enemy
- Scouts path toward nearest player-visible tile
- If scout reaches visible tile AND escapes back to fog → accelerates next wave
- If scout killed before returning → wave delayed by 15 seconds

### Camp Destruction
- Hero or military units attack camp to destroy
- Destroyed camp drops **loot pile:** 20 iron + 10 gold + 5 food
- Destroyed camp's edge sector goes quiet for 10 waves
- After 10 waves, new camp can spawn in that sector again

### Camp Rendering
- Dark red tent/fortress icon with skull
- Pulsing red aura in fog
- Loot pile: golden sparkle effect on ground tiles

---

## WAVE SYSTEM (Hybrid Timer + Scout)

### Wave Timing
| Timing | Value |
|---|---|
| First BUILD phase | **5 minutes** (300 seconds) |
| Subsequent BUILD phases | **2 minutes** (120 seconds) |
| Scout escape penalty | -15 seconds per scout |
| Multiple scout stacking | Yes, can reduce to minimum |
| Minimum BUILD time | 30 seconds (guaranteed) |
| Player early start | SPACE to start wave early |

### 30-Second Recall
- At T-30 seconds: "⚠️ WAVE INCOMING IN 30s — CITIZENS RETURNING"
- Citizens begin auto-pathing to nearest block/HQ
- Hero warning: "Recall your heroes! Press H"
- At T-0: wave spawns, any citizens/heroes outside are at risk

### Wave Composition (Wealth-Scaled)
```
WaveStrength = BaseStrength(waveNum) + WealthBonus
BaseStrength = 10 + waveNum * 8 + (waveNum/5)^2 * 3
WealthBonus = (storedResources × 0.5 + citizenCount × 8 + blockCount × 15) / 10
```

- Stored resources count 1× toward wealth
- Built structures count 0.5× (incentivizes building over hoarding)
- **Adaptation rubber band:** Lost >30% units last wave → next wave 20% weaker

### Wave Direction
- Waves spawn from direction of triggering camp(s)
- Multiple camps active = pincer from multiple sides
- Siege waves every 5th wave (extra brutes + siege rams)

### Enemy Types (Unchanged from Step 12)
- Raider, Runner, Brute, Enemy Archer, Warchief, Siege Ram, Swarm
- **NEW: Scout** — fast (speed 8), 4 HP, no attack, paths toward visible tiles then back to camp

---

## SCORE SYSTEM

### Tracked Metrics
| Metric | Points | Notes |
|---|---|---|
| Waves survived | ×100 | Primary metric |
| Enemies killed (total) | ×1 | |
| Hero kills | ×2 bonus | On top of base ×1 |
| Citizens alive (at death) | ×50 each | Rewards protection |
| Citizen blocks standing | ×200 each | Rewards expansion |
| Resources gathered (total) | ×0.5 | Lifetime total |
| Camps destroyed | ×150 each | Rewards offense |
| Scouts intercepted | ×25 each | Rewards vigilance |
| Time survived | ×1 per second | |
| Heroes alive (at death) | ×500 each | Big bonus |

### Display
- Running kill counter HUD during gameplay
- Full scorecard breakdown on Game Over screen
- **High score saved to localStorage**
- Game Over triggers: HQ destroyed OR all heroes dead

---

## STARTING CONDITIONS

### Starting Resources
| Resource | Amount |
|---|---|
| Wood | 80 |
| Stone | 20 |
| Metal | 5 |
| Food | 15 |
| Gold | 0 |

### Starting State
- 1 Commander hero (free)
- Full fog, "Place Your HQ" screen
- 4 enemy camps pre-placed on edges (invisible)

---

## RE-FOGGING MECHANIC

When a citizen block is destroyed:
1. Calculate which tiles were ONLY visible from that block
2. Tiles also covered by HQ or other blocks stay VISIBLE
3. Uncovered tiles revert to EXPLORED (grey)
4. Enemy camps can now spawn in those grey tiles again
5. Any enemies in the re-fogged area become invisible
6. Creates cascading danger: lose block → fog returns → camps spawn → more attacks

---

## IMPLEMENTATION STEPS

### Step 14 — Map, Fog & HQ Placement
- Expand map to 150×100
- Implement fog overlay (3 states)
- HQ placement phase at game start
- Resource deposits with durability/multi-harvest
- Distance-based resource generation
- Hero reveals fog to EXPLORED when walking
- HQ provides VISIBLE radius
- Update minimap for fog
- 5-minute first BUILD timer
- Update camera, zoom, A* limits for larger map
- **Estimated: +500 lines**

### Step 15 — Citizens & Blocks
- Citizen Block structure (toolbar, placement, rendering)
- Citizen entity AI (auto-gather, pathfinding to resources)
- 30-second recall system
- Citizens safe inside block radius during combat
- Citizen death/replacement
- Block adjacency bonuses
- Block upgrade tiers (click to upgrade)
- Citizen upkeep (food cost)
- **Estimated: +600 lines**

### Step 16 — Scout-Wave Hybrid & Enemy Camps
- Enemy camp spawning on edges in fog
- Camp rendering (when explored)
- Scout enemy type
- Scout AI (probe visible tiles → return to camp)
- Hybrid wave timer (2 min base, -15s per scout escape)
- Wealth-based wave scaling
- Camp destruction mechanics
- Loot pile drops from destroyed camps
- New camps every 10 waves
- Camp level scaling
- **Estimated: +400 lines**

### Step 17 — Multi-Hero System
- Hero roster (4 types with distinct stats/abilities)
- Hero recruitment at HQ (click HQ → menu)
- Tab to cycle active hero
- H to recall hero to HQ
- Hero permadeath (dramatic effect)
- All heroes dead = game over
- Hero portraits in top bar
- Hero vision (2-tile VISIBLE around active position)
- Each hero type's special ability
- **Estimated: +400 lines**

### Step 18 — Score, Re-Fog & Polish
- Comprehensive score tracking
- Game Over scorecard
- localStorage high score
- Re-fogging when blocks destroyed
- HQ upgrade tiers
- Balance pass (resource yields, wave scaling, costs)
- Tutorial hints for new mechanics
- Performance optimization for 150×100 + fog
- **Estimated: +300 lines**

### Step 19 — Deploy & README
- Update README with new game description
- Push final version
- Confirm GitHub Pages deployment
- Deliver live URL

---

## TOTAL ESTIMATED SIZE
Current: ~3,700 lines
Added: ~2,200 lines
**Final: ~5,900 lines / ~180KB single file**

---

## DESIGN PRINCIPLES (UNCHANGED)
- Single file, zero dependencies
- Dark aesthetic, clean typography, soft glows
- Mobile + desktop support
- Every step produces a playable build
- Ship quality — fix bugs before deploying
