# Base Siege — UI/Interaction Tab Rework Plan

## Problem Statement

The current system has three overlapping concerns fighting for the same inputs:
- **Hero movement** (WASD) is always active, even when placing buildings
- **Left-click** does 6+ different things depending on mode (gather, build, select unit, click settlement, click barracks, repair)
- **Right-click** handles both unit movement AND guard assignment (context: "near hero")
- **Guard assignment** is fiddly — you must right-click close to the hero with units selected
- **Unit selection** (left-click / box-select) can accidentally trigger building interactions
- During BUILD phase, moving the hero while trying to place structures is disorienting

## Solution: 3-Tab Mode System

Replace the current gather/build toggle with **three explicit tabs** during the BUILD phase. Each tab owns its inputs completely — no click conflicts.

```
┌─────────────────────────────────────────────────┐
│  [🏠 Hero (H)]  [🔨 Build (B)]  [⚔ Units (U)] │
│                                                  │
│  Tab-specific toolbar content appears here       │
└─────────────────────────────────────────────────┘
```

During **COMBAT phase**, a special combat overlay activates that gives access to everything.

---

## Tab 1: 🏠 Hero Tab (H key) — Default

**Purpose**: Hero-centric gameplay. Moving around, gathering, interacting with buildings.

### Inputs
| Input | Action |
|-------|--------|
| **WASD** | Move hero |
| **Left-click tile** | Gather resource (wood/stone/metal) |
| **Left-click settlement** | Open settlement panel (upgrade, priority, guard upgrade) |
| **Left-click military bldg** | Open training panel (queue units) |
| **Left-click damaged bldg** | Repair building |
| **Mouse wheel** | Zoom camera |
| **Minimap click** | Jump camera |

### What's DISABLED
- No unit selection / box select
- No unit movement / formation drag
- No building placement
- No demolishing

### Camera
- Camera follows hero (current behaviour)

### Toolbar Shows
- Resource bar (top)
- Context hint: "WASD move · Click to gather · Click buildings to interact · B=build · U=units"
- Settlement/Training panels open on click (same as current)

---

## Tab 2: 🔨 Build Tab (B key)

**Purpose**: Structure placement and base layout. Pure construction mode.

### Inputs
| Input | Action |
|-------|--------|
| **WASD** | **Pan camera** (hero is frozen) |
| **Left-click** | Place selected structure / Demolish |
| **Right-click** | Cancel current placement (return to no selection) |
| **1/2/3/4** | Switch category (Defense/Economy/Military/Infrastructure) |
| **X** | Switch to demolish mode |
| **Q/W/E/R/T** | Select building within category |
| **Escape** | Return to Hero tab |
| **Mouse wheel** | Zoom camera |
| **Minimap click** | Jump camera |

### What's DISABLED
- Hero does NOT move (WASD pans camera instead)
- No unit selection / movement
- No gathering
- No guard assignment
- No hero attack

### Camera
- **WASD pans camera** at a fixed speed (e.g. 8 tiles/sec)
- Edge-of-screen scrolling (mouse within 40px of canvas edge)
- Minimap click to jump

### Toolbar Shows
- Category tabs: [Defense] [Economy] [Military] [Infrastructure] [Demolish]
- Building buttons within selected category (same as current)
- Ghost preview of building on cursor
- Context hint: "WASD pan camera · Click to place · 1-4 category · X demolish · Esc back"

### Building Interactions
- **Left-click settlement**: Opens settlement panel (for upgrades — you're in build mode after all)
- **Left-click military bldg**: Opens training panel (convenient to queue troops while building)

---

## Tab 3: ⚔ Units Tab (U key)

**Purpose**: All unit management — selection, movement, formations, guards.

### Inputs
| Input | Action |
|-------|--------|
| **WASD** | **Pan camera** (hero is frozen) |
| **Left-click unit** | Select unit |
| **Left-click empty** | Deselect all |
| **Shift+click unit** | Toggle add/remove from selection |
| **Left-click drag** | Box select units |
| **Right-click ground** | Move selected units (formation if dragged) |
| **Right-click enemy** | Attack-move to enemy (during combat) |
| **Tab** | Cycle through units (Shift+Tab = reverse) |
| **Ctrl+1/2/3** | Save control group |
| **1/2/3** | Recall control group |
| **G** | Toggle guard mode (see below) |
| **Mouse wheel** | Zoom camera |
| **Minimap click** | Jump camera |
| **Escape** | Deselect all / Return to Hero tab |

### Guard Assignment — SIMPLIFIED
**Current problem**: You must right-click near the hero while having units selected. Easy to accidentally move units instead.

**New approach — dedicated Guard button + G hotkey:**
1. Select units you want to guard
2. Press **G** or click the **[🛡 Assign Guard]** button in the toolbar
3. Selected units become guards immediately (no need to click the hero)
4. Press **G** again with guards selected → **Dismiss** them from guard duty
5. **G is a toggle**: Select → G = assign. Select guards → G = dismiss.

This eliminates the "right-click near hero" guesswork entirely.

### What's DISABLED
- Hero does NOT move
- No gathering
- No building placement
- No building interactions (click passes through to unit selection)

### Camera
- **WASD pans camera** (same as Build tab)
- Edge-of-screen scrolling
- Minimap click

### Toolbar Shows
- Unit info bar: Selected unit count, types, health summary
- **[🛡 Assign Guard]** button (enabled when units selected + guard capacity available)
- **[🛡 Dismiss Guard]** button (enabled when guard units selected)
- Guard capacity indicator: "Guards: 2/4"
- Context hint: "Click to select · Drag to box-select · Right-click to move · G=guard toggle · Tab=cycle"

### Clicking Military Buildings
- **Left-click military bldg** in Units tab: Opens training panel (since unit training is naturally unit management)

---

## Combat Phase Override

When a wave starts, the game enters **COMBAT mode**. This is NOT a tab — it's an overlay that merges capabilities:

### Inputs (all active simultaneously)
| Input | Action |
|-------|--------|
| **WASD** | Move hero (hero movement takes priority in combat) |
| **Left-click enemy** | Hero attack |
| **Left-click unit** | Select unit |
| **Left-click drag** | Box select |
| **Right-click ground** | Move selected units / formation drag |
| **Right-click enemy** | Attack-move selected units to enemy |
| **G** | Guard toggle (same as Units tab) |
| **Tab** | Cycle units |
| **Ctrl+1/2/3** | Save group |
| **1/2/3** | Recall group |

### Camera
- Camera follows hero (returns to hero-follow mode)
- Minimap click still works

### Toolbar Shows
- "⚔ COMBAT" indicator
- Selected unit info bar
- Guard capacity
- Kill counter
- Context hint: "WASD move · Click attack · Right-click move units · G=guard · Tab=cycle"

### After Wave Ends
- Returns to **Hero tab** (default)

---

## Implementation Phases

### Phase 1: Tab Infrastructure (Lines ~2883-2961 rework)
- Replace `uiMode` values: `'hero'` | `'build'` | `'units'` | `'combat'`
- Replace `toggleBuildMode()` with `switchTab(tab)` function
- Update toolbar HTML with 3-tab layout
- Add tab highlight styling
- Hotkeys: H = hero, B = build, U = units
- Update `updateHint()` for all tabs

### Phase 2: Input Gating (Lines ~4921-5573 rework)
- **Hero movement** (`updateHero()`): Only process WASD when `uiMode==='hero' || uiMode==='combat'`
- **Camera panning**: New `updateCameraPan(dt)` function — process WASD when `uiMode==='build' || uiMode==='units'`
- **Click dispatch** (canvas click handler): Branch on `uiMode` first
  - `hero`: Gather / building interaction only
  - `build`: Place / demolish only
  - `units`: Unit select only (+ military building click for training)
  - `combat`: Hero attack + unit select
- **Right-click** (formation drag handler): Only active in `units` and `combat` modes
- **Box select**: Only active in `units` and `combat` modes

### Phase 3: Guard Rework (Lines ~5447-5503 rework)
- Remove "right-click near hero" guard assignment logic
- Add `toggleGuardAssignment()` function:
  - If selected units are NOT guards → assign as guards
  - If selected units ARE guards → dismiss
  - Mixed selection → assign non-guards, leave existing guards
- Wire to G key (replace current G key handler)
- Add [🛡 Assign Guard] / [🛡 Dismiss Guard] buttons to Units tab toolbar
- Update guard capacity display in Units tab

### Phase 4: Camera Panning (New code)
- New function `updateCameraPan(dt)`:
  - Uses WASD keys when in build/units mode
  - Pan speed: `CAM_PAN_SPEED = 8 * TILE_SIZE` (8 tiles/sec)
  - Clamps to map bounds
- Edge scrolling:
  - Detect mouse within 40px of canvas edge  
  - Pan camera in that direction
  - Same speed as WASD pan
- Camera mode tracking:
  - `hero` / `combat` tab: Camera follows hero (current behaviour)
  - `build` / `units` tab: Free camera (manual panning)

### Phase 5: Toolbar UI Overhaul (HTML/CSS rework)
- New tab bar HTML with 3 buttons
- Hero tab content: Minimal — just hints
- Build tab content: Category sub-tabs + building buttons (moved from current)
- Units tab content: Unit info bar + guard buttons + hints
- Combat overlay: Merges unit info + combat hints
- Ensure panels (settlement/training) work from any tab that allows them

### Phase 6: Polish & Edge Cases
- Ensure SPACE (start wave) works from any tab
- Tab memory: Remember last build category/tool when switching back to Build tab
- ESC behaviour: Units tab → deselect, then Hero tab. Build tab → cancel tool, then Hero tab
- Unit movement during BUILD phase: Confirm `updateUnits(dt)` still called regardless of tab
- Touch controls: Map touch to equivalent tab actions
- Update all `updateHint()` strings

---

## Key Design Decisions

### 1. Why freeze hero in Build/Units mode?
Moving the hero while placing buildings is disorienting. In Build mode you want camera control, not hero control. In Units mode, WASD for camera lets you survey the map to position troops. Hero movement during these would cause accidental camera shifts.

### 2. Why not keep right-click guard assignment?
Right-click near the hero is unreliable — the "near hero" detection radius is small, and a miss moves your units to a random spot. A dedicated G hotkey is faster, more reliable, and less error-prone.

### 3. Why allow training panel in both Build and Units tab?
Training units is related to both base building and unit management. Locking it to one tab would annoy players. It's a panel overlay that doesn't conflict with either tab's core actions.

### 4. Why merge everything in Combat?
Combat is time-critical. Forcing tab switches mid-fight would be frustrating. Players need hero movement, unit commands, and quick reactions simultaneously. The combat overlay gives full access.

### 5. Camera in Combat?
Returns to hero-follow because the hero is your primary actor in combat. You can still use minimap to jump around. Post-combat reverts to whatever tab you were on (defaults to Hero).

---

## Line-by-Line Impact Estimate

| Section | Lines | Impact |
|---------|-------|--------|
| HTML toolbar structure | 436-494 | **Rewrite** — new 3-tab layout |
| CSS for tabs/toolbar | 50-120 | **Add** — tab styling, active states |
| `uiMode` / mode system | 2883-2961 | **Rewrite** — new switchTab(), remove toggleBuildMode() |
| Keyboard handler | 4921-4998 | **Modify** — add H/U keys, gate WASD by mode |
| Click dispatch | 5279-5332 | **Rewrite** — branch by 4 modes |
| Unit selection mouse handlers | 5508-5573 | **Modify** — gate by units/combat mode |
| Formation drag handlers | 5356-5445 | **Modify** — gate by units/combat mode, remove hero-proximity guard |
| Guard system | 5447-5503 | **Modify** — new toggle function, remove right-click assignment |
| Guard dismiss hotkey | 5006-5014 | **Replace** — merge into G toggle |
| Hero movement | 5046-5062 | **Modify** — gate by hero/combat mode |
| Camera system | (new) | **Add** — ~40 lines for pan + edge scroll |
| Hint system | 2947-2961 | **Rewrite** — hints per tab |
| Main game loop | 7355+ | **Modify** — call updateCameraPan(dt) |

**Estimated total changes**: ~300-400 lines modified/added, ~50 lines removed.

---

## Migration Notes

- No save/load impact (modes are transient UI state)
- No balance impact (no gameplay mechanics change)
- No enemy AI impact
- No economy impact
- All unit combat behaviour unchanged
- All building stats unchanged
- Minimap unchanged (except click-to-jump camera works in all modes)
