// Render the map to a PNG without a browser
// Uses V4 Layered Climate map generation
const { createCanvas } = require('canvas');
const fs = require('fs');

// ─── CONSTANTS ───
const COLS = 950, ROWS = 632, TILE_SIZE = 1; // 1px per tile for overview
const T = {GRASS:0,TREE:1,STONE:2,ORE:3,BERRY:4,WATER:5,HQ:6,GOLD:7,
           TREE_DEPLETED:8,STONE_DEPLETED:9,ORE_DEPLETED:10,BERRY_DEPLETED:11,GOLD_DEPLETED:12};

const TILE_COLORS = {
  [T.GRASS]:  {base:[38,72,34],v:12},
  [T.TREE]:   {base:[22,50,18],v:8},
  [T.STONE]:  {base:[88,88,96],v:10},
  [T.ORE]:    {base:[60,82,110],v:8},
  [T.BERRY]:  {base:[42,78,38],v:8},
  [T.WATER]:  {base:[20,42,72],v:6},
  [T.GOLD]:   {base:[140,120,40],v:10},
};

const DEPOSITS = {
  [T.TREE]:  {res:'wood', amt:2, maxHP:5},
  [T.BERRY]: {res:'food', amt:3, maxHP:4},
  [T.STONE]: {res:'stone',amt:2, maxHP:8},
  [T.ORE]:   {res:'metal',amt:1, maxHP:6},
  [T.GOLD]:  {res:'gold', amt:1, maxHP:3},
};

// ─── NOISE ───
const _seed = (Math.random() * 65536) | 0;
console.log('Map seed:', _seed);

function hash(x,y){let h=_seed;h^=x*374761393;h^=y*668265263;h=Math.imul(h^(h>>>13),1274126177);h^=h>>>16;return(h&0x7fffffff)/0x7fffffff;}
function smoothNoise(x,y){const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy;const sx=fx*fx*(3-2*fx),sy=fy*fy*(3-2*fy);const n00=hash(ix,iy),n10=hash(ix+1,iy),n01=hash(ix,iy+1),n11=hash(ix+1,iy+1);return(n00+(n10-n00)*sx)+((n01+(n11-n01)*sx)-(n00+(n10-n00)*sx))*sy;}
function fbm(x,y,oct,freq,lac,gain){let v=0,a=1,f=freq,ta=0;for(let i=0;i<oct;i++){v+=smoothNoise(x*f,y*f)*a;ta+=a;f*=lac;a*=gain;}return v/ta;}

// ─── SEEDED RANDOM ───
let _mapRandState = _seed;
function initMapRand(){_mapRandState=_seed;}
function seededRand(){
  _mapRandState=(_mapRandState*1103515245+12345)&0x7fffffff;
  return _mapRandState/0x7fffffff;
}
initMapRand();

// ─── MAP ARRAYS ───
let map = [], tileVariant = [], depositHP = [];

// Stub for initFogMap (not needed for rendering)
function initFogMap() {}

// ═══════════════════════════════════════════════════════
//  MAP GENERATION V4 — Layered Climate (RimWorld-style)
// ═══════════════════════════════════════════════════════

// ─── TUNING LEVERS ───
const MAP_GEN = {
  // Elevation
  BASE_FREQ: 0.006,        // Lower = bigger mountain masses
  BASE_OCT: 6,
  RIDGE_FREQ: 0.008,       // Ridge line frequency (lower = wider ridges)
  RIDGE_OCT: 5,
  RIDGE_WEIGHT: 0.50,      // Higher = more prominent ridges
  WARP_FREQ: 0.004,        // Domain warp frequency
  WARP_STRENGTH: 100,      // Domain warp in tiles (organic shapes)

  // Moisture
  MOIST_FREQ: 0.007,       // Moisture variation scale
  MOIST_OCT: 5,
  WATER_PROX_BONUS: 0.10,  // Extra moisture near water
  WATER_PROX_RADIUS: 10,   // Tiles to check for water proximity

  // Thresholds (Whittaker lookup)
  WATER_LEVEL: 0.28,       // Below = water
  MOUNTAIN_LEVEL: 0.65,    // Above = stone (slightly higher = ~15% mountain)
  FOREST_ELEV_MIN: 0.43,   // Forest minimum elevation
  FOREST_ELEV_MAX: 0.65,   // Forest max (must match mountain level)
  FOREST_MOIST: 0.56,      // Forest needs this moisture (balanced ~15-18%)
  BERRY_ELEV_MAX: 0.44,    // Berries in low-elevation
  BERRY_MOIST: 0.52,       // Berries need this moisture

  // Dithering
  DITHER_FREQ: 0.05,       // High-freq noise for biome boundaries
  DITHER_AMP: 0.05,        // Dither amplitude (bigger = more jagged boundaries)

  // Resources
  STONE_EDGE_CHANCE: 0.12, // Stone at mountain edges
  ORE_CHANCE: 0.10,        // Inner mountain ore
  GOLD_CHANCE: 0.03,       // Deep mountain gold
  BERRY_CHANCE: 0.12,      // Berry in qualifying grass
  RESOURCE_CLUSTER_FREQ: 0.04, // Clustering noise freq

  // Rivers
  RIVER_COUNT_MIN: 2,
  RIVER_COUNT_MAX: 4,
  RIVER_MEANDER: 0.15,     // Lateral drift probability

  // Polish
  MIN_CLUSTER_SIZE: 3,     // Remove smaller clusters
  EDGE_BUFFER: 25,         // Tiles from edge kept as grass for spawning
};

// ─── NOISE HELPERS (use different seeds for independent layers) ───
// fbm with offset seeds for independent layers
function fbmLayer(x, y, oct, freq, seedOffX, seedOffY) {
  return fbm(x + seedOffX, y + seedOffY, oct, freq, 2.0, 0.5);
}

// Ridged multifractal: 1 - |noise| creates connected ridge lines
function ridgedMultifractal(x, y, oct, freq, seedOffX, seedOffY) {
  let v = 0, a = 1, f = freq, ta = 0;
  for (let i = 0; i < oct; i++) {
    const n = smoothNoise((x + seedOffX) * f, (y + seedOffY) * f);
    v += (1.0 - Math.abs(n * 2 - 1)) * a; // fold at zero → ridges
    ta += a;
    f *= 2.0;
    a *= 0.5;
  }
  return v / ta;
}

// ─── ELEVATION FIELD ───
function computeElevation(c, r) {
  const G = MAP_GEN;

  // Domain warping for organic shapes
  const warpX = fbmLayer(c, r, 4, G.WARP_FREQ, 3000, 7000) * G.WARP_STRENGTH;
  const warpY = fbmLayer(c, r, 4, G.WARP_FREQ, 8000, 2000) * G.WARP_STRENGTH;
  const wc = c + warpX, wr = r + warpY;

  // Base elevation (smooth rolling hills)
  const base = fbmLayer(wc, wr, G.BASE_OCT, G.BASE_FREQ, 0, 0);

  // Ridged multifractal (connected mountain chains)
  const ridges = ridgedMultifractal(wc, wr, G.RIDGE_OCT, G.RIDGE_FREQ, 5000, 5000);

  // Combine
  let elev = base * (1.0 - G.RIDGE_WEIGHT) + ridges * G.RIDGE_WEIGHT;

  // Edge falloff — keep edges as grass for enemy spawning
  const ed = Math.min(c, r, COLS - 1 - c, ROWS - 1 - r);
  const edgeFactor = Math.min(ed / G.EDGE_BUFFER, 1.0);
  elev *= edgeFactor;

  return elev;
}

// ─── MOISTURE FIELD ───
function computeMoisture(c, r) {
  return fbmLayer(c, r, MAP_GEN.MOIST_OCT, MAP_GEN.MOIST_FREQ, 12000, 15000);
}

// ─── MAIN GENERATE MAP ───
function generateMap() {
  map = []; tileVariant = []; depositHP = [];
  initFogMap();
  initMapRand();

  const G = MAP_GEN;

  // ═══ Init arrays ═══
  for (let c = 0; c < COLS; c++) {
    map[c] = []; tileVariant[c] = []; depositHP[c] = [];
    for (let r = 0; r < ROWS; r++) {
      tileVariant[c][r] = (hash(c * 7 + 31, r * 13 + 47) - 0.5) * 2;
      depositHP[c][r] = 0;
      map[c][r] = T.GRASS;
    }
  }

  // ═══ PASS 1 & 2: Compute elevation and moisture fields ═══
  const elevMap = [];
  const moistMap = [];
  for (let c = 0; c < COLS; c++) {
    elevMap[c] = new Float32Array(ROWS);
    moistMap[c] = new Float32Array(ROWS);
  }

  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r < ROWS; r++) {
      elevMap[c][r] = computeElevation(c, r);
      moistMap[c][r] = computeMoisture(c, r);
    }
  }

  // Compute percentile-based thresholds for consistent biome coverage across seeds
  // Sample ~10% of tiles for speed
  const sampleSize = Math.floor(COLS * ROWS * 0.1);
  const elevSamples = new Float32Array(sampleSize);
  const moistSamples = new Float32Array(sampleSize);
  for (let i = 0; i < sampleSize; i++) {
    const sc = Math.floor(seededRand() * COLS);
    const sr = Math.floor(seededRand() * ROWS);
    elevSamples[i] = elevMap[sc][sr];
    moistSamples[i] = elevMap[sc][sr]; // reuse for sorting
  }
  // Re-sample moisture independently
  for (let i = 0; i < sampleSize; i++) {
    const sc = Math.floor(seededRand() * COLS);
    const sr = Math.floor(seededRand() * ROWS);
    moistSamples[i] = moistMap[sc][sr];
  }
  elevSamples.sort();
  moistSamples.sort();

  // Target: ~7% water, ~15% mountain, ~15% forest → ~63% grass
  const waterThresh = elevSamples[Math.floor(sampleSize * 0.07)];
  const mountainThresh = elevSamples[Math.floor(sampleSize * 0.85)]; // top 15%
  const forestMoistThresh = moistSamples[Math.floor(sampleSize * 0.72)]; // top 28% moisture (forest only in wet zones)

  // ═══ PASS 3: Water + Biome assignment using percentile thresholds ═══
  // First pass: place water
  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r < ROWS; r++) {
      if (elevMap[c][r] < waterThresh) {
        map[c][r] = T.WATER;
      }
    }
  }

  // Moisture bonus near water (cross-pattern sampling for speed)
  const proxRad = G.WATER_PROX_RADIUS;
  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r < ROWS; r++) {
      if (map[c][r] === T.WATER) continue;
      let nearWater = false;
      for (let d = 1; d <= proxRad && !nearWater; d++) {
        if (c - d >= 0 && map[c - d][r] === T.WATER) nearWater = true;
        if (c + d < COLS && map[c + d][r] === T.WATER) nearWater = true;
        if (r - d >= 0 && map[c][r - d] === T.WATER) nearWater = true;
        if (r + d < ROWS && map[c][r + d] === T.WATER) nearWater = true;
      }
      if (nearWater) moistMap[c][r] += G.WATER_PROX_BONUS;
    }
  }

  // Biome assignment with dithered boundaries
  // forestElevMin: halfway between water and mountain thresholds
  const forestElevMin = waterThresh + (mountainThresh - waterThresh) * 0.35;

  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r < ROWS; r++) {
      if (map[c][r] === T.WATER) continue;

      const elev = elevMap[c][r];
      const moist = moistMap[c][r];
      const dither = fbmLayer(c, r, 2, G.DITHER_FREQ, 20000, 20000) * G.DITHER_AMP;

      if (elev > mountainThresh + dither) {
        // HIGH ELEVATION → Mountain (stone)
        map[c][r] = T.STONE;
      } else if (elev > forestElevMin + dither && elev <= mountainThresh + dither) {
        // MID-HIGH ELEVATION — forest if wet enough
        if (moist > forestMoistThresh + dither * 0.5) {
          map[c][r] = T.TREE;
        } else {
          map[c][r] = T.GRASS;
        }
      } else {
        map[c][r] = T.GRASS;
      }
    }
  }

  // ═══ PASS 5: River carving ═══
  const numRivers = G.RIVER_COUNT_MIN + Math.floor(seededRand() * (G.RIVER_COUNT_MAX - G.RIVER_COUNT_MIN + 1));
  for (let i = 0; i < numRivers; i++) {
    // Find a high-elevation source point
    let bestC = 0, bestR = 0, bestE = 0;
    for (let attempt = 0; attempt < 50; attempt++) {
      const tc = 30 + Math.floor(seededRand() * (COLS - 60));
      const tr = 30 + Math.floor(seededRand() * (ROWS - 60));
      if (elevMap[tc][tr] > bestE && map[tc][tr] === T.STONE) {
        bestE = elevMap[tc][tr];
        bestC = tc; bestR = tr;
      }
    }
    if (bestE > mountainThresh * 0.9) {
      carveRiverV4(bestC, bestR, elevMap, moistMap);
    }
  }

  // ═══ PASS 6: Resource scattering (within parent biomes) ═══
  scatterResourcesV4(elevMap, moistMap, mountainThresh, forestMoistThresh);

  // ═══ PASS 7: Polish ═══
  polishMapV4(elevMap);

  // ═══ Init deposit HP ═══
  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r < ROWS; r++) {
      const dep = DEPOSITS[map[c][r]];
      if (dep) depositHP[c][r] = dep.maxHP;
    }
  }
}

// ─── RIVER CARVING V4 (downhill steepest-descent) ───
function carveRiverV4(startC, startR, elevMap, moistMap) {
  let c = startC, r = startR;
  let width = 1;
  const visited = new Set();
  const maxSteps = COLS + ROWS;
  const dirs = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]];

  for (let step = 0; step < maxSteps; step++) {
    // Carve water in current width
    const w = Math.ceil(width);
    for (let dc = -w; dc <= w; dc++) {
      for (let dr = -w; dr <= w; dr++) {
        const nc = c + dc, nr = r + dr;
        if (nc >= 0 && nc < COLS && nr >= 0 && nr < ROWS) {
          if (dc * dc + dr * dr <= width * width) {
            map[nc][nr] = T.WATER;
          }
        }
      }
    }

    // Boost moisture near river
    const boostR = 6;
    for (let dc = -boostR; dc <= boostR; dc++) {
      for (let dr = -boostR; dr <= boostR; dr++) {
        const nc = c + dc, nr = r + dr;
        if (nc >= 0 && nc < COLS && nr >= 0 && nr < ROWS) {
          if (dc * dc + dr * dr <= boostR * boostR) {
            moistMap[nc][nr] = Math.min(1.0, moistMap[nc][nr] + 0.08);
          }
        }
      }
    }

    // Find steepest downhill neighbor
    let bestDC = 0, bestDR = 1, bestH = Infinity;
    for (const [dc, dr] of dirs) {
      const nc = c + dc, nr = r + dr;
      if (nc < 1 || nc >= COLS - 1 || nr < 1 || nr >= ROWS - 1) continue;
      let h = elevMap[nc][nr];
      // Small random meander
      if (seededRand() < MAP_GEN.RIVER_MEANDER) {
        h += (seededRand() - 0.5) * 0.05;
      }
      if (h < bestH) { bestH = h; bestDC = dc; bestDR = dr; }
    }

    c += bestDC; r += bestDR;
    width = Math.min(3.5, 1.0 + step / 120); // gradual widening

    const key = c * 10000 + r;
    if (visited.has(key)) break;
    visited.add(key);

    // Stop at map edge or existing water body
    if (c <= 2 || c >= COLS - 3 || r <= 2 || r >= ROWS - 3) break;
    if (map[c][r] === T.WATER && step > 10) break; // merge into existing water
  }
}

// ─── RESOURCE SCATTERING V4 (within parent biomes, clustered) ───
function scatterResourcesV4(elevMap, moistMap, mtnThresh, fMoistThresh) {
  const G = MAP_GEN;

  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r < ROWS; r++) {
      const tile = map[c][r];
      const elev = elevMap[c][r];
      const moist = moistMap[c][r];
      const detail = hash(c * 131 + 7, r * 173 + 13);

      if (tile === T.STONE) {
        // Clustering noise for ore/gold
        const oreCluster = fbmLayer(c, r, 2, G.RESOURCE_CLUSTER_FREQ, 30000, 30000);
        const goldCluster = fbmLayer(c, r, 2, G.RESOURCE_CLUSTER_FREQ * 0.7, 35000, 35000);

        // Deep mountain → gold (top 30% of mountain elevation, rare, clustered)
        const deepMtn = mtnThresh + (1.0 - mtnThresh) * 0.5;
        if (elev > deepMtn && goldCluster > 0.6 && detail < G.GOLD_CHANCE) {
          map[c][r] = T.GOLD;
        } else if (oreCluster > 0.55 && detail < G.ORE_CHANCE) {
          // Inner mountain → ore (clustered)
          map[c][r] = T.ORE;
        }

      } else if (tile === T.GRASS) {
        // Berries in low-elevation wet areas
        if (elev < mtnThresh * 0.6 && moist > fMoistThresh * 0.9) {
          const berryCluster = fbmLayer(c, r, 2, G.RESOURCE_CLUSTER_FREQ, 40000, 40000);
          if (berryCluster > 0.55 && detail < G.BERRY_CHANCE) {
            map[c][r] = T.BERRY;
          }
        }
      }
    }
  }
}

// ─── MAP POLISH V4 ───
function polishMapV4(elevMap) {
  const G = MAP_GEN;

  // Pass 1: Remove isolated single tiles
  for (let c = 1; c < COLS - 1; c++) {
    for (let r = 1; r < ROWS - 1; r++) {
      const t = map[c][r];
      if (t === T.STONE || t === T.ORE || t === T.GOLD || t === T.TREE) {
        let cnt = 0;
        for (let dc = -1; dc <= 1; dc++) {
          for (let dr = -1; dr <= 1; dr++) {
            if (dc === 0 && dr === 0) continue;
            const nt = map[c + dc][r + dr];
            if (t === T.TREE && nt === T.TREE) cnt++;
            else if ((t === T.STONE || t === T.ORE || t === T.GOLD) &&
                     (nt === T.STONE || nt === T.ORE || nt === T.GOLD)) cnt++;
          }
        }
        if (cnt < G.MIN_CLUSTER_SIZE - 1) map[c][r] = T.GRASS;
      }
    }
  }

  // Pass 2: Remove single-tile water
  for (let c = 1; c < COLS - 1; c++) {
    for (let r = 1; r < ROWS - 1; r++) {
      if (map[c][r] === T.WATER) {
        let cnt = 0;
        for (let dc = -1; dc <= 1; dc++) {
          for (let dr = -1; dr <= 1; dr++) {
            if (dc === 0 && dr === 0) continue;
            if (map[c + dc][r + dr] === T.WATER) cnt++;
          }
        }
        if (cnt < 2) map[c][r] = T.GRASS;
      }
    }
  }

  // Pass 3: Remove single-tile grass in water (islands)
  for (let c = 1; c < COLS - 1; c++) {
    for (let r = 1; r < ROWS - 1; r++) {
      if (map[c][r] === T.GRASS || map[c][r] === T.BERRY) {
        let waterCnt = 0;
        for (let dc = -1; dc <= 1; dc++) {
          for (let dr = -1; dr <= 1; dr++) {
            if (dc === 0 && dr === 0) continue;
            if (map[c + dc][r + dr] === T.WATER) waterCnt++;
          }
        }
        if (waterCnt >= 7) map[c][r] = T.WATER; // surrounded by water → fill in
      }
    }
  }

  // Pass 4: Clear base zone near center
  const cx = Math.floor(COLS / 2), cy = Math.floor(ROWS / 2);
  // Find nearest grass-heavy spot near center
  let bestC = cx, bestR = cy, bestGrass = 0;
  for (let dc = -40; dc <= 40; dc += 5) {
    for (let dr = -40; dr <= 40; dr += 5) {
      const tc = cx + dc, tr = cy + dr;
      if (tc < 30 || tc >= COLS - 30 || tr < 30 || tr >= ROWS - 30) continue;
      let grassCnt = 0;
      for (let i = -12; i <= 12; i++) {
        for (let j = -12; j <= 12; j++) {
          if (tc + i >= 0 && tc + i < COLS && tr + j >= 0 && tr + j < ROWS) {
            if (map[tc + i][tr + j] === T.GRASS) grassCnt++;
          }
        }
      }
      if (grassCnt > bestGrass) { bestGrass = grassCnt; bestC = tc; bestR = tr; }
    }
  }

  // Clear the base zone
  for (let dc = -15; dc <= 15; dc++) {
    for (let dr = -15; dr <= 15; dr++) {
      const nc = bestC + dc, nr = bestR + dr;
      if (nc >= 0 && nc < COLS && nr >= 0 && nr < ROWS) {
        if (dc * dc + dr * dr <= 15 * 15) {
          map[nc][nr] = T.GRASS;
        }
      }
    }
  }

  // Pass 5: Ensure minimum resources near base
  ensureMinResources(bestC, bestR, 80, T.TREE, 40);
  ensureMinResources(bestC, bestR, 80, T.STONE, 15);
  ensureMinResources(bestC, bestR, 80, T.BERRY, 8);

  // Pass 6: Ensure spawn paths from all 4 edges
  ensureSpawnPaths(bestC, bestR);
}

// ─── ENSURE MIN RESOURCES ───
function ensureMinResources(cx, cy, radius, tileType, minCount) {
  let count = 0;
  for (let dc = -radius; dc <= radius; dc++) {
    for (let dr = -radius; dr <= radius; dr++) {
      const nc = cx + dc, nr = cy + dr;
      if (nc >= 0 && nc < COLS && nr >= 0 && nr < ROWS) {
        if (map[nc][nr] === tileType) count++;
      }
    }
  }
  while (count < minCount) {
    const angle = seededRand() * Math.PI * 2;
    const dist = 20 + seededRand() * (radius - 25);
    const nc = Math.round(cx + Math.cos(angle) * dist);
    const nr = Math.round(cy + Math.sin(angle) * dist);
    if (nc >= 0 && nc < COLS && nr >= 0 && nr < ROWS && map[nc][nr] === T.GRASS) {
      map[nc][nr] = tileType;
      count++;
    }
  }
}

// ─── ENSURE SPAWN PATHS (BFS from center to all 4 edges) ───
function ensureSpawnPaths(cx, cy) {
  // Check if a 2-wide path exists from base to each edge using BFS
  // If blocked, carve a minimal grass path
  const edges = [
    { c: cx, r: 0 },          // top
    { c: cx, r: ROWS - 1 },   // bottom
    { c: 0, r: cy },          // left
    { c: COLS - 1, r: cy },   // right
  ];

  for (const target of edges) {
    // Carve a straight-ish path from base to edge, only converting blocking tiles
    let c = cx, r = cy;
    const tc = target.c, tr = target.r;
    while (c !== tc || r !== tr) {
      // Move toward target
      if (Math.abs(c - tc) > Math.abs(r - tr)) {
        c += (tc > c) ? 1 : -1;
      } else {
        r += (tr > r) ? 1 : -1;
      }
      if (c >= 0 && c < COLS && r >= 0 && r < ROWS) {
        if (map[c][r] !== T.GRASS && map[c][r] !== T.BERRY && map[c][r] !== T.TREE) {
          map[c][r] = T.GRASS;
        }
        // Also clear adjacent tile for 2-wide path
        if (c + 1 < COLS && map[c + 1][r] !== T.GRASS && map[c + 1][r] !== T.BERRY && map[c + 1][r] !== T.TREE) {
          map[c + 1][r] = T.GRASS;
        }
      }
    }
  }
}

// ═══════════════════════════════════════
//  GENERATE THE MAP
// ═══════════════════════════════════════

console.time('Map generation');
generateMap();
console.timeEnd('Map generation');

// ═══════════════════════════════════════
//  COUNT TILES
// ═══════════════════════════════════════
const counts = {};
for(let c=0;c<COLS;c++) for(let r=0;r<ROWS;r++){
  const t = map[c][r];
  counts[t] = (counts[t]||0) + 1;
}
const total = COLS * ROWS;
const names = ['Grass','Tree','Stone','Ore','Berry','Water','HQ','Gold'];
console.log('\nTile distribution:');
for(const [k,v] of Object.entries(counts)){
  console.log(`  ${names[k]||'?'}: ${v} (${(v/total*100).toFixed(1)}%)`);
}

// ═══════════════════════════════════════
//  RENDER TO PNG
// ═══════════════════════════════════════

// Render at 2x for better visibility
const SCALE = 2;
const canvas = createCanvas(COLS * SCALE, ROWS * SCALE);
const ctx = canvas.getContext('2d');

for(let c=0;c<COLS;c++){
  for(let r=0;r<ROWS;r++){
    const t = map[c][r];
    const tc = TILE_COLORS[t] || TILE_COLORS[T.GRASS];
    const v = tileVariant[c][r] * tc.v;
    const red = Math.max(0, Math.min(255, tc.base[0] + v));
    const grn = Math.max(0, Math.min(255, tc.base[1] + v));
    const blu = Math.max(0, Math.min(255, tc.base[2] + v));
    ctx.fillStyle = `rgb(${red|0},${grn|0},${blu|0})`;
    ctx.fillRect(c * SCALE, r * SCALE, SCALE, SCALE);
  }
}

// Draw base clearing indicator
const cx = Math.floor(COLS/2), cy = Math.floor(ROWS/2);
ctx.strokeStyle = 'rgba(255,255,0,0.6)';
ctx.lineWidth = 2;
ctx.beginPath();
ctx.arc(cx*SCALE, cy*SCALE, 15*SCALE, 0, Math.PI*2);
ctx.stroke();

// Add legend
ctx.fillStyle = 'rgba(0,0,0,0.7)';
ctx.fillRect(10, 10, 220, 170);
ctx.font = '14px sans-serif';
ctx.fillStyle = '#fff';
ctx.fillText('MAP V4 — Layered Climate', 20, 30);

const legend = [
  {color:[38,72,34], label:'Grass'},
  {color:[22,50,18], label:'Forest'},
  {color:[88,88,96], label:'Stone/Mountain'},
  {color:[60,82,110], label:'Iron Ore'},
  {color:[140,120,40], label:'Gold'},
  {color:[42,78,38], label:'Berry Bush'},
  {color:[20,42,72], label:'Water'},
];

legend.forEach((item, i) => {
  const y = 48 + i * 18;
  ctx.fillStyle = `rgb(${item.color[0]},${item.color[1]},${item.color[2]})`;
  ctx.fillRect(20, y-10, 14, 14);
  ctx.fillStyle = '#fff';
  ctx.font = '12px sans-serif';
  ctx.fillText(item.label, 40, y+1);
});

// Save
const buf = canvas.toBuffer('image/png');
fs.writeFileSync('/home/user/base-siege/map_preview.png', buf);
console.log(`\nSaved map_preview.png (${COLS*SCALE}x${ROWS*SCALE}px, ${(buf.length/1024).toFixed(0)}KB)`);
