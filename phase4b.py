#!/usr/bin/env python3
"""
Phase 4B: Fog Overlay Optimization
Replace per-tile fillRect with batched rendering:
- Collect all unexplored rects, fill once
- Collect all explored rects, fill once
- Eliminates per-tile fillStyle changes (from ~2 per tile to 2 total)
"""

import sys

with open('index.html', 'r') as f:
    lines = f.readlines()

print(f"Starting: {len(lines)} lines")

# The current drawFogOverlay (lines 4209-4232):
# function drawFogOverlay(){
#   if(game.phase==='MENU') return;
#   const z=cam.zoom;
#   const sc=...,sr=...;
#   const ec=...,er=...;
#   const ts=TILE_SIZE*z;
#   for(let c=sc;c<=ec;c++){
#     for(let r=sr;r<=er;r++){
#       const fog=fogMap[c]?fogMap[c][r]:FOG_UNEXPLORED;
#       if(fog===FOG_VISIBLE) continue;
#       const sx=(c*TILE_SIZE-cam.x)*z,sy=(r*TILE_SIZE-cam.y)*z;
#       if(fog===FOG_UNEXPLORED){ ctx.fillStyle='rgba(5,5,12,0.97)'; ctx.fillRect(sx,sy,ts+1,ts+1); }
#       else { ctx.fillStyle='rgba(5,5,12,0.6)'; ctx.fillRect(sx,sy,ts+1,ts+1); }
#     }
#   }
# }

# Replace with batched version
NEW_FOG = '''function drawFogOverlay(){
  if(game.phase==='MENU') return;
  const z=cam.zoom;
  const sc=Math.max(0,Math.floor(cam.x/TILE_SIZE)),sr=Math.max(0,Math.floor(cam.y/TILE_SIZE));
  const ec=Math.min(COLS-1,Math.ceil((cam.x+canvas.width/z)/TILE_SIZE));
  const er=Math.min(ROWS-1,Math.ceil((cam.y+canvas.height/z)/TILE_SIZE));
  const ts=TILE_SIZE*z, ts1=ts+1;
  // Batch unexplored and explored into separate paths
  ctx.beginPath();
  for(let c=sc;c<=ec;c++){
    for(let r=sr;r<=er;r++){
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
  for(let c=sc;c<=ec;c++){
    for(let r=sr;r<=er;r++){
      const fog=fogMap[c]?fogMap[c][r]:FOG_UNEXPLORED;
      if(fog===FOG_EXPLORED){
        const sx=(c*TILE_SIZE-cam.x)*z,sy=(r*TILE_SIZE-cam.y)*z;
        ctx.rect(sx,sy,ts1,ts1);
      }
    }
  }
  ctx.fillStyle='rgba(5,5,12,0.6)';
  ctx.fill();
}'''

# Find exact start/end of drawFogOverlay
start_line = None
end_line = None
for i, line in enumerate(lines):
    if 'function drawFogOverlay(){' in line:
        start_line = i
    if start_line is not None and i > start_line:
        stripped = line.rstrip()
        if stripped == '}' and end_line is None:
            end_line = i
            break

if start_line is None or end_line is None:
    print("ERROR: Could not find drawFogOverlay function boundaries")
    sys.exit(1)

print(f"Found drawFogOverlay: lines {start_line+1}-{end_line+1}")
old_len = end_line - start_line + 1
print(f"Old function: {old_len} lines")

# Replace
new_lines = [l + '\n' for l in NEW_FOG.split('\n')]
lines[start_line:end_line+1] = new_lines
new_len = len(new_lines)
print(f"New function: {new_len} lines")

with open('index.html', 'w') as f:
    f.writelines(lines)

print(f"\nFinal: {len(lines)} lines (delta: {len(lines) - 5679})")
