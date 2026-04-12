<div align="center">

# 🏰 Base Siege

*Place your army like a Roman general, then fight alongside them as a hero when the horde arrives.*

<br>

[![Play Now](https://img.shields.io/badge/%E2%96%B6%20PLAY%20NOW-fergusri.github.io%2Fbase--siege-gold?style=for-the-badge&labelColor=1a1a2e)](https://fergusri.github.io/base-siege/)

<br>

[![Built with AutoGPT AutoPilot](https://img.shields.io/badge/built%20with-AutoGPT%20AutoPilot-blueviolet?style=flat-square)](https://agpt.co) [![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen?style=flat-square)](.) [![Single File](https://img.shields.io/badge/files-1%20×%20index.html-blue?style=flat-square)](./index.html) [![Vibe Jam 2026](https://img.shields.io/badge/Vibe%20Jam-2026-e8c56a?style=flat-square)](https://vibej.am/2026)

</div>

---

## The Story

This game was built entirely by AI in a single conversation.

No frameworks. No build step. No npm install. One human with a vision, one AI that writes code. The brief was simple: *"a tactical base defense game where you place units like a Roman general, then fight alongside them."* What you see is the result — a single HTML file containing a complete real-time strategy game with procedural map generation, A* pathfinding, and autonomous unit combat.

Every tree, every stone quarry, every enemy pathfinding around your walls — it's all running in one `<canvas>` element with zero dependencies.

## What Is It?

**Base Siege** is a tactical base defense game. Between waves, you're a god-view strategist — gathering resources, building walls and towers, and planning your defense. When the wave starts, enemies pour in from the map edges, and your structures fight autonomously while you run around as the hero plugging gaps.

**How to play:** WASD to move. Click resources to gather. Press 1-3 to select structures, click to place them. Press SPACE to start a wave. Survive.

## What's Inside

- 🗺️ **50×30 procedurally generated maps** with forests, quarries, ore veins, water, and natural chokepoints
- 🧭 **A* pathfinding** with binary min-heap — enemies intelligently route around your walls
- 🗼 **Autonomous tower combat** — towers track, lead, and fire homing projectiles at enemies
- 🪤 **Spike traps** that damage and slow — single-use per wave, reset between waves
- 👹 **2 enemy types** (Raiders and Runners) with scaling wave difficulty
- 🏰 **Base damage system** with visual crack overlays and HP color shifts
- 🎆 **Particle system**, camera shake, floating damage numbers, wave banners
- 🗾 **Live minimap** with enemy positions, structures, and viewport rectangle
- 📱 **Mobile + desktop** — mouse, keyboard, and touch input
- 🎮 **Zero dependencies. One file. 1,089 lines.**

## Run Locally

```bash
git clone https://github.com/FergusRi/base-siege.git
cd base-siege
open index.html
```

No server needed. No build step. Just open the file.

## License

MIT

---

<div align="center">

Made with ✨ by **AutoGPT AutoPilot** × **Fergus**

*A Vibe Jam 2026 entry*

</div>
