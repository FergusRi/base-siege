# Map Generation V3 — "Continent Builder"

## The Problem
All previous approaches failed because they treated terrain as **per-tile classification** (noise → threshold → tile type). This produces scatter or blobs, never connected geographic features.

## The Reference
Your hand-drawn map shows:
- **Mountain RANGES** — elongated ridges, connected chains, not circles
- **Forest REGIONS** — large continuous masses filling valleys
- **Rivers** — flowing from highlands to map edges, creating chokepoints
- **Open grassland** — the default between features
- **Resource patches** — naturally clustered within their parent biome

## New Approach: Feature-First Generation

Instead of classifying tiles, we **draw geographic features** onto a blank grass canvas.

### Phase 1: Height Map with Ridge Lines (Mountains)

**Technique: Warped Ridge Lines**

1. Generate 3-5 **spine curves** across the map using cubic Bézier curves with random control points
2. Each spine has a **thickness profile** (wider at center, tapering at ends)
3. For each tile, calculate distance to nearest spine → if within thickness, it's mountain
4. Add **fractal displacement** to the spine edges (domain warping with fbm) so edges are jagged and natural, not smooth ellipses
5. Mountain cores (closest to spine center) get stone/ore; outer slopes get scattered stone

**Why this works:** Real mountain ranges ARE elongated ridges. Bézier curves naturally produce connected, flowing shapes.

```
Example spine: 
  Start (50, 300) → Control (250, 100) → Control (500, 400) → End (800, 200)
  Width: 40 tiles at center, 8 tiles at ends
  + fbm displacement on edges for jagged natural look
```

### Phase 2: River Carving

**Technique: Downhill Flow from Mountain Peaks**

1. Pick 2-4 points on mountain spines as **river sources**
2. From each source, walk **downhill** using the height map (mountains = high, plains = low)
3. Add gentle **random wandering** (Perlin noise offsets) so rivers meander
4. Rivers widen as they flow (1 tile at source → 2-3 tiles downstream)
5. Rivers end at map edges or join other rivers

**Why this works:** Real rivers flow from mountains to lowlands. This creates natural chokepoints between mountain ranges.

### Phase 3: Forest Regions

**Technique: Moisture-Seeded Flood Fill**

1. Generate a **moisture noise map** (low-frequency fbm, freq ~0.004)
2. Where moisture > threshold AND tile is grass AND not within 3 tiles of mountain → seed forest
3. **Grow forests** outward from seeds using cellular automata (2-3 iterations):
   - A grass tile becomes forest if 3+ neighbors are forest AND moisture > lower threshold
4. This creates large continuous blobs with organic edges
5. Add **clearings** inside forests: random patches (5-10 tile radius) reverted to grass

**Why this works:** Cellular automata naturally produces connected regions with organic boundaries. Clearings add realism and gameplay variety.

### Phase 4: Resource Scattering

Resources placed **within their parent biome** using clustered Poisson-disc sampling:

| Resource | Biome | Cluster Size | Density |
|----------|-------|-------------|---------|
| Stone | Mountain slopes | 3-8 tiles | Medium |
| Ore | Mountain cores | 2-5 tiles | Low |
| Gold | Deep mountain cores | 1-3 tiles | Very rare |
| Trees | Forest regions | Already placed | High |
| Berries | Forest edges & meadows | 2-4 tiles | Low |

**Clustering method:** Pick a random valid tile in the biome, then place 2-8 resources within a 4-tile radius. This creates natural "deposits" not scattered pixels.

### Phase 5: Polish & Validation

1. **Edge smoothing:** Remove isolated single-tile terrain (mountain/forest tiles with 0 same-type neighbors)
2. **Walkability check:** BFS from map center to ensure at least 60% of grass is reachable
3. **Base zone clearing:** Clear a 20×20 grass area near center for the starting base
4. **Minimum resource guarantee:** Ensure at least N of each resource within 100 tiles of center

---

## Implementation Details

### Spine Generation (pseudocode)
```javascript
function generateSpines(count) {
  const spines = [];
  for (let i = 0; i < count; i++) {
    // Random start/end on different sides/quadrants
    const start = randomEdgePoint();
    const end = randomEdgePoint(oppositeSide);
    // 2 control points pulled toward random interior locations
    const cp1 = { x: lerp(start.x, end.x, 0.33) + rand(-200,200), 
                  y: lerp(start.y, end.y, 0.33) + rand(-150,150) };
    const cp2 = { x: lerp(start.x, end.x, 0.66) + rand(-200,200),
                  y: lerp(start.y, end.y, 0.66) + rand(-150,150) };
    spines.push({ start, cp1, cp2, end, 
                  baseWidth: rand(15, 40),  // tiles
                  taper: rand(0.2, 0.4) });
  }
  return spines;
}
```

### Height Map Construction
```javascript
// For each tile, height = max contribution from all spines
for each tile (c, r):
  height = 0
  for each spine:
    t = closestParameterOnBezier(spine, c, r)  // 0..1
    closestPt = evalBezier(spine, t)
    dist = distance(c, r, closestPt)
    width = spine.baseWidth * (1 - spine.taper * abs(t - 0.5) * 2)
    // Add fractal displacement to width
    width += fbm(c, r, 2, 0.02, 2, 0.5) * 12
    if dist < width:
      contribution = 1 - (dist / width)  // 1 at center, 0 at edge
      height = max(height, contribution)
  
  // height: 0 = flat, 0.3-0.6 = foothills, 0.6-1.0 = mountain core
```

### Forest Growth (Cellular Automata)
```javascript
// Step 1: Seed from moisture
for each tile:
  if moistureNoise > 0.55 && tile == GRASS && !nearMountain:
    forestSeed[c][r] = true

// Step 2: Grow 3 iterations
for (let iter = 0; iter < 3; iter++):
  for each tile:
    if !forestSeed[c][r] && tile == GRASS:
      neighborCount = count forestSeed neighbors (8-dir)
      if neighborCount >= 3 && moistureNoise > 0.42:
        newForest[c][r] = true
  merge newForest into forestSeed

// Step 3: Carve clearings
for (let i = 0; i < 8; i++):
  pick random forest tile
  clear 4-8 tile radius circle back to GRASS
```

### River Carving
```javascript
function carveRiver(startC, startR, heightMap) {
  let c = startC, r = startR, width = 1;
  const visited = new Set();
  
  while (inBounds(c, r) && !isEdge(c, r)) {
    // Set water in width radius
    for tiles within width of (c, r): tile = WATER
    
    // Find lowest neighbor (with Perlin wander)
    const wander = fbm(c, r, 2, 0.01, 2, 0.5) * 0.3;
    let bestDir = lowestNeighborDirection(c, r, heightMap, wander);
    c += bestDir.dc; r += bestDir.dr;
    
    // Gradually widen
    width = Math.min(3, 1 + steps / 100);
    
    if (visited.has(key(c,r))) break; // prevent loops
    visited.add(key(c,r));
  }
}
```

---

## Performance Notes

- Spine distance calculations: O(COLS × ROWS × numSpines) — fast since numSpines ≤ 5
- Cellular automata: O(COLS × ROWS × 3 iterations) — trivial
- River carving: O(river_length) per river — negligible
- Total: ~3× current generation time, still under 500ms for 950×632

## Expected Visual Result

```
  [Mountain range snaking NW → SE with stone/ore inside]
       \
        [River flowing from mountains down to south edge]
         \
  [Large forest mass filling the valley between two ranges]
    [Clearings with berry bushes inside the forest]
  
  [Open grassland with sparse trees]    [Second mountain chain]
                                           [Gold deep inside]
  
  [Another forest region near east side]
    [River creating chokepoint between forest and mountains]
```

This should produce maps that look like your reference drawing — real geography, not noise patterns.

---

## Files to Modify

Only `index.html`:
- **Replace** `generateMap()` (lines 972-1008) — new multi-phase generator
- **Replace** `placeBiomeResources()` (lines 1013-1133) — now resource scattering within features
- **Add** new helper functions: `generateSpines()`, `evalBezier()`, `closestPointOnBezier()`, `carveRiver()`, `growForests()`
- Estimated: ~250 lines of new code replacing ~160 lines of old code
