#!/usr/bin/env python3
"""Step 2 — Resource Building Definitions & Toolbar
Adds RESOURCE_BUILDINGS constant, toolbar buttons, rendering support, cracked overlay.
All operations collected then applied bottom-to-top to avoid line-shift bugs.
"""

import re

with open('index.html', 'r') as f:
    lines = f.readlines()

# Operations: (line_number_0indexed, 'insert_after'|'insert_before'|'replace', content)
ops = []

# ============================================================
# 1. Add RESOURCE_BUILDINGS constant after STRUCTS definition
#    Find the closing }; of STRUCTS (line with CITIZEN_BLOCK)
# ============================================================
structs_end = None
for i, line in enumerate(lines):
    if 'CITIZEN_BLOCK:' in line and 'name:' in line:
        structs_end = i
        break

assert structs_end is not None, "Could not find STRUCTS CITIZEN_BLOCK line"

# Find the closing }; after CITIZEN_BLOCK
for i in range(structs_end, min(structs_end + 3, len(lines))):
    if lines[i].strip() == '};':
        structs_end = i
        break

resource_buildings_code = """
// ─── RESOURCE BUILDINGS ───
// Chain: Farm(free) → Lumber(food) → Quarry(wood) → Mine(stone) → Gold Mine(metal)
const RESOURCE_BUILDINGS = {
  FARM:       { name:'Farm',        cost:{},          hp:30, produces:'food',  perWave:3, requiredTile:T.BERRY, color:[180,140,80],  letter:'F', maxRepairs:3 },
  LUMBER:     { name:'Lumber Camp', cost:{food:3},    hp:30, produces:'wood',  perWave:3, requiredTile:T.TREE,  color:[120,90,50],   letter:'L', maxRepairs:3 },
  QUARRY:     { name:'Quarry',      cost:{wood:5},    hp:30, produces:'stone', perWave:3, requiredTile:T.STONE, color:[140,140,150],  letter:'Q', maxRepairs:3 },
  MINE:       { name:'Mine',        cost:{stone:8},   hp:30, produces:'metal', perWave:3, requiredTile:T.ORE,   color:[100,130,180],  letter:'M', maxRepairs:3 },
  GOLD_MINE:  { name:'Gold Mine',   cost:{metal:10},  hp:30, produces:'gold',  perWave:3, requiredTile:T.GOLD,  color:[200,180,60],   letter:'$', maxRepairs:3 },
};
// Merge resource buildings into STRUCTS so canAfford/rendering/etc. work
for(const[k,v] of Object.entries(RESOURCE_BUILDINGS)){
  STRUCTS[k] = v;
}
"""
ops.append((structs_end, 'insert_after', resource_buildings_code))

# ============================================================
# 2. Add a "resources" category tab + toolbar buttons
#    Insert after "economy" category tab (line 365) and add
#    a new tb-item-group for resources
# ============================================================

# Find the economy category button line
econ_cat_line = None
for i, line in enumerate(lines):
    if "data-cat=\"economy\"" in line and "selectCategory" in line:
        econ_cat_line = i
        break

assert econ_cat_line is not None, "Could not find economy category tab"

# Add a resources category tab after economy
new_cat_tab = '      <button class="tb-cat" data-cat="resources" onclick="selectCategory(\'resources\')"><span class="tool-key">4</span> ⛏ Resources</button>\n'
ops.append((econ_cat_line, 'insert_after', new_cat_tab))

# Find the demolish tb-item-group and insert the resources group before it
demolish_group_line = None
for i, line in enumerate(lines):
    if 'data-cat="demolish"' in line and 'tb-item-group' in line:
        demolish_group_line = i
        break

assert demolish_group_line is not None, "Could not find demolish item group"

resources_toolbar = """      <div class="tb-item-group" data-cat="resources" style="display:none">
        <button class="tool-btn" data-tool="FARM" onclick="selectTool('FARM')"><span class="tool-key">Q</span> Farm <span class="tool-cost">Free</span></button>
        <button class="tool-btn" data-tool="LUMBER" onclick="selectTool('LUMBER')"><span class="tool-key">W</span> Lumber <span class="tool-cost">3F</span></button>
        <button class="tool-btn" data-tool="QUARRY" onclick="selectTool('QUARRY')"><span class="tool-key">E</span> Quarry <span class="tool-cost">5W</span></button>
        <button class="tool-btn" data-tool="MINE" onclick="selectTool('MINE')"><span class="tool-key">R</span> Mine <span class="tool-cost">8S</span></button>
        <button class="tool-btn" data-tool="GOLD_MINE" onclick="selectTool('GOLD_MINE')"><span class="tool-key">T</span> Gold Mine <span class="tool-cost">10M</span></button>
      </div>
"""
ops.append((demolish_group_line, 'insert_before', resources_toolbar))

# ============================================================
# 3. Update canAfford to handle resource buildings (free = empty cost)
#    The existing canAfford already works since STRUCTS[key].cost
#    is checked and {} would pass (no entries to fail). No change needed.
# ============================================================

# ============================================================
# 4. Update updateHint for resource building tools
#    Find the line with "else{const s=STRUCTS[selectedTool]" in updateHint
# ============================================================
hint_struct_line = None
for i, line in enumerate(lines):
    if "const s=STRUCTS[selectedTool]" in line and "updateHint" not in line:
        hint_struct_line = i
        break

if hint_struct_line is not None:
    # Replace the line to also handle resource buildings with a "can't place yet" message
    old_hint = lines[hint_struct_line]
    new_hint = old_hint.replace(
        "else{const s=STRUCTS[selectedTool];if(s)h.textContent=`Click to place ${s.name} · 1/2/3 switch tab · Esc back`;}",
        "else{const rb=RESOURCE_BUILDINGS[selectedTool];if(rb){h.textContent=`${rb.name} — must be placed on ${rb.produces} resource tile · 1-4 switch tab · Esc back`;}else{const s=STRUCTS[selectedTool];if(s)h.textContent=`Click to place ${s.name} · 1-4 switch tab · Esc back`;}}"
    )
    ops.append((hint_struct_line, 'replace', new_hint))

# ============================================================
# 5. Update keyboard shortcuts in the keydown handler
#    Find where keys 1/2/3 select categories and add 4 for resources
# ============================================================
for i, line in enumerate(lines):
    if "selectCategory('economy')" in line and ("key==='3'" in line or "=== '3'" in line or "'3'" in line):
        # Insert line for key 4 after this
        indent = '      '
        new_key4 = indent + "if(e.key==='4'&&uiMode==='build'){selectCategory('resources');e.preventDefault();}\n"
        ops.append((i, 'insert_after', new_key4))
        break

# ============================================================
# 6. Add rendering for resource buildings in drawStructures()
#    Find the line "if(s.type==='CITIZEN_BLOCK'){"  in drawStructures
#    and insert resource building rendering BEFORE it
# ============================================================
draw_citizen_line = None
for i, line in enumerate(lines):
    if "s.type==='CITIZEN_BLOCK'" in line and "Settlement icon" in lines[i+1] if i+1 < len(lines) else False:
        draw_citizen_line = i
        break

# Alternative search
if draw_citizen_line is None:
    for i, line in enumerate(lines):
        if "if(s.type==='CITIZEN_BLOCK'){" in line and i > 4000:
            # Check next line has "Settlement icon"
            if i+1 < len(lines) and 'Settlement icon' in lines[i+1]:
                draw_citizen_line = i
                break

assert draw_citizen_line is not None, "Could not find CITIZEN_BLOCK rendering in drawStructures"

resource_rendering = """    // ── RESOURCE BUILDINGS ──
    if(RESOURCE_BUILDINGS[s.type]){
      const rb=RESOURCE_BUILDINGS[s.type];
      const isDestroyed=s.hp<=0;
      // Unique visuals per resource building type
      if(s.type==='FARM'){
        // Green field rows
        ctx.fillStyle=isDestroyed?'rgba(80,70,40,0.5)':'rgba(140,170,60,0.6)';
        for(let row=0;row<3;row++){
          ctx.fillRect(sx+sw*0.1,sy+sw*(0.25+row*0.25),sw*0.8,sw*0.12);
        }
        // Wheat stalks (if not destroyed)
        if(!isDestroyed){
          ctx.strokeStyle='rgba(200,180,60,0.5)';ctx.lineWidth=z;
          for(let st=0;st<4;st++){
            const stx=sx+sw*(0.2+st*0.2);
            ctx.beginPath();ctx.moveTo(stx,sy+sw*0.7);ctx.lineTo(stx,sy+sw*0.2);ctx.stroke();
            ctx.fillStyle='rgba(220,190,60,0.6)';ctx.beginPath();ctx.arc(stx,sy+sw*0.18,2*z,0,Math.PI*2);ctx.fill();
          }
        }
      }
      if(s.type==='LUMBER'){
        // Log pile
        ctx.fillStyle=isDestroyed?'rgba(60,45,25,0.4)':'rgba(120,80,40,0.7)';
        for(let lg=0;lg<3;lg++){
          ctx.fillRect(sx+sw*0.15,sy+sw*(0.35+lg*0.18),sw*0.7,sw*0.1);
          ctx.strokeStyle='rgba(80,55,25,0.4)';ctx.lineWidth=z*0.5;
          ctx.beginPath();ctx.arc(sx+sw*0.15,sy+sw*(0.4+lg*0.18),sw*0.05,0,Math.PI*2);ctx.stroke();
        }
        // Saw
        if(!isDestroyed){
          ctx.strokeStyle='rgba(180,180,180,0.4)';ctx.lineWidth=z*1.5;
          ctx.beginPath();ctx.moveTo(sx+sw*0.7,sy+sw*0.2);ctx.lineTo(sx+sw*0.85,sy+sw*0.35);ctx.stroke();
        }
      }
      if(s.type==='QUARRY'){
        // Stone blocks stacked
        ctx.fillStyle=isDestroyed?'rgba(80,80,85,0.4)':'rgba(150,150,160,0.7)';
        ctx.fillRect(sx+sw*0.15,sy+sw*0.5,sw*0.3,sw*0.3);
        ctx.fillRect(sx+sw*0.5,sy+sw*0.55,sw*0.35,sw*0.25);
        ctx.fillRect(sx+sw*0.25,sy+sw*0.3,sw*0.25,sw*0.22);
        // Chisel marks
        if(!isDestroyed){
          ctx.strokeStyle='rgba(100,100,110,0.4)';ctx.lineWidth=z*0.5;
          ctx.beginPath();ctx.moveTo(sx+sw*0.2,sy+sw*0.55);ctx.lineTo(sx+sw*0.4,sy+sw*0.55);ctx.stroke();
          ctx.beginPath();ctx.moveTo(sx+sw*0.55,sy+sw*0.6);ctx.lineTo(sx+sw*0.8,sy+sw*0.6);ctx.stroke();
        }
      }
      if(s.type==='MINE'){
        // Mine shaft entrance (dark opening)
        ctx.fillStyle=isDestroyed?'rgba(40,40,50,0.5)':'rgba(30,30,45,0.8)';
        ctx.beginPath();ctx.moveTo(sx+sw*0.2,sy+sw*0.8);ctx.lineTo(sx+sw*0.5,sy+sw*0.3);ctx.lineTo(sx+sw*0.8,sy+sw*0.8);ctx.fill();
        // Support beams
        if(!isDestroyed){
          ctx.strokeStyle='rgba(120,90,50,0.6)';ctx.lineWidth=z*2;
          ctx.beginPath();ctx.moveTo(sx+sw*0.25,sy+sw*0.75);ctx.lineTo(sx+sw*0.5,sy+sw*0.35);ctx.stroke();
          ctx.beginPath();ctx.moveTo(sx+sw*0.75,sy+sw*0.75);ctx.lineTo(sx+sw*0.5,sy+sw*0.35);ctx.stroke();
          // Ore sparkle
          ctx.fillStyle='rgba(140,170,220,0.5)';ctx.beginPath();ctx.arc(sx+sw*0.5,sy+sw*0.6,2*z,0,Math.PI*2);ctx.fill();
        }
      }
      if(s.type==='GOLD_MINE'){
        // Ornate mine shaft
        ctx.fillStyle=isDestroyed?'rgba(50,45,20,0.5)':'rgba(40,35,25,0.8)';
        ctx.beginPath();ctx.moveTo(sx+sw*0.2,sy+sw*0.8);ctx.lineTo(sx+sw*0.5,sy+sw*0.3);ctx.lineTo(sx+sw*0.8,sy+sw*0.8);ctx.fill();
        // Gold trim archway
        if(!isDestroyed){
          ctx.strokeStyle='rgba(220,190,60,0.6)';ctx.lineWidth=z*2;
          ctx.beginPath();ctx.moveTo(sx+sw*0.25,sy+sw*0.78);ctx.lineTo(sx+sw*0.5,sy+sw*0.35);ctx.lineTo(sx+sw*0.75,sy+sw*0.78);ctx.stroke();
          // Gold nuggets
          ctx.fillStyle='rgba(255,215,0,0.6)';
          ctx.beginPath();ctx.arc(sx+sw*0.4,sy+sw*0.65,2*z,0,Math.PI*2);ctx.fill();
          ctx.beginPath();ctx.arc(sx+sw*0.6,sy+sw*0.6,1.5*z,0,Math.PI*2);ctx.fill();
        }
      }
      // ── CRACKED OVERLAY when destroyed (hp<=0) ──
      if(isDestroyed){
        ctx.strokeStyle='rgba(180,50,30,0.6)';ctx.lineWidth=z*1.5;
        // Large X crack
        ctx.beginPath();ctx.moveTo(sx+sw*0.15,sy+sw*0.15);ctx.lineTo(sx+sw*0.85,sy+sw*0.85);ctx.stroke();
        ctx.beginPath();ctx.moveTo(sx+sw*0.85,sy+sw*0.15);ctx.lineTo(sx+sw*0.15,sy+sw*0.85);ctx.stroke();
        // Jagged crack lines
        ctx.strokeStyle='rgba(120,40,20,0.4)';ctx.lineWidth=z;
        ctx.beginPath();ctx.moveTo(sx+sw*0.5,sy+sw*0.1);ctx.lineTo(sx+sw*0.45,sy+sw*0.35);ctx.lineTo(sx+sw*0.55,sy+sw*0.5);ctx.lineTo(sx+sw*0.4,sy+sw*0.7);ctx.lineTo(sx+sw*0.5,sy+sw*0.9);ctx.stroke();
        // Dark smoke overlay
        ctx.fillStyle='rgba(30,20,15,0.3)';ctx.fillRect(sx+z,sy+z,sw-2*z,sw-2*z);
        // "DESTROYED" tint
        ctx.fillStyle='rgba(80,20,10,0.15)';ctx.fillRect(sx,sy,sw,sw);
      }
      // Production badge — top-right corner (shows +3 and resource type)
      if(!isDestroyed){
        const badgeX=sx+sw*0.85,badgeY=sy+sw*0.15,badgeR=sw*0.16;
        ctx.beginPath();ctx.arc(badgeX,badgeY,badgeR,0,Math.PI*2);
        ctx.fillStyle='rgba(40,120,40,0.85)';ctx.fill();
        ctx.fillStyle='rgba(255,255,255,0.9)';ctx.font=`bold ${Math.max(6,sw*0.18)|0}px system-ui`;
        ctx.textAlign='center';ctx.textBaseline='middle';
        ctx.fillText('+'+rb.perWave,badgeX,badgeY);
      }
      // Repair count badge — bottom-left (shows repairs remaining)
      if(s.repairsUsed>0){
        const rpX=sx+sw*0.15,rpY=sy+sw*0.85,rpR=sw*0.14;
        ctx.beginPath();ctx.arc(rpX,rpY,rpR,0,Math.PI*2);
        ctx.fillStyle='rgba(180,80,30,0.8)';ctx.fill();
        ctx.fillStyle='rgba(255,255,255,0.9)';ctx.font=`bold ${Math.max(5,sw*0.15)|0}px system-ui`;
        ctx.textAlign='center';ctx.textBaseline='middle';
        ctx.fillText((rb.maxRepairs-s.repairsUsed)+'',rpX,rpY);
      }
    }
"""
ops.append((draw_citizen_line, 'insert_before', resource_rendering))

# ============================================================
# 7. Update the letter rendering skip — skip for resource buildings too
#    Find "if(s.type!=='CITIZEN_BLOCK')" near the letter drawing
# ============================================================
letter_skip_line = None
for i, line in enumerate(lines):
    if "s.type!=='CITIZEN_BLOCK'" in line and "Letter label" in lines[i-1] if i > 0 else False:
        letter_skip_line = i
        break

if letter_skip_line is None:
    for i, line in enumerate(lines):
        if "s.type!=='CITIZEN_BLOCK'" in line and "letter" in lines[i+1].lower() if i+1 < len(lines) else False:
            letter_skip_line = i
            break

if letter_skip_line is not None:
    old_line = lines[letter_skip_line]
    new_line = old_line.replace(
        "if(s.type!=='CITIZEN_BLOCK')",
        "if(s.type!=='CITIZEN_BLOCK'&&!RESOURCE_BUILDINGS[s.type])"
    )
    ops.append((letter_skip_line, 'replace', new_line))

# ============================================================
# 8. Add CSS for resource building toolbar buttons
#    Find the .tb-demolish-btn style and add resource btn style after
# ============================================================
demolish_css_line = None
for i, line in enumerate(lines):
    if '.tb-demolish-btn.active' in line:
        demolish_css_line = i
        break

if demolish_css_line is not None:
    resource_css = """
  /* Resource building buttons */
  .tool-btn[data-tool="FARM"] { border-color: rgba(180,140,80,0.2); }
  .tool-btn[data-tool="LUMBER"] { border-color: rgba(120,90,50,0.2); }
  .tool-btn[data-tool="QUARRY"] { border-color: rgba(140,140,150,0.2); }
  .tool-btn[data-tool="MINE"] { border-color: rgba(100,130,180,0.2); }
  .tool-btn[data-tool="GOLD_MINE"] { border-color: rgba(200,180,60,0.2); }
"""
    ops.append((demolish_css_line, 'insert_after', resource_css))

# ============================================================
# 9. handleBuild — resource buildings can't be placed yet (Step 2 requirement)
#    Add a check at the top of handleBuild: if selectedTool is a resource building, show "Coming soon"
#    Find "function handleBuild" and insert check after the first line
# ============================================================
handle_build_line = None
for i, line in enumerate(lines):
    if 'function handleBuild(col,row)' in line:
        handle_build_line = i
        break

assert handle_build_line is not None, "Could not find handleBuild function"

# Insert after the "const def=STRUCTS[selectedTool]" line (line after function declaration)
coming_soon_check = """  // Resource buildings: placement not yet implemented (Step 2 — toolbar only)
  if(RESOURCE_BUILDINGS[selectedTool]){
    addFloat('Building system coming soon!',col*TILE_SIZE+TILE_SIZE/2,row*TILE_SIZE,'#e8c56a');
    return;
  }
"""
ops.append((handle_build_line, 'insert_after', coming_soon_check))

# ============================================================
# APPLY ALL OPS — bottom to top to avoid line-shift
# ============================================================

# Sort ops by line number descending
ops.sort(key=lambda x: x[0], reverse=True)

for line_num, op_type, content in ops:
    content_lines = content.split('\n') if not content.endswith('\n') else content.rstrip('\n').split('\n')
    # Ensure each line ends with \n
    content_lines = [l + '\n' for l in content_lines]
    
    if op_type == 'insert_after':
        lines[line_num+1:line_num+1] = content_lines
    elif op_type == 'insert_before':
        lines[line_num:line_num] = content_lines
    elif op_type == 'replace':
        lines[line_num] = content

with open('index.html', 'w') as f:
    f.writelines(lines)

print(f"✅ Patch applied. New line count: {len(lines)}")
print("Changes:")
print("  1. RESOURCE_BUILDINGS constant added (5 buildings)")
print("  2. Resources category tab (key 4) added to toolbar")
print("  3. 5 resource building buttons in toolbar")
print("  4. Unique rendering for each building type + cracked overlay")
print("  5. Letter rendering skip for resource buildings")
print("  6. CSS styles for resource buttons")
print("  7. handleBuild blocks resource building placement (coming soon)")
print("  8. Hint text for resource buildings")
print("  9. Keyboard shortcut 4 for resources tab")
