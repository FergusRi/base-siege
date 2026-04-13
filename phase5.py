#!/usr/bin/env python3
"""Phase 5: Combat Code Dedup — Cavalry helper + Gate destruction dedup"""
import sys

FILE = 'index.html'
with open(FILE, 'r') as f:
    lines = f.readlines()

original_count = len(lines)
print(f"Read {original_count} lines")

# ─────────────────────────────────────────────────────────────────
# 5A: Create cavalryAttack(u, nearest) helper and replace both blocks
# ─────────────────────────────────────────────────────────────────

# The helper function — to be inserted before §11 UNIT AI section
cavalry_helper = '''\
// ── Shared cavalry attack (charge + Thundercharge) ──
function cavalryAttack(u, nearest){
  const isThunder=unitRank(u.xp)>=3;
  const chargeMult=isThunder?4.0:CAVALRY_CHARGE_MULT;
  u.atkCooldown=getUnitAtkRate(u);
  let dmg=u.dmg;
  if(!u.hasCharged){dmg=Math.round(u.dmg*chargeMult);u.hasCharged=true;}
  nearest.hp-=dmg;
  nearest.hitFlash=1;
  const isCharge=dmg>u.dmg;
  addFloat(`${isCharge?(isThunder?'⚡⚡ THUNDER ':'⚡ '):''}−${dmg}`,nearest.x,nearest.y-14,isCharge?'#ffcc44':'#c88040');
  addParticles(nearest.x,nearest.y,isCharge?'rgba(255,200,60,0.8)':'rgba(160,100,60,0.7)',isCharge?8:4);
  if(isCharge){
    cam.shake=Math.max(cam.shake,isThunder?6:3);
    if(isThunder){
      for(const se of enemies){
        const sdx=se.x-nearest.x,sdy=se.y-nearest.y;
        if(sdx*sdx+sdy*sdy<=(2*TILE_SIZE)*(2*TILE_SIZE)) se.slowTimer=Math.max(se.slowTimer,0.8);
      }
      addParticles(nearest.x,nearest.y,'rgba(255,255,100,0.9)',10);
    }
  }
  if(nearest.hp<=0){
    const idx=enemies.indexOf(nearest);
    if(idx>=0){killEnemy(nearest,idx,'unit',u);u.xp+=10;}
  } else {
    u.xp+=1;
    const nr=checkRankUp(u); if(nr>0) showRankUpEffect(u,nr);
  }
}

'''

# ─────────────────────────────────────────────────────────────────
# Find exact line numbers by content matching
# ─────────────────────────────────────────────────────────────────

def find_line(text, start=0):
    """Find 1-indexed line number containing text, searching from start (0-indexed)"""
    for i in range(start, len(lines)):
        if text in lines[i]:
            return i + 1  # 1-indexed
    return None

# --- 5A PATROL CAVALRY (first block) ---
# Find: "if(nearest&&u.atkCooldown<=0){" inside the patrol section (around line 3112)
patrol_atk_start = find_line('if(nearest&&u.atkCooldown<=0){', 3100)
assert patrol_atk_start, "Could not find patrol cavalry attack start"
print(f"Patrol cavalry attack starts at line {patrol_atk_start}")

# The block ends with the closing "}" of the if — find it
# It's the line with just "      }" after the xp/rankup logic
# We need to find the closing brace that matches — count from patrol_atk_start
brace_depth = 0
patrol_atk_end = None
for i in range(patrol_atk_start - 1, len(lines)):
    line = lines[i]
    brace_depth += line.count('{') - line.count('}')
    if brace_depth == 0:
        patrol_atk_end = i + 1  # 1-indexed
        break
assert patrol_atk_end, "Could not find patrol cavalry attack end"
print(f"Patrol cavalry attack ends at line {patrol_atk_end}")

# --- 5A STATIONARY CAVALRY (second block) ---
# Find: "else if(u.type==='CAVALRY'){" around line 3252
stat_cav_start = find_line("else if(u.type==='CAVALRY'){", 3240)
assert stat_cav_start, "Could not find stationary cavalry start"
print(f"Stationary cavalry block starts at line {stat_cav_start}")

# Find the end of this block
brace_depth = 0
stat_cav_end = None
for i in range(stat_cav_start - 1, len(lines)):
    line = lines[i]
    brace_depth += line.count('{') - line.count('}')
    if brace_depth == 0:
        stat_cav_end = i + 1  # 1-indexed
        break
assert stat_cav_end, "Could not find stationary cavalry end"
print(f"Stationary cavalry block ends at line {stat_cav_end}")

# --- 5B GATE DESTRUCTION ---
# Find: "if(struct.hp<=0){" after the gate section (around line 2908)
gate_section_start = find_line("if(struct&&struct.type==='GATE'){", 2890)
assert gate_section_start, "Could not find gate section"
print(f"Gate section starts at line {gate_section_start}")

# Find "if(struct.hp<=0){" within this gate block
gate_destroy_start = find_line("if(struct.hp<=0){", gate_section_start - 1)
assert gate_destroy_start, "Could not find gate destroy start"
print(f"Gate destroy block starts at line {gate_destroy_start}")

# Find the closing brace of this if block
brace_depth = 0
gate_destroy_end = None
for i in range(gate_destroy_start - 1, len(lines)):
    line = lines[i]
    brace_depth += line.count('{') - line.count('}')
    if brace_depth == 0:
        gate_destroy_end = i + 1  # 1-indexed
        break
assert gate_destroy_end, "Could not find gate destroy end"
print(f"Gate destroy block ends at line {gate_destroy_end}")

# --- Find insertion point for cavalryAttack helper ---
# Insert before §10 COMBAT section — find the section header
combat_section = find_line('§10')
assert combat_section, "Could not find §10 COMBAT section"
print(f"§10 COMBAT section at line {combat_section}")

# ─────────────────────────────────────────────────────────────────
# Build all operations (bottom-to-top for safe line surgery)
# ─────────────────────────────────────────────────────────────────

operations = []

# Op 1: Replace stationary cavalry block (lines stat_cav_start..stat_cav_end)
stat_cav_replacement = '    else if(u.type===\'CAVALRY\'){\n      // Stationary cavalry — uses shared cavalryAttack()\n      cavalryAttack(u, nearest);\n    }\n'
operations.append(('replace', stat_cav_start, stat_cav_end, stat_cav_replacement))

# Op 2: Replace patrol cavalry attack block (lines patrol_atk_start..patrol_atk_end)
patrol_cav_replacement = '      if(nearest&&u.atkCooldown<=0){\n        cavalryAttack(u, nearest);\n      }\n'
operations.append(('replace', patrol_atk_start, patrol_atk_end, patrol_cav_replacement))

# Op 3: Replace gate destruction block with destroyStructure(sk) call
gate_replacement = '        if(struct.hp<=0) destroyStructure(sk);\n'
operations.append(('replace', gate_destroy_start, gate_destroy_end, gate_replacement))

# Op 4: Insert cavalryAttack helper before §10 COMBAT section
operations.append(('insert', combat_section, combat_section, cavalry_helper))

# Sort operations bottom-to-top (highest line first) to preserve line numbers
operations.sort(key=lambda op: -op[1])

print(f"\nApplying {len(operations)} operations (bottom-to-top):")
for op_type, start, end, _ in operations:
    print(f"  {op_type}: lines {start}-{end}")

# Apply operations
for op_type, start, end, content in operations:
    if op_type == 'replace':
        # Replace lines[start-1:end] with content
        old_lines = lines[start-1:end]
        new_lines = content.splitlines(True)
        lines[start-1:end] = new_lines
        print(f"  Replaced lines {start}-{end} ({len(old_lines)} lines -> {len(new_lines)} lines)")
    elif op_type == 'insert':
        # Insert content before line 'start'
        new_lines = content.splitlines(True)
        lines[start-1:start-1] = new_lines
        print(f"  Inserted {len(new_lines)} lines before line {start}")

new_count = len(lines)
print(f"\nResult: {original_count} -> {new_count} lines (saved {original_count - new_count} lines)")

# ─────────────────────────────────────────────────────────────────
# Integrity checks
# ─────────────────────────────────────────────────────────────────
content = ''.join(lines)

checks = [
    ('kill-hud', 'id="kill-hud"'),
    ('cavalryAttack function', 'function cavalryAttack(u, nearest)'),
    ('cavalryAttack call (patrol)', 'cavalryAttack(u, nearest);'),
    ('destroyStructure in gate', "if(struct.hp<=0) destroyStructure(sk);"),
    ('game loop', 'requestAnimationFrame'),
    ('hero object', 'const hero='),
    ('showGameOverScreen', 'function showGameOverScreen'),
    ('§10 COMBAT', '§10'),
    ('§11 UNIT AI', '§11'),
]

all_pass = True
for name, needle in checks:
    if needle not in content:
        print(f"  ❌ FAIL: {name} not found!")
        all_pass = False
    else:
        print(f"  ✅ {name}")

if not all_pass:
    print("\n❌ INTEGRITY CHECK FAILED — NOT WRITING FILE")
    sys.exit(1)

# Check brace balance in script section
script_start = content.index('<script>')
script_section = content[script_start:]
opens = script_section.count('{')
closes = script_section.count('}')
print(f"\n  Brace balance: {opens} open, {closes} close, diff={opens-closes}")
if abs(opens - closes) > 2:
    print("  ❌ BRACE IMBALANCE — NOT WRITING FILE")
    sys.exit(1)
else:
    print("  ✅ Braces balanced")

with open(FILE, 'w') as f:
    f.writelines(lines)
print(f"\n✅ Phase 5 complete — wrote {new_count} lines")
