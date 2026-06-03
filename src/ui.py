"""Terminal UI helpers — input prompts, menus, battle display."""
from __future__ import annotations
from typing import TypeVar, Callable

T = TypeVar("T")

LINE = "─" * 60
THIN = "·" * 60


def header(title: str) -> None:
    print(f"\n{LINE}")
    print(f"  {title}")
    print(LINE)


def section(title: str) -> None:
    print(f"\n  [{title}]")


def pause() -> None:
    input("\n  Press Enter to continue...")


def choose(prompt: str, options: list[str], allow_back: bool = False) -> int:
    """Returns 0-based index of chosen option, or -1 if back."""
    while True:
        print(f"\n  {prompt}")
        for i, opt in enumerate(options, 1):
            print(f"    {i}. {opt}")
        if allow_back:
            print(f"    0. Back")
        raw = input("  > ").strip()
        if raw == "0" and allow_back:
            return -1
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
        print("  Invalid choice.")


def choose_target(prompt: str, targets: list) -> int:
    """Returns 0-based index of chosen target."""
    return choose(prompt, [str(t) for t in targets])


def print_battle_header(party: list, enemies: list) -> None:
    header("BATTLE")
    section("ENEMIES")
    for e in enemies:
        alive = "" if e.is_alive else " [DEFEATED]"
        print(f"    {e.name:<18} {e.hp_bar(16)}{alive}{e.status_str()}")
    section("PARTY")
    for c in party:
        alive = " [KO]" if c.is_ko else ""
        print(f"    {c.name:<10} Lv{c.level} "
              f"HP:{c.hp:>4}/{c.stats.max_hp:<4} {c.hp_bar(14)}"
              f"  MP:{c.mp:>3}/{c.stats.max_mp:<3}{alive}{c.status_str()}")


def print_messages(messages: list[str]) -> None:
    for msg in messages:
        print(f"  >> {msg}")


def battle_menu(character) -> str:
    """Returns: 'attack', 'skill', 'item', 'defend', 'run'."""
    print(f"\n  {character.name}'s turn  (HP:{character.hp}/{character.stats.max_hp}  MP:{character.mp}/{character.stats.max_mp})")
    options = ["Attack", "Skill", "Item", "Defend", "Run"]
    idx = choose("Choose action:", options)
    return ["attack", "skill", "item", "defend", "run"][idx]
