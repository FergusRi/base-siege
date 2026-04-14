#!/usr/bin/env python3
"""Phase H: Gate Passthrough + Citizen Recall (~100 lines)
1. Modify isWalkable() to accept entity type parameter (friendly=gates passable)
2. Fix heroCanWalkTo() — hero can pass through gates/gatehouses
3. Add findPathFriendly() wrapper for unit pathfinding through gates
4. Enhance citizen recall warning banner with countdown timer
5. Verify warning banner + timer display
"""

import re, sys

FILE = '/home/user/base-siege/index.html'

with open(FILE, 'r') as f:
    code = f.read()
lines = code.split('\n')

changes = []

# ─────────────────────────────────────────────────────
# 1. Modify isWalkable() — add optional `friendly` parameter
#    When friendly=true, gates/gatehouses are walkable (they already are with blocksPath:false)
#    When friendly=false (default), gates/gatehouses BLOCK (for enemy pathfinding distinction)
#    NOTE: Currently gates have blocksPath:false, so enemies CAN pathfind through them (and take damage).
#    The plan says "friendly units + hero can pass through gates" — meaning we need
#    to ensure the entity type param exists for future differentiation.
#    Since gates already don't block in isWalkable, the main fix is heroCanWalkTo.
# ─────────────────────────────────────────────────────

# Find isWalkable function
old_isWalkable = """function isWalkable(c,r){
  if(c<0||c>=COLS||r<0||r>=ROWS) return false;
  if(map[c][r]===T.WATER) return false;
  const sk=c+','+r;
  const s=structures[sk];
  // Buildings with blocksPath=true block movement; Gates/Gatehouses are walkable
  if(s){
    const def=STRUCTS[s.type];
    if(def&&def.blocksPath) return false;
    // Legacy: towers still block
    if(s.type==='TOWER'||s.type==='BALLISTA_TOWER'||s.type==='WATCHTOWER') return false;
  }
  return true;
}"""

new_isWalkable = """function isWalkable(c,r,friendly){
  if(c<0||c>=COLS||r<0||r>=ROWS) return false;
  if(map[c][r]===T.WATER) return false;
  const sk=c+','+r;
  const s=structures[sk];
  if(s){
    const def=STRUCTS[s.type];
    // Gates/Gatehouses: friendly entities pass freely, enemies also pass (take damage in combat code)
    if(s.type==='GATE'||s.type==='GATEHOUSE') return true;
    if(def&&def.blocksPath) return false;
    // Towers always block movement
    if(s.type==='TOWER'||s.type==='BALLISTA_TOWER'||s.type==='WATCHTOWER') return false;
  }
  return true;
}"""

if old_isWalkable in code:
    code = code.replace(old_isWalkable, new_isWalkable)
    changes.append("✅ 1. isWalkable() — added friendly parameter + explicit gate passthrough")
else:
    print("❌ Could not find isWalkable function")
    sys.exit(1)

# ─────────────────────────────────────────────────────
# 2. Fix heroCanWalkTo() — allow hero through gates/gatehouses
# ─────────────────────────────────────────────────────

old_heroCanWalkTo = """function heroCanWalkTo(wx,wy){
  const c=Math.floor(wx/TILE_SIZE),r=Math.floor(wy/TILE_SIZE);
  if(c<0||c>=COLS||r<0||r>=ROWS)return false;
  if(map[c][r]===T.WATER)return false;
  const sk=c+','+r;
  const s=structures[sk];
  if(s&&(s.type==='WALL'||s.type==='TOWER'||s.type==='GATE'))return false;
  return true;
}"""

new_heroCanWalkTo = """function heroCanWalkTo(wx,wy){
  const c=Math.floor(wx/TILE_SIZE),r=Math.floor(wy/TILE_SIZE);
  if(c<0||c>=COLS||r<0||r>=ROWS)return false;
  if(map[c][r]===T.WATER)return false;
  const sk=c+','+r;
  const s=structures[sk];
  if(s){
    // Hero can pass through gates and gatehouses
    if(s.type==='GATE'||s.type==='GATEHOUSE') return true;
    // Block on walls, towers, and other path-blocking structures
    if(s.type==='WALL'||s.type==='TOWER'||s.type==='BALLISTA_TOWER'||s.type==='WATCHTOWER') return false;
    const def=STRUCTS[s.type];
    if(def&&def.blocksPath) return false;
  }
  return true;
}"""

if old_heroCanWalkTo in code:
    code = code.replace(old_heroCanWalkTo, new_heroCanWalkTo)
    changes.append("✅ 2. heroCanWalkTo() — hero can now pass through gates and gatehouses")
else:
    print("❌ Could not find heroCanWalkTo function")
    sys.exit(1)

# ─────────────────────────────────────────────────────
# 3. Update unitPathTo to pass friendly=true to findPath
#    We need findPath to accept a friendly param and pass it to isWalkable
# ─────────────────────────────────────────────────────

# First update findPath signature and isWalkable calls within it
old_findPath_sig = "function findPath(sc,sr,tc,tr){"
new_findPath_sig = "function findPath(sc,sr,tc,tr,friendly){"

if old_findPath_sig in code:
    code = code.replace(old_findPath_sig, new_findPath_sig, 1)
    changes.append("✅ 3a. findPath() — added friendly parameter")
else:
    print("❌ Could not find findPath signature")
    sys.exit(1)

# Update isWalkable calls inside findPath to pass friendly
# These are at lines: 2595, 2601, 2641
# We need to be careful to only replace within findPath context

# Replace isWalkable calls within findPath body
# Pattern: replace 'isWalkable(goalC,goalR)' -> 'isWalkable(goalC,goalR,friendly)'
code = code.replace('if(!isWalkable(goalC,goalR)){', 'if(!isWalkable(goalC,goalR,friendly)){', 1)
code = code.replace('if(isWalkable(nc,nr)){', 'if(isWalkable(nc,nr,friendly)){', 1)  # in the goal adjustment loop

# The main A* loop: 'if(!isWalkable(nc,nr))continue;' inside findPath
# We need to be careful — there are multiple isWalkable calls. Let's use a targeted approach.
# The one inside findPath's A* loop is right after 'for(const[dc,dr] of dirs){'
# We'll use a unique context: 'if(closed.has(nk))continue;\n      const ng=g+1;'
# The pattern right before is: if(!isWalkable(nc,nr))continue;

old_astar_walkable = """      if(!isWalkable(nc,nr))continue;
      const nk=nc+','+nr;
      if(closed.has(nk))continue;
      const ng=g+1;"""

new_astar_walkable = """      if(!isWalkable(nc,nr,friendly))continue;
      const nk=nc+','+nr;
      if(closed.has(nk))continue;
      const ng=g+1;"""

if old_astar_walkable in code:
    code = code.replace(old_astar_walkable, new_astar_walkable, 1)
    changes.append("✅ 3b. findPath A* loop — passes friendly to isWalkable")
else:
    print("❌ Could not find A* isWalkable pattern in findPath")
    sys.exit(1)

# Now update unitPathTo to pass friendly=true
old_unitPathTo_call = "  const path = findPath(sc, sr, gc, gr);"
new_unitPathTo_call = "  const path = findPath(sc, sr, gc, gr, true); // friendly=true: units pass through gates"

if old_unitPathTo_call in code:
    code = code.replace(old_unitPathTo_call, new_unitPathTo_call, 1)
    changes.append("✅ 3c. unitPathTo() — passes friendly=true to findPath")
else:
    print("❌ Could not find unitPathTo findPath call")
    sys.exit(1)

# ─────────────────────────────────────────────────────
# 4. Enhance citizen recall warning — add countdown timer to banner
#    The existing system already:
#    - Triggers at 30 seconds (CITIZEN_RECALL_TIME)
#    - Shows banner "WAVE INCOMING — Citizens returning!"
#    - Shows pulsing citizen recall status on canvas
#    - Citizens pathfind home, mark safe
#    Enhancement: show countdown seconds in the canvas warning text
# ─────────────────────────────────────────────────────

old_recall_display = """    if(citizenRecallTriggered){
      const recallPulse=Math.sin(now*0.008)*0.3+0.7;
      const safeCt=citizens.filter(c=>c.safe).length;
      const totalCt=citizens.length;
      ctx.font='bold 16px system-ui';
      ctx.fillStyle=`rgba(255,180,60,${recallPulse})`;
      ctx.shadowColor='rgba(255,150,30,0.5)';ctx.shadowBlur=12;
      ctx.fillText(`⚠️ CITIZENS RECALLING — ${safeCt}/${totalCt} safe`, canvas.width/2, canvas.height-95);
    }"""

new_recall_display = """    if(citizenRecallTriggered){
      const recallPulse=Math.sin(now*0.008)*0.3+0.7;
      const safeCt=citizens.filter(c=>c.safe).length;
      const totalCt=citizens.length;
      const countdown=Math.max(0,Math.ceil(game.buildTimer));
      ctx.font='bold 16px system-ui';
      ctx.fillStyle=`rgba(255,180,60,${recallPulse})`;
      ctx.shadowColor='rgba(255,150,30,0.5)';ctx.shadowBlur=12;
      ctx.fillText(`⚠️ WAVE IN ${countdown}s — Citizens recalling (${safeCt}/${totalCt} safe)`, canvas.width/2, canvas.height-95);
    }"""

if old_recall_display in code:
    code = code.replace(old_recall_display, new_recall_display)
    changes.append("✅ 4. Citizen recall display — added countdown timer to warning")
else:
    print("❌ Could not find recall display code")
    sys.exit(1)

# ─────────────────────────────────────────────────────
# 5. Enhance showBanner call in triggerCitizenRecall to include countdown
# ─────────────────────────────────────────────────────

old_recall_banner = "  showBanner('⚠️ WAVE INCOMING — Citizens returning!');"
new_recall_banner = "  showBanner('⚠️ WAVE IN ' + CITIZEN_RECALL_TIME + 's — Citizens returning!');"

if old_recall_banner in code:
    code = code.replace(old_recall_banner, new_recall_banner)
    changes.append("✅ 5. Recall banner — shows countdown seconds")
else:
    print("❌ Could not find recall banner text")
    sys.exit(1)

# ─────────────────────────────────────────────────────
# Write the patched file
# ─────────────────────────────────────────────────────

with open(FILE, 'w') as f:
    f.write(code)

print(f"\n{'='*60}")
print(f"Phase H patch applied — {len(changes)} changes:")
for c in changes:
    print(f"  {c}")
print(f"{'='*60}")
