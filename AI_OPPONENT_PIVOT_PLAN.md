# 🏰 HYBRID WAR PLAN — "Empire Siege: Survive & Conquer"
## Waves + AI Empires — CoD Zombies meets Civilization

> **Goal**: Keep the wave-based survival system ("How many waves can you survive?")
> as the core heartbeat AND add AI empires that build bases, train armies, and wage war.
> The wave counter is the bragging-rights metric. AI empires add strategic depth.
> You lose when your settlement falls — to waves OR to AI attacks.

> **The Feel**: "I hit wave 100 AND took out the Red Empire while fending off zombies. I'm amazing."

> **Inspiration**: CoD Zombies (wave survival bragging rights), Beyond All Reason (macro RTS),
> Civilization (expand & conquer), They Are Billions (fog danger + wave survival hybrid),
> Northgard (tile-based territory + citizens), RimWorld (survival feel).

---

## TABLE OF CONTENTS

1. [Why Hybrid Works Best](#1-why-hybrid-works-best)
2. [Two Threat Layers](#2-two-threat-layers)
3. [Wave System — The Heartbeat](#3-wave-system--the-heartbeat)
4. [AI Empire System — The Strategy](#4-ai-empire-system--the-strategy)
5. [How Waves & AI Interact](#5-how-waves--ai-interact)
6. [AI Settlement System](#6-ai-settlement-system)
7. [AI Economy & Tech](#7-ai-economy--tech)
8. [AI Military & Attack Patterns](#8-ai-military--attack-patterns)
9. [AI Personalities (BAR-Inspired)](#9-ai-personalities)
10. [Fog of War — Critical for Both Systems](#10-fog-of-war)
11. [Win/Lose Conditions](#11-winlose-conditions)
12. [Difficulty Selection Screen](#12-difficulty-selection-screen)
13. [Map Generation Changes](#13-map-generation-changes)
14. [What We Keep vs What We Cut](#14-what-we-keep-vs-cut)
15. [Performance Budget](#15-performance-budget)
16. [Implementation Phases](#16-implementation-phases)
17. [Scope Reality Check](#17-scope-reality-check)

---

## 1. WHY HYBRID WORKS BEST

### Pure Waves Problem
- Predictable — player learns the pattern, it becomes routine
- No strategic depth — no reason to expand or scout
- No replayability — every game after wave 5 feels the same

### Pure AI Problem
- No guaranteed tension — AI might not attack for 3 minutes
- No score metric — "I won" doesn't have the same bragging feel as "I survived to wave 87"
- Quiet moments with nothing happening — loses the survival feel

### Hybrid Solution: Best of Both
| Feature | Waves Provide | AI Provides |
|---------|---------------|-------------|
| Guaranteed tension | ✅ Every 60s, something is coming | ❌ AI attacks on its own schedule |
| Score metric | ✅ "I hit wave 100!" | ❌ No clear bragging number |
| Strategic depth | ❌ Always the same response | ✅ Scout, expand, counter, raid |
| Replayability | ❌ Same waves every game | ✅ AI is unpredictable |
| Fog matters | ❌ Waves come from known ring | ✅ AI base is hidden in fog |
| "Oh shit" moments | ✅ Siege wave incoming! | ✅ AI cavalry raiding my farms! |
| Endgame goal | ❌ Just "survive longer" | ✅ Destroy all AI empires |

**The magic**: Waves provide the RHYTHM. AI provides the CHAOS. Together = survival tension + strategic depth + a clear endgame + bragging rights.


---

## 2. TWO THREAT LAYERS

The game has two independent threat systems running simultaneously:

```
LAYER 1: WAVES (The Heartbeat)
────────────────────────────────
- Predictable timing (BUILD phase → COMBAT phase → BUILD phase)
- Enemies spawn from the fog ring (existing system)
- Wave counter goes up: Wave 1, 2, 3... 50... 100...
- Composition scales with wave number (narrative arc)
- Every 5th wave = siege wave (bonus heavies)
- Every 10th wave = boss wave (named bosses with mechanics)
- Waves target YOUR settlement specifically
- THIS IS YOUR SCORE — "I survived to wave 87"
- Between waves = BUILD phase (safe from waves, NOT safe from AI)

LAYER 2: AI EMPIRES (The Strategy)
────────────────────────────────
- Unpredictable timing (AI attacks when ready)
- AI armies march from their hidden bases
- AI builds settlements, trains armies, expands territory
- AI attacks player AND other AIs (whoever is weakest nearby)
- AI raids can happen DURING build phase (no safe time!)
- AI doesn't care about your wave counter — they have their own agenda
- Destroying all AI empires = optional endgame victory condition
- AI provides strategic depth the waves can't
```

### The Player's Dilemma
This creates beautiful tension:
- **During BUILD phase**: "I'm safe from waves... but is the AI about to raid me?"
- **During COMBAT phase**: "I'm fighting wave 15 AND the AI just sent cavalry at my farms!"
- **Army allocation**: "Do I send troops to raid the AI base, or keep them home for wave 20?"
- **Scouting vs defense**: "I need cavalry to scout the AI... but I need them for the next wave too"

### Key Rule: AI Attacks Can Happen Anytime
Unlike waves, AI attacks are NOT tied to the BUILD/COMBAT cycle:
- AI raids during BUILD phase = "you're never truly safe"
- AI raids during COMBAT phase = "fighting on two fronts"
- This is what makes the hybrid special — the two systems create emergent chaos

---

## 3. WAVE SYSTEM — THE HEARTBEAT

### What Stays from Current System
- BUILD phase → press SPACE → COMBAT phase → aftermath → BUILD phase
- Wave counter UI (prominent — this is the SCORE)
- Enemy spawn ring (just outside fog boundary)
- Directional waves (1-4 compass directions)
- Camp portals at spawn points
- Wave composition scaling
- Siege waves every 5th wave

### What Changes
- **Waves are ENDLESS** — no final wave, it goes forever. Wave 100, 200, 500...
- **Wave enemy types** are the wild/feral faction (different from AI military units)
- **Scaling becomes exponential** after wave 20 — keeps it challenging forever
- **Boss waves** every 10 waves (wave 10, 20, 30...) with named bosses
- **Wave preview** shows incoming composition (scout report)
- **The wave counter is BIG in the UI** — center-top, always visible

### Wave Enemy Types (Feral Horde — NOT AI units)
Wave enemies are a distinct "wild threat" faction — barbarians, beasts, undead, etc.
They are NOT the same units as AI empires. This creates two distinct threat flavors.

**Tier 1 (Waves 1-4): The Probing**
| Type | HP | DMG | Speed | Role |
|------|-----|-----|-------|------|
| Raider | 12 | 4 | 5 | Baseline melee grunt |
| Runner | 6 | 2 | 10 | Fast flanker, targets exposed buildings |
| Swarm | 3 | 1 | 9 | Overwhelm in numbers |

**Tier 2 (Waves 3-7): The Warband**
| Type | HP | DMG | Speed | Role |
|------|-----|-----|-------|------|
| Brute | 50 | 8 | 3.5 | Wall smasher |
| Skirmisher | 10 | 5 | 7 | Ranged harasser, kites melee |
| Sapper | 15 | 2 | 6 | Plants bombs on structures |

**Tier 3 (Waves 6-12): The Horde**
| Type | HP | DMG | Speed | Role |
|------|-----|-----|-------|------|
| Warchief | 35 | 6 | 5 | Aura buffer (+30% dmg, +20% speed) |
| Shieldbearer | 40 | 3 | 4 | 60% DR from front, escorts others |
| Beastmaster | 20 | 4 | 5 | Spawns 3 war dogs on death |

**Tier 4 (Waves 8+): The Siege**
| Type | HP | DMG | Speed | Role |
|------|-----|-----|-------|------|
| Siege Ram | 70 | 3 | 2.5 | Massive structure damage |
| War Shaman | 18 | 3 | 5 | Heals nearby enemies, resurrects dead |
| Ravager | 25 | 10 | 8 | Charge attack, stuns target |

### Wave Scaling (Endless Mode)
```
Waves 1-10:   Linear scaling (learn the game)
Waves 11-20:  +10% HP/DMG per wave, +15% enemy count
Waves 21-50:  +5% HP/DMG per wave, +10% enemy count (exponential feel)
Waves 51-100: +3% HP/DMG per wave, +8% enemy count (brutal endgame)
Waves 100+:   +2% HP/DMG per wave, +5% enemy count (infinity scaling)
```

### Boss Waves (Every 10th Wave)
| Wave | Boss | Mechanic |
|------|------|----------|
| 10 | Ironclad Warlord (300 HP) | Armor plates (4×50 bonus HP), war cry +50% speed |
| 20 | Plague Herald (250 HP) | Toxic trail, poison bolts, plague swarm summon |
| 30 | Siege Colossus (500 HP) | 3×3 tile, crushes buildings, splits at 50% HP |
| 40 | Shadow Khan (400 HP) | Teleports, clones self ×3, real one has crown |
| 50+ | Repeat bosses with +50% stats per cycle, stacking |

### The Wave Counter UI
```
┌──────────────────────────────────┐
│          ⚔️ WAVE 47 ⚔️           │  ← BIG, center-top, always visible
│      Enemies: 23 remaining       │
│      Best: Wave 82               │  ← Personal best tracker
└──────────────────────────────────┘
```


---

## 4. AI EMPIRE SYSTEM — THE STRATEGY

### Each AI Is a "Ghost Player"
AI empires operate independently from the wave system. They build, expand, and attack on their own schedule.

```
PLAYER                          AI OPPONENT
─────────────────────────────────────────────
Has settlement(s)         →   Has settlement(s)
Builds structures         →   Places structures (simplified)
Trains citizens           →   Abstract citizen count
Trains military units     →   Trains military units (real entities)
Gathers resources         →   Income on timer (cheats slightly)
Sends scouts              →   Sends scouts (real units in fog)
Attacks with army         →   Attacks with army (real units)
Can lose settlement       →   Can lose settlement
Reveals fog with units    →   Has its own fog (doesn't cheat on info*)
Fights waves too!         →   Also gets attacked by waves!
```

*On Brutal, AI has partial map knowledge (simulates scouting)

### CRITICAL: AI Gets Attacked by Waves Too!
This is what makes the hybrid brilliant — **waves attack EVERYONE, not just the player.**
- Each wave sends a portion of enemies toward EACH empire (player + AIs)
- AI must defend against waves just like the player
- A weak AI empire might get WIPED OUT by waves before the player even finds them
- This creates emergent drama: "Red Empire fell to wave 23... now their territory is open"
- Player can strategy: "Let the waves weaken the AI, then I'll strike their battered base"
- Difficulty controls what % of wave enemies target AIs vs player (see Section 12)

### What's "Real" vs "Abstract" for the AI

| System | Player | AI | Why |
|--------|--------|-----|-----|
| Settlement | Real tile entity | Real tile entity (visible, attackable) | Must be destroyable |
| Buildings | Real placed structures | Real placed structures (visible) | Player needs to see & destroy them |
| Citizens | Real walking entities | Abstract count (invisible) | Performance |
| Military Units | Real entities | Real entities | Must fight player units |
| Resources | Gathered by citizens | Income per second | Performance |
| Fog of War | Revealed by units | Simplified (difficulty-based) | Performance |
| Wave Defense | Player defends | AI defends too (waves hit AIs) | Fairness + emergent drama |

### Key Principle: AI Units Are REAL
When the AI sends an army, those are real units on the map with real HP, real pathfinding, real combat. The player fights them the same way they'd fight wave enemies. The difference: these units came from a base you can go destroy, AND they use mirror units (Militia, Archer, Spearman, Cavalry, Catapult) — not feral types.

---

## 5. HOW WAVES & AI INTERACT

### Wave Distribution
Each wave splits its enemy count across all surviving empires:

```javascript
// Wave enemy distribution
const WAVE_DISTRIBUTION = {
  easy:   { player: 0.70, perAI: 0.30 },  // 1 AI gets 30%
  normal: { player: 0.50, perAI: 0.25 },  // 2 AIs get 25% each
  hard:   { player: 0.40, perAI: 0.20 },  // 3 AIs get 20% each
  brutal: { player: 0.35, perAI: 0.16 },  // 4 AIs get ~16% each
};
// Remaining % = roaming (spawn in wilderness, attack whoever they find)
```

### Wave Enemies vs AI Settlements
When wave enemies reach an AI settlement:
- They attack AI buildings and units just like they'd attack the player's
- AI military units defend against waves (same combat system)
- If AI settlement HP reaches 0 from wave damage → AI is eliminated!
- This means **waves can kill AIs for you** — but AIs that survive become stronger

### AI Attacks During Waves (The Chaos)
- AI empires can attack the player DURING a wave combat phase
- This creates "fighting on two fronts" moments
- Smart players will time their attacks on AI bases DURING waves (when AI is distracted defending)
- AI also exploits this — aggressive AIs attack other empires during waves when they're weakened

### The Three-Way Dance
```
WAVES ──attack──→ PLAYER
WAVES ──attack──→ AI EMPIRES
AI EMPIRES ──attack──→ PLAYER
AI EMPIRES ──attack──→ OTHER AI EMPIRES
PLAYER ──attack──→ AI EMPIRES

Everyone is fighting everyone. Waves are the equalizer.
```

### Timeline Example (Normal Difficulty, 2 AIs)
```
00:00  Game start. Player builds. AIs build (hidden in fog).
01:00  Wave 1: 70% enemies hit player, 15% hit each AI.
02:00  BUILD phase. AI Red sends scout toward player.
03:00  Wave 2: Bigger. Player fights wave. AI Blue also fights.
03:30  AI Red's scout spots player. AI Red marks location.
04:00  BUILD phase. Player scouts east, spots AI Red's base.
05:00  Wave 3: Siege wave. AI Blue loses some buildings to waves!
05:30  AI Red sends raid toward player DURING build phase!
06:00  Wave 4 starts. Player fighting waves AND AI Red raid simultaneously!
07:00  Player counterattacks AI Red while they're weak from wave damage.
08:00  Wave 5: Boss wave. AI Red and Blue both take heavy losses.
09:00  AI Blue attacks weakened AI Red (opportunistic!).
10:00  Wave 6. AI Red eliminated by waves (settlement destroyed).
10:30  "🏴 The Red Empire has fallen!" — AI Red's territory is now open.
...
Wave 50+: Only player and AI Blue remain. Both battered by waves. Final showdown.
```


---

## 6. AI SETTLEMENT SYSTEM

### AI Settlement Placement
At game start, each AI settlement spawns (1-4 AIs based on difficulty):
- **Spoke pattern** — all empires placed at maximum distance from each other (see Section 13)
- **Minimum 40 tiles from any other settlement** (ensures fog separation)
- **On a valid GRASS cluster** (same rules as player settlement)
- **Near at least 2 resource deposits** (forest + stone/metal)
- **Position stored but hidden** until player scouts discover it

### AI Settlement Structure
The AI settlement is a real CITIZEN_BLOCK tile with:
- HP: 200 (Village) / 350 (Town) / 500 (City)
- Upgrades on a timer (every 3 minutes: Village → Town → City)
- Visual appearance: same as player settlement but **color-tinted** per AI
- Build radius: same as player (15/20/25 tiles per tier)

### AI Building Placement
AI places buildings in **predefined cluster patterns** within its build radius:

```
VILLAGE LAYOUT (spawned at game start):
  [Farm] [Farm]
  [Lumberyard] [SETTLEMENT] [Quarry]
  [Barracks]

TOWN UPGRADE (+3:00):
  [Farm] [Farm] [Farm]
  [Lumberyard] [SETTLEMENT] [Quarry]
  [Barracks] [Archery Range] [Wall segment]
  [Tower]

CITY UPGRADE (+6:00):
  [Farm] [Farm] [Farm] [Granary]
  [Mine] [Lumberyard] [SETTLEMENT] [Quarry] [Storehouse]
  [Barracks] [Archery Range] [Stable]
  [Tower] [Wall] [Tower]
  [Catapult Workshop]
```

Buildings are placed instantly but have a "construction" visual (scaffold sprite, 10s build time before functional). This makes raiding during construction rewarding.

### AI Settlement Defense
- AI always builds walls on the side facing the **nearest known threat**
- 2-4 towers placed at key positions
- A "garrison" of 5-10 units stays near the settlement at all times (30% of army)
- If any empire's army approaches, AI pulls back offensive units to defend
- AI also reserves garrison to defend against WAVES hitting their base
- AI evaluates threats from ALL directions (waves + multiple enemies)

---

## 7. AI ECONOMY & TECH

### AI Resource Income
Instead of simulating citizen gathering, the AI gets resources on a timer:

```javascript
// AI income per second (scales with buildings)
const AI_BASE_INCOME = {
  wood:  2,   // +1 per Lumberyard
  stone: 1,   // +1 per Quarry
  metal: 0.5, // +1 per Mine
  food:  3,   // +2 per Farm
  gold:  1    // +0.5 per Storehouse
};

// Difficulty multiplier
const AI_INCOME_MULT = {
  easy:   0.8,
  normal: 1.0,
  hard:   1.3,
  brutal: 1.6
};
```

### AI Tech/Upgrade Path
AI follows a fixed upgrade priority:
1. Build 2 Farms (food security)
2. Build Barracks (military access)
3. Build Lumberyard + Quarry (resource buildings)
4. Upgrade to Town (tier 2)
5. Build Archery Range + Mine
6. Build first Tower + Wall segment (wave defense!)
7. Upgrade to City (tier 3)
8. Build Stable + Catapult Workshop
9. Build Granary + Storehouse (economy boost)

**Key change from pure-AI plan**: AI prioritizes walls/towers earlier because they NEED them to survive waves. An AI without walls will get wrecked by wave enemies.

### AI Training Queue
AI trains units toward a **composition target**:

```
EARLY GAME (0-3 min):
  Target: 8 Militia, 4 Archers

MID GAME (3-6 min):
  Target: 10 Militia, 8 Archers, 4 Spearmen

LATE GAME (6+ min):
  Target: 12 Militia, 10 Archers, 6 Spearmen, 4 Cavalry, 2 Catapults
```

AI trains continuously toward these targets. If units die (to waves OR player), it replaces them.

---

## 8. AI MILITARY & ATTACK PATTERNS

### AI Decision Loop (runs every 1 second, per AI)
```
Every 1s (each AI independently):
  1. Update resource income
  2. Check training queue, start next unit if affordable
  3. Check build order, place next building if affordable
  4. Evaluate military strength vs ALL known threats

Every [attackTimer]s (from difficulty setting):
  1. Check: Am I currently defending against a wave? 
     → YES: Hold attack, defend first
     → NO: Evaluate offensive options
  2. Calculate threatScore for each known empire (player + other AIs)
  3. Pick target = weakest nearby opponent (lowest strength × distance)
  4. IF army size >= attack threshold (keeping garrison for wave defense):
     → Select attack composition (send 60-70% of army, keep 30-40% for waves)
     → Rally units at staging point
     → March toward TARGET settlement
  5. ELSE:
     → Continue building up
     → Send 1-2 scouts toward nearest unknown territory
```

### Attack Behavior
When an AI decides to attack (target = player OR another AI):

1. **Rally Phase (10s):** AI units gather at a point near the edge of AI territory
2. **March Phase:** Army moves as a group toward target settlement
3. **Combat Phase:** Units engage target defenses/army normally
4. **Retreat Condition:** If army drops below 30% strength, surviving units retreat
5. **Siege Mode:** Catapults stop at range and bombard while melee screens
6. **Opportunism:** If AI encounters another AI's army OR wave enemies mid-march, they fight on contact
7. **Wave Awareness:** AI won't send full army if a wave is imminent (keeps garrison)

### Attack Composition
AI attacks with what it has available, but tries to maintain:
- **60% melee frontline** (Militia, Spearmen)
- **30% ranged backline** (Archers)
- **10% special** (Cavalry flankers, Catapult siege)

### BAR-Inspired Flanking
- Units deal **1.5× damage from the side, 2× from behind**
- AI cavalry always tries to **loop around** and hit from behind
- This makes positioning matter more than raw numbers

### AI Scouting
- At minute 1:00, AI sends a single fast unit toward center of map
- If scout finds player settlement, AI marks its location
- On Hard+, AI sends scouts every 2 minutes
- Scouts that spot player army report back (AI adjusts attack timing)
- Player can kill scouts to deny AI information

### AI vs Wave Interaction
The AI must balance offense and defense:
- **Conservative AIs** (Turtle) never attack during waves
- **Aggressive AIs** (Rusher) attack during waves to exploit distracted enemies
- **Smart AIs** (Strategist) time attacks to hit right AFTER a wave weakens the target
- If wave kills most of an AI's army, the AI goes into "rebuild mode" (no attacks for 2 attack cycles)


---

## 9. AI PERSONALITIES (BAR-Inspired)

### 🐢 The Turtle
- **Build Priority:** Walls, Towers, Defenses first
- **Attack Timer:** 180s (slow, builds up massive army)
- **Army Composition:** Heavy melee + catapults
- **Wave Strategy:** Excellent defender — rarely loses units to waves
- **Behavior:** Rarely attacks, but when it does, it's overwhelming
- **Weakness:** Rush it early before walls go up
- **Quote:** *"They hide behind stone. Break the stone."*

### ⚔️ The Rusher
- **Build Priority:** Barracks immediately, minimal economy
- **Attack Timer:** 60s (attacks early and often with small groups)
- **Army Composition:** Lots of Militia + Runners
- **Wave Strategy:** Takes heavy wave losses (weak walls), but keeps pressure on others
- **Behavior:** Constant pressure, never lets you breathe
- **Weakness:** Economy is fragile — raid their farms, or let waves weaken them
- **Quote:** *"They come in waves of flesh and fury."*

### ⚖️ The Strategist (Default)
- **Build Priority:** Balanced economy → military
- **Attack Timer:** 120s (standard)
- **Army Composition:** Mixed, adapts to what works
- **Wave Strategy:** Builds towers early, attacks OTHER empires during waves
- **Behavior:** Scouts first, attacks with combined arms, exploits wave chaos
- **Weakness:** Predictable timing — ambush their march route
- **Quote:** *"A thinking enemy. The most dangerous kind."*

### 🏇 The Raider
- **Build Priority:** Stable ASAP, cavalry focus
- **Attack Timer:** 90s but sends cavalry raids every 45s
- **Army Composition:** Cavalry-heavy, hit-and-run
- **Wave Strategy:** Uses cavalry to raid OTHER empires during waves, minimal home defense
- **Behavior:** Doesn't siege — raids economy buildings, kills citizens, retreats
- **Weakness:** Walls and towers shut down cavalry, waves punish weak base
- **Quote:** *"They never attack the walls. They attack everything else."*

### Implementation Note
For MVP (Phase 1), ship only **The Strategist**. Add personalities in Phase 2.

---

## 10. FOG OF WAR — CRITICAL FOR BOTH SYSTEMS

Fog of war serves BOTH threat layers differently:

### Fog + Waves
- Wave enemies spawn from the **fog ring** (existing system)
- Wave preview shows composition but NOT exact spawn location
- Fog makes waves feel scary even though they're predictable
- Between waves, fog hides potential AI raids

### Fog + AI Empires
- AI settlements are **hidden in fog** until scouted
- AI army movements are invisible unless a player unit can see them
- Scouting is critical — find AI bases before they find you
- Re-fogging means you lose track of AI armies when scouts leave

### Fog States
```
VISIBLE (bright):  Unit within vision range RIGHT NOW
EXPLORED (gray):   Was visible before, but no unit nearby. Shows terrain but NOT moving units
UNEXPLORED (black): Never seen
```

### Vision Ranges
```
Militia:    4 tiles
Archer:     6 tiles
Spearman:   4 tiles
Cavalry:    7 tiles (natural scouts)
Catapult:   3 tiles (needs escort)
Citizen:    3 tiles
Tower:      6 tiles
Settlement: 8 tiles
```

### Minimap Fog Rules (Civ-Style) ✅ CONFIRMED
The minimap mirrors fog of war — AI settlements/units ONLY visible when currently scouted:

```
MINIMAP DISPLAY RULES:
─────────────────────────────────────────
UNEXPLORED tiles:  BLACK on minimap
EXPLORED tiles:    DIM terrain color (shows land shape but nothing else)
VISIBLE tiles:     BRIGHT terrain color + any entities:
                     🔵 Player units/buildings = blue dots
                     🔴 AI units/buildings = colored dots (ONLY when VISIBLE)
                     🟢 Citizens = green dots
                     ⚫ Wave enemies = dark red dots (when in vision)
```

**Multiple AI minimap colors:**
```javascript
const AI_COLORS = {
  0: '#FF4444',  // Red
  1: '#FF8800',  // Orange
  2: '#AA44FF',  // Purple
  3: '#FFCC00',  // Yellow
};
```

---

## 11. WIN/LOSE CONDITIONS

### Primary Score: Wave Counter 🏆
- The wave counter is the MAIN score metric
- "I hit wave 100!" is the bragging right
- Personal best is saved (localStorage)
- Wave counter persists even after all AIs are dead — you keep going

### You Lose When:
- **All YOUR settlements destroyed** AND **all citizens dead**
- This can happen from waves, AI attacks, or BOTH at once
- If you have citizens alive but no settlement → 60s grace period to rebuild
- Game Over screen shows: **Wave reached, AIs defeated, time survived, units trained**

### AI Elimination:
- When an AI loses ALL its settlements (to you, other AIs, OR waves):
  - That AI is **eliminated** from the game
  - Remaining buildings crumble (2s animation)
  - Remaining units scatter, become hostile to ALL, despawn after 10s
  - Announcement: "🏴 The Red Empire has fallen!"
  - Territory reverts to unclaimed

### Optional Victory: Last Empire Standing
- If you destroy all AI empires, you get a **VICTORY banner**
- But the game DOESN'T END — waves keep coming
- This creates two phases of the game:
  1. **Empire War** (early-mid): Fight AIs + survive waves simultaneously
  2. **Pure Survival** (late): All AIs dead, now it's just you vs endless waves → CoD Zombies mode
- The victory banner is a milestone, not an ending

### Scoring System
```
GAME OVER SCREEN:
─────────────────────────────────────
  ⚔️ FINAL SCORE ⚔️
  
  Wave Reached:     87          ← THE number
  Personal Best:    103
  
  Empires Defeated: 3/3
  Empire Victory:   ✅ Wave 34  ← When you killed last AI
  
  Time Survived:    47:23
  Units Trained:    234
  Buildings Built:  45
  Enemies Killed:   1,847
─────────────────────────────────────
```


---

## 12. DIFFICULTY SELECTION SCREEN

### Pre-Game Setup
Before the game starts, player sees a **Difficulty Selection Screen**:

```
┌─────────────────────────────────────────┐
│       ⚔️  CHOOSE YOUR CHALLENGE  ⚔️      │
│                                         │
│   🟢 EASY                               │
│      1 AI opponent · Waves are lighter  │
│      AI income: 0.8× · 70% waves→you   │
│                                         │
│   🟡 NORMAL                             │
│      2 AI opponents · Balanced chaos    │
│      AI income: 1.0× · 50% waves→you   │
│                                         │
│   🔴 HARD                               │
│      3 AI opponents · Aggressive AIs    │
│      AI income: 1.3× · 40% waves→you   │
│                                         │
│   💀 BRUTAL                             │
│      4 AI opponents · Relentless        │
│      AI income: 1.6× · 35% waves→you   │
│      AI has partial map knowledge        │
│                                         │
│         [Click to Start]                │
└─────────────────────────────────────────┘
```

### Difficulty Scaling Table

| Setting | AI Count | Income Mult | Attack Timer | Scout Freq | Wave→Player % | Wave→AI % (each) | AI Unit Cap | Map Knowledge |
|---------|----------|-------------|-------------|------------|---------------|-------------------|-------------|---------------|
| Easy    | 1        | 0.8×        | 150s        | 180s       | 70%           | 30%               | 25          | None          |
| Normal  | 2        | 1.0×        | 120s        | 120s       | 50%           | 25%               | 35          | None          |
| Hard    | 3        | 1.3×        | 90s         | 60s        | 40%           | 20%               | 45          | None          |
| Brutal  | 4        | 1.6×        | 60s         | 30s        | 35%           | 16%               | 50          | Partial       |

### Key Design Choices
- **More AIs = harder**, not just faster/stronger AIs
- On higher difficulties, **MORE waves hit you** (less distributed to AIs)
- On Brutal, AI has **partial map knowledge** (simulates extensive scouting)
- Each AI gets an independent personality (randomly assigned from pool)
- Waves scale the same regardless of difficulty — the wave counter is the universal score

### Implementation
```javascript
const DIFFICULTY = {
  easy:   { aiCount: 1, incomeMult: 0.8, attackTimer: 150, scoutFreq: 180, 
            wavePlayerPct: 0.70, waveAIPct: 0.30, unitCap: 25, mapKnowledge: false },
  normal: { aiCount: 2, incomeMult: 1.0, attackTimer: 120, scoutFreq: 120,
            wavePlayerPct: 0.50, waveAIPct: 0.25, unitCap: 35, mapKnowledge: false },
  hard:   { aiCount: 3, incomeMult: 1.3, attackTimer: 90,  scoutFreq: 60,
            wavePlayerPct: 0.40, waveAIPct: 0.20, unitCap: 45, mapKnowledge: false },
  brutal: { aiCount: 4, incomeMult: 1.6, attackTimer: 60,  scoutFreq: 30,
            wavePlayerPct: 0.35, waveAIPct: 0.16, unitCap: 50, mapKnowledge: true  }
};
```

---

## 13. MAP GENERATION CHANGES

### Map Size: Keep 950×632 ✅ CONFIRMED
Current map: **950 × 632 tiles** — large enough for up to 4 AI opponents with guaranteed separation.

### Spawn Placement (Multiple AIs + Wave Ring)
All empires (player + AIs) spawn at **maximum distance from each other** using a spoke pattern.
The wave spawn ring surrounds the ENTIRE map — waves attack everyone.

```
1 AI (Easy):     Player bottom-left,    AI top-right
2 AIs (Normal):  Player bottom-center,  AI1 top-left, AI2 top-right
3 AIs (Hard):    Player south,          AI1 NE, AI2 NW, AI3 east
4 AIs (Brutal):  Player south,          AI1-4 in remaining positions
```

**Minimum separation:** 40 tiles between any two settlements

**Spawn placement algorithm:**
```javascript
function placeSpawns(playerPos, aiCount, mapW, mapH) {
  const cx = mapW/2, cy = mapH/2;
  const angleStep = (2 * Math.PI) / (aiCount + 1);
  const radius = Math.min(mapW, mapH) * 0.35;
  
  const spawns = [];
  for (let i = 0; i <= aiCount; i++) {
    const angle = angleStep * i - Math.PI/2;
    spawns.push({
      x: Math.round(cx + radius * Math.cos(angle)),
      y: Math.round(cy + radius * Math.sin(angle))
    });
  }
  return spawns; // [0] = player, [1..n] = AIs
}
```

### Wave Spawn Ring
Waves spawn from the fog ring as before, BUT:
- Wave enemies that target the player spawn near the player's fog boundary
- Wave enemies that target AI empires spawn near THAT AI's fog boundary
- This means waves feel "local" — each empire fights their own wave portion
- Roaming wave enemies (the remaining %) spawn randomly in the wilderness

### Resource Distribution
```
EACH SPAWN QUADRANT:  Enough to survive (2-3 of each deposit type)
                      Mirrored for fairness
CENTER (contested):   Rich deposits — 2× metal, 2× stone, bonus gold
                      Whoever controls the center wins the economy war
BORDER ZONES:         Sparse resources, but strategic terrain (chokepoints)
```

### Map Zones (4-AI Brutal Example)
```
┌─────────────────────────────────────┐
│  AI 1 (🔴)  │  CONTESTED  │ AI 2 (🟠) │
│  spawn      │  RESOURCE   │ spawn     │
│  + waves    │  ZONE       │ + waves   │
├─────────────┤  (center)   ├───────────┤
│  AI 3 (🟣)  │  rich,open  │ AI 4 (🟡) │
│  spawn      │             │ spawn     │
│  + waves    │             │ + waves   │
├─────────────┴─────────────┴───────────┤
│           PLAYER (🔵) spawn            │
│           + waves (biggest share)     │
└─────────────────────────────────────┘
```

---

## 14. WHAT WE KEEP VS WHAT WE CUT

### ✅ KEEP (from current game)
- **Wave system** (the CORE — CoD Zombies heartbeat) ✅
- **BUILD/COMBAT phase cycle** ✅ (but AI attacks can happen during BUILD)
- **Wave counter UI** ✅ (prominently displayed — this is the score)
- **Enemy spawn ring** ✅ (for wave enemies)
- **SPACE to start wave** ✅ (player controls wave pacing)
- **Wave preview** ✅ (scout report before each wave)
- All 19 building types
- All 5 player unit types + training system
- Settlement tier system (Village→Town→City)
- Multi-resource economy
- Citizen auto-gather system
- Wall/gate system
- Tower combat system
- Formation drag (Total War style)
- Control groups (Ctrl+1/2/3)
- Morale system
- Veterancy/XP system
- V4 map generation (with zone modifications)
- Minimap

### ➕ ADD (new systems)
- AI empire opponents (1-4 based on difficulty)
- Difficulty selection screen
- AI settlement/building/training systems
- AI attack & scouting AI
- Waves attack AIs too (wave distribution)
- Civ-style minimap fog
- Empire elimination system
- Wave counter as primary score + personal best
- New wave enemy types (12 types + bosses from Enemy Rework Plan)
- Endless wave scaling

### ✂️ CUT
- Hero entity (already planned for removal)
- Pre-defined 7 enemy types → replaced by 12 new types + 3 bosses

### 🔄 MODIFY
- **Phase system:** BUILD/COMBAT stays, but AI attacks can happen during BUILD phase too
- **Wave enemies:** Feral horde faction (distinct from AI military units)
- **Wave distribution:** Split across all empires, not 100% to player
- **Difficulty:** Controls AI count + wave distribution + AI stats


---

## 15. PERFORMANCE BUDGET

### Target: 60 FPS on mid-range laptop browser

| System | Budget | Notes |
|--------|--------|-------|
| Player units | 50 max | Already supported |
| AI units (each) | 25-50 per AI | Scales with difficulty |
| Total AI units | ~100 max | 4 AIs × 25 on Brutal |
| Wave enemies | 60 max on-screen | Existing budget |
| Total entities | ~210 max | Player + AI + waves (staggered updates) |
| AI pathfinding | 1 call/2s per AI | Not every frame |
| AI decision loop | 1/second per AI | Cheap |
| Wave pathfinding | Existing budget | Already optimized |
| Fog recalculation | Staggered | 10 units/frame |
| AI buildings | 15 per AI max | Static sprites |

### Optimization Tricks
1. **AI citizens are abstract** — no entities, just a number
2. **AI pathfinding is coarse** — 4-tile grid (each cell = 4×4 real tiles)
3. **AI buildings rendered as sprites** — no complex draw logic
4. **Stagger updates** — AI units update pathfinding on rotating schedule (5 units/frame)
5. **Cull off-screen** — don't render AI units/buildings outside camera view
6. **Wave + AI unit budget shared** — if waves have 60 enemies, AI armies reduced proportionally
7. **Wave enemies targeting AIs are ABSTRACT until near player** — only render wave enemies near the player's camera

### Performance Priority
If FPS drops below 50:
1. First: reduce AI unit caps (-10 each)
2. Second: reduce wave enemy cap for AI targets (abstract more)
3. Third: increase AI pathfinding interval (1→3s)
4. Last resort: reduce max AI count by 1

---

## 16. IMPLEMENTATION PHASES

### Phase 0: Hero Removal (prerequisite)
Execute the existing HERO_REMOVAL_PLAN.md first:
- Free camera (WASD pans)
- Remove hero entity
- Unit-based fog of war
- Citizen guard system
- Smaller soldier sizes
- All 9 phases of that plan

**Estimated effort: 3-4 focused sessions**

### Phase 1: Wave Survival Enhancement 🎯
**Goal:** Upgrade the wave system to be endless with a clear score metric, new enemy types, and bosses.

1. **Wave Counter UI** (~40 lines)
   - Big center-top wave counter (always visible)
   - Personal best tracker (localStorage)
   - "NEW BEST!" celebration when surpassing record

2. **Endless Wave Scaling** (~60 lines)
   - Exponential scaling curves (HP, DMG, count per wave)
   - No "final wave" — it goes forever
   - Difficulty curve tuned for waves 1-100+

3. **New Wave Enemy Types** (~200 lines)
   - 12 types in 4 tiers (from Enemy Rework Plan)
   - Sapper, Shieldbearer, Beastmaster, War Shaman, Ravager, Skirmisher
   - Each with unique AI behavior

4. **Boss Waves** (~150 lines)
   - Every 10th wave = boss with unique mechanics
   - Ironclad Warlord (wave 10), Plague Herald (wave 20), Siege Colossus (wave 30)
   - Boss HP bar, phase transitions, death effects

5. **Wave Preview** (~40 lines)
   - Scout report panel before each wave
   - Shows composition and attack directions

**Phase 1 total: ~490 new lines**
**Estimated effort: 2-3 focused sessions**

### Phase 2: Multi-AI Empire War 🎯 SHIP THIS
**Goal:** Add 1-4 AI opponents that build, train, attack, and fight each other AND survive waves.

1. **Difficulty Selection Screen** (~80 lines)
   - HTML overlay: Easy/Normal/Hard/Brutal
   - Sets AI count, income multiplier, attack timer, wave distribution
   - Stores `gameState.difficulty` for all scaling

2. **AI Player Array** (~60 lines)
   - `aiPlayers[]` — array of AI empire objects
   - Each has: settlement, buildings[], units[], resources{}, personality, color
   - Spoke-based spawn placement

3. **AI Settlement Spawn** (~100 lines)
   - Place N AI CITIZEN_BLOCKs at calculated spawn points
   - Color-tinted visuals per AI
   - Fair resource environment (mirrored deposits)

4. **AI Building System** (~150 lines)
   - Fixed build order + timing
   - Buildings are real entities (attackable, visible when scouted)
   - AI prioritizes walls/towers for wave defense

5. **AI Economy** (~60 lines)
   - Abstract income per second per AI
   - Scale with buildings, multiply by difficulty

6. **AI Training** (~100 lines)
   - Units toward composition target (same types as player)
   - Units spawn at AI barracks, colored to match AI

7. **Wave Distribution** (~80 lines)
   - Split wave enemies across all empires based on difficulty %
   - Wave enemies that target AIs spawn near AI fog boundary
   - AI defends against waves using their garrison
   - Waves can eliminate AIs!

8. **AI Attack Loop** (~150 lines)
   - Timer-based (from difficulty)
   - Target selection: weakest nearby empire (player or other AI)
   - Rally → March → Fight → Retreat
   - Wave-aware: keeps garrison for wave defense

9. **AI Defense** (~80 lines)
   - Garrison near base (30-40% of army for wave defense)
   - Pull back if base under attack
   - Prioritize defense when settlement HP < 50%

10. **AI Elimination** (~60 lines)
    - Settlement HP = 0 → AI eliminated (from waves, player, or other AI)
    - "🏴 The Red Empire has fallen!"
    - Buildings crumble, units scatter

11. **Victory Milestone** (~40 lines)
    - All AIs dead → "EMPIRE VICTORY" banner
    - Game continues — waves keep coming
    - Pure survival mode after all AIs dead

12. **Minimap Fog (Civ-style)** (~40 lines)
    - AI dots only when tile is VISIBLE
    - Wave enemy dots in dark red
    - Each AI unique color

**Phase 2 total: ~1,000 new lines**
**Estimated effort: 4-5 focused sessions**

### Phase 3: Polish & Personality
- Re-fogging system (VISIBLE→EXPLORED when units leave)
- AI scouting (sends scouts toward nearest unknown empire)
- AI personalities (Turtle, Rusher, Strategist, Raider)
- Scout unit type (cheap, fast, no attack, 10-tile vision)
- Flanking damage bonus (1.5× side, 2× rear)
- Terrain combat bonuses (hills +range, forests +stealth)
- AI attacks during BUILD phase (the "never safe" feeling)
- Spectator mode on player elimination

**Estimated effort: 3-4 sessions**

### Phase 4: Advanced (Stretch)
- AI expansion (second settlement when economy is strong)
- AI adapts composition to counter what defeated it
- Dynamic difficulty adjustment
- Enemy camp system (persistent strategic objectives)
- Camp raiding rewards (from Enemy Rework Plan)
- Minimap threat pulse (red flash when army spotted)

**Estimated effort: 3-4 sessions**


---

## 17. SCOPE REALITY CHECK

### What's Realistic?

```
MUST HAVE (Phase 0 + Phase 1 + Phase 2):
  ✓ Hero removed, free camera, unit fog
  ✓ Endless wave system with wave counter as THE score
  ✓ New enemy types (12 types + bosses)
  ✓ Personal best tracker
  ✓ Difficulty selection screen (Easy/Normal/Hard/Brutal)
  ✓ 1-4 AI opponents based on difficulty
  ✓ AIs build bases, train armies, fight player AND each other
  ✓ Waves attack AIs too (wave distribution system)
  ✓ Civ-style minimap fog (only see AI when scouted)
  ✓ Empire elimination (by you, other AIs, OR waves!)
  ✓ Optional victory: destroy all AIs, then pure survival
  → This IS a complete game. Wave survival + empire warfare. Ship it.

NICE TO HAVE (Phase 3):
  ○ AI personalities (Turtle/Rusher/Strategist/Raider)
  ○ Re-fogging + continuous scouting need
  ○ Flanking bonus + terrain bonuses
  ○ Scout unit type
  ○ AI raids during BUILD phase
  → Makes it a GOOD game.

STRETCH (Phase 4):
  ○ AI expansion (second settlements)
  ○ Adaptive AI composition
  ○ Dynamic difficulty
  ○ Enemy camp system
  → Makes it a GREAT game.
```

### Honest Assessment
- **Phase 0 (Hero Removal):** 3-4 sessions — well-planned, will work
- **Phase 1 (Wave Enhancement):** 2-3 sessions — builds on existing system
- **Phase 2 (Multi-AI Empires):** 4-5 sessions — biggest chunk, but most systems exist
- **Phase 3 (Polish):** 3-4 sessions — incremental improvements
- **Phase 4 (Advanced):** 3-4 sessions — modular additions

**Total for complete hybrid game: ~15-20 focused sessions**
**Total for playable MVP (Phase 0+1+2): ~9-12 sessions**

### The Key Insight
The hybrid approach is EASIER to build than pure AI because:
1. **Waves already exist** — we're enhancing, not replacing
2. **Waves guarantee tension** — AI doesn't need to be aggressive to keep the game exciting
3. **Waves test AI defenses** — we don't need complex AI threat evaluation, waves do it for us
4. **AI can be simpler** — since waves provide the heartbeat, AI just needs to add strategic chaos
5. **The wave counter sells itself** — "I hit wave 100" is instantly shareable, no explanation needed

The AI doesn't need to be smart. It needs to be PRESENT — a base in the fog, an army that sometimes raids you, a threat you can choose to eliminate. The WAVES do the heavy lifting for tension. The AI adds the strategic layer that makes each game different.

---

## RECOMMENDATION

**Hybrid: Waves (CoD Zombies survival) + AI Empires (Civ strategic depth)**

Build order:
1. **Phase 0:** Execute Hero Removal Plan — already written, 9 phases
2. **Phase 1:** Enhance waves — endless mode, new enemies, bosses, wave counter as score
3. **Phase 2:** Add AI empires — difficulty screen, 1-4 AIs, wave distribution, empire war
4. **Phase 3:** Polish — personalities, re-fogging, flanking, terrain bonuses
5. **Phase 4:** Advanced — expansion, camps, adaptive AI

This gives you:
- 🧟 **CoD Zombies survival feel** — "I hit wave 100, I'm amazing"
- 🏰 **Civ strategic depth** — scout, expand, conquer AI empires
- 🎲 **Massive replayability** — AI count × personality × random map × wave RNG
- 😱 **Double tension** — fighting waves AND watching for AI raids
- 🏆 **Clear bragging metric** — the wave counter IS the score
- 🎭 **Two-phase gameplay** — empire war early, pure survival late
- 💀 **Emergent drama** — waves can kill AIs, AIs attack during waves, chaos everywhere

**Start with Hero Removal. Then wave enhancement. Then ~1,000 lines gets you a full hybrid war game.**

---

## ✅ CONFIRMED DESIGN DECISIONS

All questions resolved (2026-04-14):

| # | Question | Answer |
|---|----------|--------|
| 1 | Keep waves? | **YES** — CoD Zombies "how many waves can you survive" is the core. Wave counter = score |
| 2 | Add AI empires? | **YES** — 1-4 AI opponents that build, fight, and wage war |
| 3 | Hybrid approach? | **YES** — Waves provide heartbeat, AI provides strategic depth. Both run simultaneously |
| 4 | Waves are endless? | **YES** — No final wave. Wave 100, 200, 500... "I'm amazing" |
| 5 | Difficulty selection? | **YES** — Easy (1 AI) / Normal (2) / Hard (3) / Brutal (4) |
| 6 | AI visible on minimap? | **Only when scouted** — Civ-style, dots disappear when not in vision |
| 7 | Shared unit types? | **YES for AI** — AI uses Militia/Archer/Spearman/Cavalry/Catapult. Waves use feral types |
| 8 | Map size? | **Keep 950×632** — large enough for 4 AIs with spoke-based spawns |
| 9 | Multiple AIs fight each other? | **YES** — all fighting for biggest empire, player is just another empire |
| 10 | Attack warnings? | **NO for AI** — hidden tension. YES for waves — wave preview scout report |
| 11 | Waves attack AIs too? | **YES** — wave distribution based on difficulty. Waves can eliminate AIs |
| 12 | Game ends when all AIs dead? | **NO** — Victory banner, but waves keep coming. Pure survival after empire war |
| 13 | AI attacks during BUILD phase? | **YES (Phase 3)** — "you're never truly safe" |
| 14 | Wave enemy types? | **Feral horde** — distinct faction from AI military (12 types + 3 bosses) |

