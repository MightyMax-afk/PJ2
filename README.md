# Chronicle of Echoes

A classic turn-based RPG skeleton inspired by Final Fantasy and Breath of Fire.
Built entirely in Python with a terminal UI.

## Features

| System | Details |
|---|---|
| **Battle Engine** | Speed-sorted turn order, elemental damage/resistance, status effects |
| **Characters** | Warrior · Mage · Rogue · Healer — each with unique stat growth and skill trees |
| **Skills** | Physical, Magic (Fire/Ice/Lightning/Dark/Light), Healing, Buff/Debuff |
| **Enemies** | Slime · Goblin · Fire Sprite · Wolf Pack · Dark Knight · Ancient Dragon (boss) |
| **Items** | Potions, Ethers, Antidote, Phoenix Down, Elixir, and more |
| **Party** | Up to 4 members, shared gold and inventory |
| **Overworld** | Zone-based exploration (Forest → Cave → Dungeon) with random encounters |
| **Save / Load** | JSON-based save file |

## Project Structure

```
src/
├── main.py        — Entry point, game loop, overworld, battle I/O
├── battle.py      — Core battle engine (turn order, damage, status ticks)
├── character.py   — Playable character data, leveling, EXP gain
├── enemy.py       — Enemy definitions, AI action selection, drop rolls
├── skills.py      — Skill library (all spells and abilities)
├── items.py       — Item catalog and Inventory class
├── party.py       — Party container (gold, inventory, rest)
├── stats.py       — Stats dataclass, Element & StatusEffect enums
├── ui.py          — Terminal display helpers, menus, prompts
└── save_load.py   — JSON save / load helpers
```

## How to Run

```bash
cd src
python main.py
```

Requires Python 3.10+, no external dependencies.

## Roadmap

- [ ] Equipment system (weapons, armor, accessories)
- [ ] World map with named locations and event triggers
- [ ] Shops (buy/sell items and gear)
- [ ] Boss scripted phases (conditional AI patterns)
- [ ] Persistent story flags / dialogue system
- [ ] Sprite-based GUI (pygame or similar)
