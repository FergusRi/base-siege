#!/usr/bin/env python3
"""
Phase 2: Insert §1-§17 section headers + TOC into index.html.
Strategy:
  - Replace existing ═══ section header blocks with §-tagged versions
  - Keep the game title block (BASE SIEGE) untouched
  - Insert new §-headers where no existing block exists
  - Add TOC after the game title block
Works bottom-to-top so line numbers don't shift.
"""

INPUT  = '/home/user/base-siege/index.html'
OUTPUT = '/home/user/base-siege/index.html'

with open(INPUT, 'r') as f:
    lines = f.readlines()

total = len(lines)
print(f"Read {total} lines")

def make_header(num, title):
    tag = f"§{num}"
    inner = f"  {tag}  {title}  "
    width = max(len(inner) + 4, 55)
    bar = "═" * width
    return [
        f"// {bar}\n",
        f"//{inner}\n",
        f"// {bar}\n",
    ]

# ── PHASE A: Replace existing ═══ headers (NOT the title block) ──
# (middle_line_1idx, section_num, new_title_or_None_for_subsection)
replacements = [
    # Skip line 454 — that's the game title "BASE SIEGE", not a section
    (1052, 3,  "CITIZEN SYSTEM"),
    (1571, 6,  "PATHFINDING (A* + BFS)"),
    (1660, 7,  "GAME STATE & ENTITIES"),
    (1974, 10, "COMBAT (waves, enemies, hero, towers, projectiles)"),
    (2616, 10, None),   # HERO COMBAT sub-header → §10 (cont.)
    (2965, 10, None),   # TOWER COMBAT sub-header → §10 (cont.)
    (3093, 11, "UNIT AI & FORMATIONS"),
    (3426, 12, "ECONOMY, UPKEEP & FORMATIONS"),
    (3613, 13, "MORALE & VETERANCY"),
    (3736, 14, "INPUT & CAMERA"),
    (4077, 15, "RENDERING"),
    (5321, 17, "SCREENS, OVERLAYS & GAME LOOP"),
    (5457, 17, None),   # MAIN GAME LOOP sub-header → §17 (cont.)
]

replacements.sort(key=lambda r: r[0], reverse=True)

for mid_line_1idx, sec_num, new_title in replacements:
    idx_above = mid_line_1idx - 2  # 0-indexed (═══ bar above)
    idx_mid   = mid_line_1idx - 1  # 0-indexed (title line)
    idx_below = mid_line_1idx      # 0-indexed (═══ bar below)
    
    if '═══' not in lines[idx_above] or '═══' not in lines[idx_below]:
        print(f"  WARNING: Expected ═══ bars around line {mid_line_1idx}, skipping")
        continue
    
    if new_title is not None:
        new_block = make_header(sec_num, new_title)
        lines[idx_above:idx_below+1] = new_block
        print(f"  Replaced L{mid_line_1idx} → §{sec_num} {new_title}")
    else:
        old_text = lines[idx_mid].strip().lstrip('/').strip()
        lines[idx_mid] = f"//  §{sec_num} (cont.) — {old_text}\n"
        print(f"  Relabeled L{mid_line_1idx} → §{sec_num} (cont.)")

# ── PHASE B: Insert NEW §-headers ──
def find_line(text, start=0):
    for i in range(start, len(lines)):
        if text in lines[i]:
            return i + 1  # 1-indexed
    return None

new_sections = []

# §1 CONSTANTS & CONFIG — before "// ─── CONSTANTS ───"
ln = find_line("// ─── CONSTANTS ───")
if ln: new_sections.append((ln, 1, "CONSTANTS & CONFIG"))

# §2 TILE TYPES & STRUCTS — before "const T={GRASS"
ln = find_line("const T={GRASS")
if ln: new_sections.append((ln, 2, "TILE TYPES & STRUCTS"))

# §4 FOG OF WAR — before "// ─── FOG OF WAR ───"
ln = find_line("// ─── FOG OF WAR ───")
if ln: new_sections.append((ln, 4, "FOG OF WAR"))

# §5 MAP GENERATION — before "// ─── NOISE ───"
ln = find_line("// ─── NOISE ───")
if ln: new_sections.append((ln, 5, "MAP GENERATION"))

# §8 SPAWN & WAVE SYSTEM — before "// ─── ENEMY CAMPS ───"
ln = find_line("// ─── ENEMY CAMPS ───")
if ln: new_sections.append((ln, 8, "SPAWN & WAVE SYSTEM"))

# §9 UI & MODE SYSTEM — before "// ─── BUILD / TOOL STATE ───"
ln = find_line("// ─── BUILD / TOOL STATE ───")
if ln: new_sections.append((ln, 9, "UI & MODE SYSTEM"))

# §16 MINIMAP — before "function drawMinimap(){"
ln = find_line("function drawMinimap(){")
if ln: new_sections.append((ln, 16, "MINIMAP"))

new_sections.sort(key=lambda s: s[0], reverse=True)
for target_line, sec_num, title in new_sections:
    idx = target_line - 1
    header = ["\n"] + make_header(sec_num, title) + ["\n"]
    lines[idx:idx] = header
    print(f"  Inserted §{sec_num} {title} before L{target_line}")

# ── PHASE C: Insert TOC after game title block ──
# Find the JS title block: look for "BASE SIEGE" AFTER the <script> tag
toc_insert_idx = None
script_start = 0
for i, line in enumerate(lines):
    if '<script>' in line and 'widget' not in line:
        script_start = i
        break
for i in range(script_start, len(lines)):
    if 'BASE SIEGE' in lines[i] and '//' in lines[i]:
        # Found the JS comment title line; find closing ═══ bar after it
        for j in range(i+1, min(i+3, len(lines))):
            if '═══' in lines[j]:
                toc_insert_idx = j + 1  # 0-indexed, after closing bar
                break
        break

if toc_insert_idx is None:
    print("ERROR: Could not find title block for TOC insertion!")
    exit(1)

all_sections = [
    (1,  "CONSTANTS & CONFIG"),
    (2,  "TILE TYPES & STRUCTS"),
    (3,  "CITIZEN SYSTEM"),
    (4,  "FOG OF WAR"),
    (5,  "MAP GENERATION"),
    (6,  "PATHFINDING (A* + BFS)"),
    (7,  "GAME STATE & ENTITIES"),
    (8,  "SPAWN & WAVE SYSTEM"),
    (9,  "UI & MODE SYSTEM"),
    (10, "COMBAT (waves, enemies, hero, towers, projectiles)"),
    (11, "UNIT AI & FORMATIONS"),
    (12, "ECONOMY, UPKEEP & FORMATIONS"),
    (13, "MORALE & VETERANCY"),
    (14, "INPUT & CAMERA"),
    (15, "RENDERING"),
    (16, "MINIMAP"),
    (17, "SCREENS, OVERLAYS & GAME LOOP"),
]

toc = [
    "\n",
    "// ┌───────────────────────────────────────────────────────────────┐\n",
    "// │                     TABLE OF CONTENTS                        │\n",
    "// ├───────────────────────────────────────────────────────────────┤\n",
]
for num, title in all_sections:
    tag = f"§{num:<3}"
    entry = f"// │  {tag} {title:<57}│\n"
    toc.append(entry)
toc.append("// └───────────────────────────────────────────────────────────────┘\n")

lines[toc_insert_idx:toc_insert_idx] = toc
print(f"\n  Inserted TOC ({len(toc)} lines) after title block at L{toc_insert_idx+1}")

with open(OUTPUT, 'w') as f:
    f.writelines(lines)

new_total = len(lines)
print(f"\nDone! {total} → {new_total} lines (+{new_total - total} lines added)")
