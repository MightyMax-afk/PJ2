# Chronicle of Echoes — Sprite & Art Asset Guide

A complete checklist of the visual assets needed to build a graphical version of
the game. The asset names below match the game's actual data (characters, enemies,
zones, items), so they can be wired into a front-end with zero guessing.

> **Workflow tip:** The game logic (`battle.py`, `character.py`, `enemy.py`,
> `skills.py`, `items.py`, `party.py`, `stats.py`) is fully decoupled from the
> terminal UI — only `main.py`/`ui.py` handle display. A graphical version reuses
> all of that logic unchanged and only replaces the presentation layer. You can
> build the engine on placeholder art first, then drop real PNGs in later with no
> code changes.

---

## 1. Character sprites — 4 heroes

Front-line battle sprites (classic JRPG: shown from the side/back).

| Code name | Class  | Visual notes                                            |
|-----------|--------|---------------------------------------------------------|
| **Kael**  | Warrior| armored, sword + shield, tanky (highest HP)             |
| **Lyra**  | Mage   | robed, staff, fire/ice/lightning caster                 |
| **Shen**  | Rogue  | light armor, daggers, poison/silence                    |
| **Aria**  | Healer | cleric / white-mage, restores HP, revives               |

- **Minimum:** 1 idle battle pose each (4 sprites)
- **Nice-to-have states:** `idle`, `attack`, `hurt`, `ko` (4 poses × 4 heroes = 16)

---

## 2. Enemy sprites — 6 (front-facing)

| Name              | Zone(s)          | Size hint        |
|-------------------|------------------|------------------|
| **Slime**         | forest           | small            |
| **Goblin**        | forest, cave     | small / medium   |
| **Wolf Pack**     | forest           | medium           |
| **Fire Sprite**   | cave             | small, glowing   |
| **Dark Knight**   | cave, dungeon    | large            |
| **Ancient Dragon**| dungeon (boss)   | **extra large**  |

---

## 3. Backgrounds — 3 battle backdrops + title

`forest`, `cave`, `dungeon`, and 1 **title screen** background.

---

## 4. UI elements

- Menu / dialog window frame (9-slice panel)
- Selection cursor / arrow
- HP bar + MP bar frames (the fill is drawn in code)
- Title logo: **"Chronicle of Echoes"**
- A readable bitmap / TTF font

---

## 5. Item icons — ~5 visual types (covers all 11 items)

| Icon         | Items covered                              | Look              |
|--------------|--------------------------------------------|-------------------|
| Potion       | Potion, Hi-Potion, Mega-Potion             | red vial          |
| Ether        | Ether, Hi-Ether                            | blue vial         |
| Elixir       | Elixir                                      | gold vial         |
| Cure         | Antidote, Echo Screen, Soft                | green vial        |
| Phoenix Down | Phoenix Down (revive)                      | feather           |

Size: 32×32 or 48×48.

---

## 6. Skill / status effect art (optional — adds a lot of polish)

- **Element effects:** fire, ice, lightning, dark, light, physical slash, heal sparkle
- **Status icons** (small, 16–24px): poison, freeze, silence, defend

---

## Technical specs to give the image AI

General image AIs struggle with *consistency*, so be explicit:

1. **One style, stated up front** — e.g. *"16-bit SNES JRPG pixel art, Final
   Fantasy VI style, consistent palette, top-left light source."* Prepend this to
   **every** prompt.
2. **Transparent background** — PNG with alpha. (Most AIs return a solid
   background; you'll likely need to key it out — see below.)
3. **Consistent canvas sizes:** heroes / small enemies ~128px, large enemies
   ~256px, dragon ~512px, backgrounds 1280×720, items 48px, status icons 24px.
4. **Generate characters as a set in one prompt** when possible, so proportions
   and style match.
5. **Naming convention** — use exactly this so the art wires in with no guessing:

```
assets/
  heroes/   kael_idle.png  lyra_idle.png  shen_idle.png  aria_idle.png
  enemies/  slime.png  goblin.png  wolf_pack.png  fire_sprite.png
            dark_knight.png  ancient_dragon.png
  bg/       forest.png  cave.png  dungeon.png  title.png
  ui/       window.png  cursor.png  font.ttf
  items/    potion.png  ether.png  elixir.png  cure.png  phoenix_down.png
  fx/       fire.png  ice.png  lightning.png  dark.png  light.png
            slash.png  heal.png
            status_poison.png  status_freeze.png  status_silence.png
            status_defend.png
```

---

## Other ways to get the art

- **Free asset packs are often better than AI here.** AI sprite sets are
  notoriously inconsistent (style drift, messy transparency, mismatched sizes).
  Check **OpenGameArt.org**, **itch.io** (search "JRPG battlers"), **Kenney.nl**,
  and the **LPC (Liberated Pixel Cup)** set — many are free / CC-licensed and
  already uniform.
- **Build the engine on placeholders first.** Colored rectangles as stand-in
  sprites make the whole game graphically playable now; real PNGs swap in later
  with no code changes.
- **Plan to post-process AI output:** background removal (`rembg` is a one-line
  Python tool) + batch resize. Budget time for that.
- **Keep it simple to start:** static battle sprites (no animation frames) already
  look great for a turn-based JRPG. Add attack/hurt frames later.

---

## Suggested next steps

1. Generate or source the assets above into the `assets/` folder structure.
2. Scaffold a **Pygame front-end** (new layer next to `src/`) that reuses the
   existing game engine and renders these sprites.
3. Start with placeholders so the game is playable immediately, then drop in real
   art as it's ready.

---

## Asset checklist

**Heroes**
- [ ] kael_idle
- [ ] lyra_idle
- [ ] shen_idle
- [ ] aria_idle
- [ ] (optional) attack / hurt / ko states for each

**Enemies**
- [ ] slime
- [ ] goblin
- [ ] wolf_pack
- [ ] fire_sprite
- [ ] dark_knight
- [ ] ancient_dragon

**Backgrounds**
- [ ] forest
- [ ] cave
- [ ] dungeon
- [ ] title

**UI**
- [ ] window frame
- [ ] cursor
- [ ] HP/MP bar frames
- [ ] title logo
- [ ] font

**Items**
- [ ] potion
- [ ] ether
- [ ] elixir
- [ ] cure
- [ ] phoenix_down

**FX / status (optional)**
- [ ] fire, ice, lightning, dark, light, slash, heal
- [ ] status: poison, freeze, silence, defend
