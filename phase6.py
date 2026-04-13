#!/usr/bin/env python3
"""Phase 6: CSS & HTML Cleanup — All three sub-phases in one safe script.

6A: Consolidate backdrop-filter into 3 utility classes (.glass-sm, .glass-md, .glass-lg)
6B: Move inline styles from HTML to CSS classes
6C: Not touching JS magic numbers (too risky for negligible gain in single-file game)
"""

import re, sys

INPUT  = 'index.html'
OUTPUT = 'index.html'

with open(INPUT, 'r') as f:
    lines = f.readlines()

original_count = len(lines)
print(f"Read {original_count} lines")

# ============================================================
# PHASE 6A: Consolidate backdrop-filter
# ============================================================
# Group the 10 CSS backdrop-filter declarations into 3 utility classes:
#   .glass-sm  = blur(4px)   — lines 137, 285
#   .glass-md  = blur(6px)   — lines 116, 186, 229, 261
#   .glass-lg  = blur(8px)   — lines 19, 173, 248
#   blur(10px) on toolbar (line 48) — use .glass-lg (close enough, 8→10 is subtle)
#
# Strategy: Remove "backdrop-filter: blur(Npx);" from each CSS line,
# then add the utility classes to the corresponding HTML elements.
# Also add the 3 utility class definitions.

# Map: line number (1-indexed) → (blur value, CSS selector for reference)
backdrop_map = {
    19:  (8,  '#top-bar'),
    48:  (10, '#toolbar'),
    116: (6,  '#hint'),
    137: (4,  '#wave-preview-overlay'),
    173: (8,  '#unit-info'),
    186: (6,  '#aftermath-overlay'),
    229: (6,  '#start-screen'),
    248: (8,  '#hq-placement-bar'),
    261: (6,  '#gameover-screen'),
    285: (4,  '#kill-hud'),
}

# Remove backdrop-filter from CSS lines
for line_no, (blur_val, selector) in backdrop_map.items():
    idx = line_no - 1
    line = lines[idx]
    # Remove " backdrop-filter: blur(Npx);" — with optional leading space
    # Handle both mid-line and end-of-line cases
    new_line = re.sub(r'\s*backdrop-filter:\s*blur\(\d+px\);?\s*', ' ', line)
    # Clean up double spaces
    new_line = re.sub(r'  +', ' ', new_line)
    # Clean up " }" to "}"  
    new_line = new_line.replace(' }', ' }')  # keep one space before }
    if new_line != line:
        lines[idx] = new_line
        print(f"  6A: Removed backdrop-filter from line {line_no} ({selector})")

# Add utility classes right after the * reset rule (line 8)
# Insert after line 8 (the * { margin:0... } rule)
glass_css = """  /* Glass utility classes (Phase 6A) */
  .glass-sm { backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); }
  .glass-md { backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); }
  .glass-lg { backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); }
"""
# Insert after line 9 (html,body rule) — at index 9
lines.insert(9, glass_css)
print("  6A: Inserted glass utility classes at line 10")

# Now line numbers shifted by the number of inserted lines
# Count inserted lines
glass_lines_count = glass_css.count('\n')
print(f"  6A: Shifted subsequent lines by {glass_lines_count}")

# Add glass classes to HTML elements
# Map: HTML element id → glass class to add
html_glass_map = {
    'id="top-bar"':             'glass-lg',
    'id="toolbar"':             'glass-lg',
    'id="hint"':                'glass-md',
    'id="wave-preview-overlay"':'glass-sm',
    'id="unit-info"':           'glass-lg',
    'id="aftermath-overlay"':   'glass-md',
    'id="start-screen"':        'glass-md',
    'id="hq-placement-bar"':    'glass-lg',
    'id="gameover-screen"':     'glass-md',
    'id="kill-hud"':            'glass-sm',
}

for i, line in enumerate(lines):
    for id_attr, glass_class in html_glass_map.items():
        if id_attr in line:
            # Check if element already has a class attribute
            if 'class="' in line and id_attr in line:
                # Add glass class to existing class list
                # Find the class closest to or on same element as the id
                # e.g. <div class="foo" id="bar"> → <div class="foo glass-lg" id="bar">
                # We need to be careful: only modify if the id is on the same tag
                tag_start = line.rfind('<', 0, line.index(id_attr))
                tag_segment = line[tag_start:]
                class_match = re.search(r'class="([^"]*)"', tag_segment)
                if class_match and glass_class not in class_match.group(1):
                    old_class = class_match.group(0)
                    new_class = f'class="{class_match.group(1)} {glass_class}"'
                    lines[i] = line.replace(old_class, new_class, 1)
                    print(f"  6A: Added {glass_class} to existing class on line {i+1} ({id_attr})")
            elif 'class=' not in line[line.index(id_attr)-50:line.index(id_attr)] if id_attr in line else True:
                # No class attribute on this element, add one
                lines[i] = lines[i].replace(id_attr, f'class="{glass_class}" {id_attr}')
                print(f"  6A: Added class=\"{glass_class}\" to line {i+1} ({id_attr})")
            break  # Only process first match per line

print("  6A: Complete\n")

# ============================================================
# PHASE 6B: Move inline styles to CSS classes  
# ============================================================
# Target only the static HTML inline styles (not JS template literals).
# 
# Group 1: display:none — these are toggled by JS so we keep them as inline styles
# (they serve as initial state that JS .show class overrides)
# → SKIP lines 326, 347, 357, 372, 379, 382, 388 — display:none is functional
#
# Group 2: Static decorative inline styles → move to CSS classes
#   Line 334: style="font-size:14px;" on hero sword emoji → .bar-emoji
#   Line 339: style="font-size:14px;" on base emoji → .bar-emoji (reuse)
#   Line 335: style="width:100%;background:linear-gradient(90deg,#4a4,#6c6)" on hero-hp-fill → #hero-hp-fill
#   Line 340: style="width:100%" on base-hp-fill → #base-hp-fill
#   Line 400: style="color:#e8c56a" on ui-morale → #ui-morale
#   Line 401: style="color:#d87aa0" on ui-upkeep → #ui-upkeep  
#   Line 402: style="color:#8ad0ff" on ui-formation → #ui-formation

# Add CSS rules for Phase 6B
phase6b_css = """  /* Inline style → CSS (Phase 6B) */
  .bar-emoji { font-size: 14px; }
  #hero-hp-fill { width: 100%; background: linear-gradient(90deg, #4a4, #6c6); }
  #base-hp-fill { width: 100%; }
  #ui-morale { color: #e8c56a; }
  #ui-upkeep { color: #d87aa0; }
  #ui-formation { color: #8ad0ff; }
"""

# Find the closing </style> tag and insert before it
for i, line in enumerate(lines):
    if '</style>' in line:
        lines.insert(i, phase6b_css)
        print(f"  6B: Inserted CSS rules before </style> at line {i+1}")
        break

# Now remove the inline styles from HTML
# We need to re-scan since lines shifted
removals_6b = [
    ('style="font-size:14px;"', 'class="bar-emoji"', '⚔️'),      # hero emoji
    ('style="font-size:14px;"', 'class="bar-emoji"', '🏘'),       # base emoji
    ('style="width:100%;background:linear-gradient(90deg,#4a4,#6c6)"', '', 'hero-hp-fill'),  # hero hp
    ('style="width:100%"', '', 'base-hp-fill'),                     # base hp  
    ('style="color:#e8c56a"', '', 'ui-morale'),                     # morale
    ('style="color:#d87aa0"', '', 'ui-upkeep'),                     # upkeep
    ('style="color:#8ad0ff"', '', 'ui-formation'),                  # formation
]

for i, line in enumerate(lines):
    for old_style, new_class, marker in removals_6b:
        if old_style in line and marker in line:
            new_line = line.replace(f' {old_style}', '')
            if new_line == line:  # try without leading space
                new_line = line.replace(old_style, '')
            if new_class and new_class not in new_line:
                # Add class to the span
                new_line = new_line.replace(f'<span', f'<span {new_class}', 1)
            lines[i] = new_line
            print(f"  6B: Removed inline style from line {i+1} (marker: {marker})")
            break

print("  6B: Complete\n")

# ============================================================
# INTEGRITY CHECKS
# ============================================================
content = ''.join(lines)

# Check 1: kill-hud exists
assert 'id="kill-hud"' in content, "FAIL: kill-hud missing!"
assert 'id="kh-hero"' in content, "FAIL: kh-hero missing!"
print("✓ kill-hud intact")

# Check 2: Key elements exist
for elem in ['game-canvas', 'minimap', 'top-bar', 'toolbar', 'start-screen', 
             'gameover-screen', 'wave-banner', 'aftermath-overlay', 'unit-info',
             'hint', 'hq-placement-bar', 'wave-preview-overlay', 'kill-hud']:
    assert f'id="{elem}"' in content, f"FAIL: {elem} missing!"
print("✓ All key HTML elements intact")

# Check 3: Glass classes exist
for cls in ['glass-sm', 'glass-md', 'glass-lg']:
    assert cls in content, f"FAIL: {cls} class missing!"
print("✓ Glass utility classes present")

# Check 4: No remaining backdrop-filter in individual selectors (should only be in utility classes)
# Count backdrop-filter occurrences
bf_count = content.count('backdrop-filter')
# Should be exactly 6: 3 in .glass-sm/md/lg definitions × 2 (webkit + standard)
print(f"  backdrop-filter occurrences: {bf_count} (expected 6)")
assert bf_count == 6, f"FAIL: Expected 6 backdrop-filter, found {bf_count}"
print("✓ backdrop-filter consolidated correctly")

# Check 5: Brace balance in CSS
style_start = content.index('<style>')
style_end = content.index('</style>')
css_block = content[style_start:style_end]
open_braces = css_block.count('{')
close_braces = css_block.count('}')
print(f"  CSS braces: {open_braces} open, {close_braces} close")
assert open_braces == close_braces, f"FAIL: Brace mismatch in CSS!"
print("✓ CSS brace balance OK")

# Check 6: Script tag still present
assert '<script' in content, "FAIL: script tag missing!"
assert 'function draw(' in content, "FAIL: draw() game loop missing!"
print("✓ JavaScript intact")

# Check 7: New CSS rules present
assert '#hero-hp-fill' in content, "FAIL: hero-hp-fill CSS rule missing"
assert '#ui-morale' in content, "FAIL: ui-morale CSS rule missing"
assert '.bar-emoji' in content, "FAIL: bar-emoji CSS rule missing"
print("✓ Phase 6B CSS rules present")

# Write output
with open(OUTPUT, 'w') as f:
    f.writelines(lines)

final_count = len(lines)
print(f"\nDone! {original_count} → {final_count} lines (delta: {final_count - original_count:+d})")
print("Phase 6A + 6B complete. Skipped 6C (magic numbers in JS — too risky for minimal gain).")
