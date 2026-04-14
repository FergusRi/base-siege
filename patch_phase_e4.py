#!/usr/bin/env python3
"""Phase E Part 4: Fix all remaining u.col/u.row references."""

FILE = 'index.html'

with open(FILE, 'r') as f:
    src = f.read()
lines = src.split('\n')

def find_line(pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    raise ValueError(f"Pattern not found from line {start}: {pattern}")

def find_line_safe(pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

fixes = 0

# Fix 1: onFriendlyDeath(u.col, u.row, rank)
idx = find_line_safe("onFriendlyDeath(u.col,u.row,rank)")
if idx >= 0:
    lines[idx] = lines[idx].replace("onFriendlyDeath(u.col,u.row,rank)", "onFriendlyDeath(Math.floor(u.x/TILE_SIZE),Math.floor(u.y/TILE_SIZE),rank)")
    fixes += 1
    print(f"  Fix {fixes}: onFriendlyDeath at line {idx+1}")

# Fix 2-8: All "const ux=u.col*TILE_SIZE+TILE_SIZE/2, uy=u.row*TILE_SIZE+TILE_SIZE/2;"
# These appear in morale/cavalry/charge functions — scan and replace all
search_from = 0
while True:
    idx = find_line_safe("const ux=u.col*TILE_SIZE+TILE_SIZE/2, uy=u.row*TILE_SIZE+TILE_SIZE/2;", search_from)
    if idx < 0:
        break
    lines[idx] = lines[idx].replace("const ux=u.col*TILE_SIZE+TILE_SIZE/2, uy=u.row*TILE_SIZE+TILE_SIZE/2;", "const ux=u.x, uy=u.y;")
    fixes += 1
    print(f"  Fix {fixes}: ux/uy conversion at line {idx+1}")
    search_from = idx + 1

# Similar pattern with double x
search_from = 0
while True:
    idx = find_line_safe("const uxx=u.col*TILE_SIZE+TILE_SIZE/2, uyy=u.row*TILE_SIZE+TILE_SIZE/2;", search_from)
    if idx < 0:
        break
    lines[idx] = lines[idx].replace("const uxx=u.col*TILE_SIZE+TILE_SIZE/2, uyy=u.row*TILE_SIZE+TILE_SIZE/2;", "const uxx=u.x, uyy=u.y;")
    fixes += 1
    print(f"  Fix {fixes}: uxx/uyy conversion at line {idx+1}")
    search_from = idx + 1

# Fix: baseDist calculation
idx = find_line_safe("const baseDist=Math.abs(u.col-BASE_CX)+Math.abs(u.row-BASE_CY);")
if idx >= 0:
    lines[idx] = lines[idx].replace(
        "const baseDist=Math.abs(u.col-BASE_CX)+Math.abs(u.row-BASE_CY);",
        "const baseDist=Math.abs(Math.floor(u.x/TILE_SIZE)-BASE_CX)+Math.abs(Math.floor(u.y/TILE_SIZE)-BASE_CY);"
    )
    fixes += 1
    print(f"  Fix {fixes}: baseDist at line {idx+1}")

# Fix: deadCol/deadRow distance
idx = find_line_safe("const dist=Math.abs(u.col-deadCol)+Math.abs(u.row-deadRow);")
if idx >= 0:
    lines[idx] = lines[idx].replace(
        "const dist=Math.abs(u.col-deadCol)+Math.abs(u.row-deadRow);",
        "const dist=Math.abs(Math.floor(u.x/TILE_SIZE)-deadCol)+Math.abs(Math.floor(u.y/TILE_SIZE)-deadRow);"
    )
    fixes += 1
    print(f"  Fix {fixes}: deadCol/deadRow at line {idx+1}")

# Fix: handleDemolish findIndex using col/row
idx = find_line_safe("const uIdx=units.findIndex(u=>u.col===col&&u.row===row);")
if idx >= 0:
    lines[idx] = lines[idx].replace(
        "const uIdx=units.findIndex(u=>u.col===col&&u.row===row);",
        "const uIdx=units.findIndex(u=>Math.abs(u.x-(col*TILE_SIZE+TILE_SIZE/2))<TILE_SIZE&&Math.abs(u.y-(row*TILE_SIZE+TILE_SIZE/2))<TILE_SIZE);"
    )
    fixes += 1
    print(f"  Fix {fixes}: handleDemolish findIndex at line {idx+1}")

# Fix: Ghost preview pu.col/pu.row references (these are in drawGhostPreview)
# wDist check
search_from = 0
while True:
    idx = find_line_safe("const wDist=Math.abs(col-pu.col)+Math.abs(row-pu.row);", search_from)
    if idx < 0:
        break
    lines[idx] = lines[idx].replace(
        "const wDist=Math.abs(col-pu.col)+Math.abs(row-pu.row);",
        "const wDist=Math.abs(col-Math.floor(pu.x/TILE_SIZE))+Math.abs(row-Math.floor(pu.y/TILE_SIZE));"
    )
    fixes += 1
    print(f"  Fix {fixes}: wDist ghost at line {idx+1}")
    search_from = idx + 1

# pu screen position
search_from = 0
while True:
    idx = find_line_safe("const pux=(pu.col*TILE_SIZE+TILE_SIZE/2-cam.x)*z, puy=(pu.row*TILE_SIZE+TILE_SIZE/2-cam.y)*z;", search_from)
    if idx < 0:
        break
    lines[idx] = lines[idx].replace(
        "const pux=(pu.col*TILE_SIZE+TILE_SIZE/2-cam.x)*z, puy=(pu.row*TILE_SIZE+TILE_SIZE/2-cam.y)*z;",
        "const pux=(pu.x-cam.x)*z, puy=(pu.y-cam.y)*z;"
    )
    fixes += 1
    print(f"  Fix {fixes}: pu screen coords at line {idx+1}")
    search_from = idx + 1

# meleeGrid using col,row
idx = find_line_safe("if(isMeleeUnit(u.type)&&u.hp>0)meleeGrid[u.col+','+u.row]=u;")
if idx >= 0:
    lines[idx] = lines[idx].replace(
        "if(isMeleeUnit(u.type)&&u.hp>0)meleeGrid[u.col+','+u.row]=u;",
        "if(isMeleeUnit(u.type)&&u.hp>0)meleeGrid[Math.floor(u.x/TILE_SIZE)+','+Math.floor(u.y/TILE_SIZE)]=u;"
    )
    fixes += 1
    print(f"  Fix {fixes}: meleeGrid at line {idx+1}")

# Old minimap u.col/u.row (might be a second minimap reference)
idx = find_line_safe("mmCtx.fillRect(u.col*sx,u.row*sy,")
if idx >= 0:
    lines[idx] = lines[idx].replace(
        "mmCtx.fillRect(u.col*sx,u.row*sy,",
        "mmCtx.fillRect((u.x/TILE_SIZE)*sx,(u.y/TILE_SIZE)*sy,"
    )
    fixes += 1
    print(f"  Fix {fixes}: old minimap ref at line {idx+1}")

# Line 7020-ish: another ux=u.col reference (might be in cycleUnit or similar)
idx = find_line_safe("const ux=u.col*TILE_SIZE+TILE_SIZE/2, uy=u.row*TILE_SIZE+TILE_SIZE/2;")
if idx >= 0:
    lines[idx] = lines[idx].replace("const ux=u.col*TILE_SIZE+TILE_SIZE/2, uy=u.row*TILE_SIZE+TILE_SIZE/2;", "const ux=u.x, uy=u.y;")
    fixes += 1
    print(f"  Fix {fixes}: remaining ux/uy at line {idx+1}")

print(f"\nTotal fixes applied: {fixes}")

# Final scan for any remaining
print("\nFinal scan for remaining u.col/u.row...")
remaining = 0
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('//') or stripped.startswith('*'):
        continue
    if 'u.col' in line or 'u.row' in line:
        # Skip if in comment context
        if '// ' in line and line.index('//') < line.index('u.col' if 'u.col' in line else 'u.row'):
            continue
        remaining += 1
        print(f"  Line {i+1}: {stripped[:120]}")

if remaining == 0:
    print("  ✓ All u.col/u.row references fixed!")
else:
    print(f"  ⚠ {remaining} remaining (may be in comments or other variable names)")

# Save
with open(FILE, 'w') as f:
    f.write('\n'.join(lines))
print("\n  ✓ Saved (Part 4 complete)")
