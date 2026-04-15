# 🏰 HYBRID WAR PLAN — "Empire Siege: Survive & Conquer"
## Waves + 1 AI Empire — CoD Zombies meets "All vs The User"

> **Goal**: Keep the wave-based survival system ("How many waves can you survive?")
> as the core heartbeat AND add ONE AI empire that builds, trains, expands, and wages war.
> Waves ONLY attack the player. The AI is a separate, independent strategic threat.
> The wave counter is the bragging-rights metric. The AI adds strategic depth.
> You lose when your settlement falls — to waves OR to the AI.

> **The Feel**: "I hit wave 100 AND took out the AI Empire while fending off hordes. I'm amazing."

> **Core Tension**: Waves weaken YOU but never touch the AI.
> While you're burning resources fighting wave 47, the AI is quietly massing cavalry.
> You're fighting on two fronts. The AI is fighting on zero.

> **Inspiration**: CoD Zombies (wave survival bragging rights), Beyond All Reason (macro RTS),
> Civilization (expand & conquer), They Are Billions (fog danger + wave survival hybrid),
> Northgard (tile-based territory + citizens), RimWorld (survival feel).

---

## TABLE OF CONTENTS

1. [Why "All vs The User" Works](#1-why-all-vs-the-user-works)
2. [Two Threat Layers](#2-two-threat-layers)
3. [Wave System — The Heartbeat](#3-wave-system--the-heartbeat)
4. [AI Empire System — The Strategy](#4-ai-empire-system--the-strategy)
5. [How Waves & AI Interact (They Don't)](#5-how-waves--ai-interact)
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

## 1. WHY "ALL VS THE USER" WORKS

### The Asymmetry Is the Game
In most RTS games, all factions face the same threats. But "All vs The User" creates a
beautiful **asymmetric pressure** that makes every decision agonizing:

| | Player | AI |
|---|---|---|
| Fights waves? | **YES — every 60s** | **NO — immune** |
| Fights the other empire? | YES | YES |
| Resources burned on defense? | **Massive (waves + AI)** | **Only on player attacks** |
| Free to expand? | No — must defend base from waves | **YES — uncontested growth** |
| Army always at full strength? | Rarely — waves chip away | **Yes — unless player raids** |

### Why This Creates Great Tension

1. **The AI grows unchecked** — while you're fighting wave 15, the AI is building its 3rd
   barracks and training cavalry. Every wave you survive, the AI gets relatively stronger.

2. **Resource dilemma** — you need walls and towers FOR WAVES and soldiers FOR THE AI.
   Every gold spent on a tower is a soldier you didn't train.

3. **Timing pressure** — you MUST find and weaken the AI before it becomes overwhelming.
   But scouting costs units you need for wave defense.

4. **The player's unique burden** — waves are YOUR problem. The AI gets a free pass.
   This makes destroying the AI feel earned: "I beat them while also surviving wave 73."

5. **Natural difficulty curve** — early game, waves are easy and the AI is weak.
   Late game, waves are brutal AND the AI has a maxed-out army. Pressure from both sides.

### Compared to Waves-Attack-Everyone
The old plan (waves attack all empires) had problems:
- Waves could randomly kill AIs, removing strategic challenge you didn't earn
- Player could turtle and let waves do the work
- Wave distribution math was complex and hard to balance
- The AI spending resources on wave defense made it weaker and less threatening

**"All vs The User" is simpler, more intense, and creates clearer decisions.**

---

## 2. TWO THREAT LAYERS

The game has two independent threat systems. They NEVER interact with each other —
they both target only YOU.

```
LAYER 1: WAVES (The Heartbeat)
────────────────────────────────
- Predictable timing (BUILD phase → COMBAT phase → BUILD phase)
- Enemies spawn from the fog ring (existing system)
- Wave counter goes up: Wave 1, 2, 3... 50... 100...
- Composition scales with wave number (narrative arc)
- Every 5th wave = siege wave (bonus heavies)
- Every 10th wave = boss wave (named bosses with mechanics)
- Waves target YOUR settlement ONLY — AI is immune
- THIS IS YOUR SCORE — "I survived to wave 87"
- Between waves = BUILD phase (safe from waves, NOT safe from AI)

LAYER 2: THE AI EMPIRE (The Strategy)
────────────────────────────────
- Unpredictable timing (AI attacks when ready)
- AI army marches from its hidden base
- AI builds settlement, trains army, expands territory
- AI attacks ONLY the player (you're its only enemy)
- AI raids can happen DURING build phase (no safe time!)
- AI doesn't care about your wave counter — it has its own agenda
- Destroying the AI = optional endgame victory condition
- AI is NEVER weakened by waves — it grows freely
- The longer you wait to deal with the AI, the stronger it gets
```

### The Player's Dilemma
This creates beautiful tension:
- **During BUILD phase**: "I'm safe from waves... but is the AI about to raid me?"
- **During COMBAT phase**: "I'm fighting wave 15 AND the AI just sent cavalry at my farms!"
- **Army allocation**: "Do I send troops to raid the AI base, or keep them home for wave 20?"
- **Economy split**: "Towers for waves or soldiers for the AI? I can't afford both!"
- **Timing**: "The AI is getting stronger every minute I spend fighting waves..."

### Key Rule: AI Attacks Can Happen Anytime
Unlike waves, AI attacks are NOT tied to the BUILD/COMBAT cycle:
- AI raids during BUILD phase = "you're never truly safe"
- AI raids during COMBAT phase = "fighting on two fronts"
- This is what makes the hybrid special — the two systems create emergent chaos

### Key Rule: The AI Is Immune to Waves
- Wave enemies completely ignore the AI settlement and units
- AI units and wave enemies can coexist on the map without fighting
- This is simple to implement: wave enemy target = always playerSettlement
- The AI is YOUR problem to deal with. Waves won't do it for you.

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
- **ALL wave enemies target the player** — 100% aimed at your settlement (simplified!)

### Wave Enemy Types (Feral Horde — NOT AI units)
Wave enemies are a distinct "wild threat" faction — barbarians, beasts, undead, etc.
They are NOT the same units as the AI empire. This creates two distinct threat flavors.

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

### The AI Is a "Ghost Player" — But Waves-Immune
The AI empire operates COMPLETELY independently from the wave system. It builds, expands,
and attacks on its own schedule. Crucially, **waves never touch it**.

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
Can lose settlement       →   Can lose settlement (only to player!)
Reveals fog with units    →   Has its own fog (doesn't cheat on info*)
Fights waves              →   IMMUNE TO WAVES
```

*On Brutal, AI has partial map knowledge (simulates scouting)

### CRITICAL: The AI Never Fights Waves
This is the key asymmetry that makes the game intense:
- **The AI uses ALL its resources on building up and attacking you**
- It never needs walls or towers for wave defense — only for YOUR attacks
- It never loses units to waves — its army only shrinks when YOU fight it
- This means the AI **always has a stronger army** relative to a player who's
  burning resources on wave defense
- The only way to weaken the AI is to **actively raid it**
- If you ignore the AI, it snowballs into an unstoppable force

### Why This Is Better Than Waves-Attack-AI
| Old Design | New Design |
|---|---|
| Waves randomly weaken AIs | AI army always at full strength |
| Player can turtle, let waves kill AI | Player MUST engage AI actively |
| Complex wave distribution math | Simple: all waves → player |
| AI wastes resources on wave defense | AI focuses all resources on attacking you |
| AI might die to waves (unsatisfying) | AI only dies to YOUR attack (earned victory) |

### What's "Real" vs "Abstract" for the AI

| System | Player | AI | Why |
|--------|--------|-----|-----|
| Settlement | Real tile entity | Real tile entity (visible, attackable) | Must be destroyable |
| Buildings | Real placed structures | Real placed structures (visible) | Player needs to see & destroy them |
| Citizens | Real walking entities | Abstract count (invisible) | Performance |
| Military Units | Real entities | Real entities | Must fight player units |
| Resources | Gathered by citizens | Income per second | Performance |
| Fog of War | Revealed by units | Simplified (difficulty-based) | Performance |
| Wave Defense | Player defends against waves | **N/A — IMMUNE** | Core asymmetry |

### Key Principle: AI Units Are REAL
When the AI sends an army, those are real units on the map with real HP, real pathfinding,
real combat. The player fights them the same way they'd fight wave enemies. The difference:
- These units came from a base you can go destroy
- They use mirror units (Militia, Archer, Spearman, Cavalry, Catapult) — not feral types
- They retreat when weakened (wave enemies fight to the death)
- The AI replaces them for free (no wave damage eating its reserves)

---

## 5. HOW WAVES & AI INTERACT (THEY DON'T)

### Separation of Concerns
Waves and the AI are **completely independent systems** that never interact directly:

```
WAVES ──attack──→ PLAYER ←──attack── AI EMPIRE
                    ↓
              PLAYER ──attack──→ AI EMPIRE

That's it. Two arrows pointing at you. One arrow you can point back.
```

### What This Means in Practice:
- **Wave enemies ignore AI** — they pathfind to YOUR settlement only
- **AI units ignore wave enemies** — they don't fight ferals
- **Wave enemies and AI units can coexist** — they pass through each other on the map
- **No wave distribution system needed** — 100% of wave enemies target the player
- **No AI wave defense needed** — AI doesn't need walls/towers for waves

### The "Two-Front War" Moments
Even though the systems don't interact, they create incredible pressure when they overlap:

```
SCENARIO: Wave 15 is incoming. AI cavalry spotted approaching from the east.

Option A: Send all troops to defend the wave spawn (west).
  → Wave defended ✅, but AI cavalry raids your unprotected farms ❌

Option B: Split army — half west for wave, half east for AI raid.
  → Both defenses are weaker. You might lose troops on both fronts ⚠️

Option C: Let towers handle the wave, send army to intercept AI cavalry.
  → Works if towers are strong enough. If not, wall breach! ❌

Option D: Ignore the AI raid, focus the wave, counterattack AI base after.
  → Accept farm losses now, hit back harder later 🤔
```

**This is the game.** Every wave becomes a question: "Can I afford to split my attention?"

### Timeline Example (Normal Difficulty)
```
00:00  Game start. Player builds. AI builds (hidden in fog).
01:00  Wave 1: All enemies target player. AI is building peacefully.
02:00  BUILD phase. AI sends a scout toward center of map.
03:00  Wave 2: Player fights wave. Meanwhile AI finishes its barracks.
03:30  AI scout spots player. AI marks player's location.
04:00  BUILD phase. Player scouts east, spots AI base through fog.
05:00  Wave 3: Siege wave. Player needs all troops. AI trains 6 more militia.
05:30  BUILD phase. AI now has 12 militia, 6 archers. Player has 8 militia, lost 3 to waves.
06:00  AI sends first raid (8 militia + 4 archers) toward player!
06:30  Wave 4 starts. Player fighting waves AND AI raid simultaneously!
       AI still has 6 units at home (garrison). Player is stretched thin.
07:00  Player beats wave 4, but lost 4 soldiers. AI raid killed 2 farms.
07:30  BUILD phase. Player faces choice: rebuild farms or train soldiers?
       AI is already training replacements for its raid losses.
08:00  Wave 5: Boss wave. Player barely survives with damaged economy.
08:30  Player decides to go on offense — sends 10 troops to raid AI base.
       But wave 6 is coming in 90 seconds... will they make it back in time?
09:00  Player troops reach AI base, destroy a barracks. AI garrison fights back.
09:30  Wave 6 is about to start. Player's raiding force is still at the AI base!
       Player's HOME defense: just towers + 3 militia. Is it enough?
...
Wave 50+: AI has a massive army. Player is juggling wave defense + AI raids every 2 minutes.
          The pressure is relentless from both sides.
```

---

## 6. AI SETTLEMENT SYSTEM

### AI Settlement Placement
At game start, exactly 1 AI settlement spawns:
- **Opposite side of the map from the player** (maximum distance)
- **Minimum 40 tiles from player settlement** (ensures fog separation)
- **On a valid GRASS cluster** (same rules as player settlement)
- **Near at least 2 resource deposits** (forest + stone/metal)
- **Position stored but hidden** until player scouts discover it

### Spawn Placement
```
Player spawns in the SOUTH portion of the map.
AI spawns in the NORTH portion of the map.
Maximum separation ensures early-game fog hides both empires.

┌─────────────────────────────────────┐
│         AI EMPIRE (🔴)              │
│         Hidden in fog               │
│                                     │
│      ~~~ contested zone ~~~         │
│      (rich resources in center)     │
│                                     │
│         PLAYER (🔵)                 │
│         + wave spawn ring           │
└─────────────────────────────────────┘
```

### AI Settlement Structure
The AI settlement is a real CITIZEN_BLOCK tile with:
- HP: 200 (Village) / 350 (Town) / 500 (City)
- Upgrades on a timer (every 3 minutes: Village → Town → City)
- Visual appearance: same as player settlement but **RED-tinted**
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
  [Barracks] [Archery Range]
  [Tower]

CITY UPGRADE (+6:00):
  [Farm] [Farm] [Farm] [Granary]
  [Mine] [Lumberyard] [SETTLEMENT] [Quarry] [Storehouse]
  [Barracks] [Archery Range] [Stable]
  [Tower] [Wall] [Tower]
  [Catapult Workshop]
```

Buildings are placed instantly but have a "construction" visual (scaffold sprite,
10s build time before functional). This makes raiding during construction rewarding.

**NOTE:** AI does NOT build walls/towers for wave defense (it doesn't need them).
AI only builds defensive structures when it detects player scouting or after being raided.
This means early raids can catch the AI wide open — rewarding aggression!

### AI Settlement Defense
- AI initially focuses on economy and military — minimal walls
- After first player contact (scout spotted or raid received):
  - AI builds walls facing the direction the player came from
  - AI places 2-4 towers at key positions
- A "garrison" of 30-40% of army stays near settlement at all times
- If player army approaches, AI pulls back offensive units to defend
- AI evaluates threats from the player's direction only

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
  easy:   0.6,
  normal: 1.0,
  hard:   1.4,
  brutal: 1.8
};
```

### AI Tech/Upgrade Path
AI follows a fixed upgrade priority:
1. Build 2 Farms (food security)
2. Build Barracks (military access)
3. Build Lumberyard + Quarry (resource buildings)
4. Upgrade to Town (tier 2)
5. Build Archery Range + Mine
6. Upgrade to City (tier 3)
7. Build Stable + Catapult Workshop
8. Build Granary + Storehouse (economy boost)
9. Build defenses (walls/towers) — **only after player contact**

**Key change from old plan**: AI does NOT prioritize walls/towers early because it
doesn't need them for waves. This makes early raiding the AI VERY rewarding — disrupt
them before they build defenses.

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

AI trains continuously toward these targets. If units die (only to PLAYER attacks),
it replaces them. Since waves never kill AI units, the AI's army steadily grows
unless the player actively raids.


---

## 8. AI MILITARY & ATTACK PATTERNS

### AI Decision Loop (runs every 1 second)
```
Every 1s:
  1. Update resource income
  2. Check training queue, start next unit if affordable
  3. Check build order, place next building if affordable
  4. Evaluate military strength vs player (if player location known)

Every [attackTimer]s (from difficulty setting):
  1. Check: Do I know where the player is?
     → NO: Send scout toward center / unexplored territory
     → YES: Evaluate offensive options
  2. Calculate: myArmyStrength vs estimated player strength
  3. IF army size >= attack threshold:
     → Select attack composition (send 60-70% of army, keep 30-40% garrison)
     → Rally units at staging point
     → March toward PLAYER settlement
  4. ELSE:
     → Continue building up
     → Send 1-2 scouts toward player territory
```

### Attack Behavior
When the AI decides to attack:

1. **Rally Phase (10s):** AI units gather at a point near the edge of AI territory
2. **March Phase:** Army moves as a group toward player settlement
3. **Combat Phase:** Units engage player defenses/army normally
4. **Retreat Condition:** If army drops below 30% strength, surviving units retreat
5. **Siege Mode:** Catapults stop at range and bombard while melee screens
6. **Opportunism:** If AI encounters player units mid-march, they fight on contact
7. **NO wave awareness needed:** AI doesn't care about waves — they're not its problem

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

### AI Timing Exploitation (The Cruel Part)
Since the AI knows waves only attack the player, smart AI can exploit this:
- **Strategist AI:** Times attacks to land DURING a wave combat phase
  (player is distracted fighting waves, AI hits from the other direction)
- **Raider AI:** Sends cavalry raids during EVERY wave (guaranteed the player is busy)
- **Turtle AI:** Waits until player is weakened after a boss wave, then sends everything
- This creates the "fighting on two fronts" feeling that makes the game special

---

## 9. AI PERSONALITIES (BAR-Inspired)

Since there's always exactly 1 AI, the personality is selected based on difficulty
(or randomly for replayability):

### 🐢 The Turtle (Easy Default)
- **Build Priority:** Economy first, then military mass
- **Attack Timer:** 180s (slow, builds up massive army)
- **Army Composition:** Heavy melee + catapults
- **Behavior:** Rarely attacks, but when it does, it's overwhelming
- **Timing:** Attacks during BUILD phase (gives player time to react)
- **Weakness:** Rush it early before it masses up
- **Quote:** *"They hide behind stone. Break the stone."*

### ⚔️ The Rusher (Hard Default)
- **Build Priority:** Barracks immediately, minimal economy
- **Attack Timer:** 60s (attacks early and often with small groups)
- **Army Composition:** Lots of Militia + Runners
- **Behavior:** Constant pressure, never lets you breathe
- **Timing:** Attacks constantly, overlapping with waves for maximum chaos
- **Weakness:** Economy is fragile — raid their farms
- **Quote:** *"They come in waves of flesh and fury."*

### ⚖️ The Strategist (Normal Default)
- **Build Priority:** Balanced economy → military
- **Attack Timer:** 120s (standard)
- **Army Composition:** Mixed, adapts to what works
- **Behavior:** Scouts first, attacks with combined arms
- **Timing:** Times attacks to land during wave combat phase (cruel!)
- **Weakness:** Predictable timing — ambush their march route
- **Quote:** *"A thinking enemy. The most dangerous kind."*

### 🏇 The Raider (Brutal Default)
- **Build Priority:** Stable ASAP, cavalry focus
- **Attack Timer:** 90s but sends cavalry raids every 45s
- **Army Composition:** Cavalry-heavy, hit-and-run
- **Behavior:** Doesn't siege — raids economy buildings, kills citizens, retreats
- **Timing:** Sends cavalry during EVERY wave to exploit distraction
- **Weakness:** Walls and towers shut down cavalry
- **Quote:** *"They never attack the walls. They attack everything else."*

### Personality Assignment
```javascript
const DIFFICULTY_PERSONALITY = {
  easy:   'turtle',      // Forgiving — slow attacks, player has time to learn
  normal: 'strategist',  // Balanced — smart but not overwhelming
  hard:   'rusher',      // Relentless — constant pressure + wave pressure
  brutal: 'raider',      // Cruel — cavalry raids during every wave
};
// Optional: random personality for "Chaotic" mode (unlock after first win?)
```

### Implementation Note
For MVP (Phase 2), ship **The Strategist** only (works for all difficulties with
timer adjustments). Add personality variations in Phase 3.

---

## 10. FOG OF WAR — CRITICAL FOR BOTH SYSTEMS

Fog of war serves BOTH threat layers differently:

### Fog + Waves
- Wave enemies spawn from the **fog ring** (existing system)
- Wave preview shows composition but NOT exact spawn location
- Fog makes waves feel scary even though they're predictable
- Between waves, fog hides potential AI raids

### Fog + AI Empire
- AI settlement is **hidden in fog** until scouted
- AI army movements are invisible unless a player unit can see them
- Scouting is critical — find the AI base before it gets too strong
- Re-fogging means you lose track of AI army when scouts leave
- **The AI grows in the dark** — every moment you haven't scouted, it's building

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
The minimap mirrors fog of war — AI settlement/units ONLY visible when currently scouted:

```
MINIMAP DISPLAY RULES:
─────────────────────────────────────────
UNEXPLORED tiles:  BLACK on minimap
EXPLORED tiles:    DIM terrain color (shows land shape but nothing else)
VISIBLE tiles:     BRIGHT terrain color + any entities:
                     🔵 Player units/buildings = blue dots
                     🔴 AI units/buildings = RED dots (ONLY when VISIBLE)
                     🟢 Citizens = green dots
                     ⚫ Wave enemies = dark red dots (when in vision)
```

**AI color: always RED** (single AI, single color — simple)


---

## 11. WIN/LOSE CONDITIONS

### Primary Score: Wave Counter 🏆
- The wave counter is the MAIN score metric
- "I hit wave 100!" is the bragging right
- Personal best is saved (localStorage)
- Wave counter persists even after AI is dead — you keep going

### You Lose When:
- **All YOUR settlements destroyed** AND **all citizens dead**
- This can happen from waves, AI attacks, or BOTH at once
- If you have citizens alive but no settlement → 60s grace period to rebuild
- Game Over screen shows: **Wave reached, AI defeated (yes/no), time survived, units trained**

### AI Elimination:
- When the AI loses ALL its settlements (to YOUR attack only):
  - The AI is **eliminated** from the game
  - Remaining buildings crumble (2s animation)
  - Remaining AI units scatter, become hostile to ALL, despawn after 10s
  - Announcement: "🏴 The Enemy Empire has fallen!"
  - Territory reverts to unclaimed
  - **This is a PLAYER achievement** — waves can't do this for you

### Optional Victory: Empire Destroyed
- When you destroy the AI empire, you get a **VICTORY banner**
- But the game DOESN'T END — waves keep coming
- This creates two phases of the game:
  1. **Empire War** (early-mid): Fight the AI + survive waves simultaneously
  2. **Pure Survival** (late): AI is dead, now it's just you vs endless waves → CoD Zombies mode
- The victory banner is a milestone, not an ending
- Players compete on: "At what WAVE did you kill the AI?" + "How far did you survive after?"

### Scoring System
```
GAME OVER SCREEN:
─────────────────────────────────────
  ⚔️ FINAL SCORE ⚔️
  
  Wave Reached:     87          ← THE number
  Personal Best:    103
  
  Empire Defeated:  ✅ Wave 34  ← When you killed the AI
       — OR —
  Empire Defeated:  ❌          ← You died before killing the AI
  
  Time Survived:    47:23
  Units Trained:    234
  Buildings Built:  45
  Enemies Killed:   1,847
  Difficulty:       Normal (Strategist AI)
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
│      Passive AI · Lighter waves         │
│      AI: Turtle (slow build, rare attack│
│      Waves: 0.8× HP/count              │
│                                         │
│   🟡 NORMAL                             │
│      Balanced AI · Standard waves       │
│      AI: Strategist (smart, timed raids)│
│      Waves: 1.0× HP/count              │
│                                         │
│   🔴 HARD                               │
│      Aggressive AI · Tough waves        │
│      AI: Rusher (constant pressure)     │
│      Waves: 1.2× HP/count              │
│                                         │
│   💀 BRUTAL                             │
│      Relentless AI · Punishing waves    │
│      AI: Raider (cavalry during waves)  │
│      Waves: 1.5× HP/count              │
│      AI has partial map knowledge        │
│                                         │
│         [Click to Start]                │
└─────────────────────────────────────────┘
```

### Difficulty Scaling Table

Since AI count is always 1, difficulty scales through INTENSITY:

| Setting | AI Personality | AI Income | AI Attack Timer | AI Scout Freq | AI Unit Cap | Wave HP/Count Mult | Wave Scaling | Map Knowledge |
|---------|---------------|-----------|----------------|---------------|-------------|-------------------|--------------|---------------|
| Easy    | Turtle        | 0.6×      | 180s           | Never*        | 25          | 0.8×              | Slower       | None          |
| Normal  | Strategist    | 1.0×      | 120s           | 120s          | 35          | 1.0×              | Standard     | None          |
| Hard    | Rusher        | 1.4×      | 60s            | 60s           | 45          | 1.2×              | Faster       | None          |
| Brutal  | Raider        | 1.8×      | 45s+cavalry30s | 30s           | 55          | 1.5×              | Aggressive   | Partial       |

*Easy AI doesn't scout — it waits for the player to come to it.

### Key Design Choices
- **1 AI always** — difficulty comes from AI behavior + wave intensity, not AI count
- **Personality matches difficulty** — Turtle for easy, Raider for brutal (thematic)
- **Waves ALSO scale with difficulty** — on Brutal, waves are 1.5× AND the AI is relentless
- **No wave distribution** — 100% of wave enemies always target the player
- **On Brutal, AI has partial map knowledge** (simulates extensive scouting)
- **Wave counter is the universal score** — same scaling formula, difficulty shown on score screen

### Implementation
```javascript
const DIFFICULTY = {
  easy:   { personality: 'turtle',     incomeMult: 0.6, attackTimer: 180, 
            scoutFreq: Infinity, unitCap: 25, waveHPMult: 0.8,
            waveCountMult: 0.8, mapKnowledge: false },
  normal: { personality: 'strategist', incomeMult: 1.0, attackTimer: 120,
            scoutFreq: 120,     unitCap: 35, waveHPMult: 1.0,
            waveCountMult: 1.0, mapKnowledge: false },
  hard:   { personality: 'rusher',     incomeMult: 1.4, attackTimer: 60,
            scoutFreq: 60,      unitCap: 45, waveHPMult: 1.2,
            waveCountMult: 1.2, mapKnowledge: false },
  brutal: { personality: 'raider',     incomeMult: 1.8, attackTimer: 45,
            scoutFreq: 30,      unitCap: 55, waveHPMult: 1.5,
            waveCountMult: 1.5, mapKnowledge: true  }
};
```

---

## 13. MAP GENERATION CHANGES

### Map Size: Keep 950×632 ✅ CONFIRMED
Current map: **950 × 632 tiles** — large enough for 2 empires (player + 1 AI)
with guaranteed fog separation and a contested center zone.

### Spawn Placement (Player + 1 AI)
Player and AI spawn on **opposite sides** of the map for maximum distance.
Wave spawn ring ONLY surrounds the player's territory.

```
Player → SOUTH portion of map (bottom third)
AI     → NORTH portion of map (top third)
Center → Contested resource zone (rich deposits, strategic terrain)
```

**Minimum separation:** 40 tiles between settlements

**Spawn placement:**
```javascript
function placeSpawns(mapW, mapH) {
  const padding = 60; // tiles from edge
  return {
    player: { x: Math.round(mapW * 0.5), y: mapH - padding },
    ai:     { x: Math.round(mapW * 0.5), y: padding }
  };
}
// Jitter ±30 tiles for variety
```

### Wave Spawn Ring
Waves spawn from the fog ring as before:
- **ALL wave enemies target the player's settlement** (simple pathfinding)
- Wave spawn ring is centered on the PLAYER'S fog boundary (not the whole map)
- AI settlement is far enough that wave enemies never accidentally wander near it
- If a wave enemy somehow pathfinds past the AI base, it ignores it completely

### Resource Distribution
```
PLAYER QUADRANT (south):  Standard resources, enough to survive
CENTER (contested):       Rich deposits — 2× metal, 2× stone, bonus gold
                          Whoever controls the center wins the economy war
AI QUADRANT (north):      Mirrored resources (fair start for AI)
BORDER ZONES:             Sparse resources, but strategic terrain (chokepoints)
```

### Map Layout
```
┌─────────────────────────────────────┐
│         AI SETTLEMENT (🔴)          │
│         + AI buildings              │
│         (hidden in fog)             │
│                                     │
│  ─ ─ ─ AI TERRITORY ─ ─ ─ ─ ─ ─   │
│                                     │
│   ░░░ CONTESTED ZONE ░░░           │
│   ░░░ (rich resources) ░░░         │
│   ░░░ (chokepoints)   ░░░         │
│                                     │
│  ─ ─ ─ PLAYER TERRITORY ─ ─ ─ ─   │
│                                     │
│       WAVE SPAWN RING (around      │
│       player's fog boundary)        │
│         PLAYER SETTLEMENT (🔵)      │
└─────────────────────────────────────┘
```

---

## 14. WHAT WE KEEP VS WHAT WE CUT

### ✅ KEEP (from current game)
- **Wave system** (the CORE — CoD Zombies heartbeat) ✅
- **BUILD/COMBAT phase cycle** ✅ (but AI attacks can happen during BUILD)
- **Wave counter UI** ✅ (prominently displayed — this is the score)
- **Enemy spawn ring** ✅ (for wave enemies, targeting player only)
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
- 1 AI empire opponent (always present, never killed by waves)
- Difficulty selection screen (Easy/Normal/Hard/Brutal)
- AI settlement/building/training systems
- AI attack & scouting AI
- AI personality system (Turtle/Rusher/Strategist/Raider)
- Civ-style minimap fog
- Empire elimination system (player-earned only)
- Wave counter as primary score + personal best
- New wave enemy types (12 types + bosses from Enemy Rework Plan)
- Endless wave scaling
- Wave HP/count scaling by difficulty

### ✂️ CUT
- Hero entity (already planned for removal)
- Pre-defined 7 enemy types → replaced by 12 new types + 3 bosses
- Wave distribution system (was: split waves across empires — now: 100% to player)
- Multiple AI opponents (was: 1-4 based on difficulty — now: always 1)
- AI wave defense code (AI doesn't need it — immune to waves)

### 🔄 MODIFY
- **Phase system:** BUILD/COMBAT stays, but AI attacks can happen during BUILD phase too
- **Wave enemies:** Feral horde faction (distinct from AI military units)
- **Wave targeting:** ALL wave enemies → player only (simplified, no distribution)
- **Difficulty:** Controls AI personality + AI stats + wave intensity (not AI count)


---

## 15. PERFORMANCE BUDGET

### Target: 60 FPS on mid-range laptop browser

| System | Budget | Notes |
|--------|--------|-------|
| Player units | 50 max | Already supported |
| AI units | 55 max | Scales with difficulty (25-55) |
| Wave enemies | 60 max on-screen | Existing budget |
| Total entities | ~165 max | Player + AI + waves |
| AI pathfinding | 1 call/2s | Not every frame |
| AI decision loop | 1/second | Cheap |
| Wave pathfinding | Existing budget | Already optimized |
| Fog recalculation | Staggered | 10 units/frame |
| AI buildings | 15 max | Static sprites |

### Why 1 AI Is Better for Performance
The old plan (1-4 AIs) had a total entity budget of ~210 with complex wave
distribution across multiple AI bases. The new plan (1 AI) is significantly simpler:

- **~165 max entities** vs ~210 (25% fewer)
- **1 AI decision loop** vs 4 (75% less AI computation)
- **No wave distribution math** (100% to player, simple)
- **No abstract wave-vs-AI combat** (was needed for off-screen AI wave defense)
- **1 AI pathfinding context** vs 4

### Optimization Tricks
1. **AI citizens are abstract** — no entities, just a number
2. **AI pathfinding is coarse** — 4-tile grid (each cell = 4×4 real tiles)
3. **AI buildings rendered as sprites** — no complex draw logic
4. **Stagger updates** — AI units update pathfinding on rotating schedule (5 units/frame)
5. **Cull off-screen** — don't render AI units/buildings outside camera view
6. **Wave enemy budget shared with entity count** — if waves have 60 enemies, manageable

### Performance Priority
If FPS drops below 50:
1. First: reduce AI unit cap (-10)
2. Second: reduce wave enemy cap
3. Third: increase AI pathfinding interval (1→3s)
4. Last resort: reduce visual effects

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
**Goal:** Upgrade the wave system to be endless with a clear score metric, new
enemy types, and bosses.

1. **Wave Counter UI** (~40 lines)
   - Big center-top wave counter (always visible)
   - Personal best tracker (localStorage)
   - "NEW BEST!" celebration when surpassing record

2. **Endless Wave Scaling** (~60 lines)
   - Exponential scaling curves (HP, DMG, count per wave)
   - No "final wave" — it goes forever
   - Difficulty-based wave multiplier (0.8× Easy → 1.5× Brutal)

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

### Phase 2: AI Empire (1 Opponent) 🎯 SHIP THIS
**Goal:** Add 1 AI opponent that builds, trains, attacks independently from waves.

1. **Difficulty Selection Screen** (~80 lines)
   - HTML overlay: Easy/Normal/Hard/Brutal
   - Sets AI personality, income mult, attack timer, wave scaling
   - Stores `gameState.difficulty` for all scaling

2. **AI Player Object** (~40 lines)
   - `aiPlayer` — single AI empire object
   - Has: settlement, buildings[], units[], resources{}, personality, color (red)
   - Spawns in north portion of map

3. **AI Settlement Spawn** (~80 lines)
   - Place 1 AI CITIZEN_BLOCK at calculated spawn point (opposite player)
   - Red-tinted visuals
   - Fair resource environment (mirrored deposits)

4. **AI Building System** (~150 lines)
   - Fixed build order + timing
   - Buildings are real entities (attackable, visible when scouted)
   - AI builds defenses ONLY after player contact (not for waves)

5. **AI Economy** (~50 lines)
   - Abstract income per second
   - Scale with buildings, multiply by difficulty

6. **AI Training** (~100 lines)
   - Units toward composition target (same types as player)
   - Units spawn at AI barracks, colored red

7. **AI Attack Loop** (~120 lines)
   - Timer-based (from difficulty)
   - Target: always the player (only 1 other empire)
   - Rally → March → Fight → Retreat
   - NO wave awareness needed (AI is immune to waves)

8. **AI Defense** (~60 lines)
   - Garrison near base (30-40% of army)
   - Pull back if base under attack by player
   - Build walls/towers reactively after first player contact

9. **AI Elimination** (~50 lines)
   - Settlement HP = 0 → AI eliminated (only by player attack)
   - "🏴 The Enemy Empire has fallen!"
   - Buildings crumble, units scatter

10. **Victory Milestone** (~40 lines)
    - AI destroyed → "EMPIRE VICTORY" banner
    - Game continues — waves keep coming
    - Pure survival mode after AI is dead

11. **Minimap Fog (Civ-style)** (~30 lines)
    - AI dots only when tile is VISIBLE (red dots)
    - Wave enemy dots in dark red
    - Simple: 1 color for AI (red)

**Phase 2 total: ~800 new lines** (200 fewer than old plan — no wave distribution!)
**Estimated effort: 3-4 focused sessions** (faster than old plan — 1 AI is simpler)

### Phase 3: Polish & Personality
- Re-fogging system (VISIBLE→EXPLORED when units leave)
- AI scouting (sends scouts toward player territory)
- AI personalities (Turtle, Rusher, Strategist, Raider — 4 behaviors)
- Scout unit type (cheap, fast, no attack, 10-tile vision)
- Flanking damage bonus (1.5× side, 2× rear)
- Terrain combat bonuses (hills +range, forests +stealth)
- AI attacks during BUILD phase (the "never safe" feeling)
- AI wave-timing exploitation (attacks during waves on Hard+)

**Estimated effort: 3-4 sessions**

### Phase 4: Advanced (Stretch)
- AI expansion (second settlement when economy is strong)
- AI adapts composition to counter what defeated it
- Dynamic difficulty adjustment (AI eases up if player is losing badly)
- Enemy camp system (persistent strategic objectives in contested zone)
- Camp raiding rewards (from Enemy Rework Plan)
- Minimap threat pulse (red flash when AI army spotted)
- Multiple AI support (2+ AIs for future "Insane" difficulty?)

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
  ✓ 1 AI opponent that builds, trains, attacks independently
  ✓ ALL waves target player only (AI is immune)
  ✓ AI grows unchecked unless player raids
  ✓ Civ-style minimap fog (only see AI when scouted)
  ✓ Empire elimination (by you ONLY — earned victory)
  ✓ Optional victory: destroy AI, then pure survival
  → This IS a complete game. Wave survival + empire warfare. Ship it.

NICE TO HAVE (Phase 3):
  ○ AI personalities (Turtle/Rusher/Strategist/Raider)
  ○ Re-fogging + continuous scouting need
  ○ Flanking bonus + terrain bonuses
  ○ Scout unit type
  ○ AI wave-timing exploitation (attacks during waves)
  → Makes it a GOOD game.

STRETCH (Phase 4):
  ○ AI expansion (second settlements)
  ○ Adaptive AI composition
  ○ Dynamic difficulty
  ○ Enemy camp system
  ○ Multiple AI support (future mode)
  → Makes it a GREAT game.
```

### Honest Assessment
- **Phase 0 (Hero Removal):** 3-4 sessions — well-planned, will work
- **Phase 1 (Wave Enhancement):** 2-3 sessions — builds on existing system
- **Phase 2 (1 AI Empire):** 3-4 sessions — SIMPLER than old plan (1 AI, no wave distribution)
- **Phase 3 (Polish):** 3-4 sessions — incremental improvements
- **Phase 4 (Advanced):** 3-4 sessions — modular additions

**Total for complete hybrid game: ~14-19 focused sessions**
**Total for playable MVP (Phase 0+1+2): ~8-11 sessions** (faster than old plan!)

### Why "All vs The User" Is EASIER to Build
The new design is simpler than the old "waves attack everyone" approach:

1. **No wave distribution system** — 100% of waves → player (already works!)
2. **No AI wave defense** — AI doesn't need walls-for-waves logic
3. **No abstract off-screen combat** — waves never fight AI (nothing to simulate)
4. **1 AI only** — no array management, no AI-vs-AI combat
5. **Simpler AI decision tree** — AI only has 1 target (the player)
6. **~200 fewer lines** in Phase 2 (800 vs 1000)
7. **Better performance** — fewer entities, simpler interactions

### The Key Insight
The "All vs The User" asymmetry is the GAME:
- Waves are your **constant burden** — they drain your resources every 60 seconds
- The AI is your **growing threat** — it builds freely while you fight waves
- The question is always: **"When do I stop defending and go on offense?"**
- Too early → you lose to waves because your army is away
- Too late → the AI army is unstoppable because it's been growing unchecked
- Finding that moment — that's the game. That's the skill. That's the fun.

---

## RECOMMENDATION

**Hybrid: Waves (CoD Zombies survival) + 1 AI Empire (independent strategic threat)**
**All vs The User — waves and AI both target only the player.**

Build order:
1. **Phase 0:** Execute Hero Removal Plan — already written, 9 phases
2. **Phase 1:** Enhance waves — endless mode, new enemies, bosses, wave counter as score
3. **Phase 2:** Add 1 AI empire — difficulty screen, build/train/attack, immune to waves
4. **Phase 3:** Polish — personalities, re-fogging, flanking, terrain bonuses
5. **Phase 4:** Advanced — expansion, camps, adaptive AI, multiple AI stretch goal

This gives you:
- 🧟 **CoD Zombies survival feel** — "I hit wave 100, I'm amazing"
- 🏰 **Strategic depth** — scout, raid, and destroy the AI empire
- ⚖️ **Brutal asymmetry** — you fight two fronts, the AI fights zero
- 🎲 **Replayability** — personality × difficulty × random map × wave RNG
- 😱 **Double tension** — fighting waves AND watching for AI raids
- 🏆 **Clear bragging metric** — wave counter IS the score
- 🎭 **Two-phase gameplay** — empire war early, pure survival late
- 💀 **Growing pressure** — the AI snowballs while you burn resources on waves
- 🎯 **The Moment** — finding the perfect window to attack the AI between waves

**Start with Hero Removal. Then wave enhancement. Then ~800 lines gets you a full hybrid war game.**

---

## ✅ CONFIRMED DESIGN DECISIONS

All questions resolved (2026-04-15):

| # | Question | Answer |
|---|----------|--------|
| 1 | Keep waves? | **YES** — CoD Zombies "how many waves can you survive" is the core. Wave counter = score |
| 2 | Add AI empire? | **YES** — 1 AI opponent that builds, trains, and wages war |
| 3 | Hybrid approach? | **YES** — Waves provide heartbeat, AI provides strategic depth. Both target only the player |
| 4 | Waves are endless? | **YES** — No final wave. Wave 100, 200, 500... "I'm amazing" |
| 5 | How many AIs? | **ALWAYS 1** — difficulty comes from AI behavior + wave intensity, not AI count |
| 6 | Waves attack AI? | **NO** — waves ONLY target the player. AI is immune. "All vs the user" |
| 7 | AI visible on minimap? | **Only when scouted** — Civ-style, dots disappear when not in vision |
| 8 | Shared unit types? | **YES for AI** — AI uses Militia/Archer/Spearman/Cavalry/Catapult. Waves use feral types |
| 9 | Map size? | **Keep 950×632** — large enough for 2 empires with north/south separation |
| 10 | AI fights other AIs? | **N/A** — only 1 AI, it only fights the player |
| 11 | Attack warnings? | **NO for AI** — hidden tension. YES for waves — wave preview scout report |
| 12 | Game ends when AI dead? | **NO** — Victory banner, but waves keep coming. Pure survival after empire war |
| 13 | AI attacks during BUILD phase? | **YES (Phase 3)** — "you're never truly safe" |
| 14 | Wave enemy types? | **Feral horde** — distinct faction from AI military (12 types + 3 bosses) |
| 15 | Difficulty selection? | **YES** — Easy/Normal/Hard/Brutal controls AI personality + AI stats + wave intensity |
