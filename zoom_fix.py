#!/usr/bin/env python3
"""
Zoom & FPS fix for Base Siege:
1. Cap min zoom at 0.3 (was 0.063 — showing entire 950x632 map)
2. LOD fog overlay — at low zoom, render fog in NxN blocks instead of per-tile
3. Skip water overlay when zoom < 0.4 (biggest per-tile loop)
4. Add full-map overlay toggle (M key) using minimap canvas scaled up
5. Add FPS counter for debugging
"""

import re

FILE = '/home/user/base-siege/index.html'

with open(FILE, 'r') as f:
    lines = f.readlines()

original_count = len(lines)
print(f"Read {original_count} lines")

# ──────────────────────────────────────────────────────
# 1. Cap min zoom at 0.3
# ──────────────────────────────────────────────────────
# Find: function getMinZoom(){...}
# Replace with capped version
old_minzoom = "function getMinZoom(){const c=document.getElementById('game-canvas');if(!c)return 0.1;return Math.max(c.width/MAP_PX_W,c.height/MAP_PX_H);}"
new_minzoom = "function getMinZoom(){return 0.3;}"

found = False
for i, line in enumerate(lines):
    if old_minzoom in line:
        lines[i] = line.replace(old_minzoom, new_minzoom)
        found = True
        print(f"  [1] Capped minZoom at 0.3 on line {i+1}")
        break
assert found, "Could not find getMinZoom function"

# ──────────────────────────────────────────────────────
# 2. LOD fog overlay — use larger blocks at low zoom
# ──────────────────────────────────────────────────────
# Replace the entire drawFogOverlay function
old_fog_start = "function drawFogOverlay(){"
fog_start_line = None
fog_end_line = None

for i, line in enumerate(lines):
    if old_fog_start in line:
        fog_start_line = i
        break

assert fog_start_line is not None, "Could not find drawFogOverlay"

# Find closing brace (track brace depth)
depth = 0
for i in range(fog_start_line, len(lines)):
    depth += lines[i].count('{') - lines[i].count('}')
    if depth == 0:
        fog_end_line = i
        break

assert fog_end_line is not None, "Could not find end of drawFogOverlay"
print(f"  [2] drawFogOverlay spans lines {fog_start_line+1}-{fog_end_line+1}")

new_fog = """function drawFogOverlay(){
  if(game.phase==='MENU') return;
  const z=cam.zoom;
  // LOD: at low zoom use larger step to reduce fill calls
  const step=z<0.35?4:z<0.5?2:1;
  const stepPx=TILE_SIZE*step;
  const sc=Math.max(0,Math.floor(cam.x/TILE_SIZE/step)*step);
  const sr=Math.max(0,Math.floor(cam.y/TILE_SIZE/step)*step);
  const ec=Math.min(COLS-1,Math.ceil((cam.x+canvas.width/z)/TILE_SIZE));
  const er=Math.min(ROWS-1,Math.ceil((cam.y+canvas.height/z)/TILE_SIZE));
  const ts=stepPx*z, ts1=ts+1;
  // Batch unexplored and explored into separate paths
  ctx.beginPath();
  for(let c=sc;c<=ec;c+=step){
    for(let r=sr;r<=er;r+=step){
      const fog=fogMap[c]?fogMap[c][r]:FOG_UNEXPLORED;
      if(fog===FOG_UNEXPLORED){
        const sx=(c*TILE_SIZE-cam.x)*z,sy=(r*TILE_SIZE-cam.y)*z;
        ctx.rect(sx,sy,ts1,ts1);
      }
    }
  }
  ctx.fillStyle='rgba(5,5,12,0.97)';
  ctx.fill();
  ctx.beginPath();
  for(let c=sc;c<=ec;c+=step){
    for(let r=sr;r<=er;r+=step){
      const fog=fogMap[c]?fogMap[c][r]:FOG_UNEXPLORED;
      if(fog===FOG_EXPLORED){
        const sx=(c*TILE_SIZE-cam.x)*z,sy=(r*TILE_SIZE-cam.y)*z;
        ctx.rect(sx,sy,ts1,ts1);
      }
    }
  }
  ctx.fillStyle='rgba(5,5,12,0.6)';
  ctx.fill();
}
"""

# Replace fog function
lines[fog_start_line:fog_end_line+1] = [new_fog]
print(f"  [2] Replaced drawFogOverlay with LOD version")

# ──────────────────────────────────────────────────────
# 3. Skip water overlay animation at low zoom
# ──────────────────────────────────────────────────────
old_water_start = "function drawWaterOverlay(now){"
for i, line in enumerate(lines):
    if old_water_start in line:
        water_start = i
        break

# Find end of water function
depth = 0
for i in range(water_start, len(lines)):
    depth += lines[i].count('{') - lines[i].count('}')
    if depth == 0:
        water_end = i
        break

print(f"  [3] drawWaterOverlay spans lines {water_start+1}-{water_end+1}")

new_water = """function drawWaterOverlay(now){
  const z=cam.zoom;
  // Skip animated water at low zoom — too many per-tile calls
  if(z<0.4) return;
  const wt=now*0.001;
  const sc=Math.max(0,Math.floor(cam.x/TILE_SIZE)),sr=Math.max(0,Math.floor(cam.y/TILE_SIZE));
  const ec=Math.min(COLS-1,Math.ceil((cam.x+canvas.width/z)/TILE_SIZE));
  const er=Math.min(ROWS-1,Math.ceil((cam.y+canvas.height/z)/TILE_SIZE));
  for(let c=sc;c<=ec;c++)for(let r=sr;r<=er;r++){
    if(map[c][r]!==T.WATER)continue;
    const sx=(c*TILE_SIZE-cam.x)*z,sy=(r*TILE_SIZE-cam.y)*z;
    ctx.fillStyle=`rgba(80,140,200,${Math.sin(wt*1.5+c*0.7+r*0.5)*0.08+0.04})`;
    ctx.fillRect(sx,sy,TILE_SIZE*z,TILE_SIZE*z);
  }
}
"""

lines[water_start:water_end+1] = [new_water]
print(f"  [3] Replaced drawWaterOverlay with zoom-gated version")

# ──────────────────────────────────────────────────────
# 4. Add full-map overlay (M key toggle)
# ──────────────────────────────────────────────────────
# Find the drawMinimap function to add after it
for i, line in enumerate(lines):
    if 'function drawMinimap()' in line:
        minimap_start = i
        break

# Find end of drawMinimap
depth = 0
for i in range(minimap_start, len(lines)):
    depth += lines[i].count('{') - lines[i].count('}')
    if depth == 0:
        minimap_end = i
        break

print(f"  [4] drawMinimap ends at line {minimap_end+1}")

# Insert full-map overlay function right after drawMinimap
fullmap_code = """
// ─── FULL MAP OVERLAY (M key) ───
let showFullMap=false;
function drawFullMapOverlay(){
  if(!showFullMap||game.phase==='MENU') return;
  const pad=40;
  const maxW=canvas.width-pad*2, maxH=canvas.height-pad*2;
  const mapAspect=COLS/ROWS;
  let dw,dh;
  if(maxW/maxH>mapAspect){dh=maxH;dw=dh*mapAspect;}
  else{dw=maxW;dh=dw/mapAspect;}
  const dx=(canvas.width-dw)/2, dy=(canvas.height-dh)/2;
  // Dim background
  ctx.fillStyle='rgba(0,0,0,0.75)';ctx.fillRect(0,0,canvas.width,canvas.height);
  // Draw minimap canvas scaled up
  ctx.imageSmoothingEnabled=false;
  ctx.drawImage(mmCanvas,dx,dy,dw,dh);
  ctx.imageSmoothingEnabled=true;
  // Border
  ctx.strokeStyle='rgba(200,180,120,0.6)';ctx.lineWidth=2;
  ctx.strokeRect(dx,dy,dw,dh);
  // Label
  ctx.fillStyle='rgba(232,197,106,0.9)';ctx.font='bold 16px system-ui';ctx.textAlign='center';
  ctx.fillText('MAP OVERVIEW — press M to close',canvas.width/2,dy-12);
  // Viewport rect
  const z=cam.zoom;
  const vx=dx+(cam.x/MAP_PX_W)*dw, vy=dy+(cam.y/MAP_PX_H)*dh;
  const vw=(canvas.width/z/MAP_PX_W)*dw, vh=(canvas.height/z/MAP_PX_H)*dh;
  ctx.strokeStyle='rgba(255,255,255,0.7)';ctx.lineWidth=2;
  ctx.strokeRect(vx,vy,vw,vh);
}

"""

lines.insert(minimap_end+1, fullmap_code)
print(f"  [4] Inserted drawFullMapOverlay after line {minimap_end+1}")

# ──────────────────────────────────────────────────────
# 5. Add M key handler for full-map toggle
# ──────────────────────────────────────────────────────
# Find the Tab key handler "if(e.key==='Tab'){" and insert M key handler before the BUILD phase block
# We'll insert right after the Tab return statement
for i, line in enumerate(lines):
    if "if(e.key==='Tab')" in line:
        tab_line = i
        print(f"  [5] Found Tab key handler at line {tab_line+1}")
        break

# Find the "return;" that closes the Tab block
for i in range(tab_line, tab_line+10):
    if 'return;' in lines[i]:
        tab_return = i
        break

# Find the closing brace + next if after Tab block  
for i in range(tab_return, tab_return+5):
    stripped = lines[i].strip()
    if stripped == '}':
        insert_after = i
        break
    # Sometimes return and } are on same line
    if 'return;' in lines[i] and '}' in lines[i]:
        insert_after = i
        break

m_key_code = "  // M: toggle full map overlay\n  if(e.key==='m'||e.key==='M'){if(game.phase!=='MENU'){showFullMap=!showFullMap;}return;}\n"
lines.insert(insert_after+1, m_key_code)
print(f"  [5] Added M key toggle for full-map overlay after line {insert_after+1}")

# ──────────────────────────────────────────────────────
# 6. Call drawFullMapOverlay in the game loop
# ──────────────────────────────────────────────────────
# Find drawMinimap() call in the game loop and add fullmap after it
for i, line in enumerate(lines):
    if 'drawMinimap();' in line and 'function' not in line:
        # This is the call site in the game loop
        lines[i] = line.rstrip() + '\n  drawFullMapOverlay();\n'
        print(f"  [6] Added drawFullMapOverlay() call after drawMinimap() on line {i+1}")
        break

# ──────────────────────────────────────────────────────
# 7. Add FPS counter
# ──────────────────────────────────────────────────────
# Find the game loop function to add FPS display
for i, line in enumerate(lines):
    if 'updateKillHUD();' in line and 'function' not in line:
        fps_line = i
        break

fps_code = """  // FPS counter
  if(!window._fpsFrames){window._fpsFrames=0;window._fpsLast=performance.now();window._fpsCur=60;}
  window._fpsFrames++;
  if(performance.now()-window._fpsLast>=1000){window._fpsCur=window._fpsFrames;window._fpsFrames=0;window._fpsLast=performance.now();}
  ctx.fillStyle=window._fpsCur<30?'rgba(255,80,60,0.8)':'rgba(120,200,120,0.6)';ctx.font='bold 12px monospace';ctx.textAlign='left';
  ctx.fillText(window._fpsCur+' FPS',10,canvas.height-10);
"""
lines.insert(fps_line+1, fps_code)
print(f"  [7] Added FPS counter after line {fps_line+1}")

# ──────────────────────────────────────────────────────
# Write result
# ──────────────────────────────────────────────────────
with open(FILE, 'w') as f:
    f.writelines(lines)

final_count = sum(1 for line in open(FILE))
print(f"\nDone! {original_count} → {final_count} lines (+{final_count-original_count})")
